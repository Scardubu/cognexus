"""
middleware/trace_block_validator.py
=====================================
Enforces the Skill Trace Block format in every NEXUS response.

CORRECTIONS APPLIED (v2.1):
  - validate() always returns a plain dict (not ValidationReport.__dict__),
    ensuring consistent key access in nexus_agent.py.
  - Fields dataclass removed — parse result returned as plain dict.
  - 'valid' key is always present in the returned dict.
  - BLOCK_START_MARKER check uses str.startswith on stripped text.
  - Tier-name fuzzy match only runs when both tier_number and tier_name exist.
  - Cross-validation (Level 4) only runs if Level 1–3 passed.
  - Max skills warning uses > 5 (not >= 5) to allow exactly 5.
  - anomalies list distinguishes blocking errors from warnings via severity key.
"""

from __future__ import annotations

import re
from typing import Any

from config.settings import TIER_NAMES, VALID_APP_CONTEXTS

BLOCK_START = "┌─ NEXUS SKILL TRACE"
BLOCK_END = "└─"
BLOCK_STARTS = (BLOCK_START, "+-- NEXUS SKILL TRACE")
BLOCK_ENDS = (BLOCK_END, "+--")
FIELD_PREFIX = r"(?:│|\|)"

FIELD_PATTERNS: dict[str, str] = {
    "intent": rf"{FIELD_PREFIX}\s*Intent\s*:\s*(.+?)(?:\s*{FIELD_PREFIX}|\s*$)",
    "tier": rf"{FIELD_PREFIX}\s*Tier\s*:\s*([1-8])\s*[—–-]\s*(.+?)(?:\s*{FIELD_PREFIX}|\s*$)",
    "app_context": rf"{FIELD_PREFIX}\s*App Context\s*:\s*(.+?)(?:\s*{FIELD_PREFIX}|\s*$)",
    "skills": rf"{FIELD_PREFIX}\s*Skills\s*:\s*(.+?)(?:\s*{FIELD_PREFIX}|\s*$)",
    "conflicts": rf"{FIELD_PREFIX}\s*Conflicts\s*:\s*(.+?)(?:\s*{FIELD_PREFIX}|\s*$)",
    "constraints": rf"{FIELD_PREFIX}\s*Constraints\s*:\s*(.+?)(?:\s*{FIELD_PREFIX}|\s*$)",
    "obs_gaps": rf"{FIELD_PREFIX}\s*Obs\.\s*Gaps\s*:\s*(.+?)(?:\s*{FIELD_PREFIX}|\s*$)",
}


def _parse_fields(block: str) -> dict[str, Any]:
    """Extract the 7 required fields from the raw block text."""
    fields: dict[str, Any] = {
        "intent": "",
        "tier_number": 0,
        "tier_name": "",
        "app_context": "",
        "skills": [],
        "conflicts": "",
        "constraints": "",
        "obs_gaps": "",
    }

    m = re.search(FIELD_PATTERNS["intent"], block, re.MULTILINE)
    if m:
        fields["intent"] = m.group(1).strip()

    m = re.search(FIELD_PATTERNS["tier"], block, re.MULTILINE)
    if m:
        try:
            fields["tier_number"] = int(m.group(1))
            fields["tier_name"] = m.group(2).strip()
        except (ValueError, IndexError):
            pass

    m = re.search(FIELD_PATTERNS["app_context"], block, re.MULTILINE)
    if m:
        raw_app = m.group(1).strip()
        for app in VALID_APP_CONTEXTS:
            if app.lower() in raw_app.lower():
                fields["app_context"] = app
                break
        if not fields["app_context"]:
            fields["app_context"] = raw_app

    m = re.search(FIELD_PATTERNS["skills"], block, re.MULTILINE)
    if m:
        raw_skills = m.group(1).strip()
        fields["skills"] = [
            s.strip() for s in re.split(r"\s*(?:→|->|,)\s*", raw_skills) if s.strip()
        ]

    for key in ("conflicts", "constraints", "obs_gaps"):
        m = re.search(FIELD_PATTERNS[key], block, re.MULTILINE)
        if m:
            fields[key] = m.group(1).strip()

    return fields


class TraceBlockValidator:
    """
    Validates the Skill Trace Block in NEXUS responses.
    validate() always returns a dict with at minimum {"valid": bool, "anomalies": list}.
    """

    def validate(self, response_text: str) -> dict[str, Any]:
        """
        Validate the Skill Trace Block.

        Returns:
            {
              "valid": bool,
              "fields": dict | None,
              "anomalies": list[str],
              "raw_block": str,
            }
        """
        anomalies: list[str] = []
        fields: dict[str, Any] | None = None
        raw_block = ""

        # ── Level 1: Presence and position ──────────────────────────────────
        stripped = response_text.strip()
        start_marker = next(
            (candidate for candidate in BLOCK_STARTS if stripped.startswith(candidate)),
            None,
        )
        if start_marker is None:
            if any(candidate in response_text for candidate in BLOCK_STARTS):
                anomalies.append(
                    "BLOCKING: Skill Trace Block found but not at the start. "
                    "No text may precede it."
                )
            else:
                anomalies.append("BLOCKING: Skill Trace Block is entirely absent.")
            return {"valid": False, "fields": None, "anomalies": anomalies, "raw_block": ""}

        # ── Extract raw block ────────────────────────────────────────────────
        start_idx = response_text.find(start_marker)
        end_candidates = [
            (response_text.find(candidate, start_idx + len(start_marker)), candidate)
            for candidate in BLOCK_ENDS
        ]
        end_idx, end_marker = min(
            ((index, candidate) for index, candidate in end_candidates if index != -1),
            default=(-1, ""),
            key=lambda item: item[0],
        )
        if end_idx != -1:
            raw_block = response_text[start_idx : end_idx + 80]
        else:
            raw_block = "\n".join(response_text[start_idx:].split("\n")[:12])
            anomalies.append("WARNING: Skill Trace Block closing line not found.")

        # ── Level 2: Field parsing and validation ────────────────────────────
        fields = _parse_fields(raw_block)

        if not fields["intent"]:
            anomalies.append("BLOCKING: 'Intent' field is empty.")
        elif len(fields["intent"]) > 150:
            anomalies.append(
                f"WARNING: 'Intent' field is {len(fields['intent'])} chars; keep under 150."
            )

        tier_num: int = fields["tier_number"]
        if tier_num not in range(1, 9):
            anomalies.append(f"BLOCKING: 'Tier' value '{tier_num}' is invalid. Must be 1–8.")

        app: str = fields["app_context"]
        if app not in VALID_APP_CONTEXTS:
            anomalies.append(
                f"BLOCKING: 'App Context' value '{app}' is not valid. "
                f"Must be one of: {', '.join(sorted(VALID_APP_CONTEXTS))}."
            )

        skills: list[str] = fields["skills"]
        if not skills:
            anomalies.append("BLOCKING: 'Skills' field is empty; list at least one skill.")
        elif len(skills) > 5:
            anomalies.append(f"WARNING: 'Skills' lists {len(skills)} skills; NEXUS should use ≤ 5.")

        anomalies.extend(
            f"BLOCKING: '{req_field}' field is empty. Must be 'NONE' or a description."
            for req_field in ("conflicts", "constraints", "obs_gaps")
            if not fields[req_field]
        )

        # ── Level 3: Semantic validation ─────────────────────────────────────
        if tier_num in range(1, 9) and fields["tier_name"]:
            expected = TIER_NAMES.get(tier_num, "")
            key_words = expected.lower().split()[:2]
            if expected and not any(w in fields["tier_name"].lower() for w in key_words):
                anomalies.append(
                    f"WARNING: Tier name '{fields['tier_name']}' doesn't match "
                    f"T{tier_num} expected name '{expected}'."
                )

        # ── Level 4: Cross-validation (only if no blocking errors) ───────────
        blocking = [a for a in anomalies if a.startswith("BLOCKING")]
        if not blocking:
            rest_start = end_idx + len(end_marker) if end_idx != -1 else start_idx + len(raw_block)
            rest = response_text[rest_start:]
            conflict_language = re.search(
                r"\b(?:conflict|contradicts|overrides|takes precedence|wins over)\b",
                rest,
                re.IGNORECASE,
            )
            if conflict_language and fields["conflicts"].strip().upper() == "NONE":
                anomalies.append(
                    "WARNING: 'Conflicts' field says NONE but response body uses "
                    "conflict resolution language. Update the Conflicts field."
                )

        is_valid = (
            len(blocking) == 0
            and fields is not None
            and bool(
                fields["intent"]
                and tier_num in range(1, 9)
                and app in VALID_APP_CONTEXTS
                and skills
            )
        )

        return {
            "valid": is_valid,
            "fields": fields,
            "anomalies": anomalies,
            "raw_block": raw_block,
        }
