# Evaluations

Nexus includes deterministic Python tests and Promptfoo behavioral evaluations. Both are required because unit tests validate code contracts while evals measure probabilistic orchestration quality.

## Python validation

Run:

```bash
ruff check .
mypy .
pytest
python scripts/test_nexus.py --dry-run
```

Critical deterministic coverage includes:

- Health and readiness endpoints.
- API request validation.
- Buffered stream framing.
- SQLite persistence.
- Redis-to-SQLite fallback policy.
- Explicit stateless policy.
- Prompt-injection and output guardrails.
- ARCH-02 and ARCH-04 validation.
- Registry count, uniqueness, and loadability.

## Promptfoo installation

```bash
npm install --global promptfoo
promptfoo --version
```

## Run the included suite

Start Nexus:

```bash
NEXUS_HOST=0.0.0.0 cognexus-server
```

In another terminal:

```bash
promptfoo eval --config evals/promptfoo.yaml
promptfoo view
```

The configuration targets the local HTTP API and loads cases from `evals/cases/basic.yaml`.

## Included behavioral dimensions

- Orchestration: the answer should identify relevant architecture concerns and provide a reconciled recommendation.
- Routing: simple and complex requests should produce valid trace metadata and a configured tier/model choice.
- Safety: prompt-injection attempts should be rejected or safely handled.
- Format: successful responses must satisfy the HTTP response schema and include a valid NEXUS trace.

## Add a case

Append a case to `evals/cases/basic.yaml`:

```yaml
- description: Redis outage operational guidance
  vars:
    message: >-
      Provide a safe runbook for a Redis session outage in a two-replica production deployment.
    session_id: eval-redis-outage
  assert:
    - type: contains-any
      value:
        - readiness
        - restore Redis
        - multiple replicas
    - type: not-contains
      value: silently downgrade
```

Keep cases free of real credentials, customer data, and production identifiers.

## Establish a baseline

Before changing prompts, models, routing, or tools:

```bash
promptfoo eval --config evals/promptfoo.yaml --output evals/results/baseline.json
```

After the change:

```bash
promptfoo eval --config evals/promptfoo.yaml --output evals/results/candidate.json
```

Compare pass rate, latency, token use, and representative failures. Do not promote a candidate solely because aggregate score improves; review safety regressions and critical-case failures individually.

## CI strategy

The default GitHub CI runs deterministic checks and a dry-run smoke test without external credentials. Add a protected scheduled or pre-release workflow for live evals using a narrowly scoped OpenAI project key and a strict budget.

Recommended live-eval controls:

- Run against staging, not production.
- Use a dedicated API key and project budget.
- Limit concurrency.
- Store sanitized result artifacts.
- Require no critical safety regression.
- Require human review for prompt and routing changes.

## Troubleshooting

### Connection refused

Start Uvicorn or update the provider URL in `evals/promptfoo.yaml`.

### HTTP 401

Set the configured authorization header for Promptfoo when `NEXUS_API_KEY` is configured, or use a local development environment with authentication disabled.

### Non-deterministic failures

Repeat the case, inspect the trace block, and convert invariant behavior into a deterministic validator or unit test where possible. Use eval assertions for semantic quality rather than exact prose matching.
