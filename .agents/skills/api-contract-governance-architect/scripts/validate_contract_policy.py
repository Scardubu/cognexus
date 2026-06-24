#!/usr/bin/env python3
"""Validate a Cognexus API contract-governance policy file."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

REQUIRED_GATES = {
    "schema_lint",
    "breaking_change_diff",
    "provider_contract_tests",
    "consumer_fixture_tests",
    "replay_and_idempotency_tests",
}


def _mapping(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path} must be a mapping")
        return {}
    return value


def validate(document: Any) -> list[str]:
    errors: list[str] = []
    root = _mapping(document, "document", errors)
    if root.get("policy_version") != 1:
        errors.append("policy_version must equal 1")
    for section in (
        "compatibility",
        "errors",
        "pagination",
        "idempotency",
        "webhooks",
        "deprecation",
    ):
        _mapping(root.get(section), section, errors)

    compatibility = _mapping(root.get("compatibility"), "compatibility", errors)
    if compatibility.get("default_strategy") != "additive":
        errors.append("compatibility.default_strategy must be additive")
    if compatibility.get("breaking_changes_require_version") is not True:
        errors.append("compatibility.breaking_changes_require_version must be true")

    error_policy = _mapping(root.get("errors"), "errors", errors)
    envelope = error_policy.get("envelope_fields")
    if not isinstance(envelope, list) or not {"code", "message", "request_id"}.issubset(envelope):
        errors.append("errors.envelope_fields must include code, message, and request_id")

    pagination = _mapping(root.get("pagination"), "pagination", errors)
    if pagination.get("mutable_collections") != "cursor":
        errors.append("pagination.mutable_collections must be cursor")
    page_size = pagination.get("max_page_size")
    if not isinstance(page_size, int) or not 1 <= page_size <= 1000:
        errors.append("pagination.max_page_size must be an integer from 1 to 1000")

    for section, required in {
        "idempotency": (
            "retryable_writes_require_key",
            "request_digest_binding",
            "concurrent_replay_test_required",
        ),
        "webhooks": (
            "timestamp_signature_required",
            "replay_store_required",
            "constant_time_verification_required",
        ),
        "deprecation": ("owner_required", "sunset_date_required", "usage_telemetry_required"),
    }.items():
        values = _mapping(root.get(section), section, errors)
        errors.extend(
            f"{section}.{key} must be true" for key in required if values.get(key) is not True
        )

    gates = root.get("gates")
    if not isinstance(gates, list):
        errors.append("gates must be a list")
    else:
        missing = REQUIRED_GATES - {str(gate) for gate in gates}
        if missing:
            errors.append(f"gates missing required entries: {', '.join(sorted(missing))}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(__file__).resolve().parent.parent / "assets" / "openapi-governance-policy.yaml"
    parser.add_argument("policy", nargs="?", type=Path, default=default)
    args = parser.parse_args()
    try:
        document = yaml.safe_load(args.policy.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"contract policy could not be read: {exc}")
        return 2
    errors = validate(document)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Contract governance policy valid: {args.policy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
