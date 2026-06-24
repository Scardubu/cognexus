# AGENTS.md — NEXUS Repository Contract

## Runtime contract

- Python 3.11–3.14.
- OpenAI Agents SDK 0.17.6, OpenAI Python 2.43.0, and Pydantic v2.
- FastAPI handlers, session operations, and network operations are asynchronous.
- Model identifiers come from validated settings, never business logic.
- `TRACE_INCLUDE_SENSITIVE=false` is invariant and cannot be enabled through settings.

## Package boundaries

The installed OpenAI Agents SDK owns the top-level `agents` import namespace. Local NEXUS specialist definitions live in `nexus_agents`.

Use:

```python
from agents import Agent, Runner
from nexus_agents.registry import agent_tools
```

Never add a local top-level `agents/` package, import shim, namespace bridge, or `.pyi` facade. Reintroducing that name shadows the SDK and breaks runtime and static-analysis behavior.

## Architecture rules

1. Preserve hierarchical routing and `parallel_tool_calls=False`.
2. Keep the orchestrator stateless; conversational state belongs in SDK session backends.
3. Use Redis for multi-replica production. SQLite is local or single-replica fallback. Stateless mode is explicit and forbidden in production.
4. Reuse the shared OpenAI client; do not create a client per request, agent, or tool.
5. Route live execution through the bounded `RunGate`; do not create unbounded tasks or fan-out.
6. Serialize runs sharing a session ID while allowing independent sessions to execute concurrently.
7. Every output must pass deterministic trace, safety, and constraint validation before transmission.
8. Never stream raw model deltas without a tested incremental safety design. The default SSE path buffers and validates first.
9. Keep model validation cached and outside readiness hot loops.
10. Never hardcode secrets, CORS wildcards, raw prompts, outputs, or session content into logs, metrics, or traces.
11. Preserve ARCH-01 through ARCH-10 in `config/stack_manifest.json`.
12. Do not claim a test, image, deployment, API, model, or file was verified unless it was actually verified.

## Adding a specialist

1. Define it in `nexus_agents/specialists.py` with `make_specialist_agent`.
2. Add a unique key to `AGENT_REGISTRY`.
3. Add the matching record to `config/agent_registry.json`.
4. Preserve immutable model settings and `parallel_tool_calls=False`.
5. Update registry integrity and behavior tests.

## Adding a stateless tool

1. Add a strict `@function_tool(defer_loading=True)` in `tools/namespaces.py`.
2. Add the domain prompt to `tools/_handlers.py`.
3. Register status and namespace in `tools/registry.py`.
4. Reuse `sdk_runtime`; never create a per-call `AsyncOpenAI` client.
5. Keep payload size bounded and return schema-validated output.
6. Update registry tests.

## Observability rules

- Use low-cardinality labels only.
- Prefer route templates, tier IDs, model IDs, agent names, and tool names.
- Never label metrics with request IDs, session IDs, user text, exception messages, or stack traces.
- Add spans only for material latency or failure boundaries.
- Always close pending LLM or tool spans on cancellation and exceptions.
- Keep sampling and exporter queues bounded.

## Required checks

```bash
ruff check .
ruff format --check .
mypy .
pytest --cov --cov-report=term-missing
python scripts/test_nexus.py --dry-run
python -m build
```

## Online security gate

```bash
pip-audit -r constraints/runtime.txt
```
