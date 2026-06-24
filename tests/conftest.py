"""Shared pytest fixtures."""

from __future__ import annotations

import os
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

from config.settings import Settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_TMP_ROOT = PROJECT_ROOT / "artifacts" / "test-tmp"
os.environ.setdefault("NEXUS_DISABLE_DOTENV", "true")
os.environ.setdefault("NEXUS_MODEL_VALIDATION_MODE", "off")


@pytest.fixture
def tmp_path() -> Iterator[Path]:
    """Return an isolated temporary directory without pytest's tmpdir plugin."""
    TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TEST_TMP_ROOT / os.urandom(8).hex()
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


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
    monkeypatch.delenv("NEXUS_API_KEY", raising=False)
    monkeypatch.setenv("NEXUS_DISABLE_DOTENV", "true")
    monkeypatch.setenv("NEXUS_MODEL_VALIDATION_MODE", "off")
