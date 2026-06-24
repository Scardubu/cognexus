"""Session backend resolution, bounded caching, fallback policy, and lifecycle."""

from __future__ import annotations

import asyncio
import inspect
import time
from collections import OrderedDict
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

from agents.memory import Session

from config.settings import Settings, get_settings
from observability.logging import get_logger
from observability.metrics import metrics
from security.identifiers import session_observability_reference, validate_session_id
from sessions.compaction import wrap_with_compaction
from sessions.intelligence import SessionIntelligence, analyze_session_items
from sessions.redis_session import create_redis_client, create_redis_session
from sessions.sqlite_session import create_sqlite_session

logger = get_logger(__name__)


class SessionUnavailableError(RuntimeError):
    """Raised when the configured backend is unavailable and fallback is forbidden."""


@dataclass(slots=True)
class SessionHandle:
    """A resolved SDK session plus operational and concurrency metadata."""

    session_id: str
    requested_backend: str
    effective_backend: str
    session: Session | None
    degraded: bool = False
    warnings: list[str] = field(default_factory=list)
    last_accessed: float = field(default_factory=time.monotonic)
    active_users: int = 0
    run_lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)


class SessionManager:
    """Resolve and reuse session backends under an explicit failover policy."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._redis_client: Any | None = None
        self._redis_lock = asyncio.Lock()
        self._cache_lock = asyncio.Lock()
        self._creation_locks: dict[str, asyncio.Lock] = {}
        self._handles: OrderedDict[str, SessionHandle] = OrderedDict()
        self._closed = False

    async def get_handle(self, session_id: str) -> SessionHandle:
        """Return a cached handle, creating exactly one handle per validated session ID."""
        if self._closed:
            raise RuntimeError("session manager is closed")
        session_id = validate_session_id(session_id)

        async with self._cache_lock:
            existing = self._handles.get(session_id)
            if existing is not None:
                existing.last_accessed = time.monotonic()
                self._handles.move_to_end(session_id)
                metrics.session_cache_events.labels("hit", existing.effective_backend).inc()
                return existing
            creation_lock = self._creation_locks.setdefault(session_id, asyncio.Lock())

        try:
            async with creation_lock:
                async with self._cache_lock:
                    existing = self._handles.get(session_id)
                    if existing is not None:
                        existing.last_accessed = time.monotonic()
                        self._handles.move_to_end(session_id)
                        metrics.session_cache_events.labels("hit", existing.effective_backend).inc()
                        return existing

                handle = await self._resolve_handle(session_id)
                metrics.session_cache_events.labels("miss", handle.effective_backend).inc()
                async with self._cache_lock:
                    self._handles[session_id] = handle
                    self._handles.move_to_end(session_id)
        finally:
            async with self._cache_lock:
                current = self._creation_locks.get(session_id)
                if current is creation_lock and not creation_lock.locked():
                    self._creation_locks.pop(session_id, None)

        await self._prune()
        return handle

    @asynccontextmanager
    async def session_scope(self, session_id: str) -> AsyncIterator[SessionHandle]:
        """Serialize one session locally and, for Redis, across service replicas."""
        handle = await self.get_handle(session_id)
        async with self._cache_lock:
            handle.active_users += 1
            handle.last_accessed = time.monotonic()
        try:
            async with self._execution_lock(handle):
                yield handle
        finally:
            async with self._cache_lock:
                handle.active_users = max(0, handle.active_users - 1)
                handle.last_accessed = time.monotonic()
            await self._prune()

    @asynccontextmanager
    async def _execution_lock(self, handle: SessionHandle) -> AsyncIterator[None]:
        """Hold the process-local lock and a bounded Redis lease when required.

        The local lock protects cached SDK session objects. The Redis lease extends
        that invariant across workers and Kubernetes replicas. Its lifetime is
        bounded above the outer request timeout so a crashed worker cannot hold a
        session forever.
        """
        async with handle.run_lock:
            if handle.effective_backend != "redis":
                yield
                return

            client = await self._get_redis_client()
            lock = client.lock(
                f"{self.settings.nexus_redis_key_prefix}:run-lock:{handle.session_id}",
                timeout=(
                    self.settings.nexus_queue_timeout_seconds
                    + self.settings.nexus_request_timeout_seconds
                    + 30.0
                ),
                blocking_timeout=self.settings.nexus_queue_timeout_seconds,
                thread_local=False,
                raise_on_release_error=False,
            )
            started = time.monotonic()
            try:
                acquired = bool(await lock.acquire())
            except Exception as exc:
                metrics.session_lock_events.labels("acquire_error").inc()
                metrics.errors.labels("session_lock", type(exc).__name__).inc()
                raise SessionUnavailableError(
                    "distributed session coordination is unavailable"
                ) from exc
            finally:
                metrics.session_lock_wait.observe(time.monotonic() - started)

            if not acquired:
                metrics.session_lock_events.labels("timeout").inc()
                raise SessionUnavailableError("session is busy; retry later")

            metrics.session_lock_events.labels("acquired").inc()
            try:
                yield
            finally:
                try:
                    await asyncio.shield(lock.release())
                except Exception as exc:
                    metrics.session_lock_events.labels("release_error").inc()
                    metrics.errors.labels("session_lock_release", type(exc).__name__).inc()
                    logger.warning(
                        "redis_session_lock_release_failed",
                        error_type=type(exc).__name__,
                    )

    async def get_session(self, session_id: str) -> Session | None:
        """Return the SDK session object for direct integrations and tests."""
        return (await self.get_handle(session_id)).session

    async def inspect(self, session_id: str, *, limit: int = 20) -> dict[str, Any]:
        """Return backend and history metadata without exposing message content."""
        async with self.session_scope(session_id) as handle:
            items: list[Any] = []
            if handle.session is not None:
                items = await handle.session.get_items(limit=limit)
            intelligence = self.analyze_items(items)
            return {
                "session_id": session_id,
                "requested_backend": handle.requested_backend,
                "effective_backend": handle.effective_backend,
                "degraded": handle.degraded,
                "warnings": list(handle.warnings),
                "item_count": len(items),
                "item_types": [
                    item.get("type", "unknown") if isinstance(item, dict) else type(item).__name__
                    for item in items
                ],
                **intelligence.model_dump(mode="json"),
            }

    def analyze_items(self, items: list[Any]) -> SessionIntelligence:
        """Return a privacy-preserving continuity snapshot for already loaded items."""
        snapshot = analyze_session_items(
            items,
            candidate_items=self.settings.nexus_compaction_candidate_items,
            summary_max_chars=self.settings.nexus_session_summary_max_chars,
            represented_item_limit=self.settings.nexus_session_summary_item_limit,
        )
        metrics.session_continuity.observe(snapshot.continuity_score)
        if snapshot.compaction_recommended:
            metrics.session_compaction_signals.labels("recommended").inc()
        return snapshot

    async def intelligence(
        self, session_id: str, *, limit: int | None = None
    ) -> SessionIntelligence:
        """Return rolling summary and continuity signals without exposing raw history."""
        async with self.session_scope(session_id) as handle:
            items: list[Any] = []
            if handle.session is not None:
                items = await handle.session.get_items(
                    limit=limit or self.settings.nexus_session_summary_item_limit
                )
            return self.analyze_items(items)

    async def delete(self, session_id: str) -> bool:
        """Clear a session atomically without invalidating queued or active users."""
        async with self.session_scope(session_id) as handle:
            if handle.session is not None:
                await handle.session.clear_session()
            handle.last_accessed = time.monotonic()
        metrics.session_cache_events.labels("delete", handle.effective_backend).inc()
        return True

    async def readiness(self) -> dict[str, Any]:
        """Check the configured backend without silently selecting stateless mode."""
        backend = self.settings.nexus_session_backend
        if backend == "redis":
            try:
                client = await self._get_redis_client()
                await client.ping()
                return {"ready": True, "backend": "redis", "degraded": False}
            except Exception as exc:
                if self.settings.nexus_allow_sqlite_fallback:
                    sqlite_status = await self._sqlite_readiness()
                    return {
                        **sqlite_status,
                        "degraded": True,
                        "reason": f"redis unavailable: {type(exc).__name__}",
                    }
                return {
                    "ready": False,
                    "backend": "redis",
                    "degraded": False,
                    "reason": type(exc).__name__,
                }
        if backend == "sqlite":
            return await self._sqlite_readiness()
        return {
            "ready": self.settings.nexus_allow_stateless_fallback,
            "backend": "stateless",
            "degraded": False,
        }

    async def _sqlite_readiness(self) -> dict[str, Any]:
        """Open the configured database and execute a real SDK read probe."""
        try:
            self.settings.nexus_sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            probe = create_sqlite_session("readiness-probe", self.settings.nexus_sqlite_path)
            await probe.get_items(limit=1)
            close = getattr(probe, "close", None)
            if close is not None:
                result = close()
                if inspect.isawaitable(result):
                    await result
            return {"ready": True, "backend": "sqlite", "degraded": False}
        except Exception as exc:
            metrics.errors.labels("session_readiness", type(exc).__name__).inc()
            return {
                "ready": False,
                "backend": "sqlite",
                "degraded": False,
                "reason": type(exc).__name__,
            }

    async def close(self) -> None:
        """Close cached SDK sessions and the shared Redis connection pool."""
        if self._closed:
            return
        self._closed = True
        async with self._cache_lock:
            handles = list(self._handles.values())
            self._handles.clear()
            self._creation_locks.clear()
        await asyncio.gather(
            *(self._close_handle(handle) for handle in handles),
            return_exceptions=True,
        )
        if self._redis_client is not None:
            await self._redis_client.aclose()
            self._redis_client = None

    async def _resolve_handle(self, session_id: str) -> SessionHandle:
        requested = self.settings.nexus_session_backend
        if requested == "stateless":
            return SessionHandle(session_id, requested, "stateless", None)

        if requested == "redis":
            try:
                client = await self._get_redis_client()
                redis_base: Session = create_redis_session(
                    session_id,
                    client,
                    self.settings.nexus_redis_ttl_seconds,
                    self.settings.nexus_redis_key_prefix,
                )
                return self._wrap(session_id, requested, "redis", redis_base)
            except Exception as exc:
                logger.error(
                    "redis_session_unavailable",
                    error_type=type(exc).__name__,
                    session_ref=session_observability_reference(session_id),
                )
                if self.settings.nexus_allow_sqlite_fallback:
                    metrics.session_fallbacks.labels("redis", "sqlite").inc()
                    fallback_base: Session = create_sqlite_session(
                        session_id, self.settings.nexus_sqlite_path
                    )
                    return self._wrap(
                        session_id,
                        requested,
                        "sqlite",
                        fallback_base,
                        degraded=True,
                        warnings=[
                            f"Redis unavailable; SQLite fallback active: {type(exc).__name__}"
                        ],
                    )
                if self.settings.nexus_allow_stateless_fallback:
                    metrics.session_fallbacks.labels("redis", "stateless").inc()
                    return SessionHandle(
                        session_id,
                        requested,
                        "stateless",
                        None,
                        degraded=True,
                        warnings=[
                            f"Redis unavailable; stateless fallback active: {type(exc).__name__}"
                        ],
                    )
                raise SessionUnavailableError(
                    "Redis is unavailable and all fallback backends are disabled"
                ) from exc

        sqlite_base: Session = create_sqlite_session(session_id, self.settings.nexus_sqlite_path)
        return self._wrap(session_id, requested, "sqlite", sqlite_base)

    async def _get_redis_client(self) -> Any:
        if self._redis_client is not None:
            return self._redis_client
        async with self._redis_lock:
            if self._redis_client is None:
                self._redis_client = await create_redis_client(
                    self.settings.redis_url,
                    connect_timeout_seconds=self.settings.nexus_redis_connect_timeout_seconds,
                    socket_timeout_seconds=self.settings.nexus_redis_socket_timeout_seconds,
                    max_connections=self.settings.nexus_redis_max_connections,
                )
        return self._redis_client

    def _wrap(
        self,
        session_id: str,
        requested: str,
        effective: str,
        base: Session,
        *,
        degraded: bool = False,
        warnings: list[str] | None = None,
    ) -> SessionHandle:
        session: Session = base
        notes = list(warnings or ())
        if self.settings.nexus_compaction_enabled and self.settings.openai_api_key:
            session = wrap_with_compaction(
                session_id,
                base,
                model=self.settings.nexus_compaction_model,
                candidate_items=self.settings.nexus_compaction_candidate_items,
            )
        elif self.settings.nexus_compaction_enabled:
            notes.append("Compaction inactive until OPENAI_API_KEY is configured.")
        return SessionHandle(
            session_id=session_id,
            requested_backend=requested,
            effective_backend=effective,
            session=session,
            degraded=degraded,
            warnings=notes,
        )

    async def _prune(self) -> None:
        now = time.monotonic()
        stale_before = now - self.settings.nexus_session_cache_ttl_seconds
        evicted: list[SessionHandle] = []
        async with self._cache_lock:
            for session_id, handle in list(self._handles.items()):
                if handle.active_users == 0 and handle.last_accessed < stale_before:
                    evicted.append(self._handles.pop(session_id))

            overflow = len(self._handles) - self.settings.nexus_session_cache_max_entries
            if overflow > 0:
                for session_id, handle in list(self._handles.items()):
                    if overflow <= 0:
                        break
                    if handle.active_users == 0:
                        evicted.append(self._handles.pop(session_id))
                        overflow -= 1

        if evicted:
            await asyncio.gather(
                *(self._close_handle(handle) for handle in evicted),
                return_exceptions=True,
            )
            for handle in evicted:
                metrics.session_cache_events.labels("evict", handle.effective_backend).inc()

    async def _close_handle(self, handle: SessionHandle) -> None:
        session = handle.session
        if session is None:
            return
        underlying = getattr(session, "underlying_session", session)
        close = getattr(underlying, "close", None)
        if close is None:
            return
        try:
            result = close()
            if inspect.isawaitable(result):
                await result
        except Exception as exc:
            metrics.errors.labels("session_close", type(exc).__name__).inc()
            logger.warning(
                "session_close_failed",
                session_ref=session_observability_reference(handle.session_id),
                error_type=type(exc).__name__,
            )
