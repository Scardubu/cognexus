PYTHON ?= python3
VENV ?= .venv
BOOTSTRAP_ARGS ?=
BIN := $(VENV)/bin

.PHONY: help bootstrap start lint format type test validate verify-version verify-runtime-lock smoke server build verify-dist audit quality quality-quick skills-package release-checksums release-manifest clean

help:
	@printf '%s\n' \
	  'bootstrap       Create .venv and install development dependencies' \
	  'start           Run venv-aware preflight checks and start the API' \
	  'lint            Run Ruff lint checks' \
	  'format          Format Python sources with Ruff' \
	  'type            Run strict mypy' \
	  'test            Run tests with branch coverage' \
	  'validate        Validate repository and portable skills' \
	  'verify-version  Verify synchronized release versions' \
	  'verify-runtime-lock Verify runtime constraints and checked-in SBOM parity' \
	  'smoke           Run the offline Cognexus smoke test' \
	  'server          Start the configuration-driven HTTP server' \
	  'build           Build wheel and source distribution' \
	  'verify-dist     Verify imports, entry points, and bundled skills from the wheel' \
	  'audit           Audit runtime dependencies' \
	  'quality         Run the complete release gate' \
	  'quality-quick   Run the gate without building distributions' \
	  'skills-package  Build reproducible .skill archives' \
	  'release-checksums Create deterministic top-level release checksums' \
	  'release-manifest Create deterministic hashes/sizes for release artifacts' \
	  'clean           Remove generated artifacts and caches'

bootstrap:
	$(PYTHON) scripts/bootstrap.py --venv $(VENV) $(BOOTSTRAP_ARGS)

start:
	$(PYTHON) scripts/start.py --venv $(VENV)

lint:
	$(BIN)/ruff check .
	$(BIN)/ruff format --check .

format:
	$(BIN)/ruff check . --fix
	$(BIN)/ruff format .

type:
	$(BIN)/mypy .

test:
	@mkdir -p artifacts
	$(BIN)/pytest --cov --cov-report=term-missing --cov-report=xml:artifacts/coverage.xml

validate: verify-version verify-runtime-lock
	$(BIN)/python scripts/validate_repository.py
	$(BIN)/python scripts/verify_deployment.py
	$(BIN)/python .agents/skills/api-contract-governance-architect/scripts/validate_contract_policy.py
	$(BIN)/python .agents/skills/edge-cache-architecture-architect/scripts/validate_cache_policy.py
	$(BIN)/python .agents/skills/release-incident-operations-architect/scripts/validate_release_policy.py
	$(BIN)/python -m skill_runtime.cli validate

verify-version:
	$(BIN)/python scripts/verify_version.py

verify-runtime-lock:
	$(BIN)/python scripts/verify_runtime_lock.py

smoke:
	$(BIN)/python scripts/test_nexus.py --dry-run

server:
	$(BIN)/cognexus-server

build: verify-version
	rm -rf build dist
	$(BIN)/python scripts/build_distribution.py --no-isolation

verify-dist:
	$(BIN)/python scripts/verify_distribution.py

audit:
	$(BIN)/pip-audit -r constraints/runtime.txt

quality:
	$(BIN)/python scripts/quality_gate.py

quality-quick:
	$(BIN)/python scripts/quality_gate.py --quick

skills-package:
	$(BIN)/python -m skill_runtime.cli package --output dist/skills

release-checksums:
	$(BIN)/python scripts/create_checksums.py

release-manifest:
	$(BIN)/python scripts/create_release_manifest.py

clean:
	rm -rf .coverage .mypy_cache .pytest_cache .ruff_cache artifacts build dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
