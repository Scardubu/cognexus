#!/usr/bin/env python3
"""Generate or verify the deterministic Cognexus source repository inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Final

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT: Final = PROJECT_ROOT / "docs" / "V3_3_1_REPOSITORY_INVENTORY.md"
IGNORED_PARTS: Final = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "artifacts",
        "build",
        "dist",
        "nexus_openai.egg-info",
    }
)
IGNORED_NAMES: Final = frozenset({".coverage", ".env", "coverage.xml"})
IGNORED_PREFIXES: Final = ("nexus_openai-", "pytest-cache-files-")
IGNORED_SUFFIXES: Final = frozenset({".db", ".pyc", ".pyo"})


def _digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def _included_files(output: Path) -> list[Path]:
    resolved_output = output.resolve()
    files: list[Path] = []
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink() or path.resolve() == resolved_output:
            continue
        relative = path.relative_to(PROJECT_ROOT)
        if IGNORED_PARTS.intersection(relative.parts):
            continue
        if any(part.startswith(IGNORED_PREFIXES) for part in relative.parts):
            continue
        if (
            path.name in IGNORED_NAMES
            or path.name.startswith(".coverage")
            or path.suffix in IGNORED_SUFFIXES
        ):
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(PROJECT_ROOT).as_posix())


def _project_metadata() -> tuple[str, str, dict[str, str]]:
    document = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = document.get("project")
    if not isinstance(project, dict):
        raise RuntimeError("pyproject.toml is missing [project]")
    name = str(project.get("name", ""))
    version = str(project.get("version", ""))
    scripts = project.get("scripts", {})
    if not name or not version or not isinstance(scripts, dict):
        raise RuntimeError("pyproject project name, version, or scripts are invalid")
    return name, version, {str(key): str(value) for key, value in scripts.items()}


def render(output: Path) -> str:
    name, version, entry_points = _project_metadata()
    files = _included_files(output)
    top_levels: Counter[str] = Counter()
    extensions: Counter[str] = Counter()
    total_bytes = 0
    records: list[tuple[str, int, str]] = []
    for path in files:
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        size = path.stat().st_size
        total_bytes += size
        top_levels[relative.split("/", maxsplit=1)[0]] += 1
        extensions[path.suffix.lower() or "<none>"] += 1
        records.append((relative, size, _digest(path)))

    architecture = (
        ("config/", "validated settings, registry and stack manifests"),
        (
            "orchestrator/",
            "classification, execution modes, routing, conflicts and response assembly",
        ),
        ("nexus_agents/", "specialist construction and registry"),
        ("server/", "FastAPI application, schemas, middleware and launcher"),
        ("sessions/", "SQLite/Redis persistence, compaction and continuity intelligence"),
        ("observability/", "structured logging, metrics, tracing and privacy processors"),
        ("security/", "identifier, policy, rate-limit, sanitization and secret controls"),
        ("skill_runtime/", "portable skill loading, validation, packaging and tool exposure"),
        (".agents/skills/", "canonical portable skill definitions and operational assets"),
        ("deploy/", "OpenTelemetry and Kubernetes deployment resources"),
        ("scripts/", "quality, release, SBOM, inventory and deployment verification tooling"),
        ("tests/", "unit, integration, regression, failure and security tests"),
        (".github/workflows/", "CI, security, release, container and deployment gates"),
    )

    lines = [
        "# Cognexus v3.3.1 Repository Inventory",
        "",
        f"**Distribution:** `{name}`  ",
        f"**Version:** `{version}`  ",
        f"**Inventoried source files:** **{len(records)}**  ",
        f"**Inventoried bytes:** **{total_bytes:,}**",
        "",
        "This inventory is generated deterministically by "
        "`scripts/generate_repository_inventory.py`. Generated build, distribution, "
        "coverage, cache, database, local virtual-environment, secret environment, "
        "and evidence-artifact state is excluded. The inventory document itself is "
        "excluded to avoid a self-referential digest.",
        "",
        "## Architecture surfaces",
        "",
        "| Path | Responsibility |",
        "|---|---|",
    ]
    lines.extend(f"| `{path}` | {description} |" for path, description in architecture)
    lines.extend(
        [
            "",
            "## Console entry points",
            "",
            "| Command | Target |",
            "|---|---|",
        ]
    )
    lines.extend(
        f"| `{command}` | `{target}` |" for command, target in sorted(entry_points.items())
    )
    lines.extend(
        [
            "",
            "## Files by top-level path",
            "",
            "| Path | Files |",
            "|---|---:|",
        ]
    )
    lines.extend(f"| `{path}` | {count} |" for path, count in sorted(top_levels.items()))
    lines.extend(
        [
            "",
            "## Files by extension",
            "",
            "| Extension | Files |",
            "|---|---:|",
        ]
    )
    lines.extend(f"| `{extension}` | {count} |" for extension, count in sorted(extensions.items()))
    lines.extend(
        [
            "",
            "## Complete source file manifest",
            "",
            "| Path | Bytes | SHA-256 |",
            "|---|---:|---|",
        ]
    )
    lines.extend(f"| `{path}` | {size} | `{digest}` |" for path, size, digest in records)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        expected = render(args.output)
        if args.check:
            if not args.output.is_file() or args.output.read_text(encoding="utf-8") != expected:
                print(
                    f"repository inventory is stale: run {Path(__file__).relative_to(PROJECT_ROOT)}",
                    file=sys.stderr,
                )
                return 1
            print(json.dumps({"status": "verified", "output": str(args.output)}))
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(expected, encoding="utf-8")
    except (OSError, RuntimeError, tomllib.TOMLDecodeError) as exc:
        print(f"repository inventory generation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "generated", "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
