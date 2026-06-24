"""Specialist registry with integrity checks and cached tool exports."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Literal

from agents import RunConfig

from config.settings import Settings, get_settings
from nexus_agents.base_agent import specialist_model_settings
from nexus_agents.specialists import AGENT_REGISTRY as AGENT_REGISTRY

AgentStatus = Literal["implemented", "stubbed", "missing", "deprecated"]


@dataclass(frozen=True, slots=True)
class AgentRecord:
    """Operational metadata for one specialist agent."""

    name: str
    status: AgentStatus
    tiers: tuple[int, ...]
    description: str


AGENT_RECORDS: dict[str, AgentRecord] = {
    name: AgentRecord(
        name=name,
        status="implemented",
        tiers=(),
        description=f"NEXUS specialist agent: {name}",
    )
    for name in AGENT_REGISTRY
}


def get_agent(name: str) -> Any:
    """Return a registered specialist or raise a useful error."""
    try:
        return AGENT_REGISTRY[name]
    except KeyError as exc:
        raise KeyError(f"Unknown specialist agent: {name}") from exc


def _normalize_names(names: Iterable[str] | None) -> tuple[str, ...]:
    if names is None:
        return tuple(AGENT_REGISTRY)
    requested = tuple(dict.fromkeys(names))
    unknown = sorted(set(requested) - set(AGENT_REGISTRY))
    if unknown:
        raise KeyError(f"Unknown specialist agent(s): {', '.join(unknown)}")
    return requested


@lru_cache(maxsize=32)
def _cached_agent_tools(
    model: str,
    prompt_cache_retention: str | None,
    model_retries: int,
    max_turns: int,
    selected_names: tuple[str, ...],
) -> tuple[Any, ...]:
    cfg = get_settings().model_copy(
        update={
            "nexus_specialist_model": model,
            "nexus_prompt_cache_retention": prompt_cache_retention or "off",
            "nexus_model_retries": model_retries,
        }
    )
    model_settings = specialist_model_settings(cfg)
    run_config = RunConfig(
        model=model,
        model_settings=model_settings,
        workflow_name="nexus-specialist-tool",
        trace_include_sensitive_data=False,
    )
    tools: list[Any] = []
    for name in selected_names:
        agent = AGENT_REGISTRY[name]
        tool = agent.clone(model=model, model_settings=model_settings).as_tool(
            tool_name=name,
            tool_description=f"Delegate complex domain analysis to {name}.",
            run_config=run_config,
            max_turns=max_turns,
        )
        tool.defer_loading = True
        tools.append(tool)
    return tuple(tools)


def agent_tools(
    settings: Settings | None = None,
    *,
    names: Iterable[str] | None = None,
) -> list[Any]:
    """Expose a validated, mode-selected specialist subset as cached tools.

    Omitting ``names`` preserves the historical behavior and exports all implemented
    specialists, so existing direct callers remain backward compatible.
    """
    cfg = settings or get_settings()
    selected_names = _normalize_names(names)
    return list(
        _cached_agent_tools(
            cfg.nexus_specialist_model,
            cfg.prompt_cache_retention,
            cfg.nexus_model_retries,
            cfg.max_tool_calls_per_tier,
            selected_names,
        )
    )


def validate_agent_registry() -> list[str]:
    """Return registry anomalies; an empty list means integrity is valid."""
    errors: list[str] = []
    if len(AGENT_REGISTRY) != 20:
        errors.append(f"expected 20 unique agents, found {len(AGENT_REGISTRY)}")
    if len(AGENT_REGISTRY) != len(set(AGENT_REGISTRY)):
        errors.append("duplicate agent registry keys detected")
    return errors
