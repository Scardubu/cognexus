# Elite Skill Forge checklist

## Mandatory checks

- Start with the simplest single-agent or deterministic workflow that can satisfy the task.
- Define agent roles, tool permissions, state ownership, termination conditions, and escalation paths.
- Use structured outputs and externally verifiable evidence instead of requesting hidden chain-of-thought.
- Apply progressive disclosure so only relevant skills, tools, and references enter context.
- Evaluate routing, tool use, safety, latency, cost, and task success with reproducible cases.
- Add bounded retries, fallbacks, human approval, tracing, and failure-safe behavior.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `What a Skill Is`
- `Skill Generation Protocol`
- `Step 1 — Capture Intent`
- `Ingestion Protocol (for pasted prompts / existing documents)`
- `Step 2 — Generate Skills`
- `A. Frontmatter (trigger-optimized)`
- `B. Skill Body`
- `C. Activation Triggers (required section)`
- `Step 3 — Output Format`
- `Quality Standards`
- `Generating a Suite (3+ Skills)`
- `Skill Body Principles`
- `Quality Gates`
- `The 34-Skill Suite Map`
- `Creative Combinations`
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
