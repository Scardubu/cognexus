# API Contract Governance Architect checklist

## Mandatory checks

- Identify all producers, consumers, shared schemas, generated clients, and deployment order before proposing any change.
- Classify every changed field, parameter, response code, header, error code, and semantic as additive, behavioral, deprecating, or breaking.
- Verify that existing consumers continue to function correctly under mixed-version rollout before promoting any change.
- Validate all request, response, error, and pagination shapes against the canonical schema and confirm examples are executable.
- Ensure retries cannot duplicate side effects: idempotency keys must be present, scoped, and replay-detectable for all write operations.
- Confirm sensitive fields are not over-returned, not logged, and not present in pagination cursors or error details.
- Assign an owner, sunset date, consumer telemetry signal, and reversible rollout plan to every deprecation.
- Define authentication, authorization, rate-limit, and webhook replay contracts explicitly — not implied by implementation.
- Bound request sizes, cursor lifetimes, page sizes, and header lengths; document the `unknown-field` and `unknown-enum-value` policy.
- Produce migration ordering (producer-before-consumer or consumer-before-producer) and document the compatibility window.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Contract-First Discipline`
- `Step 1 — Identify the Contract Boundary`
- `Step 2 — Define Resource and Operation Semantics`
- `Step 3 — Schema Design Patterns`
- `A. Error Envelope Standard`
- `B. Cursor Pagination Contract`
- `C. Partial-Update (PATCH) Contract`
- `Step 4 — Idempotency and Replay Safety`
- `Step 5 — Webhook Contract`
- `Step 6 — Breaking Change Classification Matrix`
- `Step 7 — Expand-Migrate-Contract Sequencing`
- `Step 8 — Consumer-Driven Contract Tests`
- `Step 9 — Deprecation Runbook`
- `Quality Gates`
- `Activation Triggers`
- `Skill Chain`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] All consumers and their schema dependencies are identified.
- [ ] Every change is classified by compatibility category with evidence.
- [ ] Idempotency contract is defined for all write operations.
- [ ] Sensitive field policy is explicit and verified.
- [ ] Migration ordering and compatibility window are documented.
- [ ] Contract tests cover positive, negative, compatibility, and replay paths.
- [ ] Deprecations have owners, telemetry, sunset dates, and rollback plans.
- [ ] Observability signals and alert conditions are named.
- [ ] No secrets or sensitive values appear in the contract output.
