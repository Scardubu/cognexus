"""Configuration-backed model routing and bounded live model validation."""

from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import dataclass
from typing import Any

from config.settings import Settings, get_settings
from observability.metrics import metrics
from orchestrator.runtime import sdk_runtime


@dataclass(frozen=True, slots=True)
class ModelRoute:
    """Resolved models for one orchestration request."""

    orchestrator: str
    specialist: str
    guardrail: str
    compaction: str


def route_models(tier: int, settings: Settings | None = None) -> ModelRoute:
    """Resolve model names solely from validated configuration.

    ``tier`` remains part of the interface so future configuration can route tiers
    differently without changing callers. The stabilized baseline intentionally uses
    one configured model per role.
    """
    del tier
    cfg = settings or get_settings()
    return ModelRoute(
        orchestrator=cfg.nexus_orchestrator_model,
        specialist=cfg.nexus_specialist_model,
        guardrail=cfg.nexus_guardrail_model,
        compaction=cfg.nexus_compaction_model,
    )


class _ModelValidationCache:
    """Account-scoped validation cache with bounded provider pagination."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._entries: dict[tuple[str, ...], tuple[float, dict[str, Any]]] = {}

    @staticmethod
    def _key(settings: Settings, configured: tuple[str, ...]) -> tuple[str, ...]:
        key = settings.openai_key_value or ""
        fingerprint = hashlib.blake2s(key.encode("utf-8"), digest_size=8).hexdigest()
        return (*configured, settings.nexus_model_validation_mode, fingerprint)

    async def get(
        self,
        settings: Settings,
        *,
        force: bool = False,
    ) -> dict[str, Any]:
        configured = tuple(
            sorted(
                {
                    settings.nexus_orchestrator_model,
                    settings.nexus_specialist_model,
                    settings.nexus_guardrail_model,
                    settings.nexus_compaction_model,
                }
            )
        )
        if settings.nexus_model_validation_mode == "off":
            return {"checked": False, "available": [], "missing": [], "cached": False}
        if not settings.openai_key_value:
            message = "OPENAI_API_KEY is not configured"
            if settings.nexus_model_validation_mode == "strict":
                return {
                    "checked": False,
                    "available": [],
                    "missing": list(configured),
                    "error": message,
                    "cached": False,
                }
            return {
                "checked": False,
                "available": [],
                "missing": [],
                "warning": message,
                "cached": False,
            }

        cache_key = self._key(settings, configured)
        now = time.monotonic()
        cached = self._entries.get(cache_key)
        if not force and cached is not None and cached[0] > now:
            return {**cached[1], "cached": True}

        async with self._lock:
            now = time.monotonic()
            cached = self._entries.get(cache_key)
            if not force and cached is not None and cached[0] > now:
                return {**cached[1], "cached": True}

            client = await sdk_runtime.ensure(settings)
            available_ids: set[str] = set()
            try:
                page = await client.models.list()
                pages_read = 0
                while True:
                    pages_read += 1
                    available_ids.update(item.id for item in page.data)
                    if not page.has_next_page():
                        break
                    if pages_read >= settings.nexus_model_validation_max_pages:
                        raise RuntimeError("model catalog pagination limit exceeded")
                    page = await page.get_next_page()
            except Exception as exc:
                metrics.model_validation.labels("error").inc()
                result: dict[str, Any] = {
                    "checked": False,
                    "available": [],
                    "missing": [],
                    "error": type(exc).__name__,
                    "cached": False,
                }
                self._entries[cache_key] = (
                    now + settings.nexus_model_validation_error_ttl_seconds,
                    result,
                )
                return result

            missing = sorted(set(configured) - available_ids)
            result = {
                "checked": True,
                "available": sorted(set(configured) & available_ids),
                "missing": missing,
                "cached": False,
            }
            status = "missing" if missing else "success"
            metrics.model_validation.labels(status).inc()
            self._entries[cache_key] = (
                now + settings.nexus_model_validation_ttl_seconds,
                result,
            )
            return result

    def clear(self) -> None:
        self._entries.clear()


_model_validation_cache = _ModelValidationCache()


async def validate_configured_models(
    settings: Settings | None = None,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """Validate configured IDs through the Models API with a bounded process cache."""
    return await _model_validation_cache.get(settings or get_settings(), force=force)


def reset_model_validation_cache() -> None:
    """Clear validation cache for tests or controlled configuration reloads."""
    _model_validation_cache.clear()
