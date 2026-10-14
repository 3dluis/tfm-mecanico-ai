"""Genera las figuras de los capítulos 5 y 6 de la memoria.

**Qué es.** El único procedimiento de generación de las figuras que entran en el
documento. Cada figura de la memoria sale de aquí, y su pie remite a este guion:
eso es lo que permite que un tercero compruebe de dónde viene cada trazo.

**De dónde lee.** De las tablas versionadas de ``artifacts/tables/``, de los
registros de ``experiments/*.json`` y, en dos figuras, del conjunto procesado
``synthetic_v2``, que se reconstruye bit a bit y cuyas huellas congela
``configs/manifest_e19.json``. **No ejecuta ningún experimento, no abre ningún
conjunto de prueba y no escribe fuera de su directorio de salida.**

**Qué no puede redibujar.** Cuatro figuras se copian de donde ya estaban, porque
regenerarlas exigiría algo que no está autorizado o ya no existe:

- la serie pareada de E4 **no se puede redibujar**: la función que la hace genera
  sus propias sesiones con el generador vigente, y el generador cambió el 1 de
  septiembre de 2026. Redibujarla hoy daría otra figura;
- el límite de evidencia del termostato necesita la predicción **por ventana**,
  que el registro de E6 no guarda y que solo existió durante aquella ejecución;
- la expresión efectiva del fallo y el recorrido experimental los produce un
  notebook, y duplicar su código aquí añadiría una segunda fuente de verdad.

**Salida.** ``artifacts/figures/memoria/``, en PNG a 300 puntos por pulgada para
el documento y en SVG para quien quiera la versión vectorial.

    uv run python scripts/figuras_memoria.py            # todas
    uv run python scripts/figuras_memoria.py 5.6 5.13   # solo esas
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import textwrap
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.visualization.style import (
    BASELINE,
    CATEGORICAL,
    INK_MUTED,
    INK_SECONDARY,
    SEQUENTIAL,
    apply_style,
)

DESTINO = paths.ROOT / "artifacts" / "figures" / "memoria"
TABLAS = paths.ROOT / "artifacts" / "tables"
REGISTROS = paths.ROOT / "experiments"
HISTORICAS = paths.ROOT / "artifacts" / "figures"
SALIDA_NOTEBOOKS = paths.ROOT / "notebooks" / "salida"

#: Nombres legibles de las seis condiciones. El identificador se conserva en el
#: eje cuando la figura lo necesita para cruzarse con una tabla.
CONDICION = {
    "F00_normal": "sin fallo",
    "F01_vacuum_leak": "fuga de vacío",
    "F02_maf_drift": "deriva del caudalímetro",
    "F03_thermostat_stuck": "termostato bloqueado",
    "F04_o2_lag": "sonda lenta",
    "F05_misfire": "fallo de encendido",
}

COLOR_BOSQUE = CATEGORICAL[0]
COLOR_RED = CATEGORICAL[1]
COLOR_BIEN = CATEGORICAL[5]
COLOR_MAL = CATEGORICAL[7]


def _num(valor: float, decimales: int = 3, *, signo: bool = False) -> str:
    """Las cifras de la memoria llevan coma decimal, también dentro de la figura."""
    texto = f"{valor:+.{decimales}f}" if signo else f"{valor:.{decimales}f}"
    return texto.replace(".", ",").replace("-", "\u2212")


def _pie(fig: Figure, texto: str, *, y: float | None = None) -> None:
    """La línea de procedencia que va impresa dentro de la propia figura.

    Se parte en varias líneas según el ancho de la figura. Sin partirla, el
    recorte ajustado de matplotlib ensancha el lienzo hasta donde llegue el
    texto, y la figura entra en la página como una tira desproporcionada.
    """
    ancho = max(60, int(fig.get_figwidth() * 19))
    envuelto = "\n".join(textwrap.wrap(texto, width=ancho))
    fig.supxlabel(envuelto, fontsize=6.2, x=0.0, ha="left", color=INK_MUTED, y=y)


def _titulo(fig: Figure, texto: str) -> None:
    fig.suptitle(texto, fontsize=10.5, fontweight="bold", x=0.0, ha="left")


def guardar(fig: Figure, nombre: str) -> Path:
    DESTINO.mkdir(parents=True, exist_ok=True)
    png = DESTINO / f"{nombre}.png"
    fig.savefig(png, dpi=300)
    fig.savefig(DESTINO / f"{nombre}.svg")
    plt.close(fig)
    return png


# --------------------------------------------------------------------------- #
# Capítulo 5
# --------------------------------------------------------------------------- #


def fig_5_01_particiones() -> Figure:
    """Ventanas por clase y partición, con la etiqueta de cada ventana.

    Se cuenta por **etiqueta de ventana** y no por fallo de la sesión: las
    ventanas anteriores a la entrada del fallo en una sesión averiada son
    ventanas sin fallo, y de ahí que la clase normal doble a cada condición.
    """
    meta = pd.read_parquet(paths.DATA_PROCESSED / "synthetic_v2_meta.parquet")
    tabla = meta.groupby(["label", "partition"]).size().unstack(fill_value=0)
    orden = ["train", "validation", "test"]
    etiquetas = {"train": "entrenamiento", "validation": "validación", "test": "prueba"}

    apply_style()
    fig, eje = plt.subplots(figsize=(7.2, 3.2))
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
    _titulo(fig, "Ventanas por clase y partición")
    _pie(
        fig,
        "E5 · synthetic_v2 · reparto por sesión, nunca por ventana · "
        "la clase sin fallo dobla a cada fallo porque las sesiones averiadas "
        "aportan sus ventanas anteriores a la entrada del fallo",
    )
    fig.tight_layout()
    return fig


def fig_5_03_separabilidad() -> Figure:
    """Delta de Cliff de cada señal por condición, en nivel y en dispersión."""
    tabla = pd.read_csv(TABLAS / "E4_separabilidad.csv")
    senales = list(dict.fromkeys(tabla.signal))
    fallos = [c for c in CONDICION if c != "F00_normal"]

    apply_style()
    fig, ejes = plt.subplots(1, 2, figsize=(9.6, 5.2), sharey=True)
    for eje, (columna, titulo) in zip(
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
        eje.set_title(titulo, fontsize=9)
        eje.grid(visible=False)
    ejes[0].set_yticks(range(len(senales)))
    ejes[0].set_yticklabels(senales, fontsize=7)
    barra = fig.colorbar(imagen, ax=ejes, fraction=0.025, pad=0.02)
    barra.set_label("delta de Cliff frente a la condición sin fallo", fontsize=7)
    # El pie va por debajo de las etiquetas giradas del eje: sin este margen se
    # imprime encima de ellas, que es el defecto que esta figura venía a corregir.
    fig.subplots_adjust(bottom=0.30, top=0.86)
    _titulo(fig, "Qué señal separa cada condición, y por qué vía")
    _pie(
        fig,
        "E4 · synthetic_v1, bloques de 60 s · se etiquetan las celdas con efecto grande "
        "(|delta| ≥ 0,474) · synthetic_v1 es pre-calibración y NO se reconstruye con el "
        "generador publicado (L-25)",
        y=0.015,
    )
    return fig


def _confusion(eje: plt.Axes, matriz: pd.DataFrame, titulo: str) -> None:
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
    eje.set_title(titulo, fontsize=9)
    eje.grid(visible=False)


def fig_5_04_confusiones() -> Figure:
    """Las dos matrices juntas: lo que las separa es adónde van los errores."""
    bosque = pd.read_csv(TABLAS / "E6_baseline_confusion_synthetic_v2.csv", index_col=0)
    red = pd.read_csv(TABLAS / "E7_temporal_confusion_synthetic_v2.csv", index_col=0)

    apply_style()
    fig, ejes = plt.subplots(1, 2, figsize=(9.0, 4.2), sharey=True)
    _confusion(ejes[0], bosque, "Bosque aleatorio (E6) · 12 errores, los 12 a «sin fallo»")
    _confusion(ejes[1], red, "GRU bidireccional (E7) · 17 errores, 4 de ellos cruzados")
    ejes[0].set_ylabel("condición anotada")
    _titulo(fig, "Adónde van los errores de cada modelo")
    _pie(
        fig,
        "E6 y E7 · synthetic_v2, validación, 98 ventanas de 12 sesiones · una ejecución por "
        "modelo, semilla 20260901 · el color es la proporción de la fila · F00 sin fallo, "
        "F01 fuga de vacío, F02 deriva del caudalímetro, F03 termostato bloqueado, "
        "F04 sonda lenta, F05 fallo de encendido",
    )
    fig.tight_layout()
    return fig


def fig_5_05_por_clase() -> Figure:
    """F1 por condición de los dos modelos, y su diferencia."""
    bosque = pd.read_csv(TABLAS / "E6_baseline_por_clase_synthetic_v2.csv").set_index("label")
    red = pd.read_csv(TABLAS / "E7_temporal_por_clase_synthetic_v2.csv").set_index("label")
    clases = [c for c in CONDICION if c in bosque.index]
    diferencia = (red.loc[clases, "f1"] - bosque.loc[clases, "f1"]).to_numpy()
    orden = np.argsort(diferencia)
    clases = [clases[i] for i in orden]
    diferencia = diferencia[orden]

    apply_style()
    fig, ejes = plt.subplots(1, 2, figsize=(9.6, 3.6), gridspec_kw={"width_ratios": [1.5, 1]})
    y = np.arange(len(clases))
    ejes[0].barh(
        y - 0.19, bosque.loc[clases, "f1"], height=0.36, color=COLOR_BOSQUE, label="bosque (E6)"
    )
    ejes[0].barh(y + 0.19, red.loc[clases, "f1"], height=0.36, color=COLOR_RED, label="GRU (E7)")
    ejes[0].set_yticks(y)
    ejes[0].set_yticklabels(
        [f"{CONDICION[c]}\n(n={int(bosque.loc[c, 'support'])})" for c in clases], fontsize=7
    )
    ejes[0].set_xlabel("F1 de la clase (0–1)")
    ejes[0].set_xlim(0, 1.05)
    ejes[0].grid(visible=True, axis="x")
    ejes[0].set_axisbelow(True)
    ejes[0].legend(loc="lower right", fontsize=7)
    ejes[0].set_title("F1 de cada condición", fontsize=9)

    colores = [COLOR_RED if d > 0 else COLOR_BOSQUE for d in diferencia]
    ejes[1].barh(y, diferencia, color=colores, height=0.55)
    for i, d in enumerate(diferencia):
        ejes[1].text(
            d + (0.004 if d > 0 else -0.004),
            i,
            _num(d, 3, signo=True),
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
    ejes[1].set_title("Diferencia: a la derecha gana la red", fontsize=9)

    _titulo(fig, "La desventaja de la red no es uniforme: gana en una condición y pierde en cinco")
    _pie(
        fig,
        "E6 y E7 · synthetic_v2, validación · una ejecución por modelo, sin repeticiones ni "
        "intervalos · n es el número de ventanas de la clase en validación",
    )
    fig.tight_layout()
    return fig


def fig_5_06_calibracion() -> Figure:
    """Confianza declarada frente a acierto, antes y después de calibrar."""
    registro = json.loads((REGISTROS / "E15_suficiencia.json").read_text("utf-8"))
    calibracion = registro["calibration"]

    apply_style()
    fig, eje = plt.subplots(figsize=(5.6, 4.6))
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
            f"{etiqueta}\nECE {_num(punto['ece'])}\nsesgo {_num(punto['bias'], signo=True)}",
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
    _titulo(fig, "El modelo estaba infraconfiado, y la calibración lo centra")
    _pie(
        fig,
        f"E6, calibrado en E15 · synthetic_v2, validación, {calibracion['n_windows']} ventanas, "
        f"{calibracion['n_bins']} tramos · {calibracion['method']} · "
        "el sesgo es confianza media menos acierto; el ECE no lleva signo",
    )
    fig.tight_layout()
    return fig


def fig_5_09_confusor() -> Figure:
    """El orden se invierte entre los dos conjuntos, y cambian dos cosas a la vez."""

    def f1(nombre: str) -> float:
        return float(json.loads((REGISTROS / nombre).read_text("utf-8"))["metrics"]["macro_f1"])

    valores = {
        "synthetic_v2": (f1("E6_baseline_synthetic_v2.json"), f1("E7_temporal_synthetic_v2.json")),
        "synthetic_v3": (f1("E6_baseline_synthetic_v3.json"), f1("E7_temporal_synthetic_v3.json")),
    }

    apply_style()
    fig, eje = plt.subplots(figsize=(7.2, 3.8))
    x = np.array([0.0, 1.0])
    for desplazamiento, color, etiqueta, indice in (
        (-0.15, COLOR_BOSQUE, "bosque aleatorio (E6)", 0),
        (0.15, COLOR_RED, "GRU bidireccional (E7)", 1),
    ):
        alturas = [valores[c][indice] for c in valores]
        eje.bar(x + desplazamiento, alturas, width=0.26, color=color, label=etiqueta)
        for xi, altura in zip(x + desplazamiento, alturas, strict=True):
            eje.text(xi, altura + 0.012, _num(altura, 4), ha="center", fontsize=7.5)

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
        "entre las dos columnas cambian DOS cosas:\nel volumen y el fenómeno generado",
        xy=(0.5, 0.40),
        ha="center",
        fontsize=7.5,
        color=INK_SECONDARY,
    )
    eje.annotate(
        "",
        xy=(0.19, 0.60),
        xytext=(0.81, 0.60),
        arrowprops={"arrowstyle": "<->", "color": INK_MUTED, "lw": 0.9},
    )
    _titulo(fig, "El orden se invierte, y la comparación no dice por qué")
    _pie(
        fig,
        "E6 y E7 sobre los dos conjuntos · una ejecución por celda · la conclusión «el límite "
        "era el volumen» quedó retirada el 12-10-2026 · synthetic_v3 es pre-calibración y no "
        "se reconstruye (L-25)",
    )
    fig.tight_layout()
    return fig


def fig_5_11_recuperacion() -> Figure:
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

    apply_style()
    fig, ejes = plt.subplots(1, 2, figsize=(9.6, 3.4), gridspec_kw={"width_ratios": [1, 1.25]})
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

    _titulo(fig, "Sin el código de avería, la similitud semántica no encuentra el procedimiento")
    _pie(
        fig,
        "E12, reejecución canónica del 13-09-2026 · corpus del vehículo de referencia · "
        "6 casos anotados, 5 puntuados; el sexto tiene la evidencia retirada del índice y no "
        "entra en las métricas · la estrategia guiada usa los códigos de la condición ANOTADA, "
        "que el sistema no tiene antes de diagnosticar: su ventaja es una cota asistida",
    )
    fig.tight_layout()
    return fig


def _tasas_e15() -> dict[str, tuple[int, int]]:
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


def fig_5_13_ablaciones() -> Figure:
    """Qué componente sostiene el resultado, y cuál es sustituible."""
    filas: list[tuple[str, int, int, int, int, str]] = []
    canonica = _tasas_e15()
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

    apply_style()
    fig, ejes = plt.subplots(1, 2, figsize=(9.6, 3.8), sharey=True)
    y = np.arange(len(filas))
    for eje, (indice_num, indice_den, titulo, color) in zip(
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
        eje.set_title(titulo, fontsize=9)
        eje.set_xlabel("ejecuciones (recuento)")
        eje.set_xlim(0, max(denominadores) + 2.2)
        eje.grid(visible=True, axis="x")
        eje.set_axisbelow(True)
    ejes[0].set_yticks(y)
    ejes[0].set_yticklabels([f[0] for f in filas], fontsize=7)
    ejes[0].invert_yaxis()

    _titulo(fig, "Lo que sostiene el resultado es el criterio de suficiencia, no la atribución")
    _pie(
        fig,
        "E18, ablaciones pre-registradas, ejecutadas el 1-10-2026 · synthetic_v2, los mismos 17 "
        "casos · la falsa confianza se cuenta sobre 9 ejecuciones de 3 ventanas y la abstención "
        "sobre 5 de 5 ventanas · A2 quedó INCONCLUSA: la ruta léxica no recupera nada con una "
        "consulta en prosa, y la causa no es la ablación sino la consulta",
    )
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- #
# Capítulo 6
# --------------------------------------------------------------------------- #


def fig_6_01_objetivos() -> Figure:
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

    apply_style()
    fig, eje = plt.subplots(figsize=(8.4, 3.6))
    for i, (identificador, nombre, evidencia, estado) in enumerate(objetivos):
        y = len(objetivos) - i - 1
        eje.add_patch(
            plt.Rectangle((0, y - 0.38), 10, 0.76, color=colores[estado], alpha=0.14, lw=0)
        )
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
    _titulo(fig, "Qué sostiene cada objetivo, y hasta dónde")
    _pie(
        fig,
        "elaboración propia a partir del capítulo 6 y de docs/experiment-index.md · sin conjunto "
        "de datos: es el mapa de lo que el capítulo declara, no una medición · «parcial» es la "
        "palabra que usa el texto, y no se redondea hacia arriba",
    )
    fig.tight_layout()
    return fig


def fig_6_02_compromiso() -> Figure:
    """Los dos errores del sistema y los de las dos políticas triviales."""
    tasas = _tasas_e15()
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

    apply_style()
    fig, eje = plt.subplots(figsize=(6.6, 4.6))
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
    _titulo(fig, "Cada política trivial iguala al sistema en un error y lo empeora en el otro")
    _pie(
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


@dataclass(frozen=True)
class Figura:
    identificador: str
    nombre: str
    dibuja: Callable[[], Figure] | None = None
    copia_de: Path | None = None
    motivo_de_la_copia: str = ""
    extras: tuple[str, ...] = field(default_factory=tuple)


FIGURAS: tuple[Figura, ...] = (
    Figura("5.1", "FIG-5-01_particiones", fig_5_01_particiones),
    Figura(
        "5.2",
        "FIG-5-02_series_normal_vs_fallo",
        copia_de=HISTORICAS / "FIG-E4-01_series_normal_vs_fallo.png",
        motivo_de_la_copia=(
            "no se puede redibujar: la función genera sus propias sesiones con el generador "
            "vigente, y el generador cambió el 1-09-2026"
        ),
    ),
    Figura("5.3", "FIG-5-03_separabilidad", fig_5_03_separabilidad),
    Figura("5.4", "FIG-5-04_confusiones", fig_5_04_confusiones),
    Figura("5.5", "FIG-5-05_f1_por_clase", fig_5_05_por_clase),
    Figura("5.6", "FIG-5-06_calibracion", fig_5_06_calibracion),
    Figura(
        "5.7",
        "FIG-5-07_limite_evidencia_termostato",
        copia_de=HISTORICAS / "FIG-E6-02_limite_evidencia_f03.png",
        motivo_de_la_copia=(
            "necesita la predicción por ventana, que el registro de E6 no guarda y que solo "
            "existió durante aquella ejecución"
        ),
    ),
    Figura(
        "5.8",
        "FIG-5-08_expresion_del_fallo",
        copia_de=SALIDA_NOTEBOOKS / "06_expresion" / "FIG-N06-01_expresion_y_aciertos.png",
        motivo_de_la_copia="la produce el notebook 06; duplicar su código daría dos fuentes de verdad",
        extras=("svg",),
    ),
    Figura("5.9", "FIG-5-09_confusor_volumen", fig_5_09_confusor),
    Figura(
        "5.10",
        "FIG-5-10_mapa_atribucion",
        copia_de=SALIDA_NOTEBOOKS / "04_explicabilidad" / "FIG-NB04-01_mapa_atribucion.png",
        motivo_de_la_copia="la produce el notebook 04, que calcula el mapa de señales declaradas",
        extras=("svg",),
    ),
    Figura("5.11", "FIG-5-11_recuperacion", fig_5_11_recuperacion),
    Figura(
        "5.12",
        "FIG-5-12_aplicables_vs_cobertura",
        copia_de=SALIDA_NOTEBOOKS / "05_suficiencia" / "FIG-N05-01_aplicables_vs_cobertura.png",
        motivo_de_la_copia="la produce el notebook 05, corregido el 13-10-2026 para dibujar las cinco condiciones",
        extras=("svg",),
    ),
    Figura("5.13", "FIG-5-13_ablaciones", fig_5_13_ablaciones),
    Figura(
        "5.14",
        "FIG-5-14_evaluacion_final",
        copia_de=SALIDA_NOTEBOOKS / "03_analisis_e19" / "FIG-NB03-01_primario.png",
        motivo_de_la_copia="la produce el notebook 03",
        extras=("svg",),
    ),
    Figura(
        "5.15",
        "FIG-5-15_decisiones_e19",
        copia_de=SALIDA_NOTEBOOKS / "03_analisis_e19" / "FIG-NB03-02_decisiones.png",
        motivo_de_la_copia="la produce el notebook 03",
        extras=("svg",),
    ),
    Figura("6.1", "FIG-6-01_objetivos_y_evidencia", fig_6_01_objetivos),
    Figura("6.2", "FIG-6-02_compromiso_cobertura_abstencion", fig_6_02_compromiso),
    Figura(
        "6.3",
        "FIG-6-03_recorrido_experimental",
        copia_de=SALIDA_NOTEBOOKS / "00_introduccion" / "FIG-NB00-01_recorrido.png",
        motivo_de_la_copia="la produce el notebook 00",
        extras=("svg",),
    ),
)


def producir(figura: Figura) -> Path | None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    if figura.dibuja is not None:
        return guardar(figura.dibuja(), figura.nombre)
    assert figura.copia_de is not None
    if not figura.copia_de.is_file():
        print(
            f"  {figura.identificador:5s} FALTA el origen: "
            f"{figura.copia_de.relative_to(paths.ROOT)}",
            file=sys.stderr,
        )
        return None
    destino = DESTINO / f"{figura.nombre}.png"
    shutil.copy2(figura.copia_de, destino)
    for extra in figura.extras:
        origen = figura.copia_de.with_suffix(f".{extra}")
        if origen.is_file():
            shutil.copy2(origen, DESTINO / f"{figura.nombre}.{extra}")
    return destino


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("identificadores", nargs="*")
    args = analizador.parse_args(argv)

    pedidas = set(args.identificadores)
    faltan = pedidas - {f.identificador for f in FIGURAS}
    if faltan:
        print(f"no existen: {', '.join(sorted(faltan))}", file=sys.stderr)
        return 1

    fallos = 0
    for figura in FIGURAS:
        if pedidas and figura.identificador not in pedidas:
            continue
        destino = producir(figura)
        if destino is None:
            fallos += 1
            continue
        como = "dibujada" if figura.dibuja is not None else "copiada"
        print(f"  {figura.identificador:5s} {como:9s} {destino.relative_to(paths.ROOT)}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
