"""Carga del conjunto ya preprocesado, con el test bajo llave.

El conjunto de test permanece cerrado hasta la evaluación final (E19). No es una
formalidad: si los umbrales de suficiencia o la elección de modelo se ajustan
mirando el test, las cifras finales dejan de ser una predicción y pasan a ser una
descripción de datos ya vistos.

La disciplina no se confía a la memoria de quien escribe el código. Pedir la
partición de test exige pasar ``allow_test=True`` **y** una razón por escrito, que
queda registrada. Un descuido produce una excepción, no un resultado inválido.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import numpy.typing as npt
import pandas as pd

from mecanico_ia_exp.config import paths

Particion = Literal["train", "validation", "test"]

#: Fase a partir de la cual el test deja de estar cerrado.
FASE_APERTURA_TEST = "E19"


@dataclass(frozen=True)
class Dataset:
    """Ventanas, descriptores y metadatos de una partición."""

    x: npt.NDArray[np.float32]
    """(n, pasos, señales) — series crudas, para el modelo temporal."""
    features: npt.NDArray[np.float64]
    """(n, 139) — descriptores, para el baseline."""
    y: npt.NDArray[np.str_]
    meta: pd.DataFrame
    partition: str
    feature_names: tuple[str, ...]

    def __len__(self) -> int:
        return int(self.features.shape[0])


class LockedPartitionError(RuntimeError):
    """Se ha intentado leer una partición cerrada sin declararlo explícitamente."""


def _rutas(dataset_id: str) -> tuple[Path, Path, Path, Path]:
    base = paths.DATA_PROCESSED
    return (
        base / f"{dataset_id}_x.npy",
        base / f"{dataset_id}_features.npy",
        base / f"{dataset_id}_meta.parquet",
        base / f"{dataset_id}_preprocess.json",
    )


def load_partition(
    partition: Particion,
    *,
    dataset_id: str = "synthetic_v2",
    allow_test: bool = False,
    reason: str = "",
) -> Dataset:
    """Carga una partición.

    Para ``partition="test"`` hay que pasar ``allow_test=True`` y una ``reason``
    no vacía, que se imprime. Así queda constancia de cada apertura del test en
    la salida de la ejecución que la hizo.
    """
    if partition == "test":
        if not allow_test or not reason.strip():
            msg = (
                "El conjunto de test está cerrado hasta "
                f"{FASE_APERTURA_TEST}. Para abrirlo hay que pasar allow_test=True "
                "y una razón por escrito. Si estás calibrando o eligiendo modelo, "
                "usa la partición de validación."
            )
            raise LockedPartitionError(msg)
        print(f"[TEST ABIERTO] {reason}")

    ruta_x, ruta_f, ruta_meta, ruta_cfg = _rutas(dataset_id)
    for ruta in (ruta_x, ruta_f, ruta_meta, ruta_cfg):
        if not ruta.is_file():
            msg = f"Falta {ruta.name}. Ejecuta antes: mecanico-exp preprocess"
            raise FileNotFoundError(msg)

    meta = pd.read_parquet(ruta_meta)
    mascara = (meta["partition"] == partition).to_numpy(dtype=bool)
    if not mascara.any():
        msg = f"La partición {partition!r} no contiene ninguna ventana"
        raise ValueError(msg)

    configuracion = json.loads(ruta_cfg.read_text(encoding="utf-8"))
    return Dataset(
        x=np.load(ruta_x)[mascara],
        features=np.load(ruta_f)[mascara],
        y=meta.loc[mascara, "label"].to_numpy(dtype=np.str_),
        meta=meta.loc[mascara].reset_index(drop=True),
        partition=partition,
        feature_names=tuple(configuracion["feature_names"]),
    )
