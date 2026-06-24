#!/usr/bin/env python3
"""Venv-aware local startup wrapper for the Cognexus HTTP API."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from collections.abc import MutableMapping, Sequence
from pathlib import Path
from typing import Final

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
DEFAULT_VENV: Final = PROJECT_ROOT / ".venv"


def _venv_python(venv_path: Path) -> Path:
    if os.name == "nt":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def _select_python(venv_path: Path, *, prefer_venv: bool) -> Path:
    candidate = _venv_python(venv_path)
    if prefer_venv and candidate.is_file():
        return candidate
    return Path(sys.executable)


def _same_interpreter(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return False


def _prepare_local_state() -> None:
    environment = PROJECT_ROOT / ".env"
    example = PROJECT_ROOT / ".env.example"
    if not environment.exists() and example.is_file():
        shutil.copyfile(example, environment)
        print("Created .env from .env.example; add OPENAI_API_KEY only for live runs.")
    for directory in (
        PROJECT_ROOT / "artifacts" / "tmp",
        PROJECT_ROOT / "data",
        PROJECT_ROOT / "logs",
    ):
        directory.mkdir(parents=True, exist_ok=True)


def _run_check(python: Path, command: Sequence[str]) -> None:
    printable = " ".join(command)
    print(f"+ {python} {printable}", flush=True)
    completed = subprocess.run(  # noqa: S603 -- fixed repository-owned commands.
        [str(python), *command],
        cwd=PROJECT_ROOT,
        check=False,
    )
    if completed.returncode != 0:
        raise subprocess.CalledProcessError(completed.returncode, [str(python), *command])


def _preflight(python: Path, *, dry_run: bool) -> None:
    _run_check(python, ("scripts/verify_runtime_lock.py",))
    if dry_run:
        _run_check(python, ("scripts/test_nexus.py", "--dry-run"))


def _server_command(python: Path, *, reload: bool) -> list[str]:
    if reload:
        return [str(python), "-m", "uvicorn", "server.app:app", "--reload"]
    return [str(python), "-m", "server.run"]


def _server_environment(
    base: MutableMapping[str, str],
    *,
    host: str | None,
    port: int | None,
    env_name: str | None,
) -> dict[str, str]:
    environment = dict(base)
    if host is not None:
        environment["NEXUS_HOST"] = host
    if port is not None:
        environment["NEXUS_PORT"] = str(port)
    if env_name is not None:
        environment["NEXUS_ENV"] = env_name
    return environment


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--venv", type=Path, default=DEFAULT_VENV)
    parser.add_argument("--no-venv", action="store_true", help="Use the current interpreter.")
    parser.add_argument("--host", help="Set NEXUS_HOST for this process.")
    parser.add_argument("--port", type=int, help="Set NEXUS_PORT for this process.")
    parser.add_argument("--env", dest="env_name", help="Set NEXUS_ENV for this process.")
    parser.add_argument("--reload", action="store_true", help="Start uvicorn with auto-reload.")
    parser.add_argument("--skip-preflight", action="store_true")
    parser.add_argument("--skip-dry-run", action="store_true")
    parser.add_argument("--no-reexec", action="store_true", help=argparse.SUPPRESS)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    python = _select_python(args.venv.resolve(), prefer_venv=not args.no_venv)
    current = Path(sys.executable)

    if not args.no_reexec and not _same_interpreter(python, current):
        os.execv(  # noqa: S606 -- re-execs the validated project interpreter without a shell.
            str(python),
            [str(python), str(Path(__file__).resolve()), *sys.argv[1:]],
        )

    if args.port is not None and not (1 <= args.port <= 65535):
        print("ERROR: --port must be between 1 and 65535.", file=sys.stderr)
        return 2

    _prepare_local_state()
    try:
        if not args.skip_preflight:
            _preflight(python, dry_run=not args.skip_dry_run)
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: startup preflight failed: {exc}", file=sys.stderr)
        return exc.returncode or 1

    command = _server_command(python, reload=args.reload)
    environment = _server_environment(
        os.environ,
        host=args.host,
        port=args.port,
        env_name=args.env_name,
    )
    print("+ " + " ".join(command), flush=True)
    try:
        completed = subprocess.run(  # noqa: S603 -- command is built from trusted constants.
            command,
            cwd=PROJECT_ROOT,
            env=environment,
            check=False,
        )
    except KeyboardInterrupt:
        return 130
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
