"""Canonical status registry for NEXUS stateless tools."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

from tools.namespaces import ALL_FUNCTION_TOOLS, TOOL_NAMESPACES

ToolStatus = Literal["implemented", "stubbed", "missing", "deprecated"]


@dataclass(frozen=True, slots=True)
class ToolRecord:
    """Status and routing metadata for one tool record."""

    name: str
    status: ToolStatus
    namespace: str | None
    executable: bool
    note: str


_IMPLEMENTED_NAMES = (
    "typescript_config_surgeon",
    "component_quality_gate",
    "edge_cache_architect",
    "vscode_debug_profiler",
    "motion_performance_architect",
    "motion_interaction_architect",
    "accessibility_architect",
    "api_automation_architect",
    "vscode_monorepo_forge",
    "release_incident_ops",
    "git_workflow_architect",
    "vscode_cognitive_os",
    "vscode_ai_agent_stack",
    "design_token_system_architect",
)

_NAMESPACE_BY_TOOL = {
    "typescript_config_surgeon": "correctness",
    "component_quality_gate": "correctness",
    "edge_cache_architect": "performance",
    "vscode_debug_profiler": "performance",
    "motion_performance_architect": "architecture",
    "motion_interaction_architect": "architecture",
    "accessibility_architect": "architecture",
    "api_automation_architect": "architecture",
    "vscode_monorepo_forge": "architecture",
    "release_incident_ops": "release_tooling",
    "git_workflow_architect": "release_tooling",
    "vscode_cognitive_os": "release_tooling",
    "vscode_ai_agent_stack": "release_tooling",
    "design_token_system_architect": "ux_motion",
}

TOOL_RECORDS: dict[str, ToolRecord] = {
    name: ToolRecord(
        name=name,
        status="implemented",
        namespace=_NAMESPACE_BY_TOOL[name],
        executable=True,
        note="Confirmed @function_tool implementation and handler.",
    )
    for name in _IMPLEMENTED_NAMES
}

# The old report said 16 tools but supplied no identifiers for two additional tools.
# They are recorded as non-executable historical gaps rather than fabricated APIs.
TOOL_RECORDS.update(
    {
        "historical_expected_tool_slot_15": ToolRecord(
            name="historical_expected_tool_slot_15",
            status="missing",
            namespace=None,
            executable=False,
            note="Unnamed count-only slot from the v2.1 report; no API was invented.",
        ),
        "historical_expected_tool_slot_16": ToolRecord(
            name="historical_expected_tool_slot_16",
            status="missing",
            namespace=None,
            executable=False,
            note="Unnamed count-only slot from the v2.1 report; no API was invented.",
        ),
    }
)


def implemented_tools() -> list[Any]:
    """Return the fourteen executable deferred tools."""
    return list(ALL_FUNCTION_TOOLS)


def registry_snapshot() -> list[dict[str, object]]:
    """Return JSON-safe registry records."""
    return [asdict(record) for record in TOOL_RECORDS.values()]


def validate_tool_registry() -> list[str]:
    """Return integrity anomalies; empty means valid."""
    errors: list[str] = []
    implemented = [record for record in TOOL_RECORDS.values() if record.status == "implemented"]
    if len(implemented) != 14:
        errors.append(f"expected 14 implemented tools, found {len(implemented)}")
    if len(ALL_FUNCTION_TOOLS) != 14:
        errors.append(f"expected 14 function tools, found {len(ALL_FUNCTION_TOOLS)}")
    if set(TOOL_NAMESPACES) != {
        "security",
        "correctness",
        "performance",
        "architecture",
        "ai_engineering",
        "release_tooling",
        "ux_motion",
        "compliance",
    }:
        errors.append("tool namespaces are incomplete")
    return errors
