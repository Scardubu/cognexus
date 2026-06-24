"""Cached model validation and configuration-backed routing tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from pydantic import SecretStr

from config.settings import Settings
from orchestrator.model_router import (
    reset_model_validation_cache,
    route_models,
    validate_configured_models,
)
from orchestrator.runtime import sdk_runtime


@dataclass(frozen=True, slots=True)
class _Model:
    id: str


class _Page:
    def __init__(self, ids: list[str], next_page: _Page | None = None) -> None:
        self.data = [_Model(item) for item in ids]
        self._next_page = next_page

    def has_next_page(self) -> bool:
        return self._next_page is not None

    async def get_next_page(self) -> _Page:
        assert self._next_page is not None
        return self._next_page


class _Models:
    def __init__(self, page: _Page | None = None, error: Exception | None = None) -> None:
        self.page = page
        self.error = error
        self.calls = 0

    async def list(self) -> _Page:
        self.calls += 1
        if self.error is not None:
            raise self.error
        assert self.page is not None
        return self.page


class _Client:
    def __init__(self, models: _Models) -> None:
        self.models = models


@pytest.fixture(autouse=True)
def _clear_model_cache() -> None:
    reset_model_validation_cache()


def test_route_models_uses_validated_configuration(test_settings: Settings) -> None:
    route = route_models(5, test_settings)
    assert route.orchestrator == test_settings.nexus_orchestrator_model
    assert route.specialist == test_settings.nexus_specialist_model
    assert route.guardrail == test_settings.nexus_guardrail_model
    assert route.compaction == test_settings.nexus_compaction_model


@pytest.mark.asyncio
async def test_model_validation_off_and_missing_key(test_settings: Settings) -> None:
    disabled = await validate_configured_models(test_settings)
    assert disabled == {"checked": False, "available": [], "missing": [], "cached": False}

    warning_settings = test_settings.model_copy(update={"nexus_model_validation_mode": "warn"})
    warning = await validate_configured_models(warning_settings)
    assert warning["warning"] == "OPENAI_API_KEY is not configured"

    strict_settings = test_settings.model_copy(update={"nexus_model_validation_mode": "strict"})
    strict = await validate_configured_models(strict_settings)
    assert strict["missing"]
    assert strict["error"] == "OPENAI_API_KEY is not configured"


@pytest.mark.asyncio
async def test_model_validation_paginates_and_caches(
    test_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = test_settings.model_copy(
        update={
            "openai_api_key": SecretStr("test-key"),
            "nexus_model_validation_mode": "strict",
            "nexus_orchestrator_model": "model-a",
            "nexus_specialist_model": "model-b",
            "nexus_guardrail_model": "model-a",
            "nexus_compaction_model": "model-c",
        }
    )
    models = _Models(_Page(["model-a"], _Page(["model-b", "other"])))
    client = _Client(models)

    async def _ensure(_settings: Settings) -> Any:
        return client

    monkeypatch.setattr(sdk_runtime, "ensure", _ensure)
    first = await validate_configured_models(settings)
    second = await validate_configured_models(settings)

    assert first["available"] == ["model-a", "model-b"]
    assert first["missing"] == ["model-c"]
    assert first["cached"] is False
    assert second["cached"] is True
    assert models.calls == 1


@pytest.mark.asyncio
async def test_model_validation_reports_transport_error(
    test_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = test_settings.model_copy(
        update={"openai_api_key": SecretStr("test-key"), "nexus_model_validation_mode": "warn"}
    )
    client = _Client(_Models(error=RuntimeError("network unavailable")))

    async def _ensure(_settings: Settings) -> Any:
        return client

    monkeypatch.setattr(sdk_runtime, "ensure", _ensure)
    result = await validate_configured_models(settings, force=True)
    assert result["checked"] is False
    assert result["error"] == "RuntimeError"
