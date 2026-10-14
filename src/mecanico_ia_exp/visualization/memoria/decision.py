"""Dónde cae cada decisión de la evaluación final respecto del umbral.

La Tabla 5.7 publica los recuentos de la evaluación final y la Figura 5.13 el
reparto de las decisiones. Ninguna de las dos dice **dónde** quedó cada caso
respecto de la puerta de confianza, que es la pregunta que queda abierta cuando
se lee que hubo dos abstenciones innecesarias.

Lee el registro de E19 y no escribe ningún valor a mano.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from mecanico_ia_exp.visualization.memoria.base import (
    ANCHO_DE_PAGINA,
    BASELINE,
    COLOR_BIEN,
    COLOR_MAL,
    INK_MUTED,
    INK_SECONDARY,
    TABLAS,
    estilo_para_impresion,
    numero,
)

#: El registro de la evaluación final. El sufijo `_v3` es el **tercer intento**
#: de la ejecución, no una versión del conjunto de datos: E19 se interrumpió dos
#: veces y la tercera llegó al final.
REGISTRO_E19 = TABLAS / "E19_evaluacion_final_v3.csv"

#: Umbral de confianza calibrada de la política de suficiencia vigente.
UMBRAL = 0.79


def decisiones_de_e19() -> pd.DataFrame:
    """Las 35 ejecuciones del registro, una por fila, ordenadas para la figura.

    No se agrega nada: el autor pidió ver las 35, y agregarlas escondería que
    una misma pareja de caso y sesión se evaluó en varias ejecuciones y que en
    una de ellas la confianza fue otra. El acierto se toma de la columna
    `correct` del registro, no se recalcula.
    """
    tabla = pd.read_csv(REGISTRO_E19)
    tabla["regimen"] = [str(s).split("__")[1] for s in tabla.session_id]
    tabla["caso"] = [str(c).split("_")[0] for c in tabla.case_id_gold]
    tabla["abstencion_innecesaria"] = (tabla.expected_decision == "EXPLAIN") & (
        tabla.decision == "ABSTAIN"
    )
    orden = {"operativo": 0, "comparativo": 1, "adverso": 2}
    tabla["orden_estrato"] = [orden.get(str(e), 9) for e in tabla.stratum]
    return tabla.sort_values(
        ["orden_estrato", "expected_decision", "confidence", "caso"],
        ascending=[True, True, True, True],
    ).reset_index(drop=True)


def fig_decisiones_y_umbral() -> Figure:
    """Las 35 ejecuciones de la evaluación final, situadas respecto de la puerta de confianza."""
    datos = decisiones_de_e19()

    estilo_para_impresion()
    fig, eje = plt.subplots(figsize=(ANCHO_DE_PAGINA, 7.6))

    eje.axvspan(0.42, UMBRAL, color=COLOR_MAL, alpha=0.07)
    eje.axvline(UMBRAL, color=INK_SECONDARY, lw=1.0, ls="--")
    eje.annotate(
        f"umbral: {numero(UMBRAL, 2)}",
        xy=(UMBRAL - 0.012, len(datos) - 0.3),
        fontsize=6.6,
        ha="right",
        color=INK_SECONDARY,
    )

    # Las columnas numéricas se convierten una vez, fuera del bucle: leerlas desde
    # la tupla de pandas devuelve un tipo unión que la comprobación estricta no
    # acepta, y convertirlas en cada iteración repetiría el mismo trabajo.
    confianzas = datos.confidence.to_numpy(float)
    coberturas = datos.claim_coverage.to_numpy(float)
    documentos = datos.n_documents_applicable.to_numpy(int)

    for i, fila in enumerate(datos.itertuples()):
        marca = "s" if fila.expected_decision == "ABSTAIN" else "o"
        color = COLOR_BIEN if bool(fila.correct) else COLOR_MAL
        eje.plot(
            confianzas[i],
            i,
            marca,
            ms=5.4,
            color=color,
            mec="white" if bool(fila.prediction_correct) else "#111111",
            mew=0.7 if bool(fila.prediction_correct) else 1.3,
            zorder=3,
        )
        eje.text(
            1.045,
            i,
            f"cob. {numero(float(coberturas[i]), 1)} · {int(documentos[i])} doc.",
            va="center",
            fontsize=6.4,
            color=INK_MUTED,
        )

    # Separadores entre estratos: el registro mezcla tres y la lectura cambia.
    limites: list[tuple[int, str]] = []
    anterior = ""
    for i, estrato in enumerate(datos.stratum):
        if str(estrato) != anterior:
            limites.append((i, str(estrato)))
            anterior = str(estrato)
    for i, estrato in limites:
        if i:
            eje.axhline(i - 0.5, color=BASELINE, lw=0.8)
        eje.annotate(
            f"estrato {estrato}",
            xy=(0.44, i + 0.25),
            fontsize=6.4,
            color=INK_SECONDARY,
            fontweight="bold",
        )

    eje.set_yticks(np.arange(len(datos)))
    eje.set_yticklabels(
        [
            f"{f.caso} · {f.regimen} · "
            f"{'callar' if f.expected_decision == 'ABSTAIN' else 'explicar'}"
            for f in datos.itertuples()
        ],
        fontsize=6.6,
    )
    eje.set_ylim(-0.8, len(datos) - 0.2)
    eje.set_xlim(0.42, 1.26)
    eje.set_xticks([0.5, 0.6, 0.7, 0.79, 0.9, 1.0])
    eje.set_xticklabels(["0,50", "0,60", "0,70", "0,79", "0,90", "1,00"])
    eje.set_xlabel("confianza calibrada del diagnóstico")
    eje.grid(visible=True, axis="x")
    eje.set_axisbelow(True)

    for i, fila in enumerate(datos.itertuples()):
        if bool(fila.abstencion_innecesaria):
            eje.annotate(
                "se calló debiendo explicar",
                xy=(float(confianzas[i]) + 0.022, i),
                fontsize=6.2,
                va="center",
                color=COLOR_MAL,
            )

    leyenda = [
        Line2D([], [], marker="o", ls="", color=COLOR_BIEN, ms=6, label="la decisión fue correcta"),
        Line2D(
            [], [], marker="o", ls="", color=COLOR_MAL, ms=6, label="la decisión fue incorrecta"
        ),
        Line2D([], [], marker="o", ls="", color=BASELINE, ms=6, label="el caso pedía explicar"),
        Line2D([], [], marker="s", ls="", color=BASELINE, ms=6, label="el caso pedía callar"),
        Line2D(
            [],
            [],
            marker="o",
            ls="",
            color=BASELINE,
            mec="#111111",
            mew=1.3,
            ms=6,
            label="el diagnóstico del modelo era incorrecto",
        ),
    ]
    eje.legend(
        handles=leyenda, loc="lower center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=6.3
    )
    fig.tight_layout()
    return fig
