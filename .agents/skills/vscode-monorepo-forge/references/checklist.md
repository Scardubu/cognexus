# VS Code Monorepo Forge checklist

## Mandatory checks

- Inventory the workspace before changing it; preserve user files and existing conventions.
- Use dry-run or preview modes for destructive, bulk, history-rewriting, or environment-changing actions.
- Keep commands cross-platform or clearly identify platform-specific variants.
- Validate paths, quoting, permissions, exit codes, and rollback behavior.
- Never print or commit secrets, tokens, private keys, or sensitive environment values.
- Produce exact file paths, commands, expected results, and recovery instructions.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Monorepo Structure Assumed`
- `Protocol`
- `Step 1 — Intake`
- `Step 2 — Generate the `.code-workspace` File`
- `Step 3 — Generate `launch.json` (Debug All Apps)`
- `Step 4 — Generate `tasks.json``
- `Step 5 — Generate `turbo.json` Pipeline`
- `Step 6 — Per-Package Settings`
- `Installation Steps (one-time)`
- `Key Keybindings to Add`
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
