"""La procedencia del dato es obligatoria y cerrada (ADR-003).

La pregunta de investigación no exige que los datos sean reales; exige que cada
resultado diga sobre qué datos se obtuvo. Un valor fuera de la taxonomía es un
error, no una categoría nueva.
"""

from __future__ import annotations

from pathlib import Path
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


# ------------------------------------------- cabecera de registro (RX-00)


def test_todo_registro_declara_de_qué_ejecución_habla() -> None:
    """Sin commit ni fecha, dos ejecuciones son indistinguibles desde el registro.

    Es lo que hizo invisibles las sobrescrituras de tres fases: el informe
    publicaba una ejecución y el árbol contenía otra, y nada en el fichero lo
    delataba.
    """
    from mecanico_ia_exp.experiments.registro import CAMPOS_OBLIGATORIOS, cabecera

    datos = cabecera("E15_sufficiency", seed=20260901, dataset_id="synthetic_v2")
    assert set(datos) >= CAMPOS_OBLIGATORIOS
    assert datos["experiment_id"] == "E15_sufficiency"
    assert datos["seed"] == 20260901
    # El estado del árbol se declara: un registro escrito con cambios sin
    # confirmar no es reproducible desde el commit que dice.
    assert "dirty" in datos


def test_el_registro_se_escribe_con_la_cabecera_delante(tmp_path: Path) -> None:
    import json

    from mecanico_ia_exp.experiments.registro import escribir

    destino = escribir(tmp_path / "r.json", {"experiment_id": "E99", "metrics": {"f1": 0.5}})
    datos = json.loads(destino.read_text(encoding="utf-8"))
    assert next(iter(datos)) == "experiment_id"
    assert datos["metrics"] == {"f1": 0.5}
