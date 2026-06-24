"""OpenTelemetry setup, safe span helpers, and Agents SDK lifecycle hooks."""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from agents import Agent, ModelResponse, RunContextWrapper, RunHooks, Tool
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
from opentelemetry.trace import Span, Status, StatusCode

from observability.metrics import metrics
from observability.privacy import safe_span_attributes

_configured = False
_provider: TracerProvider | None = None


def configure_tracing(
    service_name: str,
    *,
    enabled: bool,
    endpoint: str | None = None,
    console: bool = False,
    sample_ratio: float = 0.25,
    service_version: str | None = None,
    environment: str | None = None,
) -> None:
    """Configure one process-wide tracer provider with bounded export overhead."""
    global _configured, _provider
    if _configured or not enabled:
        return

    attributes: dict[str, str] = {"service.name": service_name}
    if service_version:
        attributes["service.version"] = service_version
    if environment:
        attributes["deployment.environment.name"] = environment

    provider = TracerProvider(
        resource=Resource.create(attributes),
        sampler=ParentBased(TraceIdRatioBased(sample_ratio)),
    )
    if endpoint:
        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=endpoint),
                max_queue_size=512,
                max_export_batch_size=128,
                schedule_delay_millis=2_000,
                export_timeout_millis=10_000,
            )
        )
    elif console:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    _provider = provider
    _configured = True


def flush_tracing(*, timeout_millis: int = 5_000) -> bool:
    """Flush queued spans during graceful shutdown without resetting global state."""
    if _provider is None:
        return True
    return bool(_provider.force_flush(timeout_millis=timeout_millis))


def get_tracer(name: str = "nexus-openai") -> trace.Tracer:
    """Return a tracer from the active provider."""
    return trace.get_tracer(name)


def get_trace_id() -> str | None:
    """Return the current OTel trace ID as lowercase hexadecimal."""
    context = trace.get_current_span().get_span_context()
    return f"{context.trace_id:032x}" if context.is_valid else None


@asynccontextmanager
async def span(name: str, attributes: dict[str, Any] | None = None) -> AsyncIterator[Span]:
    """Create an async-friendly span and attach low-cardinality attributes."""
    with get_tracer().start_as_current_span(name) as current:
        for key, value in safe_span_attributes(attributes).items():
            current.set_attribute(key, value)
        try:
            yield current
        except BaseException as exc:
            current.record_exception(exc)
            current.set_status(Status(StatusCode.ERROR, type(exc).__name__))
            raise


def _tool_name(tool: Tool) -> str:
    value = getattr(tool, "name", None)
    return value if isinstance(value, str) and value else type(tool).__name__


class NexusRunHooks(RunHooks[Any]):
    """Record high-value LLM and tool timings without capturing prompts or outputs."""

    def __init__(self) -> None:
        self._llm_started: dict[int, tuple[float, Span, str]] = {}
        self._tool_started: dict[str, tuple[float, Span, str]] = {}

    async def on_llm_start(
        self,
        context: RunContextWrapper[Any],
        agent: Agent[Any],
        system_prompt: str | None,
        input_items: list[Any],
    ) -> None:
        del context, system_prompt, input_items
        name = agent.name
        current = get_tracer().start_span("nexus.llm.call")
        current.set_attribute("nexus.agent.name", name)
        self._llm_started[id(agent)] = (time.perf_counter(), current, name)

    async def on_llm_end(
        self,
        context: RunContextWrapper[Any],
        agent: Agent[Any],
        response: ModelResponse,
    ) -> None:
        del context, response
        started = self._llm_started.pop(id(agent), None)
        if started is None:
            return
        timestamp, current, agent_name = started
        duration = time.perf_counter() - timestamp
        metrics.llm_calls.labels(agent_name, "success").inc()
        metrics.llm_latency.labels(agent_name).observe(duration)
        current.set_attribute("nexus.llm.duration_ms", duration * 1000)
        current.set_status(Status(StatusCode.OK))
        current.end()

    async def on_tool_start(
        self,
        context: RunContextWrapper[Any],
        agent: Agent[Any],
        tool: Tool,
    ) -> None:
        del agent
        name = _tool_name(tool)
        call_id = str(getattr(context, "tool_call_id", id(tool)))
        current = get_tracer().start_span("nexus.tool.execute")
        current.set_attribute("nexus.tool.name", name)
        self._tool_started[call_id] = (time.perf_counter(), current, name)

    async def on_tool_end(
        self,
        context: RunContextWrapper[Any],
        agent: Agent[Any],
        tool: Tool,
        result: object,
    ) -> None:
        del agent, tool, result
        call_id = str(getattr(context, "tool_call_id", ""))
        started = self._tool_started.pop(call_id, None)
        if started is None:
            return
        timestamp, current, name = started
        duration = time.perf_counter() - timestamp
        metrics.tool_runs.labels(name, "success").inc()
        metrics.tool_latency.labels(name).observe(duration)
        current.set_attribute("nexus.tool.duration_ms", duration * 1000)
        current.set_status(Status(StatusCode.OK))
        current.end()

    def finish_pending(self, error_type: str) -> None:
        """Close spans left open when the SDK exits before an end hook fires."""
        for _agent_id, (timestamp, current, agent_name) in tuple(self._llm_started.items()):
            duration = time.perf_counter() - timestamp
            metrics.llm_calls.labels(agent_name, "error").inc()
            metrics.llm_latency.labels(agent_name).observe(duration)
            current.set_attribute("nexus.llm.duration_ms", duration * 1000)
            current.set_status(Status(StatusCode.ERROR, error_type))
            current.end()
        self._llm_started.clear()

        for _call_id, (timestamp, current, name) in tuple(self._tool_started.items()):
            duration = time.perf_counter() - timestamp
            metrics.tool_runs.labels(name, "error").inc()
            metrics.tool_latency.labels(name).observe(duration)
            current.set_attribute("nexus.tool.duration_ms", duration * 1000)
            current.set_status(Status(StatusCode.ERROR, error_type))
            current.end()
        self._tool_started.clear()
