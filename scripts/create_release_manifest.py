#!/usr/bin/env python3
"""Create a deterministic integrity manifest for Cognexus release artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Final, TypedDict

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import APP_VERSION  # noqa: E402

DEFAULT_DIST: Final = PROJECT_ROOT / "dist"
DEFAULT_OUTPUT_NAME: Final = "RELEASE_MANIFEST.json"


class ManifestFile(TypedDict):
    """Integrity metadata for one release artifact."""

    path: str
    sha256: str
    size_bytes: int


class ReleaseManifest(TypedDict):
    """Deterministic release manifest payload."""

    schema_version: int
    product: str
    distribution: str
    version: str
    files: list[ManifestFile]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(dist: Path, output: Path) -> ReleaseManifest:
    """Return deterministic metadata for regular, non-symlink files under ``dist``."""
    root = dist.resolve()
    if not root.is_dir():
        raise RuntimeError(f"distribution directory does not exist: {root}")
    output_resolved = output.resolve()
    entries: list[ManifestFile] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"release artifacts cannot contain symlinks: {path}")
        if path.resolve() == output_resolved or not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        entries.append(
            {
                "path": relative,
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    if not entries:
        raise RuntimeError(f"no release artifacts found under {root}")
    return {
        "schema_version": 1,
        "product": "Cognexus",
        "distribution": "nexus-openai",
        "version": APP_VERSION,
        "files": entries,
    }


def write_manifest(dist: Path, output: Path) -> ReleaseManifest:
    """Atomically write the release manifest and return its payload."""
    payload = build_manifest(dist, output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output)
    return payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=DEFAULT_DIST)
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = _parser().parse_args()
    output = args.output or args.dist / DEFAULT_OUTPUT_NAME
    try:
        payload = write_manifest(args.dist, output)
    except RuntimeError as exc:
        print(f"release manifest failed: {exc}", file=sys.stderr)
        return 1
    print(
        f"Release manifest written: {output} ({len(payload['files'])} files, version {APP_VERSION})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
