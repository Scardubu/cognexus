"""OpenAI Agents SDK output guardrail and deterministic output screening."""

from __future__ import annotations

import re
from typing import Any, cast

from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, output_guardrail

from middleware.trace_block_validator import TraceBlockValidator
from validators.constraint_validator import ConstraintValidator, ValidationResult

_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "SAFETY-SECRET-01",
        re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        "Output appears to contain an OpenAI-style secret key.",
    ),
    (
        "SAFETY-SECRET-02",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "Output appears to contain a private key.",
    ),
    (
        "SAFETY-PROMPT-01",
        re.compile(r"(?:here is|verbatim|full)\s+(?:the\s+)?(?:system|developer)\s+prompt", re.I),
        "Output appears to disclose privileged prompt material.",
    ),
)


def output_safety_findings(text: str) -> list[dict[str, str]]:
    """Return deterministic output-safety findings without exposing matched secrets."""
    findings: list[dict[str, str]] = []
    for code, pattern, description in _SECRET_PATTERNS:
        if pattern.search(text):
            findings.append(
                {
                    "code": code,
                    "severity": "P0",
                    "description": description,
                    "rejection_prompt": "Remove all secrets or privileged prompt content.",
                }
            )
    return findings


def validate_output(text: str, *, require_trace: bool = True) -> dict[str, Any]:
    """Validate architecture constraints, output safety, and the NEXUS trace block."""
    constraints = ConstraintValidator().validate(text)
    safety = output_safety_findings(text)
    trace = (
        TraceBlockValidator().validate(text) if require_trace else {"valid": True, "anomalies": []}
    )
    return {
        "valid": constraints.passed and not safety and bool(trace["valid"]),
        "constraints": constraints,
        "safety": safety,
        "trace": trace,
    }


@output_guardrail(name="nexus_output_guardrail")
async def nexus_output_guardrail(
    context: RunContextWrapper[Any],
    agent: Agent[Any],
    output_value: Any,
) -> GuardrailFunctionOutput:
    """Trip when the final output violates safety, trace, or architecture constraints."""
    del context, agent
    text = output_value if isinstance(output_value, str) else str(output_value)
    result = validate_output(text)
    constraint_result = cast(ValidationResult, result["constraints"])
    violations = [*constraint_result.violations, *result["safety"]]
    return GuardrailFunctionOutput(
        output_info={
            "violations": violations,
            "trace_anomalies": result["trace"].get("anomalies", []),
        },
        tripwire_triggered=not result["valid"],
    )
