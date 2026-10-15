"""La calibración de la confianza del modelo: sus dos puntos y su forma.

**Dos figuras, dos estatutos.** `fig_calibracion` dibuja los dos puntos agregados
que el registro de suficiencia publica, antes y después de calibrar, con el error
esperado de calibración de cada uno. `fig_fiabilidad` dibuja la **forma** de la
calibración por intervalos de confianza, y lo hace por una vía que conviene
explicar, porque no es la habitual.

**De dónde sale el diagrama de fiabilidad.** El registro del modelo de diagnóstico
**no conserva la confianza por ventana**: guarda exactitud, F1 y un bloque
agregado de calibración. Lo que sí se conserva es la curva acumulada del barrido
del umbral: 101 puntos con, en cada umbral, cuántas ventanas quedan cubiertas y
con qué precisión se decide entre ellas. Por diferencias entre umbrales
consecutivos se recuperan, de cada intervalo de confianza de una centésima, el
número de ventanas y el número de aciertos:

    n(intervalo)        = n_cubiertas(t) − n_cubiertas(t + 0,01)
    aciertos(intervalo) = precisión(t)·n_cubiertas(t) − precisión(t+0,01)·n_cubiertas(t+0,01)

La reconstrucción **no es aproximada en lo que dibuja**: suma las 98 ventanas de
validación con 86 aciertos en 32 intervalos no vacíos, y la exactitud global que
produce coincide dígito a dígito con la publicada por el registro del modelo.
Pero tiene dos límites que la figura declara en su pie y respeta en su dibujo:

1. **la confianza media dentro de cada intervalo no se conservó**, de modo que cada
   intervalo se dibuja ocupando su intervalo y no en un punto;
2. **solo existe para la confianza calibrada** —isotónica, cv = 5, ajustada sobre
   entrenamiento—, que es la que usa el verificador. La confianza anterior a
   calibrar no se guardó por ventana y su diagrama no se dibuja.

**Y un error que no se comete.** De aquí no se publica un error esperado de
calibración. Con intervalos de una centésima sale un valor distinto del registrado,
y no porque uno corrija al otro: miden con **particiones de confianza diferentes**.
El valor canónico sigue siendo el del registro.
"""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Patch, Rectangle

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
    fig.tight_layout()
    return fig


#: Anchura del intervalo de confianza del barrido: el registro avanza de centésima
#: en centésima, y esa es la resolución máxima que la reconstrucción admite.
ANCHURA = 0.01

#: Por debajo de este número de ventanas, un intervalo no sostiene una proporción:
#: se dibuja igual, porque ocultarlo sería peor, y se marca.
POCAS_OBSERVACIONES = 2


@dataclass(frozen=True)
class Intervalo:
    """Un intervalo de confianza con lo que se recuperó de él."""

    desde: float
    hasta: float
    ventanas: int
    aciertos: int

    @property
    def exactitud(self) -> float:
        return self.aciertos / self.ventanas

    @property
    def escaso(self) -> bool:
        return self.ventanas <= POCAS_OBSERVACIONES


def intervalos_de_fiabilidad() -> list[Intervalo]:
    """Reconstruye los intervalos por diferencias de la curva acumulada del barrido.

    El último punto de la curva, el del umbral 1,0, no tiene siguiente con el que
    restarse: es la cola de las ventanas cuya confianza calibrada es exactamente
    1,0, y entra como intervalo propio.
    """
    barrido = json.loads((REGISTROS / "E15b_barrido_umbral.json").read_text("utf-8"))
    curva = barrido["curve"]
    puntos = [(p["threshold"], p["n_windows_covered"], p["precision_windows"]) for p in curva]

    recuperados: list[Intervalo] = []
    for (desde, n_desde, p_desde), (hasta, n_hasta, p_hasta) in itertools.pairwise(puntos):
        ventanas = n_desde - n_hasta
        if ventanas <= 0:
            continue
        # El registro redondea la precisión a seis decimales, de modo que el
        # producto vuelve con un residuo del orden de 1e-4. El recuento de
        # aciertos es un entero por construcción y se restituye como tal.
        aciertos = round(p_desde * n_desde - p_hasta * n_hasta)
        recuperados.append(Intervalo(desde, hasta, ventanas, aciertos))

    cola_umbral, cola_n, cola_p = puntos[-1]
    if cola_n:
        recuperados.append(Intervalo(cola_umbral, cola_umbral, cola_n, round(cola_n * cola_p)))
    return recuperados


def comprobacion_de_la_reconstruccion() -> dict[str, float | int]:
    """Lo que permite afirmar que la reconstrucción es correcta y no aproximada.

    Si la suma de los intervalos no reprodujera las 98 ventanas de validación y la
    exactitud global del registro del modelo, la figura no debería dibujarse.
    """
    intervalos = intervalos_de_fiabilidad()
    ventanas = sum(i.ventanas for i in intervalos)
    aciertos = sum(i.aciertos for i in intervalos)
    diagnostico = json.loads((REGISTROS / "E6_baseline_synthetic_v2.json").read_text("utf-8"))
    return {
        "intervalos_no_vacios": len(intervalos),
        "ventanas": ventanas,
        "aciertos": aciertos,
        "exactitud_reconstruida": aciertos / ventanas,
        "exactitud_del_registro": diagnostico["metrics"]["accuracy"],
        "intervalos_escasos": sum(1 for i in intervalos if i.escaso),
    }


#: Anchura con que se **dibuja**. Los intervalos de una centésima recuperados del
#: barrido son exactos pero ilegibles: con 98 ventanas repartidas en 33, casi
#: todos contienen una sola y su proporción solo puede valer 0 o 1. Agrupar es
#: suma de enteros, de modo que no pierde exactitud; lo que cambia es la
#: resolución del eje, y el pie de la figura la declara.
ANCHURA_DE_DIBUJO = 0.05

#: Por debajo de este número de ventanas una proporción no describe nada estable.
POCAS_PARA_DIBUJAR = 4


def agrupar(anchura: float = ANCHURA_DE_DIBUJO) -> list[Intervalo]:
    """Suma los intervalos recuperados en otros más anchos, sin perder exactitud."""
    acumulado: dict[int, list[int]] = {}
    for intervalo in intervalos_de_fiabilidad():
        # La cola de confianza exactamente 1,0 entra en el último intervalo.
        indice = min(int(intervalo.desde / anchura), round(1 / anchura) - 1)
        celda = acumulado.setdefault(indice, [0, 0])
        celda[0] += intervalo.ventanas
        celda[1] += intervalo.aciertos
    return [
        Intervalo(i * anchura, (i + 1) * anchura, ventanas, aciertos)
        for i, (ventanas, aciertos) in sorted(acumulado.items())
    ]


def fig_fiabilidad() -> Figure:
    """Acierto observado frente a confianza declarada, por intervalos agrupados."""
    intervalos = agrupar()
    estilo_para_impresion()
    fig, (arriba, abajo) = plt.subplots(
        2, 1, figsize=(ANCHO_DE_PAGINA, 4.6), sharex=True, height_ratios=[2.2, 1.0]
    )
    izquierda = min(i.desde for i in intervalos)

    panel(arriba, "a")
    arriba.plot([izquierda, 1.0], [izquierda, 1.0], color=INK_MUTED, ls=":", lw=1.0, zorder=1)
    arriba.text(
        izquierda + 0.06,
        izquierda + 0.035,
        "calibración perfecta",
        fontsize=6.6,
        color=INK_SECONDARY,
        rotation=30,
    )
    for intervalo in intervalos:
        escaso = intervalo.ventanas <= POCAS_PARA_DIBUJAR
        arriba.add_patch(
            Rectangle(
                (intervalo.desde, 0.0),
                intervalo.hasta - intervalo.desde,
                intervalo.exactitud,
                facecolor=CATEGORICAL[0],
                alpha=0.30 if escaso else 0.85,
                edgecolor=CATEGORICAL[0],
                linewidth=0.5,
                hatch="///" if escaso else None,
                zorder=2,
            )
        )
        # El recuento va con fondo: sobre la diagonal, el número y la línea se
        # cruzan en los tramos altos y el dígito deja de leerse.
        arriba.text(
            (intervalo.desde + intervalo.hasta) / 2,
            intervalo.exactitud + 0.035,
            str(intervalo.ventanas),
            ha="center",
            fontsize=6.4,
            color=INK_SECONDARY,
            zorder=5,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.8, "alpha": 0.85},
        )
    arriba.set_xlim(izquierda, 1.0)
    arriba.set_ylim(0.0, 1.12)
    arriba.set_ylabel("acierto observado (fracción)")
    arriba.legend(
        handles=[
            Patch(
                facecolor=CATEGORICAL[0],
                alpha=0.85,
                label=f"más de {POCAS_PARA_DIBUJAR} ventanas",
            ),
            Patch(
                facecolor=CATEGORICAL[0],
                alpha=0.30,
                hatch="///",
                label=f"{POCAS_PARA_DIBUJAR} ventanas o menos",
            ),
        ],
        loc="upper left",
        frameon=False,
        fontsize=6.6,
    )

    panel(abajo, "b")
    for intervalo in intervalos:
        abajo.add_patch(
            Rectangle(
                (intervalo.desde, 0.0),
                intervalo.hasta - intervalo.desde,
                intervalo.ventanas,
                facecolor=INK_SECONDARY,
                alpha=0.30 if intervalo.ventanas <= POCAS_PARA_DIBUJAR else 0.8,
                edgecolor=INK_SECONDARY,
                linewidth=0.5,
            )
        )
    abajo.set_xlim(izquierda, 1.0)
    abajo.set_ylim(0, max(i.ventanas for i in intervalos) + 4)
    abajo.set_xlabel(f"confianza calibrada, en intervalos de {numero(ANCHURA_DE_DIBUJO, 2)} (0–1)")
    abajo.set_ylabel("ventanas")

    fig.tight_layout()
    return fig
