#!/usr/bin/env python3
"""Validate release promotion, rollback, and incident policy controls."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

REQUIRED_SIGNALS = {
    "availability",
    "latency",
    "error_rate",
    "saturation",
    "critical_synthetics",
    "security_events",
}
REQUIRED_ROLES = {"incident_commander", "technical_lead", "communications_lead", "scribe"}
REQUIRED_EVIDENCE = {
    "test_report",
    "vulnerability_report",
    "sbom",
    "provenance",
    "release_manifest",
    "deployment_verification",
}


def _map(value: Any, name: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{name} must be a mapping")
        return {}
    return value


def validate(document: Any) -> list[str]:
    errors: list[str] = []
    root = _map(document, "document", errors)
    if root.get("policy_version") != 1:
        errors.append("policy_version must equal 1")

    release = _map(root.get("release"), "release", errors)
    errors.extend(
        f"release.{field} must be true"
        for field in (
            "immutable_artifact_digest_required",
            "dependency_audit_required",
            "sbom_required",
            "provenance_required",
            "rollback_rehearsal_required",
        )
        if release.get(field) is not True
    )

    promotion = _map(root.get("promotion"), "promotion", errors)
    stages = promotion.get("stages_percent")
    if (
        not isinstance(stages, list)
        or not stages
        or stages[-1] != 100
        or stages != sorted(set(stages))
    ):
        errors.append("promotion.stages_percent must be unique, increasing, and end at 100")
    dwell = promotion.get("minimum_dwell_minutes")
    if not isinstance(dwell, int) or dwell < 1:
        errors.append("promotion.minimum_dwell_minutes must be a positive integer")
    signals = promotion.get("required_signals")
    missing_signals = REQUIRED_SIGNALS - (
        {str(item) for item in signals} if isinstance(signals, list) else set()
    )
    if missing_signals:
        errors.append(f"promotion.required_signals missing: {', '.join(sorted(missing_signals))}")
    if promotion.get("automatic_abort_on_gate_failure") is not True:
        errors.append("promotion.automatic_abort_on_gate_failure must be true")

    rollback = _map(root.get("rollback"), "rollback", errors)
    errors.extend(
        f"rollback.{field} must be true"
        for field in (
            "previous_artifact_required",
            "compatibility_window_required",
            "queue_and_inflight_drain_required",
        )
        if rollback.get(field) is not True
    )

    incident = _map(root.get("incident"), "incident", errors)
    roles = incident.get("roles")
    missing_roles = REQUIRED_ROLES - (
        {str(item) for item in roles} if isinstance(roles, list) else set()
    )
    if missing_roles:
        errors.append(f"incident.roles missing: {', '.join(sorted(missing_roles))}")
    for field in ("sev1_ack_minutes", "sev1_update_minutes"):
        value = incident.get(field)
        if not isinstance(value, int) or value < 1:
            errors.append(f"incident.{field} must be a positive integer")
    if incident.get("pii_and_secrets_forbidden") is not True:
        errors.append("incident.pii_and_secrets_forbidden must be true")

    evidence = _map(root.get("evidence"), "evidence", errors)
    required = evidence.get("required")
    missing_evidence = REQUIRED_EVIDENCE - (
        {str(item) for item in required} if isinstance(required, list) else set()
    )
    if missing_evidence:
        errors.append(f"evidence.required missing: {', '.join(sorted(missing_evidence))}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(__file__).resolve().parent.parent / "assets" / "release-verification-policy.yaml"
    parser.add_argument("policy", nargs="?", type=Path, default=default)
    args = parser.parse_args()
    try:
        document = yaml.safe_load(args.policy.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"release policy could not be read: {exc}")
        return 2
    errors = validate(document)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Release and incident policy valid: {args.policy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
