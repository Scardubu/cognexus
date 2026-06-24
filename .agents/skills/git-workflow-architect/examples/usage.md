# Usage examples: Git Workflow Architect

## Direct activation

- "Audit this implementation using the git workflow architect workflow and return prioritized findings."
- "Apply the git workflow architect workflow in dry-run mode first, then provide exact commands and rollback steps."
- "Use git-workflow-architect to review the current approach, identify risks, and propose the smallest safe upgrade."

## Composition example

1. Activate `git-workflow-architect` for the domain workflow.
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
