# Cognexus User Guide

This guide explains Cognexus in plain language and shows the safest way to use it.

## What Cognexus Does

Cognexus is a local API and command-line tool for coordinated AI work. It receives a task,
classifies what kind of help is needed, chooses a safe execution mode, can recommend useful
skills, and validates the response before returning it.

Think of it as a careful coordinator:

```text
Your task -> Cognexus -> routing + skills + session memory -> validated answer
```

## Who It Is For

Cognexus is useful if you want:

- a local, testable AI service instead of a one-off script;
- dry runs that prove the system is wired correctly before live model calls;
- session memory for longer conversations;
- production controls such as health checks, metrics, logging, and release gates.

It may be too much if you only need a single short script that calls one model once.

## The Three Ways To Use Cognexus

| Path | Best For | Starting Point |
|---|---|---|
| Dry run | Testing setup without OpenAI calls | `python scripts/test_nexus.py --dry-run` |
| Command line | One task from your terminal | `.venv\Scripts\python.exe -m orchestrator.run --dry-run "Review this plan"` |
| HTTP API | Apps, tools, and integrations | `POST /v1/run` |

## Core Words In Plain English

| Term | Plain Meaning |
|---|---|
| Dry run | A safe test run that does not call OpenAI. |
| Session | A named conversation history, such as `demo-session`. |
| Skill | A reusable instruction pack for a specialty area. |
| Execution mode | The style of work, such as focused answer, review, research, or incident response. |
| Readiness | A check that says whether the app is ready to receive traffic. |

See [GLOSSARY.md](GLOSSARY.md) for more definitions.

## Choose An Execution Mode

| Mode | Use When You Want |
|---|---|
| `focus` | A direct answer with minimal extra detail. |
| `review` | A risk-focused audit or second opinion. |
| `research` | Evidence gathering with uncertainty called out. |
| `architect` | A design with trade-offs and migration notes. |
| `brainstorm` | Several options before choosing a direction. |
| `incident` | Containment, recovery, verification, and follow-up. |

If you are unsure, use `focus`. It is the default.

## First Meaningful Task

Start with a dry run:

```powershell
.venv\Scripts\python.exe -m orchestrator.run `
  "Review my startup plan and suggest the safest next step." `
  --dry-run `
  --mode review `
  --session-id first-task `
  --json
```

You should see JSON with:

- `execution_mode`: `review`
- `session_backend`: usually `sqlite` for local use
- `trace_validation.valid`: `true`
- `recommended_skills`: a list of suggested skill packs

## Using The HTTP API

Start the server:

```powershell
python scripts/start.py --env development --host 127.0.0.1 --port 8000
```

Check it:

```powershell
curl.exe http://127.0.0.1:8000/health
```

Protected endpoints need `NEXUS_API_KEY` from `.env`.

```powershell
$key = (Get-Content .env | Where-Object { $_ -match '^NEXUS_API_KEY=' } | Select-Object -First 1) -replace '^NEXUS_API_KEY=', ''
curl.exe -X POST http://127.0.0.1:8000/v1/run `
  -H "X-API-Key: $key" `
  -H "Content-Type: application/json" `
  -d "{\"message\":\"Review startup health\",\"session_id\":\"guide-demo\",\"dry_run\":true,\"execution_mode\":\"review\"}"
```

## What To Read Next

- Installation from zero: [../QUICKSTART.md](../QUICKSTART.md)
- Setup details: [SETUP.md](SETUP.md)
- API reference by example: [API.md](API.md)
- Troubleshooting: [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- Production operations: [OPERATIONS.md](OPERATIONS.md)
