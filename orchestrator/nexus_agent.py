"""Cognexus agent construction and safe execution entry points."""

from __future__ import annotations

import hashlib
import time
from collections import OrderedDict
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from threading import RLock
from typing import Any, Literal
from uuid import uuid4

import structlog
from agents import (
    Agent,
    ModelRetrySettings,
    ModelSettings,
    OutputGuardrailTripwireTriggered,
    RunConfig,
    Runner,
)
from pydantic import BaseModel, ConfigDict, Field

from config.settings import Settings, get_settings
from middleware.guardrails import create_input_guardrail, nexus_output_guardrail, screen_input
from middleware.output_guardrail import validate_output
from nexus_agents.registry import AGENT_REGISTRY, agent_tools
from observability.logging import get_logger
from observability.metrics import metrics
from observability.tracing import NexusRunHooks, get_trace_id, span
from orchestrator.errors import NexusOutputTooLargeError, NexusOutputValidationError
from orchestrator.execution_modes import ExecutionMode, specialist_names_for_mode
from orchestrator.model_router import route_models
from orchestrator.nexus_prompt import build_nexus_system_prompt
from orchestrator.response_metadata import derive_response_metadata
from orchestrator.runtime import RunGate, sdk_runtime
from orchestrator.skill_recommender import SkillRecommendation, recommend_skills
from orchestrator.tier_classifier import ClassificationResult, classify_task
from security.identifiers import session_observability_reference
from sessions.session_manager import SessionManager
from skill_runtime.catalog import get_skill_registry
from skill_runtime.loader import SkillRegistry
from skill_runtime.tools import build_skill_tools
from tools.registry import implemented_tools
from tools.search_tool import build_tool_search

logger = get_logger(__name__)


class NexusRunResult(BaseModel):
    """Stable result schema shared by CLI and HTTP callers."""

    model_config = ConfigDict(extra="forbid")
    run_id: str
    session_id: str
    response_text: str
    tier: int
    tier_name: str
    app_context: str
    execution_mode: ExecutionMode = "focus"
    classification_confidence: float = 0.0
    classification_ambiguity: str = "low"
    supporting_tiers: list[int] = Field(default_factory=list)
    model: str
    trace_id: str | None = None
    trace_validation: dict[str, Any]
    constraint_violations: list[dict[str, str]] = Field(default_factory=list)
    token_usage: dict[str, int] | None = None
    session_backend: str
    degraded: bool = False
    warnings: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    recommended_skills: list[SkillRecommendation] = Field(default_factory=list)
    session_intelligence: dict[str, Any] = Field(default_factory=dict)
    queue_wait_ms: float = 0.0
    duration_ms: float


def _orchestrator_model_settings(
    *,
    prompt_cache_retention: Literal["in_memory", "24h"] | None,
    model_retries: int,
) -> ModelSettings:
    return ModelSettings(
        parallel_tool_calls=False,
        truncation="auto",
        include_usage=True,
        prompt_cache_retention=prompt_cache_retention,
        retry=ModelRetrySettings(max_retries=model_retries),
    )


_AGENT_CACHE_MAX = 32
_AGENT_CACHE_LOCK = RLock()
_AGENT_CACHE: OrderedDict[tuple[Any, ...], Agent[Any]] = OrderedDict()


def _skill_prompt_state(cfg: Settings) -> tuple[SkillRegistry | None, str, str]:
    """Return the live registry, rendered catalog, and non-secret catalog fingerprint."""
    if not cfg.nexus_skills_enabled:
        return None, "", "skills-disabled"
    registry = get_skill_registry(cfg)
    catalog = registry.render_catalog(max_chars=cfg.nexus_skill_catalog_max_chars)
    fingerprint = hashlib.sha256(catalog.encode("utf-8")).hexdigest()
    return registry, catalog, fingerprint


def _agent_cache_key(
    cfg: Settings,
    *,
    skill_catalog_fingerprint: str,
    execution_mode: ExecutionMode = "focus",
    specialist_names: tuple[str, ...] = (),
) -> tuple[Any, ...]:
    """Return only agent-construction settings and safe content fingerprints."""
    return (
        cfg.nexus_orchestrator_model,
        cfg.nexus_specialist_model,
        cfg.prompt_cache_retention,
        cfg.nexus_model_retries,
        cfg.nexus_max_input_chars,
        cfg.max_tool_calls_per_tier,
        cfg.nexus_skills_enabled,
        str(cfg.nexus_skills_path.resolve()),
        cfg.nexus_skill_max_file_bytes,
        cfg.nexus_skill_max_resource_bytes,
        cfg.nexus_skill_activation_max_chars,
        cfg.nexus_skill_catalog_max_chars,
        cfg.nexus_skill_cache_ttl_seconds,
        tuple(sorted(cfg.nexus_skill_allowed_names)),
        tuple(sorted(cfg.nexus_skill_denied_names)),
        execution_mode,
        specialist_names,
        skill_catalog_fingerprint,
    )


def _build_nexus_agent_uncached(
    cfg: Settings,
    *,
    skill_registry: SkillRegistry | None,
    skill_catalog: str,
    execution_mode: ExecutionMode,
    specialist_names: tuple[str, ...],
) -> Agent[Any]:
    tools: list[Any] = [
        build_tool_search(),
        *implemented_tools(),
        *agent_tools(cfg, names=specialist_names),
    ]
    instructions = build_nexus_system_prompt(skill_catalog, execution_mode=execution_mode)

    if skill_registry is not None and skill_catalog:
        tools.extend(build_skill_tools(skill_registry))

    return Agent(
        name="Cognexus Production Orchestrator",
        model=cfg.nexus_orchestrator_model,
        instructions=instructions,
        tools=tools,
        input_guardrails=[create_input_guardrail(cfg.nexus_max_input_chars)],
        output_guardrails=[nexus_output_guardrail],
        model_settings=_orchestrator_model_settings(
            prompt_cache_retention=cfg.prompt_cache_retention,
            model_retries=cfg.nexus_model_retries,
        ),
    )


def build_nexus_agent(
    settings: Settings | None = None,
    *,
    execution_mode: ExecutionMode = "focus",
    primary_tier: int | None = None,
    supporting_tiers: tuple[int, ...] = (),
) -> Agent[Any]:
    """Build or reuse a mode-aware orchestrator keyed by non-secret policy settings."""
    cfg = settings or get_settings()
    registry, catalog, catalog_fingerprint = _skill_prompt_state(cfg)
    specialist_names = (
        tuple(AGENT_REGISTRY)
        if primary_tier is None
        else specialist_names_for_mode(
            execution_mode,
            primary_tier=primary_tier,
            supporting_tiers=supporting_tiers,
        )
    )
    key = _agent_cache_key(
        cfg,
        skill_catalog_fingerprint=catalog_fingerprint,
        execution_mode=execution_mode,
        specialist_names=specialist_names,
    )
    with _AGENT_CACHE_LOCK:
        cached = _AGENT_CACHE.get(key)
        if cached is not None:
            _AGENT_CACHE.move_to_end(key)
            return cached

    agent = _build_nexus_agent_uncached(
        cfg,
        skill_registry=registry,
        skill_catalog=catalog,
        execution_mode=execution_mode,
        specialist_names=specialist_names,
    )
    with _AGENT_CACHE_LOCK:
        existing = _AGENT_CACHE.get(key)
        if existing is not None:
            _AGENT_CACHE.move_to_end(key)
            return existing
        _AGENT_CACHE[key] = agent
        while len(_AGENT_CACHE) > _AGENT_CACHE_MAX:
            _AGENT_CACHE.popitem(last=False)
    return agent


def _dry_run_response(
    classification: ClassificationResult,
    execution_mode: ExecutionMode = "focus",
) -> str:
    return (
        "┌─ NEXUS SKILL TRACE\n"
        f"│ Intent      : {classification.intent or 'Dry-run validation'}\n"
        f"│ Tier        : {classification.tier} — {classification.tier_name}\n"
        f"│ App Context : {classification.app_context}\n"
        "│ Skills      : dry_run_validator\n"
        "│ Conflicts   : NONE\n"
        "│ Constraints : NONE\n"
        "│ Obs. Gaps   : NONE\n"
        "└─\n"
        f"Dry-run completed in {execution_mode} mode. Imports, routing, guardrails, sessions, "
        "recommendations, and validators are available."
    )


def _usage_snapshot(result: Any, *, model: str) -> dict[str, int] | None:
    usage = getattr(getattr(result, "context_wrapper", None), "usage", None)
    if usage is None:
        return None
    cached_tokens = int(getattr(getattr(usage, "input_tokens_details", None), "cached_tokens", 0))
    reasoning_tokens = int(
        getattr(getattr(usage, "output_tokens_details", None), "reasoning_tokens", 0)
    )
    metrics.prompt_cache_requests.labels(
        model,
        "hit" if cached_tokens > 0 else "miss",
    ).inc()
    if cached_tokens > 0:
        metrics.prompt_cache_tokens.labels(model).inc(cached_tokens)
    return {
        "requests": int(getattr(usage, "requests", 0)),
        "input_tokens": int(getattr(usage, "input_tokens", 0)),
        "cached_input_tokens": cached_tokens,
        "output_tokens": int(getattr(usage, "output_tokens", 0)),
        "reasoning_tokens": reasoning_tokens,
        "total_tokens": int(getattr(usage, "total_tokens", 0)),
    }


@asynccontextmanager
async def _optional_run_slot(
    gate: RunGate | None,
    *,
    run_id: str,
    timeout_seconds: float,
) -> AsyncIterator[float]:
    if gate is None:
        yield 0.0
        return
    async with gate.slot(run_id=run_id, timeout_seconds=timeout_seconds) as slot:
        yield slot.wait_ms


async def _session_snapshot(
    manager: SessionManager,
    session: Any | None,
    *,
    limit: int,
) -> dict[str, Any]:
    items: list[Any] = []
    if session is not None:
        items = await session.get_items(limit=limit)
    return manager.analyze_items(items).model_dump(mode="json")


async def run_nexus(
    message: str,
    *,
    session_id: str | None = None,
    dry_run: bool = False,
    execution_mode: ExecutionMode = "focus",
    expert_tier_override: int | None = None,
    settings: Settings | None = None,
    session_manager: SessionManager | None = None,
    run_gate: RunGate | None = None,
) -> NexusRunResult:
    """Execute one bounded, mode-aware run with deterministic validation and persistence."""
    cfg = settings or get_settings()
    clean_message = screen_input(message, max_chars=cfg.nexus_max_input_chars)
    classification = classify_task(clean_message, expert_override=expert_tier_override)
    route = route_models(classification.tier, cfg)
    skill_registry = get_skill_registry(cfg) if cfg.nexus_skills_enabled else None
    recommendations = recommend_skills(
        clean_message,
        execution_mode=execution_mode,
        classification=classification,
        registry=skill_registry,
    )
    resolved_session_id = session_id or f"session-{uuid4().hex}"
    run_id = f"run-{uuid4().hex}"
    session_ref = session_observability_reference(resolved_session_id)
    manager = session_manager or SessionManager(cfg)
    owns_manager = session_manager is None
    started = time.perf_counter()
    status = "error"
    structlog.contextvars.bind_contextvars(run_id=run_id, session_ref=session_ref)

    metrics.routing_decisions.labels(str(classification.tier), route.orchestrator).inc()
    metrics.classifier_decisions.labels(
        str(classification.tier),
        classification.ambiguity,
        "true" if classification.expert_override_applied else "false",
    ).inc()
    for recommendation in recommendations:
        metrics.skill_recommendations.labels(
            execution_mode,
            "true" if recommendation.activation_suggested else "false",
        ).inc()
    logger.info(
        "nexus_run_started",
        tier=classification.tier,
        model=route.orchestrator,
        execution_mode=execution_mode,
        classification_confidence=classification.confidence,
        classification_ambiguity=classification.ambiguity,
        dry_run=dry_run,
    )

    try:
        async with span(
            "nexus.run",
            {
                "nexus.run_id": run_id,
                "nexus.session_ref": session_ref,
                "nexus.tier": classification.tier,
                "nexus.model": route.orchestrator,
                "nexus.execution_mode": execution_mode,
                "nexus.classification_confidence": classification.confidence,
                "nexus.classification_ambiguity": classification.ambiguity,
                "nexus.dry_run": dry_run,
            },
        ):
            trace_id = get_trace_id()
            async with span(
                "nexus.routing.decision",
                {
                    "nexus.tier": classification.tier,
                    "nexus.model": route.orchestrator,
                    "nexus.app_context": classification.app_context,
                    "nexus.execution_mode": execution_mode,
                },
            ):
                pass

            async with manager.session_scope(resolved_session_id) as handle:
                if dry_run:
                    response_text = _dry_run_response(classification, execution_mode)
                    validation = validate_output(response_text)
                    session_intelligence = await _session_snapshot(
                        manager,
                        handle.session,
                        limit=cfg.nexus_session_summary_item_limit,
                    )
                    metadata = derive_response_metadata(
                        response_text,
                        classification=classification,
                        execution_mode=execution_mode,
                        recommendations=recommendations,
                        validated=bool(validation["valid"]),
                    )
                    status = "dry_run"
                    return NexusRunResult(
                        run_id=run_id,
                        session_id=resolved_session_id,
                        response_text=response_text,
                        tier=classification.tier,
                        tier_name=classification.tier_name,
                        app_context=classification.app_context,
                        execution_mode=execution_mode,
                        classification_confidence=classification.confidence,
                        classification_ambiguity=classification.ambiguity,
                        supporting_tiers=list(classification.supporting_tiers),
                        model=route.orchestrator,
                        trace_id=trace_id,
                        trace_validation=validation["trace"],
                        constraint_violations=validation["constraints"].violations,
                        session_backend=handle.effective_backend,
                        degraded=handle.degraded,
                        warnings=list(handle.warnings),
                        next_actions=metadata.next_actions,
                        assumptions=metadata.assumptions,
                        open_questions=metadata.open_questions,
                        confidence=metadata.confidence,
                        recommended_skills=metadata.recommended_skills,
                        session_intelligence=session_intelligence,
                        duration_ms=(time.perf_counter() - started) * 1000,
                    )

                await sdk_runtime.ensure(cfg)
                try:
                    agent = build_nexus_agent(
                        cfg,
                        execution_mode=execution_mode,
                        primary_tier=classification.tier,
                        supporting_tiers=classification.supporting_tiers,
                    )
                except TypeError as exc:
                    # Compatibility adapter for extensions that wrapped the historical
                    # one-argument factory before execution-mode routing was introduced.
                    if "unexpected keyword argument" not in str(exc):
                        raise
                    agent = build_nexus_agent(cfg)
                run_config = RunConfig(
                    model=route.orchestrator,
                    model_settings=_orchestrator_model_settings(
                        prompt_cache_retention=cfg.prompt_cache_retention,
                        model_retries=cfg.nexus_model_retries,
                    ),
                    workflow_name=f"nexus-{execution_mode}-run",
                    group_id=session_ref,
                    trace_metadata={
                        "run_id": run_id,
                        "tier": str(classification.tier),
                        "execution_mode": execution_mode,
                    },
                    trace_include_sensitive_data=False,
                )

                async with _optional_run_slot(
                    run_gate,
                    run_id=run_id,
                    timeout_seconds=cfg.nexus_queue_timeout_seconds,
                ) as queue_wait_ms:
                    hooks = NexusRunHooks()
                    try:
                        async with span("nexus.agent.run", {"nexus.run_id": run_id}):
                            result = await Runner.run(
                                agent,
                                clean_message,
                                session=handle.session,
                                run_config=run_config,
                                max_turns=cfg.max_turns,
                                hooks=hooks,
                            )
                    except OutputGuardrailTripwireTriggered as exc:
                        hooks.finish_pending(type(exc).__name__)
                        metrics.guardrail_rejections.labels("output").inc()
                        raise NexusOutputValidationError(
                            "NEXUS output was rejected by the production guardrail"
                        ) from exc
                    except BaseException as exc:
                        hooks.finish_pending(type(exc).__name__)
                        raise

                response_text = str(result.final_output or "")
                if len(response_text) > cfg.nexus_max_output_chars:
                    raise NexusOutputTooLargeError(
                        f"NEXUS output exceeded {cfg.nexus_max_output_chars} characters"
                    )
                validation = validate_output(response_text)
                if not validation["valid"]:
                    metrics.guardrail_rejections.labels("output").inc()
                    raise NexusOutputValidationError(
                        "NEXUS output failed deterministic trace or constraint validation"
                    )

                session_intelligence = await _session_snapshot(
                    manager,
                    handle.session,
                    limit=cfg.nexus_session_summary_item_limit,
                )
                metadata = derive_response_metadata(
                    response_text,
                    classification=classification,
                    execution_mode=execution_mode,
                    recommendations=recommendations,
                    validated=True,
                )
                token_usage = _usage_snapshot(result, model=route.orchestrator)
                status = "success"
                return NexusRunResult(
                    run_id=run_id,
                    session_id=resolved_session_id,
                    response_text=response_text,
                    tier=classification.tier,
                    tier_name=classification.tier_name,
                    app_context=classification.app_context,
                    execution_mode=execution_mode,
                    classification_confidence=classification.confidence,
                    classification_ambiguity=classification.ambiguity,
                    supporting_tiers=list(classification.supporting_tiers),
                    model=route.orchestrator,
                    trace_id=trace_id,
                    trace_validation=validation["trace"],
                    constraint_violations=validation["constraints"].violations,
                    token_usage=token_usage,
                    session_backend=handle.effective_backend,
                    degraded=handle.degraded,
                    warnings=list(handle.warnings),
                    next_actions=metadata.next_actions,
                    assumptions=metadata.assumptions,
                    open_questions=metadata.open_questions,
                    confidence=metadata.confidence,
                    recommended_skills=metadata.recommended_skills,
                    session_intelligence=session_intelligence,
                    queue_wait_ms=queue_wait_ms,
                    duration_ms=(time.perf_counter() - started) * 1000,
                )
    except Exception as exc:
        metrics.errors.labels("orchestrator", type(exc).__name__).inc()
        logger.error("nexus_run_failed", error_type=type(exc).__name__)
        raise
    finally:
        duration_seconds = time.perf_counter() - started
        metrics.agent_runs.labels(status, str(classification.tier)).inc()
        metrics.execution_modes.labels(execution_mode, status).inc()
        metrics.agent_latency.labels(str(classification.tier)).observe(duration_seconds)
        logger.info(
            "nexus_run_finished",
            status=status,
            execution_mode=execution_mode,
            duration_ms=duration_seconds * 1000,
        )
        if owns_manager:
            await manager.close()
        structlog.contextvars.unbind_contextvars("run_id", "session_ref")


async def stream_nexus(**kwargs: Any) -> AsyncIterator[str]:
    """Yield a fully validated result in bounded chunks without leaking unsafe deltas."""
    result = await run_nexus(**kwargs)
    chunk_size = (kwargs.get("settings") or get_settings()).nexus_stream_chunk_chars
    for index in range(0, len(result.response_text), chunk_size):
        yield result.response_text[index : index + chunk_size]
