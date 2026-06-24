"""Regression tests for stable command-line metadata contracts."""

from __future__ import annotations

import sys

import pytest

from config.settings import APP_VERSION
from orchestrator.run import parse_args
from skill_runtime.cli import _parser


def test_cognexus_cli_reports_application_version(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["cognexus", "--version"])

    with pytest.raises(SystemExit) as exc_info:
        parse_args()

    assert exc_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"cognexus {APP_VERSION}"


def test_skill_cli_reports_application_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        _parser().parse_args(["--version"])

    assert exc_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"cognexus-skills {APP_VERSION}"


def test_server_cli_reports_application_version(capsys: pytest.CaptureFixture[str]) -> None:
    from server.run import _parser as server_parser

    with pytest.raises(SystemExit) as exc_info:
        server_parser().parse_args(["--version"])

    assert exc_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"cognexus-server {APP_VERSION}"
