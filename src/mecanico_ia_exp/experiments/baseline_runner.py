"""Ejecución de E6: baseline y su referencia mínima.

Solo se usan entrenamiento y validación. El test permanece cerrado hasta E19, y
``load_partition`` lo impide por construcción.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.dataset import load_partition
from mecanico_ia_exp.evaluation.metrics import evaluate_classification
from mecanico_ia_exp.models.baseline import (
    BaselineConfig,
    train_baseline,
    train_majority_baseline,
)
from mecanico_ia_exp.obd.faults import FAULTS
from mecanico_ia_exp.visualization import modeling

DATASET = "synthetic_v2"


def run_baseline(dataset_id: str = DATASET) -> int:
    """Entrena el baseline, lo evalúa en validación y guarda los artefactos."""
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

    tablas = paths.ensure(paths.TABLES)
    informe.per_class.to_csv(tablas / "E6_baseline_por_clase.csv", index=False)
    informe.confusion.to_csv(tablas / "E6_baseline_confusion.csv")

    importancias = pd.DataFrame(
        {
            "feature": entrenamiento.feature_names,
            "importance": np.asarray(modelo.feature_importances_, dtype=np.float64),
        }
    ).sort_values("importance", ascending=False)
    importancias.to_csv(tablas / "E6_baseline_importancias.csv", index=False)

    experimentos = paths.ensure(paths.EXPERIMENTS)
    (experimentos / "E6_baseline.json").write_text(
        json.dumps(
            {
                "experiment_id": "E6_baseline",
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
    figuras = paths.ensure(paths.FIGURES)
    modeling.fig_confusion(
        informe.confusion,
        figuras / "FIG-E6-01_confusion_baseline.png",
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
        figuras / "FIG-E6-02_limite_evidencia_f03.png",
    )
    print("\nfigura  FIG-E6-01_confusion_baseline.png, FIG-E6-02_limite_evidencia_f03.png")

    print(
        "tabla   E6_baseline_por_clase.csv, E6_baseline_confusion.csv, E6_baseline_importancias.csv"
    )
    print("registro experiments/E6_baseline.json")
    return 0
