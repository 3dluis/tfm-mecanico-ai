"""Las dos figuras que describen la muestra: su reparto y su separabilidad."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.visualization.memoria.base import (
    ANCHO_DE_PAGINA,
    CATEGORICAL,
    CONDICION,
    INK_SECONDARY,
    TABLAS,
    estilo_para_impresion,
    pie,
    titulo,
)


def fig_particiones() -> Figure:
    """Ventanas por clase y partición, con la etiqueta de cada ventana.

    Se cuenta por **etiqueta de ventana** y no por fallo de la sesión: las
    ventanas anteriores a la entrada del fallo en una sesión averiada son
    ventanas sin fallo, y de ahí que la clase normal doble a cada condición.
    """
    meta = pd.read_parquet(paths.DATA_PROCESSED / "synthetic_v2_meta.parquet")
    tabla = meta.groupby(["label", "partition"]).size().unstack(fill_value=0)
    orden = ["train", "validation", "test"]
    etiquetas = {"train": "entrenamiento", "validation": "validación", "test": "prueba"}

    estilo_para_impresion()
    fig, eje = plt.subplots(figsize=(ANCHO_DE_PAGINA, 3.4))
    clases = list(CONDICION)
    izquierda = np.zeros(len(clases))
    for i, particion in enumerate(orden):
        valores = np.array([tabla.loc[c, particion] for c in clases], dtype=float)
        eje.barh(
            range(len(clases)),
            valores,
            left=izquierda,
            color=CATEGORICAL[i],
            height=0.62,
            label=etiquetas[particion],
        )
        for y, (v, x0) in enumerate(zip(valores, izquierda, strict=True)):
            eje.text(
                x0 + v / 2,
                y,
                f"{int(v)}",
                ha="center",
                va="center",
                fontsize=7.5,
                color="white" if v > 20 else INK_SECONDARY,
            )
        izquierda += valores

    eje.set_yticks(range(len(clases)))
    eje.set_yticklabels([CONDICION[c] for c in clases], fontsize=7.5)
    eje.invert_yaxis()
    eje.set_xlabel("ventanas de 120 s (recuento)")
    eje.grid(visible=True, axis="x")
    eje.set_axisbelow(True)
    # La leyenda va FUERA del área de trazado: en la figura anterior se dibujaba
    # encima de la barra de la clase sin fallo y tapaba su cifra.
    eje.legend(loc="lower center", bbox_to_anchor=(0.5, -0.42), ncol=3, fontsize=7.5)
    titulo(fig, "Ventanas por clase y partición")
    pie(
        fig,
        "E5 · synthetic_v2 · reparto por sesión, nunca por ventana · "
        "la clase sin fallo dobla a cada fallo porque las sesiones averiadas "
        "aportan sus ventanas anteriores a la entrada del fallo",
    )
    fig.tight_layout()
    return fig


def fig_separabilidad() -> Figure:
    """Delta de Cliff de cada señal por condición, en nivel y en dispersión."""
    tabla = pd.read_csv(TABLAS / "E4_separabilidad.csv")
    senales = list(dict.fromkeys(tabla.signal))
    fallos = [c for c in CONDICION if c != "F00_normal"]

    estilo_para_impresion()
    fig, ejes = plt.subplots(2, 1, figsize=(ANCHO_DE_PAGINA, 8.6), sharex=True)
    for eje, (columna, rotulo) in zip(
        ejes,
        [("delta_level", "Nivel (media del bloque)"), ("delta_dispersion", "Dispersión")],
        strict=True,
    ):
        matriz = (
            tabla.pivot(index="signal", columns="fault_id", values=columna)
            .reindex(index=senales, columns=fallos)
            .to_numpy(dtype=float)
        )
        imagen = eje.imshow(matriz, cmap="RdBu_r", vmin=-1.0, vmax=1.0, aspect="auto")
        for i in range(matriz.shape[0]):
            for j in range(matriz.shape[1]):
                if abs(matriz[i, j]) >= 0.474:  # umbral de efecto grande
                    eje.text(
                        j,
                        i,
                        f"{matriz[i, j]:+.2f}",
                        ha="center",
                        va="center",
                        fontsize=7,
                        color="white" if abs(matriz[i, j]) > 0.8 else "#111111",
                    )
        eje.set_xticks(range(len(fallos)))
        eje.set_xticklabels([CONDICION[f] for f in fallos], rotation=35, ha="right", fontsize=7)
        eje.set_title(rotulo, fontsize=9)
        eje.grid(visible=False)
    ejes[0].set_yticks(range(len(senales)))
    ejes[0].set_yticklabels(senales, fontsize=7)
    barra = fig.colorbar(imagen, ax=ejes, fraction=0.025, pad=0.02)
    barra.set_label("delta de Cliff frente a la condición sin fallo", fontsize=7)
    # El pie va por debajo de las etiquetas giradas del eje: sin este margen se
    # imprime encima de ellas, que es el defecto que esta figura venía a corregir.
    fig.subplots_adjust(bottom=0.30, top=0.86)
    titulo(fig, "Qué señal separa cada condición, y por qué vía")
    pie(
        fig,
        "E4 · synthetic_v1, bloques de 60 s · se etiquetan las celdas con efecto grande "
        "(|delta| ≥ 0,474) · synthetic_v1 es pre-calibración y NO se reconstruye con el "
        "generador publicado (L-25)",
        y=0.015,
    )
    return fig
