"""Factories and typed schemas shared by NEXUS specialist agents."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from agents import Agent, ModelRetrySettings, ModelSettings
from pydantic import BaseModel, ConfigDict, Field

from config.settings import Settings, get_settings


class Recommendation(BaseModel):
    """A prioritised recommendation produced by a specialist."""

    model_config = ConfigDict(extra="forbid")
    priority: str = Field(pattern="^(critical|high|medium|low|info)$")
    action: str = Field(min_length=1)
    rationale: str = Field(min_length=1)


class SpecialistOutput(BaseModel):
    """Structured result shared by all specialist agents."""

    model_config = ConfigDict(extra="forbid")
    analysis: str
    recommendations: list[Recommendation] = Field(default_factory=list)
    constraint_violations: list[str] = Field(default_factory=list)
    observability_gaps: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


SHARED_CONSTRAINTS = """
## Immutable architecture constraints
ARCH-01: Optimize incrementally; avoid unnecessary rewrites.
ARCH-02: Preserve architecture unless the user explicitly requests a rewrite.
ARCH-03: Maintain Next.js 15 and React 19 compatibility.
ARCH-04: Prefer React Server Components and streaming over client fetching.
ARCH-05: Preserve Effect-TS Layer discipline in backend services.
ARCH-06: BullMQ Queue, Worker, and QueueEvents use separate Redis connections.
ARCH-07: maxTsServerMemory must not exceed 3072.
ARCH-08: Edge Runtime code must not use Node-only modules such as jsonwebtoken.
ARCH-09: SwarmX agents remain stateless between turns.
ARCH-10: TaxBridge financial writes require idempotency keys.

Return structured output only. Never fabricate repository files, APIs, test results,
model availability, or deployment state. Call out assumptions explicitly.
"""


def specialist_model_settings(settings: Settings) -> ModelSettings:
    """Return one conservative model-settings policy for every specialist."""
    return ModelSettings(
        parallel_tool_calls=False,
        truncation="auto",
        include_usage=True,
        prompt_cache_retention=settings.prompt_cache_retention,
        retry=ModelRetrySettings(max_retries=settings.nexus_model_retries),
    )


def make_specialist_agent(
    name: str,
    domain_prompt: str,
    extra_tools: Sequence[Any] | None = None,
    *,
    settings: Settings | None = None,
) -> Agent[Any]:
    """Create a configuration-backed specialist Agent with bounded behavior."""
    cfg = settings or get_settings()
    return Agent(
        name=name,
        model=cfg.nexus_specialist_model,
        instructions=f"{domain_prompt.strip()}\n\n{SHARED_CONSTRAINTS}",
        output_type=SpecialistOutput,
        tools=list(extra_tools or ()),
        model_settings=specialist_model_settings(cfg),
    )
