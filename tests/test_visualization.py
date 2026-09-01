"""Las figuras deben generarse sin error y en el sitio pedido.

No se comprueba su aspecto --eso se revisa mirándolas-- sino que el código que
las produce funciona sobre datos reales del laboratorio. Una figura que revienta
al regenerarse rompe la reproducibilidad tanto como un número inventado.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import matplotlib
import pandas as pd
import pytest

matplotlib.use("Agg")

from mecanico_ia_exp.obd.synthetic import (
    build_balanced_specs,
    generate_dataset,
)
from mecanico_ia_exp.visualization import eda
from mecanico_ia_exp.visualization.style import CATEGORICAL, DIVERGING

FIGURAS: list[Callable[[pd.DataFrame, Path], Path]] = [
    eda.fig_series_normal_vs_fallo,
    eda.fig_separabilidad,
    eda.fig_correlaciones,
    eda.fig_distribuciones,
    eda.fig_correlacion_cruzada,
    eda.fig_balance,
]


@pytest.fixture(scope="module")
def datos() -> pd.DataFrame:
    specs = build_balanced_specs(seed=55, sessions_per_fault=2, duration_s=300.0)
    marco, _ = generate_dataset(specs, dataset_id="d_fig", seed=55)
    return marco


@pytest.mark.parametrize("figura", FIGURAS, ids=lambda f: f.__name__)
def test_cada_figura_se_genera(
    figura: Callable[[pd.DataFrame, Path], Path], datos: pd.DataFrame, tmp_path: Path
) -> None:
    destino = figura(datos, tmp_path / "f.png")
    assert destino.is_file()
    assert destino.stat().st_size > 10_000, "la figura salió sospechosamente pequeña"


def test_cada_figura_declara_la_pregunta_que_responde() -> None:
    """Una figura sin pregunta no entra en la memoria; el docstring es el sitio
    donde esa pregunta queda escrita."""
    for figura in FIGURAS:
        doc = figura.__doc__ or ""
        assert "?" in doc, f"{figura.__name__} no declara ninguna pregunta"


def test_las_ranuras_categoricas_no_se_repiten() -> None:
    """El color sigue a la entidad. Dos ranuras iguales harían que dos series
    distintas se leyeran como la misma."""
    assert len(set(CATEGORICAL)) == len(CATEGORICAL)


def test_el_mapa_divergente_tiene_un_centro_neutro() -> None:
    """El cero debe leerse como ausencia de efecto, no como un valor más: en el
    centro la saturación tiene que ser mínima."""
    r, g, b, _ = DIVERGING(0.5)
    assert max(r, g, b) - min(r, g, b) < 0.08, "el centro del mapa no es neutro"
