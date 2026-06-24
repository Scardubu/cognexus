# Component Quality Gate checklist

## Mandatory checks

- Confirm the product goal, target users, supported devices, accessibility level, and performance budget.
- Preserve existing design tokens and component contracts unless a migration is explicitly approved.
- Validate keyboard, screen-reader, reduced-motion, responsive, loading, error, and empty states.
- Prefer measurable changes tied to usability, conversion, Core Web Vitals, or maintenance cost.
- Avoid decorative complexity that increases bundle size, interaction latency, or cognitive load.
- Provide implementation-ready tokens, component boundaries, and verification steps.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Protocol`
- `Step 1 — Intake`
- `Six Quality Dimensions`
- `1. TypeScript Contract`
- `2. Accessibility (WCAG AA)`
- `3. Performance`
- `4. Testing`
- `5. Storybook Stories`
- `6. Error & Loading States`
- `Audit Report Format`
- `Component Quality Gate: [ComponentName]`
- `TypeScript Contract`
- `Accessibility`
- `Performance`
- `Testing Coverage`
- `Storybook`
- `Error & Loading States`
- `Overall: [Production Ready | Needs Work | Blocked]`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] High-risk actions have approval gates.
- [ ] Inputs and outputs are validated.
- [ ] Failure and rollback behavior are documented.
- [ ] Security and privacy implications are addressed.
- [ ] Tests or deterministic validation have run.
- [ ] Observability and maintenance implications are covered.
- [ ] No secrets or sensitive data appear in output.
