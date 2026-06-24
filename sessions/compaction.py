"""OpenAI Responses compaction wrapper for long-running sessions."""

from __future__ import annotations

from typing import Any

from agents.memory import OpenAIResponsesCompactionSession, Session


def wrap_with_compaction(
    session_id: str,
    underlying_session: Session,
    *,
    model: str,
    candidate_items: int,
) -> OpenAIResponsesCompactionSession:
    """Wrap a session using the SDK's native Responses compaction mechanism."""

    def should_trigger(context: dict[str, Any]) -> bool:
        items = context.get("compaction_candidate_items")
        return isinstance(items, list) and len(items) >= candidate_items

    return OpenAIResponsesCompactionSession(
        session_id=session_id,
        underlying_session=underlying_session,
        model=model,
        compaction_mode="auto",
        should_trigger_compaction=should_trigger,
    )
