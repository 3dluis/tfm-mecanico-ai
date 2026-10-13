"""Ejecución de E7: modelo temporal y su comparación con el baseline.

Solo entrenamiento y validación. El test sigue cerrado.

**Dos salvedades sobre lo que este ejecutor mide.** La primera, que la época se
elige mirando la misma partición de validación sobre la que después se reporta:
el bosque no tiene paso de selección equivalente, así que la comparación entre
los dos no es simétrica. La segunda, que ninguno de los dos calibra --el error de
calibración sale de ``predict_proba`` en crudo--, de modo que la diferencia de
ECE publicada no es una diferencia entre calibradores. Las dos se corrigen en el
protocolo de PI.1, con tres particiones internas
(``data/interno.py``), y ese protocolo **no sobrescribe** estas cifras: escribe
con etiqueta propia.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.dataset import load_partition
from mecanico_ia_exp.evaluation.metrics import evaluate_classification
from mecanico_ia_exp.experiments.destinos import exigir_libres
from mecanico_ia_exp.models.temporal import TemporalConfig
from mecanico_ia_exp.models.training import train_temporal
from mecanico_ia_exp.visualization import modeling

DATASET = "synthetic_v2"

#: Protocolo del que salen las cifras publicadas de E7: época elegida sobre la
#: validación que se reporta y red **sin calibrar**.
PROTOCOLO_HISTORICO = "E7_v1_epoca_sobre_validacion_sin_calibrar"


def destinos_de(dataset_id: str, etiqueta: str = "") -> dict[str, Path]:
    """Los artefactos que una ejecución escribe, antes de escribir el primero."""
    sufijo = f"_{etiqueta}" if etiqueta else ""
    base = f"E7{sufijo}"
    return {
        "registro": paths.EXPERIMENTS / f"{base}_temporal_{dataset_id}.json",
        "tabla_por_clase": paths.TABLES / f"{base}_temporal_por_clase_{dataset_id}.csv",
        "tabla_confusion": paths.TABLES / f"{base}_temporal_confusion_{dataset_id}.csv",
        "figura_confusion": paths.FIGURES / f"FIG-{base}-01_confusion_temporal.png",
        "figura_entrenamiento": paths.FIGURES / f"FIG-{base}-02_entrenamiento.png",
        "normalizador_media": paths.MODELS / f"{base}_standardizer_mean.npy",
        "normalizador_escala": paths.MODELS / f"{base}_standardizer_scale.npy",
    }


def run_temporal(dataset_id: str = DATASET, *, etiqueta: str = "") -> int:
    """Entrena la GRU, la evalúa en validación y la contrasta con el baseline.

    ``etiqueta`` entra en el nombre de todos los artefactos. Sin ella se
    conservan los nombres históricos y la ejecución **se niega a escribir** si ya
    existen, porque las cifras de E7 son evidencia publicada.
    """
    destinos = exigir_libres(destinos_de(dataset_id, etiqueta))
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

    paths.ensure(paths.TABLES)
    informe.per_class.to_csv(destinos["tabla_por_clase"], index=False)
    informe.confusion.to_csv(destinos["tabla_confusion"])

    paths.ensure(paths.FIGURES)
    modeling.fig_confusion(
        informe.confusion,
        destinos["figura_confusion"],
        "GRU bidireccional sobre validación",
    )
    modeling.fig_curvas_entrenamiento(
        entrenado.history.train_loss,
        entrenado.history.val_loss,
        entrenado.history.val_macro_f1,
        entrenado.history.best_epoch,
        destinos["figura_entrenamiento"],
    )

    paths.ensure(paths.EXPERIMENTS)
    destinos["registro"].write_text(
        json.dumps(
            {
                "experiment_id": "E7_temporal",
                "protocolo": PROTOCOLO_HISTORICO,
                "etiqueta": etiqueta or None,
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
    paths.ensure(paths.MODELS)
    np.save(destinos["normalizador_media"], entrenado.standardizer.mean)
    np.save(destinos["normalizador_escala"], entrenado.standardizer.scale)

    for clave, ruta in sorted(destinos.items()):
        print(f"{clave:22s} {ruta.relative_to(paths.ROOT)}")
    return 0
