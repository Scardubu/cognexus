---
name: release-incident-operations-architect
description: Designs observable, reversible release and incident workflows using staged delivery, migration safety, kill switches, rollback plans, SLO-linked monitoring, and blameless learning. Use for canaries, feature flags, release gates, incident response, and post-release validation.
license: MIT
compatibility: Portable Agent Skills format; works with filesystem-based skill clients and Cognexus 3.3+.
metadata:
  cognexus.version: 3.3.0
  cognexus.category: release-tooling
  cognexus.risk: medium
  cognexus.progressive_disclosure: 'true'
---

# Release & Incident Operations Architect

## Activation boundary

**Use this skill when:** a change needs a rollout, rollback, feature flag, canary, migration sequence, production verification, incident playbook, or postmortem.

**Do not use it when:** no production behavior changes and ordinary CI validation fully covers the risk.

## Operating contract

1. Define blast radius, failure modes, owner, success signal, abort threshold, and rollback before deployment.
2. Prefer reversible, backward-compatible changes and independently deployable migration steps.
3. Treat health checks as dependency-aware service signals, not proof that a user journey works.
4. Keep feature flags bounded, owned, observable, and scheduled for removal.
5. Link release validation and incident severity to user-facing SLOs and error budgets.
6. Preserve evidence and timelines without exposing secrets or blaming individuals.

## Workflow

1. Classify change risk by user impact, data mutation, dependency coupling, and reversibility.
2. Map preconditions, migration order, compatibility window, and rollback constraints.
3. Choose direct, staged, canary, dark, blue/green, or flag-gated delivery.
4. Define dashboards, logs, traces, synthetic checks, and SLO thresholds that prove success.
5. Write deployment, verification, abort, rollback, and communication steps together.
6. Exercise failure injection or a tabletop scenario for high-risk changes.
7. Close the loop with post-release review, incident learning, and debt removal.

## Required patterns

- Forward- and backward-compatible expand-migrate-contract database changes.
- Small canary cohorts with automatic or explicitly owned promotion gates.
- Kill switches for externally amplified or high-risk behavior.
- Correlated release markers in telemetry and immutable artifact provenance.
- Incident roles, severity criteria, escalation paths, and communication cadence.
- Blameless postmortems with concrete owners and due dates.

## Quality gates

- A failed rollout can be stopped without corrupting data or stranding mixed versions.
- The team can identify the exact artifact, configuration, and migration state in production.
- Readiness, synthetic checks, and SLO signals cover the critical user journey.
- Rollback steps are executable and account for irreversible data changes.
- Flags and temporary compatibility code have expiration ownership.
- Incident actions preserve security, auditability, and customer communication quality.

## Output contract

Return the risk classification, rollout stages, migration order, health and SLO signals, promotion/abort thresholds, rollback procedure, incident ownership, communication plan, and post-release cleanup tasks.

## Pair this skill with

- `git-workflow-architect` for CI/CD and artifact hygiene.
- `testing-strategy-architect` for pre-release confidence.
- `opentelemetry-observability-architect` for release evidence.
- `backend-systems-auditor` for dependency and data safety.
