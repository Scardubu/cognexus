# Production Codebase Zip Audit Skill checklist

## Mandatory checks

- Inventory the workspace before changing it; preserve user files and existing conventions.
- Use dry-run or preview modes for destructive, bulk, history-rewriting, or environment-changing actions.
- Keep commands cross-platform or clearly identify platform-specific variants.
- Validate paths, quoting, permissions, exit codes, and rollback behavior.
- Never print or commit secrets, tokens, private keys, or sensitive environment values.
- Produce exact file paths, commands, expected results, and recovery instructions.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Phase 0 — Extract & Map`
- `Phase 1 — Audit Dimensions`
- `1A — Build Correctness`
- `1B — Runtime Correctness`
- `1C — Accessibility (WCAG 2.2 AA)`
- `1D — Performance`
- `1E — Responsive Layout`
- `1F — Design System Integrity`
- `Phase 2 — Prioritize`
- `Phase 3 — Surgical Output`
- `Phase 4 — File Manifest`
- `File Manifest`
- `Stack-Specific Notes`
- `Next.js 15 / React 19`
- `Framer Motion`
- `Tailwind CSS v4`
- `TypeScript Strict Mode`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] High-risk actions have approval gates.
- [ ] Inputs and outputs are validated.
- [ ] Failure and rollback behavior are documented.
- [ ] Security and privacy implications are addressed.
- [ ] Tests or deterministic validation have run.
- [ ] Observability and maintenance implications are covered.
- [ ] No secrets or sensitive data appear in output.
