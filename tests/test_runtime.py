"""Runtime capacity, SDK namespace, and immutable settings tests."""

from __future__ import annotations

import asyncio
from pathlib import Path

import agents
import pytest
from pydantic import ValidationError

import nexus_agents
from config.settings import Settings
from orchestrator.nexus_agent import build_nexus_agent
from orchestrator.runtime import RunCapacityError, RunGate


def test_local_package_does_not_shadow_openai_agents_sdk() -> None:
    sdk_path = Path(agents.__file__).resolve()
    local_path = Path(nexus_agents.__file__).resolve()
    assert sdk_path.parent.name == "agents"
    assert "site-packages" in sdk_path.parts
    assert local_path.parent.name == "nexus_agents"


def test_agent_definition_is_cached(test_settings: Settings) -> None:
    assert build_nexus_agent(test_settings) is build_nexus_agent(test_settings)


def test_sensitive_tracing_cannot_be_enabled() -> None:
    with pytest.raises(ValidationError):
        Settings(trace_include_sensitive=True)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_run_gate_times_out_when_capacity_is_exhausted() -> None:
    gate = RunGate(1)
    entered = asyncio.Event()
    release = asyncio.Event()

    async def holder() -> None:
        async with gate.slot(run_id="holder", timeout_seconds=1):
            entered.set()
            await release.wait()

    task = asyncio.create_task(holder())
    await entered.wait()
    with pytest.raises(RunCapacityError):
        async with gate.slot(run_id="blocked", timeout_seconds=0.01):
            pass
    release.set()
    await task


@pytest.mark.asyncio
async def test_sdk_runtime_requires_api_key(test_settings: Settings) -> None:
    from orchestrator.runtime import OpenAISDKRuntime

    runtime = OpenAISDKRuntime()
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        await runtime.ensure(test_settings)


@pytest.mark.asyncio
async def test_sdk_runtime_reuses_client_and_rotates_on_key_change(
    test_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from typing import Any

    from pydantic import SecretStr

    from orchestrator import runtime as runtime_module

    class _Client:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.closed = False

        async def close(self) -> None:
            self.closed = True

    created: list[_Client] = []

    def _factory(**kwargs: Any) -> Any:
        client = _Client(**kwargs)
        created.append(client)
        return client

    monkeypatch.setattr(runtime_module, "AsyncOpenAI", _factory)
    monkeypatch.setattr(runtime_module, "set_default_openai_api", lambda _api: None)
    monkeypatch.setattr(
        runtime_module,
        "set_default_openai_client",
        lambda _client, *, use_for_tracing: None,
    )

    runtime = runtime_module.OpenAISDKRuntime()
    first_settings = test_settings.model_copy(update={"openai_api_key": SecretStr("first-key")})
    second_settings = test_settings.model_copy(update={"openai_api_key": SecretStr("second-key")})

    first = await runtime.ensure(first_settings)
    assert await runtime.ensure(first_settings) is first
    second = await runtime.ensure(second_settings)

    assert second is not first
    assert len(created) == 2
    assert created[0].closed is True
    assert created[1].kwargs["max_retries"] == test_settings.nexus_openai_transport_retries

    await runtime.close()
    assert created[1].closed is True
