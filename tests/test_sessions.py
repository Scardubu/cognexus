"""Session creation, persistence, deletion, and fallback tests."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from config.settings import Settings
from sessions.session_manager import SessionManager


@pytest.mark.asyncio
async def test_sqlite_session_persists(test_settings: Settings) -> None:
    manager = SessionManager(test_settings)
    session = await manager.get_session("persist-test")
    assert session is not None
    await session.add_items([{"role": "user", "content": "hello"}])
    items = await session.get_items()
    assert len(items) == 1
    await manager.close()


@pytest.mark.asyncio
async def test_delete_clears_session(test_settings: Settings) -> None:
    manager = SessionManager(test_settings)
    session = await manager.get_session("delete-test")
    assert session is not None
    await session.add_items([{"role": "user", "content": "hello"}])
    await manager.delete("delete-test")
    session2 = await manager.get_session("delete-test")
    assert session2 is not None
    assert await session2.get_items() == []
    await manager.close()


@pytest.mark.asyncio
async def test_redis_falls_back_to_sqlite(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings(
        nexus_env="test",
        nexus_session_backend="redis",
        nexus_allow_sqlite_fallback=True,
        nexus_allow_stateless_fallback=False,
        nexus_sqlite_path=tmp_path / "fallback.db",
        nexus_compaction_enabled=False,
        nexus_model_validation_mode="off",
    )
    manager = SessionManager(settings)

    async def fail() -> Any:
        raise ConnectionError("redis unavailable")

    monkeypatch.setattr(manager, "_get_redis_client", fail)
    handle = await manager.get_handle("fallback-test")
    assert handle.effective_backend == "sqlite"
    assert handle.degraded is True
    await manager.close()


def test_stateless_requires_explicit_opt_in(tmp_path: Any) -> None:
    with pytest.raises(ValidationError, match="NEXUS_ALLOW_STATELESS_FALLBACK"):
        Settings(
            nexus_env="test",
            nexus_session_backend="stateless",
            nexus_allow_stateless_fallback=False,
            nexus_sqlite_path=tmp_path / "unused.db",
            nexus_compaction_enabled=False,
            nexus_model_validation_mode="off",
        )


@pytest.mark.asyncio
async def test_concurrent_handle_creation_is_deduplicated(test_settings: Settings) -> None:
    manager = SessionManager(test_settings)
    first, second = await __import__("asyncio").gather(
        manager.get_handle("same-session"),
        manager.get_handle("same-session"),
    )
    assert first is second
    assert first.session is second.session
    await manager.close()


class _SharedAsyncLock:
    """Small redis-py lock stand-in for cross-manager serialization tests."""

    def __init__(self, lock: Any, *, acquire_result: bool = True) -> None:
        self._lock = lock
        self._acquire_result = acquire_result
        self._owned = False

    async def acquire(self) -> bool:
        if not self._acquire_result:
            return False
        await self._lock.acquire()
        self._owned = True
        return True

    async def release(self) -> None:
        if self._owned:
            self._owned = False
            self._lock.release()


class _FakeRedisClient:
    def __init__(self, *, acquire_result: bool = True) -> None:
        import asyncio

        self._locks: dict[str, Any] = {}
        self._acquire_result = acquire_result
        self._asyncio = asyncio

    def lock(self, name: str, **_: Any) -> _SharedAsyncLock:
        shared = self._locks.setdefault(name, self._asyncio.Lock())
        return _SharedAsyncLock(shared, acquire_result=self._acquire_result)


@pytest.mark.asyncio
async def test_redis_session_scope_serializes_across_managers(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    import asyncio

    from sessions.session_manager import SessionHandle

    settings = Settings(
        nexus_env="test",
        nexus_session_backend="redis",
        nexus_sqlite_path=tmp_path / "unused.db",
        nexus_compaction_enabled=False,
        nexus_model_validation_mode="off",
    )
    client = _FakeRedisClient()
    managers = (SessionManager(settings), SessionManager(settings))
    for manager in managers:
        manager._handles["shared-session"] = SessionHandle("shared-session", "redis", "redis", None)
        monkeypatch.setattr(manager, "_redis_client", client)

    active = 0
    peak = 0

    async def work(manager: SessionManager) -> None:
        nonlocal active, peak
        async with manager.session_scope("shared-session"):
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0.01)
            active -= 1

    await asyncio.gather(*(work(manager) for manager in managers))
    assert peak == 1


@pytest.mark.asyncio
async def test_redis_session_scope_fails_closed_when_lock_times_out(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sessions.session_manager import SessionHandle, SessionUnavailableError

    settings = Settings(
        nexus_env="test",
        nexus_session_backend="redis",
        nexus_sqlite_path=tmp_path / "unused.db",
        nexus_compaction_enabled=False,
        nexus_model_validation_mode="off",
    )
    manager = SessionManager(settings)
    manager._handles["busy-session"] = SessionHandle("busy-session", "redis", "redis", None)
    monkeypatch.setattr(manager, "_redis_client", _FakeRedisClient(acquire_result=False))

    with pytest.raises(SessionUnavailableError, match="session is busy"):
        async with manager.session_scope("busy-session"):
            pytest.fail("busy Redis sessions must not execute concurrently")


@pytest.mark.asyncio
async def test_delete_keeps_cached_handle_valid_for_queued_users(test_settings: Settings) -> None:
    manager = SessionManager(test_settings)
    handle = await manager.get_handle("delete-queued-test")
    assert handle.session is not None
    await handle.session.add_items([{"role": "user", "content": "before"}])

    await manager.delete("delete-queued-test")

    same_handle = await manager.get_handle("delete-queued-test")
    assert same_handle is handle
    assert same_handle.session is not None
    assert await same_handle.session.get_items() == []
    await same_handle.session.add_items([{"role": "user", "content": "after"}])
    assert len(await same_handle.session.get_items()) == 1
    await manager.close()


@pytest.mark.asyncio
async def test_delete_marks_handle_active_while_waiting_and_cannot_be_pruned(
    test_settings: Settings,
) -> None:
    import asyncio

    settings = test_settings.model_copy(update={"nexus_session_cache_max_entries": 1})
    manager = SessionManager(settings)
    target = await manager.get_handle("delete-prune-target")
    assert target.session is not None

    await target.run_lock.acquire()
    delete_task = asyncio.create_task(manager.delete("delete-prune-target"))
    try:
        for _ in range(100):
            if target.active_users == 1:
                break
            await asyncio.sleep(0)
        assert target.active_users == 1

        await manager.get_handle("overflow-session")
        assert manager._handles.get("delete-prune-target") is target
    finally:
        target.run_lock.release()

    assert await delete_task is True
    assert target.active_users == 0
    await manager.close()
