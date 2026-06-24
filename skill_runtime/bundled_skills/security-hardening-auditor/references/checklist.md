# Security Hardening Auditor checklist

## Mandatory checks

- Establish the applicable threat model, trust boundaries, jurisdiction, and data classification.
- Verify time-sensitive legal, regulatory, dependency, and platform claims against authoritative sources.
- Prefer deny-by-default authorization, least privilege, explicit validation, and auditable decisions.
- Separate confirmed findings from assumptions; assign severity and remediation ownership.
- Never expose secrets, credentials, personal data, or internal reasoning in outputs or logs.
- Require human approval before destructive, financial, privileged, or externally visible actions.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `OWASP Top 10 Checklist (2025)`
- `Protocol`
- `Step 1 — Classify Request`
- `Step 2 — Authentication (Auth.js v5 / NextAuth v5)`
- `Step 3 — Authorization (Route + Resource)`
- `Step 4 — Security Headers`
- `Step 5 — Rate Limiting`
- `Step 6 — Input Validation`
- `Step 7 — SQL Injection Prevention`
- `Step 8 — Secrets Management`
- `Security Audit Report Format`
- `Security Audit: [Service/App Name]`
- `🔴 Critical (fix before any deployment)`
- `🟡 High (fix within 1 week)`
- `🟠 Medium (fix within sprint)`
- `✅ Passing`
- `Summary`
- `Quality Gates`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] High-risk actions have approval gates.
- [ ] Inputs and outputs are validated.
- [ ] Failure and rollback behavior are documented.
- [ ] Security and privacy implications are addressed.
- [ ] Tests or deterministic validation have run.
- [ ] Observability and maintenance implications are covered.
- [ ] No secrets or sensitive data appear in output.
