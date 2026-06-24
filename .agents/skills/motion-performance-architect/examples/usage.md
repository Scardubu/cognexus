# Usage examples: Motion Performance Architect

## Direct activation

- "Audit this implementation using the motion performance architect workflow and return prioritized findings."
- "Design a production-ready motion performance architect solution for the attached codebase with exact file paths and tests."
- "Use motion-performance-architect to review the current approach, identify risks, and propose the smallest safe upgrade."

## Composition example

1. Activate `motion-performance-architect` for the domain workflow.
2. Activate `testing-strategy-architect` before defining the validation plan.
3. Activate `security-hardening-auditor` when the change touches trust boundaries, authentication, authorization, secrets, financial data, or external execution.
4. Activate `opentelemetry-observability-architect` before production rollout.

## Expected response shape

```text
Assessment
- Confirmed findings
- Assumptions
- Priorities

Changes
- path/to/file.ext — purpose

Validation
- command — observed result

Operations
- setup, rollout, rollback, monitoring

Residual risk
- unresolved issue and owner
```
