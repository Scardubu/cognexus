"""Fail-safe redaction for observability-only identifiers."""

from __future__ import annotations

import hashlib
from typing import Any

_SESSION_KEYS = {"session_id", "sessionid", "session-id"}


def _session_reference(value: object) -> str:
    digest = hashlib.sha256(
        f"cognexus-session\0{value}".encode("utf-8", errors="replace")
    ).hexdigest()
    return f"session-ref-{digest[:32]}"


def redact_observability_fields(
    logger: object,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Replace accidentally logged raw session identifiers with stable references."""
    del logger, method_name
    for key in tuple(event_dict):
        if key.lower() not in _SESSION_KEYS:
            continue
        value = event_dict.pop(key)
        event_dict.setdefault("session_ref", _session_reference(value))
    return event_dict


def safe_span_attributes(attributes: dict[str, Any] | None) -> dict[str, Any]:
    """Return scalar span attributes with raw session IDs replaced."""
    safe: dict[str, Any] = {}
    for key, value in (attributes or {}).items():
        if value is None or not isinstance(value, str | bool | int | float):
            continue
        if key.lower().replace("nexus.", "") in _SESSION_KEYS:
            safe["nexus.session_ref"] = _session_reference(value)
        else:
            safe[key] = value
    return safe


__all__ = ["redact_observability_fields", "safe_span_attributes"]
