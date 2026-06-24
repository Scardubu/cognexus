"""Deterministic, ambiguity-aware pre-classification for Cognexus routing."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Final, Literal

AmbiguityLevel = Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    """Intent classification used for routing, recommendations, and trace generation."""

    tier: int
    tier_name: str
    app_context: str
    intent: str
    confidence: float
    supporting_tiers: tuple[int, ...] = ()
    hybrid_intents: tuple[str, ...] = ()
    ambiguity: AmbiguityLevel = "low"
    ambiguity_reason: str | None = None
    matched_terms: tuple[str, ...] = ()
    expert_override_applied: bool = False


_TIER_PATTERNS: Final[tuple[tuple[int, str, tuple[str, ...]], ...]] = (
    (
        1,
        "Security & Safety",
        (
            "security",
            "auth",
            "secret",
            "vulnerability",
            "injection",
            "compliance",
            "breach",
            "exploit",
        ),
    ),
    (
        2,
        "Correctness & Stability",
        ("bug", "error", "test", "typescript", "lint", "correctness", "failure", "regression"),
    ),
    (
        3,
        "Performance & Scalability",
        (
            "performance",
            "latency",
            "cache",
            "memory",
            "scale",
            "profile",
            "throughput",
            "concurrency",
        ),
    ),
    (
        4,
        "Architecture & Design",
        (
            "architecture",
            "design",
            "refactor",
            "api",
            "database",
            "system",
            "contract",
            "migration",
        ),
    ),
    (
        5,
        "AI Engineering",
        ("agent", "prompt", "llm", "rag", "model", "openai", "machine learning", "orchestration"),
    ),
    (
        6,
        "Release / Productivity / Tooling",
        ("deploy", "release", "ci", "docker", "git", "vscode", "incident", "sbom", "provenance"),
    ),
    (
        7,
        "UX / UI / Motion",
        ("ui", "ux", "motion", "animation", "accessibility", "typography", "color", "interface"),
    ),
    (
        8,
        "Vertical Domain Compliance",
        ("firs", "tax", "vat", "cit", "wht", "invoice", "betting", "fintech"),
    ),
)
_TIER_NAMES: Final[dict[int, str]] = {tier: name for tier, name, _ in _TIER_PATTERNS}


def _score_message(message: str) -> tuple[dict[int, int], dict[int, tuple[str, ...]]]:
    lower = message.lower()
    scores: dict[int, int] = {}
    matches: dict[int, tuple[str, ...]] = {}
    for tier, _name, terms in _TIER_PATTERNS:
        found = tuple(term for term in terms if re.search(rf"\b{re.escape(term)}\b", lower))
        scores[tier] = len(found)
        matches[tier] = found
    return scores, matches


def classify_task(message: str, *, expert_override: int | None = None) -> ClassificationResult:
    """Classify a task with hybrid-intent metadata and an explicit expert override."""
    normalized = " ".join(message.strip().split())
    scores, matches = _score_message(normalized)
    ranked = sorted(scores, key=lambda tier: (-scores[tier], tier))
    best_tier = ranked[0] if ranked else 4
    best_score = scores.get(best_tier, 0)
    second_score = scores.get(ranked[1], 0) if len(ranked) > 1 else 0

    if best_score == 0:
        best_tier = 4
        confidence = 0.35
        ambiguity: AmbiguityLevel = "high"
        ambiguity_reason = "No material tier-specific terms were detected; architecture is the conservative default."
        material_tiers: list[int] = []
    else:
        dominance = (best_score - second_score) / max(best_score, 1)
        coverage = min(1.0, sum(scores.values()) / 8.0)
        confidence = min(0.98, 0.56 + (0.24 * dominance) + (0.16 * coverage))
        material_threshold = max(1, math.ceil(best_score * 0.5))
        material_tiers = [tier for tier in ranked if scores[tier] >= material_threshold]
        if best_score == second_score:
            ambiguity = "high"
            ambiguity_reason = "Multiple tiers have equal evidence; deterministic numeric priority resolved the tie."
            confidence = min(confidence, 0.62)
        elif len(material_tiers) > 1:
            ambiguity = "medium"
            ambiguity_reason = "The request contains multiple material intents; one primary tier and supporting tiers were selected."
        else:
            ambiguity = "low"
            ambiguity_reason = None

    override_applied = expert_override is not None
    if expert_override is not None:
        if expert_override not in _TIER_NAMES:
            raise ValueError("expert_override must be an integer from 1 through 8")
        if expert_override != best_tier and best_tier not in material_tiers and best_score > 0:
            material_tiers.append(best_tier)
        best_tier = expert_override
        confidence = max(confidence, 0.9)
        ambiguity_reason = f"Expert tier override selected tier {expert_override}; deterministic evidence is retained as supporting metadata."

    supporting = tuple(tier for tier in material_tiers if tier != best_tier)[:3]
    hybrid = tuple(_TIER_NAMES[tier] for tier in (best_tier, *supporting))
    matched = tuple(
        dict.fromkeys(term for tier in (best_tier, *supporting) for term in matches[tier])
    )
    lower = normalized.lower()
    app = next(
        (
            candidate
            for candidate in ("TaxBridge", "SabiScore", "Hashablanca", "SwarmX")
            if candidate.lower() in lower
        ),
        "None",
    )
    return ClassificationResult(
        tier=best_tier,
        tier_name=_TIER_NAMES[best_tier],
        app_context=app,
        intent=normalized[:150],
        confidence=round(confidence, 4),
        supporting_tiers=supporting,
        hybrid_intents=hybrid,
        ambiguity=ambiguity,
        ambiguity_reason=ambiguity_reason,
        matched_terms=matched,
        expert_override_applied=override_applied,
    )
