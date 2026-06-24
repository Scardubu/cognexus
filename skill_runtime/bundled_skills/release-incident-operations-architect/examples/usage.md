# Usage examples: Release & Incident Operations Architect

## Direct activation

- "Design the rollout plan for this database migration using the release incident operations architect workflow, including blast radius, rollback conditions, and promotion gates."
- "Write the incident response playbook for a payment processing outage: severity criteria, roles, escalation path, communication cadence, and immediate mitigation steps."
- "Use release-incident-operations-architect to design a canary release for this breaking API change with SLO-linked automatic abort and rollback procedure."
- "Produce a blameless postmortem template for the session loss incident, with a 5-why root cause analysis and concrete action items with owners and due dates."
- "Design a feature flag lifecycle for the new checkout redesign: launch criteria, monitoring signals, percent-rollout schedule, and cleanup timeline."
- "Create the release runbook for the Redis upgrade: pre-deployment checks, staged traffic shift, health verification steps, and rollback procedure."

## Composition example

1. Activate `release-incident-operations-architect` to classify change risk, design the rollout strategy, define abort thresholds, and write the rollback procedure.
2. Activate `git-workflow-architect` for CI/CD pipeline configuration, artifact provenance, immutable image tagging, and branch protection rules.
3. Activate `testing-strategy-architect` to define the pre-release confidence suite, staging integration tests, and synthetic monitors that serve as promotion gates.
4. Activate `opentelemetry-observability-architect` to instrument the release markers, SLO dashboards, error budget burn alerts, and canary traffic comparison.
5. Activate `backend-systems-auditor` for dependency safety review, expand-migrate-contract sequencing, and data mutation reversibility analysis.

## Expected response shape

```text
Assessment
- Risk classification (reversibility, user impact, data mutation, dependency coupling)
- Blast radius (affected users/services/data at full rollout)
- Assumptions (deployment topology, Redis availability, rollback constraint)
- Priorities (P0 data safety, P1 availability, P2 performance)

Rollout design
- Delivery strategy: direct | staged | canary | dark | blue-green | flag-gated
- Migration order: producer-before-consumer or consumer-before-producer with window
- Stages: percentages, dwell times, promotion gates, abort conditions

Monitoring and SLO signals
- Dashboards to open before, during, and after deployment
- Synthetic checks covering critical user journeys
- Error budget burn rate threshold that triggers abort
- Alert conditions that require immediate rollback

Promotion gates
- Signal and threshold required to advance each stage
- Who approves or what automates the gate

Abort and rollback procedure
- Step-by-step rollback commands with exact syntax
- Data mutation reversibility analysis
- Stale handle / in-flight request drain procedure
- Communication steps on abort

Feature flag lifecycle (if applicable)
- Launch criteria and initial cohort
- Percent-rollout schedule and dwell at each step
- Owner, expiry date, and cleanup ticket

Incident playbook (if applicable)
- Severity criteria (SEV-1 through SEV-4)
- Roles: incident commander, communications lead, technical lead
- Escalation path and contact order
- Communication cadence: internal and external

Postmortem structure (if applicable)
- Timeline of events (UTC)
- Impact statement (users affected, duration, revenue/SLO impact)
- Root cause (5-whys)
- Contributing factors
- Action items: owner, due date, type (prevent/detect/mitigate)
- What went well / what to improve

Post-release cleanup
- Flags to remove, compatibility shims to retire, temporary code to delete
- Verification checklist for cleanup completion
```
