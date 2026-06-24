"""Mode-aware deterministic skill recommendations for Cognexus."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from orchestrator.execution_modes import ExecutionMode, get_execution_mode_profile
from orchestrator.tier_classifier import ClassificationResult
from skill_runtime.loader import SkillRegistry
from skill_runtime.models import SkillMetadata, SkillRisk


class SkillRecommendation(BaseModel):
    """One explainable recommendation safe for API and orchestration responses."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    activation_suggested: bool
    category: str
    risk: SkillRisk


_TIER_HINTS: Final[dict[int, tuple[str, ...]]] = {
    1: ("security-hardening-auditor", "nigerian-fintech-compliance-architect"),
    2: (
        "testing-strategy-architect",
        "api-contract-governance-architect",
        "component-quality-gate",
    ),
    3: (
        "opentelemetry-observability-architect",
        "nextjs-performance-architect",
        "edge-cache-architecture-architect",
    ),
    4: (
        "multi-agent-orchestration-architect",
        "backend-domain-model-architect",
        "prisma-database-architect",
    ),
    5: ("prompt-engineering-architect", "ai-feature-architect", "agent-prompt-upgrade"),
    6: ("release-incident-operations-architect", "git-workflow-architect", "vscode-ai-agent-stack"),
    7: (
        "frontend-product-design-architect",
        "accessibility-system-architect",
        "motion-performance-architect",
    ),
    8: ("nigerian-fintech-compliance-architect", "api-contract-governance-architect"),
}

_TOKEN_PATTERN: Final = re.compile(r"[a-z0-9]+(?:\.[a-z0-9]+)?")
_TOKEN_ALIASES: Final[dict[str, str]] = {
    "api's": "api",
    "apis": "api",
    "cached": "cache",
    "caches": "cache",
    "caching": "cache",
    "compatibility": "contract",
    "contracts": "contract",
    "databases": "database",
    "deployed": "deploy",
    "deploying": "deploy",
    "deployment": "deploy",
    "deployments": "deploy",
    "incidents": "incident",
    "llms": "llm",
    "migrations": "migration",
    "next.js": "nextjs",
    "portfolios": "portfolio",
    "releases": "release",
    "scalability": "scale",
    "scaling": "scale",
    "schemas": "schema",
    "sessions": "session",
    "tests": "test",
    "testing": "test",
    "webhooks": "webhook",
}
_GENERIC_TERMS: Final[frozenset[str]] = frozenset(
    {
        "a",
        "an",
        "and",
        "app",
        "apps",
        "application",
        "applications",
        "analysis",
        "analyze",
        "analyzes",
        "analyzing",
        "architect",
        "architecture",
        "are",
        "as",
        "at",
        "audit",
        "auditing",
        "audits",
        "be",
        "before",
        "build",
        "building",
        "builds",
        "by",
        "can",
        "create",
        "creates",
        "creating",
        "debug",
        "debugging",
        "design",
        "designing",
        "designs",
        "do",
        "even",
        "feature",
        "features",
        "for",
        "from",
        "hardening",
        "has",
        "have",
        "identify",
        "identifies",
        "identifying",
        "implement",
        "implementation",
        "implements",
        "improve",
        "improves",
        "improving",
        "in",
        "into",
        "is",
        "it",
        "its",
        "mentioned",
        "name",
        "of",
        "on",
        "operational",
        "or",
        "production",
        "required",
        "requirement",
        "requirements",
        "requires",
        "review",
        "reviewing",
        "reviews",
        "solution",
        "solutions",
        "strategy",
        "strategies",
        "support",
        "supporting",
        "supports",
        "system",
        "systems",
        "task",
        "the",
        "their",
        "this",
        "to",
        "use",
        "when",
        "with",
        "without",
        "work",
        "working",
        "works",
    }
)


def _specific_tokens(value: str) -> set[str]:
    """Return normalized domain-bearing tokens, excluding skill boilerplate."""
    tokens: set[str] = set()
    for raw in _TOKEN_PATTERN.findall(value.lower()):
        normalized = _TOKEN_ALIASES.get(raw, raw)
        if len(normalized) > 1 and normalized not in _GENERIC_TERMS:
            tokens.add(normalized)
    return tokens


def _lexical_evidence(message: str, item: SkillMetadata) -> tuple[float, list[str]]:
    """Score direct task-to-skill evidence without rewarding generic boilerplate."""
    query_tokens = _specific_tokens(message)
    if not query_tokens:
        return 0.0, []

    name_tokens = _specific_tokens(item.name.replace("-", " "))
    category_tokens = _specific_tokens(item.category.replace("-", " "))
    description_tokens = _specific_tokens(item.description)
    name_overlap = query_tokens & name_tokens
    category_overlap = query_tokens & category_tokens
    description_overlap = query_tokens & description_tokens

    score = (
        (2.4 * len(name_overlap))
        + (1.0 * len(category_overlap))
        + (0.45 * len(description_overlap))
    )
    reasons: list[str] = []
    if name_overlap:
        reasons.append(f"skill-name match ({', '.join(sorted(name_overlap))})")
    if category_overlap:
        reasons.append(f"category match ({', '.join(sorted(category_overlap))})")
    if description_overlap:
        reasons.append(f"task terminology ({', '.join(sorted(description_overlap))})")

    normalized_message = " ".join(message.lower().split())
    normalized_name = item.name.replace("-", " ")
    if normalized_name in normalized_message:
        score += 6.0
        reasons.insert(0, "explicit skill reference")
    if len(name_overlap) >= 2:
        score += 0.4
    return score, reasons


def _add_ordered_fallbacks(
    scores: defaultdict[str, float],
    reasons: defaultdict[str, list[str]],
    names: tuple[str, ...],
    *,
    metadata: dict[str, SkillMetadata],
    base_score: float,
    step: float,
    reason: str,
) -> None:
    """Add deterministic low-confidence fallbacks while preserving declared order."""
    for index, name in enumerate(names):
        if name not in metadata:
            continue
        scores[name] += max(0.05, base_score - (step * index))
        reasons[name].append(reason)


def recommend_skills(
    message: str,
    *,
    execution_mode: ExecutionMode,
    classification: ClassificationResult,
    registry: SkillRegistry | None,
) -> list[SkillRecommendation]:
    """Recommend the smallest useful skill set with confidence and rationale."""
    if registry is None:
        return []
    profile = get_execution_mode_profile(execution_mode)
    metadata = {item.name: item for item in registry.metadata()}
    if not metadata:
        return []

    scores: defaultdict[str, float] = defaultdict(float)
    reasons: defaultdict[str, list[str]] = defaultdict(list)
    evidence_backed: set[str] = set()
    for name, item in metadata.items():
        score, lexical_reasons = _lexical_evidence(message, item)
        if score < 0.9:
            continue
        scores[name] += score
        reasons[name].extend(lexical_reasons)
        evidence_backed.add(name)

    tier_hints = _TIER_HINTS.get(classification.tier, ())
    supporting_hints = tuple(
        name for tier in classification.supporting_tiers for name in _TIER_HINTS.get(tier, ())
    )

    if evidence_backed:
        for name in tier_hints:
            if name in evidence_backed:
                scores[name] += 0.45
                reasons[name].append(f"tier {classification.tier} alignment")
        for name in supporting_hints:
            if name in evidence_backed:
                scores[name] += 0.2
                reasons[name].append("hybrid-intent coverage")
        for name in profile.skill_hints:
            if name in evidence_backed:
                scores[name] += 0.25
                reasons[name].append(f"{execution_mode} mode")
    else:
        _add_ordered_fallbacks(
            scores,
            reasons,
            tier_hints,
            metadata=metadata,
            base_score=0.9,
            step=0.12,
            reason=f"tier {classification.tier} conservative fallback",
        )
        _add_ordered_fallbacks(
            scores,
            reasons,
            supporting_hints,
            metadata=metadata,
            base_score=0.5,
            step=0.08,
            reason="hybrid-intent fallback",
        )
        _add_ordered_fallbacks(
            scores,
            reasons,
            profile.skill_hints,
            metadata=metadata,
            base_score=0.4,
            step=0.06,
            reason=f"{execution_mode} mode fallback",
        )

    ranked = sorted(scores, key=lambda name: (-scores[name], name))
    recommendations: list[SkillRecommendation] = []
    for name in ranked:
        if scores[name] <= 0:
            continue
        item = metadata[name]
        normalized = 1.0 - math.exp(-scores[name] / 3.0)
        confidence = min(0.97, 0.35 + (0.62 * normalized))
        rationale_parts = list(dict.fromkeys(reasons[name]))
        rationale = (
            f"Selected for {', '.join(rationale_parts)}; {item.description.rstrip('.')}"
            if rationale_parts
            else item.description
        )
        recommendations.append(
            SkillRecommendation(
                name=name,
                confidence=round(confidence, 4),
                rationale=rationale,
                activation_suggested=confidence >= 0.68,
                category=item.category,
                risk=item.risk,
            )
        )
        if len(recommendations) >= profile.recommendation_limit:
            break
    return recommendations


__all__ = ["SkillRecommendation", "recommend_skills"]
