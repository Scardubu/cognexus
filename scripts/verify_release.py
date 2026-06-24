#!/usr/bin/env python3
"""Verify Cognexus release integrity, checksums, SBOM, and completed skill assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tarfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Final

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import APP_VERSION  # noqa: E402
from scripts.verify_runtime_lock import verify_runtime_lock  # noqa: E402

TARGET_SKILL_RESOURCES: Final = {
    "api-contract-governance-architect": {
        "assets/openapi-governance-policy.yaml",
        "scripts/validate_contract_policy.py",
        "references/playbooks.md",
    },
    "edge-cache-architecture-architect": {
        "assets/cache-policy.yaml",
        "scripts/validate_cache_policy.py",
        "references/playbooks.md",
    },
    "release-incident-operations-architect": {
        "assets/release-verification-policy.yaml",
        "assets/incident-command-template.md",
        "scripts/validate_release_policy.py",
        "references/playbooks.md",
    },
}


def _digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def _single(dist: Path, pattern: str, label: str) -> Path:
    matches = sorted(dist.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(f"expected one {label} matching {pattern}, found {len(matches)}")
    return matches[0]


def _safe_archive_names(path: Path) -> set[str]:
    names: list[str]
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            names = [item.filename for item in archive.infolist() if not item.is_dir()]
    elif tarfile.is_tarfile(path):
        with tarfile.open(path, "r:gz") as archive:
            names = [item.name for item in archive.getmembers() if item.isfile()]
    else:
        raise RuntimeError(f"unsupported release archive: {path}")
    if len(names) != len(set(names)):
        raise RuntimeError(f"archive contains duplicate paths: {path.name}")
    for raw in names:
        name = PurePosixPath(raw)
        if name.is_absolute() or ".." in name.parts:
            raise RuntimeError(f"archive contains unsafe path: {raw}")
    return set(names)


def _parse_checksums(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        parts = raw.split(maxsplit=1)
        if len(parts) != 2 or len(parts[0]) != 64:
            raise RuntimeError(f"invalid SHA256SUMS line {line_number}")
        name = parts[1].lstrip("* ")
        if Path(name).is_absolute() or ".." in Path(name).parts:
            raise RuntimeError(f"unsafe checksum path on line {line_number}")
        if name in entries:
            raise RuntimeError(f"duplicate checksum entry: {name}")
        entries[name] = parts[0].lower()
    return entries


def _verify_checksums(dist: Path, checksums: Path) -> int:
    entries = _parse_checksums(checksums)
    if not entries:
        raise RuntimeError("SHA256SUMS is empty")
    for name, expected in entries.items():
        artifact = dist / name
        if not artifact.is_file() or artifact.is_symlink():
            raise RuntimeError(f"checksummed artifact missing or unsafe: {name}")
        actual = _digest(artifact)
        if actual != expected:
            raise RuntimeError(f"checksum mismatch: {name}")
    return len(entries)


def _verify_manifest(dist: Path, manifest_path: Path) -> int:
    document: Any = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise RuntimeError("release manifest schema_version must equal 1")
    if document.get("product") != "Cognexus" or document.get("version") != APP_VERSION:
        raise RuntimeError("release manifest product/version does not match source")
    files = document.get("files")
    if not isinstance(files, list) or not files:
        raise RuntimeError("release manifest must contain files")
    seen: set[str] = set()
    for item in files:
        if not isinstance(item, dict):
            raise RuntimeError("release manifest file entry must be an object")
        name = str(item.get("path", ""))
        if not name or name in seen or Path(name).is_absolute() or ".." in Path(name).parts:
            raise RuntimeError(f"invalid or duplicate manifest path: {name!r}")
        seen.add(name)
        artifact = dist / name
        if not artifact.is_file() or artifact.is_symlink():
            raise RuntimeError(f"manifest artifact missing or unsafe: {name}")
        if _digest(artifact) != item.get("sha256") or artifact.stat().st_size != item.get(
            "size_bytes"
        ):
            raise RuntimeError(f"manifest integrity mismatch: {name}")
    return len(files)


def _verify_sbom(path: Path) -> str:
    document: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise RuntimeError("SBOM must be a JSON object")
    if document.get("bomFormat") == "CycloneDX" and isinstance(document.get("specVersion"), str):
        return "CycloneDX"
    if (
        isinstance(document.get("spdxVersion"), str)
        and document.get("SPDXID") == "SPDXRef-DOCUMENT"
    ):
        return "SPDX"
    raise RuntimeError("SBOM must be valid CycloneDX JSON or SPDX JSON")


def _verify_completed_skills(sdist: Path) -> int:
    names = _safe_archive_names(sdist)
    roots = {PurePosixPath(name).parts[0] for name in names}
    if len(roots) != 1:
        raise RuntimeError("source archive must have one root directory")
    root = next(iter(roots))
    required: set[str] = set()
    for skill, resources in TARGET_SKILL_RESOURCES.items():
        for resource in resources:
            required.add(f"{root}/.agents/skills/{skill}/{resource}")
            required.add(f"{root}/skill_runtime/bundled_skills/{skill}/{resource}")
    missing = required - names
    if missing:
        raise RuntimeError(
            f"source archive missing completed skill assets: {', '.join(sorted(missing))}"
        )
    return len(required)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=PROJECT_ROOT / "dist")
    parser.add_argument("--sbom", type=Path)
    parser.add_argument("--require-sbom", action="store_true")
    args = parser.parse_args()
    dist = args.dist.resolve()
    try:
        wheel = _single(dist, "*.whl", "wheel")
        sdist = _single(dist, "*.tar.gz", "source archive")
        _safe_archive_names(wheel)
        completed_resources = _verify_completed_skills(sdist)
        top_level_checksum_entries = _verify_checksums(dist, dist / "SHA256SUMS")
        skill_checksum_entries = _verify_checksums(dist / "skills", dist / "skills" / "SHA256SUMS")
        checksum_entries = top_level_checksum_entries + skill_checksum_entries
        manifest_entries = _verify_manifest(dist, dist / "RELEASE_MANIFEST.json")
        sbom_path = args.sbom
        if sbom_path is None:
            candidates = sorted([*dist.glob("*.spdx.json"), *dist.glob("*.cdx.json")])
            sbom_path = candidates[0] if len(candidates) == 1 else None
        sbom_format = _verify_sbom(sbom_path) if sbom_path else None
        runtime_lock_components: int | None = None
        if sbom_path is not None and sbom_format == "CycloneDX":
            runtime_lock = verify_runtime_lock(sbom_path=sbom_path)
            runtime_lock_components = runtime_lock.locked_components
        if args.require_sbom and sbom_format is None:
            raise RuntimeError(
                "exactly one --sbom or discoverable *.spdx.json/*.cdx.json is required"
            )
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"release verification failed: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "verified",
                "version": APP_VERSION,
                "wheel": wheel.name,
                "source_archive": sdist.name,
                "checksum_entries": checksum_entries,
                "top_level_checksum_entries": top_level_checksum_entries,
                "skill_checksum_entries": skill_checksum_entries,
                "manifest_entries": manifest_entries,
                "completed_skill_resources": completed_resources,
                "sbom_format": sbom_format,
                "runtime_lock_components": runtime_lock_components,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
