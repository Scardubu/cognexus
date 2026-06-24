"""ARCH-04 React Server Component and streaming preference validator."""

from __future__ import annotations

import re


class Arch04Validator:
    """Detect avoidable client-side data fetching recommendations."""

    _client_fetch = re.compile(
        r"(?:['\"]use client['\"].{0,500})?(?:useEffect\s*\(|axios\.|fetch\s*\()",
        re.I | re.S,
    )
    _server_pattern = re.compile(
        r"\b(?:RSC|server component|server action|Suspense|streaming)\b", re.I
    )
    _justification = re.compile(
        r"\b(?:browser-only|client-only|real-time interaction|websocket|device API)\b", re.I
    )

    def validate(self, text: str) -> dict[str, str] | None:
        """Return a violation for unjustified client fetching in Next.js recommendations."""
        if "next.js" not in text.lower() and "react" not in text.lower():
            return None
        if self._client_fetch.search(text) and not (
            self._server_pattern.search(text) or self._justification.search(text)
        ):
            return {
                "code": "ARCH-04",
                "severity": "P1",
                "description": "Client-side data fetching is recommended without an RSC/streaming assessment.",
                "rejection_prompt": "Use an async Server Component or streaming pattern unless client execution is required.",
            }
        return None
