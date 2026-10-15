"""El compromiso entre cobertura y precisión al mover el umbral de confianza.

**Qué dibuja, y qué no.** Dibuja los 101 puntos que el barrido del umbral (E15b)
registró sobre la partición de **validación**: en cada umbral, qué fracción de
ventanas queda cubierta y con qué precisión se decide entre las cubiertas, por
ventana y por sesión. Las bandas proceden del remuestreo de 1 000 réplicas que el
propio registro guarda, y existen **solo en los dos umbrales de la política**.

**Lo que esta figura no es.** No es el compromiso de la política de abstención del
agente. El criterio de suficiencia es compuesto —confianza **y** soporte
documental—, y este barrido mueve solo la mitad de confianza: la mitad documental
permanece fija. Tampoco es una exploración de la política completa, ni una curva
sobre el conjunto de prueba, que no interviene (`test_used: false`).

**Nada se interpola.** Cada punto dibujado es un punto registrado. Las líneas unen
puntos medidos para que se lea la tendencia; no añaden observaciones.
"""

from __future__ import annotations

import json
from typing import Any

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
    panel,
)

#: El registro del barrido. No se reejecuta nada: se lee.
REGISTRO = "E15b_barrido_umbral"


def _barrido() -> dict[str, Any]:
    datos: dict[str, Any] = json.loads((REGISTROS / f"{REGISTRO}.json").read_text("utf-8"))
    return datos


def compromiso_del_umbral() -> dict[str, Any]:
    """Los 101 puntos y los dos umbrales de la política, tal como se registraron."""
    d = _barrido()
    curva = d["curve"]
    return {
        "umbrales": [p["threshold"] for p in curva],
        "cobertura_ventanas": [p["coverage_windows"] for p in curva],
        "precision_ventanas": [p["precision_windows"] for p in curva],
        "cobertura_sesiones": [p["coverage_sessions"] for p in curva],
        "precision_sesiones": [p["precision_sessions"] for p in curva],
        "n_ventanas": d["n_windows"],
        "n_sesiones": d["n_sessions"],
        "umbral_original": d["original_criterion_threshold"],
        "umbral_vigente": d["amended_criterion_threshold"],
        "objetivo": d["criterion"]["target_precision"],
        "sensibilidad": d["sensitivity"],
        "conjunto_de_prueba_usado": d["test_used"],
    }


def fig_riesgo_cobertura() -> Figure:
    """Cobertura y precisión frente al umbral, y el plano que forman."""
    c = compromiso_del_umbral()
    estilo_para_impresion()
    fig, (izq, der) = plt.subplots(1, 2, figsize=(ANCHO_DE_PAGINA, 3.3))

    # (a) · las dos magnitudes frente al umbral, por ventana y por sesión.
    panel(izq, "a")
    for y, etiqueta, color, trazo in (
        (c["cobertura_ventanas"], "cobertura, ventanas", CATEGORICAL[0], "-"),
        (c["cobertura_sesiones"], "cobertura, sesiones", CATEGORICAL[0], "--"),
        (c["precision_ventanas"], "precisión, ventanas", CATEGORICAL[1], "-"),
        (c["precision_sesiones"], "precisión, sesiones", CATEGORICAL[1], "--"),
    ):
        izq.plot(c["umbrales"], y, color=color, ls=trazo, lw=1.3, label=etiqueta)

    for umbral, etiqueta in (
        (c["umbral_original"], f"{numero(c['umbral_original'], 2)} original"),
        (c["umbral_vigente"], f"{numero(c['umbral_vigente'], 2)} vigente"),
    ):
        izq.axvline(umbral, color=INK_MUTED, ls=":", lw=1.0)
        izq.text(umbral + 0.012, 0.055, etiqueta, fontsize=6.4, color=INK_SECONDARY, rotation=90)
    izq.axhline(c["objetivo"], color=INK_MUTED, lw=0.8, alpha=0.6)
    izq.text(
        0.02,
        c["objetivo"] + 0.015,
        f"objetivo {numero(c['objetivo'], 2)}",
        fontsize=6.4,
        color=INK_SECONDARY,
    )
    izq.set_xlim(0.0, 1.0)
    izq.set_ylim(0.0, 1.04)
    izq.set_xlabel("umbral de confianza calibrada (0–1)")
    izq.set_ylabel("fracción (0–1)")
    izq.legend(loc="lower left", frameon=False, fontsize=6.4)

    # (b) · el plano, solo por ventana: con doce sesiones la línea se cruza consigo
    # misma y no se lee. Las sesiones están en el panel (a), que es donde informan.
    panel(der, "b")
    der.plot(
        c["cobertura_ventanas"],
        c["precision_ventanas"],
        color=CATEGORICAL[0],
        lw=1.3,
        marker="o",
        ms=2.2,
        label=f"ventanas (n = {c['n_ventanas']})",
    )

    desplazamientos = {0: (-9, -24), 1: (-9, 14)}
    for orden, (umbral, datos) in enumerate(sorted(c["sensibilidad"].items())):
        x = datos["coverage_median"]
        y = datos["precision_median"]
        der.errorbar(
            x,
            y,
            yerr=[[y - datos["precision_p05"]], [datos["precision_p95"] - y]],
            fmt="D",
            ms=4.5,
            color=INK_SECONDARY,
            ecolor=INK_SECONDARY,
            elinewidth=1.0,
            capsize=2.5,
            alpha=0.75,
            zorder=4,
        )
        dx, dy = desplazamientos[orden]
        der.annotate(
            f"umbral {numero(float(umbral), 2)}",
            (x, y),
            textcoords="offset points",
            xytext=(dx, dy),
            fontsize=6.4,
            color=INK_SECONDARY,
            ha="right" if dx < 0 else "left",
        )
    der.axhline(c["objetivo"], color=INK_MUTED, lw=0.8, alpha=0.6)
    der.text(
        0.285,
        c["objetivo"] - 0.009,
        f"objetivo {numero(c['objetivo'], 2)}",
        fontsize=6.4,
        color=INK_SECONDARY,
    )
    der.set_xlabel("cobertura observada (fracción, 0–1)")
    der.set_ylabel("precisión de la decisión (0–1)")
    der.legend(
        loc="lower right",
        frameon=False,
        fontsize=6.4,
        title="barras: percentiles 5 y 95\nde 1 000 remuestreos",
        title_fontsize=6.0,
    )

    fig.tight_layout()
    return fig
