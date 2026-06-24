# Release & Incident Operations Architect checklist

## Mandatory checks

- Define blast radius, failure modes, owner, success signal, abort threshold, and rollback procedure before any deployment begins — not after.
- Classify the change by reversibility, user impact, data mutation, and dependency coupling before choosing a delivery strategy.
- Verify that rollback steps are executable, account for irreversible data changes, and do not leave the system in a mixed-version state that causes new failures.
- Confirm that every database or data migration follows expand-migrate-contract sequencing so each step is independently deployable and independently reversible.
- Ensure health checks and synthetic monitors cover at least one end-to-end user journey, not just process liveness.
- Link every release gate and incident severity threshold to a user-facing SLO and its error budget burn rate, not to internal process metrics.
- Assign a bounded lifetime, a named owner, and a cleanup ticket to every feature flag and every temporary compatibility shim.
- Preserve incident evidence (timeline, artifacts, metrics snapshots) before remediation steps overwrite it.
- Produce blameless postmortems with concrete, time-bounded action items assigned to named owners — not vague improvements.
- Validate that communication steps (internal and external) are part of the runbook and are exercised in tabletop drills.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Change Risk Classification Matrix`
- `Step 1 — Classify Change Risk`
- `Step 2 — Choose Delivery Strategy`
- `A. Direct (low risk, small blast radius)`
- `B. Staged percentage rollout`
- `C. Canary with SLO-linked gates`
- `D. Blue-green deployment`
- `E. Flag-gated dark launch`
- `Step 3 — Database Migration Safety`
- `A. Expand-migrate-contract pattern`
- `B. Zero-downtime migration checklist`
- `Step 4 — Feature Flag Lifecycle`
- `Step 5 — SLO-Linked Monitoring and Gates`
- `Step 6 — Incident Response Playbook`
- `A. Severity criteria`
- `B. Roles and escalation`
- `C. Communication templates`
- `Step 7 — Blameless Postmortem Template`
- `Quality Gates`
- `Activation Triggers`
- `Skill Chain`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] Change risk is classified by reversibility, user impact, data mutation, and coupling.
- [ ] Blast radius at full rollout is documented.
- [ ] Rollback procedure is step-by-step, executable, and accounts for irreversible changes.
- [ ] Database migrations follow expand-migrate-contract sequencing.
- [ ] SLO-linked abort thresholds are defined and tied to real dashboards.
- [ ] Feature flags have owners, expiry dates, and cleanup tickets.
- [ ] Incident roles, severity criteria, and escalation paths are named.
- [ ] Communication cadence and templates are included.
- [ ] Postmortem has a concrete timeline, root cause, and owner-assigned action items.
- [ ] No secrets, credentials, or PII appear in postmortem or runbook documents.
