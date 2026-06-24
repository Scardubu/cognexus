#!/usr/bin/env python3
"""Run ``python -m build`` with writable temp directories on Windows."""

from __future__ import annotations

import os
import secrets
import sys
import tempfile
from pathlib import Path
from typing import Any, Final, cast

import build.__main__

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
TEMP_ROOT: Final = PROJECT_ROOT / "artifacts" / "tmp"
SITECUSTOMIZE_ROOT: Final = PROJECT_ROOT / "artifacts" / "build-sitecustomize"

SITECUSTOMIZE_SOURCE: Final = """
from pathlib import Path
import os
import secrets
import tempfile

_TEMP_ROOT = Path(os.environ.get("NEXUS_BUILD_TEMP_ROOT", tempfile.gettempdir()))


def _writable_mkdtemp(suffix=None, prefix=None, dir=None):
    if isinstance(dir, bytes):
        root = Path(dir.decode())
    else:
        root = Path(dir) if dir is not None else _TEMP_ROOT
    root.mkdir(parents=True, exist_ok=True)
    name_prefix = prefix or "tmp"
    name_suffix = suffix or ""
    for _ in range(100):
        path = root / f"{name_prefix}{secrets.token_hex(8)}{name_suffix}"
        try:
            path.mkdir()
        except FileExistsError:
            continue
        return str(path)
    raise FileExistsError("could not create a unique temporary build directory")


tempfile.tempdir = str(_TEMP_ROOT)
tempfile.mkdtemp = _writable_mkdtemp
"""


def _writable_mkdtemp(
    suffix: str | None = None,
    prefix: str | None = None,
    dir: str | bytes | None = None,
) -> str:
    """Create temp directories with inherited writable ACLs for build hooks."""
    if isinstance(dir, bytes):
        root = Path(dir.decode())
    else:
        root = Path(dir) if dir is not None else TEMP_ROOT
    root.mkdir(parents=True, exist_ok=True)
    name_prefix = prefix or "tmp"
    name_suffix = suffix or ""
    for _ in range(100):
        path = root / f"{name_prefix}{secrets.token_hex(8)}{name_suffix}"
        try:
            path.mkdir()
        except FileExistsError:
            continue
        return str(path)
    raise FileExistsError("could not create a unique temporary build directory")


def main() -> int:
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    SITECUSTOMIZE_ROOT.mkdir(parents=True, exist_ok=True)
    (SITECUSTOMIZE_ROOT / "sitecustomize.py").write_text(
        SITECUSTOMIZE_SOURCE,
        encoding="utf-8",
    )
    python_path = os.environ.get("PYTHONPATH")
    os.environ["PYTHONPATH"] = (
        str(SITECUSTOMIZE_ROOT)
        if not python_path
        else f"{SITECUSTOMIZE_ROOT}{os.pathsep}{python_path}"
    )
    os.environ["NEXUS_BUILD_TEMP_ROOT"] = str(TEMP_ROOT)
    tempfile.tempdir = str(TEMP_ROOT)
    cast("Any", tempfile).mkdtemp = _writable_mkdtemp
    build.__main__.main(sys.argv[1:], prog="python scripts/build_distribution.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
