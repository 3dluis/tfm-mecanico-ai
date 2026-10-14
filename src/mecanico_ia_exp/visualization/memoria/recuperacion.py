"""La recuperación de evidencia documental, por estrategia de consulta."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from mecanico_ia_exp.visualization.memoria.base import (
    ANCHO_DE_PAGINA,
    CATEGORICAL,
    COLOR_BIEN,
    COLOR_MAL,
    TABLAS,
    estilo_para_impresion,
    pie,
    titulo,
)


def fig_recuperacion() -> Figure:
    """Qué estrategia encuentra el procedimiento del manual, y cuál no."""
    tabla = pd.read_csv(TABLAS / "E12_retrieval_por_estrategia.csv")
    nombres = {
        "semantic": "semántica",
        "semantic+engine": "semántica + filtro de motor",
        "semantic+authority": "semántica + filtro de autoridad",
        "hybrid": "híbrida (semántica y léxica)",
        "diagnosis-guided": "guiada por el diagnóstico",
    }
    tabla = tabla.set_index("strategy").reindex(list(nombres))

    estilo_para_impresion()
    fig, ejes = plt.subplots(
        2, 1, figsize=(ANCHO_DE_PAGINA, 6.2), gridspec_kw={"height_ratios": [1, 1.25]}
    )
    y = np.arange(len(tabla))
    aciertos = tabla["hit_rate"].to_numpy() * 5
    colores = [COLOR_BIEN if a == 5 else COLOR_MAL if a == 0 else CATEGORICAL[3] for a in aciertos]
    ejes[0].barh(y, aciertos, color=colores, height=0.6)
    for i, a in enumerate(aciertos):
        ejes[0].text(a + 0.08, i, f"{int(a)}/5", va="center", fontsize=7.5)
    ejes[0].set_yticks(y)
    ejes[0].set_yticklabels([nombres[s] for s in tabla.index], fontsize=7.5)
    ejes[0].invert_yaxis()
    ejes[0].set_xlim(0, 5.8)
    ejes[0].set_xlabel("casos en que el procedimiento aparece entre los 10 primeros")
    ejes[0].grid(visible=True, axis="x")
    ejes[0].set_axisbelow(True)
    ejes[0].set_title("Lo encuentra o no lo encuentra", fontsize=9)

    for i, (columna, color) in enumerate(
        (("mrr", CATEGORICAL[0]), ("ndcg_at_k", CATEGORICAL[2]), ("precision_at_k", CATEGORICAL[3]))
    ):
        ejes[1].barh(
            y + (i - 1) * 0.26,
            tabla[columna],
            height=0.24,
            color=color,
            label={"mrr": "MRR", "ndcg_at_k": "nDCG@10", "precision_at_k": "P@10"}[columna],
        )
    ejes[1].set_yticks(y)
    ejes[1].set_yticklabels([])
    ejes[1].invert_yaxis()
    ejes[1].set_xlabel("valor de la métrica (0–1)")
    ejes[1].grid(visible=True, axis="x")
    ejes[1].set_axisbelow(True)
    # Arriba a la derecha: la fila de la estrategia semántica vale cero en las
    # tres métricas, de modo que ahí no hay nada que tapar.
    ejes[1].legend(fontsize=7, loc="upper right")
    ejes[1].set_title("Y dónde lo coloca", fontsize=9)

    titulo(fig, "Sin el código de avería, la similitud semántica no encuentra el procedimiento")
    pie(
        fig,
        "E12, reejecución canónica del 13-09-2026 · corpus del vehículo de referencia · "
        "6 casos anotados, 5 puntuados; el sexto tiene la evidencia retirada del índice y no "
        "entra en las métricas · la estrategia guiada usa los códigos de la condición ANOTADA, "
        "que el sistema no tiene antes de diagnosticar: su ventaja es una cota asistida",
    )
    fig.tight_layout()
    return fig
