# Cognexus Troubleshooting

Use this guide when a command fails or the server does not behave as expected.

## First Checks

Run these from the repository root:

```powershell
git status --short --branch
.venv\Scripts\python.exe --version
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe scripts\verify_runtime_lock.py
```

Expected results:

- Git shows the branch and no unexpected modified files.
- Python is 3.11-3.14.
- `pip check` says no broken requirements.
- Runtime lock status is `verified`.

## Install Fails While Downloading Packages

Symptoms:

- `Failed to establish a new connection`
- `getaddrinfo failed`
- `No matching distribution found` after DNS or socket errors

What it means: Python could not reach the package index. The pinned dependency is usually
not the problem.

Try:

```powershell
python scripts/bootstrap.py --diagnose-only
Resolve-DnsName pypi.org
Test-NetConnection pypi.org -Port 443
python -m pip config debug
```

If you are on a managed network, ask for the approved proxy, private package index, or CA
certificate path. Do not disable TLS verification.

## `python` Uses The Wrong Environment

Symptoms:

- `No module named pytest`
- `No module named fastapi`
- Commands work with `.venv\Scripts\python.exe` but fail with `python`

Fix:

```powershell
.venv\Scripts\python.exe scripts\quality_gate.py --quick
python scripts/start.py --env development --host 127.0.0.1 --port 8000
```

`scripts/start.py` prefers `.venv` when it exists, so it helps avoid this mistake.

## Port 8000 Is Already In Use

Check:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

Use another port:

```powershell
python scripts/start.py --env development --host 127.0.0.1 --port 8001
```

Then open `http://127.0.0.1:8001/health`.

## `/health` Works But `/v1/run` Returns `401`

Protected endpoints need `NEXUS_API_KEY`.

1. Generate a key:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

2. Put it in `.env`:

   ```dotenv
   NEXUS_API_KEY=your-generated-value
   ```

3. Restart Cognexus.

4. Send `X-API-Key` or `Authorization: Bearer ...`.

## `/ready` Shows OpenAI Model Errors

If `NEXUS_MODEL_VALIDATION_MODE=warn`, local readiness may still pass. This lets dry runs
work while offline or before your OpenAI key is configured.

For live requests, verify:

- `OPENAI_API_KEY` is set in `.env`;
- the model names in `.env` are available to your OpenAI project;
- your network allows access to the OpenAI API.

## Live Requests Fail But Dry Runs Pass

Dry runs do not call OpenAI. Live requests do.

Check:

```powershell
.venv\Scripts\python.exe scripts\test_nexus.py --dry-run
curl.exe http://127.0.0.1:8000/ready
```

Then confirm `OPENAI_API_KEY` and model access.

## SQLite Cannot Create Or Open The Database

Create the local data folder:

```powershell
New-Item -ItemType Directory -Force data
```

Do not put the SQLite file on a read-only drive. For production or multiple workers, use
Redis instead of SQLite.

## Redis Is Unavailable

For local development, SQLite is simpler. Set:

```dotenv
NEXUS_SESSION_BACKEND=sqlite
```

For production, restore Redis rather than falling back to node-local SQLite across replicas.

## Quality Gate Fails

Run the quick gate first:

```powershell
.venv\Scripts\python.exe scripts\quality_gate.py --quick
```

The gate writes detailed logs under `artifacts/quality-*.log`. Open the log named after the
failed check.

## Logs To Check

Startup wrapper logs, if you launched it in the background:

```text
artifacts/cognexus-start.out.log
artifacts/cognexus-start.err.log
```

Quality gate logs:

```text
artifacts/quality-*.log
```

## Still Stuck?

When asking for help, share:

- the command you ran;
- the exact error text;
- your operating system;
- `python --version`;
- the relevant `request_id` from an API error response.

Do not share `.env`, API keys, bearer tokens, or private prompts.
