"""Ejecución de E9: atribución sobre el modelo especializado.

Solo entrenamiento y validación. El fondo sale exclusivamente de entrenamiento.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.dataset import load_partition
from mecanico_ia_exp.experiments.destinos import exigir_libres
from mecanico_ia_exp.models.baseline import BaselineConfig, train_baseline
from mecanico_ia_exp.obd.faults import FAULTS, NORMAL_ID
from mecanico_ia_exp.xai.attribution import (
    FUNCION_EXPLICADA,
    explain_cases,
    select_background,
)

DATASET = "synthetic_v2"
#: Casos a explicar por condición. La atribución por permutación es costosa y no
#: hace falta explicar cada ventana para caracterizar una condición.
POR_CONDICION = 3


def destinos_de(dataset_id: str, etiqueta: str = "") -> dict[str, Path]:
    """Los tres artefactos de E9, antes de escribir el primero."""
    sufijo = f"_{etiqueta}" if etiqueta else ""
    return {
        "registro": paths.EXPERIMENTS / f"E9_xai_{dataset_id}{sufijo}.json",
        "tabla_atribuciones": paths.TABLES / f"E9_atribuciones_{dataset_id}{sufijo}.csv",
        "tabla_resumen": paths.TABLES / f"E9_resumen_{dataset_id}{sufijo}.csv",
    }


def run_xai(dataset_id: str = DATASET, *, etiqueta: str = "") -> int:
    destinos = exigir_libres(destinos_de(dataset_id, etiqueta))
    entrenamiento = load_partition("train", dataset_id=dataset_id)
    validacion = load_partition("validation", dataset_id=dataset_id)

    configuracion = BaselineConfig()
    modelo = train_baseline(entrenamiento.features, entrenamiento.y, configuracion)
    model_id = f"rf_{dataset_id}_seed{configuracion.seed}"

    fondo, huella = select_background(
        entrenamiento.features,
        entrenamiento.y,
        normal_label=NORMAL_ID,
        n=100,
        seed=configuracion.seed,
    )
    print(f"función explicada : {FUNCION_EXPLICADA}")
    print(f"fondo             : {fondo.shape[0]} ventanas normales de entrenamiento")
    print(f"huella del fondo  : {huella}")

    # Se eligen casos correctamente clasificados: explicar un acierto responde a
    # «por qué el modelo cree esto»; explicar un error mezcla dos preguntas.
    predicciones = np.asarray(modelo.predict(validacion.features), dtype=np.str_)
    aciertos = predicciones == validacion.y

    indices: list[int] = []
    for etiqueta in sorted(set(validacion.y.tolist())):
        candidatos = np.flatnonzero((validacion.y == etiqueta) & aciertos)
        indices.extend(candidatos[:POR_CONDICION].tolist())

    if not indices:
        print("No hay casos correctamente clasificados que explicar")
        return 1

    seleccion = np.array(sorted(indices))
    case_ids = [
        f"{validacion.meta.iloc[i]['session_id']}@{validacion.meta.iloc[i]['t_start']:.0f}s"
        for i in seleccion
    ]
    print(f"casos a explicar  : {len(seleccion)}\n")

    atribuciones = explain_cases(
        modelo,
        validacion.features[seleccion],
        feature_names=entrenamiento.feature_names,
        background=fondo,
        background_hash=huella,
        case_ids=case_ids,
        model_id=model_id,
        meta=validacion.meta.iloc[seleccion].reset_index(drop=True),
        seed=configuracion.seed,
    )

    filas: list[dict[str, object]] = []
    for a in atribuciones:
        for orden, atr in enumerate(a.top(10), start=1):
            filas.append(
                {
                    "explanation_id": a.explanation_id,
                    "case_id": a.case_id,
                    "predicted_class": a.predicted_class,
                    "confidence": round(a.confidence, 4),
                    "rank": orden,
                    **atr.to_dict(),
                    "window_start_s": a.window_start_s,
                    "window_end_s": a.window_end_s,
                    "session_id": a.session_id,
                }
            )
    tabla = pd.DataFrame(filas)
    paths.ensure(paths.TABLES)
    tabla.to_csv(destinos["tabla_atribuciones"], index=False)

    print("Señales más atribuidas por condición (agregando los casos explicados):")
    print(f"  {'condición':<24}{'señales principales':<58}{'confianza'}")
    resumen: list[dict[str, object]] = []
    for clase in sorted({a.predicted_class for a in atribuciones}):
        casos = [a for a in atribuciones if a.predicted_class == clase]
        pesos: dict[str, float] = {}
        for a in casos:
            for atr in a.top(8):
                pesos[atr.signal] = pesos.get(atr.signal, 0.0) + abs(atr.importance)
        principales = sorted(pesos, key=lambda s: pesos[s], reverse=True)[:4]
        confianza = float(np.mean([a.confidence for a in casos]))
        print(f"  {clase:<24}{', '.join(principales):<58}{confianza:>7.3f}")

        ficha = FAULTS.get(clase)
        declaradas = set(ficha.affected_signals) if ficha else set()
        resumen.append(
            {
                "predicted_class": clase,
                "n_cases": len(casos),
                "mean_confidence": round(confianza, 4),
                "top_signals": ", ".join(principales),
                "declared_by_fault": ", ".join(sorted(declaradas)) or "—",
                "top_signal_declared": principales[0] in declaradas if ficha else None,
            }
        )
    pd.DataFrame(resumen).to_csv(destinos["tabla_resumen"], index=False)

    paths.ensure(paths.EXPERIMENTS)
    destinos["registro"].write_text(
        json.dumps(
            {
                "experiment_id": "E9_xai",
                "dataset_id": dataset_id,
                "model_id": model_id,
                "explained_function": FUNCION_EXPLICADA,
                "explainer": "shap.explainers.Permutation",
                "background": {
                    "n": int(fondo.shape[0]),
                    "source": "train, clase normal",
                    "hash": huella,
                    "seed": configuracion.seed,
                },
                "n_cases": len(atribuciones),
                "cases": [a.to_dict() for a in atribuciones],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\ntabla   E9_atribuciones_{dataset_id}.csv, E9_resumen_{dataset_id}.csv")
    print(f"registro experiments/E9_xai_{dataset_id}.json")
    return 0
