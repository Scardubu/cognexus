"""OpenAI Agents SDK input guardrail and HTTP pre-screening."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, input_guardrail

from security.sanitization import sanitize_text


class InputRejectedError(ValueError):
    """Raised when input fails deterministic pre-screening."""


def screen_input(text: str, *, max_chars: int) -> str:
    """Sanitize input and reject likely instruction-injection attempts."""
    try:
        result = sanitize_text(text, max_chars=max_chars)
    except ValueError as exc:
        raise InputRejectedError(str(exc)) from exc
    if result.findings:
        raise InputRejectedError("request contains prompt-injection or policy-bypass patterns")
    if not result.text:
        raise InputRejectedError("request message is empty")
    return result.text


InputGuardrailCallable = Callable[
    [RunContextWrapper[Any], Agent[Any], str | list[Any]],
    Awaitable[GuardrailFunctionOutput],
]


def create_input_guardrail(max_chars: int) -> Any:
    """Build a guardrail that enforces the configured input-size policy.

    The SDK wraps the decorated callable in an ``InputGuardrail`` object, so the
    return type intentionally remains ``Any`` for compatibility across supported
    OpenAI Agents SDK releases.
    """
    if max_chars < 1:
        raise ValueError("max_chars must be positive")

    @input_guardrail(name="nexus_input_guardrail", run_in_parallel=False)
    async def configured_input_guardrail(
        context: RunContextWrapper[Any],
        agent: Agent[Any],
        input_value: str | list[Any],
    ) -> GuardrailFunctionOutput:
        del context, agent
        text = input_value if isinstance(input_value, str) else str(input_value)
        try:
            screen_input(text, max_chars=max_chars)
        except InputRejectedError as exc:
            return GuardrailFunctionOutput(
                output_info={"reason": str(exc)}, tripwire_triggered=True
            )
        return GuardrailFunctionOutput(output_info={"accepted": True}, tripwire_triggered=False)

    return configured_input_guardrail


# Backward-compatible default for direct imports. Agent construction uses the
# configured factory so SDK-level and HTTP-level limits cannot drift.
nexus_input_guardrail = create_input_guardrail(50_000)
