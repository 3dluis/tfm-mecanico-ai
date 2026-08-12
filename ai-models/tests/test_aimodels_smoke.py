"""Smoke: el paquete importa."""

import ai_models


def test_version() -> None:
    assert ai_models.__version__
