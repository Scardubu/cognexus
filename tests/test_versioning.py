"""Release version parity and verifier bootstrap tests."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from config.settings import APP_VERSION, PROJECT_ROOT
from scripts.verify_version import declared_versions, verify_versions


def test_release_critical_versions_are_synchronized() -> None:
    versions = verify_versions(APP_VERSION)
    assert versions
    assert set(versions.values()) == {APP_VERSION}
    assert declared_versions() == versions


def test_release_tag_mismatch_fails_closed() -> None:
    with pytest.raises(RuntimeError, match="does not match source"):
        verify_versions("v999.0.0")


def test_distribution_verifier_bootstraps_project_root(tmp_path: Path) -> None:
    """Direct script execution must not depend on cwd or an injected PYTHONPATH."""
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    # pytest-cov exports subprocess instrumentation variables. This bootstrap test
    # intentionally runs outside the repository, so prevent it from writing a
    # statement-only coverage fragment that cannot be merged with branch data.
    for key in tuple(environment):
        if key.startswith("COV_CORE_") or key == "COVERAGE_PROCESS_START":
            environment.pop(key, None)
    completed = subprocess.run(  # noqa: S603
        [sys.executable, str(PROJECT_ROOT / "scripts" / "verify_distribution.py"), "--help"],
        cwd=tmp_path,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Verify built Cognexus wheel" in completed.stdout
