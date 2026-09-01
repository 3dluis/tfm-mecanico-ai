"""Ejecución de E5: estudio de longitud de ventana, ventanado y reparto.

El estudio de ventana es la evidencia con la que se elige la geometría. No se
elige un valor por costumbre: se mide cada candidato y se compara con el suelo de
ruido correspondiente.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.exploration import cliffs_delta, noise_floor_max_delta
from mecanico_ia_exp.data.splits import PARTICIONES, audit_masks, split_by_session
from mecanico_ia_exp.features.temporal import FEATURE_NAMES, extract_features
from mecanico_ia_exp.obd.faults import FAULTS, NORMAL_ID
from mecanico_ia_exp.timeseries.windowing import WindowConfig, make_windows
from mecanico_ia_exp.visualization import preprocessing as figuras_pre

#: Candidatas del plan experimental.
LONGITUDES: tuple[float, ...] = (10.0, 30.0, 60.0, 120.0)

#: Geometría elegida en E5. La justificación está en docs/experiments/E5_*.md.
VENTANA_ELEGIDA = WindowConfig(length_s=120.0, stride_s=60.0)

DATASET = "synthetic_v2"


def window_length_study(datos: pd.DataFrame) -> pd.DataFrame:
    """Tamaño de efecto por condición y longitud, contra su suelo de ruido."""
    filas: list[dict[str, object]] = []

    for longitud in LONGITUDES:
        ventanas = make_windows(datos, WindowConfig(length_s=longitud, stride_s=longitud / 2))
        descriptores = extract_features(ventanas.x)
        es_normal = ventanas.y == NORMAL_ID
        normales = descriptores[es_normal]

        suelo = noise_floor_max_delta(normales, ventanas.meta.loc[es_normal, "session_id"])

        for fault_id, ficha in FAULTS.items():
            con_fallo = descriptores[ventanas.y == fault_id]
            deltas = np.array(
                [
                    abs(cliffs_delta(con_fallo[:, j], normales[:, j]))
                    for j in range(descriptores.shape[1])
                ]
            )
            mejor = int(np.argmax(deltas))
            nombre = FEATURE_NAMES[mejor]
            declarada = any(nombre.startswith(s) for s in ficha.affected_signals)

            filas.append(
                {
                    "length_s": longitud,
                    "n_windows": len(ventanas),
                    "n_discarded": ventanas.n_discarded,
                    "fault_id": fault_id,
                    "noise_floor_p90": round(suelo, 4),
                    "best_delta": round(float(deltas[mejor]), 4),
                    "best_feature": nombre,
                    # La concordancia con el mecanismo es el criterio decisivo:
                    # un efecto sobre una señal que el fallo no toca es ruido con
                    # buena puntuación.
                    "feature_declared_by_fault": declarada,
                    "above_noise_floor": bool(deltas[mejor] > suelo),
                }
            )

    return pd.DataFrame(filas)


def run_preprocess(dataset_id: str = DATASET) -> int:
    """Produce el estudio, el conjunto ventaneado y el reparto auditado."""
    origen = paths.DATA_RAW_SYNTHETIC / f"{dataset_id}.parquet"
    if not origen.is_file():
        print(f"No existe {origen}. Ejecuta antes: mecanico-exp generate-synthetic")
        return 1

    datos = pd.read_parquet(origen)
    tablas = paths.ensure(paths.TABLES)
    procesados = paths.ensure(paths.DATA_PROCESSED)

    estudio = window_length_study(datos)
    estudio.to_csv(tablas / "E5_estudio_ventana.csv", index=False)
    print(f"tabla   E5_estudio_ventana.csv ({len(estudio)} filas)")

    ventanas = make_windows(datos, VENTANA_ELEGIDA)
    descriptores = extract_features(ventanas.x)
    reparto = split_by_session(ventanas.meta)
    mascaras = {p: reparto.mask(ventanas.meta, p) for p in PARTICIONES}

    informe = audit_masks(ventanas.meta, mascaras)
    print(f"\nAuditoría del reparto:\n  {informe}")
    if not informe.ok:
        print("\nReparto rechazado. No se guarda nada.")
        return 1

    resumen = reparto.summary(ventanas.meta)
    resumen.to_csv(tablas / "E5_reparto.csv", index=False)

    meta = ventanas.meta.copy()
    meta["partition"] = meta["session_id"].map(reparto.assignment)
    meta["label"] = ventanas.y

    np.save(procesados / f"{dataset_id}_x.npy", ventanas.x)
    np.save(procesados / f"{dataset_id}_features.npy", descriptores)
    meta.to_parquet(procesados / f"{dataset_id}_meta.parquet", index=False)
    (procesados / f"{dataset_id}_preprocess.json").write_text(
        json.dumps(
            {
                "dataset_id": dataset_id,
                "window_length_s": VENTANA_ELEGIDA.length_s,
                "window_stride_s": VENTANA_ELEGIDA.stride_s,
                "overlap_fraction": VENTANA_ELEGIDA.overlap_fraction,
                "n_windows": len(ventanas),
                "n_discarded": ventanas.n_discarded,
                "n_features": len(FEATURE_NAMES),
                "feature_names": list(FEATURE_NAMES),
                "split_seed": reparto.config.seed,
                "split_assignment": reparto.assignment,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    figuras = paths.ensure(paths.FIGURES)
    figuras_pre.fig_estudio_ventana(estudio, figuras / "FIG-E5-01_estudio_ventana.png")
    figuras_pre.fig_balance_particiones(meta, figuras / "FIG-E5-02_particiones.png")
    print("figura  FIG-E5-01_estudio_ventana.png")
    print("figura  FIG-E5-02_particiones.png")

    print(
        f"\n{len(ventanas)} ventanas de {VENTANA_ELEGIDA.length_s:.0f} s "
        f"({ventanas.n_discarded} descartadas por cruzar la entrada del fallo)"
    )
    print(
        resumen.pivot(index="session_fault_id", columns="partition", values="windows").to_string()
    )
    return 0
