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
import numpy.typing as npt
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

#: Anchura mínima de la meseta que exige la enmienda ENM-U01
#: (`docs/methodology/criterio-umbral-enmienda-01.md`). Un umbral es estable si él
#: y todos los de la rejilla hasta `t + ANCHURA_ESTABLE` alcanzan la precisión
#: objetivo. Con 98 ventanas, 0,05 en la escala de confianza mueve en torno al 5 %
#: de la muestra: un punto que no sobrevive a eso lo determina un puñado de
#: observaciones, no la forma de la curva.
ANCHURA_ESTABLE = 0.05

#: Remuestreos del análisis de sensibilidad, por sesión. Caracteriza la robustez
#: del punto elegido; **no** se usa para elegirlo.
N_REMUESTREOS = 1000


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

    # --- Criterio original, conservado tal cual. Su resultado se publica aunque
    # la enmienda seleccione otro punto: ocultarlo sería reescribir el pasado.
    cumple = curva["precision_windows"].notna() & (curva["precision_windows"] >= PRECISION_OBJETIVO)
    elegibles = curva[cumple]
    original = float(elegibles["threshold"].min()) if not elegibles.empty else None
    print(f"\ncriterio original: umbral más bajo con precisión ≥ {PRECISION_OBJETIVO}")
    print(f"  seleccionado: {original}")

    # --- Enmienda ENM-U01: estabilidad. Un umbral es estable si él y todos los de
    # la rejilla hasta t + ANCHURA_ESTABLE cumplen el objetivo.
    umbrales = curva["threshold"].to_numpy()
    ok = cumple.to_numpy()
    n_ventana = round(ANCHURA_ESTABLE / PASO) + 1
    estable = np.array(
        [bool(ok[i : i + n_ventana].all()) and i + n_ventana <= len(ok) for i in range(len(ok))]
    )
    curva["cumple_objetivo"] = ok
    curva["estable"] = estable
    indices = np.flatnonzero(estable)
    revisado = float(umbrales[indices[0]]) if indices.size else None
    print(f"enmienda ENM-U01: estable si [t, t+{ANCHURA_ESTABLE}] cumple entero")
    print(f"  seleccionado: {revisado}")
    if revisado is None:
        # E-3: la regla no se relaja. Se reporta la ausencia.
        print("  ningún umbral es estable: la decisión escala al autor (E-3)")

    # --- Tramos elegibles, para que la fragilidad sea legible en el artefacto.
    tramos: list[dict[str, Any]] = []
    inicio: float | None = None
    for i, valor in enumerate(ok):
        if valor and inicio is None:
            inicio = float(umbrales[i])
        elif not valor and inicio is not None:
            tramos.append(
                {
                    "from": inicio,
                    "to": float(umbrales[i - 1]),
                    "width": round(float(umbrales[i - 1]) - inicio, 4),
                }
            )
            inicio = None
    if inicio is not None:
        tramos.append(
            {
                "from": inicio,
                "to": float(umbrales[-1]),
                "width": round(float(umbrales[-1]) - inicio, 4),
            }
        )
    print(f"  tramos que cumplen el objetivo: {tramos}")

    # --- Robustez: intervalo en que la decisión de cada ventana no cambia.
    unicos = np.unique(np.round(confianza, 6))
    print(f"confianzas distintas en validación: {len(unicos)}")

    # --- Sensibilidad por remuestreo de sesiones. Caracteriza, no selecciona.
    sensibilidad = _sensibilidad(
        confianza, aciertos, sesiones, [t for t in (original, revisado) if t is not None]
    )
    for punto, datos in sensibilidad.items():
        print(
            f"  sensibilidad t={punto}: precisión mediana {datos['precision_median']:.4f} "
            f"[{datos['precision_p05']:.4f}, {datos['precision_p95']:.4f}] · "
            f"cumple el objetivo en el {datos['share_meeting_target']:.0%} de los remuestreos"
        )

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
            "original_criterion_threshold": original,
            "amended_criterion_threshold": revisado,
            "amendment": {
                "id": "ENM-U01",
                "document": "docs/methodology/criterio-umbral-enmienda-01.md",
                "rule": "estable si [t, t+w] cumple el objetivo en toda la rejilla",
                "w": ANCHURA_ESTABLE,
                "written_after_first_sweep": True,
            },
            "eligible_runs": tramos,
            "sensitivity": sensibilidad,
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


def _sensibilidad(
    confianza: npt.NDArray[np.float64],
    aciertos: npt.NDArray[np.bool_],
    sesiones: npt.NDArray[Any],
    puntos: list[float],
    *,
    n: int = N_REMUESTREOS,
    seed: int = 20260901,
) -> dict[str, dict[str, float]]:
    """Remuestrea **sesiones**, no ventanas, y describe cuánto varía cada punto.

    La unidad de independencia es la sesión: remuestrear ventanas trataría doce
    trayectos como noventa y ocho observaciones y estrecharía artificialmente el
    intervalo.

    Esto **caracteriza** la robustez del punto ya elegido. No lo elige: la
    elección la fijan E-1 y E-2 de la enmienda, y ninguna cifra de aquí puede
    cambiarla.
    """
    rng = np.random.default_rng(seed)
    unicas = sorted(set(sesiones))
    indices_por_sesion = {s: np.flatnonzero(sesiones == s) for s in unicas}
    salida: dict[str, dict[str, float]] = {}
    for punto in puntos:
        precisiones, coberturas = [], []
        for _ in range(n):
            elegidas = rng.choice(len(unicas), size=len(unicas), replace=True)
            idx = np.concatenate([indices_por_sesion[unicas[k]] for k in elegidas])
            cubierto = confianza[idx] >= punto
            coberturas.append(float(cubierto.mean()))
            if cubierto.any():
                precisiones.append(float(aciertos[idx][cubierto].mean()))
        arr = np.asarray(precisiones)
        salida[f"{punto:.2f}"] = {
            "precision_median": round(float(np.median(arr)), 6),
            "precision_p05": round(float(np.percentile(arr, 5)), 6),
            "precision_p95": round(float(np.percentile(arr, 95)), 6),
            "coverage_median": round(float(np.median(coberturas)), 6),
            "share_meeting_target": round(float((arr >= PRECISION_OBJETIVO).mean()), 6),
            "n_resamples": float(len(arr)),
        }
    return salida
