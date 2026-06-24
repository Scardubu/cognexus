"""Shared pytest fixtures."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from config.settings import Settings


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    """Return isolated test settings without network dependencies."""
    return Settings(
        nexus_env="test",
        nexus_model_validation_mode="off",
        nexus_session_backend="sqlite",
        nexus_sqlite_path=tmp_path / "sessions.db",
        nexus_compaction_enabled=False,
        nexus_otel_enabled=False,
        nexus_enable_docs=False,
        nexus_trusted_hosts=["testserver", "localhost", "127.0.0.1"],
    )


@pytest.fixture(autouse=True)
def clean_openai_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent accidental live OpenAI calls in unit tests."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    os.environ.setdefault("NEXUS_MODEL_VALIDATION_MODE", "off")
