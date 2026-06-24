"""Rate-limit primitives used by FastAPI."""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from config.settings import Settings


def create_limiter(settings: Settings) -> Limiter:
    """Create a fail-closed limiter with shared storage for live Redis deployments."""
    return Limiter(
        key_func=get_remote_address,
        headers_enabled=True,
        storage_uri=settings.effective_rate_limit_storage_uri,
        key_prefix="cognexus",
        swallow_errors=False,
        in_memory_fallback_enabled=False,
    )
