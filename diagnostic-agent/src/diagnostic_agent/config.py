"""Configuración tipada del agente edge (variables ``MECANICO_*``)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Configuración del nodo edge. Ver ``.env.example`` en la raíz del monorepo."""

    model_config = SettingsConfigDict(env_prefix="MECANICO_", extra="ignore")

    # Identidad (ADR-0007: los contratos exigen vehicle_id/device_id)
    device_id: str = "dev-local"
    vehicle_id: str = "veh-local"

    # Transporte OBD (ADR-0004)
    transport: str = "tcp"  # serial | tcp | bluetooth-rfcomm
    serial_port: str = ""
    emulator_host: str = "obd-emulator"
    emulator_port: int = 35000
    sample_rate_hz: float = 1.0

    # LLM local (la selección final se decide con el smoke test de Fase 2)
    ollama_host: str = "http://ollama:11434"
    llm_model: str = "qwen2.5:3b"

    # Persistencia
    db_path: str = "/app/data/agent.sqlite3"

    # API local
    api_host: str = "0.0.0.0"
    api_port: int = 8000


settings = AgentSettings()
