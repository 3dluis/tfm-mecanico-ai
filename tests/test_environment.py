"""La auditoría del entorno informa; no modifica la máquina ni oculta fallbacks."""

from __future__ import annotations

from mecanico_ia_exp.config.environment import (
    audit,
    check_platform,
    check_python,
    resolve_device,
)


def test_auditoria_sin_base_de_datos_no_consulta_postgres() -> None:
    informe = audit(include_database=False)
    nombres = {c.name for c in informe.checks}
    assert nombres == {"python", "plataforma", "torch"}


def test_interprete_es_3_11() -> None:
    assert check_python().ok, check_python().detail


def test_plataforma_se_reporta_siempre() -> None:
    assert check_platform().detail


def test_dispositivo_nunca_es_cuda() -> None:
    assert resolve_device() in {"mps", "cpu"}


def test_informe_serializa_a_diccionario() -> None:
    datos = audit(include_database=False).to_dict()
    assert set(datos) == {"ok", "checks"}
    assert all(set(c) == {"name", "ok", "detail"} for c in datos["checks"])
