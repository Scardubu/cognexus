"""Validation primitives for externally supplied opaque identifiers."""

from __future__ import annotations

import hashlib
import re
from typing import Final
from uuid import uuid4

SESSION_ID_MAX_LENGTH: Final = 128
SESSION_ID_PATTERN_TEXT: Final = r"^[A-Za-z0-9._:-]+$"
SESSION_ID_PATTERN: Final = re.compile(SESSION_ID_PATTERN_TEXT)
REQUEST_ID_MAX_LENGTH: Final = 128
REQUEST_ID_PATTERN_TEXT: Final = r"^[A-Za-z0-9._:-]+$"
REQUEST_ID_PATTERN: Final = re.compile(REQUEST_ID_PATTERN_TEXT)


class InvalidIdentifierError(ValueError):
    """Raised when an external identifier violates the public contract."""


def validate_session_id(value: str) -> str:
    """Return a normalized session identifier or raise a bounded validation error."""
    normalized = value.strip()
    if not normalized:
        raise InvalidIdentifierError("session_id cannot be blank")
    if len(normalized) > SESSION_ID_MAX_LENGTH:
        raise InvalidIdentifierError(f"session_id cannot exceed {SESSION_ID_MAX_LENGTH} characters")
    if SESSION_ID_PATTERN.fullmatch(normalized) is None:
        raise InvalidIdentifierError(
            "session_id may contain only letters, digits, dot, underscore, colon, and hyphen"
        )
    return normalized


def session_observability_reference(value: str) -> str:
    """Return a stable, domain-separated reference without exposing the raw session ID.

    This value is suitable for logs and trace metadata. It is intentionally not part
    of the public API contract and must never be used as an authentication token.
    """
    normalized = validate_session_id(value)
    digest = hashlib.sha256(f"cognexus-session\0{normalized}".encode()).hexdigest()
    return f"session-ref-{digest[:32]}"


def new_request_id() -> str:
    """Return a locally generated, header-safe opaque request identifier."""
    return f"req-{uuid4().hex}"


def normalize_request_id(value: str | None) -> str:
    """Accept one bounded header-safe request ID or generate a safe replacement.

    Request identifiers are echoed in response headers and bound into structured logs.
    Keeping validation in one primitive prevents middleware-order changes from creating
    inconsistent trust boundaries.
    """
    if value is None:
        return new_request_id()
    candidate = value.strip()
    if (
        not candidate
        or len(candidate) > REQUEST_ID_MAX_LENGTH
        or REQUEST_ID_PATTERN.fullmatch(candidate) is None
    ):
        return new_request_id()
    return candidate


def normalize_request_id_header(value: bytes | None) -> str:
    """Decode an ASGI header strictly and normalize it without lossy character removal."""
    if value is None:
        return new_request_id()
    try:
        candidate = value.decode("ascii")
    except UnicodeDecodeError:
        return new_request_id()
    return normalize_request_id(candidate)
