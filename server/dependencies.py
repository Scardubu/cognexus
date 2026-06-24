"""FastAPI dependencies for authentication and lifespan-owned services."""

from __future__ import annotations

import hmac
from typing import Annotated, cast

from fastapi import Depends, Header, HTTPException, Request, status

from config.settings import Settings
from orchestrator.runtime import RunGate
from sessions.session_manager import SessionManager
from skill_runtime.loader import SkillRegistry


def settings_dependency(request: Request) -> Settings:
    """Provide the immutable settings attached to this application instance."""
    return cast(Settings, request.app.state.settings)


def session_manager_dependency(request: Request) -> SessionManager:
    """Provide the lifespan-managed session manager."""
    return cast(SessionManager, request.app.state.session_manager)


def run_gate_dependency(request: Request) -> RunGate:
    """Provide the process-local bounded execution gate."""
    return cast(RunGate, request.app.state.run_gate)


def skill_registry_dependency(request: Request) -> SkillRegistry:
    """Provide the lifespan-owned portable skill registry."""
    return cast(SkillRegistry, request.app.state.skill_registry)


async def require_api_key(
    settings: Annotated[Settings, Depends(settings_dependency)],
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> None:
    """Require X-API-Key or Bearer authentication when a key is configured."""
    expected = settings.api_key_value
    if expected is None:
        if settings.nexus_env in {"staging", "production"}:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="service authentication is not configured",
            )
        return

    bearer: str | None = None
    if authorization and authorization.lower().startswith("bearer "):
        bearer = authorization[7:].strip()
    candidates = tuple(value for value in (x_api_key, bearer) if value)
    if not candidates or not any(
        hmac.compare_digest(candidate, expected) for candidate in candidates
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
