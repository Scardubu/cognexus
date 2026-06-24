# Nigerian Fintech Compliance Architect checklist

## Mandatory checks

- Establish the applicable threat model, trust boundaries, jurisdiction, and data classification.
- Verify time-sensitive legal, regulatory, dependency, and platform claims against authoritative sources.
- Prefer deny-by-default authorization, least privilege, explicit validation, and auditable decisions.
- Separate confirmed findings from assumptions; assign severity and remediation ownership.
- Never expose secrets, credentials, personal data, or internal reasoning in outputs or logs.
- Require human approval before destructive, financial, privileged, or externally visible actions.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Regulatory Reference Frame (as of Finance Act 2023 / NRS 2026)`
- `Step 1 — Tax Computation Kernel`
- `Step 2 — FIRS e-Invoice Integration (Phase 1)`
- `Step 3 — Identity Validation (BVN / NIN / TIN / CAC)`
- `Step 4 — Currency and Number Formatting`
- `Step 5 — Lagos Pidgin (pcm) i18n`
- `Step 6 — NDPR Data Handling (Nigerian Data Protection Regulation)`
- `Quality Gates`
- `Pair This Skill With`
- `Activation Triggers`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] High-risk actions have approval gates.
- [ ] Inputs and outputs are validated.
- [ ] Failure and rollback behavior are documented.
- [ ] Security and privacy implications are addressed.
- [ ] Tests or deterministic validation have run.
- [ ] Observability and maintenance implications are covered.
- [ ] No secrets or sensitive data appear in output.
