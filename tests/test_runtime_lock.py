"""Runtime dependency lock and SBOM parity tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

from config.settings import PROJECT_ROOT
from scripts.verify_runtime_lock import verify_runtime_lock


def test_runtime_lock_covers_repository_requirements() -> None:
    summary = verify_runtime_lock(
        PROJECT_ROOT / "requirements.txt",
        PROJECT_ROOT / "constraints/runtime.txt",
    )
    assert summary.direct_requirements >= 20
    assert summary.locked_components == 72
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


def test_runtime_lock_accepts_platform_marked_exact_pins(tmp_path: Path) -> None:
    requirements = tmp_path / "requirements.txt"
    lock = tmp_path / "runtime.txt"
    requirements.write_text("example>=1,<3\n", encoding="utf-8")
    lock.write_text(
        'example==2.0\nposix-only==1.0; platform_system != "Windows"\n',
        encoding="utf-8",
    )

    summary = verify_runtime_lock(requirements, lock)

    assert summary.locked_components == 2


def test_development_requirements_accept_overlapping_runtime_pins() -> None:
    lock: dict[str, Version] = {}
    for raw in (PROJECT_ROOT / "constraints/runtime.txt").read_text(encoding="utf-8").splitlines():
        value = raw.split("#", 1)[0].strip()
        if not value:
            continue
        requirement = Requirement(value)
        specifier = next(iter(requirement.specifier))
        lock[canonicalize_name(requirement.name)] = Version(specifier.version)

    overlaps = 0
    for raw in (PROJECT_ROOT / "requirements-dev.txt").read_text(encoding="utf-8").splitlines():
        value = raw.split("#", 1)[0].strip()
        if not value or value.startswith(("-r ", "--requirement ")):
            continue
        requirement = Requirement(value)
        locked_version = lock.get(canonicalize_name(requirement.name))
        if locked_version is None:
            continue
        overlaps += 1
        assert locked_version in requirement.specifier, (
            f"development requirement {requirement} rejects certified runtime pin "
            f"{requirement.name}=={locked_version}"
        )

    assert overlaps >= 2
