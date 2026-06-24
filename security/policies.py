"""Central security policy constants and deployment checks."""

from __future__ import annotations

from typing import Final

_PLACEHOLDER_MARKERS: Final = (
    "change-me",
    "changeme",
    "example",
    "not-a-real-secret",
    "placeholder",
    "replace-me",
    "replace_with",
    "replace-with",
    "test-key",
    "your-key",
    "your_secret",
)


def looks_like_placeholder_secret(value: str) -> bool:
    """Return whether a configured secret is clearly a template or low-entropy value."""
    normalized = value.strip().lower()
    if not normalized:
        return True
    if any(marker in normalized for marker in _PLACEHOLDER_MARKERS):
        return True
    # Reject trivially repeated or very low-variety values without attempting to
    # estimate entropy from user-supplied secret material.
    return len(set(normalized)) < 8


PRODUCTION_SECURITY_CHECKLIST = (
    "OPENAI_API_KEY comes from a managed secret store and is not a placeholder.",
    "NEXUS_API_KEY or upstream identity-aware proxy protects public endpoints.",
    "CORS origins are explicit HTTPS origins; wildcard CORS is disabled.",
    "Forwarded headers are accepted only from explicitly trusted proxy addresses.",
    "Redis uses TLS/authentication, private networking, and a no-eviction policy.",
    "Distributed rate limits use shared Redis storage in replicated deployments.",
    "OpenAI trace sensitive-data capture remains disabled.",
    "Container runs as a non-root user with a read-only root filesystem where supported.",
    "Dependency and image scanning are enabled in CI/CD.",
    "Rate limits and upstream request-size limits are enforced.",
)
