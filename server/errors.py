"""Structured error types and FastAPI exception handlers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from middleware.input_guardrail import InputRejectedError
from observability.logging import get_logger
from observability.metrics import metrics
from orchestrator.errors import NexusOutputTooLargeError, NexusOutputValidationError
from orchestrator.runtime import RunCapacityError
from server.schemas import ErrorResponse
from sessions.session_manager import SessionUnavailableError
from skill_runtime.loader import SkillLoadError
from skill_runtime.security import SkillSecurityError

logger = get_logger(__name__)


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _response(
    request: Request,
    status_code: int,
    error: str,
    message: str,
    details: dict[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        error=error,
        message=message,
        request_id=_request_id(request),
        details=details,
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json"),
        headers=headers,
    )


def install_exception_handlers(app: FastAPI) -> None:
    """Install consistent, non-sensitive JSON exception handlers."""

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _response(
            request,
            422,
            "validation_error",
            "request validation failed",
            {
                "errors": [
                    {key: value for key, value in item.items() if key != "input"}
                    for item in exc.errors()
                ]
            },
        )

    @app.exception_handler(InputRejectedError)
    async def input_handler(request: Request, exc: InputRejectedError) -> JSONResponse:
        return _response(request, 400, "input_rejected", str(exc))

    @app.exception_handler(SessionUnavailableError)
    async def session_handler(request: Request, exc: SessionUnavailableError) -> JSONResponse:
        return _response(request, 503, "session_unavailable", str(exc))

    @app.exception_handler(SkillLoadError)
    async def skill_load_handler(request: Request, exc: SkillLoadError) -> JSONResponse:
        return _response(request, 404, "skill_not_found", str(exc))

    @app.exception_handler(SkillSecurityError)
    async def skill_security_handler(request: Request, exc: SkillSecurityError) -> JSONResponse:
        return _response(request, 400, "invalid_skill_path", str(exc))

    @app.exception_handler(RunCapacityError)
    async def capacity_handler(request: Request, exc: RunCapacityError) -> JSONResponse:
        return _response(
            request,
            503,
            "capacity_exhausted",
            str(exc),
            headers={"Retry-After": "5"},
        )

    @app.exception_handler(TimeoutError)
    async def timeout_handler(request: Request, exc: TimeoutError) -> JSONResponse:
        del exc
        return _response(request, 504, "request_timeout", "Cognexus execution timed out")

    @app.exception_handler(NexusOutputValidationError)
    async def output_handler(request: Request, exc: NexusOutputValidationError) -> JSONResponse:
        return _response(request, 502, "invalid_model_output", str(exc))

    @app.exception_handler(NexusOutputTooLargeError)
    async def output_size_handler(request: Request, exc: NexusOutputTooLargeError) -> JSONResponse:
        return _response(request, 502, "model_output_too_large", str(exc))

    @app.exception_handler(HTTPException)
    async def http_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return _response(
            request,
            exc.status_code,
            "http_error",
            str(exc.detail),
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        metrics.errors.labels("http", type(exc).__name__).inc()
        logger.exception(
            "unhandled_http_error",
            request_id=_request_id(request),
            error_type=type(exc).__name__,
        )
        return _response(request, 500, "internal_error", "unexpected server error")
