# Detailed guidance: API Contract Governance Architect

> This reference preserves and reorganizes the supplied domain guidance. It is loaded on demand. Verify time-sensitive framework versions, security recommendations, legal requirements, prices, APIs, and platform behavior against authoritative current documentation before applying them. The core `SKILL.md` operating contract takes precedence if guidance conflicts.

# API Contract Governance Architect

Define and govern API contracts with contract-first discipline. Every boundary is
explicit, every breaking change is classified, every deprecation has an owner and
a sunset date. Retries cannot duplicate. Webhooks cannot be replayed.

---

## Contract-First Discipline

A contract is not the implementation — it is the agreement between producer and
consumer. Write it before writing code. Review it before merging. Test it before
shipping. Treat violations as bugs, not configuration.

```
Producer publishes schema →  Consumer generates typed client
Consumer writes fixtures  →  CI verifies fixtures against schema
Schema changes → diff     →  classify → approve → migrate → retire
```

---

## Step 1 — Identify the Contract Boundary

Before writing a single field, answer:

| Question | Why it matters |
|---|---|
| Who are all current consumers? | Breaking changes require migration plans for each. |
| What is the deployment order? | Producer-before-consumer for additive; consumer-before-producer for removal. |
| What data sensitivity applies? | Sensitive fields must never appear in errors, logs, or cursors. |
| What is the consistency need? | Strong vs eventual consistency shapes idempotency requirements. |
| What is the SLA on backward compat? | Determines minimum deprecation window. |
| Are there generated clients? | Regeneration must be coordinated with schema changes. |

---

## Step 2 — Define Resource and Operation Semantics

Define semantics independent of transport. Avoid letting HTTP method choices drive
business semantics.

```
Resource:  Payment
Identity:  payment_id (UUID v7, globally unique, immutable)
Lifecycle: created → processing → settled | failed | refunded
Ownership: belongs to exactly one account

Operations:
  POST /v1/payments           → create (idempotent via idempotency-key header)
  GET  /v1/payments/:id       → read (safe, cacheable for settled state)
  GET  /v1/payments           → list (cursor-paginated, mutable)
  POST /v1/payments/:id/refund → command (idempotent via idempotency-key)
  DELETE /v1/payments/:id     → NOT SUPPORTED — payments are immutable records
```

---

## Step 3 — Schema Design Patterns

### A. Error Envelope Standard

Every error response uses the same shape regardless of status code. This allows
consumers to handle errors generically without parsing status codes and message strings.

```typescript
// Shared error types used throughout these examples
class ContractError extends Error {
  constructor(public readonly code: string, message = code) { super(message); this.name = 'ContractError' }
}
class WebhookError extends Error {
  constructor(public readonly code: string, message = code) { super(message); this.name = 'WebhookError' }
}
```

```typescript
// TypeScript — canonical error envelope
interface ApiError {
  error: {
    code:    string          // stable machine-readable code, e.g. "payment_not_found"
    message: string          // human-readable, English, safe to log
    request_id: string       // correlates with server logs and traces
    details?: ErrorDetail[]  // field-level validation errors
  }
}

interface ErrorDetail {
  field:   string   // JSON path, e.g. "body.amount"
  code:    string   // stable, e.g. "must_be_positive"
  message: string
}
```

```python
# Python — pydantic error envelope
from pydantic import BaseModel
from typing import Optional

class ErrorDetail(BaseModel):
    field:   str
    code:    str
    message: str

class ApiErrorBody(BaseModel):
    code:       str
    message:    str
    request_id: str
    details:    Optional[list[ErrorDetail]] = None

class ApiErrorResponse(BaseModel):
    error: ApiErrorBody
```

**Stable error codes are a public contract.** Never change their meaning.
Add new codes for new conditions; deprecate old codes with a sunset date.

```
"payment_not_found"        → 404  (permanent)
"payment_already_settled"  → 409  (permanent, use for idempotent duplicates with diff state)
"amount_must_be_positive"  → 422  (permanent)
"rate_limit_exceeded"      → 429  (transient, safe to retry after Retry-After header)
"upstream_unavailable"     → 503  (transient, safe to retry with exponential backoff)
```

### B. Cursor Pagination Contract

Offset pagination is dangerous for mutable collections: insertions during traversal
cause items to be skipped or duplicated. Use opaque cursor pagination for all mutable
collections.

```typescript
interface PagedResponse<T> {
  data:          T[]
  next_cursor?:  string    // absent when no more pages
  has_more:      boolean
}

interface PageRequest {
  cursor?:  string          // opaque; treat as black box
  limit?:   number          // 1–100; default 20; server enforces maximum
  // No `page` or `offset` parameters
}
```

**Cursor contract rules:**
- Cursors are opaque — consumers must not parse or construct them.
- Cursors expire after a documented TTL (default: 5 minutes for mutable, 24 hours for immutable).
- Cursors must not embed sensitive data, user IDs, or private keys.
- A cursor from one filter/sort combination is invalid for another.
- The `limit` parameter applies to the current page only, not the total result set.

```typescript
// Example cursor implementation (server-side, not exposed to consumers)
import { createHmac, timingSafeEqual } from 'crypto'

function encodeCursor(payload: { id: string; ts: number }, secret: string): string {
  const data = Buffer.from(JSON.stringify(payload)).toString('base64url')
  const sig  = createHmac('sha256', secret).update(data).digest('base64url')
  return `${data}.${sig}`
}

function decodeCursor(cursor: string, secret: string): { id: string; ts: number } {
  const [data, sig] = cursor.split('.')
  const expected = createHmac('sha256', secret).update(data).digest('base64url')
  // Constant-time comparison
  if (!timingSafeEqual(Buffer.from(sig), Buffer.from(expected))) {
    throw new ContractError('invalid_cursor')
  }
  return JSON.parse(Buffer.from(data, 'base64url').toString())
}
```

### C. Partial-Update (PATCH) Contract

Use JSON Merge Patch (RFC 7396) for simple partial updates. Use JSON Patch (RFC 6902)
only when atomic multi-field updates are required. Never use PATCH to send a full
replacement body — that is what PUT is for.

```typescript
// JSON Merge Patch — absent fields are unchanged, null fields are cleared
PATCH /v1/users/:id
Content-Type: application/merge-patch+json

{ "display_name": "New Name", "avatar_url": null }
//  ^ updated                  ^ cleared (set to null/unset)
// All other fields are unchanged

// Rule: optional fields in the patch body must be explicitly typed as
// T | null, not T | undefined, to distinguish "not provided" from "clear this field"
interface UserPatch {
  display_name?: string | null    // null = clear; absent = no change
  avatar_url?:   string | null
  // email is NOT patchable — changing it requires email verification flow
}
```

---

## Step 4 — Idempotency and Replay Safety

Every write operation that has side effects (creates a resource, charges money, sends
a notification, triggers a workflow) must be idempotent via a client-supplied key.

```typescript
// Server-side idempotency key handler
import { createHash } from 'crypto'
import type { RedisClientType } from 'redis'

const IDEMPOTENCY_TTL_SECONDS = 86_400   // 24 hours

async function withIdempotency<T>(
  key:      string,
  redis:    RedisClientType,
  execute:  () => Promise<T>,
): Promise<{ result: T; replayed: boolean }> {
  if (!key || key.length > 255) {
    throw new ContractError('idempotency_key_invalid')
  }

  const cacheKey = `idem:${createHash('sha256').update(key).digest('hex')}`

  // Check for existing result
  const existing = await redis.get(cacheKey)
  if (existing !== null) {
    return { result: JSON.parse(existing) as T, replayed: true }
  }

  // Set a lock to prevent concurrent execution with same key
  const lock = await redis.set(`${cacheKey}:lock`, '1', {
    NX: true,
    EX: 30,
  })
  if (!lock) {
    throw new ContractError('idempotency_key_in_flight')   // 409; client should retry
  }

  try {
    const result = await execute()
    // Store result before releasing lock
    await redis.setEx(cacheKey, IDEMPOTENCY_TTL_SECONDS, JSON.stringify(result))
    return { result, replayed: false }
  } finally {
    await redis.del(`${cacheKey}:lock`)
  }
}
```

**HTTP contract for idempotency:**
```
POST /v1/payments
Idempotency-Key: <client-generated UUID v4 or v7>

# First call:  201 Created    + X-Idempotency-Status: new
# Repeat call: 200 OK         + X-Idempotency-Status: replayed
# In-flight:   409 Conflict   + error.code: "idempotency_key_in_flight" (retry after 1s)
# Conflict:    409 Conflict   + error.code: "idempotency_key_mismatch" (different body, same key)
```

---

## Step 5 — Webhook Contract

Webhooks are consumer-pulled events published by the producer. Treat them as
an untrusted channel that any attacker can spoof.

### Signing and replay defense

```typescript
import { createHmac, timingSafeEqual } from 'crypto'

const WEBHOOK_SECRET_BYTES  = 32      // 256-bit minimum
const REPLAY_WINDOW_SECONDS = 300     // 5 minutes

interface WebhookEnvelope<T> {
  id:         string   // UUID v7, unique per delivery; use for deduplication
  timestamp:  number   // Unix epoch seconds at time of emission
  type:       string   // stable event type, e.g. "payment.settled"
  api_version: string  // e.g. "2026-01-01"
  data:       T
}

// Producer — sign the payload
function signWebhook(payload: string, secret: string, timestamp: number): string {
  const message = `${timestamp}.${payload}`
  return createHmac('sha256', secret).update(message).digest('hex')
}

// Consumer — verify signature and replay window
function verifyWebhook(
  rawBody:   string,
  signature: string,       // from X-Signature-SHA256 header: "t=<ts>,v1=<sig>"
  secret:    string,
): WebhookEnvelope<unknown> {
  const parts = Object.fromEntries(
    signature.split(',').map(p => p.split('=') as [string, string])
  )
  const ts  = parseInt(parts['t'] ?? '0', 10)
  const sig = parts['v1'] ?? ''

  // Replay window check
  const age = Math.abs(Date.now() / 1000 - ts)
  if (age > REPLAY_WINDOW_SECONDS) {
    throw new WebhookError('webhook_replay_rejected')
  }

  // Constant-time signature comparison
  const expected = signWebhook(rawBody, secret, ts)
  if (!timingSafeEqual(Buffer.from(sig, 'hex'), Buffer.from(expected, 'hex'))) {
    throw new WebhookError('webhook_signature_invalid')
  }

  return JSON.parse(rawBody) as WebhookEnvelope<unknown>
}
```

### Delivery and deduplication contract

```typescript
// Consumer — idempotent event processor
const PROCESSED_TTL_SECONDS = 7 * 24 * 60 * 60  // 7 days

async function processWebhookEvent(
  event:  WebhookEnvelope<unknown>,
  redis:  RedisClientType,
  handle: (event: WebhookEnvelope<unknown>) => Promise<void>,
): Promise<{ status: 'processed' | 'duplicate' }> {
  const key = `webhook:seen:${event.id}`
  const set  = await redis.set(key, '1', { NX: true, EX: PROCESSED_TTL_SECONDS })
  if (!set) {
    return { status: 'duplicate' }   // already processed; return 200 to stop retries
  }
  await handle(event)
  return { status: 'processed' }
}
```

**Webhook contract rules:**
- Producers retry delivery with exponential backoff for 3 days on non-2xx.
- Consumers must return 2xx within 30 seconds or the delivery is retried.
- Consumers must process events idempotently using the `id` field.
- `type` values are stable and additive. New types will not break consumers with an
  unknown-type policy of `log and discard`.

---

## Step 6 — Breaking Change Classification Matrix

| Change | Classification | Migration required? |
|---|---|---|
| Add optional request field | Additive | No |
| Add optional response field | Additive | No (consumers must tolerate unknown fields) |
| Add new enum value | Additive | Document unknown-value policy; consumers must not switch exhaustively |
| Add new error code | Additive | Consumers with generic error handling: no change |
| Remove optional request field | Breaking | Yes — expand-migrate-contract |
| Remove required request field | Breaking | Yes — expand-migrate-contract |
| Remove response field | Breaking | Yes — consumers must stop using it first |
| Remove enum value | Breaking | Yes — all consumer references must migrate |
| Change field type (narrow) | Breaking | Yes |
| Change field semantics (same name, different meaning) | Breaking | Yes — rename required |
| Change error code meaning | Breaking | Yes — new code for new meaning; deprecate old |
| Change authentication scheme | Breaking | Yes — dual-auth compatibility window |
| Change rate limit policy | Behavioral | Document, notify consumers |
| Change cursor format | Breaking | Yes — existing cursors immediately invalid |
| Add required request field | Breaking | Yes — additive with default first |
| Change pagination default page size | Behavioral | Document explicit limit usage |
| Change idempotency window | Behavioral | Document, notify; 24h minimum recommended |
| Change webhook retry policy | Behavioral | Document, notify |
| Remove endpoint | Breaking | Yes — deprecation window required |

**Additive-only releases need no consumer coordination.**
All other categories require a migration plan.

---

## Step 7 — Expand-Migrate-Contract Sequencing

The expand-migrate-contract pattern allows zero-downtime schema evolution without a
coordinated flag-day release.

```
Phase 1 — Expand (producer ships first, backward-compatible)
  - Add new field alongside old field
  - Both fields co-exist; old field is still populated and accepted
  - Producer emits both old and new field; reads both

Phase 2 — Migrate (consumers update independently)
  - Each consumer switches to the new field at their own pace
  - Telemetry confirms when old field usage drops to zero
  - Old field is still populated and accepted by the producer

Phase 3 — Contract (remove old field, close window)
  - Old field usage is zero (confirmed by telemetry)
  - Remove old field from producer response and documentation
  - Remove backward-compat read for old field in requests
  - Update consumer tests and generated clients
```

**Example: renaming `user_id` → `account_id`**

```
Phase 1 (week 0):
  Response: { "user_id": "u_123", "account_id": "u_123" }  ← both present
  Request:  accept both user_id and account_id in body
  Deprecation notice on user_id in docs and X-Deprecated-Fields header

Phase 2 (weeks 1–4):
  Consumers migrate to account_id independently
  Monitor: GET /v1/metrics/deprecation?field=user_id until count approaches zero

Phase 3 (week 5+, after telemetry confirms):
  Response: { "account_id": "u_123" }   ← user_id removed
  Request:  reject user_id; return 422 with error.code: "field_removed"
```

---

## Step 8 — Consumer-Driven Contract Tests

Contract tests verify that the API producer honors its contract from the consumer's
perspective. They are faster and more reliable than end-to-end integration tests.

```typescript
// Using Pact (consumer-driven contract testing)
import { PactV3, MatchersV3 } from '@pact-foundation/pact'

const { like, eachLike, string, integer } = MatchersV3

const pact = new PactV3({
  consumer: 'billing-service',
  provider: 'payments-api',
})

describe('Payments API contract', () => {
  it('creates a payment with idempotency key', async () => {
    await pact
      .given('account acc_test exists with sufficient balance')
      .uponReceiving('a create-payment request with idempotency key')
      .withRequest({
        method: 'POST',
        path:   '/v1/payments',
        headers: {
          'Content-Type':    'application/json',
          'Idempotency-Key': string('idem_abc123'),
          'Authorization':   string('Bearer tok_test'),
        },
        body: {
          account_id: like('acc_test'),
          amount:     integer(1000),
          currency:   like('NGN'),
        },
      })
      .willRespondWith({
        status: 201,
        headers: { 'Content-Type': 'application/json' },
        body: {
          id:         like('pay_xyz'),
          status:     like('processing'),
          amount:     integer(1000),
          currency:   like('NGN'),
          account_id: like('acc_test'),
          created_at: like('2026-01-01T00:00:00Z'),
        },
      })
      .executeTest(async (mockServer) => {
        const client = new PaymentsClient(mockServer.url)
        const result = await client.createPayment({
          accountId:      'acc_test',
          amount:         1000,
          currency:       'NGN',
          idempotencyKey: 'idem_abc123',
        })
        expect(result.id).toMatch(/^pay_/)
        expect(result.status).toBe('processing')
      })
  })

  it('returns stable error envelope for validation failures', async () => {
    await pact
      .given('any account')
      .uponReceiving('a create-payment with negative amount')
      .withRequest({
        method: 'POST',
        path:   '/v1/payments',
        headers: { 'Content-Type': 'application/json', 'Authorization': string('Bearer tok_test') },
        body:   { account_id: like('acc_test'), amount: integer(-1), currency: like('NGN') },
      })
      .willRespondWith({
        status: 422,
        body: {
          error: {
            code:       like('validation_failed'),
            message:    like('Request validation failed'),
            request_id: like('req_xyz'),
            details:    eachLike({ field: like('body.amount'), code: like('must_be_positive'), message: like('Amount must be greater than zero') }),
          },
        },
      })
      .executeTest(async (mockServer) => {
        const client = new PaymentsClient(mockServer.url)
        await expect(client.createPayment({ accountId: 'acc_test', amount: -1, currency: 'NGN' }))
          .rejects.toMatchObject({ code: 'validation_failed' })
      })
  })
})
```

---

## Step 9 — Deprecation Runbook

Every deprecation must be a managed project, not a surprise removal.

```markdown
## Deprecation: `user_id` field in Payment responses

**Deprecation date:** 2026-02-01
**Sunset date:**      2026-05-01  (90-day window)
**Owner:**            @platform-team
**Replacement:**      `account_id`

### Consumer notification checklist
- [ ] Docs updated with deprecation notice and migration guide
- [ ] HTTP header added: `Deprecation: Tue, 01 Feb 2026 00:00:00 GMT`
- [ ] HTTP header added: `Sunset: Fri, 01 May 2026 00:00:00 GMT`
- [ ] HTTP header added: `Link: <https://docs.example.com/migrations/user-id>; rel="deprecation"`
- [ ] Changelog entry and email to registered API consumers
- [ ] Telemetry counter added: `api_deprecated_field_usage_total{field="user_id"}`

### Migration tracking
- [ ] All known internal consumers migrated
- [ ] External consumer telemetry at zero for 14+ days
- [ ] Consumer list audit complete

### Sunset execution
- [ ] Removal merged behind a feature flag
- [ ] Gradual traffic shift: 10% → 50% → 100% over 7 days
- [ ] Monitoring alert: 5xx spike > 0.1% triggers immediate rollback
- [ ] Old compatibility code removed in the follow-up sprint
```

---

## Quality Gates

- Existing consumers continue to function under mixed-version rollout.
- Validation is deterministic and examples match the executable schema.
- Retries cannot duplicate side effects (idempotency key required and tested).
- Sensitive fields are neither over-returned nor present in error details or cursors.
- Deprecations have owners, telemetry signals, sunset dates, and reversible rollout plans.
- Generated clients or consumer fixtures pass against the changed contract.
- Webhook signatures are verified with constant-time comparison and a replay window.
- Unknown fields in requests and unknown enum values in responses have documented policies.
- Breaking changes have completed expand-migrate-contract sequencing, not just documentation.

---

## Activation Triggers

- "Add a new field to this API response"
- "Is this API change backward-compatible?"
- "Design the pagination contract for this collection"
- "Write the idempotency contract for this payment operation"
- "Add webhook support with replay protection"
- "Plan the deprecation of this endpoint / field"
- "Generate consumer-driven contract tests for this API"
- "What is the migration path for renaming this field?"
- "Review this OpenAPI diff for breaking changes"

---

## Skill Chain

**Feeds into:**
- `testing-strategy-architect` — consumer-driven contract tests, schema regression suites, idempotency replay tests.
- `security-hardening-auditor` — webhook trust model, sensitive field policy, replay protection correctness.
- `release-incident-operations-architect` — producer-before-consumer deployment ordering, deprecation timelines, rollback conditions.
- `opentelemetry-observability-architect` — deprecation usage counters, error-envelope metrics, idempotency replay rate instrumentation.

**Creative combination:** `api-contract-governance-architect` defines the contract and
classifies the migration. `backend-domain-model-architect` validates that the contract
correctly encodes business invariants. `testing-strategy-architect` generates the
consumer fixture suite. Together these three skills make API evolution safe, typed, and
testable at every stage.
