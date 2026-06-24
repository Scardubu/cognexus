"""Command-line validation, discovery, and deterministic packaging for Cognexus skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Final

from config.settings import APP_VERSION, PROJECT_ROOT, get_settings
from skill_runtime.catalog import get_skill_registry
from skill_runtime.loader import SkillLoadError, SkillRegistry

_ZIP_TIMESTAMP: Final = (1980, 1, 1, 0, 0, 0)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cognexus-skills", description="Manage Cognexus Agent Skills"
    )
    parser.add_argument("--version", action="version", version=f"cognexus-skills {APP_VERSION}")
    parser.add_argument(
        "--root", type=Path, default=None, help="Override the configured skills root"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List discovered skill metadata")
    validate = subparsers.add_parser("validate", help="Validate all installed skills")
    validate.add_argument("--json", action="store_true", dest="as_json")

    search = subparsers.add_parser("search", help="Search skill metadata")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=8)

    show = subparsers.add_parser("show", help="Show an activated skill")
    show.add_argument("name")

    package = subparsers.add_parser("package", help="Build reproducible portable .skill archives")
    package.add_argument("--output", type=Path, default=PROJECT_ROOT / "dist" / "skills")
    return parser


def _registry(root: Path | None) -> SkillRegistry:
    settings = get_settings()
    if root is None:
        return get_skill_registry(settings)
    return get_skill_registry(settings.model_copy(update={"nexus_skills_path": root}))


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _write_entry(archive: zipfile.ZipFile, name: str, content: bytes, *, executable: bool) -> None:
    info = zipfile.ZipInfo(name, date_time=_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    mode = 0o755 if executable else 0o644
    info.external_attr = mode << 16
    archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def _package_skills(root: Path, output: Path) -> int:
    registry = _registry(root)
    output.mkdir(parents=True, exist_ok=True)
    archive_checksums: list[str] = []
    count = 0
    for metadata in registry.metadata():
        target = output / f"{metadata.name}.skill"
        temporary = target.with_suffix(".skill.tmp")
        files: list[tuple[str, bytes, bool]] = []
        manifest_files: dict[str, str] = {}
        for path in sorted(metadata.directory.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            relative = path.relative_to(metadata.directory).as_posix()
            arcname = f"{metadata.name}/{relative}"
            content = path.read_bytes()
            executable = bool(path.stat().st_mode & 0o111)
            files.append((arcname, content, executable))
            manifest_files[relative] = _sha256_bytes(content)

        manifest = (
            json.dumps(
                {
                    "format_version": 1,
                    "skill": metadata.name,
                    "files": manifest_files,
                },
                indent=2,
                sort_keys=True,
            ).encode("utf-8")
            + b"\n"
        )
        with zipfile.ZipFile(temporary, "w") as archive:
            for arcname, content, executable in files:
                _write_entry(archive, arcname, content, executable=executable)
            _write_entry(
                archive,
                f"{metadata.name}/MANIFEST.json",
                manifest,
                executable=False,
            )
        temporary.replace(target)
        archive_checksums.append(f"{_sha256_bytes(target.read_bytes())}  {target.name}")
        count += 1

    catalog_source = PROJECT_ROOT / "skills" / "catalog.yaml"
    if catalog_source.exists():
        shutil.copyfile(catalog_source, output / "catalog.yaml")
        archive_checksums.append(
            f"{_sha256_bytes((output / 'catalog.yaml').read_bytes())}  catalog.yaml"
        )
    (output / "SHA256SUMS").write_text(
        "\n".join(sorted(archive_checksums)) + "\n", encoding="utf-8"
    )
    return count


def main() -> None:
    """Run the skill management CLI."""
    args = _parser().parse_args()
    registry = _registry(args.root)
    try:
        if args.command == "list":
            for item in registry.metadata():
                print(f"{item.name}\t{item.category}\t{item.risk}\t{item.description}")
            return
        if args.command == "validate":
            registry.refresh(force=True)
            issues = registry.issues()
            status = registry.status()
            if args.as_json:
                print(
                    json.dumps(
                        {
                            "status": status,
                            "issues": [issue.model_dump(mode="json") for issue in issues],
                        },
                        indent=2,
                    )
                )
            else:
                print(
                    f"skills={status['skill_count']} errors={status['error_count']} "
                    f"warnings={status['warning_count']}"
                )
                for issue in issues:
                    print(f"{issue.severity.upper()} {issue.code}: {issue.path}: {issue.message}")
            raise SystemExit(1 if status["error_count"] else 0)
        if args.command == "search":
            print(
                json.dumps(
                    [
                        item.model_dump(mode="json")
                        for item in registry.search(args.query, limit=args.limit)
                    ],
                    indent=2,
                )
            )
            return
        if args.command == "show":
            document = registry.activate(args.name)
            print(document.instructions)
            if document.resources:
                print("\nResources:")
                for resource in document.resources:
                    print(f"- {resource.path} ({resource.kind}, {resource.size_bytes} bytes)")
            return
        if args.command == "package":
            root = args.root or registry.root
            count = _package_skills(root, args.output)
            print(f"Packaged {count} skills into {args.output}")
            return
    except SkillLoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
