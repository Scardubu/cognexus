#!/usr/bin/env python3
"""Create deterministic SHA-256 checksums for top-level Cognexus release artifacts."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Final

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
DEFAULT_DIST: Final = PROJECT_ROOT / "dist"
DEFAULT_OUTPUT_NAME: Final = "SHA256SUMS"
DEFAULT_PATTERNS: Final = ("*.whl", "*.tar.gz", "*.spdx.json", "*.cdx.json")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def build_checksum_lines(
    dist: Path,
    *,
    patterns: tuple[str, ...] = DEFAULT_PATTERNS,
    output: Path | None = None,
) -> list[str]:
    """Return sorted checksum lines with paths relative to ``dist``."""
    root = dist.resolve()
    if not root.is_dir():
        raise RuntimeError(f"distribution directory does not exist: {root}")
    output_resolved = output.resolve() if output is not None else None
    selected: dict[str, Path] = {}
    for pattern in patterns:
        for path in root.glob(pattern):
            if not path.is_file() or path.is_symlink():
                continue
            resolved = path.resolve()
            if output_resolved is not None and resolved == output_resolved:
                continue
            relative = path.relative_to(root).as_posix()
            if "/" in relative:
                raise RuntimeError(f"top-level release artifact expected, found: {relative}")
            selected[relative] = path
    if not selected:
        raise RuntimeError(f"no release artifacts matched under {root}")
    return [f"{_sha256(selected[name])}  {name}" for name in sorted(selected)]


def write_checksums(
    dist: Path,
    output: Path,
    *,
    patterns: tuple[str, ...] = DEFAULT_PATTERNS,
) -> int:
    """Atomically write deterministic checksum entries and return their count."""
    lines = build_checksum_lines(dist, patterns=patterns, output=output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    temporary.replace(output)
    return len(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=DEFAULT_DIST)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--pattern",
        action="append",
        dest="patterns",
        help="Top-level glob to include; repeatable. Defaults to wheel, sdist, and JSON SBOMs.",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    output = args.output or args.dist / DEFAULT_OUTPUT_NAME
    patterns = tuple(args.patterns) if args.patterns else DEFAULT_PATTERNS
    try:
        count = write_checksums(args.dist, output, patterns=patterns)
    except (OSError, RuntimeError) as exc:
        print(f"checksum generation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Checksums written: {output} ({count} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
