"""Bounded orchestration capacity and shared OpenAI SDK client lifecycle."""

from __future__ import annotations

import asyncio
import hashlib
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from agents import set_default_openai_api, set_default_openai_client
from openai import AsyncOpenAI

from config.settings import Settings
from observability.logging import get_logger
from observability.metrics import metrics
from observability.tracing import span

logger = get_logger(__name__)


class RunCapacityError(RuntimeError):
    """Raised when a run cannot acquire bounded execution capacity in time."""


@dataclass(frozen=True, slots=True)
class RunSlot:
    """Metadata captured when a run enters the bounded execution pool."""

    wait_ms: float


class RunGate:
    """Small, fair-enough process-local gate that prevents unbounded LLM fan-out."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._semaphore = asyncio.Semaphore(capacity)

    @asynccontextmanager
    async def slot(self, *, run_id: str, timeout_seconds: float) -> AsyncIterator[RunSlot]:
        """Acquire one run slot with a bounded wait and release it reliably."""
        started = time.perf_counter()
        try:
            async with asyncio.timeout(timeout_seconds):
                async with span("nexus.run.queue_wait", {"nexus.run_id": run_id}):
                    await self._semaphore.acquire()
        except TimeoutError as exc:
            waited = time.perf_counter() - started
            metrics.run_queue_wait.observe(waited)
            metrics.errors.labels("run_gate", type(exc).__name__).inc()
            raise RunCapacityError("NEXUS run capacity is temporarily saturated") from exc

        waited = time.perf_counter() - started
        metrics.run_queue_wait.observe(waited)
        metrics.run_inflight.inc()
        try:
            yield RunSlot(wait_ms=waited * 1000)
        finally:
            metrics.run_inflight.dec()
            self._semaphore.release()


class OpenAISDKRuntime:
    """Own and reuse the AsyncOpenAI client configured for the Agents SDK."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._client: AsyncOpenAI | None = None
        self._fingerprint: tuple[bytes, float, int] | None = None

    async def ensure(self, settings: Settings) -> AsyncOpenAI:
        """Create or reuse a client with explicit timeout and retry bounds."""
        key = settings.openai_key_value
        if key is None:
            raise RuntimeError("OPENAI_API_KEY is required for live NEXUS runs")

        fingerprint = (
            hashlib.sha256(key.encode("utf-8")).digest()[:8],
            settings.nexus_openai_timeout_seconds,
            settings.nexus_openai_transport_retries,
        )
        if self._client is not None and self._fingerprint == fingerprint:
            return self._client

        async with self._lock:
            if self._client is not None and self._fingerprint == fingerprint:
                return self._client
            previous = self._client
            client = AsyncOpenAI(
                api_key=key,
                timeout=settings.nexus_openai_timeout_seconds,
                max_retries=settings.nexus_openai_transport_retries,
            )
            set_default_openai_api("responses")
            set_default_openai_client(client, use_for_tracing=True)
            self._client = client
            self._fingerprint = fingerprint
            if previous is not None:
                await previous.close()
            logger.info(
                "openai_sdk_runtime_configured",
                timeout_seconds=settings.nexus_openai_timeout_seconds,
                transport_retries=settings.nexus_openai_transport_retries,
            )
            return client

    async def close(self) -> None:
        """Close the shared HTTP client during service shutdown."""
        async with self._lock:
            client = self._client
            self._client = None
            self._fingerprint = None
        if client is not None:
            await client.close()


sdk_runtime = OpenAISDKRuntime()
