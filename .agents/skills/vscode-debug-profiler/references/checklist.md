# VS Code Debug & Profiler checklist

## Mandatory checks

- Inventory the workspace before changing it; preserve user files and existing conventions.
- Use dry-run or preview modes for destructive, bulk, history-rewriting, or environment-changing actions.
- Keep commands cross-platform or clearly identify platform-specific variants.
- Validate paths, quoting, permissions, exit codes, and rollback behavior.
- Never print or commit secrets, tokens, private keys, or sensitive environment values.
- Produce exact file paths, commands, expected results, and recovery instructions.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Three Profiling Tools in VS Code`
- `Protocol`
- `Step 1 — Classify the Problem`
- `Step 2 — Generate `launch.json``
- `Step 3 — CPU Profiling Workflow (step-by-step)`
- `Step 4 — Memory Leak Detection (step-by-step)`
- `Step 5 — Source Map Debugging (fixing "can't find source" errors)`
- `Step 6 — Advanced Debugger Features`
- `Required Extensions`
- `Quick Reference: Debug Toolbar`
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
