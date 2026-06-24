"""Portable Agent Skills discovery, security, and orchestration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from config.settings import PROJECT_ROOT, Settings
from orchestrator.nexus_agent import build_nexus_agent
from skill_runtime.loader import SkillLoadError, SkillRegistry
from skill_runtime.security import SkillSecurityError

SKILLS_ROOT = PROJECT_ROOT / ".agents" / "skills"


def test_canonical_skill_pack_is_valid_and_progressive() -> None:
    registry = SkillRegistry(SKILLS_ROOT)
    registry.refresh(force=True)
    assert len(registry.metadata()) == 39
    assert not [issue for issue in registry.issues() if issue.severity == "error"]
    assert all(len(item.description) <= 1024 for item in registry.metadata())
    assert all(
        len(item.location.read_text(encoding="utf-8").splitlines()) <= 500
        for item in registry.metadata()
    )


def test_activation_discloses_resources_without_loading_them() -> None:
    registry = SkillRegistry(SKILLS_ROOT)
    document = registry.activate("multi-agent-orchestration-architect")
    assert "Workflow" in document.instructions
    assert "Detailed guidance" not in document.instructions
    paths = {resource.path for resource in document.resources}
    assert "references/guidance.md" in paths
    assert "references/checklist.md" in paths
    assert "examples/usage.md" in paths
    assert len(document.fingerprint) == 64


def test_resource_reader_rejects_traversal_and_binary_files(tmp_path: Path) -> None:
    skill = tmp_path / "safe-skill"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: safe-skill\ndescription: Safe test skill.\n---\n# Safe\n",
        encoding="utf-8",
    )
    (skill / "references" / "note.md").write_text("hello", encoding="utf-8")
    (skill / "references" / "blob.bin").write_bytes(b"\x00\x01")
    registry = SkillRegistry(tmp_path)

    assert registry.read_resource("safe-skill", "references/note.md") == "hello"
    with pytest.raises(SkillSecurityError):
        registry.read_resource("safe-skill", "../secret.txt")
    with pytest.raises(SkillLoadError, match="binary"):
        registry.read_resource("safe-skill", "references/blob.bin")


def test_search_and_allow_deny_filters() -> None:
    registry = SkillRegistry(
        SKILLS_ROOT,
        allowed_names=["testing-strategy-architect", "security-hardening-auditor"],
        denied_names=["security-hardening-auditor"],
    )
    assert [item.name for item in registry.metadata()] == ["testing-strategy-architect"]
    result = registry.search("test strategy boundary failures")
    assert result and result[0].name == "testing-strategy-architect"


def test_agent_exposes_lazy_specialists_and_skill_tools(test_settings: Settings) -> None:
    agent = build_nexus_agent(test_settings)
    tools = {getattr(tool, "name", ""): tool for tool in agent.tools}
    assert {"search_skills", "activate_skill", "read_skill_resource"} <= tools.keys()
    assert getattr(tools["read_skill_resource"], "defer_loading", False) is True
    assert getattr(tools["security_hardening_agent"], "defer_loading", False) is True
    instructions = str(agent.instructions)
    assert "## 9. Portable Agent Skills loading protocol" in instructions
    assert "<available_skills>" in instructions
    assert instructions.index("<available_skills>") < instructions.index(
        "## 10. Final response contract"
    )


@pytest.mark.parametrize(
    "skill_name",
    [
        "api-contract-governance-architect",
        "edge-cache-architecture-architect",
        "release-incident-operations-architect",
    ],
)
def test_completed_v330_skills_expose_examples_and_references(skill_name: str) -> None:
    registry = SkillRegistry(SKILLS_ROOT)
    document = registry.activate(skill_name)
    resources = {resource.path for resource in document.resources}

    assert {
        "examples/usage.md",
        "references/checklist.md",
        "references/guidance.md",
        "references/playbooks.md",
    } <= resources
    assert any(path.startswith("assets/") for path in resources)
    assert any(path.startswith("scripts/") for path in resources)
    for resource in resources:
        assert registry.read_resource(skill_name, resource).strip()
