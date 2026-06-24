"""Session backends and lifecycle management."""

from sessions.session_manager import SessionManager, SessionUnavailableError

__all__ = ["SessionManager", "SessionUnavailableError"]
