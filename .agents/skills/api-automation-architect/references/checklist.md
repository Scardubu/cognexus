# API Automation Architect checklist

## Mandatory checks

- Map data ownership, invariants, failure domains, idempotency requirements, and consistency guarantees.
- Define typed boundaries for external inputs, internal state, persistence, and emitted events.
- Bound retries, timeouts, concurrency, queue depth, payload size, and resource consumption.
- Design for partial failure, cancellation, backpressure, replay, duplicate delivery, and safe recovery.
- Instrument latency, errors, saturation, retries, and business outcomes with low-cardinality telemetry.
- Include migrations, rollback, compatibility, and operational runbook implications.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Resilience Pattern Taxonomy`
- `Protocol`
- `Step 1 — Classify the Workflow`
- `Step 2 — Design the Workflow`
- `A. Operation Contract`
- `B. Step-by-Step Flow (text diagram)`
- `C. Resilience Configuration`
- `Step 3 — Generate Implementation`
- `Standard resilient call wrapper:`
- `Step 4 — Observability Checklist`
- `Step 5 — Idempotency Implementation`
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
