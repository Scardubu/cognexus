# Surgical Merge & Audit Skill checklist

## Mandatory checks

- Inventory the workspace before changing it; preserve user files and existing conventions.
- Use dry-run or preview modes for destructive, bulk, history-rewriting, or environment-changing actions.
- Keep commands cross-platform or clearly identify platform-specific variants.
- Validate paths, quoting, permissions, exit codes, and rollback behavior.
- Never print or commit secrets, tokens, private keys, or sensitive environment values.
- Produce exact file paths, commands, expected results, and recovery instructions.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Phase 0 — Intake`
- `Phase 1 — Exhaustive Diff`
- `Phase 2 — Gap Taxonomy`
- `Phase 3 — Produce Definitive Output`
- `Phase 4 — Audit Trail`
- `Merge Audit — [date]`
- `Source versions`
- `P0 fixes applied`
- `P1 fixes applied`
- `Regressions restored`
- `Conflicts resolved`
- `Unchanged (verified correct across all versions)`
- `Output Format`
- `Constraints & Guardrails`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] High-risk actions have approval gates.
- [ ] Inputs and outputs are validated.
- [ ] Failure and rollback behavior are documented.
- [ ] Security and privacy implications are addressed.
- [ ] Tests or deterministic validation have run.
- [ ] Observability and maintenance implications are covered.
- [ ] No secrets or sensitive data appear in output.
