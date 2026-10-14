"""Por qué dos fallos que el agregado confunde acaban distinguiéndose.

La fuga de vacío y la deriva del caudalímetro empobrecen la mezcla las dos, y la
centralita responde a las dos subiendo las correcciones de combustible. En el
nivel de esas correcciones son **indistinguibles**. Este módulo mide con qué
descriptores se separan, y comprueba qué hace el cociente informado por la
física que se construyó precisamente para delatar un caudalímetro que subestima.

Todo sale del conjunto procesado `synthetic_v2` y del delta de Cliff que el
laboratorio ya usa. No ejecuta ningún experimento y no escribe ningún valor a mano.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.exploration import cliffs_delta
from mecanico_ia_exp.features.temporal import FEATURE_NAMES, RATIO_NAME
from mecanico_ia_exp.visualization.memoria.base import (
    ANCHO_DE_PAGINA,
    BASELINE,
    CATEGORICAL,
    CONDICION,
    INK_SECONDARY,
    estilo_para_impresion,
    numero,
    panel,
)

#: Las dos condiciones que empobrecen la mezcla, y la referencia.
FUGA = "F01_vacuum_leak"
DERIVA = "F02_maf_drift"
SIN_FALLO = "F00_normal"

#: Corte convencional del efecto grande para el delta de Cliff. Es una
#: convención de lectura, no un resultado.
EFECTO_GRANDE = 0.474

#: Cuántos descriptores se toman de cada extremo del orden. La figura muestra la
#: unión de los que mejor separan de la condición sin fallo y los que mejor
#: separan las dos condiciones entre sí, más el cociente declarado.
CUANTOS = 4


def _rasgos() -> tuple[np.ndarray, pd.DataFrame]:
    """Solo la partición de entrenamiento.

    Una figura descriptiva no justifica mirar el conjunto reservado: las
    ventanas de prueba se quedan fuera, y las de validación también, de modo que
    nada de lo que esta figura muestra procede de datos que el trabajo declara
    no haber abierto para explorar.
    """
    rasgos = np.load(paths.DATA_PROCESSED / "synthetic_v2_features.npy")
    meta = pd.read_parquet(paths.DATA_PROCESSED / "synthetic_v2_meta.parquet")
    de_entrenamiento = (meta.partition == "train").to_numpy()
    return rasgos[de_entrenamiento], meta[de_entrenamiento].reset_index(drop=True)


def separabilidad_entre_mezclas_pobres() -> pd.DataFrame:
    """Delta de Cliff de los 139 descriptores, en las tres comparaciones que importan.

    `entre_los_dos` responde «¿distingue esta característica una condición de la
    otra?»; `frente_a_sin_fallo` responde «¿delata que algo va mal?», y se toma
    el **menor** de los dos fallos, porque un descriptor solo sirve de aviso si
    delata a los dos.
    """
    rasgos, meta = _rasgos()
    etiquetas = meta.label.to_numpy()
    fuga = rasgos[etiquetas == FUGA]
    deriva = rasgos[etiquetas == DERIVA]
    normal = rasgos[etiquetas == SIN_FALLO]

    filas = [
        {
            "descriptor": nombre,
            "entre_los_dos": abs(cliffs_delta(fuga[:, i], deriva[:, i])),
            "fuga_vs_sin_fallo": abs(cliffs_delta(fuga[:, i], normal[:, i])),
            "deriva_vs_sin_fallo": abs(cliffs_delta(deriva[:, i], normal[:, i])),
        }
        for i, nombre in enumerate(FEATURE_NAMES)
    ]
    tabla = pd.DataFrame(filas)
    tabla["frente_a_sin_fallo"] = tabla[["fuga_vs_sin_fallo", "deriva_vs_sin_fallo"]].min(axis=1)
    return tabla


def _seleccion(tabla: pd.DataFrame) -> list[str]:
    """Regla declarada: los mejores de cada extremo, más el cociente de la física."""
    avisan = list(tabla.nlargest(CUANTOS, "frente_a_sin_fallo").descriptor)
    distinguen = list(tabla.nlargest(CUANTOS, "entre_los_dos").descriptor)
    elegidos: list[str] = []
    for nombre in [*avisan, *distinguen, RATIO_NAME]:
        if nombre not in elegidos:
            elegidos.append(nombre)
    return elegidos


def fig_mezcla_pobre() -> Figure:
    """Lo que las iguala, lo que las separa, y el descriptor que no cumplió."""
    rasgos, meta = _rasgos()
    tabla = separabilidad_entre_mezclas_pobres()

    estilo_para_impresion()
    fig, ejes = plt.subplots(
        2, 1, figsize=(ANCHO_DE_PAGINA, 6.4), gridspec_kw={"height_ratios": [1.0, 1.25]}
    )

    # Arriba: las dos correcciones de combustible, que es donde el taller
    # miraría. Las dos condiciones caen en la misma región.
    i_corto = FEATURE_NAMES.index("stft_bank1_mean")
    i_largo = FEATURE_NAMES.index("ltft_bank1_mean")
    puntos = pd.DataFrame(
        {
            "ajuste a corto plazo (%)": rasgos[:, i_corto],
            "ajuste a largo plazo (%)": rasgos[:, i_largo],
            "condición": [CONDICION[e] for e in meta.label],
        }
    )
    interes = [CONDICION[c] for c in (SIN_FALLO, FUGA, DERIVA)]
    sns.scatterplot(
        data=puntos[puntos["condición"].isin(interes)],
        x="ajuste a corto plazo (%)",
        y="ajuste a largo plazo (%)",
        hue="condición",
        hue_order=interes,
        palette=[BASELINE, CATEGORICAL[0], CATEGORICAL[1]],
        s=16,
        alpha=0.75,
        edgecolor="none",
        ax=ejes[0],
    )
    panel(ejes[0], "a")
    ejes[0].legend(loc="upper left", fontsize=6.8, title=None, frameon=False)
    ejes[0].grid(visible=True)
    ejes[0].set_axisbelow(True)

    # Abajo: qué descriptor avisa de que algo va mal, y cuál distingue cuál es.
    elegidos = _seleccion(tabla)
    datos = tabla.set_index("descriptor").loc[elegidos]
    y = np.arange(len(elegidos))
    ejes[1].barh(
        y - 0.19,
        datos.frente_a_sin_fallo.to_numpy(float),
        height=0.36,
        color=BASELINE,
        label="delata que algo va mal (frente a la condición sin fallo)",
    )
    ejes[1].barh(
        y + 0.19,
        datos.entre_los_dos.to_numpy(float),
        height=0.36,
        color=CATEGORICAL[2],
        label="distingue una avería de la otra",
    )
    for i, (aviso, entre) in enumerate(
        zip(datos.frente_a_sin_fallo, datos.entre_los_dos, strict=True)
    ):
        ejes[1].text(
            float(aviso) + 0.012, i - 0.19, numero(float(aviso), 2), va="center", fontsize=6.3
        )
        ejes[1].text(
            float(entre) + 0.012, i + 0.19, numero(float(entre), 2), va="center", fontsize=6.3
        )
    ejes[1].axvline(EFECTO_GRANDE, color=INK_SECONDARY, lw=0.8, ls="--")
    ejes[1].annotate(
        "efecto grande",
        xy=(EFECTO_GRANDE + 0.012, len(elegidos) - 0.35),
        fontsize=6.3,
        color=INK_SECONDARY,
    )
    etiquetas = [
        f"{n}\n(el cociente informado por la física)" if n == RATIO_NAME else n for n in elegidos
    ]
    ejes[1].set_yticks(y)
    ejes[1].set_yticklabels(etiquetas, fontsize=6.8)
    ejes[1].invert_yaxis()
    ejes[1].set_xlim(0.0, 1.16)
    ejes[1].set_xlabel("|delta de Cliff| (0 solape total, 1 separación completa)")
    panel(ejes[1], "b")
    ejes[1].legend(loc="lower center", bbox_to_anchor=(0.5, -0.40), ncol=1, fontsize=6.8)
    ejes[1].grid(visible=True, axis="x")
    ejes[1].set_axisbelow(True)
    fig.tight_layout()
    return fig
