"""Evidence-weighted deterministic conflict resolution for specialist recommendations."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Candidate:
    """One specialist result with bounded confidence and source-quality metadata."""

    source: str
    tier: int
    output: dict[str, Any]
    confidence: float = 0.5
    source_quality: float = 0.5

    def __post_init__(self) -> None:
        if not 1 <= self.tier <= 8:
            raise ValueError("tier must be between 1 and 8")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not 0.0 <= self.source_quality <= 1.0:
            raise ValueError("source_quality must be between 0 and 1")

    @property
    def weighted_score(self) -> float:
        """Return a deterministic score that preserves tier priority."""
        tier_component = (9 - self.tier) / 8
        return round(
            (0.5 * tier_component) + (0.3 * self.confidence) + (0.2 * self.source_quality), 6
        )


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _recommendation_identity(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("id", "title", "recommendation", "action", "summary"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return f"text:{_normalize_text(candidate)}"
        return "json:" + json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    if isinstance(value, str):
        return f"text:{_normalize_text(value)}"
    return "json:" + json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def resolve_conflicts(candidates: list[Candidate]) -> dict[str, Any]:
    """Merge outputs by weighted evidence, eliminate duplicates, and explain ordering."""
    ordered = sorted(
        candidates,
        key=lambda item: (-item.weighted_score, item.tier, item.source.lower()),
    )
    recommendations: list[Any] = []
    recommendation_sources: list[dict[str, Any]] = []
    caveats: list[str] = []
    seen_recommendations: set[str] = set()
    seen_caveats: set[str] = set()

    for candidate in ordered:
        for recommendation in candidate.output.get("recommendations", []):
            identity = _recommendation_identity(recommendation)
            if identity in seen_recommendations:
                continue
            seen_recommendations.add(identity)
            recommendations.append(recommendation)
            recommendation_sources.append(
                {
                    "source": candidate.source,
                    "tier": candidate.tier,
                    "weighted_score": candidate.weighted_score,
                }
            )
        for raw_caveat in candidate.output.get("caveats", []):
            caveat = str(raw_caveat).strip()
            identity = _normalize_text(caveat)
            if not caveat or identity in seen_caveats:
                continue
            seen_caveats.add(identity)
            caveats.append(caveat)

    score_set = {item.weighted_score for item in ordered}
    if len(ordered) <= 1:
        summary = "NONE"
    elif len(score_set) == 1:
        summary = "RESOLVED_BY_TIER_THEN_SOURCE"
    else:
        summary = "RESOLVED_BY_WEIGHTED_EVIDENCE"

    return {
        "conflict_summary": summary,
        "recommendations": recommendations,
        "recommendation_sources": recommendation_sources,
        "caveats": caveats,
        "sources": [item.source for item in ordered],
        "resolution_metadata": {
            "candidate_count": len(ordered),
            "duplicate_recommendations_removed": sum(
                len(item.output.get("recommendations", [])) for item in ordered
            )
            - len(recommendations),
            "ordering": [
                {
                    "source": item.source,
                    "tier": item.tier,
                    "confidence": item.confidence,
                    "source_quality": item.source_quality,
                    "weighted_score": item.weighted_score,
                }
                for item in ordered
            ],
            "tie_breaker": "weighted_score desc, tier asc, source asc",
        },
    }
