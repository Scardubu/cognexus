"""Authenticated skill catalog API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from config.settings import Settings
from server.app import create_app


def _settings(tmp_path: object) -> Settings:
    return Settings(
        nexus_env="test",
        nexus_model_validation_mode="off",
        nexus_session_backend="sqlite",
        nexus_sqlite_path=tmp_path / "skill-api.db",  # type: ignore[operator]
        nexus_compaction_enabled=False,
        nexus_otel_enabled=False,
        nexus_enable_docs=False,
        nexus_trusted_hosts=["testserver"],
    )


def test_skill_catalog_and_detail(tmp_path: object) -> None:
    app = create_app(_settings(tmp_path))
    with TestClient(app) as client:
        catalog = client.get("/v1/skills")
        detail = client.get("/v1/skills/testing-strategy-architect")
    assert catalog.status_code == 200
    assert catalog.json()["count"] == 39
    assert detail.status_code == 200
    assert detail.json()["name"] == "testing-strategy-architect"
    assert any(item["path"] == "references/guidance.md" for item in detail.json()["resources"])


def test_unknown_skill_returns_structured_404(tmp_path: object) -> None:
    app = create_app(_settings(tmp_path))
    with TestClient(app) as client:
        response = client.get("/v1/skills/not-installed")
    assert response.status_code == 404
    assert response.json()["error"] == "skill_not_found"
