"""Low-cardinality Prometheus instruments for Cognexus runtime behavior."""

from __future__ import annotations

from dataclasses import dataclass

from prometheus_client import Counter, Gauge, Histogram

_LATENCY_BUCKETS = (0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120)
_QUEUE_BUCKETS = (0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30)
_SCORE_BUCKETS = (0.0, 0.1, 0.25, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0)


@dataclass(frozen=True, slots=True)
class NexusMetrics:
    """Metric instruments used by the API, orchestrator, tools, and sessions."""

    requests: Counter
    request_latency: Histogram
    agent_runs: Counter
    agent_latency: Histogram
    run_queue_wait: Histogram
    run_inflight: Gauge
    routing_decisions: Counter
    classifier_decisions: Counter
    execution_modes: Counter
    skill_recommendations: Counter
    tool_runs: Counter
    tool_latency: Histogram
    llm_calls: Counter
    llm_latency: Histogram
    prompt_cache_requests: Counter
    prompt_cache_tokens: Counter
    errors: Counter
    guardrail_rejections: Counter
    session_fallbacks: Counter
    session_cache_events: Counter
    session_lock_wait: Histogram
    session_lock_events: Counter
    session_continuity: Histogram
    session_compaction_signals: Counter
    model_validation: Counter


metrics = NexusMetrics(
    requests=Counter(
        "nexus_http_requests_total",
        "HTTP requests handled by route template.",
        ["method", "route", "status"],
    ),
    request_latency=Histogram(
        "nexus_http_request_duration_seconds",
        "HTTP request latency by route template.",
        ["route"],
        buckets=_LATENCY_BUCKETS,
    ),
    agent_runs=Counter(
        "nexus_agent_runs_total",
        "Top-level Cognexus runs.",
        ["status", "tier"],
    ),
    agent_latency=Histogram(
        "nexus_agent_run_duration_seconds",
        "Top-level Cognexus run latency.",
        ["tier"],
        buckets=_LATENCY_BUCKETS,
    ),
    run_queue_wait=Histogram(
        "nexus_run_queue_wait_seconds",
        "Time spent waiting for bounded run capacity.",
        buckets=_QUEUE_BUCKETS,
    ),
    run_inflight=Gauge(
        "nexus_runs_inflight",
        "Number of active top-level Cognexus runs.",
    ),
    routing_decisions=Counter(
        "nexus_routing_decisions_total",
        "Deterministic routing decisions.",
        ["tier", "model"],
    ),
    classifier_decisions=Counter(
        "nexus_classifier_decisions_total",
        "Task classifications by tier, ambiguity, and override state.",
        ["tier", "ambiguity", "override"],
    ),
    execution_modes=Counter(
        "nexus_execution_modes_total",
        "Top-level runs by first-class execution mode and outcome.",
        ["mode", "status"],
    ),
    skill_recommendations=Counter(
        "nexus_skill_recommendations_total",
        "Skill recommendations by execution mode and activation suggestion.",
        ["mode", "activation_suggested"],
    ),
    tool_runs=Counter(
        "nexus_tool_runs_total",
        "Local tool and specialist-agent tool executions.",
        ["tool", "status"],
    ),
    tool_latency=Histogram(
        "nexus_tool_run_duration_seconds",
        "Local tool latency.",
        ["tool"],
        buckets=_LATENCY_BUCKETS,
    ),
    llm_calls=Counter(
        "nexus_llm_calls_total",
        "LLM calls observed through Agents SDK hooks.",
        ["agent", "status"],
    ),
    llm_latency=Histogram(
        "nexus_llm_call_duration_seconds",
        "LLM call latency observed through Agents SDK hooks.",
        ["agent"],
        buckets=_LATENCY_BUCKETS,
    ),
    prompt_cache_requests=Counter(
        "nexus_prompt_cache_requests_total",
        "Runs with a prompt-cache hit or miss.",
        ["model", "outcome"],
    ),
    prompt_cache_tokens=Counter(
        "nexus_prompt_cache_input_tokens_total",
        "Input tokens served from the prompt cache.",
        ["model"],
    ),
    errors=Counter(
        "nexus_errors_total",
        "Cognexus errors by component and exception type.",
        ["component", "type"],
    ),
    guardrail_rejections=Counter(
        "nexus_guardrail_rejections_total",
        "Guardrail rejections by stage.",
        ["stage"],
    ),
    session_fallbacks=Counter(
        "nexus_session_fallbacks_total",
        "Session backend fallbacks.",
        ["from_backend", "to_backend"],
    ),
    session_cache_events=Counter(
        "nexus_session_cache_events_total",
        "Session-handle cache events.",
        ["event", "backend"],
    ),
    session_lock_wait=Histogram(
        "nexus_session_lock_wait_seconds",
        "Time spent waiting for cross-process Redis session serialization.",
        buckets=_QUEUE_BUCKETS,
    ),
    session_lock_events=Counter(
        "nexus_session_lock_events_total",
        "Cross-process Redis session lock outcomes.",
        ["event"],
    ),
    session_continuity=Histogram(
        "nexus_session_continuity_score",
        "Privacy-preserving session continuity score.",
        buckets=_SCORE_BUCKETS,
    ),
    session_compaction_signals=Counter(
        "nexus_session_compaction_signals_total",
        "Session context-optimization and compaction signals.",
        ["signal"],
    ),
    model_validation=Counter(
        "nexus_model_validation_total",
        "Configured-model validation attempts.",
        ["status"],
    ),
)
