# API contract governance playbooks

## Additive endpoint rollout

1. Capture the currently published schema and consumer fixtures as immutable baseline evidence.
2. Add fields as optional and preserve existing defaults, status codes, error codes, and pagination semantics.
3. Run schema linting, breaking-change detection, provider tests, and consumer fixtures before deployment.
4. Deploy the producer first behind a disabled capability flag; verify old consumers against the new producer.
5. Enable the capability for an internal cohort, then staged external cohorts while monitoring 4xx changes, validation failures, retry volume, and idempotency conflicts.
6. Roll back by disabling the capability; do not remove additive schema fields during the rollback window.

## Breaking-change prevention

Classify a change as breaking when it removes or renames a field, narrows an accepted value, changes a field type, makes optional input required, changes durable error semantics, or alters ordering/pagination guarantees. Stop promotion unless a versioned endpoint or an expand-migrate-contract plan exists. The migration must name consumers, owners, telemetry, sunset date, and a tested compatibility adapter.

## Retry-safe write design

- Require an idempotency key for retryable commands.
- Bind the key to authenticated principal, operation, and normalized request digest.
- Persist the first terminal response for the documented retention window.
- Return the stored response for exact replays and a stable conflict error for a reused key with a different digest.
- Test concurrent duplicate requests and timeout-after-commit behavior.

## Webhook delivery and verification

Sign the timestamp and exact request bytes. Reject stale timestamps before signature comparison, compare signatures in constant time, persist delivery identifiers to prevent replay, and document retry cadence plus terminal failure behavior. Rotate signing secrets with an overlap window and identify the key version in the signature header.

## Deprecation and retirement

A deprecation is not complete until usage telemetry shows no active consumers, the announced sunset date has passed, migration support is available, and a rollback path remains tested. Remove compatibility code only in a separate release after retirement evidence is approved.
