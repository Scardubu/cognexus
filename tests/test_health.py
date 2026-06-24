"""HTTP liveness and readiness tests."""

from fastapi.testclient import TestClient

from server.app import app


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_in_development() -> None:
    with TestClient(app) as client:
        response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
