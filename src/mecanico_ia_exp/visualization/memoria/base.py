"""Lo que comparten todas las figuras de la memoria: medidas, estilo y rutas."""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
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
    "pie",
    "titulo",
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


def pie(fig: Figure, texto: str, *, y: float | None = None) -> None:
    """La línea de procedencia que va impresa dentro de la propia figura.

    Se parte en varias líneas según el ancho de la figura. Sin partirla, el
    recorte ajustado de matplotlib ensancha el lienzo hasta donde llegue el
    texto, y la figura entra en la página como una tira desproporcionada.
    """
    ancho = max(60, int(fig.get_figwidth() * 19))
    envuelto = "\n".join(textwrap.wrap(texto, width=ancho))
    fig.supxlabel(envuelto, fontsize=6.2, x=0.0, ha="left", color=INK_MUTED, y=y)


def titulo(fig: Figure, texto: str) -> None:
    fig.suptitle(texto, fontsize=10.5, fontweight="bold", x=0.0, ha="left")


def guardar(fig: Figure, nombre: str) -> Path:
    """Escribe la figura en PNG a 300 puntos por pulgada y en SVG."""
    DESTINO.mkdir(parents=True, exist_ok=True)
    png = DESTINO / f"{nombre}.png"
    fig.savefig(png, dpi=300)
    fig.savefig(DESTINO / f"{nombre}.svg")
    plt.close(fig)
    return png
