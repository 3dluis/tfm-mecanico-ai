"""API de la plataforma cloud — scaffolding mínimo de Fase 2 (/health y /ready)."""

from typing import Any

from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, text

import mecanico_contracts as mc
from cloud_platform import __version__


class CloudSettings(BaseSettings):
    """Configuración de la nube. Ver ``.env.example``."""

    model_config = SettingsConfigDict(env_prefix="MECANICO_CLOUD_", extra="ignore")

    database_url: str = "postgresql+psycopg://mecanico:mecanico@postgres:5432/mecanico"
    api_key: str = "dev-key-change-me"


settings = CloudSettings()

app = FastAPI(
    title="Mecánico IA — Cloud Platform",
    version=__version__,
    description="Plataforma complementaria (simple a propósito, ADR-0006).",
)


@app.get("/health")
def health() -> dict[str, Any]:
    """Liveness."""
    return {
        "status": "ok",
        "service": "cloud-platform",
        "version": __version__,
        "contracts_schema_version": mc.SCHEMA_VERSION,
    }


@app.get("/ready")
def ready() -> dict[str, Any]:
    """Readiness: PostgreSQL alcanzable."""
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ready": True, "checks": {"postgres": True}}
    except Exception as exc:  # pragma: no cover - camino de error de infraestructura
        return {"ready": False, "checks": {"postgres": f"unreachable: {exc}"}}
