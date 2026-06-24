"""Deterministic execution-mode policies for Cognexus orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

ExecutionMode = Literal["focus", "review", "research", "architect", "brainstorm", "incident"]
EXECUTION_MODES: Final[tuple[ExecutionMode, ...]] = (
    "focus",
    "review",
    "research",
    "architect",
    "brainstorm",
    "incident",
)


@dataclass(frozen=True, slots=True)
class ExecutionModeProfile:
    """Runtime policy that changes reasoning, structure, delegation, and orchestration."""

    name: ExecutionMode
    objective: str
    reasoning_policy: str
    orchestration_strategy: str
    output_sections: tuple[str, ...]
    specialist_budget: int
    supporting_tier_order: tuple[int, ...]
    recommendation_limit: int
    skill_hints: tuple[str, ...]


_PROFILES: Final[dict[ExecutionMode, ExecutionModeProfile]] = {
    "focus": ExecutionModeProfile(
        name="focus",
        objective="Produce the smallest complete answer that directly resolves the request.",
        reasoning_policy="Converge early, avoid speculative branches, and state only material assumptions.",
        orchestration_strategy="Use deterministic evidence first and at most two narrowly relevant specialists.",
        output_sections=("Answer", "Validation", "Next Actions"),
        specialist_budget=2,
        supporting_tier_order=(),
        recommendation_limit=2,
        skill_hints=("component-quality-gate", "testing-strategy-architect"),
    ),
    "review": ExecutionModeProfile(
        name="review",
        objective="Audit the supplied work for correctness, risk, omissions, and maintainability.",
        reasoning_policy="Challenge assumptions, rank findings by severity, and separate evidence from judgment.",
        orchestration_strategy="Use independent review coverage across correctness, security, and operations.",
        output_sections=("Findings", "Evidence", "Risks", "Recommendations", "Next Actions"),
        specialist_budget=4,
        supporting_tier_order=(1, 2, 3, 6, 4),
        recommendation_limit=3,
        skill_hints=(
            "codebase-zip-audit",
            "security-hardening-auditor",
            "testing-strategy-architect",
        ),
    ),
    "research": ExecutionModeProfile(
        name="research",
        objective="Build an evidence-backed answer with explicit uncertainty and source-quality discipline.",
        reasoning_policy="Explore competing explanations, verify important claims, and quantify uncertainty.",
        orchestration_strategy="Gather evidence before synthesis and delegate only distinct research questions.",
        output_sections=(
            "Question",
            "Evidence",
            "Analysis",
            "Confidence",
            "Open Questions",
            "Next Actions",
        ),
        specialist_budget=3,
        supporting_tier_order=(5, 4, 2, 1),
        recommendation_limit=3,
        skill_hints=(
            "prompt-engineering-architect",
            "data-visualization-architect",
            "testing-strategy-architect",
        ),
    ),
    "architect": ExecutionModeProfile(
        name="architect",
        objective="Produce a coherent, evolvable design with explicit contracts and migration safety.",
        reasoning_policy="Model boundaries, invariants, trade-offs, failure modes, and compatibility constraints.",
        orchestration_strategy="Combine architecture, correctness, security, and operability specialists in dependency order.",
        output_sections=(
            "Context",
            "Decision",
            "Architecture",
            "Alternatives",
            "Migration",
            "Validation",
            "Next Actions",
        ),
        specialist_budget=4,
        supporting_tier_order=(4, 2, 1, 3, 6),
        recommendation_limit=4,
        skill_hints=(
            "multi-agent-orchestration-architect",
            "api-contract-governance-architect",
            "testing-strategy-architect",
        ),
    ),
    "brainstorm": ExecutionModeProfile(
        name="brainstorm",
        objective="Generate diverse, useful options and then converge on the strongest practical direction.",
        reasoning_policy="Diverge deliberately, avoid duplicate ideas, then rank by value, feasibility, and risk.",
        orchestration_strategy="Use complementary creative and technical specialists without exhaustive fan-out.",
        output_sections=(
            "Possibilities",
            "Distinctive Options",
            "Trade-offs",
            "Recommended Direction",
            "Next Actions",
        ),
        specialist_budget=3,
        supporting_tier_order=(4, 5, 7, 3),
        recommendation_limit=3,
        skill_hints=(
            "ai-feature-architect",
            "frontend-product-design-architect",
            "prompt-engineering-architect",
        ),
    ),
    "incident": ExecutionModeProfile(
        name="incident",
        objective="Restore safety and service quickly while preserving evidence and preventing recurrence.",
        reasoning_policy="Prioritize impact, containment, reversible mitigation, recovery validation, and ownership.",
        orchestration_strategy="Use security, correctness, operations, and performance specialists under a strict action budget.",
        output_sections=(
            "Situation",
            "Impact",
            "Containment",
            "Recovery",
            "Verification",
            "Follow-up Actions",
        ),
        specialist_budget=4,
        supporting_tier_order=(1, 2, 6, 3),
        recommendation_limit=3,
        skill_hints=(
            "release-incident-operations-architect",
            "security-hardening-auditor",
            "opentelemetry-observability-architect",
        ),
    ),
}

_TIER_AGENTS: Final[dict[int, tuple[str, ...]]] = {
    1: ("security_hardening_agent", "backend_systems_auditor_agent", "taxbridge_compliance_agent"),
    2: (
        "testing_strategy_agent",
        "api_contract_governance_agent",
        "effect_ts_layer_agent",
        "backend_domain_model_agent",
    ),
    3: (
        "otel_observability_agent",
        "nextjs_performance_agent",
        "real_time_systems_agent",
        "bullmq_job_agent",
    ),
    4: (
        "multi_agent_orchestration_agent",
        "ai_feature_agent",
        "prisma_database_agent",
        "react_native_expo_agent",
    ),
    5: ("prompt_engineering_agent", "multi_agent_orchestration_agent", "ai_feature_agent"),
    6: ("testing_strategy_agent", "otel_observability_agent", "backend_systems_auditor_agent"),
    7: ("frontend_design_agent", "frontend_design_deep_agent", "data_visualization_agent"),
    8: (
        "taxbridge_compliance_agent",
        "backend_domain_model_agent",
        "api_contract_governance_agent",
    ),
}


def get_execution_mode_profile(mode: ExecutionMode) -> ExecutionModeProfile:
    """Return the immutable policy for one validated execution mode."""
    return _PROFILES[mode]


def specialist_names_for_mode(
    mode: ExecutionMode,
    *,
    primary_tier: int,
    supporting_tiers: tuple[int, ...] = (),
) -> tuple[str, ...]:
    """Select a bounded, deterministic specialist set for the mode and classification."""
    profile = get_execution_mode_profile(mode)
    tier_order: list[int] = [primary_tier]
    if mode != "focus":
        tier_order.extend(supporting_tiers)
        tier_order.extend(profile.supporting_tier_order)

    selected: list[str] = []
    seen_tiers: set[int] = set()
    for tier in tier_order:
        if tier in seen_tiers:
            continue
        seen_tiers.add(tier)
        for name in _TIER_AGENTS.get(tier, ()):
            if name not in selected:
                selected.append(name)
            if len(selected) >= profile.specialist_budget:
                return tuple(selected)
    return tuple(selected)


def render_execution_mode_contract(mode: ExecutionMode) -> str:
    """Render a bounded system-prompt contract for one execution mode."""
    profile = get_execution_mode_profile(mode)
    sections = ", ".join(profile.output_sections)
    return (
        "## Active execution mode\n\n"
        f"Mode: `{profile.name}`\n\n"
        f"Objective: {profile.objective}\n\n"
        f"Reasoning behavior: {profile.reasoning_policy}\n\n"
        f"Orchestration strategy: {profile.orchestration_strategy}\n\n"
        f"Preferred response structure: {sections}. Use only sections that add value, but preserve "
        "this order. When relevant, finish with explicit `Assumptions`, `Open Questions`, and "
        "`Next Actions` bullet lists so clients can extract response metadata deterministically."
    )


__all__ = [
    "EXECUTION_MODES",
    "ExecutionMode",
    "ExecutionModeProfile",
    "get_execution_mode_profile",
    "render_execution_mode_contract",
    "specialist_names_for_mode",
]
