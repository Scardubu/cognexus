"""Release artifact manifest tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from config.settings import APP_VERSION
from scripts.create_checksums import build_checksum_lines, write_checksums
from scripts.create_release_manifest import build_manifest, write_manifest
from scripts.verify_release import _verify_checksums, _verify_manifest


def test_release_manifest_is_sorted_deterministic_and_excludes_itself(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    (dist / "skills").mkdir(parents=True)
    (dist / "z.whl").write_bytes(b"wheel")
    (dist / "skills" / "a.skill").write_bytes(b"skill")
    output = dist / "RELEASE_MANIFEST.json"

    first = write_manifest(dist, output)
    first_bytes = output.read_bytes()
    second = write_manifest(dist, output)

    assert first == second
    assert output.read_bytes() == first_bytes
    assert first["version"] == APP_VERSION
    paths = [entry["path"] for entry in first["files"]]
    assert paths == sorted(paths)
    assert "RELEASE_MANIFEST.json" not in paths
    assert json.loads(first_bytes) == first


def test_release_manifest_rejects_empty_directory(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()

    with pytest.raises(RuntimeError, match="no release artifacts"):
        build_manifest(dist, dist / "RELEASE_MANIFEST.json")


def test_release_checksum_verification_supports_nested_artifact_sets(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    skills.mkdir()
    artifact = skills / "example.skill"
    artifact.write_bytes(b"portable skill")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    checksum_file = skills / "SHA256SUMS"
    checksum_file.write_text(f"{digest}  example.skill\n", encoding="utf-8")

    assert _verify_checksums(skills, checksum_file) == 1


def test_release_checksum_verification_rejects_tampering(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.whl"
    artifact.write_bytes(b"tampered")
    checksum_file = tmp_path / "SHA256SUMS"
    checksum_file.write_text(f"{'0' * 64}  artifact.whl\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="checksum mismatch"):
        _verify_checksums(tmp_path, checksum_file)


def test_checksum_generator_writes_relative_sorted_paths(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "z.whl").write_bytes(b"z")
    (dist / "a.tar.gz").write_bytes(b"a")
    output = dist / "SHA256SUMS"

    assert write_checksums(dist, output) == 2
    lines = output.read_text(encoding="utf-8").splitlines()
    assert [line.split(maxsplit=1)[1] for line in lines] == ["a.tar.gz", "z.whl"]
    assert all("dist/" not in line for line in lines)


def test_checksum_generator_rejects_empty_artifact_set(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()

    with pytest.raises(RuntimeError, match="no release artifacts"):
        build_checksum_lines(dist)


def test_release_manifest_verification_rejects_unlisted_artifacts(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "artifact.whl").write_bytes(b"wheel")
    manifest = dist / "RELEASE_MANIFEST.json"
    write_manifest(dist, manifest)
    (dist / "injected.txt").write_text("unexpected", encoding="utf-8")

    with pytest.raises(RuntimeError, match=r"unlisted=injected\.txt"):
        _verify_manifest(dist, manifest)


def test_release_manifest_creation_rejects_directory_symlinks(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    target = tmp_path / "target"
    dist.mkdir()
    target.mkdir()
    (dist / "artifact.whl").write_bytes(b"wheel")
    link = dist / "linked-directory"
    try:
        link.symlink_to(target, target_is_directory=True)
    except (NotImplementedError, OSError):
        pytest.skip("directory symlinks are unavailable on this platform")

    with pytest.raises(RuntimeError, match="cannot contain symlinks"):
        build_manifest(dist, dist / "RELEASE_MANIFEST.json")
