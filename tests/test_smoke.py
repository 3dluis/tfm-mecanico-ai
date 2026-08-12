"""Prueba de humo: el paquete y sus componentes se importan correctamente."""

import importlib

import mecanico_ia

COMPONENTES = [
    "vehicle_sim",
    "acquisition",
    "storage",
    "anomaly",
    "rag",
    "memory",
    "agent",
    "api",
]


def test_version() -> None:
    assert mecanico_ia.__version__


def test_importa_componentes() -> None:
    for comp in COMPONENTES:
        assert importlib.import_module(f"mecanico_ia.{comp}")
