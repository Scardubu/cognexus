# AI Feature Architect checklist

## Mandatory checks

- Start with the simplest single-agent or deterministic workflow that can satisfy the task.
- Define agent roles, tool permissions, state ownership, termination conditions, and escalation paths.
- Use structured outputs and externally verifiable evidence instead of requesting hidden chain-of-thought.
- Apply progressive disclosure so only relevant skills, tools, and references enter context.
- Evaluate routing, tool use, safety, latency, cost, and task success with reproducible cases.
- Add bounded retries, fallbacks, human approval, tracing, and failure-safe behavior.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Core Primitives (AI SDK v6)`
- `Protocol`
- `Step 1 — Classify the Feature`
- `Step 2 — Streaming Chat Route (Next.js App Router)`
- `Step 3 — Structured Output with Zod`
- `Step 4 — Tool Calling`
- `Step 5 — RAG Pipeline (Retrieval-Augmented Generation)`
- `Step 6 — Multi-Model Routing`
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
