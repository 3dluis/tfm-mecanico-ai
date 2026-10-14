"""Lo que comparten todas las figuras de la memoria: medidas, estilo y rutas.

**Qué NO hay aquí, desde el 14 de octubre de 2026.** No hay ayudante para poner
un título dentro de la figura ni para escribirle un pie de procedencia. Los dos
existieron y se retiraron: una imagen con su título y su fuente incrustados
obliga a regenerar el PNG para corregir una errata, se queda fuera del índice de
figuras del documento y duplica un texto que el documento ya lleva.

El reparto es el siguiente, y solo lo incumplen los artefactos históricos, que
no se pueden regenerar y lo declaran:

* **dentro de la imagen**: ejes, unidades, categorías, valores, leyendas, barras
  de color, umbrales, intervalos, las anotaciones técnicas sin las cuales el
  gráfico se lee mal, y el identificador de panel «(a)», «(b)»;
* **en el documento**, como texto editable: el número, el título, la fuente, el
  experimento, el conjunto, el protocolo y la interpretación.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
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

#: Se reexportan para que cada módulo de figura importe de un solo sitio.
__all__ = [
    "ANCHO_DE_PAGINA",
    "BASELINE",
    "CATEGORICAL",
    "COLOR_BIEN",
    "COLOR_BOSQUE",
    "COLOR_MAL",
    "COLOR_RED",
    "CONDICION",
    "CONTRAFACTUAL",
    "DESTINO",
    "HISTORICAS",
    "INK_MUTED",
    "INK_SECONDARY",
    "REGISTROS",
    "SALIDA_NOTEBOOKS",
    "SEQUENTIAL",
    "TABLAS",
    "estilo_para_impresion",
    "guardar",
    "numero",
    "panel",
]

#: Dónde se escriben las figuras del documento, y de dónde se leen sus datos.
DESTINO = paths.ROOT / "artifacts" / "figures" / "memoria"
TABLAS = paths.ROOT / "artifacts" / "tables"
REGISTROS = paths.ROOT / "experiments"
HISTORICAS = paths.ROOT / "artifacts" / "figures"
SALIDA_NOTEBOOKS = paths.ROOT / "notebooks" / "salida"

#: El artefacto derivado del análisis contrafactual T2. Lo produce
#: `scripts/contrafactual_t2.py`, vive en su propio directorio y **no es un
#: conjunto de datos**: no tiene ventanado ni particiones, no entra en ningún
#: entrenamiento y no modifica ninguna métrica. Las figuras que lo usan lo
#: declaran en su pie.
CONTRAFACTUAL = paths.ROOT / "artifacts" / "contrafactual" / "T2_contrafactual_synthetic_v2.parquet"

#: Nombres legibles de las seis condiciones. El identificador se conserva en el
#: eje cuando la figura lo necesita para cruzarse con una tabla.
CONDICION: dict[str, str] = {
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

#: Ancho útil de la página con los márgenes de la plantilla: 21 cm menos 3,0 a
#: cada lado son 15 cm, que son 5,9 pulgadas. Una figura más ancha que esto la
#: escala el procesador de textos al entrar, y el escalado encoge las etiquetas:
#: a 9,6 pulgadas, una etiqueta de 7 puntos se imprime a 4,3. Dibujar a la medida
#: de la página es lo que hace que un punto de la figura sea un punto en el papel.
ANCHO_DE_PAGINA = 5.9


def estilo_para_impresion() -> None:
    """El estilo común del laboratorio, con los cuerpos subidos para leer en papel."""
    apply_style()
    mpl.rcParams.update(
        {
            "font.size": 8.5,
            "axes.titlesize": 9.5,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
        }
    )


def numero(valor: float, decimales: int = 3, *, signo: bool = False) -> str:
    """Las cifras de la memoria llevan coma decimal, también dentro de la figura."""
    texto = f"{valor:+.{decimales}f}" if signo else f"{valor:.{decimales}f}"
    # El signo menos tipográfico, no el guion: es el que se imprime bien.
    return texto.replace(".", ",").replace("-", "\N{MINUS SIGN}")


def panel(eje: Axes, letra: str) -> None:
    """El identificador discreto de un panel: «(a)», «(b)», «(c)».

    **Por qué una letra y no un título.** Lo que cada panel muestra se explica en
    el pie de la figura, que es texto del documento y entra en el índice de
    figuras. Un título narrativo dentro de la imagen duplica esa explicación, se
    queda fuera del índice y no se puede corregir sin regenerar el PNG. La letra
    basta para que el pie pueda referirse a cada panel sin ambigüedad.
    """
    eje.set_title(f"({letra})", fontsize=9, fontweight="bold", loc="left", pad=6)


def guardar(fig: Figure, nombre: str) -> Path:
    """Escribe la figura en PNG a 300 puntos por pulgada y en SVG."""
    DESTINO.mkdir(parents=True, exist_ok=True)
    png = DESTINO / f"{nombre}.png"
    fig.savefig(png, dpi=300)
    fig.savefig(DESTINO / f"{nombre}.svg")
    plt.close(fig)
    return png
