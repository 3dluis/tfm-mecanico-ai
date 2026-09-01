"""Baseline: bosque aleatorio sobre los descriptores por ventana.

Es la referencia contra la que se mide el modelo temporal. Si el modelo temporal
no lo supera, la complejidad añadida no está justificada y hay que decirlo.

Se acompaña de una referencia todavía más simple --predecir siempre la clase
mayoritaria-- porque un modelo que no supera eso no ha aprendido nada, y con un
reparto de 2:1 la exactitud de esa estrategia ya es del 28,6 %.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class BaselineConfig:
    """Hiperparámetros del baseline. Se registran con el modelo."""

    n_estimators: int = 400
    max_depth: int | None = None
    min_samples_leaf: int = 2
    # El reparto es 2:1 entre la clase normal y cada fallo (E5). Sin compensar,
    # el bosque optimiza la clase abundante y la exactitud global engaña.
    class_weight: str | None = "balanced"
    seed: int = 20260901
    n_jobs: int = -1


def train_baseline(
    x: npt.NDArray[np.float64], y: npt.NDArray[np.str_], config: BaselineConfig | None = None
) -> Any:
    """Entrena el bosque. Devuelve el estimador de scikit-learn."""
    from sklearn.ensemble import RandomForestClassifier

    cfg = config or BaselineConfig()
    modelo = RandomForestClassifier(
        n_estimators=cfg.n_estimators,
        max_depth=cfg.max_depth,
        min_samples_leaf=cfg.min_samples_leaf,
        class_weight=cfg.class_weight,
        random_state=cfg.seed,
        n_jobs=cfg.n_jobs,
    )
    modelo.fit(x, y)
    return modelo


def train_majority_baseline(y: npt.NDArray[np.str_]) -> str:
    """Referencia mínima: la clase mayoritaria del entrenamiento."""
    valores, cuentas = np.unique(y, return_counts=True)
    return str(valores[int(np.argmax(cuentas))])
