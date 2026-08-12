"""Smoke: el paquete importa y el CLI responde."""

from obd_lab import __version__
from obd_lab.cli import main


def test_version() -> None:
    assert __version__


def test_cli() -> None:
    assert main([]) == 0
