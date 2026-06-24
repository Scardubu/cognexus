# NEXUS v3.0 to v3.1 Migration Checklist

## Package namespace

- [ ] Remove any local top-level `agents/` package, bridge initializer, or `.pyi` facade.
- [ ] Import the SDK through `agents`.
- [ ] Import local specialists through `nexus_agents`.
- [ ] Update external references from `agents/specialists.py` to `nexus_agents/specialists.py`.

## Dependencies and tooling

- [ ] Install production dependencies from `requirements.txt`.
- [ ] Install developer and CI dependencies from `requirements-dev.txt`.
- [ ] Add `ruff format --check .`, coverage, and `python -m build` to CI.
- [ ] Test supported minimum and current Python versions.

## Runtime bounds

- [ ] Set `NEXUS_MAX_CONCURRENT_RUNS` for process capacity.
- [ ] Set `NEXUS_QUEUE_TIMEOUT_SECONDS` for bounded admission.
- [ ] Set OpenAI transport timeout and retry limits.
- [ ] Remove application-level retry loops that rerun a complete agent workflow after output-validation failure.

## Sessions

- [ ] Use SDK-native `AsyncSQLiteSession` for local or single-worker operation.
- [ ] Use Redis for multiple workers or replicas.
- [ ] Configure Redis connect/socket timeouts and maximum connections.
- [ ] Size session handle TTL and maximum cache entries.
- [ ] Confirm fallback policy is explicit and observable.

## HTTP and streaming

- [ ] Construct the service through `server.app:create_app` in tests or embedded deployments.
- [ ] Preserve route-template metric labels.
- [ ] Expect SSE events from `/v1/run/stream`, including heartbeats during long runs.
- [ ] Do not expect raw model-token deltas; output remains buffered until validation succeeds.

## Observability

- [ ] Set `TRACE_INCLUDE_SENSITIVE=false`.
- [ ] Set `OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA=false`.
- [ ] Configure `NEXUS_OTEL_SAMPLE_RATIO` and an OTLP endpoint when required.
- [ ] Alert on queue wait, errors, guardrail rejections, session fallback, and model-validation failure.
- [ ] Verify no prompts, outputs, session content, API keys, request IDs, or session IDs are metric labels.

## Deployment

- [ ] Build and scan the v3.1.0 container.
- [ ] Mount `/app/data` writable when SQLite fallback is enabled; keep the root filesystem read-only.
- [ ] Keep the process non-root with dropped capabilities.
- [ ] Configure `/health` and `/ready` probes.
- [ ] Test rollback to the previous immutable image digest.

## Verification

```bash
python -m pip install -r requirements-dev.txt -c constraints/runtime.txt
python -m pip check
ruff check .
ruff format --check .
mypy .
pytest --cov --cov-report=term-missing
python scripts/test_nexus.py --dry-run
python -m build
docker compose config
docker compose up --build -d
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:8000/ready
```
