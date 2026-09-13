"""Configuración por variables de entorno.

Todo lo que distingue una máquina de otra —credenciales, endpoints, puertos— se
lee del entorno o de ``.env``. Nada de eso entra en Git: ``.env.example``
documenta las claves, ``.env`` guarda los valores.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from mecanico_ia_exp.config.paths import ROOT

#: Proveedores con implementación en ``mecanico_ia_exp.llm.provider.get_llm``. La variante
#: ``transformers-lora@<subdirectorio>`` se acepta por la CLI, no por configuración de entorno.
LLMProviderName = Literal["echo", "ollama", "transformers", "transformers-lora"]


class DatabaseSettings(BaseSettings):
    """Conexión al PostgreSQL que alberga el corpus vectorial."""

    model_config = SettingsConfigDict(
        env_file=ROOT / ".env", env_prefix="DATABASE_", extra="ignore"
    )

    host: str = "localhost"
    port: int = 5432
    name: str = "mecanico_ia_exp"
    user: str = ""
    password: str = ""
    schema_name: str = Field(default="public", alias="DATABASE_SCHEMA")

    @property
    def url(self) -> str:
        """URL SQLAlchemy. Usuario y contraseña vacíos delegan en la autenticación
        local de PostgreSQL (peer/trust), que es el caso habitual en macOS."""
        credentials = ""
        if self.user:
            credentials = self.user
            if self.password:
                credentials += f":{self.password}"
            credentials += "@"
        return f"postgresql+psycopg://{credentials}{self.host}:{self.port}/{self.name}"


class LLMSettings(BaseSettings):
    """Proveedor LLM. La lógica científica no depende de cuál sea."""

    model_config = SettingsConfigDict(env_file=ROOT / ".env", env_prefix="LLM_", extra="ignore")

    provider: LLMProviderName = "echo"
    model: str = ""
    base_url: str = ""
    api_key: str = ""
    temperature: float = 0.0
    max_tokens: int = 2048
    timeout_s: int = 120


class ExperimentSettings(BaseSettings):
    """Parámetros que definen la reproducibilidad de una ejecución."""

    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")

    global_seed: int = Field(default=20260901, alias="GLOBAL_SEED")
    output_dir: str = Field(default="experiments", alias="EXPERIMENT_OUTPUT_DIR")


class Settings(BaseSettings):
    """Punto único de acceso a la configuración."""

    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    experiment: ExperimentSettings = Field(default_factory=ExperimentSettings)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Configuración cacheada. ``get_settings.cache_clear()`` la recarga en tests."""
    return Settings()
