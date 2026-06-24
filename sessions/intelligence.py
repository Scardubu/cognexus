"""Privacy-preserving session summaries, context signals, and continuity scoring."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.IGNORECASE),
    re.compile(
        r"""["']?\b(?:password|passwd|secret|token|api[_-]?key)\b["']?\s*[:=]\s*"""
        r"""(?:"[^"\r\n]*"|'[^'\r\n]*'|[^\s,;}\]]+)""",
        re.IGNORECASE,
    ),
    re.compile(r"(?<=://)[^/\s:@]+:[^@\s/]+@"),
    re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
)


class SessionIntelligence(BaseModel):
    """Safe metadata describing long-running session continuity."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    rolling_summary: str
    continuity_score: float = Field(ge=0.0, le=1.0)
    context_item_count: int = Field(ge=0)
    represented_item_count: int = Field(ge=0)
    role_counts: dict[str, int]
    compaction_recommended: bool
    context_optimization: str


def _redact(value: str) -> str:
    redacted = value
    for pattern in _SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return " ".join(redacted.split())


def _extract_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content") or item.get("output_text")
                if isinstance(text, str):
                    parts.append(text)
        return " ".join(parts)
    if isinstance(value, dict):
        text = value.get("text") or value.get("content") or value.get("output_text")
        return text if isinstance(text, str) else ""
    return ""


def _item_role(item: Any) -> str:
    if not isinstance(item, dict):
        return type(item).__name__.lower()
    role = item.get("role") or item.get("type") or "unknown"
    return str(role).strip().lower()[:48] or "unknown"


def analyze_session_items(
    items: list[Any],
    *,
    candidate_items: int,
    summary_max_chars: int = 1_200,
    represented_item_limit: int = 12,
) -> SessionIntelligence:
    """Build a bounded rolling summary without retaining secrets or raw identifiers."""
    bounded = items[-max(1, represented_item_limit) :]
    role_counts = Counter(_item_role(item) for item in items)
    fragments: list[str] = []
    for item in bounded:
        role = _item_role(item)
        content = _extract_text(item.get("content", "") if isinstance(item, dict) else item)
        safe = _redact(content)
        if safe:
            fragments.append(f"{role}: {safe[:180]}")
        else:
            fragments.append(f"{role}: [{role} item]")

    summary = " | ".join(fragments)
    if len(summary) > summary_max_chars:
        summary = summary[: max(0, summary_max_chars - 1)].rstrip() + "…"
    if not summary:
        summary = "No retained conversational items."

    item_count = len(items)
    user_count = role_counts.get("user", 0)
    assistant_count = role_counts.get("assistant", 0)
    paired_turns = min(user_count, assistant_count)
    turn_balance = paired_turns / max(1, max(user_count, assistant_count))
    depth = min(1.0, item_count / max(2, candidate_items))
    diversity = min(1.0, len(role_counts) / 3.0)
    continuity = min(
        1.0,
        (0.15 if item_count else 0.0) + (0.45 * depth) + (0.25 * turn_balance) + (0.15 * diversity),
    )
    recommended = item_count >= candidate_items
    optimization = (
        "sdk_compaction_candidate"
        if recommended
        else "rolling_window_healthy"
        if item_count
        else "empty_session"
    )
    return SessionIntelligence(
        rolling_summary=summary,
        continuity_score=round(continuity, 4),
        context_item_count=item_count,
        represented_item_count=len(bounded),
        role_counts=dict(sorted(role_counts.items())),
        compaction_recommended=recommended,
        context_optimization=optimization,
    )


__all__ = ["SessionIntelligence", "analyze_session_items"]
