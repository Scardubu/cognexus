# OpenTelemetry Observability Architect checklist

## Mandatory checks

- Identify the user-visible or operational failure being prevented and define measurable acceptance criteria.
- Prefer deterministic checks before model-based or heuristic evaluation.
- Cover normal, boundary, malformed, timeout, cancellation, concurrency, and degraded-service paths.
- Keep telemetry low-cardinality, privacy-safe, correlated, and actionable.
- Make tests hermetic where possible and clearly label integration or network-dependent checks.
- Report what was actually executed; never claim a check passed without evidence.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Protocol`
- `Step 1 — Intake`
- `Step 2 — Generate in Order`
- `The Three Pillars`
- `Critical Setup Rule`
- `Fastify Plugin Registration`
- `Custom Spans for Business Logic`
- `BullMQ Job Tracing`
- `Structured Logging with Trace Correlation`
- `RED Metrics (Rate, Errors, Duration)`
- `Environment Configuration`
- `Local Development Stack (Docker)`
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
