# Data Visualization Architect checklist

## Mandatory checks

- Identify the user-visible or operational failure being prevented and define measurable acceptance criteria.
- Prefer deterministic checks before model-based or heuristic evaluation.
- Cover normal, boundary, malformed, timeout, cancellation, concurrency, and degraded-service paths.
- Keep telemetry low-cardinality, privacy-safe, correlated, and actionable.
- Make tests hermetic where possible and clearly label integration or network-dependent checks.
- Report what was actually executed; never claim a check passed without evidence.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Core Principles`
- `Step 1 — Choose the Right Chart Type`
- `Step 2 — Recharts Setup and Core Patterns`
- `Step 3 — Chart Accessibility (Non-Negotiable)`
- `Step 4 — High-Volume Data (Canvas Rendering)`
- `Step 5 — Responsive Chart Strategy`
- `Step 6 — Dashboard Data Architecture`
- `Quality Gates`
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
