"""Request context, bounded metric labels, and baseline security headers."""

from __future__ import annotations

import time

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from observability.logging import get_logger
from observability.metrics import metrics
from observability.tracing import get_trace_id
from security.identifiers import normalize_request_id_header

logger = get_logger(__name__)


class RequestContextMiddleware:
    """Bind request metadata and attach stable request/trace identifiers."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        raw_headers = dict(scope.get("headers", []))
        request_id = normalize_request_id_header(raw_headers.get(b"x-request-id"))
        scope.setdefault("state", {})["request_id"] = request_id
        method = str(scope.get("method", "UNKNOWN"))
        status_code = 500
        started = time.perf_counter()

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                headers = list(message.get("headers", []))
                existing = {name.lower() for name, _ in headers}
                if b"x-request-id" not in existing:
                    headers.append((b"x-request-id", request_id.encode("ascii")))
                trace_id = get_trace_id()
                if trace_id and b"x-trace-id" not in existing:
                    headers.append((b"x-trace-id", trace_id.encode("ascii")))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            route = scope.get("route")
            route_template = getattr(route, "path", None)
            metric_route = route_template if isinstance(route_template, str) else "__unmatched__"
            duration = time.perf_counter() - started
            metrics.requests.labels(method, metric_route, str(status_code)).inc()
            metrics.request_latency.labels(metric_route).observe(duration)
            logger.info(
                "http_request",
                method=method,
                route=metric_route,
                status=status_code,
                duration_ms=duration * 1000,
            )
            structlog.contextvars.clear_contextvars()


class SecurityHeadersMiddleware:
    """Set conservative headers for JSON/SSE API responses."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                existing = {name.lower() for name, _ in headers}
                additions = [
                    (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"x-frame-options", b"DENY"),
                    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
                    (b"cross-origin-resource-policy", b"same-origin"),
                ]
                for name, value in additions:
                    if name not in existing:
                        headers.append((name, value))
                if b"cache-control" not in existing:
                    headers.append((b"cache-control", b"no-store"))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)
