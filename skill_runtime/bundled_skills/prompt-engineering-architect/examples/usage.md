# Usage examples: Prompt Engineering Architect

## Direct activation

- "Audit this implementation using the prompt engineering architect workflow and return prioritized findings."
- "Design a production-ready prompt engineering architect solution for the attached codebase with exact file paths and tests."
- "Use prompt-engineering-architect to review the current approach, identify risks, and propose the smallest safe upgrade."

## Composition example

1. Activate `prompt-engineering-architect` for the domain workflow.
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
