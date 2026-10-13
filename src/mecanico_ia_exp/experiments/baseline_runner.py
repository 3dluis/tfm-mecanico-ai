"""Ejecución de E6: baseline y su referencia mínima.

Solo se usan entrenamiento y validación. El test permanece cerrado hasta E19, y
``load_partition`` lo impide por construcción.

**Sobre los destinos.** Este ejecutor escribía en seis rutas fijas --un registro,
tres tablas y dos figuras--, que son los artefactos publicados de E6. Reejecutarlo
para obtener predicciones por ventana los habría sobrescrito, de modo que la
verificación habría destruido la evidencia que verifica. Ahora toda ejecución
lleva **etiqueta**: sin ella se conservan los nombres históricos y la ejecución
**se niega a escribir** si ya existen; con ella, los seis artefactos van a rutas
propias y el registro declara de qué protocolo salen.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.dataset import load_partition
from mecanico_ia_exp.evaluation.metrics import evaluate_classification
from mecanico_ia_exp.experiments.destinos import exigir_libres
from mecanico_ia_exp.models.baseline import (
    BaselineConfig,
    train_baseline,
    train_majority_baseline,
)
from mecanico_ia_exp.obd.faults import FAULTS
from mecanico_ia_exp.visualization import modeling

DATASET = "synthetic_v2"

#: Protocolo del que salen las cifras publicadas de E6: bosque **sin calibrar**,
#: con el ECE calculado sobre ``predict_proba`` en crudo. Se nombra para que una
#: ejecución con otro protocolo no se confunda con esta.
PROTOCOLO_HISTORICO = "E6_v1_bosque_sin_calibrar"


def destinos_de(dataset_id: str, etiqueta: str = "") -> dict[str, Path]:
    """Los seis artefactos que una ejecución escribe, más el de por ventana.

    Juntos y antes de escribir el primero, porque es la única forma de
    comprobar que ninguno pisa a un artefacto anterior.
    """
    sufijo = f"_{etiqueta}" if etiqueta else ""
    base = f"E6{sufijo}"
    return {
        "registro": paths.EXPERIMENTS / f"{base}_baseline_{dataset_id}.json",
        "tabla_por_clase": paths.TABLES / f"{base}_baseline_por_clase_{dataset_id}.csv",
        "tabla_confusion": paths.TABLES / f"{base}_baseline_confusion_{dataset_id}.csv",
        "tabla_importancias": paths.TABLES / f"{base}_baseline_importancias_{dataset_id}.csv",
        "figura_confusion": paths.FIGURES / f"FIG-{base}-01_confusion_baseline.png",
        "figura_limite": paths.FIGURES / f"FIG-{base}-02_limite_evidencia_f03.png",
        "por_ventana": paths.TABLES / f"{base}_predicciones_por_ventana_{dataset_id}.csv",
    }


def run_baseline(
    dataset_id: str = DATASET,
    *,
    etiqueta: str = "",
    por_ventana: bool = False,
) -> int:
    """Entrena el baseline, lo evalúa en validación y guarda los artefactos.

    ``etiqueta`` identifica la ejecución y entra en el nombre de **todos** los
    artefactos. ``por_ventana`` añade la predicción de cada ventana con su
    sesión y su temperatura media, que es lo que permite cruzar los errores del
    termostato con la expresión efectiva del fallo en lugar de inferirla de
    estadísticos agregados.
    """
    destinos = destinos_de(dataset_id, etiqueta)
    if not por_ventana:
        destinos.pop("por_ventana")
    exigir_libres(destinos)

    entrenamiento = load_partition("train", dataset_id=dataset_id)
    validacion = load_partition("validation", dataset_id=dataset_id)
    clases = tuple(sorted(set(entrenamiento.y.tolist())))

    print(
        f"entrenamiento: {len(entrenamiento)} ventanas · "
        f"validación: {len(validacion)} ventanas · "
        f"{len(entrenamiento.feature_names)} descriptores"
    )

    # Referencia mínima: siempre la clase mayoritaria.
    mayoritaria = train_majority_baseline(entrenamiento.y)
    informe_trivial = evaluate_classification(
        validacion.y,
        # El dtype se toma del propio vector de etiquetas: np.str_ a secas
        # produce "<U1" y trunca los identificadores a su primera letra.
        np.full(validacion.y.shape, mayoritaria, dtype=validacion.y.dtype),
        partition="validation",
        class_order=clases,
    )

    configuracion = BaselineConfig()
    modelo = train_baseline(entrenamiento.features, entrenamiento.y, configuracion)
    probabilidades = np.asarray(modelo.predict_proba(validacion.features), dtype=np.float64)
    # El orden de columnas de predict_proba lo fija el modelo; se reordena al
    # orden declarado en lugar de suponer que coinciden.
    orden = [list(modelo.classes_).index(c) for c in clases]
    probabilidades = probabilidades[:, orden]
    predicciones = np.asarray(modelo.predict(validacion.features), dtype=np.str_)

    informe = evaluate_classification(
        validacion.y,
        predicciones,
        partition="validation",
        probabilities=probabilidades,
        class_order=clases,
    )

    print(f"\nReferencia mínima (siempre «{mayoritaria}»):")
    print(f"  exactitud {informe_trivial.accuracy:.3f} · F1 macro {informe_trivial.macro_f1:.3f}")
    print("\nBosque aleatorio:")
    print(informe)
    print(
        f"\ncalibración: ECE {informe.calibration['ece']:.3f} · "
        f"confianza media {informe.calibration['mean_confidence']:.3f} · "
        f"acierto {informe.calibration['accuracy']:.3f} · "
        f"exceso de confianza {informe.calibration['overconfidence']:+.3f}"
    )
    print("\nMatriz de confusión (filas = verdad, columnas = predicción):")
    print(
        informe.confusion.rename(index=lambda s: s.split("_", 1)[0])
        .rename(columns=lambda s: s.split("_", 1)[0])
        .to_string()
    )

    paths.ensure(paths.TABLES)
    informe.per_class.to_csv(destinos["tabla_por_clase"], index=False)
    informe.confusion.to_csv(destinos["tabla_confusion"])

    importancias = pd.DataFrame(
        {
            "feature": entrenamiento.feature_names,
            "importance": np.asarray(modelo.feature_importances_, dtype=np.float64),
        }
    ).sort_values("importance", ascending=False)
    importancias.to_csv(destinos["tabla_importancias"], index=False)

    if por_ventana:
        pd.DataFrame(
            {
                "session_id": validacion.meta["session_id"].to_numpy(),
                "t_start": validacion.meta["t_start"].to_numpy(),
                "t_end": validacion.meta["t_end"].to_numpy(),
                "y_true": validacion.y,
                "y_pred": predicciones,
                "coolant_temperature_mean": validacion.features[
                    :, entrenamiento.feature_names.index("coolant_temperature_mean")
                ],
            }
        ).to_csv(destinos["por_ventana"], index=False)

    paths.ensure(paths.EXPERIMENTS)
    destinos["registro"].write_text(
        json.dumps(
            {
                "experiment_id": "E6_baseline",
                "protocolo": PROTOCOLO_HISTORICO,
                "etiqueta": etiqueta or None,
                "dataset_id": dataset_id,
                "model": "RandomForestClassifier",
                "config": {
                    "n_estimators": configuracion.n_estimators,
                    "max_depth": configuracion.max_depth,
                    "min_samples_leaf": configuracion.min_samples_leaf,
                    "class_weight": configuracion.class_weight,
                    "seed": configuracion.seed,
                },
                "n_features": len(entrenamiento.feature_names),
                "n_train": len(entrenamiento),
                "n_validation": len(validacion),
                "majority_class": mayoritaria,
                "majority_baseline": informe_trivial.to_dict(),
                "metrics": informe.to_dict(),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    paths.ensure(paths.FIGURES)
    modeling.fig_confusion(
        informe.confusion,
        destinos["figura_confusion"],
        "Bosque aleatorio sobre validación",
    )

    # El termostato bloqueado impone un techo de temperatura: mientras el motor
    # no lo habría superado por sí mismo, el fallo no deja firma alguna. Se
    # comprueba si los errores del modelo se concentran justo ahí.
    columna = entrenamiento.feature_names.index("coolant_temperature_mean")
    es_f03 = validacion.y == "F03_thermostat_stuck"
    modeling.fig_limite_de_evidencia(
        validacion.features[es_f03, columna],
        predicciones[es_f03] == "F03_thermostat_stuck",
        FAULTS["F03_thermostat_stuck"].default_params["temp_cap_c"],
        destinos["figura_limite"],
    )

    for clave, ruta in sorted(destinos.items()):
        print(f"{clave:20s} {ruta.relative_to(paths.ROOT)}")
    return 0
