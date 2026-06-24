"""Run deterministic repository and portable Agent Skills integrity checks."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from skill_runtime.loader import SkillRegistry  # noqa: E402

CANONICAL = PROJECT_ROOT / ".agents" / "skills"
BUNDLED = PROJECT_ROOT / "skill_runtime" / "bundled_skills"
CATALOG = PROJECT_ROOT / "skills" / "catalog.yaml"
_REASONING_TRACE_REQUEST = re.compile(
    r"(?:\b(?:show|reveal|print)\b[^\n]{0,80}"
    r"\b(?:chain-of-thought|hidden reasoning|internal reasoning)\b)"
    r"|(?:\bprovide\s+(?:the\s+)?(?:full\s+)?chain-of-thought\b)",
    re.IGNORECASE,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative_files(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and not path.is_symlink()
        and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".pyo"}
    }


def _load_catalog() -> dict[str, Any]:
    parsed = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("skills/catalog.yaml must contain a mapping")
    return parsed


def validate() -> list[str]:
    errors: list[str] = []
    registry = SkillRegistry(CANONICAL)
    registry.refresh(force=True)
    errors.extend(
        f"{issue.code}: {issue.path}: {issue.message}"
        for issue in registry.issues()
        if issue.severity == "error"
    )

    metadata = {item.name: item for item in registry.metadata()}
    try:
        catalog = _load_catalog()
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [f"catalog_invalid: {exc}"]

    entries = catalog.get("skills")
    if not isinstance(entries, list):
        errors.append("catalog_invalid: skills must be a list")
        entries = []
    if catalog.get("skill_count") != len(entries):
        errors.append("catalog_count_mismatch: skill_count does not match entries")
    if len(entries) != len(metadata):
        errors.append(f"registry_catalog_mismatch: registry={len(metadata)} catalog={len(entries)}")

    catalog_names: set[str] = set()
    for raw in entries:
        if not isinstance(raw, dict):
            errors.append("catalog_invalid: every skill entry must be a mapping")
            continue
        name = str(raw.get("name", ""))
        if name in catalog_names:
            errors.append(f"catalog_duplicate: {name}")
        catalog_names.add(name)
        item = metadata.get(name)
        if item is None:
            errors.append(f"catalog_unknown_skill: {name}")
            continue
        expected_path = PROJECT_ROOT / str(raw.get("path", ""))
        if expected_path.resolve() != item.location.resolve():
            errors.append(f"catalog_path_mismatch: {name}")
        if str(raw.get("description", "")) != item.description:
            errors.append(f"catalog_description_mismatch: {name}")
        if str(raw.get("sha256", "")) != _sha256(item.location):
            errors.append(f"catalog_hash_mismatch: {name}")
        if len(item.location.read_text(encoding="utf-8").splitlines()) > 500:
            errors.append(f"progressive_disclosure_violation: {name} exceeds 500 lines")
        skill_text = item.location.read_text(encoding="utf-8")
        if _REASONING_TRACE_REQUEST.search(skill_text):
            errors.append(f"reasoning_trace_request: {name}")

    if CANONICAL.is_dir() and BUNDLED.is_dir():
        if _relative_files(CANONICAL) != _relative_files(BUNDLED):
            errors.append("bundled_skills_stale: run scripts/sync_skill_pack.py")
    else:
        errors.append("skill_pack_missing: canonical or bundled skill tree is absent")

    return errors


def main() -> None:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        raise SystemExit(1)
    count = len(SkillRegistry(CANONICAL).metadata())
    print(f"Repository integrity valid: {count} portable skills, catalog and bundle synchronized.")


if __name__ == "__main__":
    main()
