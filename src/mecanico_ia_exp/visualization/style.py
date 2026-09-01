"""Estilo común de las figuras.

Un único sitio donde se deciden colores, grosores y tipografía, para que las
figuras de la memoria se lean como un sistema y no como una colección de
gráficas hechas en momentos distintos.

Las figuras van a un documento impreso, así que se comprometen con una sola
apariencia clara y no cambian de tema.

La paleta categórica se validó antes de usarla (banda de luminosidad, suelo de
croma, separación bajo daltonismo y suelo de visión normal): las seis primeras
ranuras pasan, con la peor pareja adyacente en ΔE 9,1 bajo protanopia y 19,6 en
visión normal. Tres de las ranuras quedan por debajo de 3:1 de contraste contra
la superficie, lo que obliga a etiquetas visibles y a que exista la tabla
correspondiente: ambas cosas se cumplen en cada figura de este laboratorio.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

# Superficie y tinta
SURFACE = "#fcfcfb"
PAGE = "#f9f9f7"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

#: Ranuras categóricas, en orden fijo. Nunca se ciclan ni se generan tonos nuevos.
CATEGORICAL: tuple[str, ...] = (
    "#2a78d6",  # 1 azul
    "#eb6834",  # 2 naranja
    "#1baf7a",  # 3 agua
    "#eda100",  # 4 amarillo
    "#e87ba4",  # 5 magenta
    "#008300",  # 6 verde
    "#4a3aa7",  # 7 violeta
    "#e34948",  # 8 rojo
)

#: Identidades fijas del experimento. El color sigue a la entidad, no a su orden
#: de aparición: filtrar condiciones nunca repinta las que quedan.
COLOR_NORMAL = CATEGORICAL[0]
COLOR_FALLO = CATEGORICAL[1]

#: Divergente para magnitudes con signo (tamaños de efecto, correlaciones):
#: dos polos opuestos con un gris neutro en el centro, de modo que "cero" se lea
#: como ausencia y no como un valor más.
NEUTRAL_MID = "#f0efec"
DIVERGING = LinearSegmentedColormap.from_list(
    "exp_diverging", [CATEGORICAL[0], NEUTRAL_MID, CATEGORICAL[7]], N=256
)

#: Secuencial de un solo tono para magnitud sin signo.
SEQUENTIAL = LinearSegmentedColormap.from_list(
    "exp_sequential", ["#cde2fb", "#3987e5", "#0d366b"], N=256
)


def apply_style() -> None:
    """Fija el estilo global de matplotlib."""
    mpl.rcParams.update(
        {
            "figure.facecolor": PAGE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": PAGE,
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.labelsize": 8,
            "axes.labelcolor": INK_SECONDARY,
            "axes.edgecolor": BASELINE,
            "axes.linewidth": 0.7,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "grid.color": GRIDLINE,
            "grid.linewidth": 0.6,
            "xtick.color": INK_MUTED,
            "ytick.color": INK_MUTED,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.frameon": False,
            "legend.fontsize": 7.5,
            "lines.linewidth": 1.4,
            "lines.markersize": 3.0,
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "text.color": INK_PRIMARY,
        }
    )


def save(fig: Any, path: Path, *, close: bool = True) -> Path:
    """Guarda una figura en alta resolución."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    if close:
        import matplotlib.pyplot as plt

        plt.close(fig)
    return path
