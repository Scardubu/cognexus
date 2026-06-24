"""Venv-aware startup wrapper regression tests."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts import start


def test_select_python_prefers_project_venv(tmp_path: Path) -> None:
    venv = tmp_path / ".venv"
    executable = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    executable.parent.mkdir(parents=True)
    executable.write_text("", encoding="utf-8")

    assert start._select_python(venv, prefer_venv=True) == executable


def test_server_command_uses_configuration_launcher_without_reload() -> None:
    command = start._server_command(Path("python"), reload=False)

    assert command == ["python", "-m", "server.run"]


def test_server_command_uses_uvicorn_for_reload() -> None:
    command = start._server_command(Path("python"), reload=True)

    assert command == ["python", "-m", "uvicorn", "server.app:app", "--reload"]


def test_server_environment_applies_only_requested_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("NEXUS_HOST", "127.0.0.1")
    environment = start._server_environment(
        os.environ,
        host="127.0.0.2",
        port=9000,
        env_name="development",
    )

    assert environment["NEXUS_HOST"] == "127.0.0.2"
    assert environment["NEXUS_PORT"] == "9000"
    assert environment["NEXUS_ENV"] == "development"


def test_preflight_runs_runtime_lock_before_dry_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, ...]] = []

    def capture(_python: Path, command: tuple[str, ...]) -> None:
        calls.append(command)

    monkeypatch.setattr(start, "_run_check", capture)

    start._preflight(Path("python"), dry_run=True)

    assert calls == [
        ("scripts/verify_runtime_lock.py",),
        ("scripts/test_nexus.py", "--dry-run"),
    ]


def test_main_returns_preflight_failure_without_starting_server(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    launched: list[list[str]] = []

    monkeypatch.setattr(start, "_prepare_local_state", lambda: None)
    monkeypatch.setattr(start, "_same_interpreter", lambda _left, _right: True)

    def fail_preflight(_python: Path, *, dry_run: bool) -> None:
        del dry_run
        raise subprocess.CalledProcessError(7, ["python", "preflight"])

    def capture_launch(*args: Any, **kwargs: Any) -> Any:
        launched.append(list(args[0]))
        return subprocess.CompletedProcess(args[0], 0)

    monkeypatch.setattr(start, "_preflight", fail_preflight)
    monkeypatch.setattr("scripts.start.subprocess.run", capture_launch)

    assert start.main(["--no-venv", "--no-reexec"]) == 7
    assert launched == []
