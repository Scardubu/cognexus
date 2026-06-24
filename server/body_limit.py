"""Streaming ASGI request-body limit with an early Content-Length fast path."""

from __future__ import annotations

import json

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from security.identifiers import normalize_request_id, normalize_request_id_header


class RequestBodyTooLarge(Exception):
    """Internal signal used to stop consuming an oversized request body."""


class RequestBodyLimitMiddleware:
    """Reject request bodies above a configured byte limit without buffering them."""

    def __init__(self, app: ASGIApp, *, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        request_id = self._request_id(scope, headers)
        content_length = self._content_length(headers)
        if content_length is not None and content_length > self.max_bytes:
            await self._send_rejection(send, request_id)
            return

        received = 0
        response_started = False

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    raise RequestBodyTooLarge
            return message

        async def tracked_send(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, limited_receive, tracked_send)
        except RequestBodyTooLarge:
            if not response_started:
                await self._send_rejection(send, request_id)
                return
            raise

    @staticmethod
    def _content_length(headers: dict[bytes, bytes]) -> int | None:
        raw = headers.get(b"content-length")
        if raw is None:
            return None
        try:
            value = int(raw)
        except ValueError:
            return None
        return max(0, value)

    @staticmethod
    def _request_id(scope: Scope, headers: dict[bytes, bytes]) -> str:
        state = scope.setdefault("state", {})
        existing = state.get("request_id")
        if isinstance(existing, str) and existing:
            request_id = normalize_request_id(existing)
            state["request_id"] = request_id
            return request_id
        request_id = normalize_request_id_header(headers.get(b"x-request-id"))
        state["request_id"] = request_id
        return request_id

    async def _send_rejection(self, send: Send, request_id: str) -> None:
        payload = json.dumps(
            {
                "error": "request_body_too_large",
                "message": f"request body exceeds the {self.max_bytes}-byte limit",
                "request_id": request_id,
                "details": {"max_bytes": self.max_bytes},
            },
            separators=(",", ":"),
        ).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(payload)).encode("ascii")),
                    (b"cache-control", b"no-store"),
                    (b"x-request-id", request_id.encode("ascii")),
                ],
            }
        )
        await send({"type": "http.response.body", "body": payload})
