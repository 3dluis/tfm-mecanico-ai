"""La configuración se lee del entorno y no lleva credenciales embebidas."""

from __future__ import annotations

import pytest

from mecanico_ia_exp.config.settings import DatabaseSettings, LLMSettings, get_settings


def test_url_sin_credenciales_delega_en_autenticacion_local() -> None:
    ajustes = DatabaseSettings(host="localhost", port=5432, name="db", user="", password="")
    assert ajustes.url == "postgresql+psycopg://localhost:5432/db"


def test_url_incluye_usuario_y_contrasena_cuando_se_declaran() -> None:
    ajustes = DatabaseSettings(host="h", port=1, name="d", user="u", password="p")
    assert ajustes.url == "postgresql+psycopg://u:p@h:1/d"


def test_proveedor_llm_por_defecto_no_llama_a_la_red() -> None:
    assert LLMSettings().provider == "echo"


def test_temperatura_por_defecto_es_determinista() -> None:
    assert LLMSettings().temperature == 0.0


@pytest.mark.parametrize("atributo", ["database", "llm", "experiment"])
def test_settings_expone_las_tres_secciones(atributo: str) -> None:
    assert getattr(get_settings(), atributo) is not None
