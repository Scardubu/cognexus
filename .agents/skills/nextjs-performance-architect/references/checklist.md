# Next.js Performance Architect checklist

## Mandatory checks

- Identify the user-visible or operational failure being prevented and define measurable acceptance criteria.
- Prefer deterministic checks before model-based or heuristic evaluation.
- Cover normal, boundary, malformed, timeout, cancellation, concurrency, and degraded-service paths.
- Keep telemetry low-cardinality, privacy-safe, correlated, and actionable.
- Make tests hermetic where possible and clearly label integration or network-dependent checks.
- Report what was actually executed; never claim a check passed without evidence.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `The Four Cache Layers (must understand all four)`
- `Rendering Decision Tree`
- `Protocol`
- `Step 1 — Audit Input`
- `Step 2 — RSC Architecture Audit`
- `Step 3 — Caching Strategy`
- `Step 4 — Partial Prerendering (PPR)`
- `Step 5 — Turbopack Migration`
- `Step 6 — Bundle Analysis`
- `Step 7 — Core Web Vitals Fixes`
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
