"""Secret presence checks without logging secret values."""

from __future__ import annotations

from config.settings import Settings


def validate_required_secrets(settings: Settings, *, live_run: bool = False) -> list[str]:
    """Return names of missing secrets required for the requested runtime mode."""
    missing: list[str] = []
    if live_run and not settings.openai_api_key:
        missing.append("OPENAI_API_KEY")
    if live_run and not settings.nexus_api_key:
        missing.append("NEXUS_API_KEY")
    return missing
