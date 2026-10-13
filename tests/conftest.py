"""Fixtures compartidas."""

from __future__ import annotations

import pytest

from mecanico_ia_exp.config.settings import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    """La configuración se cachea; los tests que tocan el entorno parten de cero."""
    get_settings.cache_clear()


#: Los cuatro ficheros procesados de `synthetic_v2`, que el repositorio **no
#: distribuye**: `data/processed/**` está en `.gitignore` y son decenas de
#: megabytes. No hace falta distribuirlos porque el generador los reconstruye
#: bit a bit, y así está comprobado contra las huellas que el manifiesto de E19
#: congeló antes de abrir el conjunto de prueba.
FICHEROS_DEL_CONJUNTO = (
    "data/processed/synthetic_v2_x.npy",
    "data/processed/synthetic_v2_features.npy",
    "data/processed/synthetic_v2_meta.parquet",
    "data/processed/synthetic_v2_preprocess.json",
)

COMO_RECONSTRUIRLO = (
    "Este conjunto no se distribuye con el repositorio y se reconstruye de forma "
    "determinista:\n"
    "    bash scripts/reconstruir_datos.sh\n"
    "El guion lo genera, lo preprocesa y COMPRUEBA sus cuatro huellas contra las "
    "congeladas en configs/manifest_e19.json. Si coinciden, es el mismo conjunto que "
    "sostiene las cifras publicadas.\n"
    "Tarda un par de minutos y no necesita ni base de datos ni acelerador."
)


@pytest.fixture
def conjunto_preprocesado() -> None:
    """Se detiene con instrucciones si el conjunto no está reconstruido.

    No es un `skip` de conveniencia: la prueba mide algo real y lo que falta es
    un dato reconstruible, no una dependencia externa. El mensaje dice la orden
    exacta, de modo que quien lo vea sepa qué hacer en lugar de suponer que la
    prueba está rota.
    """
    from mecanico_ia_exp.config import paths

    faltan = [r for r in FICHEROS_DEL_CONJUNTO if not (paths.ROOT / r).is_file()]
    if faltan:
        pytest.skip(
            f"faltan {len(faltan)} de {len(FICHEROS_DEL_CONJUNTO)} ficheros de "
            f"synthetic_v2 preprocesado.\n{COMO_RECONSTRUIRLO}"
        )
