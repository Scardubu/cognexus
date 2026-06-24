"""Install selected Cognexus skills into a filesystem-based Agent Skills client."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from skill_runtime.loader import SkillRegistry  # noqa: E402

DEFAULT_SOURCE = PROJECT_ROOT / ".agents" / "skills"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Destination skills directory, for example .claude/skills or .agents/skills",
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--skill",
        action="append",
        dest="skills",
        default=[],
        help="Install only this skill; repeat for multiple names (default: all)",
    )
    parser.add_argument("--force", action="store_true", help="Replace existing same-name skills")
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes only")
    return parser


def _absolute_without_resolving(path: Path) -> Path:
    return path.expanduser().absolute()


def _reject_existing_symlink_components(path: Path) -> None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.exists() and current.is_symlink():
            raise SystemExit(f"symlinked target path component is not permitted: {current}")


def _replace_directory(source_dir: Path, destination: Path, target: Path) -> None:
    temporary = Path(tempfile.mkdtemp(prefix=f".{source_dir.name}.", dir=target))
    staged = temporary / source_dir.name
    backup = target / f".{source_dir.name}.backup"
    try:
        shutil.copytree(source_dir, staged, symlinks=False)
        if backup.exists():
            shutil.rmtree(backup)
        if destination.exists():
            destination.replace(backup)
        try:
            staged.replace(destination)
        except Exception:
            if backup.exists() and not destination.exists():
                backup.replace(destination)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


def main() -> None:
    args = _parser().parse_args()
    source = args.source.expanduser().resolve()
    target = _absolute_without_resolving(args.target)
    _reject_existing_symlink_components(target)

    registry = SkillRegistry(source)
    registry.refresh(force=True)
    errors = [issue for issue in registry.issues() if issue.severity == "error"]
    if errors:
        messages = "; ".join(f"{issue.code}: {issue.message}" for issue in errors)
        raise SystemExit(f"source skill pack is invalid: {messages}")

    available = {item.name: item for item in registry.metadata()}
    requested = args.skills or sorted(available)
    unknown = sorted(set(requested) - available.keys())
    if unknown:
        raise SystemExit(f"unknown skills: {', '.join(unknown)}")

    target.mkdir(parents=True, exist_ok=True)
    planned: list[tuple[Path, Path]] = []
    for name in requested:
        source_dir = available[name].directory
        destination = target / name
        if destination.exists() and not args.force:
            raise SystemExit(f"destination exists (use --force): {destination}")
        if destination.is_symlink():
            raise SystemExit(f"refusing to replace symlink: {destination}")
        planned.append((source_dir, destination))

    for source_dir, destination in planned:
        action = "WOULD INSTALL" if args.dry_run else "INSTALL"
        print(f"{action} {source_dir.name} -> {destination}")
        if not args.dry_run:
            _replace_directory(source_dir, destination, target)

    result = "Planned" if args.dry_run else "Installed"
    print(f"{result} {len(planned)} skill(s).")


if __name__ == "__main__":
    main()
