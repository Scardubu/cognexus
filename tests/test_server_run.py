"""FastAPI NEXUS execution tests."""

from fastapi.testclient import TestClient

from server.app import app


def test_run_dry_run() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/run",
            json={
                "message": "Analyze this system architecture.",
                "session_id": "api-test",
                "dry_run": True,
            },
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["session_id"] == "api-test"
    assert body["trace_validation"]["valid"] is True
    assert body["response_text"].startswith("┌─ NEXUS SKILL TRACE")


def test_stream_dry_run() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/run/stream",
            json={
                "message": "Check deployment readiness.",
                "session_id": "stream-test",
                "dry_run": True,
            },
        )
    assert response.status_code == 200
    assert "event: metadata" in response.text
    assert "event: done" in response.text


def test_invalid_session_id() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/run",
            json={"message": "hello", "session_id": "not allowed spaces", "dry_run": True},
        )
    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"


def test_security_and_trace_headers() -> None:
    with TestClient(app) as client:
        response = client.get("/health", headers={"X-Request-ID": "test-request-1"})
    assert response.headers["x-request-id"] == "test-request-1"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_stream_starts_with_safe_acceptance_event() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/run/stream",
            json={"message": "Check readiness.", "dry_run": True},
        )
    assert response.text.startswith("event: accepted")
    assert "event: metadata" in response.text
    assert "event: done" in response.text
