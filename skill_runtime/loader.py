"""Secure, cached loader implementing Agent Skills progressive disclosure."""

from __future__ import annotations

import hashlib
import html
import math
import re
import threading
import time
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Final, Literal, cast

import yaml
from pydantic import ValidationError

from skill_runtime.models import (
    SkillDocument,
    SkillIssue,
    SkillMetadata,
    SkillResource,
    SkillRisk,
    SkillSearchResult,
)
from skill_runtime.security import (
    RESOURCE_ROOTS,
    SkillSecurityError,
    ensure_within,
    file_size,
    is_text_resource,
    read_bounded_text,
    safe_resource_path,
    validate_skill_name,
)

_FRONTMATTER_BOUNDARY: Final = "---"
_ALLOWED_FIELDS: Final = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
_TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9+.#_-]*")


class SkillLoadError(RuntimeError):
    """Raised when a skill cannot be safely parsed or activated."""


class SkillRegistry:
    """Discover metadata eagerly and load instructions/resources on demand."""

    def __init__(
        self,
        root: Path,
        *,
        max_skill_bytes: int = 256_000,
        max_resource_bytes: int = 1_000_000,
        max_activation_chars: int = 40_000,
        cache_ttl_seconds: int = 60,
        allowed_names: Iterable[str] = (),
        denied_names: Iterable[str] = (),
    ) -> None:
        self.root = root.expanduser().resolve()
        self.max_skill_bytes = max_skill_bytes
        self.max_resource_bytes = max_resource_bytes
        self.max_activation_chars = max_activation_chars
        self.cache_ttl_seconds = cache_ttl_seconds
        self.allowed_names = frozenset(validate_skill_name(item) for item in allowed_names)
        self.denied_names = frozenset(validate_skill_name(item) for item in denied_names)
        self._lock = threading.RLock()
        self._loaded_at = 0.0
        self._catalog: dict[str, SkillMetadata] = {}
        self._issues: tuple[SkillIssue, ...] = ()

    def refresh(self, *, force: bool = False) -> None:
        """Refresh metadata after the TTL while retaining deterministic failures."""
        now = time.monotonic()
        with self._lock:
            if not force and self._loaded_at > 0 and now - self._loaded_at < self.cache_ttl_seconds:
                return
            catalog: dict[str, SkillMetadata] = {}
            issues: list[SkillIssue] = []
            if not self.root.exists() or not self.root.is_dir():
                issues.append(
                    SkillIssue(
                        severity="error",
                        code="skills_root_missing",
                        message="configured skills root does not exist or is not a directory",
                        path=str(self.root),
                    )
                )
            else:
                for directory in sorted(self.root.iterdir(), key=lambda item: item.name):
                    if directory.name.startswith(".") or not directory.is_dir():
                        continue
                    if directory.is_symlink():
                        issues.append(
                            SkillIssue(
                                severity="error",
                                code="skill_symlink",
                                message="symlinked skill directories are not permitted",
                                path=str(directory),
                            )
                        )
                        continue
                    try:
                        metadata, local_issues = self._read_metadata(directory)
                    except (SkillLoadError, SkillSecurityError) as exc:
                        issues.append(
                            SkillIssue(
                                severity="error",
                                code="skill_invalid",
                                message=str(exc),
                                path=str(directory),
                            )
                        )
                        continue
                    issues.extend(local_issues)
                    if not self._is_enabled(metadata.name):
                        continue
                    if metadata.name in catalog:
                        issues.append(
                            SkillIssue(
                                severity="error",
                                code="duplicate_skill",
                                message=f"duplicate skill name: {metadata.name}",
                                path=str(directory),
                            )
                        )
                        continue
                    catalog[metadata.name] = metadata
            self._catalog = catalog
            self._issues = tuple(issues)
            self._loaded_at = now

    def metadata(self) -> tuple[SkillMetadata, ...]:
        """Return enabled skill metadata in stable name order."""
        self.refresh()
        with self._lock:
            return tuple(self._catalog[name] for name in sorted(self._catalog))

    def issues(self) -> tuple[SkillIssue, ...]:
        """Return deterministic validation findings from the latest refresh."""
        self.refresh()
        with self._lock:
            return self._issues

    def get_metadata(self, name: str) -> SkillMetadata:
        """Return one discovered skill or fail with a non-ambiguous error."""
        validated = validate_skill_name(name)
        self.refresh()
        with self._lock:
            metadata = self._catalog.get(validated)
        if metadata is None:
            raise SkillLoadError(f"unknown or disabled skill: {validated}")
        return metadata

    def search(self, query: str, *, limit: int = 8) -> tuple[SkillSearchResult, ...]:
        """Rank skills with deterministic token overlap and phrase bonuses."""
        normalized = query.strip().lower()
        if not normalized:
            raise SkillLoadError("skill search query cannot be blank")
        bounded_limit = max(1, min(limit, 20))
        query_tokens = set(_TOKEN_PATTERN.findall(normalized))
        scored: list[SkillSearchResult] = []
        for item in self.metadata():
            haystack = f"{item.name.replace('-', ' ')} {item.description} {item.category}".lower()
            haystack_tokens = set(_TOKEN_PATTERN.findall(haystack))
            overlap = len(query_tokens & haystack_tokens)
            union = max(1, len(query_tokens | haystack_tokens))
            score = overlap / math.sqrt(union)
            if normalized in haystack:
                score += 2.0
            if item.name in normalized or item.name.replace("-", " ") in normalized:
                score += 4.0
            if score <= 0:
                continue
            scored.append(
                SkillSearchResult(
                    name=item.name,
                    description=item.description,
                    category=item.category,
                    risk=item.risk,
                    score=round(score, 6),
                )
            )
        scored.sort(key=lambda result: (-result.score, result.name))
        return tuple(scored[:bounded_limit])

    def activate(self, name: str) -> SkillDocument:
        """Load one skill body and disclose resources without loading them."""
        metadata = self.get_metadata(name)
        skill_path = metadata.location
        raw = self._read_bounded_text(skill_path, self.max_skill_bytes)
        _, body = self._split_frontmatter(raw, skill_path)
        instructions = body.strip()
        if not instructions:
            raise SkillLoadError(f"skill body is empty: {metadata.name}")
        if len(instructions) > self.max_activation_chars:
            raise SkillLoadError(
                f"skill body exceeds activation limit ({len(instructions)} > {self.max_activation_chars} characters)"
            )
        resources = tuple(self._list_resources(metadata.directory))
        fingerprint = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return SkillDocument(
            metadata=metadata,
            instructions=instructions,
            resources=resources,
            fingerprint=fingerprint,
        )

    def read_resource(self, name: str, relative_path: str) -> str:
        """Read one approved text resource with traversal and size protection."""
        metadata = self.get_metadata(name)
        resource = safe_resource_path(metadata.directory, relative_path)
        if not is_text_resource(resource):
            raise SkillLoadError("binary skill resources cannot be returned as model context")
        return self._read_bounded_text(resource, self.max_resource_bytes)

    def render_catalog(self, *, max_chars: int = 24_000) -> str:
        """Render only name/description discovery metadata for system instructions."""
        items = self.metadata()
        if not items:
            return ""
        header = (
            "<available_skills>\n"
            "Use activate_skill when a task matches a skill. Load references only when the active "
            "skill explicitly requires them.\n"
        )
        parts = [header]
        current_length = len(header)
        closing_length = len("</available_skills>")
        for item in items:
            entry = (
                "  <skill>\n"
                f"    <name>{html.escape(item.name)}</name>\n"
                f"    <description>{html.escape(item.description)}</description>\n"
                f"    <category>{html.escape(item.category)}</category>\n"
                f"    <risk>{html.escape(item.risk)}</risk>\n"
                "  </skill>\n"
            )
            if current_length + len(entry) + closing_length > max_chars:
                break
            parts.append(entry)
            current_length += len(entry)
        parts.append("</available_skills>")
        return "".join(parts)

    def status(self) -> dict[str, Any]:
        """Return JSON-safe readiness metadata without skill content."""
        items = self.metadata()
        issues = self.issues()
        errors = [issue for issue in issues if issue.severity == "error"]
        return {
            "ready": not errors and bool(items),
            "root": str(self.root),
            "skill_count": len(items),
            "error_count": len(errors),
            "warning_count": len(issues) - len(errors),
        }

    def _is_enabled(self, name: str) -> bool:
        if name in self.denied_names:
            return False
        return not self.allowed_names or name in self.allowed_names

    def _read_metadata(self, directory: Path) -> tuple[SkillMetadata, list[SkillIssue]]:
        validated_directory = ensure_within(self.root, directory)
        skill_path = validated_directory / "SKILL.md"
        if not skill_path.exists() or not skill_path.is_file() or skill_path.is_symlink():
            raise SkillLoadError("skill directory must contain a regular SKILL.md file")
        raw = self._read_bounded_text(skill_path, self.max_skill_bytes)
        frontmatter, body = self._split_frontmatter(raw, skill_path)
        try:
            tokens = tuple(yaml.scan(frontmatter))
            if any(
                isinstance(token, (yaml.tokens.AnchorToken, yaml.tokens.AliasToken))
                for token in tokens
            ):
                raise SkillLoadError(
                    "YAML anchors and aliases are not permitted in skill frontmatter"
                )
            parsed = yaml.safe_load(frontmatter)
        except yaml.YAMLError as exc:
            raise SkillLoadError(f"invalid YAML frontmatter: {exc}") from exc
        if not isinstance(parsed, dict):
            raise SkillLoadError("frontmatter must be a YAML mapping")
        unknown = sorted({str(key) for key in parsed} - _ALLOWED_FIELDS)
        issues: list[SkillIssue] = []
        if unknown:
            issues.append(
                SkillIssue(
                    severity="warning",
                    code="unknown_frontmatter_fields",
                    message=f"non-standard frontmatter fields: {', '.join(unknown)}",
                    path=str(skill_path),
                )
            )
        name = validate_skill_name(str(parsed.get("name", "")))
        if name != directory.name:
            raise SkillLoadError("frontmatter name must match the skill directory name")
        description = " ".join(str(parsed.get("description", "")).split())
        raw_metadata = parsed.get("metadata") or {}
        if not isinstance(raw_metadata, dict):
            raise SkillLoadError("metadata frontmatter field must be a string map")
        if len(raw_metadata) > 32:
            raise SkillLoadError("metadata frontmatter cannot contain more than 32 entries")
        metadata_map: dict[str, str] = {}
        for key, value in raw_metadata.items():
            key_text = str(key)
            value_text = str(value)
            if not key_text or len(key_text) > 128 or len(value_text) > 1024:
                raise SkillLoadError("metadata keys and values exceed bounded string limits")
            metadata_map[key_text] = value_text
        risk_value = metadata_map.get("cognexus.risk", "medium")
        if risk_value not in {"low", "medium", "high"}:
            issues.append(
                SkillIssue(
                    severity="warning",
                    code="invalid_risk_metadata",
                    message="cognexus.risk must be low, medium, or high; defaulted to medium",
                    path=str(skill_path),
                )
            )
            risk_value = "medium"
        if not body.strip():
            raise SkillLoadError("SKILL.md body cannot be empty")
        if len(raw.splitlines()) > 500:
            issues.append(
                SkillIssue(
                    severity="warning",
                    code="skill_too_long",
                    message="SKILL.md exceeds the recommended 500-line progressive-disclosure limit",
                    path=str(skill_path),
                )
            )
        try:
            metadata = SkillMetadata(
                name=name,
                description=description,
                location=skill_path.resolve(),
                directory=validated_directory,
                license=str(parsed["license"]) if parsed.get("license") is not None else None,
                compatibility=(
                    str(parsed["compatibility"])
                    if parsed.get("compatibility") is not None
                    else None
                ),
                metadata=metadata_map,
                allowed_tools=(
                    str(parsed["allowed-tools"])
                    if parsed.get("allowed-tools") is not None
                    else None
                ),
                category=metadata_map.get("cognexus.category", "uncategorized"),
                risk=cast(SkillRisk, risk_value),
            )
        except ValidationError as exc:
            raise SkillLoadError(f"frontmatter validation failed: {exc}") from exc
        return metadata, issues

    @staticmethod
    def _split_frontmatter(raw: str, path: Path) -> tuple[str, str]:
        lines = raw.splitlines()
        if not lines or lines[0].strip() != _FRONTMATTER_BOUNDARY:
            raise SkillLoadError(f"missing opening YAML frontmatter boundary: {path}")
        try:
            end_index = next(
                index
                for index, line in enumerate(lines[1:], start=1)
                if line.strip() == _FRONTMATTER_BOUNDARY
            )
        except StopIteration as exc:
            raise SkillLoadError(f"missing closing YAML frontmatter boundary: {path}") from exc
        return "\n".join(lines[1:end_index]), "\n".join(lines[end_index + 1 :])

    @staticmethod
    def _read_bounded_text(path: Path, max_bytes: int) -> str:
        try:
            return read_bounded_text(path, max_bytes)
        except SkillSecurityError as exc:
            raise SkillLoadError(str(exc)) from exc

    def _list_resources(self, skill_directory: Path) -> list[SkillResource]:
        resources: list[SkillResource] = []
        for root_name in sorted(RESOURCE_ROOTS):
            resource_root = skill_directory / root_name
            if (
                not resource_root.exists()
                or not resource_root.is_dir()
                or resource_root.is_symlink()
            ):
                continue
            for path in sorted(resource_root.rglob("*")):
                if not path.is_file() or path.is_symlink():
                    continue
                try:
                    resolved = ensure_within(skill_directory, path)
                except SkillSecurityError:
                    continue
                relative = resolved.relative_to(skill_directory).as_posix()
                kind = cast(
                    Literal["reference", "example", "asset", "script"],
                    {
                        "references": "reference",
                        "examples": "example",
                        "assets": "asset",
                        "scripts": "script",
                    }[root_name],
                )
                resources.append(
                    SkillResource(path=relative, kind=kind, size_bytes=file_size(resolved))
                )
        return resources
