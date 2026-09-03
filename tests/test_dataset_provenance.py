"""La procedencia del dato es obligatoria y cerrada (ADR-003).

La pregunta de investigación no exige que los datos sean reales; exige que cada
resultado diga sobre qué datos se obtuvo. Un valor fuera de la taxonomía es un
error, no una categoría nueva.
"""

from __future__ import annotations

from typing import get_args

import pytest
from pydantic import ValidationError

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.metadata import DatasetMetadata, DatasetType


def _ficha(tipo: str) -> DatasetMetadata:
    return DatasetMetadata(
        dataset_id="x",
        dataset_type=tipo,  # type: ignore[arg-type]
        source="prueba",
        version="0",
        sampling_rate_hz=1.0,
        vehicle_or_simulator="simulador de prueba",
    )


def test_la_taxonomia_es_exactamente_la_declarada() -> None:
    assert set(get_args(DatasetType)) == {"real", "synthetic", "simulated", "public_dataset"}


@pytest.mark.parametrize("tipo", ["real", "synthetic", "simulated", "public_dataset"])
def test_cada_procedencia_admitida_valida(tipo: str) -> None:
    assert _ficha(tipo).dataset_type == tipo


def test_una_procedencia_inventada_se_rechaza() -> None:
    """«real-ish», «mixed» o «REAL» no son categorías: hay que declarar una de las cuatro."""
    for tipo in ("mixed", "REAL", "real-ish", ""):
        with pytest.raises(ValidationError):
            _ficha(tipo)


def test_el_dataset_del_laboratorio_declara_su_procedencia() -> None:
    """Sin este registro, «resultados sobre synthetic_v2» no diría de qué datos habla."""
    ruta = paths.DATA_RAW_SYNTHETIC / "synthetic_v2.meta.json"
    if not ruta.is_file():
        pytest.skip("el dataset no está generado en esta máquina")
    meta = DatasetMetadata.read(ruta)
    assert meta.dataset_type == "synthetic"
    assert meta.seed == 20260901
    assert meta.source and meta.version and meta.created_at
