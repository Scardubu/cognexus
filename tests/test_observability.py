"""Low-cost tracing hooks and span cleanup tests."""

from __future__ import annotations

from contextlib import AbstractContextManager
from types import SimpleNamespace
from typing import Any, cast

import pytest
from opentelemetry.trace import Status

from observability import tracing
from observability.tracing import NexusRunHooks, span


class _Span:
    def __init__(self) -> None:
        self.attributes: dict[str, object] = {}
        self.status: Status | None = None
        self.ended = False
        self.exceptions: list[BaseException] = []

    def set_attribute(self, key: str, value: object) -> None:
        self.attributes[key] = value

    def set_status(self, status: Status) -> None:
        self.status = status

    def record_exception(self, exception: BaseException) -> None:
        self.exceptions.append(exception)

    def end(self) -> None:
        self.ended = True


class _SpanContext(AbstractContextManager[_Span]):
    def __init__(self, current: _Span) -> None:
        self.current = current

    def __enter__(self) -> _Span:
        return self.current

    def __exit__(self, *args: object) -> None:
        return None


class _Tracer:
    def __init__(self) -> None:
        self.spans: list[_Span] = []

    def start_span(self, _name: str) -> _Span:
        current = _Span()
        self.spans.append(current)
        return current

    def start_as_current_span(self, _name: str) -> _SpanContext:
        current = _Span()
        self.spans.append(current)
        return _SpanContext(current)


@pytest.mark.asyncio
async def test_span_records_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    tracer = _Tracer()
    monkeypatch.setattr(tracing, "get_tracer", lambda name="nexus-openai": tracer)

    with pytest.raises(RuntimeError):
        async with span("test.span", {"safe": "value", "ignored": object()}):
            raise RuntimeError("boom")

    current = tracer.spans[0]
    assert current.attributes == {"safe": "value"}
    assert len(current.exceptions) == 1
    assert current.status is not None


@pytest.mark.asyncio
async def test_run_hooks_complete_successful_spans(monkeypatch: pytest.MonkeyPatch) -> None:
    tracer = _Tracer()
    monkeypatch.setattr(tracing, "get_tracer", lambda name="nexus-openai": tracer)
    hooks = NexusRunHooks()
    agent = cast(Any, SimpleNamespace(name="router"))
    context = cast(Any, SimpleNamespace(tool_call_id="call-1"))
    tool = cast(Any, SimpleNamespace(name="search"))

    await hooks.on_llm_start(context, agent, None, [])
    await hooks.on_llm_end(context, agent, cast(Any, object()))
    await hooks.on_tool_start(context, agent, tool)
    await hooks.on_tool_end(context, agent, tool, object())

    assert len(tracer.spans) == 2
    assert all(current.ended for current in tracer.spans)
    assert tracer.spans[0].attributes["nexus.agent.name"] == "router"
    assert tracer.spans[1].attributes["nexus.tool.name"] == "search"


@pytest.mark.asyncio
async def test_run_hooks_close_pending_spans_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tracer = _Tracer()
    monkeypatch.setattr(tracing, "get_tracer", lambda name="nexus-openai": tracer)
    hooks = NexusRunHooks()
    agent = cast(Any, SimpleNamespace(name="specialist"))
    context = cast(Any, SimpleNamespace(tool_call_id="call-2"))
    tool = cast(Any, SimpleNamespace(name="audit"))

    await hooks.on_llm_start(context, agent, None, [])
    await hooks.on_tool_start(context, agent, tool)
    hooks.finish_pending("CancelledError")
    hooks.finish_pending("CancelledError")

    assert len(tracer.spans) == 2
    assert all(current.ended for current in tracer.spans)
    assert all(current.status is not None for current in tracer.spans)
