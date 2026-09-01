"""Ejecución de E7: modelo temporal y su comparación con el baseline.

Solo entrenamiento y validación. El test sigue cerrado.
"""

from __future__ import annotations

import json
import time

import numpy as np

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.dataset import load_partition
from mecanico_ia_exp.evaluation.metrics import evaluate_classification
from mecanico_ia_exp.models.temporal import TemporalConfig
from mecanico_ia_exp.models.training import train_temporal
from mecanico_ia_exp.visualization import modeling

DATASET = "synthetic_v2"


def run_temporal(dataset_id: str = DATASET) -> int:
    """Entrena la GRU, la evalúa en validación y la contrasta con el baseline."""
    entrenamiento = load_partition("train", dataset_id=dataset_id)
    validacion = load_partition("validation", dataset_id=dataset_id)
    clases = tuple(sorted(set(entrenamiento.y.tolist())))

    configuracion = TemporalConfig()
    inicio = time.perf_counter()
    entrenado = train_temporal(
        entrenamiento.x,
        entrenamiento.y,
        validacion.x,
        validacion.y,
        classes=clases,
        config=configuracion,
    )
    segundos = time.perf_counter() - inicio

    print(
        f"\ndispositivo: {entrenado.device} · {entrenado.n_parameters} parámetros · "
        f"{segundos:.1f} s"
    )
    print(
        f"mejor época {entrenado.history.best_epoch} de "
        f"{len(entrenado.history.val_macro_f1)} ejecutadas"
        + (" (parada temprana)" if entrenado.history.stopped_early else "")
    )

    probabilidades = entrenado.predict_proba(validacion.x)
    predicciones = entrenado.predict(validacion.x)
    informe = evaluate_classification(
        validacion.y,
        predicciones,
        partition="validation",
        probabilities=probabilidades,
        class_order=clases,
    )

    print("\nGRU bidireccional:")
    print(informe)
    print(
        f"\ncalibración: ECE {informe.calibration['ece']:.3f} · "
        f"confianza media {informe.calibration['mean_confidence']:.3f} · "
        f"acierto {informe.calibration['accuracy']:.3f} · "
        f"exceso de confianza {informe.calibration['overconfidence']:+.3f}"
    )

    # Comparación con el baseline ya registrado. No se reentrena: se lee su
    # registro, que es la cifra publicada en E6.
    registro_baseline = paths.EXPERIMENTS / f"E6_baseline_{dataset_id}.json"
    referencia: dict[str, float] = {}
    if registro_baseline.is_file():
        datos = json.loads(registro_baseline.read_text(encoding="utf-8"))
        referencia = {
            "macro_f1": float(datos["metrics"]["macro_f1"]),
            "accuracy": float(datos["metrics"]["accuracy"]),
        }
        diferencia = informe.macro_f1 - referencia["macro_f1"]
        veredicto = (
            "supera al baseline"
            if diferencia > 0
            else "NO supera al baseline: la complejidad añadida no está justificada"
        )
        print(
            f"\nbaseline F1 macro {referencia['macro_f1']:.3f} · "
            f"temporal {informe.macro_f1:.3f} · diferencia {diferencia:+.3f}"
            f"\n{veredicto}"
        )

    tablas = paths.ensure(paths.TABLES)
    informe.per_class.to_csv(tablas / f"E7_temporal_por_clase_{dataset_id}.csv", index=False)
    informe.confusion.to_csv(tablas / f"E7_temporal_confusion_{dataset_id}.csv")

    figuras = paths.ensure(paths.FIGURES)
    modeling.fig_confusion(
        informe.confusion,
        figuras / "FIG-E7-01_confusion_temporal.png",
        "GRU bidireccional sobre validación",
    )
    modeling.fig_curvas_entrenamiento(
        entrenado.history.train_loss,
        entrenado.history.val_loss,
        entrenado.history.val_macro_f1,
        entrenado.history.best_epoch,
        figuras / "FIG-E7-02_entrenamiento.png",
    )

    experimentos = paths.ensure(paths.EXPERIMENTS)
    (experimentos / f"E7_temporal_{dataset_id}.json").write_text(
        json.dumps(
            {
                "experiment_id": "E7_temporal",
                "dataset_id": dataset_id,
                "model": "GRU bidireccional",
                "device": entrenado.device,
                "n_parameters": entrenado.n_parameters,
                "training_seconds": round(segundos, 2),
                "config": {
                    "hidden_size": configuracion.hidden_size,
                    "num_layers": configuracion.num_layers,
                    "dropout": configuracion.dropout,
                    "bidirectional": configuracion.bidirectional,
                    "learning_rate": configuracion.learning_rate,
                    "weight_decay": configuracion.weight_decay,
                    "batch_size": configuracion.batch_size,
                    "max_epochs": configuracion.max_epochs,
                    "patience": configuracion.patience,
                    "seed": configuracion.seed,
                },
                "best_epoch": entrenado.history.best_epoch,
                "epochs_run": len(entrenado.history.val_macro_f1),
                "stopped_early": entrenado.history.stopped_early,
                "baseline_reference": referencia,
                "metrics": informe.to_dict(),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    np.save(paths.ensure(paths.MODELS) / "E7_standardizer_mean.npy", entrenado.standardizer.mean)
    np.save(paths.ensure(paths.MODELS) / "E7_standardizer_scale.npy", entrenado.standardizer.scale)

    print("\nfigura  FIG-E7-01_confusion_temporal.png, FIG-E7-02_entrenamiento.png")
    print("tabla   E7_temporal_por_clase.csv, E7_temporal_confusion.csv")
    print(f"registro experiments/E7_temporal_{dataset_id}.json")
    return 0
