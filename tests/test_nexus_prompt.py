"""Regression tests for the canonical NEXUS orchestration contract."""

from __future__ import annotations

from middleware.trace_block_validator import TraceBlockValidator
from orchestrator.nexus_agent import _agent_cache_key
from orchestrator.nexus_prompt import (
    NEXUS_RESPONSE_CONTRACT,
    NEXUS_SYSTEM_PROMPT,
    NEXUS_TRACE_TEMPLATE,
    PORTABLE_SKILL_LOADING_PROTOCOL,
    build_nexus_system_prompt,
)


def test_prompt_contains_complete_progressive_skill_protocol() -> None:
    prompt = NEXUS_SYSTEM_PROMPT
    search_index = prompt.index("call `search_skills`")
    activate_index = prompt.index("Call `activate_skill`")
    resource_index = prompt.index("Call `read_skill_resource`")

    assert search_index < activate_index < resource_index
    normalized = " ".join(prompt.split())
    assert "a skill is not active until `activate_skill` succeeds" in normalized
    assert "Do not load all references, examples, assets, or scripts by default" in normalized
    assert "Resource paths must come from the activated skill inventory" in normalized
    assert "Reading a script never authorizes or executes it" in normalized
    assert "searched-but-unused skills" in normalized


def test_builder_injects_catalog_before_the_response_contract() -> None:
    catalog = "<available_skills>\x00<skill>example</skill></available_skills>"
    prompt = build_nexus_system_prompt(catalog)

    assert "\x00" not in prompt
    assert "<skill>example</skill>" in prompt
    assert prompt.index(PORTABLE_SKILL_LOADING_PROTOCOL) < prompt.index("<skill>example</skill>")
    assert prompt.index("<skill>example</skill>") < prompt.index(NEXUS_RESPONSE_CONTRACT)
    assert prompt.endswith(NEXUS_RESPONSE_CONTRACT)


def test_builder_omits_empty_catalog_section() -> None:
    assert build_nexus_system_prompt() == NEXUS_SYSTEM_PROMPT
    assert build_nexus_system_prompt("  \x00  ") == NEXUS_SYSTEM_PROMPT
    assert "## Installed portable-skill catalog" not in NEXUS_SYSTEM_PROMPT


def test_trace_template_remains_compatible_with_runtime_validator() -> None:
    response = (
        NEXUS_TRACE_TEMPLATE.replace("<brief intent, maximum 150 characters>", "Audit prompt")
        .replace("<1-8>", "5")
        .replace("<exact tier name>", "AI Engineering")
        .replace("<TaxBridge|SabiScore|Hashablanca|SwarmX|None>", "None")
        .replace(
            "<activated skills and tools in execution order, maximum 5>",
            "agent-prompt-upgrade → prompt_engineering_agent",
        )
        .replace("<NONE or concise resolution>", "NONE")
        .replace("<NONE or comma-separated ARCH codes>", "NONE")
        .replace("<NONE or comma-separated OBS codes>", "NONE")
        + "\nImplementation-ready response."
    )

    result = TraceBlockValidator().validate(response)
    assert result["valid"] is True
    assert result["fields"]["skills"] == [
        "agent-prompt-upgrade",
        "prompt_engineering_agent",
    ]


def test_agent_cache_key_changes_when_catalog_changes(test_settings) -> None:  # type: ignore[no-untyped-def]
    first = _agent_cache_key(test_settings, skill_catalog_fingerprint="a" * 64)
    second = _agent_cache_key(test_settings, skill_catalog_fingerprint="b" * 64)

    assert first != second
