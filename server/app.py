"""Production FastAPI application for NEXUS."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi import Path as ApiPath
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import JSONResponse, StreamingResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from config.settings import APP_VERSION, Settings, get_settings
from observability import configure_logging, configure_tracing, flush_tracing
from observability.logging import get_logger
from observability.metrics import metrics
from orchestrator.model_router import validate_configured_models
from orchestrator.nexus_agent import run_nexus
from orchestrator.runtime import RunGate, sdk_runtime
from orchestrator.skill_recommender import recommend_skills
from orchestrator.tier_classifier import classify_task
from security.rate_limits import create_limiter
from security.secrets import validate_required_secrets
from server.body_limit import RequestBodyLimitMiddleware
from server.dependencies import (
    require_api_key,
    run_gate_dependency,
    session_manager_dependency,
    skill_registry_dependency,
)
from server.errors import install_exception_handlers
from server.middleware import RequestContextMiddleware, SecurityHeadersMiddleware
from server.schemas import (
    HealthResponse,
    RunRequest,
    RunResponse,
    SessionResponse,
    SkillCatalogResponse,
    SkillDetailResponse,
    SkillRecommendationRequest,
    SkillRecommendationResponse,
    SkillResourceSummary,
    SkillSummary,
)
from sessions.intelligence import SessionIntelligence
from sessions.session_manager import SessionManager
from skill_runtime.catalog import get_skill_registry
from skill_runtime.loader import SkillRegistry

AuthDependency = Annotated[None, Depends(require_api_key)]
SessionDependency = Annotated[SessionManager, Depends(session_manager_dependency)]
RunGateDependency = Annotated[RunGate, Depends(run_gate_dependency)]
SkillRegistryDependency = Annotated[SkillRegistry, Depends(skill_registry_dependency)]

logger = get_logger(__name__)


def _sse(event: str, payload: dict[str, Any] | str) -> str:
    data = payload if isinstance(payload, str) else json.dumps(payload, separators=(",", ":"))
    return f"event: {event}\ndata: {data}\n\n"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build one independently configurable application instance."""
    cfg = settings or get_settings()
    limiter = create_limiter(cfg)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging(cfg.nexus_log_level, json_logs=cfg.nexus_env != "development")
        configure_tracing(
            cfg.otel_service_name,
            enabled=cfg.nexus_otel_enabled,
            endpoint=cfg.otel_exporter_otlp_endpoint,
            console=cfg.nexus_otel_console,
            sample_ratio=cfg.nexus_otel_sample_ratio,
            service_version=APP_VERSION,
            environment=cfg.nexus_env,
        )
        app.state.settings = cfg
        app.state.session_manager = SessionManager(cfg)
        app.state.run_gate = RunGate(cfg.nexus_max_concurrent_runs)
        app.state.skill_registry = get_skill_registry(cfg)
        if cfg.nexus_skills_enabled:
            app.state.skill_registry.refresh(force=True)
        app.state.model_validation = {
            "checked": False,
            "available": [],
            "missing": [],
            "cached": False,
        }
        if cfg.nexus_model_validation_mode == "strict":
            app.state.model_validation = await validate_configured_models(cfg, force=True)
        try:
            yield
        finally:
            await app.state.session_manager.close()
            await sdk_runtime.close()
            await asyncio.to_thread(flush_tracing)

    application = FastAPI(
        title="Cognexus Production API",
        version=APP_VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    application.state.settings = cfg
    application.state.limiter = limiter
    application.state.skill_registry = get_skill_registry(cfg)

    async def slowapi_handler(request: Request, exc: Exception) -> Response:
        if not isinstance(exc, RateLimitExceeded):
            raise exc
        return _rate_limit_exceeded_handler(request, exc)

    application.add_exception_handler(RateLimitExceeded, slowapi_handler)
    application.add_middleware(SlowAPIMiddleware)
    application.add_middleware(RequestBodyLimitMiddleware, max_bytes=cfg.nexus_max_request_bytes)
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(RequestContextMiddleware)
    application.add_middleware(TrustedHostMiddleware, allowed_hosts=cfg.nexus_trusted_hosts)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.nexus_cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-API-Key",
            "X-Request-ID",
        ],
        expose_headers=[
            "X-Request-ID",
            "X-Trace-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
        ],
    )
    install_exception_handlers(application)
    FastAPIInstrumentor.instrument_app(
        application,
        excluded_urls="/health,/metrics",
        exclude_spans=["receive", "send"],
    )

    if cfg.nexus_enable_docs:

        @application.get(
            "/openapi.json",
            include_in_schema=False,
            dependencies=[Depends(require_api_key)],
        )
        async def openapi_schema() -> JSONResponse:
            """Return the OpenAPI schema behind the configured authentication policy."""
            return JSONResponse(application.openapi())

        @application.get(
            "/docs",
            include_in_schema=False,
            dependencies=[Depends(require_api_key)],
        )
        async def swagger_docs() -> Response:
            """Return authenticated Swagger UI."""
            return get_swagger_ui_html(
                openapi_url="/openapi.json", title=f"{application.title} - Swagger UI"
            )

        @application.get(
            "/redoc",
            include_in_schema=False,
            dependencies=[Depends(require_api_key)],
        )
        async def redoc_docs() -> Response:
            """Return authenticated ReDoc UI."""
            return get_redoc_html(openapi_url="/openapi.json", title=f"{application.title} - ReDoc")

    @application.get("/health", response_model=HealthResponse, tags=["operations"])
    async def health() -> HealthResponse:
        """Return process liveness without calling external services."""
        return HealthResponse(status="ok", details={"version": APP_VERSION})

    @application.get("/ready", response_model=HealthResponse, tags=["operations"])
    async def ready(manager: SessionDependency) -> Response | HealthResponse:
        """Return readiness for persistence, credentials, and configured models."""
        session_status = await manager.readiness()
        model_status: dict[str, Any] = application.state.model_validation
        if cfg.nexus_model_validation_mode == "warn" and cfg.openai_key_value:
            model_status = await validate_configured_models(cfg)
            application.state.model_validation = model_status

        skill_status = (
            application.state.skill_registry.status()
            if cfg.nexus_skills_enabled
            else {"ready": True, "enabled": False, "skill_count": 0}
        )
        live_run = cfg.nexus_env not in {"development", "test"}
        missing_secrets = validate_required_secrets(cfg, live_run=live_run)
        secrets_ready = not missing_secrets
        models_ready = cfg.nexus_model_validation_mode != "strict" or (
            bool(model_status.get("checked")) and not model_status.get("missing")
        )
        skills_ready = not cfg.nexus_skills_enabled or bool(skill_status.get("ready"))
        is_ready = (
            bool(session_status.get("ready")) and secrets_ready and models_ready and skills_ready
        )
        payload = HealthResponse(
            status="ready" if is_ready else "not_ready",
            details={
                "sessions": session_status,
                "models": model_status,
                "skills": skill_status,
                "openai_key_configured": bool(cfg.openai_key_value),
                "missing_secrets": missing_secrets,
                "run_capacity": cfg.nexus_max_concurrent_runs,
            },
        )
        if is_ready:
            return payload
        return Response(
            content=payload.model_dump_json(),
            media_type="application/json",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    @application.post(
        "/v1/run",
        response_model=RunResponse,
        dependencies=[Depends(require_api_key)],
        tags=["nexus"],
    )
    @limiter.limit(cfg.nexus_rate_limit)
    async def run(
        request: Request,
        response: Response,
        payload: RunRequest,
        manager: SessionDependency,
        gate: RunGateDependency,
    ) -> RunResponse:
        """Execute one validated, capacity-bounded NEXUS request."""
        del request, response
        async with asyncio.timeout(cfg.nexus_request_timeout_seconds):
            result = await run_nexus(
                payload.message,
                session_id=payload.session_id,
                dry_run=payload.dry_run,
                execution_mode=payload.execution_mode,
                expert_tier_override=payload.expert_tier_override,
                settings=cfg,
                session_manager=manager,
                run_gate=gate,
            )
        return RunResponse.model_validate(result.model_dump(mode="json"))

    @application.post(
        "/v1/run/stream",
        dependencies=[Depends(require_api_key)],
        tags=["nexus"],
    )
    @limiter.limit(cfg.nexus_rate_limit)
    async def run_stream(
        request: Request,
        payload: RunRequest,
        manager: SessionDependency,
        gate: RunGateDependency,
    ) -> StreamingResponse:
        """Stream progress heartbeats, then only validated output as SSE."""

        async def events() -> AsyncIterator[str]:
            yield _sse(
                "accepted",
                {
                    "request_id": getattr(request.state, "request_id", None),
                    "session_id": payload.session_id,
                    "execution_mode": payload.execution_mode,
                },
            )
            task = asyncio.create_task(
                run_nexus(
                    payload.message,
                    session_id=payload.session_id,
                    dry_run=payload.dry_run,
                    execution_mode=payload.execution_mode,
                    expert_tier_override=payload.expert_tier_override,
                    settings=cfg,
                    session_manager=manager,
                    run_gate=gate,
                ),
                name="nexus-sse-run",
            )
            try:
                async with asyncio.timeout(cfg.nexus_request_timeout_seconds):
                    while not task.done():
                        done, _ = await asyncio.wait({task}, timeout=15.0)
                        if not done:
                            yield _sse("heartbeat", {"status": "running"})
                    result = await task

                yield _sse(
                    "metadata",
                    {
                        "run_id": result.run_id,
                        "session_id": result.session_id,
                        "trace_id": result.trace_id,
                        "execution_mode": result.execution_mode,
                        "confidence": result.confidence,
                        "recommended_skills": [
                            item.model_dump(mode="json") for item in result.recommended_skills
                        ],
                    },
                )
                for index in range(0, len(result.response_text), cfg.nexus_stream_chunk_chars):
                    chunk = result.response_text[index : index + cfg.nexus_stream_chunk_chars]
                    yield _sse("delta", {"text": chunk})
                yield _sse("done", result.model_dump_json())
            except TimeoutError:
                yield _sse(
                    "error",
                    {
                        "error": "request_timeout",
                        "message": "Cognexus execution timed out",
                    },
                )
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.exception("sse_execution_failed", error_type=type(exc).__name__)
                yield _sse(
                    "error",
                    {
                        "error": "execution_failed",
                        "message": "Cognexus execution failed",
                    },
                )
            finally:
                if not task.done():
                    task.cancel()
                    with suppress(asyncio.CancelledError):
                        await task

        return StreamingResponse(
            events(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-store",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @application.get(
        "/v1/skills",
        response_model=SkillCatalogResponse,
        dependencies=[Depends(require_api_key)],
        tags=["skills"],
    )
    async def list_skills(registry: SkillRegistryDependency) -> SkillCatalogResponse:
        """Return installed skill discovery metadata without instruction bodies."""
        skills = [
            SkillSummary(
                name=item.name,
                description=item.description,
                category=item.category,
                risk=item.risk,
            )
            for item in registry.metadata()
        ]
        return SkillCatalogResponse(count=len(skills), skills=skills)

    @application.post(
        "/v1/skills/recommend",
        response_model=SkillRecommendationResponse,
        dependencies=[Depends(require_api_key)],
        tags=["skills"],
    )
    @limiter.limit(cfg.nexus_rate_limit)
    async def recommend_installed_skills(
        request: Request,
        response: Response,
        payload: SkillRecommendationRequest,
        registry: SkillRegistryDependency,
    ) -> SkillRecommendationResponse:
        """Return deterministic, explainable, mode-aware skill recommendations."""
        del request, response
        classification = classify_task(
            payload.message,
            expert_override=payload.expert_tier_override,
        )
        recommendations = recommend_skills(
            payload.message,
            execution_mode=payload.execution_mode,
            classification=classification,
            registry=registry,
        )
        for recommendation in recommendations:
            metrics.skill_recommendations.labels(
                payload.execution_mode,
                "true" if recommendation.activation_suggested else "false",
            ).inc()
        return SkillRecommendationResponse(
            execution_mode=payload.execution_mode,
            tier=classification.tier,
            tier_name=classification.tier_name,
            classification_confidence=classification.confidence,
            classification_ambiguity=classification.ambiguity,
            recommended_skills=recommendations,
        )

    @application.get(
        "/v1/skills/{skill_name}",
        response_model=SkillDetailResponse,
        dependencies=[Depends(require_api_key)],
        tags=["skills"],
    )
    async def get_skill(skill_name: str, registry: SkillRegistryDependency) -> SkillDetailResponse:
        """Return one skill's metadata and safe resource inventory."""
        document = registry.activate(skill_name)
        return SkillDetailResponse(
            name=document.metadata.name,
            description=document.metadata.description,
            category=document.metadata.category,
            risk=document.metadata.risk,
            fingerprint=document.fingerprint,
            resources=[
                SkillResourceSummary.model_validate(resource.model_dump(mode="json"))
                for resource in document.resources
            ],
        )

    @application.get(
        "/v1/sessions/{session_id}/intelligence",
        response_model=SessionIntelligence,
        dependencies=[Depends(require_api_key)],
        tags=["sessions"],
    )
    async def get_session_intelligence(
        session_id: Annotated[
            str,
            ApiPath(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$"),
        ],
        manager: SessionDependency,
    ) -> SessionIntelligence:
        """Return a secret-redacted rolling summary and continuity score."""
        return await manager.intelligence(session_id)

    @application.get(
        "/v1/sessions/{session_id}",
        response_model=SessionResponse,
        dependencies=[Depends(require_api_key)],
        tags=["sessions"],
    )
    async def get_session(
        session_id: Annotated[
            str,
            ApiPath(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$"),
        ],
        manager: SessionDependency,
    ) -> SessionResponse:
        """Return safe session metadata without message content."""
        return SessionResponse.model_validate(await manager.inspect(session_id))

    @application.delete(
        "/v1/sessions/{session_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_api_key)],
        tags=["sessions"],
    )
    async def delete_session(
        session_id: Annotated[
            str,
            ApiPath(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$"),
        ],
        manager: SessionDependency,
    ) -> Response:
        """Delete all stored history for a session."""
        await manager.delete(session_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @application.get("/metrics", include_in_schema=False)
    async def metrics_endpoint(_: AuthDependency) -> Response:
        """Expose Prometheus metrics behind the service authentication policy."""
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    return application


app = create_app()
