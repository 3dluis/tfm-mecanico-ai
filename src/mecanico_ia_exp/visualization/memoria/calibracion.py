"""La calibración de la confianza del modelo, antes y después."""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from mecanico_ia_exp.visualization.memoria.base import (
    ANCHO_DE_PAGINA,
    CATEGORICAL,
    INK_MUTED,
    INK_SECONDARY,
    REGISTROS,
    estilo_para_impresion,
    numero,
    pie,
    titulo,
)


def fig_calibracion() -> Figure:
    """Confianza declarada frente a acierto, antes y después de calibrar."""
    registro = json.loads((REGISTROS / "E15_suficiencia.json").read_text("utf-8"))
    calibracion = registro["calibration"]

    estilo_para_impresion()
    fig, eje = plt.subplots(figsize=(ANCHO_DE_PAGINA, 5.0))
    eje.plot([0.6, 1.0], [0.6, 1.0], color=INK_MUTED, ls=":", lw=1.0)
    eje.text(0.665, 0.645, "calibración perfecta", fontsize=6.8, color=INK_SECONDARY, rotation=37)
    eje.fill_between([0.6, 1.0], [0.6, 1.0], 1.0, color=CATEGORICAL[0], alpha=0.04)
    eje.text(0.63, 0.96, "promete menos de lo que cumple", fontsize=6.8, color=INK_SECONDARY)
    eje.text(0.80, 0.625, "promete más de lo que cumple", fontsize=6.8, color=INK_SECONDARY)

    for clave, etiqueta, color, marca in (
        # Naranja y azul, no rojo y verde: la pareja roja-verde es la peor para
        # un lector con daltonismo y aquí no aporta nada que la forma no diga.
        ("uncalibrated", "sin calibrar", CATEGORICAL[1], "o"),
        ("calibrated", "calibrado (isotónica)", CATEGORICAL[0], "s"),
    ):
        punto = calibracion[clave]
        eje.scatter(
            punto["mean_confidence"], punto["accuracy"], s=110, color=color, marker=marca, zorder=3
        )
        eje.annotate(
            f"{etiqueta}\nECE {numero(punto['ece'])}\nsesgo {numero(punto['bias'], signo=True)}",
            (punto["mean_confidence"], punto["accuracy"]),
            textcoords="offset points",
            xytext=(12, -30),
            fontsize=7.2,
            color=color,
        )
    eje.set_xlim(0.60, 1.0)
    eje.set_ylim(0.60, 1.0)
    eje.set_xlabel("confianza media declarada (0–1)")
    eje.set_ylabel("acierto observado (fracción, 0–1)")
    titulo(fig, "El modelo estaba infraconfiado, y la calibración lo centra")
    pie(
        fig,
        f"E6, calibrado en E15 · synthetic_v2, validación, {calibracion['n_windows']} ventanas, "
        f"{calibracion['n_bins']} tramos · {calibracion['method']} · "
        "el sesgo es confianza media menos acierto; el ECE no lleva signo",
    )
    fig.tight_layout()
    return fig
