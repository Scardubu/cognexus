"""Execution-mode, recommendation, session intelligence, and production-gate tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import cast

from fastapi.testclient import TestClient

from config.settings import PROJECT_ROOT, Settings
from observability.privacy import redact_observability_fields, safe_span_attributes
from orchestrator.conflict_resolver import Candidate, resolve_conflicts
from orchestrator.execution_modes import (
    EXECUTION_MODES,
    ExecutionMode,
    get_execution_mode_profile,
    specialist_names_for_mode,
)
from orchestrator.response_metadata import derive_response_metadata
from orchestrator.skill_recommender import recommend_skills
from orchestrator.tier_classifier import classify_task
from scripts.generate_sbom import generate as generate_sbom
from scripts.verify_deployment import validate_static
from server.app import create_app
from sessions.intelligence import analyze_session_items
from skill_runtime.loader import SkillRegistry


def _api_settings(tmp_path: Path) -> Settings:
    return Settings(
        nexus_env="test",
        nexus_model_validation_mode="off",
        nexus_session_backend="sqlite",
        nexus_sqlite_path=tmp_path / "intelligence-api.db",
        nexus_compaction_enabled=False,
        nexus_otel_enabled=False,
        nexus_enable_docs=False,
        nexus_trusted_hosts=["testserver"],
    )


def test_execution_modes_have_distinct_bounded_policies() -> None:
    assert EXECUTION_MODES == (
        "focus",
        "review",
        "research",
        "architect",
        "brainstorm",
        "incident",
    )
    profiles = [get_execution_mode_profile(cast(ExecutionMode, mode)) for mode in EXECUTION_MODES]
    assert len({profile.objective for profile in profiles}) == len(EXECUTION_MODES)
    assert all(1 <= profile.specialist_budget <= 4 for profile in profiles)
    assert specialist_names_for_mode("focus", primary_tier=4) != specialist_names_for_mode(
        "incident", primary_tier=4, supporting_tiers=(1, 6)
    )


def test_classifier_detects_hybrid_intent_and_honors_expert_override() -> None:
    hybrid = classify_task(
        "Architect a secure API rollout with tracing, load tests, and incident rollback."
    )
    assert hybrid.supporting_tiers
    assert len(hybrid.hybrid_intents) >= 2
    assert hybrid.matched_terms
    assert 0.0 <= hybrid.confidence <= 1.0

    overridden = classify_task("Review API security.", expert_override=6)
    assert overridden.tier == 6
    assert overridden.expert_override_applied is True
    assert overridden.ambiguity_reason


def test_conflict_resolution_weights_evidence_and_deduplicates() -> None:
    result = resolve_conflicts(
        [
            Candidate(
                source="operations",
                tier=6,
                confidence=0.9,
                source_quality=0.9,
                output={"recommendations": ["Add rollback gate"], "caveats": ["Test first"]},
            ),
            Candidate(
                source="security",
                tier=1,
                confidence=0.8,
                source_quality=1.0,
                output={
                    "recommendations": ["add rollback gate", "Fail closed"],
                    "caveats": ["test first"],
                },
            ),
        ]
    )
    assert result["sources"][0] == "security"
    assert result["recommendations"] == ["add rollback gate", "Fail closed"]
    assert result["caveats"] == ["test first"]
    assert result["resolution_metadata"]["duplicate_recommendations_removed"] == 1
    assert result["conflict_summary"] == "RESOLVED_BY_WEIGHTED_EVIDENCE"


def test_skill_recommendations_are_mode_aware_and_explainable() -> None:
    registry = SkillRegistry(PROJECT_ROOT / ".agents" / "skills")
    classification = classify_task("Review API compatibility and security before release")
    recommendations = recommend_skills(
        "Review API compatibility and security before release",
        execution_mode="review",
        classification=classification,
        registry=registry,
    )
    assert recommendations
    assert len(recommendations) <= get_execution_mode_profile("review").recommendation_limit
    assert all(item.rationale and 0.0 <= item.confidence <= 1.0 for item in recommendations)
    names = {item.name for item in recommendations}
    assert names & {
        "api-contract-governance-architect",
        "security-hardening-auditor",
        "release-incident-operations-architect",
    }


def test_response_metadata_extracts_sections_and_confidence() -> None:
    classification = classify_task("Review the deployment architecture")
    metadata = derive_response_metadata(
        """# Findings\nSafe baseline.\n\n## Assumptions\n- Redis is available.\n\n## Open Questions\n- Is multi-region required?\n\n## Next Actions\n1. Run the load gate.\n2. Verify rollback.\n""",
        classification=classification,
        execution_mode="review",
        recommendations=[],
        validated=True,
    )
    assert metadata.assumptions == ["Redis is available."]
    assert metadata.open_questions == ["Is multi-region required?"]
    assert metadata.next_actions == ["Run the load gate.", "Verify rollback."]
    assert metadata.confidence >= classification.confidence


def test_session_intelligence_redacts_secrets_and_scores_continuity() -> None:
    intelligence = analyze_session_items(
        [
            {"role": "user", "content": "Use api_key=super-secret-value for deployment"},
            {"role": "assistant", "content": "I will preserve the architecture contract."},
            {"role": "user", "content": "Now add tests and rollback."},
            {"role": "assistant", "content": "Validation and rollback gates added."},
        ],
        candidate_items=4,
        summary_max_chars=500,
    )
    assert "super-secret-value" not in intelligence.rolling_summary
    assert "[REDACTED]" in intelligence.rolling_summary
    assert intelligence.continuity_score > 0.5
    assert intelligence.compaction_recommended is True
    assert intelligence.role_counts == {"assistant": 2, "user": 2}


def test_observability_redacts_raw_session_identifiers() -> None:
    raw = "customer-sensitive-session"
    event = redact_observability_fields(None, "info", {"event": "run", "session_id": raw})
    assert "session_id" not in event
    assert event["session_ref"].startswith("session-ref-")
    assert raw not in str(event)

    attributes = safe_span_attributes({"nexus.session_id": raw, "nexus.tier": 4, "object": []})
    assert "nexus.session_id" not in attributes
    assert attributes["nexus.session_ref"].startswith("session-ref-")
    assert attributes["nexus.tier"] == 4
    assert "object" not in attributes


def test_http_execution_mode_and_recommendation_contracts(tmp_path: Path) -> None:
    app = create_app(_api_settings(tmp_path))
    with TestClient(app) as client:
        run = client.post(
            "/v1/run",
            json={
                "message": "Review the API contract and release safety",
                "dry_run": True,
                "execution_mode": "review",
                "expert_tier_override": 2,
            },
        )
        recommendations = client.post(
            "/v1/skills/recommend",
            json={
                "message": "Review the API contract and release safety",
                "execution_mode": "review",
            },
        )
        invalid = client.post(
            "/v1/run",
            json={"message": "test", "dry_run": True, "execution_mode": "unsupported"},
        )
    assert run.status_code == 200
    body = run.json()
    assert body["execution_mode"] == "review"
    assert body["tier"] == 2
    assert body["classification_confidence"] >= 0.0
    assert isinstance(body["recommended_skills"], list)
    assert "session_intelligence" in body
    assert recommendations.status_code == 200
    assert recommendations.json()["execution_mode"] == "review"
    assert recommendations.json()["recommended_skills"]
    assert invalid.status_code == 422


def test_static_deployment_verification_proves_required_controls() -> None:
    evidence = validate_static()
    assert "versioned container image" in evidence
    assert "startup/liveness/readiness probes" in evidence
    assert "restricted container security context" in evidence


def test_completed_skill_policy_validators_execute() -> None:
    validators = (
        PROJECT_ROOT
        / ".agents/skills/api-contract-governance-architect/scripts/validate_contract_policy.py",
        PROJECT_ROOT
        / ".agents/skills/edge-cache-architecture-architect/scripts/validate_cache_policy.py",
        PROJECT_ROOT
        / ".agents/skills/release-incident-operations-architect/scripts/validate_release_policy.py",
    )
    for validator in validators:
        completed = subprocess.run(  # noqa: S603 -- fixed repository-owned validator paths
            [sys.executable, str(validator)],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert completed.returncode == 0, completed.stderr or completed.stdout
        assert "valid" in completed.stdout.lower()


def test_runtime_sbom_is_deterministic_and_runtime_scoped() -> None:
    first = generate_sbom(PROJECT_ROOT / "requirements.txt", PROJECT_ROOT / "pyproject.toml")
    second = generate_sbom(PROJECT_ROOT / "requirements.txt", PROJECT_ROOT / "pyproject.toml")
    assert first == second
    assert first["bomFormat"] == "CycloneDX"
    assert first["specVersion"] == "1.6"
    assert first["metadata"]["component"]["version"] == "3.3.1"
    component_names = {item["name"].lower() for item in first["components"]}
    assert {"openai", "fastapi", "redis", "structlog"}.issubset(component_names)
    assert "pytest" not in component_names
    assert len(first["dependencies"]) == len(first["components"]) + 1


def test_repository_inventory_is_current() -> None:
    completed = subprocess.run(  # noqa: S603 -- fixed repository-owned script path
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts/generate_repository_inventory.py"),
            "--check",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout


def test_skill_recommendations_prioritize_direct_task_evidence() -> None:
    registry = SkillRegistry(PROJECT_ROOT / ".agents" / "skills")

    edge_message = "Design an edge caching strategy for a Next.js app"
    edge_recommendations = recommend_skills(
        edge_message,
        execution_mode="architect",
        classification=classify_task(edge_message),
        registry=registry,
    )
    edge_names = [item.name for item in edge_recommendations]
    assert edge_names[0] == "edge-cache-architecture-architect"
    assert edge_names == [
        "edge-cache-architecture-architect",
        "nextjs-performance-architect",
    ]
    assert "prisma-database-architect" not in edge_names

    portfolio_message = "Brainstorm a luxury portfolio redesign"
    portfolio_recommendations = recommend_skills(
        portfolio_message,
        execution_mode="brainstorm",
        classification=classify_task(portfolio_message),
        registry=registry,
    )
    assert portfolio_recommendations[0].name == "portfolio-conviction-engine"
    assert all(item.name != "backend-domain-model-architect" for item in portfolio_recommendations)


def test_session_intelligence_redacts_quoted_and_uri_credentials() -> None:
    intelligence = analyze_session_items(
        [
            {
                "role": "user",
                "content": (
                    '{"api_key": "quoted-super-secret", '
                    '"database": "postgresql://admin:db-password@example.test/app"}'
                ),
            }
        ],
        candidate_items=4,
    )
    assert "quoted-super-secret" not in intelligence.rolling_summary
    assert "db-password" not in intelligence.rolling_summary
    assert intelligence.rolling_summary.count("[REDACTED]") >= 2
