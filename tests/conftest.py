"""Fixtures compartidas."""

from __future__ import annotations

import pytest

from mecanico_ia_exp.config.settings import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    """La configuración se cachea; los tests que tocan el entorno parten de cero."""
    get_settings.cache_clear()
