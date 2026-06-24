"""Constraint and trace validator tests."""

from validators.arch02_validator import Arch02Validator
from validators.arch04_validator import Arch04Validator
from validators.constraint_validator import ConstraintValidator


def codes(text: str) -> set[str]:
    return {item["code"] for item in ConstraintValidator().validate(text).violations}


def test_arch02_detects_unrequested_rewrite() -> None:
    assert Arch02Validator().validate("Rewrite the entire system from scratch.") is not None


def test_arch02_allows_explicit_rewrite() -> None:
    assert (
        Arch02Validator().validate("The user explicitly requested a rewrite from scratch.") is None
    )


def test_arch04_detects_client_fetching() -> None:
    assert (
        Arch04Validator().validate("In Next.js, use useEffect(() => fetch('/api/data')).")
        is not None
    )


def test_arch04_allows_server_component() -> None:
    assert (
        Arch04Validator().validate(
            "Use an async Server Component with Suspense streaming in Next.js."
        )
        is None
    )


def test_arch07() -> None:
    assert "ARCH-07" in codes('"maxTsServerMemory": 8192')


def test_arch08() -> None:
    assert "ARCH-08" in codes("Use jsonwebtoken in an Edge Runtime middleware.")


def test_arch10() -> None:
    assert "ARCH-10" in codes("TaxBridge invoice create calls prisma.invoice.create.")
