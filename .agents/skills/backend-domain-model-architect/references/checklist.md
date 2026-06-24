# Backend Domain Model Architect checklist

## Mandatory checks

- Map data ownership, invariants, failure domains, idempotency requirements, and consistency guarantees.
- Define typed boundaries for external inputs, internal state, persistence, and emitted events.
- Bound retries, timeouts, concurrency, queue depth, payload size, and resource consumption.
- Design for partial failure, cancellation, backpressure, replay, duplicate delivery, and safe recovery.
- Instrument latency, errors, saturation, retries, and business outcomes with low-cardinality telemetry.
- Include migrations, rollback, compatibility, and operational runbook implications.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Core Principles`
- `Workflow`
- `Step 1 — Extract Bounded Contexts`
- `Step 2 — Write the Glossary`
- `Step 3 — Define the Type Model (Effect-TS + TypeScript)`
- `Step 4 — Domain Services (Effect-TS Layers)`
- `Step 5 — Domain Events`
- `Step 6 — Application Service (Orchestration Layer)`
- `Domain Model Quality Gates`
- `Anti-Patterns`
- `Pair This Skill With`
- `Activation Triggers`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] High-risk actions have approval gates.
- [ ] Inputs and outputs are validated.
- [ ] Failure and rollback behavior are documented.
- [ ] Security and privacy implications are addressed.
- [ ] Tests or deterministic validation have run.
- [ ] Observability and maintenance implications are covered.
- [ ] No secrets or sensitive data appear in output.
