#!/usr/bin/env python3
"""Verify the exact runtime constraint set and its optional CycloneDX SBOM."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
DEFAULT_REQUIREMENTS: Final = PROJECT_ROOT / "requirements.txt"
DEFAULT_LOCK: Final = PROJECT_ROOT / "constraints" / "runtime.txt"


@dataclass(frozen=True, slots=True)
class RuntimeLockSummary:
    """Machine-readable verification result."""

    direct_requirements: int
    locked_components: int
    sbom_components: int | None


def _requirement_lines(path: Path) -> list[Requirement]:
    """Parse PEP 508 requirement lines from a repository-owned text file."""
    requirements: list[Requirement] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        value = raw.split("#", 1)[0].strip()
        if not value:
            continue
        if value.startswith(("-r ", "--requirement ", "-c ", "--constraint ")):
            raise ValueError(f"{path}:{line_number}: nested requirement files are not allowed")
        try:
            requirements.append(Requirement(value))
        except InvalidRequirement as exc:
            raise ValueError(f"{path}:{line_number}: invalid requirement: {value}") from exc
    return requirements


def _exact_lock(path: Path) -> dict[str, tuple[str, str, bool]]:
    """Return canonical name -> (display name, exact version, active marker) for a strict lock."""
    locked: dict[str, tuple[str, str, bool]] = {}
    for requirement in _requirement_lines(path):
        if requirement.url or requirement.extras:
            raise ValueError(
                f"runtime lock entry must be an exact registry pin without extras: {requirement}"
            )
        specifiers = list(requirement.specifier)
        if len(specifiers) != 1 or specifiers[0].operator != "==" or "*" in specifiers[0].version:
            raise ValueError(f"runtime lock entry must use one exact == pin: {requirement}")
        key = canonicalize_name(requirement.name)
        if key in locked:
            raise ValueError(f"duplicate runtime lock entry: {requirement.name}")
        version = str(Version(specifiers[0].version))
        marker_active = requirement.marker is None or requirement.marker.evaluate()
        locked[key] = (requirement.name, version, marker_active)
    if not locked:
        raise ValueError("runtime lock cannot be empty")
    return locked


def _sbom_components(path: Path) -> dict[str, tuple[str, str]]:
    """Read a CycloneDX component map and reject malformed or duplicate entries."""
    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("SBOM root must be an object")
    if payload.get("bomFormat") != "CycloneDX" or payload.get("specVersion") != "1.6":
        raise ValueError("runtime SBOM must be CycloneDX 1.6")
    raw_components = payload.get("components")
    if not isinstance(raw_components, list):
        raise ValueError("runtime SBOM components must be a list")

    components: dict[str, tuple[str, str]] = {}
    for item in raw_components:
        if not isinstance(item, dict):
            raise ValueError("runtime SBOM component must be an object")
        name = item.get("name")
        version = item.get("version")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("runtime SBOM component name must be non-empty")
        if not isinstance(version, str) or not version.strip():
            raise ValueError(f"runtime SBOM component {name} has no version")
        key = canonicalize_name(name)
        if key in components:
            raise ValueError(f"duplicate runtime SBOM component: {name}")
        components[key] = (name, str(Version(version)))
    return components


def verify_runtime_lock(
    requirements_path: Path = DEFAULT_REQUIREMENTS,
    lock_path: Path = DEFAULT_LOCK,
    *,
    sbom_path: Path | None = None,
) -> RuntimeLockSummary:
    """Verify direct compatibility ranges, exact pins, and optional SBOM parity."""
    direct = _requirement_lines(requirements_path)
    locked = _exact_lock(lock_path)

    for requirement in direct:
        key = canonicalize_name(requirement.name)
        locked_item = locked.get(key)
        if locked_item is None:
            raise ValueError(f"runtime lock is missing direct dependency: {requirement.name}")
        locked_version = Version(locked_item[1])
        if requirement.marker is not None and not requirement.marker.evaluate():
            continue
        if requirement.specifier and locked_version not in requirement.specifier:
            raise ValueError(
                f"runtime lock pin {locked_item[0]}=={locked_version} does not satisfy {requirement}"
            )

    sbom_count: int | None = None
    if sbom_path is not None:
        components = _sbom_components(sbom_path)
        active_locked = {key: value for key, value in locked.items() if value[2]}
        missing = sorted(set(active_locked) - set(components))
        unexpected = sorted(set(components) - set(active_locked))
        mismatched = sorted(
            key
            for key in set(active_locked) & set(components)
            if active_locked[key][1] != components[key][1]
        )
        if missing or unexpected or mismatched:
            details: list[str] = []
            if missing:
                details.append(f"missing={','.join(missing)}")
            if unexpected:
                details.append(f"unexpected={','.join(unexpected)}")
            if mismatched:
                details.append(
                    "version_mismatch="
                    + ",".join(
                        f"{key}:{locked[key][1]}!={components[key][1]}" for key in mismatched
                    )
                )
            raise ValueError("runtime SBOM does not match runtime lock: " + "; ".join(details))
        sbom_count = len(components)

    return RuntimeLockSummary(
        direct_requirements=len(direct),
        locked_components=len(locked),
        sbom_components=sbom_count,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requirements", type=Path, default=DEFAULT_REQUIREMENTS)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--sbom", type=Path)
    parser.add_argument(
        "--require-sbom",
        action="store_true",
        help="Fail when the selected SBOM does not exist instead of validating only the lock.",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.require_sbom and args.sbom is None:
        raise SystemExit("--require-sbom requires --sbom")
    if args.sbom is not None and not args.sbom.is_file():
        raise SystemExit(f"runtime SBOM not found: {args.sbom}")
    selected_sbom = args.sbom
    try:
        summary = verify_runtime_lock(args.requirements, args.lock, sbom_path=selected_sbom)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, sort_keys=True))
        return 1
    print(
        json.dumps(
            {
                "status": "verified",
                "direct_requirements": summary.direct_requirements,
                "locked_components": summary.locked_components,
                "sbom_components": summary.sbom_components,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
