# Usage examples: API Contract Governance Architect

## Direct activation

- "Audit this REST API using the api contract governance architect workflow and classify every change as additive, behavioral, deprecating, or breaking."
- "Design a production-ready contract for the new /v1/payments endpoint with idempotency, pagination, error envelopes, and webhook signing."
- "Use api-contract-governance-architect to review the proposed schema change, identify backward compatibility risks, and produce the safest migration path."
- "Generate an expand-migrate-contract plan for renaming the `user_id` field to `account_id` without a coordinated flag-day release."
- "Produce an OpenAPI contract, consumer-driven contract tests, and a deprecation runbook for the legacy /v2/search endpoint."

## Composition example

1. Activate `api-contract-governance-architect` to define the contract boundary, classify changes, and produce the migration plan.
2. Activate `backend-domain-model-architect` to validate that the contract correctly reflects business invariants and aggregate boundaries.
3. Activate `security-hardening-auditor` when the contract touches authentication, authorization, webhook trust, replay protection, or sensitive field exposure.
4. Activate `testing-strategy-architect` to implement consumer-driven contract tests, schema regression suites, and idempotency replay tests.
5. Activate `opentelemetry-observability-architect` to instrument the contract boundary with spans, deprecation usage counters, and error-envelope metrics.
6. Activate `release-incident-operations-architect` for staged rollout, producer-before-consumer ordering, deprecation timelines, and rollback conditions.

## Expected response shape

```text
Assessment
- Confirmed findings (schema diff, breaking change classification, consumer impact)
- Assumptions (consumer list completeness, deployment order, backward-compat window)
- Priorities (P0 breaking changes, P1 behavioral changes, P2 deprecations)

Contract
- Resource semantics and operation definitions
- Request / response / error / pagination shapes
- Idempotency, authentication, and rate-limit contracts
- Webhook signing and replay-protection specification

Compatibility classification
- Additive: new optional fields, new enum values with documented unknown-value policy
- Behavioral: changed semantics on existing fields without field rename
- Deprecating: fields/endpoints with owner, sunset date, and telemetry
- Breaking: removed fields, narrowed types, changed required fields, semantic reversal

Migration path
- Expand-migrate-contract sequencing with deployment ordering
- Consumer fixture update requirements
- Rollback conditions and producer-side compatibility window

Security implications
- Sensitive field policy (over-return, logging)
- Webhook trust and replay window
- Authorization scope changes

Required tests
- Positive: happy-path contract examples
- Negative: schema violations, auth failures, malformed pagination cursors
- Compatibility: consumer fixtures against the new and previous contract
- Replay: idempotency key duplicate detection

Observability signals
- Deprecation usage counter by consumer
- Error-envelope code frequency histogram
- Pagination cursor exhaustion rate
- Idempotency replay rate by operation

Validation commands
- schema diff command and expected output
- contract test command and expected coverage
- replay test command and expected result

Residual risk
- Unresolved consumer not yet tested against new contract — owner and deadline
```
