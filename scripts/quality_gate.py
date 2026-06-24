#!/usr/bin/env python3
"""Run the deterministic Cognexus release gate and write a machine-readable report."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from collections.abc import Callable
from contextlib import suppress
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final, cast

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
DEFAULT_REPORT: Final = PROJECT_ROOT / "artifacts" / "quality-report.json"
CHECK_TIMEOUT_SECONDS: Final = 300
RUFF_CACHE_DIR: Final = "artifacts/ruff-cache"
PYTHON_CACHE_DIR: Final = PROJECT_ROOT / "artifacts" / "pycache"
TEMP_DIR: Final = PROJECT_ROOT / "artifacts" / "tmp"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import APP_VERSION  # noqa: E402


@dataclass(frozen=True, slots=True)
class CheckResult:
    """One quality-gate command result."""

    name: str
    command: list[str]
    returncode: int
    duration_seconds: float


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true", help="Skip distribution build")
    parser.add_argument("--audit", action="store_true", help="Run the network-backed pip audit")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser


def _terminate_process_group(process: subprocess.Popen[str]) -> None:
    """Terminate an entire check process tree so timeouts cannot leak children."""
    if os.name != "posix":
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        return

    kill_process_group = cast(
        "Callable[[int, int], None]",
        os.killpg,  # type: ignore[attr-defined]
    )
    try:
        kill_process_group(process.pid, int(signal.SIGTERM))
        process.wait(timeout=5)
    except (ProcessLookupError, subprocess.TimeoutExpired):
        with suppress(ProcessLookupError):
            kill_process_group(process.pid, 9)
        process.wait()


def _run(name: str, command: list[str]) -> CheckResult:
    """Run one bounded check and persist its complete output for diagnosis."""
    print(f"\n==> {name}: {' '.join(command)}", flush=True)
    started = time.perf_counter()
    log_path = PROJECT_ROOT / "artifacts" / f"quality-{name}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    PYTHON_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("PYTHONPYCACHEPREFIX", str(PYTHON_CACHE_DIR))
    env["TEMP"] = str(TEMP_DIR)
    env["TMP"] = str(TEMP_DIR)
    env["TMPDIR"] = str(TEMP_DIR)
    with log_path.open("w", encoding="utf-8") as log_file:
        process = subprocess.Popen(  # noqa: S603
            command,
            cwd=PROJECT_ROOT,
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
        try:
            returncode = process.wait(timeout=CHECK_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            _terminate_process_group(process)
            log_file.write(f"\nTimed out after {CHECK_TIMEOUT_SECONDS} seconds.\n")
            returncode = 124

    print(f"    returncode={returncode} log={log_path.relative_to(PROJECT_ROOT)}", flush=True)
    return CheckResult(
        name=name,
        command=command,
        returncode=returncode,
        duration_seconds=round(time.perf_counter() - started, 3),
    )


def _commands(*, python: str, quick: bool, audit: bool) -> list[tuple[str, list[str]]]:
    """Return deterministic checks bound to the invoking Python environment."""
    checks: list[tuple[str, list[str]]] = [
        ("environment-integrity", [python, "-m", "pip", "check"]),
        ("version-sync", [python, "scripts/verify_version.py"]),
        ("runtime-lock", [python, "scripts/verify_runtime_lock.py"]),
        ("ruff-lint", [python, "-m", "ruff", "check", "--cache-dir", RUFF_CACHE_DIR, "."]),
        (
            "ruff-format",
            [python, "-m", "ruff", "format", "--cache-dir", RUFF_CACHE_DIR, "--check", "."],
        ),
        ("mypy", [python, "-m", "mypy", "."]),
        (
            "bytecode-compile",
            [
                python,
                "-m",
                "compileall",
                "-q",
                "config",
                "middleware",
                "nexus_agents",
                "observability",
                "orchestrator",
                "security",
                "server",
                "sessions",
                "skill_runtime",
                "tools",
                "tracing",
                "validators",
            ],
        ),
        (
            "pytest",
            [
                python,
                "-m",
                "pytest",
                "-p",
                "no:cacheprovider",
                "-p",
                "no:tmpdir",
                "--cov",
                "--cov-report=term-missing",
                "--cov-report=xml:artifacts/coverage.xml",
            ],
        ),
        (
            "repository-inventory",
            [python, "scripts/generate_repository_inventory.py", "--check"],
        ),
        ("repository-integrity", [python, "scripts/validate_repository.py"]),
        ("deployment-verification", [python, "scripts/verify_deployment.py"]),
        (
            "api-contract-policy",
            [
                python,
                ".agents/skills/api-contract-governance-architect/scripts/validate_contract_policy.py",
            ],
        ),
        (
            "edge-cache-policy",
            [
                python,
                ".agents/skills/edge-cache-architecture-architect/scripts/validate_cache_policy.py",
            ],
        ),
        (
            "release-incident-policy",
            [
                python,
                ".agents/skills/release-incident-operations-architect/scripts/validate_release_policy.py",
            ],
        ),
        ("skill-validation", [python, "-m", "skill_runtime.cli", "validate"]),
        ("dry-run", [python, "scripts/test_nexus.py", "--dry-run"]),
    ]
    if audit:
        checks.append(
            ("dependency-audit", [python, "-m", "pip_audit", "-r", "constraints/runtime.txt"])
        )
    if not quick:
        checks.extend(
            [
                (
                    "distribution-clean",
                    [
                        python,
                        "-c",
                        (
                            "import shutil; "
                            "from pathlib import Path; "
                            "shutil.rmtree('build', ignore_errors=True); "
                            "shutil.rmtree('dist', ignore_errors=True); "
                            "[shutil.rmtree(path, ignore_errors=True) "
                            "for path in Path('.').glob('nexus_openai-*') "
                            "if path.is_dir()]"
                        ),
                    ],
                ),
                ("distribution-build", [python, "scripts/build_distribution.py", "--no-isolation"]),
                ("distribution-verify", [python, "scripts/verify_distribution.py"]),
                (
                    "skills-package",
                    [python, "-m", "skill_runtime.cli", "package", "--output", "dist/skills"],
                ),
                (
                    "runtime-sbom",
                    [
                        python,
                        "scripts/generate_sbom.py",
                        "--output",
                        "dist/cognexus-runtime.cdx.json",
                    ],
                ),
                (
                    "runtime-sbom-parity",
                    [
                        python,
                        "scripts/verify_runtime_lock.py",
                        "--sbom",
                        "dist/cognexus-runtime.cdx.json",
                        "--require-sbom",
                    ],
                ),
                ("release-checksums", [python, "scripts/create_checksums.py"]),
                ("release-manifest", [python, "scripts/create_release_manifest.py"]),
                (
                    "release-verification",
                    [
                        python,
                        "scripts/verify_release.py",
                        "--dist",
                        "dist",
                        "--sbom",
                        "dist/cognexus-runtime.cdx.json",
                        "--require-sbom",
                    ],
                ),
            ]
        )
    return checks


def main() -> int:
    args = _parser().parse_args()
    python = sys.executable
    checks = _commands(python=python, quick=args.quick, audit=args.audit)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    results: list[CheckResult] = []
    for name, command in checks:
        result = _run(name, command)
        results.append(result)
        if result.returncode != 0:
            break

    passed = len(results) == len(checks) and all(result.returncode == 0 for result in results)
    payload = {
        "schema_version": 1,
        "version": APP_VERSION,
        "passed": passed,
        "python": sys.version.split()[0],
        "checks": [asdict(result) for result in results],
        "total_duration_seconds": round(sum(result.duration_seconds for result in results), 3),
    }
    args.report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nQuality gate {'PASSED' if passed else 'FAILED'}; report: {args.report}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
