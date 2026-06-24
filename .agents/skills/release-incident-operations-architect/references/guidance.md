# Detailed guidance: Release & Incident Operations Architect

> This reference preserves and reorganizes the supplied domain guidance. It is loaded on demand. Verify time-sensitive framework versions, security recommendations, legal requirements, prices, APIs, and platform behavior against authoritative current documentation before applying them. The core `SKILL.md` operating contract takes precedence if guidance conflicts.

# Release & Incident Operations Architect

Design observable, reversible releases and blameless incident processes. Every change
has a blast radius, an abort condition, and a rollback procedure before it ships.
Every incident has a timeline, a root cause, and concrete action items.

---

## Change Risk Classification Matrix

Score every change before choosing a delivery strategy.

| Dimension | Low (1) | Medium (2) | High (3) |
|---|---|---|---|
| **Reversibility** | Stateless config | Schema additive | Data deletion / irreversible migration |
| **User impact** | Internal service | Subset of traffic | All users, all sessions |
| **Data mutation** | Read-only | Additive writes | Updates/deletes to existing records |
| **Dependency coupling** | Self-contained | Shared library | Multiple service coordination required |
| **Deployment complexity** | Single replica | Multi-replica | Multi-region / multi-service |

**Risk score = sum of dimension scores**

| Score | Category | Default strategy |
|---|---|---|
| 5–7  | Low     | Direct deploy with monitoring |
| 8–10 | Medium  | Staged percentage or flag-gated |
| 11–15 | High   | Canary + SLO-linked gates or blue-green |

---

## Step 1 — Classify Change Risk

Before writing any runbook, complete this intake:

```
Change: <one-line description>
Author: @handle
Risk score: <sum from matrix above>
Blast radius at full rollout:
  - Users affected: all | segment: <describe>
  - Data records at risk: <count or 'none'>
  - Services depending on this boundary: <list>
  - Revenue / SLO impact of failure: <estimate>
Reversibility:
  - Can be rolled back without data loss? yes | no | partial
  - Irreversible steps: <list or 'none'>
  - Rollback window: <e.g., "safe to roll back for 72h; after that, migration is permanent">
Preconditions:
  - Required migrations that must run first: <list>
  - Required consumer updates before producer deploys: <list>
  - Required flags or config before code deploys: <list>
```

---

## Step 2 — Choose Delivery Strategy

### A. Direct Deploy (low risk, score 5–7)

Use for stateless config changes, additive schema changes, feature additions behind
existing guards, and bug fixes with no behavioral change.

```bash
# Minimum monitoring checklist for direct deploys
open https://dashboards.example.com/error-rate       # 5-minute window before and after
open https://dashboards.example.com/latency-p95      # confirm no regression
open https://dashboards.example.com/slo/burn-rate    # confirm budget is not burning faster
```

### B. Staged Percentage Rollout

Use for medium-risk changes affecting all users. Reduce blast radius by routing
a small cohort first. Dwell at each stage long enough for SLO signal to stabilize.

```
Stage 1: 5%  of traffic → dwell 30 minutes → check error budget
Stage 2: 25% of traffic → dwell 1 hour    → check error budget
Stage 3: 50% of traffic → dwell 2 hours   → check error budget
Stage 4: 100% of traffic
```

```yaml
# Kubernetes — staged rollout via Deployment maxSurge / maxUnavailable
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge:        1     # add 1 new pod at a time
      maxUnavailable:  0     # never remove old pod until new one is healthy
  minReadySeconds: 30        # dwell before marking pod available
```

### C. Canary with SLO-Linked Gates

Use for high-risk changes. Route a small, observable cohort to the new version.
Compare SLO signals between canary and stable populations before promoting.

```yaml
# Example: Argo Rollouts canary with automatic analysis
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: cognexus-api
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 10             # 10% canary
        - pause: { duration: 10m }
        - analysis:
            templates:
              - templateName: cognexus-slo-check
        - setWeight: 50
        - pause: { duration: 20m }
        - analysis:
            templates:
              - templateName: cognexus-slo-check
      canaryService: cognexus-canary-svc
      stableService: cognexus-stable-svc
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: cognexus-slo-check
spec:
  metrics:
    - name: error-rate
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            # Argo Rollouts injects rollouts-pod-template-hash; use your custom label instead
            sum(rate(http_requests_total{status=~"5..",rollouts_pod_template_hash=~"$CANARY_HASH"}[5m]))
            /
            sum(rate(http_requests_total{rollouts_pod_template_hash=~"$CANARY_HASH"}[5m]))
      successCondition: result[0] < 0.01    # < 1% error rate
      failureLimit:     1
      interval:         2m
      count:            5
```

### D. Blue-Green Deployment

Use when in-place rolling updates are too risky (e.g., session format changes,
protocol upgrades, dependency-coupled service changes).

```
Blue (current production):  cognexus-blue.internal — receives 100% traffic
Green (new version):        cognexus-green.internal — idle, deployed, verified

Verification steps on Green:
  1. Run synthetic check suite against green endpoint directly
  2. Run smoke tests with production-like load against green
  3. Confirm green can read and write sessions created by blue
  4. Gate: error rate < 0.1%, p99 < SLO threshold

Traffic switch:
  Update load balancer / ingress to route 100% to green
  Blue remains live and unmodified for rollback window (default: 24h)

Rollback:
  Update load balancer to route 100% back to blue
  Blue was never modified — rollback is instantaneous and clean
```

### E. Flag-Gated Dark Launch

Use for features that change behavior in ways that are hard to test pre-production:
new algorithms, new UX flows, experimental pricing.

```typescript
// lib/flags.ts — type-safe feature flag with telemetry
interface Flag {
  name:     string
  enabled:  boolean
  cohort:   'all' | 'beta' | 'internal' | 'pct:N'
  owner:    string
  expires:  string    // ISO date — must be < 90 days from creation
  cleanup:  string    // Jira/Linear ticket URL
}

// Prometheus counter — define once at module level (prom-client example)
// import { Counter } from 'prom-client'
const flagEvaluationCounter = new Counter({
  name: 'feature_flag_evaluations_total',
  help: 'Feature flag evaluation count by flag and cohort',
  labelNames: ['flag', 'cohort'] as const,
})

const FLAGS: Record<string, Flag> = {
  new_checkout_flow: {
    name:    'new_checkout_flow',
    enabled:  process.env.FLAG_NEW_CHECKOUT_FLOW === 'true',
    cohort:  'pct:10',
    owner:   '@platform-team',
    expires: '2026-09-01',
    cleanup: 'https://linear.app/acme/issue/ENG-1234',
  },
}

function deterministicHash(input: string): number {
  let hash = 0x811c9dc5  // FNV-1a 32-bit offset basis
  for (let i = 0; i < input.length; i++) {
    hash ^= input.charCodeAt(i)
    hash = (hash * 0x01000193) >>> 0  // FNV prime, keep unsigned 32-bit
  }
  return hash
}

function isInternalUser(userId?: string): boolean {
  // Replace with your actual internal-user lookup (email domain, role claim, etc.)
  return userId?.endsWith('@internal.example.com') ?? false
}

export function isEnabled(flagName: string, userId?: string): boolean {
  const flag = FLAGS[flagName]
  if (!flag?.enabled) return false

  // Emit telemetry for every evaluation (wire to your metrics client; example uses prom-client)
  flagEvaluationCounter.inc({ flag: flagName, cohort: flag.cohort })

  if (flag.cohort === 'all') return true
  if (flag.cohort === 'internal') return isInternalUser(userId)
  if (flag.cohort.startsWith('pct:')) {
    const pct = parseInt(flag.cohort.slice(4), 10)
    // Deterministic: same user always gets same result
    // deterministicHash: stable 32-bit integer from a string (FNV-1a, no crypto overhead needed)
    return deterministicHash(userId ?? '') % 100 < pct
  }
  return false
}
```

---

## Step 3 — Database Migration Safety

### A. Expand-Migrate-Contract Pattern

Every schema change that removes or renames a field must go through three phases.
Never combine phases in a single deployment.

```sql
-- Example: rename column `user_id` → `account_id`

-- Phase 1: EXPAND (producer deploys first, backward-compatible)
ALTER TABLE payments ADD COLUMN account_id UUID;
UPDATE payments SET account_id = user_id;            -- backfill existing rows
-- Application code: reads account_id if present, falls back to user_id
-- Application code: writes both user_id and account_id on every INSERT/UPDATE
-- Constraint: NOT NULL on account_id not yet added

-- Phase 2: MIGRATE (consumers update, telemetry confirms old column unused)
-- Monitor: SELECT COUNT(*) FROM audit_log WHERE field_name = 'user_id' AND ts > NOW() - INTERVAL '7d'
-- Only proceed to Phase 3 when count approaches zero

-- Phase 3: CONTRACT (remove old column)
ALTER TABLE payments ALTER COLUMN account_id SET NOT NULL;
ALTER TABLE payments DROP COLUMN user_id;
-- Remove backward-compat code paths that read/write user_id
```

### B. Zero-Downtime Migration Checklist

```markdown
Before migration:
- [ ] Migration runs in a transaction with a savepoint
- [ ] Migration is tested on a production-size dataset in staging (time it)
- [ ] Migration holds no table lock for > 5 seconds (use CONCURRENT index creation)
- [ ] Application code handles both old and new schema simultaneously
- [ ] Read replicas lag is within acceptable window

During migration:
- [ ] Monitor replication lag during migration
- [ ] Monitor active connections and lock wait queue
- [ ] Confirm no queries are timing out on the affected table

After migration:
- [ ] ANALYZE updated tables for query planner accuracy
- [ ] Verify indexes are valid (not INVALID state)
- [ ] Run smoke queries against migrated data
- [ ] Confirm application continues to function with both code versions active
```

---

## Step 4 — Feature Flag Lifecycle

Every feature flag must have a defined life. Flags that outlive their welcome become
unmarked technical debt that nobody is willing to remove.

```
Creation  → Review → Dark launch → Graduated rollout → 100% → Cleanup → Deleted

Lifecycle rules:
  - Maximum lifetime: 90 days from creation (with documented exception for long experiments)
  - Owner must be a named individual or team, not a shared account
  - Cleanup ticket must be created at flag creation time, not at 100% rollout
  - Flag must be removed within 2 sprints of reaching 100%
  - Never ship a flag that guards a security or compliance control
```

```typescript
// Flag expiry monitoring — run daily in CI or on cron
import { FLAGS } from './lib/flags'

function checkFlagExpiry(): void {
  const today = new Date()
  for (const [name, flag] of Object.entries(FLAGS)) {
    const expiry = new Date(flag.expires)
    const daysLeft = Math.ceil((expiry.getTime() - today.getTime()) / 86_400_000)
    if (daysLeft <= 0) {
      console.error(`EXPIRED FLAG: ${name} (owner: ${flag.owner}, cleanup: ${flag.cleanup})`)
      process.exitCode = 1
    } else if (daysLeft <= 14) {
      console.warn(`FLAG EXPIRING SOON: ${name} expires in ${daysLeft} days`)
    }
  }
}
```

---

## Step 5 — SLO-Linked Monitoring and Gates

Release gates must be tied to user-facing SLOs, not to deployment process steps.
"Deployment succeeded" is not a valid gate. "Error budget burn rate < 5x for 15 minutes" is.

```typescript
// SLO definitions — single source of truth
const SLOs = {
  api_availability: {
    target:          0.999,      // 99.9% monthly
    error_budget_pct: 0.001,     // 0.1% = ~43 min/month
    burn_rate_alert: {
      fast:   { window: '5m',  threshold: 14.4 },   // consuming 100% budget in 1h
      slow:   { window: '1h',  threshold: 6 },       // consuming 100% budget in 6h
    },
  },
  api_latency_p99: {
    target_ms:       500,
    percentile:      0.99,
  },
}
```

**Promotion gate example (Prometheus / Grafana):**
```
Gate: Advance from 10% → 50% canary
Required signal (all must pass for 10 minutes):
  - error_rate_canary < 0.01  (< 1%)
  - p99_latency_canary < 500ms
  - error_budget_burn_rate_5m < 5.0
  - no SEV-1 or SEV-2 incidents open
Abort condition (any triggers immediate rollback):
  - error_rate_canary > 0.05  (> 5%)
  - p99_latency_canary > 2000ms
  - error_budget_burn_rate_5m > 14.4
```

---

## Step 6 — Incident Response Playbook

### A. Severity Criteria

| Severity | Criteria | Response time | Commander |
|---|---|---|---|
| SEV-1 | All users affected; revenue-critical path down; data loss or security breach | Immediate (< 5 min) | Senior Engineer on-call |
| SEV-2 | > 10% of users affected; major feature unavailable; SLO breach > 5x burn | < 15 min | Engineer on-call |
| SEV-3 | < 10% users affected; degraded performance; single region | < 30 min | Team on-call rotation |
| SEV-4 | Minor degradation; single user/account; no SLO impact | Next business hour | Engineering queue |

### B. Incident Roles

```markdown
Incident Commander (IC):
  - Declares severity and opens the incident channel
  - Coordinates all technical and communications actions
  - Controls the pace: calls status checks every 10–15 minutes
  - Makes the final call on rollback, escalation, and resolution

Technical Lead (TL):
  - Drives diagnosis and remediation
  - Proposes and executes mitigation steps
  - Does NOT split attention between fixing and communicating — that is the IC's job

Communications Lead (CL):
  - Writes and posts external status page updates
  - Drafts customer-facing communications for IC approval
  - Tracks stakeholder notifications and acknowledgments
  - Manages Slack announcements to internal stakeholders

Note-taker (NT):
  - Records timeline with UTC timestamps
  - Captures every hypothesis, action, and outcome during the incident
  - This raw log becomes the foundation of the postmortem
```

### C. Communication Templates

**Internal SEV-1 declaration:**
```
🔴 SEV-1 INCIDENT DECLARED — <service> — <brief description>
IC: @<name>  TL: @<name>  CL: @<name>
War room: #incident-<YYYYMMDD>-<slug>
Bridge: <video link>
Status page: <link>
Current impact: <users affected, % traffic, duration so far>
Known symptoms: <what we know>
Next update: T+15 min
```

**External status page update (during incident):**
```
We are investigating reports of <brief, non-technical description>.
Our team has identified the issue and is actively working on a fix.
Impact: <e.g., "Some users may experience delays when...">
Next update: <time>
```

**Resolution update:**
```
This incident has been resolved. <Service> is now operating normally.
Duration: <HH:MM>
Root cause: <brief description — omit if still under investigation>
We will publish a full postmortem within 72 hours.
We apologize for the disruption.
```

---

## Step 7 — Blameless Postmortem Template

```markdown
# Postmortem: <Incident Title>

**Severity:** SEV-<N>
**Date:** YYYY-MM-DD
**Duration:** HH:MM (detected: HH:MM UTC — resolved: HH:MM UTC)
**Author:** @handle
**Reviewers:** @handle, @handle
**Status:** draft | in-review | final

## Impact

- **Users affected:** <number or percentage>
- **Duration of user impact:** <HH:MM>
- **SLO impact:** <error budget consumed: e.g., "14 minutes of 99.9% availability budget">
- **Revenue / business impact:** <if quantifiable>

## Timeline (all times UTC)

| Time | Event |
|---|---|
| HH:MM | <symptom first appeared in telemetry / reported by user> |
| HH:MM | <alert fired / incident declared> |
| HH:MM | <first hypothesis and action> |
| HH:MM | <action outcome> |
| HH:MM | <correct hypothesis identified> |
| HH:MM | <mitigation applied> |
| HH:MM | <service restored> |
| HH:MM | <incident closed> |

## Root Cause

<One paragraph technical root cause. What specifically caused the failure?>

## 5-Whys

1. Why did users see errors? → <answer>
2. Why did <answer-1> happen? → <answer>
3. Why did <answer-2> happen? → <answer>
4. Why did <answer-3> happen? → <answer>
5. Why did <answer-4> happen? → <systemic root cause>

## Contributing Factors

- <Factor 1: e.g., "No alert existed for this failure mode">
- <Factor 2: e.g., "Runbook did not cover this scenario">
- <Factor 3: e.g., "Feature flag was not tested at 100% traffic">

## Action Items

| Action | Type | Owner | Due date | Ticket |
|---|---|---|---|---|
| <description> | Prevent / Detect / Mitigate | @handle | YYYY-MM-DD | <link> |
| <description> | Prevent / Detect / Mitigate | @handle | YYYY-MM-DD | <link> |

**Types:**
- **Prevent:** change that would have stopped this from happening
- **Detect:** alert, dashboard, or test that would have caught it faster
- **Mitigate:** runbook or automation that would have reduced impact faster

## What Went Well

- <e.g., "On-call responded within 3 minutes of alert">
- <e.g., "Rollback completed in under 5 minutes">

## What to Improve

- <e.g., "Detection took 12 minutes; alert threshold was too conservative">
- <e.g., "Runbook was incomplete for Redis failover scenario">
```

---

## Quality Gates

- Rollout can be stopped at any stage without corrupting data or stranding mixed versions.
- The team can identify the exact artifact, configuration version, and migration state deployed in every environment.
- Readiness, synthetic checks, and SLO signals cover at least one critical end-to-end user journey.
- Rollback steps are tested, executable, and account for irreversible data changes.
- Feature flags and temporary compatibility code have named owners and expiry dates.
- Incident actions preserve security, auditability, and customer communication quality.
- Postmortem action items are concrete, owner-assigned, and time-bounded.

---

## Activation Triggers

- "Design the rollout plan for this change"
- "Write the rollback procedure for this deployment"
- "What is our canary strategy for this release?"
- "Create an incident response playbook for <service>"
- "Write a postmortem for this incident"
- "Design the feature flag lifecycle for this rollout"
- "Is this database migration safe to run without downtime?"
- "What SLO signals should gate this canary promotion?"
- "We need a kill switch for this feature"
- "Write the communication plan for this incident"

---

## Skill Chain

**Feeds into:**
- `git-workflow-architect` — CI/CD pipeline, artifact provenance, immutable image tagging, branch protection.
- `testing-strategy-architect` — pre-release confidence suite, staging integration tests, synthetic monitors as promotion gates.
- `opentelemetry-observability-architect` — release markers in telemetry, SLO dashboards, error budget burn alerts, canary traffic comparison.
- `backend-systems-auditor` — dependency safety review, expand-migrate-contract sequencing, data mutation reversibility analysis.

**Creative combination:** `release-incident-operations-architect` designs the rollout
strategy and incident playbook. `opentelemetry-observability-architect` instruments
the SLO signals that drive promotion gates and abort conditions. `testing-strategy-architect`
generates the synthetic monitors and integration tests that serve as objective promotion
evidence. Together these three skills make every release observable, reversible, and
safe at every stage from canary to full production.
