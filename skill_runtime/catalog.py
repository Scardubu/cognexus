"""Cached construction of the process-wide portable skill registry."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from config.settings import Settings
from skill_runtime.loader import SkillRegistry


@lru_cache(maxsize=16)
def _cached_registry(
    root: str,
    max_skill_bytes: int,
    max_resource_bytes: int,
    max_activation_chars: int,
    cache_ttl_seconds: int,
    allowed_names: tuple[str, ...],
    denied_names: tuple[str, ...],
) -> SkillRegistry:
    return SkillRegistry(
        Path(root),
        max_skill_bytes=max_skill_bytes,
        max_resource_bytes=max_resource_bytes,
        max_activation_chars=max_activation_chars,
        cache_ttl_seconds=cache_ttl_seconds,
        allowed_names=allowed_names,
        denied_names=denied_names,
    )


def get_skill_registry(settings: Settings) -> SkillRegistry:
    """Return a settings-keyed registry safe to reuse across requests."""
    return _cached_registry(
        str(settings.nexus_skills_path.resolve()),
        settings.nexus_skill_max_file_bytes,
        settings.nexus_skill_max_resource_bytes,
        settings.nexus_skill_activation_max_chars,
        settings.nexus_skill_cache_ttl_seconds,
        tuple(sorted(settings.nexus_skill_allowed_names)),
        tuple(sorted(settings.nexus_skill_denied_names)),
    )
