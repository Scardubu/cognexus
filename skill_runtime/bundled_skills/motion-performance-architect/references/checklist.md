# Motion Performance Architect checklist

## Mandatory checks

- Confirm the product goal, target users, supported devices, accessibility level, and performance budget.
- Preserve existing design tokens and component contracts unless a migration is explicitly approved.
- Validate keyboard, screen-reader, reduced-motion, responsive, loading, error, and empty states.
- Prefer measurable changes tied to usability, conversion, Core Web Vitals, or maintenance cost.
- Avoid decorative complexity that increases bundle size, interaction latency, or cognitive load.
- Provide implementation-ready tokens, component boundaries, and verification steps.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Core Principles`
- `Step 1 — Classify Motion by Intent`
- `Step 2 — Property Selection Rules`
- `Compositor-Safe (always prefer)`
- `Layout-Triggering (never animate in production)`
- `Reflow Risk Table`
- `Step 3 — Performance Measurement Protocol`
- `In-Browser Profiling`
- `FPS Monitor (development only)`
- `Chrome DevTools Protocol (CI integration)`
- `Step 4 — will-change Discipline`
- `Step 5 — Reduced Motion System Contract`
- `Step 6 — Anti-Pattern Audit`
- `Step 7 — Route-Level Motion Budget`
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
