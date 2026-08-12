"""Smoke de la API cloud: /health responde."""

from fastapi.testclient import TestClient

from cloud_platform.api.main import app

HTTP_OK = 200


def test_health() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == HTTP_OK
    assert r.json()["service"] == "cloud-platform"
