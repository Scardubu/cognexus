#!/usr/bin/env python3
"""Verify built Cognexus wheel and source archives without source-tree imports."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import stat
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Final

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import APP_VERSION  # noqa: E402

DEFAULT_DIST: Final = PROJECT_ROOT / "dist"
EXPECTED_DISTRIBUTION: Final = "nexus-openai"
EXPECTED_VERSION: Final = APP_VERSION
EXPECTED_SKILLS: Final = 39
REQUIRED_SDIST_PATHS: Final = frozenset(
    {
        ".agents/skills/security-hardening-auditor/SKILL.md",
        ".github/workflows/ci.yml",
        "Dockerfile",
        "constraints/runtime.txt",
        "README.md",
        "deploy/kubernetes/deployment.yaml",
        "docs/VALIDATION_REPORT.md",
        "docs/FINAL_PRODUCTION_READINESS_REPORT.md",
        "docs/V3_3_1_PRODUCTION_READINESS_REPORT.md",
        "docs/V3_3_1_REPOSITORY_INVENTORY.md",
        "pyproject.toml",
        "requirements.txt",
        "scripts/create_checksums.py",
        "scripts/create_release_manifest.py",
        "scripts/generate_repository_inventory.py",
        "scripts/generate_sbom.py",
        "scripts/verify_deployment.py",
        "scripts/verify_release.py",
        "scripts/verify_runtime_lock.py",
        "scripts/quality_gate.py",
        "scripts/verify_distribution.py",
        "scripts/verify_version.py",
        "skill_runtime/bundled_skills/security-hardening-auditor/SKILL.md",
        "skill_runtime/bundled_skills/api-contract-governance-architect/examples/usage.md",
        "skill_runtime/bundled_skills/api-contract-governance-architect/references/checklist.md",
        "skill_runtime/bundled_skills/api-contract-governance-architect/references/guidance.md",
        "skill_runtime/bundled_skills/edge-cache-architecture-architect/examples/usage.md",
        "skill_runtime/bundled_skills/edge-cache-architecture-architect/references/checklist.md",
        "skill_runtime/bundled_skills/edge-cache-architecture-architect/references/guidance.md",
        "skill_runtime/bundled_skills/release-incident-operations-architect/examples/usage.md",
        "skill_runtime/bundled_skills/release-incident-operations-architect/references/checklist.md",
        "skill_runtime/bundled_skills/release-incident-operations-architect/references/guidance.md",
        "tests/test_runtime_lock.py",
        "tests/test_security_hardening.py",
    }
)
FORBIDDEN_SDIST_PARTS: Final = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "artifacts",
        "build",
        "dist",
    }
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "wheel",
        type=Path,
        nargs="?",
        help="Wheel to verify; defaults to the only wheel under dist/.",
    )
    parser.add_argument(
        "--sdist",
        type=Path,
        help="Source archive to verify; defaults to the only .tar.gz under dist/.",
    )
    return parser


def _resolve_single(candidate: Path | None, pattern: str, label: str) -> Path:
    if candidate is not None:
        resolved = candidate.resolve()
    else:
        matches = sorted(DEFAULT_DIST.glob(pattern))
        if len(matches) != 1:
            raise RuntimeError(
                f"expected exactly one {label} under {DEFAULT_DIST}, found {len(matches)}"
            )
        resolved = matches[0].resolve()
    if not resolved.is_file():
        raise RuntimeError(f"not a readable {label}: {resolved}")
    return resolved


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _safe_archive_name(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise RuntimeError(f"archive contains an unsafe path: {name!r}")
    return path


def _extract_wheel(wheel: Path, destination: Path) -> None:
    if not zipfile.is_zipfile(wheel):
        raise RuntimeError(f"not a wheel ZIP archive: {wheel}")
    with zipfile.ZipFile(wheel) as archive:
        validated: list[tuple[zipfile.ZipInfo, PurePosixPath]] = []
        for item in archive.infolist():
            path = _safe_archive_name(item.filename)
            mode = (item.external_attr >> 16) & 0xFFFF
            if mode and stat.S_ISLNK(mode):
                raise RuntimeError(f"wheel contains a symbolic link: {item.filename}")
            validated.append((item, path))

        for item, path in validated:
            target = destination.joinpath(*path.parts)
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(item) as source, target.open("xb") as output:
                while chunk := source.read(64 * 1024):
                    output.write(chunk)


def _verify_sdist(sdist: Path) -> tuple[str, int]:
    if not tarfile.is_tarfile(sdist):
        raise RuntimeError(f"not a readable source archive: {sdist}")
    with tarfile.open(sdist, mode="r:gz") as archive:
        members = archive.getmembers()
        roots: set[str] = set()
        relative_paths: set[str] = set()
        for member in members:
            path = _safe_archive_name(member.name)
            roots.add(path.parts[0])
            if member.issym() or member.islnk() or member.isdev() or member.isfifo():
                raise RuntimeError(
                    f"source archive contains a special or linked entry: {member.name}"
                )
            if len(path.parts) == 1:
                continue
            relative = PurePosixPath(*path.parts[1:])
            if FORBIDDEN_SDIST_PARTS.intersection(relative.parts):
                raise RuntimeError(f"source archive contains generated state: {relative}")
            if relative.name == ".env" or relative.suffix in {".db", ".pyc", ".pyo"}:
                raise RuntimeError(f"source archive contains a forbidden file: {relative}")
            if member.isfile():
                relative_paths.add(relative.as_posix())

    expected_root = f"nexus_openai-{EXPECTED_VERSION}"
    if roots != {expected_root}:
        raise RuntimeError(f"source archive root {sorted(roots)} does not match {expected_root}")
    missing = REQUIRED_SDIST_PATHS - relative_paths
    if missing:
        raise RuntimeError(f"source archive is incomplete; missing: {', '.join(sorted(missing))}")
    return expected_root, len(relative_paths)


def main() -> int:
    args = _parser().parse_args()
    wheel = _resolve_single(args.wheel, "*.whl", "wheel")
    sdist = _resolve_single(args.sdist, "*.tar.gz", "source archive")
    sdist_root, sdist_files = _verify_sdist(sdist)

    with tempfile.TemporaryDirectory(prefix="cognexus-wheel-") as temporary:
        extracted = Path(temporary).resolve()
        _extract_wheel(wheel, extracted)

        # Ensure environment-backed defaults cannot initiate provider or telemetry I/O.
        os.environ.update(
            {
                "NEXUS_ENV": "test",
                "NEXUS_MODEL_VALIDATION_MODE": "off",
                "NEXUS_COMPACTION_ENABLED": "false",
                "NEXUS_OTEL_ENABLED": "false",
                "NEXUS_SQLITE_PATH": str(extracted / "verification.db"),
            }
        )
        sys.path.insert(0, str(extracted))

        from config.settings import DEFAULT_SKILLS_ROOT
        from server.app import create_app
        from skill_runtime.loader import SkillRegistry

        imported = Path(sys.modules["server.app"].__file__ or "")
        if not _is_within(imported, extracted):
            raise RuntimeError(f"server.app was imported outside the wheel: {imported}")

        distributions = list(importlib.metadata.distributions(path=[str(extracted)]))
        matched = [item for item in distributions if item.name.lower() == EXPECTED_DISTRIBUTION]
        if len(matched) != 1:
            raise RuntimeError(
                f"expected one {EXPECTED_DISTRIBUTION} distribution, found {len(matched)}"
            )
        distribution = matched[0]
        if distribution.version != APP_VERSION or APP_VERSION != EXPECTED_VERSION:
            raise RuntimeError(
                "wheel metadata, runtime, and verifier versions do not agree: "
                f"{distribution.version}, {APP_VERSION}, {EXPECTED_VERSION}"
            )

        commands = {
            entry.name for entry in distribution.entry_points if entry.group == "console_scripts"
        }
        expected_commands = {"cognexus", "cognexus-server", "cognexus-skills"}
        if not expected_commands.issubset(commands):
            missing = ", ".join(sorted(expected_commands - commands))
            raise RuntimeError(f"wheel is missing console entry points: {missing}")

        registry = SkillRegistry(DEFAULT_SKILLS_ROOT)
        registry.refresh(force=True)
        if registry.issues():
            messages = "; ".join(issue.message for issue in registry.issues())
            raise RuntimeError(f"bundled skill validation failed: {messages}")
        skill_count = len(registry.metadata())
        if skill_count != EXPECTED_SKILLS:
            raise RuntimeError(f"expected {EXPECTED_SKILLS} bundled skills, found {skill_count}")

        application = create_app()
        payload = {
            "status": "ok",
            "wheel": wheel.name,
            "source_archive": sdist.name,
            "source_archive_root": sdist_root,
            "source_archive_files": sdist_files,
            "version": distribution.version,
            "module_origin": str(imported.relative_to(extracted)),
            "entry_points": sorted(commands),
            "skills": skill_count,
            "api_title": application.title,
        }
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
