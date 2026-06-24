"""Fail-safe redaction for observability-only identifiers."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

_SESSION_KEYS = {"session_id", "sessionid", "session-id", "session.id"}


def _session_reference(value: object) -> str:
    digest = hashlib.sha256(
        f"cognexus-session\0{value}".encode("utf-8", errors="replace")
    ).hexdigest()
    return f"session-ref-{digest[:32]}"


def _is_session_key(key: object) -> bool:
    if not isinstance(key, str):
        return False
    normalized = key.strip().lower()
    if normalized.startswith("nexus."):
        normalized = normalized.removeprefix("nexus.")
    return normalized in _SESSION_KEYS


def _redact_nested(value: object) -> object:
    if isinstance(value, Mapping):
        safe: dict[object, object] = {}
        for key, item in value.items():
            if _is_session_key(key):
                safe.setdefault("session_ref", _session_reference(item))
            else:
                safe[key] = _redact_nested(item)
        return safe
    if isinstance(value, list):
        return [_redact_nested(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_nested(item) for item in value)
    return value


def redact_observability_fields(
    logger: object,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Recursively replace accidentally logged raw session identifiers with references."""
    del logger, method_name
    redacted = _redact_nested(event_dict)
    if not isinstance(redacted, dict):  # pragma: no cover - event_dict is always a mapping
        return {}
    return {str(key): value for key, value in redacted.items()}


def safe_span_attributes(attributes: dict[str, Any] | None) -> dict[str, Any]:
    """Return scalar span attributes with raw session IDs replaced."""
    safe: dict[str, Any] = {}
    for key, value in (attributes or {}).items():
        if value is None or not isinstance(value, str | bool | int | float):
            continue
        if _is_session_key(key):
            safe["nexus.session_ref"] = _session_reference(value)
        else:
            safe[key] = value
    return safe


__all__ = ["redact_observability_fields", "safe_span_attributes"]
