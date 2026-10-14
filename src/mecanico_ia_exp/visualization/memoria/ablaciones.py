"""El efecto de retirar o degradar cada componente del recorrido."""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from mecanico_ia_exp.visualization.memoria.base import (
    ANCHO_DE_PAGINA,
    BASELINE,
    CATEGORICAL,
    COLOR_MAL,
    REGISTROS,
    TABLAS,
    estilo_para_impresion,
    pie,
    titulo,
)


def tasas_e15() -> dict[str, tuple[int, int]]:
    """Los dos errores y la cobertura, contados como los cuenta la Tabla 5.6.

    La condición con distractor y filtro de motor queda fuera del denominador de
    la falsa confianza: su configuración era idéntica a la parcial, de modo que
    no es una condición independiente.
    """
    tabla = pd.read_csv(TABLAS / "E15_suficiencia.csv")
    debe_abstenerse = tabla[tabla.expected_action == "ABSTAIN"]
    # Fuera queda SOLO «DISTRACTOR», la condición con filtro de motor, cuya
    # configuración era idéntica a la parcial. «DISTRACTOR_NO_FILTER» sí cuenta:
    # es una condición distinta y entra en el denominador de 9 de la Tabla 5.6.
    sin_distractor = debe_abstenerse[debe_abstenerse.corpus_variant != "DISTRACTOR"]
    debe_explicar = tabla[tabla.expected_action == "EXPLAIN"]
    return {
        "falsa_confianza": (
            int((sin_distractor.decision == "EXPLAIN").sum()),
            len(sin_distractor),
        ),
        "abstencion_innecesaria": (
            int((debe_explicar.decision == "ABSTAIN").sum()),
            len(debe_explicar),
        ),
        "cobertura": (int((debe_explicar.decision == "EXPLAIN").sum()), len(debe_explicar)),
    }


def fig_ablaciones() -> Figure:
    """Qué componente sostiene el resultado, y cuál es sustituible."""
    filas: list[tuple[str, int, int, int, int, str]] = []
    canonica = tasas_e15()
    filas.append(
        (
            "canónica\ncriterio compuesto, umbral 0,79",
            *canonica["falsa_confianza"],
            *canonica["abstencion_innecesaria"],
            "",
        )
    )
    for identificador in ("A1", "A2", "A3", "A4"):
        registro = json.loads((REGISTROS / f"E18_ablacion_{identificador}.json").read_text("utf-8"))
        resumen = registro["summary"]
        nota = " (inconclusa)" if identificador == "A2" else ""
        filas.append(
            (
                f"{identificador}{nota}\n{registro['ablation']}",
                resumen["false_confidence"]["numerator"],
                resumen["false_confidence"]["denominator"],
                resumen["unnecessary_abstention"]["numerator"],
                resumen["unnecessary_abstention"]["denominator"],
                nota,
            )
        )

    estilo_para_impresion()
    fig, ejes = plt.subplots(2, 1, figsize=(ANCHO_DE_PAGINA, 7.2), sharex=True)
    y = np.arange(len(filas))
    for eje, (indice_num, indice_den, rotulo, color) in zip(
        ejes,
        [
            (1, 2, "Falsa confianza: explica cuando debía callar", COLOR_MAL),
            (3, 4, "Abstención innecesaria: calla cuando debía explicar", CATEGORICAL[3]),
        ],
        strict=True,
    ):
        numeradores = np.array([f[indice_num] for f in filas], dtype=float)
        denominadores = np.array([f[indice_den] for f in filas], dtype=float)
        eje.barh(y, denominadores, color=BASELINE, height=0.6, label="ejecuciones")
        eje.barh(y, numeradores, color=color, height=0.6, label="errores")
        for i, (n, d) in enumerate(zip(numeradores, denominadores, strict=True)):
            eje.text(d + 0.2, i, f"{int(n)}/{int(d)}", va="center", fontsize=7.5)
        eje.set_title(rotulo, fontsize=9)
        eje.set_xlabel("ejecuciones (recuento)")
        eje.set_xlim(0, max(denominadores) + 2.2)
        eje.grid(visible=True, axis="x")
        eje.set_axisbelow(True)
    # Los dos paneles llevan sus etiquetas y se invierten los dos. Antes solo el
    # de arriba: el de abajo mostraba 0, 1, 2, 3 y 4, y además en orden contrario,
    # de modo que emparejar una configuración con sus dos errores exigía leer al
    # revés sin que nada lo advirtiera.
    for eje in ejes:
        eje.set_yticks(y)
        eje.set_yticklabels([f[0] for f in filas], fontsize=7)
        eje.invert_yaxis()

    titulo(fig, "Lo que sostiene el resultado es el criterio de suficiencia, no la atribución")
    pie(
        fig,
        "E18, ablaciones pre-registradas, ejecutadas el 1-10-2026 · synthetic_v2, los mismos 17 "
        "casos · la falsa confianza se cuenta sobre 9 ejecuciones de 3 ventanas y la abstención "
        "sobre 5 de 5 ventanas · A2 quedó INCONCLUSA: la ruta léxica no recupera nada con una "
        "consulta en prosa, y la causa no es la ablación sino la consulta",
    )
    fig.tight_layout()
    return fig
