# Operations Runbook

## Service indicators

Monitor at least:

- HTTP availability and readiness.
- Request rate and p50/p95/p99 latency.
- HTTP 4xx and 5xx rates.
- Agent run latency and failures.
- Tool run latency and failures.
- Guardrail rejection count.
- Redis latency, connectivity, memory, rejected writes, and evictions (expected to remain zero under `noeviction`).
- Distributed rate-limit backend latency/errors and HTTP 429 volume by route class.
- OpenAI API latency, rate-limit responses, and authentication errors.
- Container CPU, memory, restart count, and disk use.

## Health endpoints

Liveness:

```bash
curl -i http://localhost:8000/health
```

Readiness:

```bash
curl -i http://localhost:8000/ready
```

`/health` confirms that the process can serve HTTP. `/ready` checks configuration and the selected session backend. Use `/ready` for load-balancer traffic eligibility.

## Metrics

```bash
curl -sS http://localhost:8000/metrics
```

When API authentication is required:

```bash
curl -sS http://localhost:8000/metrics \
  -H "Authorization: Bearer ${NEXUS_API_KEY}"
```

Configure Prometheus to scrape `/metrics`, or route OTLP metrics through the collector if your platform standardizes on OpenTelemetry.

## Logs

Logs are one JSON object per line in production. Search by:

- `request_id`
- `session_id`
- `trace_id`
- `agent_name`
- `tool_name`
- `event`

Docker Compose:

```bash
docker compose logs --since=30m nexus
```

Systemd:

```bash
sudo journalctl -u nexus-openai --since "30 minutes ago" --output=cat
```

The implementation does not log prompt or model-output bodies by default. Preserve that behavior unless a reviewed redaction and retention policy is added.

## Session operations

Inspect a session:

```bash
curl -sS "http://localhost:8000/v1/sessions/demo-session" \
  -H "Authorization: Bearer ${NEXUS_API_KEY}" | python -m json.tool
```

Delete a session:

```bash
curl -i -X DELETE "http://localhost:8000/v1/sessions/demo-session" \
  -H "Authorization: Bearer ${NEXUS_API_KEY}"
```

A session identifier is client-supplied but constrained to a safe character set and length. It must not contain customer secrets.

## Common incidents

### Elevated HTTP 429 responses

1. Check application and edge rate-limit metrics separately.
2. Confirm every replica points to the same `NEXUS_RATE_LIMIT_STORAGE_URI`/`REDIS_URL` and inspect Redis latency or rejected writes.
3. Check upstream OpenAI rate-limit errors in logs; provider 429s are a different capacity boundary.
4. Confirm clients reuse session IDs appropriately rather than creating uncontrolled parallel traffic.
5. Reduce client concurrency or adjust the application limit only after capacity and abuse analysis.
6. Do not switch a live Redis deployment to `memory://` or disable rate limiting as a first response.

### Redis outage

1. Check `/ready`, Redis connectivity, and limiter-storage errors. Live replicated deployments fail closed rather than silently moving quota state into each process.
2. Inspect Redis authentication, DNS, TLS, and network policy.
3. If SQLite fallback is intentionally enabled and only one API replica is active, confirm the logged fallback.
4. If multiple replicas are active, do not rely on local SQLite fallback for shared state; remove unhealthy replicas from service or restore Redis.
5. Verify session behavior after recovery.

### OpenAI authentication failures

1. Confirm the secret exists in the runtime environment.
2. Rotate the key through the secret manager if exposure is suspected.
3. Restart or roll the workload so it receives the updated secret.
4. Run one controlled request and check error metrics.

### Increased model latency

1. Separate application latency from provider latency using spans.
2. Check tool invocation counts and repeated retries.
3. Check whether long sessions need compaction.
4. Confirm routing tiers are not over-selecting the highest-cost model.
5. Apply client-side timeouts and capacity controls rather than killing active workers abruptly.

### Guardrail rejection spike

1. Inspect rejection categories, not raw sensitive prompts.
2. Determine whether traffic changed or a rule introduced false positives.
3. Reproduce with sanitized test cases.
4. Add a regression test before changing the rule.
5. Never bypass output guardrails to restore availability.

## Backup and recovery

Redis persistence and backup depend on the managed service configuration. Enable appropriate snapshots and test restore procedures.

For SQLite development deployments:

```bash
sqlite3 data/nexus_sessions.db ".backup 'data/nexus_sessions-backup.db'"
```

Do not copy a live SQLite file with a naive filesystem operation while writes are active.

## Release procedure

1. Merge only after CI passes.
2. Run `python scripts/verify_version.py --expected <tag-without-v>` and require a clean `python -m pip check`.
3. Build distributions with the audited toolchain and `python -m build --no-isolation`.
4. Build an immutable image tagged with the Git SHA.
5. Scan the image and dependencies.
6. Deploy to staging.
7. Run health, readiness, API, session, distributed-rate-limit, and guardrail smoke tests.
8. Review error and latency metrics.
9. Promote the same image digest to production.
10. Observe through at least one normal traffic window.
11. Record the release SHA and rollback digest.

## Post-deployment verification

```bash
curl -f https://api.example.com/health
curl -f https://api.example.com/ready
curl -f -X POST https://api.example.com/v1/run \
  -H "Authorization: Bearer ${NEXUS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"message":"Return a concise production readiness checklist.","session_id":"postdeploy-check"}'
```

Then verify logs contain the same request ID returned in the `X-Request-ID` response header and that traces reach the configured collector.
