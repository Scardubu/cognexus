"""Regression tests for enterprise security and resilience invariants."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from agents import RunContextWrapper, Runner
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError

from config.settings import Settings
from middleware.input_guardrail import create_input_guardrail
from orchestrator.model_router import reset_model_validation_cache, validate_configured_models
from orchestrator.runtime import sdk_runtime
from orchestrator.tier_classifier import classify_task
from security.identifiers import (
    normalize_request_id,
    normalize_request_id_header,
    session_observability_reference,
)
from security.secrets import validate_required_secrets
from server.app import create_app
from server.body_limit import RequestBodyLimitMiddleware
from sessions.session_manager import SessionManager
from skill_runtime.loader import SkillRegistry


def _production_settings(tmp_path: Path, **updates: Any) -> Settings:
    values: dict[str, Any] = {
        "nexus_env": "production",
        "openai_api_key": SecretStr("sk-proj-Q7x9m2R4t6V8y1B3c5D7f9H2J4K6M8N0"),
        "nexus_api_key": SecretStr("svc_A8c2E4g6I8k0M2o4Q6s8U0w2Y4a6C8e0"),
        "nexus_session_backend": "redis",
        "nexus_allow_sqlite_fallback": False,
        "nexus_cors_origins": ["https://console.example.com"],
        "nexus_trusted_hosts": ["api.example.com"],
        "nexus_sqlite_path": tmp_path / "unused.db",
        "nexus_model_validation_mode": "off",
        "nexus_otel_enabled": False,
    }
    values.update(updates)
    return Settings(**values)


def test_production_rejects_weak_or_reused_service_keys(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="at least 32"):
        _production_settings(tmp_path, nexus_api_key=SecretStr("too-short"))

    shared = SecretStr("same_A8c2E4g6I8k0M2o4Q6s8U0w2Y4a6C8e0")
    with pytest.raises(ValidationError, match="distinct"):
        _production_settings(tmp_path, openai_api_key=shared, nexus_api_key=shared)


def test_production_rejects_unsafe_network_and_fallback_policy(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="wildcard trusted hosts"):
        _production_settings(tmp_path, nexus_trusted_hosts=["*"])
    with pytest.raises(ValidationError, match="SQLITE_FALLBACK=false"):
        _production_settings(tmp_path, nexus_allow_sqlite_fallback=True)
    with pytest.raises(ValidationError, match="paths, queries, or fragments"):
        Settings(nexus_cors_origins=["https://example.com/path"])


def test_request_body_limit_and_session_path_validation(test_settings: Settings) -> None:
    settings = test_settings.model_copy(
        update={"nexus_max_input_chars": 100, "nexus_max_request_bytes": 1024}
    )
    with TestClient(create_app(settings)) as client:
        oversized = client.post(
            "/v1/run",
            json={"message": "x" * 2_000, "dry_run": True},
        )
        invalid_path = client.get("/v1/sessions/not%20allowed")

    assert oversized.status_code == 413
    assert oversized.json()["error"] == "request_body_too_large"
    assert invalid_path.status_code == 422


def test_api_docs_follow_service_authentication(test_settings: Settings) -> None:
    settings = test_settings.model_copy(
        update={
            "nexus_api_key": SecretStr("documentation-test-key"),
            "nexus_enable_docs": True,
        }
    )
    with TestClient(create_app(settings)) as client:
        denied = client.get("/docs")
        allowed = client.get("/docs", headers={"X-API-Key": "documentation-test-key"})
        schema = client.get(
            "/openapi.json", headers={"Authorization": "Bearer documentation-test-key"}
        )

    assert denied.status_code == 401
    assert allowed.status_code == 200
    assert schema.status_code == 200
    assert schema.json()["info"]["title"] == "Cognexus Production API"


def test_api_auth_accepts_either_valid_credential_when_both_are_present(
    test_settings: Settings,
) -> None:
    settings = test_settings.model_copy(
        update={"nexus_api_key": SecretStr("credential-precedence-test-key")}
    )
    with TestClient(create_app(settings)) as client:
        valid_bearer = client.get(
            "/v1/skills",
            headers={
                "X-API-Key": "invalid-x-api-key",
                "Authorization": "Bearer credential-precedence-test-key",
            },
        )
        valid_header = client.get(
            "/v1/skills",
            headers={
                "X-API-Key": "credential-precedence-test-key",
                "Authorization": "Bearer invalid-bearer",
            },
        )

    assert valid_bearer.status_code == 200
    assert valid_header.status_code == 200


def test_oversized_rejection_replaces_untrusted_request_id(test_settings: Settings) -> None:
    settings = test_settings.model_copy(
        update={"nexus_max_input_chars": 100, "nexus_max_request_bytes": 1024}
    )
    with TestClient(create_app(settings)) as client:
        response = client.post(
            "/v1/run",
            headers={"X-Request-ID": "invalid/request/id"},
            content=b"x" * 2_000,
        )

    request_id = response.headers["X-Request-ID"]
    assert response.status_code == 413
    assert request_id.startswith("req-")
    assert response.json()["request_id"] == request_id
    assert normalize_request_id(" trusted-id ") == "trusted-id"
    assert normalize_request_id_header(b"trusted-id") == "trusted-id"
    assert normalize_request_id_header(b"trusted-\xff-id").startswith("req-")


def test_body_limit_revalidates_request_id_from_asgi_state() -> None:
    scope: dict[str, Any] = {"state": {"request_id": "invalid/request/id"}}
    request_id = RequestBodyLimitMiddleware._request_id(scope, {})

    assert request_id.startswith("req-")
    assert scope["state"]["request_id"] == request_id


@pytest.mark.asyncio
async def test_failed_session_creation_does_not_leak_lock(
    test_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    manager = SessionManager(test_settings)

    async def fail(_session_id: str) -> Any:
        raise RuntimeError("backend failed")

    monkeypatch.setattr(manager, "_resolve_handle", fail)
    with pytest.raises(RuntimeError, match="backend failed"):
        await manager.get_handle("creation-failure")
    assert manager._creation_locks == {}
    await manager.close()


class _FailingModels:
    def __init__(self) -> None:
        self.calls = 0

    async def list(self) -> Any:
        self.calls += 1
        raise RuntimeError("provider unavailable")


class _Client:
    def __init__(self, models: Any) -> None:
        self.models = models


@pytest.mark.asyncio
async def test_model_validation_errors_are_cached_by_account(
    test_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    reset_model_validation_cache()
    models = _FailingModels()
    client = _Client(models)

    async def ensure(_settings: Settings) -> Any:
        return client

    monkeypatch.setattr(sdk_runtime, "ensure", ensure)
    first_settings = test_settings.model_copy(
        update={
            "openai_api_key": SecretStr("account-one"),
            "nexus_model_validation_mode": "warn",
        }
    )
    second_settings = first_settings.model_copy(update={"openai_api_key": SecretStr("account-two")})

    first = await validate_configured_models(first_settings)
    cached = await validate_configured_models(first_settings)
    separate_account = await validate_configured_models(second_settings)

    assert first["cached"] is False
    assert cached["cached"] is True
    assert separate_account["cached"] is False
    assert models.calls == 2


@pytest.mark.asyncio
async def test_configured_sdk_input_guardrail_uses_runtime_limit() -> None:
    guardrail = create_input_guardrail(100)
    context = RunContextWrapper(context=None)

    accepted = await guardrail.guardrail_function(context, object(), "x" * 100)
    rejected = await guardrail.guardrail_function(context, object(), "x" * 101)

    assert accepted.tripwire_triggered is False
    assert rejected.tripwire_triggered is True
    assert "maximum length" in rejected.output_info["reason"]


def test_skill_frontmatter_rejects_yaml_aliases(tmp_path: Path) -> None:
    skill = tmp_path / "unsafe-yaml"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: unsafe-yaml\n"
        "description: &description Use for unsafe YAML tests.\n"
        "compatibility: *description\n"
        "---\n"
        "# Unsafe\n",
        encoding="utf-8",
    )
    registry = SkillRegistry(tmp_path)
    registry.refresh(force=True)
    assert registry.metadata() == ()
    assert any("anchors and aliases" in issue.message for issue in registry.issues())


def test_validate_required_secrets_skips_check_outside_live_run(
    test_settings: Settings,
) -> None:
    assert test_settings.openai_api_key is None
    assert validate_required_secrets(test_settings, live_run=False) == []


def test_validate_required_secrets_reports_missing_key_on_live_run(
    test_settings: Settings,
) -> None:
    assert validate_required_secrets(test_settings, live_run=True) == [
        "OPENAI_API_KEY",
        "NEXUS_API_KEY",
    ]

    configured = test_settings.model_copy(
        update={
            "openai_api_key": SecretStr("sk-proj-R8t6Y4u2I0o9P7a5S3d1F8g6H4j2K0l9"),
            "nexus_api_key": SecretStr("svc_Z9x7C5v3B1n8M6q4W2e0R9t7Y5u3I1o8"),
        }
    )
    assert validate_required_secrets(configured, live_run=True) == []


def test_readiness_reports_missing_live_credentials(test_settings: Settings) -> None:
    settings = test_settings.model_copy(update={"nexus_env": "staging"})
    with TestClient(create_app(settings)) as client:
        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["details"]["missing_secrets"] == [
        "OPENAI_API_KEY",
        "NEXUS_API_KEY",
    ]


def test_live_settings_reject_placeholder_secrets_and_proxy_wildcards(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="non-placeholder"):
        _production_settings(
            tmp_path, nexus_api_key=SecretStr("replace-with-at-least-32-random-characters")
        )
    with pytest.raises(ValidationError, match="forwarded-header trust"):
        _production_settings(tmp_path, nexus_forwarded_allow_ips="*")
    with pytest.raises(ValidationError, match="wildcards must use"):
        Settings(nexus_trusted_hosts=["*example.com"])


def test_staging_protected_routes_fail_closed_without_service_key(test_settings: Settings) -> None:
    settings = test_settings.model_copy(update={"nexus_env": "staging"})
    with TestClient(create_app(settings)) as client:
        response = client.get("/v1/skills")

    assert response.status_code == 503
    assert response.json()["message"] == "service authentication is not configured"


def test_live_redis_uses_shared_rate_limit_storage(tmp_path: Path) -> None:
    settings = Settings(
        nexus_env="staging",
        nexus_session_backend="redis",
        redis_url="rediss://redis.example.internal:6380/0",
        nexus_allow_sqlite_fallback=False,
        nexus_sqlite_path=tmp_path / "unused.db",
        nexus_compaction_enabled=False,
        nexus_model_validation_mode="off",
    )
    assert settings.effective_rate_limit_storage_uri == settings.redis_url

    with pytest.raises(ValidationError, match="shared Redis rate-limit storage"):
        Settings(
            nexus_env="staging",
            nexus_session_backend="redis",
            redis_url="rediss://redis.example.internal:6380/0",
            nexus_rate_limit_storage_uri="memory://",
            nexus_allow_sqlite_fallback=False,
            nexus_sqlite_path=tmp_path / "unused.db",
            nexus_compaction_enabled=False,
            nexus_model_validation_mode="off",
        )


def test_session_observability_reference_is_stable_and_non_raw() -> None:
    first = session_observability_reference("customer-session-123")
    second = session_observability_reference("customer-session-123")
    different = session_observability_reference("customer-session-456")

    assert first == second
    assert first != different
    assert first.startswith("session-ref-")
    assert "customer-session-123" not in first
    assert len(first) == len("session-ref-") + 32


def test_live_multi_worker_session_topologies_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="multi-worker staging and production"):
        Settings(
            nexus_env="staging",
            nexus_workers=2,
            nexus_session_backend="sqlite",
            nexus_sqlite_path=tmp_path / "unsafe.db",
            nexus_compaction_enabled=False,
            nexus_model_validation_mode="off",
        )

    with pytest.raises(ValidationError, match="NEXUS_ALLOW_SQLITE_FALLBACK=false"):
        Settings(
            nexus_env="staging",
            nexus_workers=2,
            nexus_session_backend="redis",
            nexus_allow_sqlite_fallback=True,
            redis_url="redis://redis.example.internal:6379/0",
            nexus_sqlite_path=tmp_path / "fallback.db",
            nexus_compaction_enabled=False,
            nexus_model_validation_mode="off",
        )


@pytest.mark.asyncio
async def test_run_config_uses_non_raw_session_reference(
    test_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    from types import SimpleNamespace

    from orchestrator import nexus_agent as nexus_agent_module

    captured: dict[str, str] = {}
    raw_session_id = "customer-session-sensitive-123"

    async def ensure(_settings: Settings) -> object:
        return object()

    async def fake_run(_agent: object, message: str, **kwargs: Any) -> Any:
        run_config = kwargs["run_config"]
        captured["group_id"] = run_config.group_id
        classification = classify_task(message)
        return SimpleNamespace(
            final_output=nexus_agent_module._dry_run_response(classification),
            context_wrapper=None,
        )

    monkeypatch.setattr(sdk_runtime, "ensure", ensure)
    monkeypatch.setattr(nexus_agent_module, "build_nexus_agent", lambda _settings: object())
    monkeypatch.setattr(Runner, "run", fake_run)

    manager = SessionManager(test_settings)
    try:
        result = await nexus_agent_module.run_nexus(
            "Analyze this architecture.",
            session_id=raw_session_id,
            settings=test_settings,
            session_manager=manager,
        )
    finally:
        await manager.close()

    assert result.session_id == raw_session_id
    assert captured["group_id"] == session_observability_reference(raw_session_id)
    assert raw_session_id not in captured["group_id"]
