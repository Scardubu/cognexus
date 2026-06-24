#!/usr/bin/env python3
"""Validate edge-cache policy safety and operational completeness."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

REQUIRED_CLASSES = {
    "public_immutable",
    "public_revalidatable",
    "private_user_scoped",
    "sensitive",
    "mutation",
}
REQUIRED_METRICS = {
    "hit_ratio",
    "origin_latency",
    "origin_error_rate",
    "purge_latency",
    "stale_serves",
    "evictions",
}
REQUIRED_GATES = {
    "cross_tenant_collision_test",
    "cache_poisoning_test",
    "authorization_bypass_test",
    "origin_failure_test",
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
    classes = _map(root.get("classifications"), "classifications", errors)
    missing_classes = REQUIRED_CLASSES - set(classes)
    if missing_classes:
        errors.append(f"classifications missing: {', '.join(sorted(missing_classes))}")
    for name in ("private_user_scoped", "sensitive", "mutation"):
        value = _map(classes.get(name), f"classifications.{name}", errors).get("cache_control", "")
        if "no-store" not in str(value):
            errors.append(f"classifications.{name}.cache_control must include no-store")

    key = _map(root.get("cache_key"), "cache_key", errors)
    errors.extend(
        f"cache_key.{field} must be true"
        for field in (
            "canonical_path",
            "normalized_query",
            "tenant_boundary_required",
            "unbounded_headers_forbidden",
        )
        if key.get(field) is not True
    )

    invalidation = _map(root.get("invalidation"), "invalidation", errors)
    errors.extend(
        f"invalidation.{field} must be true"
        for field in (
            "versioned_namespace",
            "update_delete_permission_paths_tested",
            "global_purge_not_only_rollback",
        )
        if invalidation.get(field) is not True
    )

    protection = _map(root.get("origin_protection"), "origin_protection", errors)
    limit = protection.get("per_key_concurrency_limit")
    if (
        protection.get("request_coalescing") is not True
        or protection.get("stale_if_error") is not True
    ):
        errors.append("origin protection must enable request_coalescing and stale_if_error")
    if not isinstance(limit, int) or not 1 <= limit <= 1000:
        errors.append("origin_protection.per_key_concurrency_limit must be from 1 to 1000")

    observability = _map(root.get("observability"), "observability", errors)
    metrics = observability.get("required_metrics")
    missing_metrics = REQUIRED_METRICS - (
        {str(item) for item in metrics} if isinstance(metrics, list) else set()
    )
    if missing_metrics:
        errors.append(
            f"observability.required_metrics missing: {', '.join(sorted(missing_metrics))}"
        )

    gates = _map(root.get("gates"), "gates", errors)
    errors.extend(
        f"gates.{gate} must be true" for gate in REQUIRED_GATES if gates.get(gate) is not True
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(__file__).resolve().parent.parent / "assets" / "cache-policy.yaml"
    parser.add_argument("policy", nargs="?", type=Path, default=default)
    args = parser.parse_args()
    try:
        document = yaml.safe_load(args.policy.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"cache policy could not be read: {exc}")
        return 2
    errors = validate(document)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Edge-cache policy valid: {args.policy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
