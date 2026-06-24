# Accessibility System Architect checklist

## Mandatory checks

- Confirm the product goal, target users, supported devices, accessibility level, and performance budget.
- Preserve existing design tokens and component contracts unless a migration is explicitly approved.
- Validate keyboard, screen-reader, reduced-motion, responsive, loading, error, and empty states.
- Prefer measurable changes tied to usability, conversion, Core Web Vitals, or maintenance cost.
- Avoid decorative complexity that increases bundle size, interaction latency, or cognitive load.
- Provide implementation-ready tokens, component boundaries, and verification steps.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Non-Negotiables`
- `Protocol`
- `Step 1 — Map the Keyboard Journey`
- `Step 2 — Semantic Structure Audit`
- `Step 3 — Component Patterns`
- `Step 4 — Color and Contrast`
- `Step 5 — Reduced Motion`
- `Testing Protocol`
- `Automated (CI gate)`
- `Manual Checklist (before every PR)`
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
