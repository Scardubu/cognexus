# Effect-TS Layer Architect checklist

## Mandatory checks

- Map data ownership, invariants, failure domains, idempotency requirements, and consistency guarantees.
- Define typed boundaries for external inputs, internal state, persistence, and emitted events.
- Bound retries, timeouts, concurrency, queue depth, payload size, and resource consumption.
- Design for partial failure, cancellation, backpressure, replay, duplicate delivery, and safe recovery.
- Instrument latency, errors, saturation, retries, and business outcomes with low-cardinality telemetry.
- Include migrations, rollback, compatibility, and operational runbook implications.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Core Concepts Reference`
- `Layer Taxonomy`
- `Service Definition Pattern`
- `Protocol`
- `Step 1 — Classify the Request`
- `Step 2 — Generate or Audit`
- `For new service design:`
- `For Layer wiring:`
- `For error modeling:`
- `For migration (Promise → Effect):`
- `For Fiber supervision / concurrency:`
- `Step 3 — Output Format`
- `Quality Gates`
- `Activation Triggers`
- `Skill Chain`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] High-risk actions have approval gates.
- [ ] Inputs and outputs are validated.
- [ ] Failure and rollback behavior are documented.
- [ ] Security and privacy implications are addressed.
- [ ] Tests or deterministic validation have run.
- [ ] Observability and maintenance implications are covered.
- [ ] No secrets or sensitive data appear in output.
