"""Synchronize the source-tree Agent Skills into the installable Python package."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE = PROJECT_ROOT / ".agents" / "skills"
DESTINATION = PROJECT_ROOT / "skill_runtime" / "bundled_skills"


def _files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }


def in_sync() -> bool:
    """Return whether canonical and wheel-bundled skill trees are byte-identical."""
    source_files = _files(SOURCE)
    destination_files = _files(DESTINATION) if DESTINATION.exists() else {}
    return source_files.keys() == destination_files.keys() and all(
        filecmp.cmp(source_files[name], destination_files[name], shallow=False)
        for name in source_files
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail instead of copying")
    args = parser.parse_args()

    if not SOURCE.is_dir():
        raise SystemExit(f"canonical skill root does not exist: {SOURCE}")
    if args.check:
        if not in_sync():
            raise SystemExit("bundled skills are stale; run scripts/sync_skill_pack.py")
        print(f"Skill bundle is synchronized ({len(_files(SOURCE))} files).")
        return

    temporary = DESTINATION.with_name(f"{DESTINATION.name}.tmp")
    if temporary.exists():
        shutil.rmtree(temporary)
    shutil.copytree(SOURCE, temporary)
    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)
    temporary.replace(DESTINATION)
    print(f"Synchronized {len(_files(SOURCE))} files into {DESTINATION}")


if __name__ == "__main__":
    main()
