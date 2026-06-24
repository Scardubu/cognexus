"""ARCH-02 architecture preservation validator."""

from __future__ import annotations

import re


class Arch02Validator:
    """Detect unsolicited rewrite or replacement recommendations."""

    _rewrite = re.compile(
        r"\b(?:rewrite|rebuild|replace|start over|from scratch|migrate away from)\b",
        re.I,
    )
    _permission = re.compile(
        r"\b(?:explicit(?:ly)? requested|user requested|rewrite requested)\b", re.I
    )

    def validate(self, text: str) -> dict[str, str] | None:
        """Return a violation when a rewrite is recommended without explicit authorization."""
        if self._rewrite.search(text) and not self._permission.search(text):
            return {
                "code": "ARCH-02",
                "severity": "P1",
                "description": "Response recommends an architecture rewrite without explicit authorization.",
                "rejection_prompt": "Preserve the existing architecture and propose incremental patches.",
            }
        return None
