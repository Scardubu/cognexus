"""Async SQLite-backed OpenAI Agents SDK session factory."""

from __future__ import annotations

from pathlib import Path

from agents.extensions.memory import AsyncSQLiteSession


def create_sqlite_session(session_id: str, db_path: Path) -> AsyncSQLiteSession:
    """Create a persistent aiosqlite session and ensure its directory exists."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return AsyncSQLiteSession(session_id=session_id, db_path=db_path)
