"""Filesystem safety primitives for untrusted skill bundles."""

from __future__ import annotations

import os
import re
import stat
from pathlib import Path

RESOURCE_ROOTS = frozenset({"references", "examples", "assets", "scripts"})
TEXT_SUFFIXES = frozenset(
    {
        ".md",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".py",
        ".sh",
        ".ps1",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".css",
        ".html",
        ".sql",
        ".csv",
    }
)
_SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class SkillSecurityError(ValueError):
    """Raised when a skill path or resource violates filesystem policy."""


def validate_skill_name(name: str) -> str:
    """Normalize and validate a portable Agent Skills identifier."""
    normalized = name.strip()
    if not _SKILL_NAME.fullmatch(normalized) or len(normalized) > 64:
        raise SkillSecurityError(
            "skill name must be lowercase kebab-case and at most 64 characters"
        )
    return normalized


def _reject_symlink_components(root: Path, candidate: Path) -> None:
    """Reject every symlink component between ``root`` and ``candidate``."""
    absolute_root = root.absolute()
    absolute_candidate = candidate.absolute()
    try:
        relative = absolute_candidate.relative_to(absolute_root)
    except ValueError as exc:
        raise SkillSecurityError("path escapes the configured skills root") from exc

    current = absolute_root
    if current.is_symlink():
        raise SkillSecurityError("configured skills root cannot be a symlink")
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise SkillSecurityError("symlinked path components are not permitted")


def ensure_within(root: Path, candidate: Path) -> Path:
    """Resolve ``candidate`` and require it to remain under a symlink-free ``root``."""
    _reject_symlink_components(root, candidate)
    resolved_root = root.resolve(strict=True)
    resolved_candidate = candidate.resolve(strict=True)
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise SkillSecurityError("path escapes the configured skills root") from exc
    return resolved_candidate


def safe_skill_directory(root: Path, name: str) -> Path:
    """Resolve a skill directory without permitting traversal or symlink escapes."""
    validated = validate_skill_name(name)
    candidate = root / validated
    resolved = ensure_within(root, candidate)
    if not resolved.is_dir():
        raise SkillSecurityError(f"skill directory does not exist: {validated}")
    return resolved


def safe_resource_path(skill_directory: Path, relative_path: str) -> Path:
    """Resolve a disclosed resource under an approved resource directory."""
    normalized = relative_path.strip().replace("\\", "/")
    relative = Path(normalized)
    if not normalized or relative.is_absolute() or ".." in relative.parts:
        raise SkillSecurityError("resource path must be a non-empty relative path")
    if not relative.parts or relative.parts[0] not in RESOURCE_ROOTS:
        raise SkillSecurityError(
            "resource must be under references/, examples/, assets/, or scripts/"
        )
    candidate = skill_directory / relative
    resolved = ensure_within(skill_directory, candidate)
    if not resolved.is_file():
        raise SkillSecurityError("resource is not a regular file")
    return resolved


def is_text_resource(path: Path) -> bool:
    """Return whether a resource is safe to decode and return as text."""
    return path.suffix.lower() in TEXT_SUFFIXES


def file_size(path: Path) -> int:
    """Return the regular-file size without following a replacement path."""
    stat_result = path.stat(follow_symlinks=False)
    if not stat.S_ISREG(stat_result.st_mode):
        raise SkillSecurityError("path is not a regular file")
    return int(stat_result.st_size)


def read_bounded_text(path: Path, max_bytes: int) -> str:
    """Read UTF-8 text from one regular file using a no-follow descriptor."""
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise SkillSecurityError("unable to open skill file safely") from exc

    try:
        stat_result = os.fstat(descriptor)
        if not stat.S_ISREG(stat_result.st_mode):
            raise SkillSecurityError("path is not a regular file")
        if stat_result.st_size > max_bytes:
            raise SkillSecurityError(
                f"file exceeds configured size limit ({stat_result.st_size} > {max_bytes} bytes)"
            )
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            raw = stream.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise SkillSecurityError(f"file exceeds configured size limit ({max_bytes} bytes)")
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SkillSecurityError("skill text must be valid UTF-8") from exc
    finally:
        os.close(descriptor)
