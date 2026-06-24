"""Cross-platform installation and dependency-resolution regression tests."""

from __future__ import annotations

import socket
from argparse import Namespace
from pathlib import Path

import pytest

from config.settings import PROJECT_ROOT
from scripts import bootstrap


def _args(**overrides: object) -> Namespace:
    values: dict[str, object] = {
        "wheelhouse": None,
        "index_url": "https://pypi.org/simple",
        "extra_index_url": [],
        "proxy": None,
        "cert": None,
        "timeout": 15,
        "retries": 5,
    }
    values.update(overrides)
    return Namespace(**values)


def test_install_command_uses_certified_runtime_constraints() -> None:
    command = bootstrap._pip_install_command(
        Path("python"),
        requirements=PROJECT_ROOT / "requirements-dev.txt",
        constraints=PROJECT_ROOT / "constraints/runtime.txt",
        args=_args(),
    )

    assert command[-4:] == [
        "-r",
        str(PROJECT_ROOT / "requirements-dev.txt"),
        "-c",
        str(PROJECT_ROOT / "constraints/runtime.txt"),
    ]
    assert "--index-url" in command
    assert "--no-index" not in command


def test_offline_install_command_disables_indexes(tmp_path: Path) -> None:
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    command = bootstrap._pip_install_command(
        Path("python"),
        requirements=PROJECT_ROOT / "requirements-dev.txt",
        constraints=PROJECT_ROOT / "constraints/runtime.txt",
        args=_args(wheelhouse=wheelhouse),
    )

    assert "--no-index" in command
    assert "--find-links" in command
    assert "--index-url" not in command
    assert str(wheelhouse.resolve()) in command


def test_network_probe_reports_dns_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_resolution(*_args: object, **_kwargs: object) -> object:
        raise socket.gaierror("name resolution unavailable")

    monkeypatch.setattr(socket, "getaddrinfo", fail_resolution)
    probe = bootstrap._probe_index("https://pypi.org/simple")

    assert not probe.ok
    assert not probe.dns_ok
    assert "DNS resolution failed" in probe.detail


def test_network_probe_rejects_insecure_package_index() -> None:
    probe = bootstrap._probe_index("http://pypi.org/simple")

    assert not probe.ok
    assert "must use HTTPS" in probe.detail


def test_safe_url_redacts_embedded_credentials() -> None:
    value = bootstrap._safe_url("https://build-user:secret@example.test/simple/token?x=1")

    assert value == "https://example.test/simple/token"
    assert "build-user" not in value
    assert "secret" not in value


def test_supported_python_contract() -> None:
    bootstrap._check_supported_python((3, 11))
    bootstrap._check_supported_python((3, 14))

    with pytest.raises(RuntimeError, match=r"Python 3\.11-3\.14"):
        bootstrap._check_supported_python((3, 10))
    with pytest.raises(RuntimeError, match=r"Python 3\.11-3\.14"):
        bootstrap._check_supported_python((3, 15))


def test_repository_install_surfaces_apply_runtime_constraints() -> None:
    paths = (
        PROJECT_ROOT / ".github/workflows/ci.yml",
        PROJECT_ROOT / ".github/workflows/release.yml",
        PROJECT_ROOT / "Makefile",
        PROJECT_ROOT / "scripts/setup.sh",
    )
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if "pip install -r requirements-dev.txt" in line:
                assert "-c constraints/runtime.txt" in line, f"unconstrained install in {path}"


def test_example_environment_file_is_loadable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    environment = tmp_path / ".env"
    environment.write_text(
        (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    from config.settings import Settings

    settings = Settings()
    assert settings.nexus_cors_origins == [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    assert settings.nexus_trusted_hosts == ["localhost", "127.0.0.1", "testserver"]
    assert settings.nexus_skill_allowed_names == []
    assert settings.nexus_skill_denied_names == []
