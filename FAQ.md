# Cognexus FAQ

## What Is Cognexus?

Cognexus is a local AI orchestration service. It can run from the command line or as an
HTTP API. It routes tasks, recommends skills, manages sessions, and validates outputs.

## Do I Need An OpenAI API Key?

Not for installation, tests, or dry runs.

You need `OPENAI_API_KEY` only for live AI requests. Start with dry runs first.

## What Is A Dry Run?

A dry run is a safe test. Cognexus exercises its routing, sessions, tools, guardrails, and
validators without calling OpenAI.

Run:

```powershell
.venv\Scripts\python.exe scripts\test_nexus.py --dry-run
```

## Why Do Some Endpoints Return `401 Unauthorized`?

Protected endpoints require `NEXUS_API_KEY`.

Generate a local key:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Add it to `.env`, restart the server, then send it as:

```http
X-API-Key: your-key
```

## What Is The Difference Between `/health` And `/ready`?

- `/health` means the process is alive.
- `/ready` means Cognexus has checked important dependencies such as sessions, skills,
  secrets, and model configuration.

Use `/health` for basic uptime and `/ready` before sending real work.

## Why Does `/ready` Say `APIConnectionError` But Still Return Ready?

In development, `NEXUS_MODEL_VALIDATION_MODE=warn` allows the server to start even if the
OpenAI model catalog cannot be reached. This is intentional so local dry runs still work.

For strict production checks, set:

```dotenv
NEXUS_MODEL_VALIDATION_MODE=strict
```

## What Is A Session?

A session is a name for conversation continuity, such as `demo-session`. Local development
uses SQLite by default. Production deployments should use Redis.

## Which Execution Mode Should I Use?

Use `focus` if unsure.

| Mode | Good For |
|---|---|
| `focus` | Direct answers |
| `review` | Audits and risk checks |
| `research` | Evidence gathering |
| `architect` | System design |
| `brainstorm` | Exploring options |
| `incident` | Outage or recovery work |

## Can I Use Cognexus Without Docker?

Yes. The beginner path uses Python directly:

```powershell
python scripts/bootstrap.py
python scripts/start.py --env development --host 127.0.0.1 --port 8000
```

Docker is useful when you want Redis and container-like production behavior.

## Can I Expose My Local Server To Other People?

Do not expose a development server publicly. If another device on your private network must
reach it, use a strong `NEXUS_API_KEY`, exact trusted hosts/CORS origins, and understand the
risk of binding to `0.0.0.0`.

## Where Should I Start?

Start with [QUICKSTART.md](QUICKSTART.md), then read [docs/USER_GUIDE.md](docs/USER_GUIDE.md).
