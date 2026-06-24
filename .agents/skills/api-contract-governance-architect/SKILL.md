---
name: api-contract-governance-architect
description: Defines and governs API contracts with contract-first discipline, explicit schemas, compatibility strategy, idempotency rules, deterministic errors, pagination policy, and safe deprecation. Use when designing or reviewing REST, webhook, or service contracts and preventing accidental breaking changes.
license: MIT
compatibility: Portable Agent Skills format; works with filesystem-based skill clients and Cognexus 3.3+.
metadata:
  cognexus.version: 3.3.0
  cognexus.category: backend-platform
  cognexus.risk: medium
  cognexus.progressive_disclosure: 'true'
---

# API Contract Governance Architect

## Activation boundary

**Use this skill when:** a shared API, webhook, event, or service boundary needs a new contract, compatibility review, schema governance, idempotency semantics, pagination, versioning, or migration plan.

**Do not use it when:** the task is an internal implementation detail with no consumer-facing boundary, or when a smaller deterministic schema check is sufficient.

## Operating contract

1. Inspect current consumers, schemas, generated clients, public examples, and deployment order before changing a contract.
2. Treat compatibility as a tested invariant. Preserve existing fields and semantics unless a migration is explicitly approved.
3. Validate untrusted input at the boundary and emit stable, machine-readable errors without leaking internals.
4. Make authentication, authorization, rate limits, idempotency, pagination, retries, and timeout behavior explicit.
5. Prefer additive evolution and expand-migrate-contract sequencing over coordinated flag-day releases.
6. Never claim compatibility or generated-client safety without schema diffing and contract tests.

## Workflow

1. Identify producers, consumers, ownership, data sensitivity, and failure modes.
2. Define resource and operation semantics independently of transport details.
3. Specify request, response, error, pagination, filtering, sorting, and partial-update shapes.
4. Define authentication, authorization, replay protection, idempotency, and retry contracts.
5. Compare the proposal against the prior contract and classify every change as additive, behavioral, deprecating, or breaking.
6. Add schema-driven positive, negative, compatibility, and replay tests.
7. Document rollout order, deprecation dates, telemetry, and rollback conditions.

## Required patterns

- OpenAPI or JSON Schema as a reviewable source of truth where practical.
- Stable error envelopes with durable codes and field-level details.
- Cursor pagination for mutable collections unless offset semantics are intentionally accepted.
- Idempotency keys and replay-safe processing for retryable writes.
- Signed webhooks with timestamp windows, replay storage, and constant-time signature verification.
- Explicit unknown-field policy and bounded request sizes.

## Quality gates

- Existing consumers continue to function under mixed-version rollout.
- Validation is deterministic and examples match the executable schema.
- Retries cannot duplicate side effects.
- Sensitive fields are neither over-returned nor logged.
- Deprecations have owners, telemetry, dates, and a reversible rollout plan.
- Generated clients or consumer fixtures pass against the changed contract.

## Output contract

Return the current-state finding, proposed contract, compatibility classification, migration path, security implications, required tests, observability signals, and exact validation commands. Separate verified evidence from assumptions.

## Pair this skill with

- `backend-domain-model-architect` for business invariants.
- `api-automation-architect` for external integration reliability.
- `security-hardening-auditor` for trust boundaries and replay defense.
- `testing-strategy-architect` for consumer-driven and schema contract tests.
