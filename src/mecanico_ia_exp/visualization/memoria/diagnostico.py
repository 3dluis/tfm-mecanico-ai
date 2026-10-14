"""Las figuras del modelo de diagnóstico: adónde van sus errores y cuánto pesa cada condición."""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from mecanico_ia_exp.visualization.memoria.base import (
    ANCHO_DE_PAGINA,
    BASELINE,
    COLOR_BOSQUE,
    COLOR_RED,
    CONDICION,
    INK_MUTED,
    REGISTROS,
    SEQUENTIAL,
    TABLAS,
    estilo_para_impresion,
    numero,
    panel,
)


def _confusion(eje: Axes, matriz: pd.DataFrame, letra: str) -> None:
    valores = matriz.to_numpy(dtype=float)
    por_fila = valores / valores.sum(axis=1, keepdims=True)
    eje.imshow(por_fila, cmap=SEQUENTIAL, vmin=0.0, vmax=1.0, aspect="auto")
    for i in range(valores.shape[0]):
        for j in range(valores.shape[1]):
            if valores[i, j] == 0:
                continue
            eje.text(
                j,
                i,
                f"{int(valores[i, j])}",
                ha="center",
                va="center",
                fontsize=8,
                color="white" if por_fila[i, j] > 0.55 else "#111111",
            )
    etiquetas = [c.split("_")[0] for c in matriz.index]
    eje.set_xticks(range(len(etiquetas)))
    eje.set_xticklabels(etiquetas, fontsize=7)
    eje.set_yticks(range(len(etiquetas)))
    eje.set_yticklabels(etiquetas, fontsize=7)
    eje.set_xlabel("predicción")
    panel(eje, letra)
    eje.grid(visible=False)


def fig_confusiones() -> Figure:
    """Las dos matrices juntas: lo que las separa es adónde van los errores."""
    bosque = pd.read_csv(TABLAS / "E6_baseline_confusion_synthetic_v2.csv", index_col=0)
    red = pd.read_csv(TABLAS / "E7_temporal_confusion_synthetic_v2.csv", index_col=0)

    estilo_para_impresion()
    fig, ejes = plt.subplots(2, 1, figsize=(ANCHO_DE_PAGINA, 6.2))
    # (a) bosque aleatorio · (b) GRU bidireccional. El pie los nombra.
    _confusion(ejes[0], bosque, "a")
    _confusion(ejes[1], red, "b")
    ejes[0].set_ylabel("condición anotada")
    fig.tight_layout()
    return fig


def fig_f1_por_clase() -> Figure:
    """F1 por condición de los dos modelos, y su diferencia."""
    bosque = pd.read_csv(TABLAS / "E6_baseline_por_clase_synthetic_v2.csv").set_index("label")
    red = pd.read_csv(TABLAS / "E7_temporal_por_clase_synthetic_v2.csv").set_index("label")
    clases = [c for c in CONDICION if c in bosque.index]
    diferencia = (red.loc[clases, "f1"] - bosque.loc[clases, "f1"]).to_numpy()
    orden = np.argsort(diferencia)
    clases = [clases[i] for i in orden]
    diferencia = diferencia[orden]

    estilo_para_impresion()
    fig, ejes = plt.subplots(
        2, 1, figsize=(ANCHO_DE_PAGINA, 5.2), gridspec_kw={"height_ratios": [1.5, 1]}
    )
    y = np.arange(len(clases))
    ejes[0].barh(
        y - 0.19, bosque.loc[clases, "f1"], height=0.36, color=COLOR_BOSQUE, label="bosque (E6)"
    )
    ejes[0].barh(y + 0.19, red.loc[clases, "f1"], height=0.36, color=COLOR_RED, label="GRU (E7)")
    ejes[0].set_yticks(y)
    # El soporte sale de la tabla como objeto de pandas; se convierte una vez.
    soporte = {c: int(bosque["support"].astype(int).loc[c]) for c in clases}
    ejes[0].set_yticklabels([f"{CONDICION[c]}\n(n={soporte[c]})" for c in clases], fontsize=7)
    ejes[0].set_xlabel("F1 de la clase (0–1)")
    ejes[0].set_xlim(0, 1.05)
    ejes[0].grid(visible=True, axis="x")
    ejes[0].set_axisbelow(True)
    ejes[0].legend(loc="lower right", fontsize=7)
    panel(ejes[0], "a")

    colores = [COLOR_RED if d > 0 else COLOR_BOSQUE for d in diferencia]
    ejes[1].barh(y, diferencia, color=colores, height=0.55)
    for i, d in enumerate(diferencia):
        ejes[1].text(
            d + (0.004 if d > 0 else -0.004),
            i,
            numero(d, 3, signo=True),
            va="center",
            ha="left" if d > 0 else "right",
            fontsize=7,
        )
    ejes[1].axvline(0.0, color=BASELINE, lw=0.8)
    ejes[1].set_yticks([])
    ejes[1].set_xlabel("F1 de la red − F1 del bosque")
    ejes[1].set_xlim(-0.22, 0.09)
    ejes[1].grid(visible=True, axis="x")
    ejes[1].set_axisbelow(True)
    panel(ejes[1], "b")
    fig.tight_layout()
    return fig


def fig_confusor_de_volumen() -> Figure:
    """El orden se invierte entre los dos conjuntos, y cambian dos cosas a la vez."""

    def f1(nombre: str) -> float:
        return float(json.loads((REGISTROS / nombre).read_text("utf-8"))["metrics"]["macro_f1"])

    valores = {
        "synthetic_v2": (f1("E6_baseline_synthetic_v2.json"), f1("E7_temporal_synthetic_v2.json")),
        "synthetic_v3": (f1("E6_baseline_synthetic_v3.json"), f1("E7_temporal_synthetic_v3.json")),
    }

    estilo_para_impresion()
    fig, eje = plt.subplots(figsize=(ANCHO_DE_PAGINA, 3.4))
    x = np.array([0.0, 1.0])
    for desplazamiento, color, etiqueta, indice in (
        (-0.15, COLOR_BOSQUE, "bosque aleatorio (E6)", 0),
        (0.15, COLOR_RED, "GRU bidireccional (E7)", 1),
    ):
        alturas = [valores[c][indice] for c in valores]
        eje.bar(x + desplazamiento, alturas, width=0.26, color=color, label=etiqueta)
        for xi, altura in zip(x + desplazamiento, alturas, strict=True):
            eje.text(xi, altura + 0.012, numero(altura, 4), ha="center", fontsize=7.5)

    eje.set_xlim(-0.45, 1.45)
    eje.set_xticks(x)
    eje.set_xticklabels(
        [
            "synthetic_v2\n72 sesiones · generador CALIBRADO",
            "synthetic_v3\n216 sesiones · generador SIN CALIBRAR",
        ],
        fontsize=7.5,
    )
    eje.set_ylabel("F1 macro sobre validación (0–1)")
    eje.set_ylim(0, 1.08)
    eje.legend(loc="lower center", bbox_to_anchor=(0.5, -0.44), ncol=2, fontsize=7.5)
    eje.annotate(
        "",
        xy=(0.19, 0.60),
        xytext=(0.81, 0.60),
        arrowprops={"arrowstyle": "<->", "color": INK_MUTED, "lw": 0.9},
    )
    fig.tight_layout()
    return fig
