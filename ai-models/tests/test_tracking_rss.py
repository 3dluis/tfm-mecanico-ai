"""El instrumento de RAM interpreta ru_maxrss según la plataforma (B0.2, F-PREREG §2.5).

Hallazgo F22: ru_maxrss son KB en Linux y BYTES en macOS. La versión anterior asumía KB
siempre, de modo que toda medición hecha en macOS quedaba inflada ×1024 — y un presupuesto
edge (≤512 MB de detección, ≤6 GB de sistema) no puede verificarse con un instrumento que
mide mal. Estos tests fijan la corrección en ambas plataformas sin depender de la
plataforma en la que corran.
"""

import resource
import sys
from unittest import mock

from ai_models.tracking import peak_rss_mb


def _fake_rusage(ru_maxrss: int) -> object:
    real = resource.getrusage(resource.RUSAGE_SELF)
    m = mock.Mock(wraps=real)
    m.ru_maxrss = ru_maxrss
    return m


def test_linux_interpreta_kb() -> None:
    with (
        mock.patch.object(sys, "platform", "linux"),
        mock.patch.object(resource, "getrusage", return_value=_fake_rusage(512_000)),
    ):
        assert peak_rss_mb() == 500.0


def test_macos_interpreta_bytes() -> None:
    with (
        mock.patch.object(sys, "platform", "darwin"),
        mock.patch.object(resource, "getrusage", return_value=_fake_rusage(524_288_000)),
    ):
        assert peak_rss_mb() == 500.0


def test_misma_memoria_misma_cifra_en_ambas_plataformas() -> None:
    """500 MB reales deben medirse como 500 MB en las dos plataformas (era ×1024 antes)."""
    with (
        mock.patch.object(sys, "platform", "linux"),
        mock.patch.object(resource, "getrusage", return_value=_fake_rusage(512_000)),
    ):
        linux = peak_rss_mb()
    with (
        mock.patch.object(sys, "platform", "darwin"),
        mock.patch.object(resource, "getrusage", return_value=_fake_rusage(512_000 * 1024)),
    ):
        mac = peak_rss_mb()
    assert linux == mac == 500.0


def test_valor_real_es_plausible() -> None:
    v = peak_rss_mb()
    assert 1.0 < v < 64_000.0
