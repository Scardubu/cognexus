#!/usr/bin/env bash
# Network-resilient local developer bootstrap for Cognexus v3.3.1.
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "ERROR: $PYTHON_BIN is not installed." >&2
  exit 1
fi

"$PYTHON_BIN" scripts/bootstrap.py "$@"

# Diagnostic and wheelhouse-download modes intentionally stop before validation.
for argument in "$@"; do
  case "$argument" in
    --diagnose-only|--download-wheelhouse) exit 0 ;;
  esac
done

VENV_PYTHON=".venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "ERROR: expected virtual-environment interpreter at $VENV_PYTHON." >&2
  echo "Use scripts/bootstrap.py directly when selecting a custom --venv path." >&2
  exit 1
fi

"$VENV_PYTHON" scripts/quality_gate.py

echo "Cognexus setup and validation completed successfully."
echo "Start the API with: .venv/bin/cognexus-server"
