#!/usr/bin/env bash
# Idempotent local developer bootstrap for Cognexus v3.2.
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "ERROR: $PYTHON_BIN is not installed." >&2
  exit 1
fi

"$PYTHON_BIN" - <<'PY'
import sys
if not ((3, 11) <= sys.version_info[:2] < (3, 15)):
    raise SystemExit(
        f"Python 3.11-3.14 is required; found {sys.version.split()[0]}"
    )
PY

if [[ ! -d .venv ]]; then
  "$PYTHON_BIN" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip check

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example. Add OPENAI_API_KEY for live runs."
fi

mkdir -p data logs

ruff check .
ruff format --check .
mypy .
pytest --cov --cov-report=term-missing
python scripts/validate_repository.py
python -m skill_runtime.cli validate
python scripts/test_nexus.py --dry-run
python -m build

echo "Cognexus setup and validation completed successfully."
echo "Start the API with: uvicorn server.app:app --reload --host 127.0.0.1 --port 8000"
