"""Input normalization and prompt-injection heuristics."""

from __future__ import annotations

import re
from dataclasses import dataclass

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
_INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(all|any|the|your)\s+(previous|prior|system)\s+instructions", re.I),
    re.compile(r"reveal\s+(the\s+)?(system|developer)\s+prompt", re.I),
    re.compile(r"(?:act|pretend)\s+as\s+(?:an?\s+)?unrestricted", re.I),
    re.compile(r"disable\s+(?:all\s+)?(?:safety|guardrails|policy)", re.I),
    re.compile(r"BEGIN\s+(?:SYSTEM|DEVELOPER)\s+PROMPT", re.I),
)


@dataclass(frozen=True, slots=True)
class SanitizationResult:
    """Normalized text plus heuristic findings."""

    text: str
    findings: tuple[str, ...]


def sanitize_text(value: str, *, max_chars: int) -> SanitizationResult:
    """Normalize control characters and detect common injection attempts."""
    normalized = _CONTROL_CHARS.sub("", value).strip()
    if len(normalized) > max_chars:
        raise ValueError(f"input exceeds maximum length of {max_chars} characters")
    findings = tuple(
        pattern.pattern for pattern in _INJECTION_PATTERNS if pattern.search(normalized)
    )
    return SanitizationResult(text=normalized, findings=findings)
