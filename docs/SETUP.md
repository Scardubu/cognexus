# NEXUS Setup Guide

If this is your first time using Cognexus, start with the shorter
[Quickstart](../QUICKSTART.md). This setup guide adds more detail and recovery paths.

## Prerequisites

- Windows 10/11 PowerShell, Linux, macOS, or WSL2.
- Python 3.11–3.14.
- Git.
- Docker Engine with Compose v2 for container deployment.
- Redis only when using the Redis backend outside Compose.
- An OpenAI API key for live runs. Dry runs and unit tests do not call OpenAI.

## Automated developer setup

Cross-platform, including native Windows PowerShell:

```bash
python scripts/bootstrap.py
```

Linux/macOS/WSL2 may also run the full validation bootstrap:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

`bootstrap.py` checks the supported Python range, verifies DNS and HTTPS reachability for
each configured primary or extra package index before pip runs, creates `.venv`, installs
against the certified runtime constraints, verifies the environment, and creates local
configuration directories. Diagnostics redact package-index credentials. It also supports
approved proxies, private package indexes, and deterministic offline wheelhouses.
`setup.sh` and `make bootstrap` delegate to this same hardened path. `setup.sh` then runs the
complete local quality and release gate.

## Manual developer setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade "pip>=26,<27" -c constraints/runtime.txt
python -m pip install -r requirements-dev.txt -c constraints/runtime.txt
python -m pip check
cp .env.example .env
mkdir -p data logs
```

Runtime-only environments may install:

```bash
python -m pip install -r requirements.txt -c constraints/runtime.txt
```

## Configure local development

The safe local baseline is SQLite with one worker:

```dotenv
NEXUS_ENV=development
NEXUS_HOST=127.0.0.1
NEXUS_WORKERS=1
NEXUS_SESSION_BACKEND=sqlite
NEXUS_SQLITE_PATH=./data/nexus_sessions.db
NEXUS_MODEL_VALIDATION_MODE=warn
NEXUS_MAX_CONCURRENT_RUNS=2
NEXUS_QUEUE_TIMEOUT_SECONDS=30
TRACE_INCLUDE_SENSITIVE=false
OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA=false
```

Add `OPENAI_API_KEY` only for live runs. Add `NEXUS_API_KEY` to require Bearer or `X-API-Key` authentication.

Model identifiers remain configurable:

```dotenv
NEXUS_ORCHESTRATOR_MODEL=gpt-5.5
NEXUS_SPECIALIST_MODEL=gpt-5.4-mini
NEXUS_GUARDRAIL_MODEL=gpt-5.4-mini
NEXUS_COMPACTION_MODEL=gpt-5.4-mini
```

`NEXUS_MODEL_VALIDATION_MODE` accepts:

- `off` — no Models API lookup.
- `warn` — report missing credentials or unavailable models without making readiness fail solely for that reason.
- `strict` — require all configured models to be available.

Checks are process-cached for `NEXUS_MODEL_VALIDATION_TTL_SECONDS`.

## Validate the installation

```bash
ruff check .
ruff format --check .
mypy .
pytest --cov --cov-report=term-missing
python scripts/test_nexus.py --dry-run
python scripts/build_distribution.py --no-isolation
```

The smoke command writes machine-readable JSON to stdout and diagnostics to stderr.

Online dependency audit (requires network access):

```bash
pip-audit -r constraints/runtime.txt
```

Validate configured models with a live key:

```bash
python scripts/test_nexus.py --dry-run --validate-models
```

## Start the API

Recommended local startup:

```bash
python scripts/start.py --env development
```

`scripts/start.py` prefers the project `.venv` interpreter when it exists, prepares local
`.env`, `data/`, `logs/`, and `artifacts/tmp/` state, verifies the runtime lock, runs the
offline dry-run smoke test, and then starts the configuration-driven server. This avoids
accidentally starting Cognexus with a global Python interpreter that is missing the
repository's pinned dependencies.

For auto-reload during local development:

```bash
python scripts/start.py --reload --host 127.0.0.1 --port 8000 --env development
```

Direct Uvicorn remains available when you have already activated the intended
environment:

```bash
uvicorn server.app:app --reload --host 127.0.0.1 --port 8000
```

For LAN access during deliberate local testing:

```bash
NEXUS_HOST=0.0.0.0 cognexus-server
```

Do not expose an unauthenticated development server to the public internet.

## Verify local endpoints

```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/ready
```

Dry-run API request:

```bash
curl -X POST http://127.0.0.1:8000/v1/run \
  -H "Content-Type: application/json" \
  -d '{
    "message":"Analyze this system architecture and propose improvements.",
    "session_id":"demo-session",
    "dry_run":true
  }'
```

Authenticated live request:

```bash
curl -X POST http://127.0.0.1:8000/v1/run \
  -H "Authorization: Bearer ${NEXUS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "message":"Analyze this system architecture and propose improvements.",
    "session_id":"demo-session"
  }'
```

## CLI

Dry run:

```bash
python -m orchestrator.run --dry-run --json "Analyze the current architecture"
```

PowerShell uses the backtick for line continuation, not the Bash backslash:

```powershell
python -m orchestrator.run `
  "Analyze this architecture and return a production checklist." `
  --session-id demo-session `
  --dry-run
```

The same command can also be run on one line:

```powershell
python -m orchestrator.run "Analyze this architecture and return a production checklist." --session-id demo-session --dry-run
```

Live run:

```bash
python -m orchestrator.run --session-id demo --json "Create a release checklist"
```

The CLI applies the same request timeout and bounded run gate used by the API.

## Redis setup

Start Redis locally:

```bash
docker run --rm --name nexus-redis -p 6379:6379 redis:7.4-alpine
```

Configure:

```dotenv
NEXUS_SESSION_BACKEND=redis
REDIS_URL=redis://localhost:6379/0
NEXUS_REDIS_CONNECT_TIMEOUT_SECONDS=2
NEXUS_REDIS_SOCKET_TIMEOUT_SECONDS=5
NEXUS_REDIS_MAX_CONNECTIONS=16
NEXUS_ALLOW_SQLITE_FALLBACK=true
```

Disable fallback in strict production deployments:

```dotenv
NEXUS_ALLOW_SQLITE_FALLBACK=false
```

## Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Compose defaults the application session backend to Redis, persists Redis and SQLite fallback data, runs the app as a non-root user, mounts the root filesystem read-only, drops capabilities, and constrains resources.

Verify:

```bash
docker compose ps
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:8000/ready
docker compose logs --tail=200 nexus
```

Enable the optional collector:

```bash
docker compose --profile observability up --build
```

## Troubleshooting

For a symptom-based guide, see [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md).

### Pip reports `No matching distribution` after DNS or socket errors

`openai-agents==0.17.6` is a valid release. When pip first reports `WinError 10051`,
`getaddrinfo failed`, or `Failed to resolve pypi.org`, the final `from versions: none` text
means pip received no package index response; it does not prove the pinned version is absent.

Run the repository-owned diagnostic before retrying:

```powershell
python scripts/bootstrap.py --diagnose-only
Resolve-DnsName pypi.org
Test-NetConnection pypi.org -Port 443
python -m pip config debug
Get-ChildItem Env:PIP_*,Env:HTTP_PROXY,Env:HTTPS_PROXY
```

Then use the appropriate safe path:

```powershell
# Standard public PyPI
python scripts/bootstrap.py

# Organization-approved proxy
python scripts/bootstrap.py --proxy http://proxy.example:8080

# Organization-approved private package index
python scripts/bootstrap.py --index-url https://packages.example/simple

# Offline wheelhouse copied from a matching connected machine
python scripts/bootstrap.py --wheelhouse .\wheelhouse
```

To prepare an offline wheelhouse on a connected machine using the same operating system,
CPU architecture, and Python minor version:

```powershell
python scripts/bootstrap.py --download-wheelhouse .\wheelhouse
```

Do not bypass TLS with `--trusted-host`, do not disable certificate validation, and do not
remove the certified dependency pin to work around a connectivity failure. On managed
networks, obtain the proxy, private index, or CA certificate path from the administrator.

### `OPENAI_API_KEY is required`

Use `--dry-run` for local validation or add the key through `.env` or the deployment secret manager.

### Readiness reports missing models

Confirm model identifiers and key permissions. Use `NEXUS_MODEL_VALIDATION_MODE=warn` during local development and `strict` only when the deployment must fail closed.

### Redis is unavailable

Check:

```bash
docker compose ps redis
docker compose logs redis
redis-cli -u "$REDIS_URL" ping
```

When SQLite fallback is enabled, readiness and run results report the degraded backend. No fallback is silent.

### Queue saturation

Inspect `nexus_run_queue_wait_seconds` and `nexus_runs_inflight`. Increase `NEXUS_MAX_CONCURRENT_RUNS` only after confirming CPU, memory, OpenAI rate limits, and downstream capacity. Prefer horizontal scaling with Redis for sustained concurrency.

### Import errors involving `agents`

The top-level `agents` package must come from `openai-agents`. Local specialist code belongs under `nexus_agents`. Remove stale local `agents/` directories, editable installs, or generated shims from the environment.

### SQLite lock pressure

Use one application worker with SQLite. For multiple workers or replicas, use Redis sessions.
