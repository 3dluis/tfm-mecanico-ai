"""Barrido del umbral de confianza sobre validación (E15b).

El criterio de selección está fijado y fechado en
``docs/methodology/criterio-umbral.md``, en un commit anterior al que produce este
artefacto. Aquí solo se ejecuta lo que allí se declaró.

**El conjunto de test no se toca.** Un umbral seleccionado con el test convertiría
la evaluación final en una descripción de lo ya visto.

Se reportan cobertura y precisión en dos unidades: por ventana, que es donde se
toma la decisión, y por sesión, que es la unidad de independencia real. Doce
sesiones de validación, dos por condición: presentar 98 ventanas como si fueran
98 observaciones independientes exageraría la precisión de cualquier lectura.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.dataset import load_partition
from mecanico_ia_exp.experiments.registro import escribir
from mecanico_ia_exp.models.baseline import BaselineConfig

#: Política declarada en `docs/methodology/criterio-umbral.md`: se acepta como
#: máximo un error de decisión de 7 entre 100 explicaciones emitidas.
PRECISION_OBJETIVO = 0.93

#: Paso del barrido. Fino a propósito: la curva es el artefacto, no cuatro puntos.
PASO = 0.01


def _calibrar(entrenamiento: Any, configuracion: BaselineConfig) -> Any:
    """Misma calibración que usa el verificador: isotónica, cv=5, sobre entrenamiento."""
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.ensemble import RandomForestClassifier

    base = RandomForestClassifier(
        n_estimators=configuracion.n_estimators,
        min_samples_leaf=configuracion.min_samples_leaf,
        class_weight=configuracion.class_weight,
        random_state=configuracion.seed,
        n_jobs=configuracion.n_jobs,
    )
    calibrado = CalibratedClassifierCV(base, method="isotonic", cv=5)
    calibrado.fit(entrenamiento.features, entrenamiento.y)
    return calibrado


def run_threshold_sweep(dataset_id: str = "synthetic_v2") -> int:
    """Recorre el rango de umbrales y aplica el criterio declarado."""
    entrenamiento = load_partition("train", dataset_id=dataset_id)
    validacion = load_partition("validation", dataset_id=dataset_id)
    configuracion = BaselineConfig()
    calibrado = _calibrar(entrenamiento, configuracion)

    prob = np.asarray(calibrado.predict_proba(validacion.features), dtype=np.float64)
    pred = np.asarray(calibrado.predict(validacion.features), dtype=validacion.y.dtype)
    confianza = prob.max(axis=1)
    aciertos = pred == validacion.y
    sesiones = np.asarray(validacion.meta["session_id"], dtype=object)
    n_sesiones = len(set(sesiones))

    print(
        f"validación: {len(confianza)} ventanas · {n_sesiones} sesiones · "
        f"acierto sin abstención {aciertos.mean():.4f}"
    )

    filas: list[dict[str, Any]] = []
    for umbral in np.arange(0.0, 1.0 + PASO / 2, PASO):
        cubierto = confianza >= umbral
        n_cub = int(cubierto.sum())
        # Por sesión: primero se agrega dentro de cada sesión, después se
        # promedia. Es la unidad de independencia; hacerlo al revés cuenta doce
        # trayectos como noventa y ocho observaciones.
        cob_s, pre_s = [], []
        for s in sorted(set(sesiones)):
            m = sesiones == s
            c = cubierto & m
            cob_s.append(float(c.sum() / max(int(m.sum()), 1)))
            if c.any():
                pre_s.append(float(aciertos[c].mean()))
        filas.append(
            {
                "threshold": round(float(umbral), 4),
                "coverage_windows": round(float(cubierto.mean()), 6),
                "precision_windows": (
                    round(float(aciertos[cubierto].mean()), 6) if n_cub else None
                ),
                "n_windows_covered": n_cub,
                "n_windows_total": len(confianza),
                "coverage_sessions": round(float(np.mean(cob_s)), 6),
                "precision_sessions": (round(float(np.mean(pre_s)), 6) if pre_s else None),
                "n_sessions_with_coverage": len(pre_s),
                "n_sessions_total": n_sesiones,
            }
        )

    curva = pd.DataFrame(filas)
    tablas = paths.ensure(paths.TABLES)
    curva.to_csv(tablas / "E15b_barrido_umbral.csv", index=False)

    # --- Aplicación del criterio declarado, sin tocarlo.
    elegibles = curva[
        curva["precision_windows"].notna() & (curva["precision_windows"] >= PRECISION_OBJETIVO)
    ]
    seleccionado = float(elegibles["threshold"].min()) if not elegibles.empty else None
    print(f"\ncriterio: umbral más bajo con precisión por ventana ≥ {PRECISION_OBJETIVO}")
    print(f"seleccionado: {seleccionado}")

    # --- Robustez: intervalo en que la decisión de cada ventana no cambia.
    # Las decisiones cambian solo cuando el umbral cruza una confianza observada.
    unicos = np.unique(np.round(confianza, 6))
    print(f"confianzas distintas en validación: {len(unicos)}")

    escribir(
        paths.ensure(paths.EXPERIMENTS) / "E15b_barrido_umbral.json",
        {
            "experiment_id": "E15b_threshold_sweep",
            "criterion": {
                "document": "docs/methodology/criterio-umbral.md",
                "rule": "umbral más bajo con precisión de decisión por ventana >= objetivo",
                "target_precision": PRECISION_OBJETIVO,
                "blind_preregistration": False,
                "note": (
                    "El criterio se fijó y registró antes de este barrido, pero después de "
                    "haber visto una tabla anterior de cuatro puntos. Se declara como "
                    "elección de política sobre una curva medida, no como pre-registro ciego."
                ),
            },
            "partition": "validation",
            "test_used": False,
            "n_windows": len(confianza),
            "n_sessions": n_sesiones,
            "accuracy_without_abstention": round(float(aciertos.mean()), 6),
            "selected_threshold": seleccionado,
            "distinct_confidences": len(unicos),
            "curve": filas,
        },
        seed=configuracion.seed,
        dataset_id=dataset_id,
        dataset_type="synthetic",
    )
    print("\ntabla    E15b_barrido_umbral.csv")
    print("registro experiments/E15b_barrido_umbral.json")
    return 0
