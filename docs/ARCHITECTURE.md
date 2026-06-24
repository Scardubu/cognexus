# NEXUS OpenAI Architecture

## Purpose

NEXUS is a tiered engineering orchestration service built on the OpenAI Agents SDK. It sanitizes and classifies a task, selects configured models, delegates to specialist agents or deferred tools, persists session state, validates the final response, and returns a typed run result with a required trace block.

Version 3.3.1 preserves the stabilized runtime architecture while adding portable Agent Skills, fail-closed production policy, bounded request ingestion, reproducible packaging, and enterprise release controls.

## Runtime flow

```text
CLI or HTTP request
        |
        v
request ID + body byte limit + authentication + environment-aware shared rate limit + timeout
        |
        v
Pydantic validation + sanitization + T1 input guardrail
        |
        v
deterministic tier classifier + configuration-backed model router
        |
        v
bounded RunGate queue
        |
        v
process-local lock + bounded Redis lease / Async SQLite / explicit stateless session
        |
        v
NEXUS manager agent
   |          |
   |          +--> 20 specialist agents exposed as tools
   +-------------> 14 deferred domain tools
   +-------------> 39 progressively disclosed Agent Skills
        |
        v
OpenAI Agents SDK Runner (`parallel_tool_calls=False`)
        |
        v
output guardrail + trace + ARCH constraint validation
        |
        v
typed NexusRunResult returned to CLI, JSON API, or safe SSE transport
```

## Package boundaries

The OpenAI Agents SDK owns the top-level `agents` namespace. NEXUS code must never create a local `agents/` package.

```python
from agents import Agent, Runner, RunConfig
from agents.extensions.memory import AsyncSQLiteSession, RedisSession
from nexus_agents.registry import agent_tools
```

Local agent code is isolated under `nexus_agents/`. This removes import-path ambiguity, runtime bridges, circular-import risk, and special typing facades.

## Configuration

`config/settings.py` is the sole runtime configuration boundary. It is an immutable Pydantic Settings v2 model with cross-field production validation.

Key invariants:

- Model IDs are configuration values and may be checked through a cached Models API lookup.
- `TRACE_INCLUDE_SENSITIVE` is typed as `Literal[False]`.
- Production requires independent non-placeholder OpenAI/service keys, explicit trusted hosts, exact CORS origins, trusted proxy IP/CIDR ranges, and non-stateless sessions.
- Multi-worker production requires Redis for sessions and shared rate-limit state; SQLite and `memory://` limits are not treated as distributed stores.
- Retry counts, network timeouts, concurrency, queue waits, session caches, and output sizes are bounded.

## OpenAI SDK runtime

`orchestrator/runtime.py` owns one reusable `AsyncOpenAI` client for the process. The client is configured with explicit transport timeout and retry limits, registered as the Agents SDK default Responses client, and closed during application or CLI shutdown.

A non-reversible API-key digest participates in the client fingerprint so controlled key rotation replaces the client without logging or storing the raw key in cache metadata.

## Orchestration and performance

`orchestrator/nexus_agent.py` is the shared execution service for HTTP, CLI, and smoke tests.

Performance controls:

- A process-local semaphore bounds concurrent top-level runs.
- Queue acquisition has a deadline and returns a capacity error instead of waiting indefinitely.
- A process-local lock protects each cached SDK session object; Redis-backed sessions additionally acquire a bounded distributed lease so ordering holds across workers and Kubernetes replicas without globally serializing unrelated sessions.
- Agent and delegated-tool definitions are cached by immutable configuration.
- Model validation is account-scoped, page-bounded, and cached separately for success and provider failure.
- The orchestrator does not silently issue a second full LLM run when output validation fails.
- Transport retries and model retries are independent, explicit, and tightly bounded.
- Input, output, turn count, tool-call count, streaming chunk sizes, HTTP concurrency, socket backlog, and graceful shutdown are bounded.

## Agents and tools

The registry contains:

- 20 uniquely named specialist agents.
- 14 implemented executable deferred tools.
- Two unnamed historical count-only tool slots recorded as missing metadata rather than fabricated APIs.

Deferred loading avoids constructing unnecessary tool graphs during import. Tool handlers reuse the process SDK client and return `SpecialistOutput` validated by Pydantic.

## Sessions and memory

`sessions/session_manager.py` supports:

1. `RedisSession` for multi-replica production.
2. SDK-native `AsyncSQLiteSession` for local and single-replica operation.
3. Explicit stateless operation outside production only.

The manager provides:

- race-safe session creation;
- process-local ordering locks plus a Redis distributed lease for multi-replica deployments;
- bounded TTL/LRU handle caching;
- explicit Redis connection and socket timeouts;
- bounded Redis pooling;
- observable Redis-to-SQLite fallback outside fail-closed production;
- deterministic close and delete lifecycle;
- real SQLite/Redis readiness probes;
- cleanup-safe per-session creation locks;
- optional Responses API compaction.

Fallback is never silent. The effective backend, degradation state, and warnings are returned in run and readiness metadata.

## HTTP API

`server.app:create_app` builds an independently testable FastAPI application. The
`cognexus-server` entry point is the production launcher and translates validated
settings into Uvicorn host, port, worker, proxy-trust, graceful-shutdown, concurrency,
and backlog options. Direct Uvicorn invocation is retained only for development reload.

Rate-limit storage is process-local only for development/single-process operation. A
staging or production Redis deployment automatically reuses `REDIS_URL` unless
`NEXUS_RATE_LIMIT_STORAGE_URI` explicitly supplies another Redis endpoint. Storage
errors fail closed and never fall back to in-memory counters.

Endpoints:

- `GET /health` — process liveness.
- `GET /ready` — configuration, session, and cached model readiness.
- `POST /v1/run` — typed orchestration response.
- `POST /v1/run/stream` — server-sent events with accepted, heartbeat, result, and error events.
- `GET /v1/sessions/{session_id}` — session metadata and item count.
- `DELETE /v1/sessions/{session_id}` — session deletion.
- `GET /metrics` — Prometheus text format, protected when API authentication is configured.

The SSE endpoint does not expose unvalidated model deltas. It emits a small acceptance event and periodic heartbeats while the bounded run executes, then emits only validated chunks or a sanitized protocol-level error event. Request bodies are rejected before JSON buffering when they exceed `NEXUS_MAX_REQUEST_BYTES`.

## Guardrails and validation

The input layer rejects malformed payloads, null bytes, oversized content, prompt-injection signatures, and disallowed requests before live execution.

The output layer checks:

- maximum size;
- secret-like values;
- required NEXUS trace structure;
- ARCH constraints;
- unresolved conflicts;
- unsafe content.

The SDK output guardrail and deterministic post-run validation provide defense in depth. Validation failure is surfaced; it does not trigger an expensive hidden rerun.

## Observability

Observability is deliberately low-cardinality and content-free.

Metrics cover:

- HTTP request count and route-template latency;
- queue wait and active runs;
- tier and model routing decisions;
- agent, LLM, and tool latency/status;
- prompt-cache hits, misses, and cached tokens;
- session cache events and fallbacks;
- model-validation outcomes;
- guardrail rejections and errors.

OpenTelemetry spans cover request, queue, routing, agent, LLM, and tool boundaries. LLM and tool hooks never record prompts, outputs, session content, or secrets. Pending spans are closed and marked failed when cancellation or SDK errors skip normal end hooks.

Exporter queues, batch sizes, deadlines, and sample ratio are bounded. With no external collector, local execution remains operational without blocking on telemetry.

## Failure behavior

- Queue saturation returns a controlled 503 response with `Retry-After`.
- Request timeout returns a structured 504 response.
- Invalid model output returns a structured upstream-output error.
- Redis fallback occurs only when enabled and is reported explicitly.
- Production configuration errors fail during settings construction or readiness.
- Optional telemetry failure does not disable core execution.
- No critical behavior is silently downgraded.
