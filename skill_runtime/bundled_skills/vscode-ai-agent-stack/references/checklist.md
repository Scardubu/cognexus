# VS Code AI Agent Stack checklist

## Mandatory checks

- Start with the simplest single-agent or deterministic workflow that can satisfy the task.
- Define agent roles, tool permissions, state ownership, termination conditions, and escalation paths.
- Use structured outputs and externally verifiable evidence instead of requesting hidden chain-of-thought.
- Apply progressive disclosure so only relevant skills, tools, and references enter context.
- Evaluate routing, tool use, safety, latency, cost, and task success with reproducible cases.
- Add bounded retries, fallbacks, human approval, tracing, and failure-safe behavior.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Protocol`
- `Step 1 — Intake`
- `Step 2 — Generate in Order`
- `The Three-Layer Model`
- `Tool Selection Guide`
- `Claude Code — Use when:`
- `GitHub Copilot — Use when:`
- `Cline (open-source, BYOK) — Use when:`
- `Continue.dev — Use when:`
- `Setup Instructions`
- `Step 1 — Install the Foundation (all users)`
- `Step 2 — GitHub Copilot Setup`
- `Step 3 — Cline Setup (optional, BYOK)`
- `Step 4 — The Hybrid Workflow`
- `Workspace Settings Block (copy-paste ready)`
- `Extension Install Commands`
- `Quality Gates`
- `Keybinding — Prevent Conflicts`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] High-risk actions have approval gates.
- [ ] Inputs and outputs are validated.
- [ ] Failure and rollback behavior are documented.
- [ ] Security and privacy implications are addressed.
- [ ] Tests or deterministic validation have run.
- [ ] Observability and maintenance implications are covered.
- [ ] No secrets or sensitive data appear in output.
