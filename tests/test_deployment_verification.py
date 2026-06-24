"""Regression tests for static deployment verification."""

from __future__ import annotations

import pytest

from scripts.verify_deployment import _validate_compose_controls


def test_compose_redis_non_root_user_required_when_capabilities_are_dropped() -> None:
    with pytest.raises(RuntimeError, match="redis service must set an explicit non-root user"):
        _validate_compose_controls({"services": {"redis": {"cap_drop": ["ALL"]}}})


def test_compose_redis_non_root_user_accepts_hardened_service() -> None:
    evidence = _validate_compose_controls(
        {"services": {"redis": {"user": "999:999", "cap_drop": ["ALL"]}}}
    )

    assert evidence == ["compose redis non-root startup under dropped capabilities"]
