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
    numero,
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


#: Corte convencional del efecto grande para el delta de Cliff. Es una
#: convención de lectura, no un resultado.
EFECTO_GRANDE = 0.474


def _mapa_de_separabilidad(columna: str, titulo_del_mapa: str, pie_extra: str) -> Figure:
    """Un mapa de calor de delta de Cliff, con sus dos ejes rotulados.

    **Por qué una figura por vía y no dos paneles.** La versión anterior ponía
    el nivel y la dispersión en el mismo lienzo, y solo el panel de arriba
    llevaba los nombres de las señales: el de abajo mostraba 0, 2, 4, 6, 8 y 10,
    de modo que no se podía saber qué fila era cada señal sin contar a mano. Dos
    mapas que comparten las doce filas y las cinco columnas se comparan mejor uno
    tras otro, cada uno completo, que apilados y con la mitad de los rótulos.
    """
    tabla = pd.read_csv(TABLAS / "E4_separabilidad.csv")
    senales = list(dict.fromkeys(tabla.signal))
    fallos = [c for c in CONDICION if c != "F00_normal"]
    matriz = (
        tabla.pivot(index="signal", columns="fault_id", values=columna)
        .reindex(index=senales, columns=fallos)
        .to_numpy(dtype=float)
    )

    estilo_para_impresion()
    fig, eje = plt.subplots(figsize=(ANCHO_DE_PAGINA, 4.6))
    imagen = eje.imshow(matriz, cmap="RdBu_r", vmin=-1.0, vmax=1.0, aspect="auto")
    for i in range(matriz.shape[0]):
        for j in range(matriz.shape[1]):
            if abs(matriz[i, j]) >= EFECTO_GRANDE:
                eje.text(
                    j,
                    i,
                    numero(float(matriz[i, j]), 2, signo=True),
                    ha="center",
                    va="center",
                    fontsize=7.5,
                    color="white" if abs(matriz[i, j]) > 0.8 else "#111111",
                )
    eje.set_xticks(range(len(fallos)))
    eje.set_xticklabels([CONDICION[f] for f in fallos], rotation=30, ha="right", fontsize=7.5)
    eje.set_yticks(range(len(senales)))
    eje.set_yticklabels(senales, fontsize=7.5)
    eje.grid(visible=False)

    barra = fig.colorbar(imagen, ax=eje, fraction=0.035, pad=0.02)
    barra.set_label("delta de Cliff frente a la condición sin fallo", fontsize=7)
    barra.ax.tick_params(labelsize=7)

    titulo(fig, titulo_del_mapa)
    pie(
        fig,
        f"E4 · synthetic_v1, bloques de 60 s · {pie_extra} · se etiquetan las celdas con efecto "
        "grande (|delta| ≥ 0,474) · synthetic_v1 es pre-calibración y NO se reconstruye con el "
        "generador publicado (L-25)",
        y=0.015,
    )
    fig.subplots_adjust(bottom=0.30, top=0.88, left=0.26, right=0.88)
    return fig


def fig_separabilidad_nivel() -> Figure:
    """Cuánto se separa cada señal por el **nivel** del bloque."""
    return _mapa_de_separabilidad(
        "delta_level",
        "Qué señales separan por su nivel medio",
        "delta de Cliff sobre la media del bloque",
    )


def fig_separabilidad_dispersion() -> Figure:
    """Cuánto se separa cada señal por su **dispersión** dentro del bloque."""
    return _mapa_de_separabilidad(
        "delta_dispersion",
        "Qué señales separan por su dispersión, y no por su nivel",
        "delta de Cliff sobre la desviación típica del bloque",
    )
