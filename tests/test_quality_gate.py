"""Tests for deterministic quality-gate command construction."""

from __future__ import annotations

from scripts.quality_gate import _commands


def test_quality_gate_uses_invoking_python_for_all_python_tools() -> None:
    python = "/isolated/venv/bin/python"
    commands = _commands(python=python, quick=False, audit=True)

    assert commands
    assert all(command[0] == python for _, command in commands)
    assert any(name == "dependency-audit" for name, _ in commands)
    assert any(name == "environment-integrity" for name, _ in commands)
    assert any(name == "version-sync" for name, _ in commands)
    assert any(name == "runtime-lock" for name, _ in commands)
    assert any(name == "bytecode-compile" for name, _ in commands)
    assert any(name == "distribution-clean" for name, _ in commands)
    assert any(name == "distribution-build" for name, _ in commands)
    audit = next(command for name, command in commands if name == "dependency-audit")
    assert audit[-1] == "constraints/runtime.txt"
    build = next(command for name, command in commands if name == "distribution-build")
    assert build[-1] == "--no-isolation"


def test_quick_quality_gate_skips_network_audit_and_distribution_build() -> None:
    commands = _commands(python="python", quick=True, audit=False)
    names = {name for name, _ in commands}

    assert "dependency-audit" not in names
    assert "distribution-clean" not in names
    assert "distribution-build" not in names
    assert "distribution-verify" not in names
