# Service-Level Objectives and Capacity Model

These are recommended initial objectives for a private production deployment. Replace them with product-specific targets after collecting representative traffic data.

## Indicators and objectives

| Indicator | Initial objective | Measurement |
|---|---:|---|
| API availability | 99.9% over 30 days | Successful non-5xx requests excluding approved maintenance |
| Readiness availability | 99.95% over 30 days | `/ready` returns 200 from eligible replicas |
| Request success | 99.0% over 30 days | Runs not ending in 5xx, timeout, or invalid model output |
| Queue admission | 99% under 1 second | `nexus_run_queue_wait_seconds` |
| API overhead | p95 under 100 ms | HTTP latency excluding the model/provider execution span |
| Dry-run latency | p95 under 500 ms | Controlled dry-run request |
| Session durability | No acknowledged loss | Managed Redis persistence and restore tests |
| Telemetry delivery | 99% within 60 seconds | Collector/exporter monitoring |

Model latency is provider- and task-dependent; define separate objectives by route or task tier after observing real workloads.

## Error-budget policy

A 99.9% monthly availability objective permits about 43 minutes of unavailability in a 30-day month. At 50% budget consumption, pause risky reliability changes and prioritize known failure modes. At 100%, freeze non-essential releases until the service is back within policy and a corrective plan exists.

## Capacity

`NEXUS_MAX_CONCURRENT_RUNS` is per process, not global. Approximate maximum active runs as:

```text
replicas × workers per replica × NEXUS_MAX_CONCURRENT_RUNS
```

Keep one worker per container unless memory and session semantics have been load-tested. Scale replicas with Redis sessions. Application IP rate limits coordinate through Redis in live deployments. Apply identity-aware tenant/provider quotas at the edge because run gates and provider budgets remain per process/account rather than one global admission controller.

## Alerting starting points

- Readiness failures for 2 consecutive minutes.
- 5xx rate above 2% for 5 minutes.
- p95 queue wait above 5 seconds for 10 minutes.
- Capacity rejections above 1% for 5 minutes.
- Redis connectivity, rejected writes, limiter errors, or memory pressure; production policy should remain `noeviction`.
- Provider authentication errors immediately.
- Model-output validation failures above the established baseline.
- Container restart loops, OOM kills, or CPU throttling.

Tune alerts against real traffic to avoid both missed incidents and noisy pages.
