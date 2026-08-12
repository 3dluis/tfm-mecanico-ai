"""Smoke de la API del agente: /health responde con contratos alineados."""

from fastapi.testclient import TestClient

import mecanico_contracts as mc
from diagnostic_agent.api.main import app

HTTP_OK = 200


def test_health() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == HTTP_OK
    body = r.json()
    assert body["status"] == "ok"
    assert body["contracts_schema_version"] == mc.SCHEMA_VERSION
