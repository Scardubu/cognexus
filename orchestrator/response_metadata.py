"""Deterministic extraction of additive response metadata."""

from __future__ import annotations

import re
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from orchestrator.execution_modes import ExecutionMode
from orchestrator.skill_recommender import SkillRecommendation
from orchestrator.tier_classifier import ClassificationResult

_HEADING: Final = re.compile(r"^(?:#{1,6}\s*)?([A-Za-z][A-Za-z ]{1,40})\s*:?\s*$")
_BULLET: Final = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+(.+?)\s*$")


class ResponseMetadata(BaseModel):
    """Machine-readable quality metadata derived without another model call."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    next_actions: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_skills: list[SkillRecommendation] = Field(default_factory=list)
    execution_mode: ExecutionMode


def _extract_section(text: str, names: tuple[str, ...]) -> list[str]:
    targets = {name.lower() for name in names}
    collecting = False
    values: list[str] = []
    for line in text.splitlines():
        heading = _HEADING.match(line.strip())
        if heading:
            normalized = " ".join(heading.group(1).lower().split())
            if normalized in targets:
                collecting = True
                continue
            if collecting:
                break
        if not collecting:
            continue
        bullet = _BULLET.match(line)
        if bullet:
            value = " ".join(bullet.group(1).split())
            if value and value not in values:
                values.append(value[:500])
        elif line.strip() and values:
            break
    return values[:12]


def derive_response_metadata(
    response_text: str,
    *,
    classification: ClassificationResult,
    execution_mode: ExecutionMode,
    recommendations: list[SkillRecommendation],
    validated: bool,
) -> ResponseMetadata:
    """Extract explicit sections and compute a bounded orchestration confidence."""
    recommendation_signal = (
        sum(item.confidence for item in recommendations) / len(recommendations)
        if recommendations
        else 0.0
    )
    confidence = classification.confidence + (0.04 if validated else -0.15)
    confidence += min(0.03, recommendation_signal * 0.03)
    if classification.ambiguity == "high":
        confidence -= 0.08
    elif classification.ambiguity == "medium":
        confidence -= 0.03
    return ResponseMetadata(
        next_actions=_extract_section(
            response_text, ("next actions", "follow-up actions", "actions")
        ),
        assumptions=_extract_section(response_text, ("assumptions",)),
        open_questions=_extract_section(response_text, ("open questions", "unresolved questions")),
        confidence=round(min(1.0, max(0.0, confidence)), 4),
        recommended_skills=recommendations,
        execution_mode=execution_mode,
    )


__all__ = ["ResponseMetadata", "derive_response_metadata"]
