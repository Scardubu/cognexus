"""
tools/namespaces.py
===================
All stateless @function_tools organised into 8 tier-based ToolNamespace objects.

CORRECTIONS APPLIED (v2.1):
  - tool_namespace() returns a ToolNamespace object, NOT a list.
    Registered in Agent.tools directly — never spread with *.
  - SkillOutput.recommendations uses typed Recommendation model from base_agent,
    replacing the non-strict list[dict].
  - Removed duplicate motion_performance_architect / motion_interaction_architect /
    accessibility_architect / component_quality_gate registrations from
    ux_motion_namespace; they are already in architecture_namespace / correctness_namespace.
    Duplication across namespaces confuses ToolSearchTool routing.
  - Empty-tools namespaces (security, ai_engineering, compliance) are intentionally
    empty — T1/T5/T8 skills are Agent-based, not tool-based. ToolSearchTool skips
    them correctly.
  - All @function_tool handlers use Optional[str] for nullable string params.
  - defer_loading=True on all tools (requires ToolSearchTool in the orchestrator).

SDK note: tool_namespace() is available from agents >= 0.0.7.
If your installed version does not export tool_namespace, update:
  pip install --upgrade openai-agents
"""

from __future__ import annotations

from typing import Any

from agents import function_tool, tool_namespace
from pydantic import BaseModel, ConfigDict, Field


class MotionPerformanceEnvelope(BaseModel):
    """Strict motion budget passed from strategy to implementation."""

    model_config = ConfigDict(extra="forbid")
    approved_css_properties: list[str] = Field(default_factory=lambda: ["opacity", "transform"])
    max_duration_ms: int = 600
    stagger_max_ms: int = 80
    notes: list[str] = Field(default_factory=list)


# ===========================================================================
# TIER 2 — CORRECTNESS & STABILITY
# ===========================================================================


@function_tool(defer_loading=True)
async def typescript_config_surgeon(
    tsconfig_content: str,
    target_package: str,
    ts_server_memory: int | None = None,
) -> dict[str, Any]:
    """
    Audits tsconfig.json for correctness, Next.js 15 / React 19 compatibility,
    and the maxTsServerMemory constraint (hard limit: 3072 — ARCH-07).
    Returns specific diff recommendations for the target package.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="typescript_config_surgeon",
        context={
            "tsconfig_content": tsconfig_content,
            "target_package": target_package,
            "ts_server_memory": ts_server_memory,
        },
    )


@function_tool(defer_loading=True)
async def component_quality_gate(
    component_code: str,
    component_name: str,
    is_server_component: bool = False,
) -> dict[str, Any]:
    """
    Evaluates a React component against quality gates: RSC compatibility,
    React 19 patterns, prop contract correctness, accessibility baseline,
    and Tailwind v4 class safety. Returns pass/fail per gate with remediation.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="component_quality_gate",
        context={
            "component_code": component_code,
            "component_name": component_name,
            "is_server_component": is_server_component,
        },
    )


# ===========================================================================
# TIER 3 — PERFORMANCE & SCALABILITY
# ===========================================================================


@function_tool(defer_loading=True)
async def edge_cache_architect(
    route_path: str,
    runtime: str,
    auth_required: bool = False,
    data_freshness_sla_seconds: int | None = None,
) -> dict[str, Any]:
    """
    Designs edge caching strategy for Next.js 15 routes. Validates Edge Runtime
    constraints (ARCH-08: no Node.js-only modules), Auth.js v5 session handling,
    and RSC streaming compatibility. runtime must be 'edge', 'nodejs', or 'mixed'.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="edge_cache_architect",
        context={
            "route_path": route_path,
            "runtime": runtime,
            "auth_required": auth_required,
            "data_freshness_sla_seconds": data_freshness_sla_seconds,
        },
    )


@function_tool(defer_loading=True)
async def vscode_debug_profiler(
    target_package: str,
    symptom_description: str,
    profiling_type: str,
) -> dict[str, Any]:
    """
    Generates VS Code launch.json / tasks.json for profiling Next.js 15,
    Fastify 5, or React Native targets. profiling_type must be one of:
    'cpu', 'memory', 'network', 'startup'.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="vscode_debug_profiler",
        context={
            "target_package": target_package,
            "symptom_description": symptom_description,
            "profiling_type": profiling_type,
        },
    )


# ===========================================================================
# TIER 4 — ARCHITECTURE & DESIGN
# ===========================================================================


@function_tool(defer_loading=True)
async def motion_performance_architect(
    component_name: str,
    animation_intent: str,
    app_context: str | None = None,
    existing_animations: list[str] | None = None,
) -> dict[str, Any]:
    """
    STRATEGY TOOL — Must be called BEFORE motion_interaction_architect.
    Analyses motion budget, compositing rules, and animation performance.
    Returns: approved_css_properties, max_duration_ms, anti_patterns,
    compositing_strategy, and performance_envelope for the interaction tool.
    app_context: 'TaxBridge', 'SabiScore', 'Hashablanca', or 'SwarmX'.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="motion_performance_architect",
        context={
            "component_name": component_name,
            "animation_intent": animation_intent,
            "app_context": app_context,
            "existing_animations": existing_animations or [],
        },
    )


@function_tool(defer_loading=True)
async def motion_interaction_architect(
    component_name: str,
    animation_intent: str,
    performance_envelope: MotionPerformanceEnvelope,
) -> dict[str, Any]:
    """
    IMPLEMENTATION TOOL — Requires performance_envelope from
    motion_performance_architect as input. Calling without it is a sequencing
    violation. Generates Framer Motion API patterns, variant definitions,
    useInView hook config, and animation tokens within the performance budget.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="motion_interaction_architect",
        context={
            "component_name": component_name,
            "animation_intent": animation_intent,
            "performance_envelope": performance_envelope.model_dump(mode="json"),
        },
    )


@function_tool(defer_loading=True)
async def accessibility_architect(
    component_code: str,
    component_name: str,
    wcag_level: str = "AA",
) -> dict[str, Any]:
    """
    Audits a React component for WCAG 2.2 compliance. Returns violations,
    remediation patches, and aria-attribute recommendations for Tailwind v4
    + React 19 RSC components. wcag_level: 'A', 'AA', or 'AAA'.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="accessibility_architect",
        context={
            "component_code": component_code,
            "component_name": component_name,
            "wcag_level": wcag_level,
        },
    )


@function_tool(defer_loading=True)
async def api_automation_architect(
    api_spec: str,
    target_framework: str,
    app_context: str | None = None,
) -> dict[str, Any]:
    """
    Generates API automation strategy from an OpenAPI 3.1 spec. Returns client
    SDK generation plan, mock server strategy, contract test scaffold, and CI
    integration recommendations. target_framework: 'fastify', 'nextjs', or 'effect-ts'.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="api_automation_architect",
        context={
            "api_spec": api_spec,
            "target_framework": target_framework,
            "app_context": app_context,
        },
    )


@function_tool(defer_loading=True)
async def vscode_monorepo_forge(
    monorepo_structure: str,
    requested_config: str,
) -> dict[str, Any]:
    """
    Generates VS Code configuration for Turborepo + pnpm workspace monorepos.
    requested_config: 'workspace', 'tasks', 'extensions', or 'launch'.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="vscode_monorepo_forge",
        context={
            "monorepo_structure": monorepo_structure,
            "requested_config": requested_config,
        },
    )


# ===========================================================================
# TIER 6 — RELEASE / PRODUCTIVITY / TOOLING
# ===========================================================================


@function_tool(defer_loading=True)
async def release_incident_ops(
    incident_type: str,
    affected_app: str,
    severity: str,
    description: str,
) -> dict[str, Any]:
    """
    Generates incident response runbooks, rollback procedures, and postmortem
    templates for Turborepo monorepo deployments.
    incident_type: 'deployment_failure', 'rollback', 'hotfix', or 'postmortem'.
    severity: 'P0', 'P1', 'P2', or 'P3'.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="release_incident_ops",
        context={
            "incident_type": incident_type,
            "affected_app": affected_app,
            "severity": severity,
            "description": description,
        },
    )


@function_tool(defer_loading=True)
async def git_workflow_architect(
    workflow_type: str,
    team_size: int,
    monorepo: bool = True,
) -> dict[str, Any]:
    """
    Designs Git workflows for Turborepo monorepos with Conventional Commits.
    workflow_type: 'branching', 'commit_conventions', 'pr_template', or 'hooks'.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="git_workflow_architect",
        context={
            "workflow_type": workflow_type,
            "team_size": team_size,
            "monorepo": monorepo,
        },
    )


@function_tool(defer_loading=True)
async def vscode_cognitive_os(
    developer_role: str,
    active_packages: list[str],
) -> dict[str, Any]:
    """
    Generates a cognitive-optimised VS Code setup for a developer role.
    developer_role: 'frontend', 'backend', 'fullstack', 'mobile', or 'ai'.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="vscode_cognitive_os",
        context={
            "developer_role": developer_role,
            "active_packages": active_packages,
        },
    )


@function_tool(defer_loading=True)
async def vscode_ai_agent_stack(
    ide_agent: str,
    active_apps: list[str],
) -> dict[str, Any]:
    """
    Configures VS Code AI agent integrations for the NEXUS project stack.
    ide_agent: 'copilot', 'cursor', 'cline', 'continue', or 'codex'.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="vscode_ai_agent_stack",
        context={
            "ide_agent": ide_agent,
            "active_apps": active_apps,
        },
    )


# ===========================================================================
# TIER 7 — UX / DESIGN SYSTEM
# ===========================================================================


@function_tool(defer_loading=True)
async def design_token_system_architect(
    token_category: str,
    app_context: str | None = None,
    existing_tokens: str | None = None,
) -> dict[str, Any]:
    """
    Designs or audits a design token system for Tailwind CSS v4. Returns CSS
    custom properties, Tailwind config extensions, dark mode strategy, and
    cross-app token consistency recommendations.
    token_category: 'color', 'typography', 'spacing', 'motion', or 'full'.
    """
    from tools._handlers import call_specialist

    return await call_specialist(
        skill="design_token_system_architect",
        context={
            "token_category": token_category,
            "app_context": app_context,
            "existing_tokens": existing_tokens,
        },
    )


# ===========================================================================
# NAMESPACE DEFINITIONS
# In SDK 0.17.6 tool_namespace() returns a list[FunctionTool].
# ===========================================================================

security_namespace: list[Any] = []
correctness_namespace = tool_namespace(
    name="correctness",
    description="TypeScript and React correctness tools.",
    tools=[typescript_config_surgeon, component_quality_gate],
)
performance_namespace = tool_namespace(
    name="performance",
    description="Caching and profiling tools.",
    tools=[edge_cache_architect, vscode_debug_profiler],
)
architecture_namespace = tool_namespace(
    name="architecture",
    description="Architecture, motion, accessibility, API automation, and monorepo tools.",
    tools=[
        motion_performance_architect,
        motion_interaction_architect,
        accessibility_architect,
        api_automation_architect,
        vscode_monorepo_forge,
    ],
)
ai_engineering_namespace: list[Any] = []
release_tooling_namespace = tool_namespace(
    name="release_tooling",
    description="Release, Git, VS Code, and developer productivity tools.",
    tools=[
        release_incident_ops,
        git_workflow_architect,
        vscode_cognitive_os,
        vscode_ai_agent_stack,
    ],
)
ux_motion_namespace = tool_namespace(
    name="ux_motion",
    description="Design token, component, motion, and accessibility tools.",
    tools=[design_token_system_architect],
)
compliance_namespace: list[Any] = []

TOOL_NAMESPACES: dict[str, list[Any]] = {
    "security": security_namespace,
    "correctness": correctness_namespace,
    "performance": performance_namespace,
    "architecture": architecture_namespace,
    "ai_engineering": ai_engineering_namespace,
    "release_tooling": release_tooling_namespace,
    "ux_motion": ux_motion_namespace,
    "compliance": compliance_namespace,
}

ALL_FUNCTION_TOOLS: list[Any] = [
    typescript_config_surgeon,
    component_quality_gate,
    edge_cache_architect,
    vscode_debug_profiler,
    motion_performance_architect,
    motion_interaction_architect,
    accessibility_architect,
    api_automation_architect,
    vscode_monorepo_forge,
    release_incident_ops,
    git_workflow_architect,
    vscode_cognitive_os,
    vscode_ai_agent_stack,
    design_token_system_architect,
]
