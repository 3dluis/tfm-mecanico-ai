"""Ejecución de E5: estudio de longitud de ventana, ventanado y reparto.

El estudio de ventana es la evidencia con la que se elige la geometría. No se
elige un valor por costumbre: se mide cada candidato y se compara con el suelo de
ruido correspondiente.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.exploration import cliffs_delta, noise_floor_max_delta
from mecanico_ia_exp.data.splits import PARTICIONES, audit_masks, split_by_session
from mecanico_ia_exp.experiments.destinos import exigir_libres
from mecanico_ia_exp.features.temporal import FEATURE_NAMES, extract_features
from mecanico_ia_exp.obd.auditoria import auditar, exigir_auditoria_limpia
from mecanico_ia_exp.obd.faults import FAULTS, NORMAL_ID
from mecanico_ia_exp.obd.procedencia import ruta_de
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


#: Los tres conjuntos anteriores al manifiesto de procedencia. Son los únicos
#: exentos de la auditoría del generador, y la lista es cerrada a propósito: una
#: exención por «no tiene manifiesto» dejaría pasar cualquier conjunto nuevo sin
#: auditar, que es justo lo que la puerta existe para impedir.
ANTERIORES_AL_MANIFIESTO: frozenset[str] = frozenset(
    {"synthetic_v1", "synthetic_v2", "synthetic_v3"}
)


def destinos_de(dataset_id: str, etiqueta: str = "") -> dict[str, Path]:
    """Los artefactos de E5, con el conjunto en el nombre.

    **Esto no lo tenían.** `run_preprocess` escribía `E5_estudio_ventana.csv`,
    `E5_reparto.csv` y las dos figuras con nombre fijo, de modo que preprocesar
    **cualquier** otro conjunto pisaba los artefactos publicados de E5 sobre
    `synthetic_v2`. No es hipotético: ocurrió al probar la puerta de auditoría
    con un conjunto de prueba, y lo detectó el censo de artefactos históricos.

    Los artefactos publicados conservan su nombre sin sufijo y **no se
    regeneran**: siguen siendo el registro de E5. Lo que escribe este ejecutor
    desde ahora lleva el identificador del conjunto, como ya lo llevaban los de
    E6, E7 y E9.
    """
    sufijo = f"_{etiqueta}" if etiqueta else ""
    return {
        "tabla_estudio": paths.TABLES / f"E5_estudio_ventana_{dataset_id}{sufijo}.csv",
        "tabla_reparto": paths.TABLES / f"E5_reparto_{dataset_id}{sufijo}.csv",
        "figura_estudio": paths.FIGURES / f"FIG-E5-01_estudio_ventana_{dataset_id}{sufijo}.png",
        "figura_particiones": paths.FIGURES / f"FIG-E5-02_particiones_{dataset_id}{sufijo}.png",
        # Los procesados NO llevan etiqueta, y es deliberado: `load_partition`
        # los busca por identificador de conjunto, y ponerles sufijo rompería el
        # contrato con todo lo que viene después. Son **caché derivada**, no
        # artefacto de registro: se regeneran del parquet cuando haga falta y su
        # procedencia está en el manifiesto que los acompaña.
        "x": paths.DATA_PROCESSED / f"{dataset_id}_x.npy",
        "features": paths.DATA_PROCESSED / f"{dataset_id}_features.npy",
        "meta": paths.DATA_PROCESSED / f"{dataset_id}_meta.parquet",
        "manifiesto": paths.DATA_PROCESSED / f"{dataset_id}_preprocess.json",
    }


#: Los que sí son artefactos de registro y no se sobrescriben.
ARTEFACTOS_DE_REGISTRO: tuple[str, ...] = (
    "tabla_estudio",
    "tabla_reparto",
    "figura_estudio",
    "figura_particiones",
)


def run_preprocess(dataset_id: str = DATASET, *, etiqueta: str = "") -> int:
    """Produce el estudio, el conjunto ventaneado y el reparto auditado."""
    destinos = destinos_de(dataset_id, etiqueta)
    exigir_libres({c: destinos[c] for c in ARTEFACTOS_DE_REGISTRO})
    origen = paths.DATA_RAW_SYNTHETIC / f"{dataset_id}.parquet"
    if not origen.is_file():
        print(f"No existe {origen}. Ejecuta antes: mecanico-exp generate-synthetic")
        return 1

    datos = pd.read_parquet(origen)

    # La puerta de la auditoría del generador, **antes** de escribir nada.
    #
    # Se aplica a los conjuntos que traen manifiesto de procedencia, que son los
    # generados desde que existe. Los tres anteriores --`synthetic_v1`, `v2` y
    # `v3`-- no lo tienen y **no se bloquean**: están congelados, sostienen
    # cifras publicadas y su reproducción tiene que seguir funcionando. Esa
    # excepción se declara en voz alta en lugar de aplicarse en silencio, que es
    # la diferencia entre una exención documentada y un agujero.
    manifiesto_de_procedencia = ruta_de(dataset_id)
    if manifiesto_de_procedencia.is_file():
        manifiesto = json.loads(manifiesto_de_procedencia.read_text("utf-8"))
        esquema = manifiesto.get("expression", {}).get("esquema", "vigente")
        if esquema == "historico":
            # Un conjunto reconstruido en esquema histórico no trae las columnas
            # de expresión, así que la comprobación 8 no se puede verificar. Se
            # informa la auditoría entera sin bloquear, igual que con los tres
            # conjuntos congelados, porque es exactamente lo que es: uno de
            # ellos, reconstruido.
            print(
                f"\nAuditoría del generador ({manifiesto_de_procedencia.name}, "
                "esquema histórico, informativa):"
            )
            for comprobacion in auditar(datos, manifiesto):
                print(f"  {comprobacion}")
        else:
            print(f"\nAuditoría del generador ({manifiesto_de_procedencia.name}):")
            for comprobacion in exigir_auditoria_limpia(datos, manifiesto):
                print(f"  {comprobacion}")
    elif dataset_id in ANTERIORES_AL_MANIFIESTO:
        print(
            f"\nAVISO: {dataset_id} es anterior al manifiesto de procedencia, así que la "
            "auditoría del generador no se le aplica. Está congelado, sostiene cifras "
            "publicadas y su reproducción tiene que seguir funcionando."
        )
    else:
        print(
            f"\n{dataset_id} no trae manifiesto de procedencia "
            f"({manifiesto_de_procedencia.name}) y no es uno de los tres anteriores al "
            f"manifiesto ({', '.join(sorted(ANTERIORES_AL_MANIFIESTO))}).\n"
            "Sin manifiesto no se puede auditar el generador, y un conjunto sin auditar no "
            "llega al entrenamiento: fue así como se entrenó sobre synthetic_v3 durante "
            "semanas sin saber que su motor estaba sin calibrar.\n"
            "Regenéralo con «mecanico-exp generate-synthetic», que escribe el manifiesto.\n"
            "\nNo se guarda nada."
        )
        return 1

    paths.ensure(paths.TABLES)
    paths.ensure(paths.DATA_PROCESSED)

    estudio = window_length_study(datos)
    estudio.to_csv(destinos["tabla_estudio"], index=False)
    print(f"tabla   {destinos['tabla_estudio'].name} ({len(estudio)} filas)")

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
    resumen.to_csv(destinos["tabla_reparto"], index=False)

    meta = ventanas.meta.copy()
    meta["partition"] = meta["session_id"].map(reparto.assignment)
    meta["label"] = ventanas.y

    np.save(destinos["x"], ventanas.x)
    np.save(destinos["features"], descriptores)
    meta.to_parquet(destinos["meta"], index=False)
    destinos["manifiesto"].write_text(
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

    paths.ensure(paths.FIGURES)
    figuras_pre.fig_estudio_ventana(estudio, destinos["figura_estudio"])
    figuras_pre.fig_balance_particiones(meta, destinos["figura_particiones"])
    print(f"figura  {destinos['figura_estudio'].name}")
    print(f"figura  {destinos['figura_particiones'].name}")

    print(
        f"\n{len(ventanas)} ventanas de {VENTANA_ELEGIDA.length_s:.0f} s "
        f"({ventanas.n_discarded} descartadas por cruzar la entrada del fallo)"
    )
    print(
        resumen.pivot(index="session_fault_id", columns="partition", values="windows").to_string()
    )
    return 0
