# API Guide

This page shows the main Cognexus HTTP endpoints by example.

Base URL for local development:

```text
http://127.0.0.1:8000
```

## Authentication

Most endpoints require the local service key from `.env`:

```http
X-API-Key: your-service-key
```

You can generate one with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Public Health Checks

### Liveness

```powershell
curl.exe http://127.0.0.1:8000/health
```

Expected result:

```json
{"status":"ok","service":"cognexus","details":{"version":"3.3.1"}}
```

### Readiness

```powershell
curl.exe http://127.0.0.1:8000/ready
```

Expected result when local SQLite is healthy:

```json
{
  "status": "ready",
  "service": "cognexus"
}
```

## Run A Task

Use `dry_run: true` while learning. It tests the full Cognexus path without calling OpenAI.

```powershell
$key = (Get-Content .env | Where-Object { $_ -match '^NEXUS_API_KEY=' } | Select-Object -First 1) -replace '^NEXUS_API_KEY=', ''
curl.exe -X POST http://127.0.0.1:8000/v1/run `
  -H "X-API-Key: $key" `
  -H "Content-Type: application/json" `
  -d "{\"message\":\"Review startup health\",\"session_id\":\"api-demo\",\"dry_run\":true,\"execution_mode\":\"review\"}"
```

Important request fields:

| Field | Required | Plain Meaning |
|---|---:|---|
| `message` | Yes | The task you want Cognexus to handle. |
| `session_id` | No | A name for conversation history. Use letters, digits, `.`, `_`, `:`, or `-`. |
| `dry_run` | No | `true` means no OpenAI call. |
| `execution_mode` | No | `focus`, `review`, `research`, `architect`, `brainstorm`, or `incident`. |

## Recommend Skills

This endpoint is deterministic and does not call OpenAI.

```powershell
$key = (Get-Content .env | Where-Object { $_ -match '^NEXUS_API_KEY=' } | Select-Object -First 1) -replace '^NEXUS_API_KEY=', ''
curl.exe -X POST http://127.0.0.1:8000/v1/skills/recommend `
  -H "X-API-Key: $key" `
  -H "Content-Type: application/json" `
  -d "{\"message\":\"Review API compatibility and release safety\",\"execution_mode\":\"review\"}"
```

## Inspect A Session

```powershell
$key = (Get-Content .env | Where-Object { $_ -match '^NEXUS_API_KEY=' } | Select-Object -First 1) -replace '^NEXUS_API_KEY=', ''
curl.exe http://127.0.0.1:8000/v1/sessions/api-demo -H "X-API-Key: $key"
```

The response returns safe metadata only. It does not return raw message content.

## Metrics

```powershell
$key = (Get-Content .env | Where-Object { $_ -match '^NEXUS_API_KEY=' } | Select-Object -First 1) -replace '^NEXUS_API_KEY=', ''
curl.exe http://127.0.0.1:8000/metrics -H "X-API-Key: $key"
```

Prometheus metrics are useful for dashboards and alerts.

## Error Responses

Errors use a consistent shape:

```json
{
  "error": "http_error",
  "message": "invalid API key",
  "request_id": "req-...",
  "details": null
}
```

Share `request_id` with an operator when asking for help. Do not share API keys or `.env`
files.
