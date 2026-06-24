"""Tool and agent registry integrity tests."""

import json
from pathlib import Path

from nexus_agents.registry import AGENT_REGISTRY, validate_agent_registry
from tools.registry import TOOL_RECORDS, validate_tool_registry


def test_agent_registry_integrity() -> None:
    assert validate_agent_registry() == []
    assert len(AGENT_REGISTRY) == 20


def test_tool_registry_integrity() -> None:
    assert validate_tool_registry() == []
    implemented = [record for record in TOOL_RECORDS.values() if record.status == "implemented"]
    missing = [record for record in TOOL_RECORDS.values() if record.status == "missing"]
    assert len(implemented) == 14
    assert len(missing) == 2
    assert all(not record.executable for record in missing)


def test_json_registry_matches_runtime() -> None:
    data = json.loads(Path("config/agent_registry.json").read_text())
    assert data["summary"]["tools"] == 14
    assert data["summary"]["agents"] == 20
    assert len({item["openai_name"] for item in data["skills"]}) == 34
