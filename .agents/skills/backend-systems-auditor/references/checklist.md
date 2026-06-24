# Backend Systems Auditor checklist

## Mandatory checks

- Map data ownership, invariants, failure domains, idempotency requirements, and consistency guarantees.
- Define typed boundaries for external inputs, internal state, persistence, and emitted events.
- Bound retries, timeouts, concurrency, queue depth, payload size, and resource consumption.
- Design for partial failure, cancellation, backpressure, replay, duplicate delivery, and safe recovery.
- Instrument latency, errors, saturation, retries, and business outcomes with low-cardinality telemetry.
- Include migrations, rollback, compatibility, and operational runbook implications.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Audit Dimensions`
- `1. Idempotency`
- `2. Observability`
- `3. Graceful Shutdown`
- `4. Database Migration Discipline`
- `5. API Design`
- `6. Reliability & Scalability`
- `Protocol`
- `Step 1 — Intake`
- `Step 2 — Audit Report`
- `Backend Audit: [Service/API Name]`
- `🔴 Critical (production risk — fix before shipping)`
- `🟡 Important (reliability risk — fix within sprint)`
- `🔵 Improvements (quality — fix when convenient)`
- `✅ Passes`
- `Observability Score: [0–10]`
- `Idempotency Score: [0–10]`
- `Shutdown Safety Score: [0–10]`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] High-risk actions have approval gates.
- [ ] Inputs and outputs are validated.
- [ ] Failure and rollback behavior are documented.
- [ ] Security and privacy implications are addressed.
- [ ] Tests or deterministic validation have run.
- [ ] Observability and maintenance implications are covered.
- [ ] No secrets or sensitive data appear in output.
