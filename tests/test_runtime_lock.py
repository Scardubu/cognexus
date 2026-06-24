"""Runtime dependency lock and SBOM parity tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from config.settings import PROJECT_ROOT
from scripts.verify_runtime_lock import verify_runtime_lock


def test_runtime_lock_covers_repository_requirements() -> None:
    summary = verify_runtime_lock(
        PROJECT_ROOT / "requirements.txt",
        PROJECT_ROOT / "constraints/runtime.txt",
    )
    assert summary.direct_requirements >= 20
    assert summary.locked_components == 70
    assert summary.sbom_components is None


def test_runtime_lock_rejects_sbom_version_drift(tmp_path: Path) -> None:
    requirements = tmp_path / "requirements.txt"
    lock = tmp_path / "runtime.txt"
    sbom = tmp_path / "runtime.cdx.json"
    requirements.write_text("example>=1,<3\n", encoding="utf-8")
    lock.write_text("example==2.0\n", encoding="utf-8")
    sbom.write_text(
        json.dumps(
            {
                "bomFormat": "CycloneDX",
                "specVersion": "1.6",
                "components": [{"name": "example", "version": "2.1"}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="version_mismatch"):
        verify_runtime_lock(requirements, lock, sbom_path=sbom)
