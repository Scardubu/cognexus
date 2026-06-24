# Frontend Design Auditor checklist

## Mandatory checks

- Confirm the product goal, target users, supported devices, accessibility level, and performance budget.
- Preserve existing design tokens and component contracts unless a migration is explicitly approved.
- Validate keyboard, screen-reader, reduced-motion, responsive, loading, error, and empty states.
- Prefer measurable changes tied to usability, conversion, Core Web Vitals, or maintenance cost.
- Avoid decorative complexity that increases bundle size, interaction latency, or cognitive load.
- Provide implementation-ready tokens, component boundaries, and verification steps.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Audit Dimensions`
- `1. Visual Hierarchy`
- `2. Typography`
- `3. Color & Contrast`
- `4. Spacing & Layout`
- `5. Accessibility`
- `6. Motion & Interaction`
- `Protocol`
- `Step 1 — Intake`
- `Step 2 — Audit Report`
- `Design Audit: [Component/Page Name]`
- `Critical Issues (fix before shipping)`
- `Improvements (meaningfully elevate quality)`
- `Polish (finishing touches)`
- `What's Working`
- `Accessibility Score`
- `Step 3 — Corrected Code (if code was provided)`
- `Step 4 — Design Token Recommendations (if no system exists)`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] High-risk actions have approval gates.
- [ ] Inputs and outputs are validated.
- [ ] Failure and rollback behavior are documented.
- [ ] Security and privacy implications are addressed.
- [ ] Tests or deterministic validation have run.
- [ ] Observability and maintenance implications are covered.
- [ ] No secrets or sensitive data appear in output.
