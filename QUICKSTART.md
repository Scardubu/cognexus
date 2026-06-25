# Cognexus Quickstart

This guide gets Cognexus running on your computer with the shortest safe local path.

You do not need to understand the architecture first. Follow the steps in order, and use
the checks after each step to confirm things are working.

## What You Will Have At The End

- Cognexus installed in a local Python environment named `.venv`.
- A local configuration file named `.env`.
- A running API at `http://127.0.0.1:8000`.
- A first dry-run request that does not call OpenAI or spend API credits.

## Before You Start

Install these first:

| Tool | Why You Need It | Check Command |
|---|---|---|
| Python 3.11-3.14 | Runs Cognexus | `python --version` |
| Git | Downloads the project | `git --version` |
| Internet access | Downloads Python packages | Open `https://pypi.org` in a browser |

If `python --version` shows Python 3.10 or older, install a newer Python before continuing.

## 1. Download The Project

```powershell
git clone https://github.com/Scardubu/cognexus.git
cd cognexus
```

Expected result: your terminal prompt is inside the `cognexus` folder.

## 2. Install Cognexus

This command creates `.venv`, installs dependencies, checks the dependency lock, and creates
local folders used by the app.

```powershell
python scripts/bootstrap.py
```

Expected result near the end:

```text
Cognexus dependencies installed and verified successfully.
```

If this fails because the network cannot reach PyPI, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## 3. Start Cognexus

```powershell
python scripts/start.py --env development --host 127.0.0.1 --port 8000
```

Expected result:

```text
Starting Cognexus on http://127.0.0.1:8000
Uvicorn running on http://127.0.0.1:8000
```

Leave this terminal open. It is now running the server.

## 4. Check That It Is Alive

Open a second terminal in the same `cognexus` folder and run:

```powershell
curl.exe http://127.0.0.1:8000/health
```

Expected result:

```json
{"status":"ok","service":"cognexus","details":{"version":"3.3.1"}}
```

## 5. Try Your First Task Without An API Key

The dry-run smoke test checks routing, sessions, tools, and output validation without calling
OpenAI:

```powershell
.venv\Scripts\python.exe scripts\test_nexus.py --dry-run
```

Expected result:

```json
{
  "status": "ok",
  "dry_run": true
}
```

## 6. Optional: Enable Live AI Requests

Dry runs are enough to verify the install. For live requests, add two values to `.env`:

```dotenv
OPENAI_API_KEY=your-openai-api-key
NEXUS_API_KEY=your-local-service-api-key
```

Generate `NEXUS_API_KEY` with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Restart Cognexus after editing `.env`.

## Where To Go Next

- New user tour: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- Common questions: [FAQ.md](FAQ.md)
- Fix problems: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Full setup details: [docs/SETUP.md](docs/SETUP.md)
- Production deployment: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
