"""Las dos figuras de síntesis del capítulo de conclusiones."""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from mecanico_ia_exp.visualization.memoria.ablaciones import tasas_e15
from mecanico_ia_exp.visualization.memoria.base import (
    ANCHO_DE_PAGINA,
    CATEGORICAL,
    COLOR_BIEN,
    COLOR_MAL,
    INK_MUTED,
    INK_SECONDARY,
    estilo_para_impresion,
    pie,
    titulo,
)


def fig_objetivos() -> Figure:
    """Qué sostiene cada objetivo específico y hasta dónde.

    El contenido de cada celda es el que el capítulo 6 afirma en prosa. No es una
    medición: es el mapa de lo que el propio capítulo declara, puesto a la vista.
    """
    objetivos = [
        (
            "OE1",
            "Revisión del estado\ndel conocimiento",
            "revisión inspirada en PRISMA",
            "cumplido",
        ),
        ("OE2", "Entorno experimental\nreproducible", "E1–E5 · clon limpio", "parcial"),
        ("OE3", "Diagnóstico, confianza\ny atribución", "E6, E7, E9", "parcial"),
        ("OE4", "Recuperación y verificación\nde la evidencia", "E10–E13, E15", "parcial"),
        (
            "OE5",
            "Comportamiento integrado\nbajo cuatro condiciones",
            "E15, E18, E19, P1",
            "parcial",
        ),
    ]
    colores = {"cumplido": COLOR_BIEN, "parcial": CATEGORICAL[3], "pendiente": COLOR_MAL}

    estilo_para_impresion()
    fig, eje = plt.subplots(figsize=(ANCHO_DE_PAGINA, 3.8))
    for i, (identificador, nombre, evidencia, estado) in enumerate(objetivos):
        y = len(objetivos) - i - 1
        eje.add_patch(Rectangle((0, y - 0.38), 10, 0.76, color=colores[estado], alpha=0.14, lw=0))
        eje.text(0.15, y, identificador, fontsize=9, fontweight="bold", va="center")
        eje.text(1.0, y, nombre, fontsize=7.5, va="center")
        eje.text(5.0, y, evidencia, fontsize=7.5, va="center", color=INK_SECONDARY)
        eje.text(
            9.85,
            y,
            estado,
            fontsize=8,
            va="center",
            ha="right",
            color=colores[estado],
            fontweight="bold",
        )
    eje.set_xlim(0, 10)
    eje.set_ylim(-0.6, len(objetivos) - 0.4)
    eje.axis("off")
    eje.text(1.0, len(objetivos) - 0.55, "objetivo", fontsize=7, color=INK_MUTED)
    eje.text(5.0, len(objetivos) - 0.55, "experimentos que lo miden", fontsize=7, color=INK_MUTED)
    eje.text(9.85, len(objetivos) - 0.55, "estado", fontsize=7, color=INK_MUTED, ha="right")
    titulo(fig, "Qué sostiene cada objetivo, y hasta dónde")
    pie(
        fig,
        "elaboración propia a partir del capítulo 6 y de docs/experiment-index.md · sin conjunto "
        "de datos: es el mapa de lo que el capítulo declara, no una medición · «parcial» es la "
        "palabra que usa el texto, y no se redondea hacia arriba",
    )
    fig.tight_layout()
    return fig


def fig_compromiso() -> Figure:
    """Los dos errores del sistema y los de las dos políticas triviales."""
    tasas = tasas_e15()
    fc_n, fc_d = tasas["falsa_confianza"]
    ai_n, ai_d = tasas["abstencion_innecesaria"]
    politicas = [
        (
            "verificador de suficiencia",
            fc_n / fc_d,
            ai_n / ai_d,
            f"{fc_n}/{fc_d}",
            f"{ai_n}/{ai_d}",
            CATEGORICAL[0],
        ),
        ("abstenerse siempre", 0.0, 1.0, f"0/{fc_d}", f"{ai_d}/{ai_d}", CATEGORICAL[6]),
        (
            "explicar siempre que el modelo confía",
            1.0,
            ai_n / ai_d,
            f"{fc_d}/{fc_d}",
            f"{ai_n}/{ai_d}",
            CATEGORICAL[7],
        ),
    ]

    estilo_para_impresion()
    fig, eje = plt.subplots(figsize=(ANCHO_DE_PAGINA, 5.2))
    for nombre, fc, ai, texto_fc, texto_ai, color in politicas:
        eje.scatter(fc, ai, s=140, color=color, zorder=3)
        # La política que explica siempre está pegada al borde derecho: su
        # etiqueta va hacia dentro, o el recorte ajustado la deja cortada.
        a_la_izquierda = fc > 0.5
        eje.annotate(
            f"{nombre}\nfalsa confianza {texto_fc} · abstención {texto_ai}",
            (fc, ai),
            textcoords="offset points",
            xytext=(-10 if a_la_izquierda else 10, 10 if nombre != "abstenerse siempre" else -24),
            ha="right" if a_la_izquierda else "left",
            fontsize=7.2,
            color=color,
        )
    eje.set_xlabel("falsa confianza: explica cuando debía abstenerse (fracción)")
    eje.set_ylabel("abstención innecesaria: calla cuando debía explicar (fracción)")
    eje.set_xlim(-0.08, 1.18)
    eje.set_ylim(-0.08, 1.18)
    eje.grid(visible=True, axis="both")
    eje.set_axisbelow(True)
    eje.text(
        0.02,
        0.02,
        "esquina sin errores\n(ninguna política la alcanza)",
        fontsize=6.8,
        color=INK_SECONDARY,
        va="bottom",
    )
    titulo(fig, "Cada política trivial iguala al sistema en un error y lo empeora en el otro")
    pie(
        fig,
        "E15 · synthetic_v2, validación, 17 ejecuciones sobre 5 ventanas · las políticas de "
        "referencia se definieron el 4-09-2026, DESPUÉS de medir las tres versiones del criterio "
        "sobre estos mismos casos · con 3 y 5 ventanas independientes no se publica intervalo",
    )
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- #
# Registro
# --------------------------------------------------------------------------- #
