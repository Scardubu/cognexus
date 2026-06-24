# Release and incident operations playbooks

## Staged production release

1. Freeze the release candidate by digest and attach test evidence, dependency audit, SBOM, provenance, migration review, and rollback rehearsal.
2. Verify backup restoration and expand-migrate-contract compatibility before any data-changing deployment.
3. Deploy to an internal cohort, then 1%, 10%, 25%, 50%, and 100% traffic. Every stage has a dwell time and requires healthy availability, latency, error rate, saturation, business KPI, and security signals.
4. Abort automatically when an SLO threshold is exceeded or a critical synthetic journey fails.
5. Record release markers in traces, logs, metrics, and the incident timeline.
6. Keep compatibility adapters and the previous immutable artifact available through the rollback window.

## Rollback decision

Rollback is the default when customer impact is increasing and the change is reversible. Roll forward only when rollback would worsen data integrity, the corrective change is smaller and already verified, and the incident commander records the rationale. Drain in-flight work before changing incompatible workers and account for queued jobs created by the new version.

## SEV-1 incident command

- Incident commander owns decisions and cadence; the technical lead owns diagnosis and mitigation; communications lead owns stakeholder updates; scribe owns UTC timeline.
- Acknowledge within five minutes, establish command within ten minutes, and update internal stakeholders every fifteen minutes until impact stabilizes.
- Preserve evidence while protecting credentials and personal data.
- Prefer reversible containment: disable flags, stop rollout, shed noncritical load, isolate a dependency, or restore the prior artifact.
- Declare recovery only after critical journeys pass, queues drain, error budgets stabilize, and monitoring remains healthy for the defined observation window.

## Post-incident review

Publish impact, timeline, root cause, contributing factors, detection gaps, response analysis, and actions categorized as prevent, detect, or mitigate. Every action has an owner, due date, measurable completion evidence, and priority. The review is blameless but operationally accountable.
