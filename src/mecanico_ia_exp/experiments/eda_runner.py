"""Ejecución del análisis exploratorio: produce las tablas y las figuras de E4.

Todo lo que se publica sale de aquí. Ninguna cifra de la memoria se transcribe a
mano desde una salida de consola.
"""

from __future__ import annotations

import pandas as pd

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.data.exploration import (
    class_balance,
    describe_signals,
    missingness,
    regime_balance,
    separability,
)
from mecanico_ia_exp.visualization import eda

DATASET = "synthetic_v1"


def run_eda(dataset_id: str = DATASET) -> int:
    """Genera tablas y figuras. Devuelve el código de salida del proceso."""
    origen = paths.DATA_RAW_SYNTHETIC / f"{dataset_id}.parquet"
    if not origen.is_file():
        print(f"No existe {origen}. Ejecuta antes: mecanico-exp generate-synthetic")
        return 1

    datos = pd.read_parquet(origen)
    tablas = paths.ensure(paths.TABLES)
    figuras = paths.ensure(paths.FIGURES)

    salidas: dict[str, pd.DataFrame] = {
        "E4_descriptivos": describe_signals(datos),
        "E4_ausencias": missingness(datos),
        "E4_balance_condicion": class_balance(datos),
        "E4_balance_regimen": regime_balance(datos),
        "E4_separabilidad": separability(datos),
    }
    for nombre, tabla in salidas.items():
        tabla.to_csv(tablas / f"{nombre}.csv", index=False)
        print(f"tabla   {nombre}.csv ({len(tabla)} filas)")

    for nombre, funcion in (
        ("FIG-E4-01_series_normal_vs_fallo", eda.fig_series_normal_vs_fallo),
        ("FIG-E4-02_separabilidad", eda.fig_separabilidad),
        ("FIG-E4-03_correlaciones", eda.fig_correlaciones),
        ("FIG-E4-04_distribuciones", eda.fig_distribuciones),
        ("FIG-E4-05_correlacion_cruzada", eda.fig_correlacion_cruzada),
        ("FIG-E4-06_balance", eda.fig_balance),
    ):
        funcion(datos, figuras / f"{nombre}.png")
        print(f"figura  {nombre}.png")

    return 0
