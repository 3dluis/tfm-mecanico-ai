"""Figuras de modelado."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mecanico_ia_exp.visualization.style import (
    BASELINE,
    CATEGORICAL,
    INK_MUTED,
    INK_SECONDARY,
    SEQUENTIAL,
    apply_style,
    save,
)


def _corto(etiqueta: object) -> str:
    return str(etiqueta).split("_", 1)[0]


def fig_confusion(confusion: pd.DataFrame, destino: Path, titulo: str) -> Path:
    """¿Con qué se confunde cada condición?

    La cifra agregada dice cuánto acierta el modelo; esta figura dice **dónde**
    falla, que es lo que permite averiguar por qué.
    """
    apply_style()
    valores = confusion.to_numpy(dtype=float)
    # Se normaliza por fila: cada fila es la verdad, así que cada celda se lee
    # como «qué proporción de esta condición se predijo como aquella».
    proporciones = valores / valores.sum(axis=1, keepdims=True)
    etiquetas = [_corto(i) for i in confusion.index]

    fig, ax = plt.subplots(figsize=(6.0, 5.2))
    ax.imshow(proporciones, cmap=SEQUENTIAL, vmin=0.0, vmax=1.0)
    ax.set_xticks(range(len(etiquetas)))
    ax.set_xticklabels(etiquetas, fontsize=7.5)
    ax.set_yticks(range(len(etiquetas)))
    ax.set_yticklabels(etiquetas, fontsize=7.5)
    ax.set_xlabel("predicción")
    ax.set_ylabel("verdad")
    ax.grid(visible=False)

    for i in range(valores.shape[0]):
        for j in range(valores.shape[1]):
            if valores[i, j] == 0:
                continue
            # Texto claro sobre celdas oscuras: en un mapa secuencial el
            # contraste se invierte a partir de la mitad de la rampa.
            color = "#ffffff" if proporciones[i, j] > 0.55 else "#0b0b0b"
            ax.text(
                j,
                i,
                f"{int(valores[i, j])}",
                ha="center",
                va="center",
                fontsize=8,
                color=color,
            )

    ax.set_title(titulo, color="#0b0b0b", pad=22)
    ax.text(
        0.0,
        1.02,
        "Color proporcional a la fila. La diagonal son los aciertos.",
        transform=ax.transAxes,
        fontsize=7.5,
        color=INK_SECONDARY,
        va="bottom",
    )
    return save(fig, destino)


def fig_limite_de_evidencia(
    temperaturas: np.ndarray, aciertos: np.ndarray, tope_c: float, destino: Path
) -> Path:
    """¿Por qué el termostato bloqueado solo se detecta a veces?

    El fallo impone un techo a la temperatura del refrigerante. Mientras el motor
    no habría superado ese techo por sí mismo, no impone nada: la señal de un
    motor averiado y la de uno sano son idénticas.

    No es una limitación del modelo. Es un límite de la evidencia disponible, y
    marca los casos en los que abstenerse es la respuesta correcta.
    """
    apply_style()
    fig, ax = plt.subplots(figsize=(7.2, 2.9))

    for valor, color, etiqueta in (
        (True, CATEGORICAL[0], "detectado"),
        (False, CATEGORICAL[1], "no detectado"),
    ):
        seleccion = temperaturas[aciertos == valor]
        if seleccion.size == 0:
            continue
        ax.plot(
            seleccion,
            np.full(seleccion.shape, 1.0 if valor else 0.0),
            "o",
            ms=7,
            color=color,
            alpha=0.75,
            markeredgecolor="#fcfcfb",
            markeredgewidth=1.0,
            label=etiqueta,
            linestyle="none",
        )

    ax.axvline(tope_c, color=INK_MUTED, lw=1.0, ls=(0, (4, 3)))
    ax.annotate(
        f"techo que impone el fallo: {tope_c:.0f} °C",
        xy=(tope_c, 0.5),
        xytext=(-8, 0),
        textcoords="offset points",
        ha="right",
        va="center",
        fontsize=7.5,
        color=INK_SECONDARY,
    )
    ax.set_yticks([0.0, 1.0])
    ax.set_yticklabels(["no detectado", "detectado"], fontsize=7.5)
    ax.set_ylim(-0.45, 1.45)
    ax.set_xlabel("temperatura media del refrigerante en la ventana (°C)")
    ax.grid(visible=True, axis="x")
    for lado in ("left",):
        ax.spines[lado].set_color(BASELINE)

    ax.set_title("Límite de evidencia del termostato bloqueado", color="#0b0b0b", pad=16)
    ax.text(
        0.0,
        1.02,
        "Cada ventana de validación de F03. Bajo el techo, el fallo no deja firma.",
        transform=ax.transAxes,
        fontsize=7.5,
        color=INK_SECONDARY,
        va="bottom",
    )
    return save(fig, destino)


def fig_curvas_entrenamiento(
    train_loss: list[float],
    val_loss: list[float],
    val_macro_f1: list[float],
    best_epoch: int,
    destino: Path,
) -> Path:
    """¿Convergió el entrenamiento, o se quedó memorizando?

    Dos paneles y no dos escalas en un mismo eje: la pérdida y el F1 no comparten
    unidades, y superponerlos con dos ejes verticales invita a leer cruces que no
    significan nada.
    """
    apply_style()
    fig, (arriba, abajo) = plt.subplots(2, 1, figsize=(7.0, 5.0), sharex=True)
    epocas = range(len(train_loss))

    arriba.plot(epocas, train_loss, color=CATEGORICAL[0], lw=1.4, label="entrenamiento")
    arriba.plot(epocas, val_loss, color=CATEGORICAL[1], lw=1.4, label="validación")
    arriba.set_ylabel("pérdida")
    arriba.legend(loc="upper right", ncol=2)
    arriba.set_title("Pérdida", color="#0b0b0b", pad=6)

    abajo.plot(epocas, val_macro_f1, color=CATEGORICAL[2], lw=1.6)
    abajo.set_ylabel("F1 macro en validación")
    abajo.set_xlabel("época")
    abajo.set_title("F1 macro en validación", color="#0b0b0b", pad=6)

    for eje in (arriba, abajo):
        eje.axvline(best_epoch, color=INK_MUTED, lw=0.9, ls=(0, (3, 3)))
        eje.grid(visible=True, axis="both")
    abajo.annotate(
        f"mejor época: {best_epoch}",
        xy=(best_epoch, val_macro_f1[best_epoch]),
        xytext=(8, -12),
        textcoords="offset points",
        fontsize=7.5,
        color=INK_SECONDARY,
    )

    fig.suptitle("Entrenamiento del modelo temporal", x=0.02, ha="left", fontsize=11, weight="bold")
    fig.text(
        0.02,
        0.945,
        "La parada temprana se decide con el F1 macro de validación, no con la "
        "pérdida: el reparto es 2:1 y la pérdida premia la clase abundante.",
        fontsize=7.5,
        color=INK_SECONDARY,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    return save(fig, destino)
