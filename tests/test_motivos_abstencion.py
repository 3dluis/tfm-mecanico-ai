"""El recuento fino de los motivos de abstención debe ser estable y clasificado.

La cifra que la memoria publica —cinco de veintiséis abstenciones de la evaluación
final con una discrepancia numérica— sale de alinear motivo con motivo, y no del
conjunto agrupado de números del caso. Esa diferencia es justo lo que estos tests
fijan: si alguien vuelve a agrupar, el recuento baja a tres y el test lo detecta.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest


def _cargar() -> ModuleType:
    ruta = Path(__file__).resolve().parents[1] / "scripts" / "auditar_motivos_abstencion.py"
    especificacion = importlib.util.spec_from_file_location("auditar_motivos_abstencion", ruta)
    assert especificacion is not None and especificacion.loader is not None
    modulo = importlib.util.module_from_spec(especificacion)
    sys.modules["auditar_motivos_abstencion"] = modulo
    especificacion.loader.exec_module(modulo)
    return modulo


@pytest.fixture(scope="module")
def guion() -> ModuleType:
    return _cargar()


def test_un_umbral_mal_citado_se_clasifica_como_umbral_erroneo(guion: ModuleType) -> None:
    hallazgos = guion._comparar(
        "caso",
        ["confianza 0.573 < 0.79"],
        ["confianza 0.573 < 0.80"],
    )
    assert [h.clase for h in hallazgos] == ["UMBRAL_ERRONEO"]


def test_un_valor_inventado_se_clasifica_como_valor_sin_origen(guion: ModuleType) -> None:
    hallazgos = guion._comparar(
        "caso",
        ["cobertura 0.00 < 0.80"],
        ["cobertura 0.852 < 0.90"],
    )
    assert [h.clase for h in hallazgos] == ["VALOR_SIN_ORIGEN"]


def test_el_umbral_ajeno_no_se_pierde_por_figurar_en_otro_motivo(guion: ModuleType) -> None:
    """El punto ciego que motivó el guion: 0,80 está en el motivo de cobertura."""
    hallazgos = guion._comparar(
        "caso",
        ["confianza 0.490 < 0.79", "cobertura 0.00 < 0.80"],
        ["confianza 0.49 < 0.80"],
    )
    clases = sorted(h.clase for h in hallazgos)
    assert clases == ["MOTIVO_OMITIDO", "UMBRAL_ERRONEO"]


def test_una_frase_sin_cifras_anadida_no_cuenta_como_discrepancia_numerica(
    guion: ModuleType,
) -> None:
    hallazgos = guion._comparar(
        "caso",
        ["cobertura 0.00 < 0.80"],
        ["ningún fragmento documental aplicable a este vehículo", "cobertura 0.00 < 0.80"],
    )
    assert [h.clase for h in hallazgos] == ["MOTIVO_SIN_CIFRAS"]


def test_motivos_identicos_no_producen_hallazgos(guion: ModuleType) -> None:
    motivos = ["confianza 0.573 < 0.79", "cobertura 0.00 < 0.80"]
    assert guion._comparar("caso", motivos, list(motivos)) == []


def test_el_recuento_de_la_evaluacion_final_es_el_publicado(guion: ModuleType) -> None:
    recuento = guion.auditar()
    assert recuento.abstenciones == 26
    assert recuento.con_discrepancia_numerica == 5
    assert recuento.con_discrepancia_de_cualquier_tipo == 16
