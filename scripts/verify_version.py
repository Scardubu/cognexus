#!/usr/bin/env python3
"""Verify that release-critical version declarations agree with package metadata."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Final

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent


def _match(path: Path, pattern: str, label: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(pattern, text, flags=re.MULTILINE)
    if match is None:
        raise RuntimeError(f"could not find {label} in {path.relative_to(PROJECT_ROOT)}")
    return match.group(1).strip().strip("\"'")


def project_version() -> str:
    """Return the canonical version from PEP 621 project metadata."""
    payload = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = payload.get("project", {}).get("version")
    if not isinstance(version, str) or not version:
        raise RuntimeError("pyproject.toml does not define project.version")
    return version


def declared_versions() -> dict[str, str]:
    """Collect release-critical declarations that must remain synchronized."""
    versions = {
        "pyproject.toml": project_version(),
        "config/settings.py": _match(
            PROJECT_ROOT / "config" / "settings.py",
            r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']',
            "APP_VERSION",
        ),
        "config/stack_manifest.json": str(
            json.loads((PROJECT_ROOT / "config" / "stack_manifest.json").read_text())["version"]
        ),
        "config/agent_registry.json": str(
            json.loads((PROJECT_ROOT / "config" / "agent_registry.json").read_text())["version"]
        ),
        "skills/catalog.yaml": _match(
            PROJECT_ROOT / "skills" / "catalog.yaml", r"^release:\s*([^\s#]+)", "release"
        ),
        "Dockerfile": _match(
            PROJECT_ROOT / "Dockerfile", r"^ARG APP_VERSION=([^\s]+)", "APP_VERSION argument"
        ),
        "docker-compose.yml build": _match(
            PROJECT_ROOT / "docker-compose.yml",
            r"^\s*APP_VERSION:\s*([^\s#]+)",
            "Compose APP_VERSION",
        ),
        "docker-compose.yml image": _match(
            PROJECT_ROOT / "docker-compose.yml",
            r"^\s*image:\s*nexus-openai:([^\s#]+)",
            "Compose image tag",
        ),
        "deploy/kubernetes/deployment.yaml": _match(
            PROJECT_ROOT / "deploy" / "kubernetes" / "deployment.yaml",
            r"^\s*image:\s*ghcr\.io/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+:([^\s#]+)",
            "Kubernetes image tag",
        ),
    }
    return versions


def verify_versions(expected: str | None = None) -> dict[str, str]:
    """Raise when any release declaration differs from the canonical version."""
    versions = declared_versions()
    canonical = versions["pyproject.toml"]
    mismatches = {source: value for source, value in versions.items() if value != canonical}
    if mismatches:
        details = ", ".join(f"{source}={value}" for source, value in sorted(mismatches.items()))
        raise RuntimeError(f"version declarations differ from {canonical}: {details}")
    if expected is not None:
        normalized = expected.removeprefix("v")
        if normalized != canonical:
            raise RuntimeError(
                f"release tag/version {normalized} does not match source {canonical}"
            )
    return versions


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected", help="Expected release version or v-prefixed tag")
    parser.add_argument(
        "--print-version", action="store_true", help="Print only the canonical version"
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        versions = verify_versions(args.expected)
    except RuntimeError as exc:
        print(f"version verification failed: {exc}", file=sys.stderr)
        return 1
    canonical = versions["pyproject.toml"]
    if args.print_version:
        print(canonical)
    elif args.as_json:
        print(
            json.dumps({"status": "ok", "version": canonical, "declarations": versions}, indent=2)
        )
    else:
        print(f"Version declarations valid: {canonical} ({len(versions)} synchronized sources).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
