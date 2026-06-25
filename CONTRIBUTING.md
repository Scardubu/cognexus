# Contributing to Cognexus

## Development Setup

If you are new to the project, read [QUICKSTART.md](QUICKSTART.md) first. It explains the
local install and dry-run flow without assuming production knowledge.

With `make`:

```bash
make bootstrap
cp .env.example .env
make quality-quick
```

Cross-platform commands without `make`:

```bash
python scripts/bootstrap.py
python scripts/quality_gate.py --quick
python scripts/start.py --env development --host 127.0.0.1 --port 8000
```

Python 3.11-3.14 is supported. Python 3.13 is the primary development and release runtime.

## Engineering Rules

1. Preserve `/v1/*` API compatibility and the `NEXUS_*` configuration namespace unless a versioned migration is approved.
2. Keep model behavior probabilistic but authorization, limits, state transitions, and side effects deterministic.
3. Do not add local packages named `agents`; that namespace belongs to the OpenAI Agents SDK.
4. Do not log prompts, model outputs, secrets, authorization headers, or session content.
5. Every network, filesystem, database, or model call needs an explicit timeout or bounded lifecycle.
6. New tools require a strict schema, least-privilege scope, output bounds, error mapping, and tests.
7. New skills must use lowercase kebab-case directories, valid YAML frontmatter, concise activation instructions, and on-demand references.
8. Avoid dependencies when the standard library or an existing dependency is sufficient.

## Required Checks

```bash
make format
make quality
make audit
```

`make quality` runs linting, formatting checks, strict mypy, branch-aware tests, repository
integrity checks, skill validation, the offline smoke test, and distribution builds. The
network-backed dependency audit is separate so offline development remains deterministic.

## Pull Requests

Keep changes reviewable and include:

- the root cause and user or operational impact;
- compatibility and migration notes;
- tests for success, failure, and boundary behavior;
- security and observability implications;
- rollback instructions for deployment changes;
- documentation and changelog updates.

Generated caches, local databases, `.env`, credentials, and build outputs must not be committed.
