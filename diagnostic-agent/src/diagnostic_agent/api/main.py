"""API local del agente — scaffolding mínimo de Fase 2.

Solo expone salud y preparación del entorno; la lógica funcional del agente
llega en fases posteriores (aprobación del autor pendiente).
"""

import socket
from typing import Any

import httpx
from fastapi import FastAPI

import mecanico_contracts as mc
from diagnostic_agent import __version__
from diagnostic_agent.config import settings

HTTP_OK = 200

app = FastAPI(
    title="Mecánico IA — Diagnostic Agent (edge)",
    version=__version__,
    description="Núcleo inteligente edge. Scaffolding: /health y /ready.",
)


@app.get("/health")
def health() -> dict[str, Any]:
    """Liveness: el proceso está vivo y la configuración cargada."""
    return {
        "status": "ok",
        "service": "diagnostic-agent",
        "version": __version__,
        "contracts_schema_version": mc.SCHEMA_VERSION,
        "device_id": settings.device_id,
        "transport": settings.transport,
    }


@app.get("/ready")
def ready() -> dict[str, Any]:
    """Readiness: comprueba dependencias externas alcanzables (emulador, Ollama)."""
    checks: dict[str, bool | str] = {}

    if settings.transport == "tcp":
        try:
            with socket.create_connection(
                (settings.emulator_host, settings.emulator_port), timeout=2
            ):
                checks["obd_transport_tcp"] = True
        except OSError as exc:
            checks["obd_transport_tcp"] = f"unreachable: {exc}"
    else:
        checks["obd_transport_tcp"] = "n/a (transport != tcp)"

    try:
        r = httpx.get(f"{settings.ollama_host}/api/version", timeout=2)
        checks["ollama"] = r.status_code == HTTP_OK
    except httpx.HTTPError as exc:
        checks["ollama"] = f"unreachable: {exc}"

    all_ok = all(v is True or (isinstance(v, str) and v.startswith("n/a")) for v in checks.values())
    return {"ready": all_ok, "checks": checks}
