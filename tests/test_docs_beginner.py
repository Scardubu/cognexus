"""Beginner documentation discoverability and encoding checks."""

from __future__ import annotations

from config.settings import PROJECT_ROOT

BEGINNER_DOCS = (
    "QUICKSTART.md",
    "FAQ.md",
    "TROUBLESHOOTING.md",
    "docs/USER_GUIDE.md",
    "docs/API.md",
    "docs/GLOSSARY.md",
    "docs/README.md",
)


def test_beginner_documentation_entry_points_exist_and_are_linked() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    for relative in BEGINNER_DOCS:
        path = PROJECT_ROOT / relative
        assert path.is_file(), f"missing beginner documentation: {relative}"
        assert relative in readme or relative.startswith("docs/"), (
            f"root README should link the beginner entry point {relative}"
        )


def test_beginner_documentation_avoids_common_mojibake() -> None:
    checked = [
        PROJECT_ROOT / ".env.example",
        PROJECT_ROOT / "CONTRIBUTING.md",
        *(PROJECT_ROOT / relative for relative in BEGINNER_DOCS),
    ]
    for path in checked:
        content = path.read_text(encoding="utf-8")
        assert "â" not in content, f"mojibake marker found in {path.relative_to(PROJECT_ROOT)}"
        assert "ð" not in content, f"mojibake marker found in {path.relative_to(PROJECT_ROOT)}"


def test_quickstart_keeps_first_run_offline_first() -> None:
    quickstart = (PROJECT_ROOT / "QUICKSTART.md").read_text(encoding="utf-8")

    assert "dry-run request" in quickstart.lower()
    assert "does not call OpenAI" in quickstart
    assert "python scripts/start.py --env development --host 127.0.0.1 --port 8000" in quickstart


def test_beginner_docs_avoid_machine_specific_guidance() -> None:
    checked = [
        PROJECT_ROOT / "QUICKSTART.md",
        PROJECT_ROOT / "FAQ.md",
        PROJECT_ROOT / "TROUBLESHOOTING.md",
        PROJECT_ROOT / "docs" / "README.md",
        PROJECT_ROOT / "docs" / "USER_GUIDE.md",
        PROJECT_ROOT / "docs" / "API.md",
        PROJECT_ROOT / "docs" / "GLOSSARY.md",
    ]
    forbidden = ("C:\\Users\\", "/Users/", "/home/")

    for path in checked:
        content = path.read_text(encoding="utf-8")
        assert not any(marker in content for marker in forbidden), (
            f"machine-specific path found in {path.relative_to(PROJECT_ROOT)}"
        )
        assert "10-20 minutes" not in content


def test_example_environment_is_private_by_default() -> None:
    env_example = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")

    assert "NEXUS_HOST=127.0.0.1" in env_example
    assert "Use 0.0.0.0 only when Docker" in env_example
