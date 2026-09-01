"""Modelo temporal: normalización sin fuga, dispositivo declarado y contrato de salida."""

from __future__ import annotations

import numpy as np
import pytest

from mecanico_ia_exp.models.temporal import (
    Standardizer,
    TemporalConfig,
    build_model,
    count_parameters,
    resolve_device,
)
from mecanico_ia_exp.models.training import train_temporal

CLASES = ("A", "B")


def _series(n: int = 48, pasos: int = 40, senales: int = 3, seed: int = 0):
    rng = np.random.default_rng(seed)
    a = rng.normal(0.0, 0.3, (n // 2, pasos, senales)).astype(np.float32)
    b = rng.normal(2.0, 0.3, (n // 2, pasos, senales)).astype(np.float32)
    x = np.concatenate([a, b]).astype(np.float32)
    y = np.array(["A"] * (n // 2) + ["B"] * (n // 2), dtype=np.str_)
    return x, y


# ------------------------------------------------------------ normalización


def test_la_normalizacion_deja_media_cero_y_escala_uno() -> None:
    x, _ = _series(seed=1)
    z = Standardizer.fit(x).transform(x)
    assert np.allclose(z.mean(axis=(0, 1)), 0.0, atol=1e-4)
    assert np.allclose(z.std(axis=(0, 1)), 1.0, atol=1e-4)


def test_una_senal_constante_no_divide_por_cero() -> None:
    x = np.ones((6, 10, 2), dtype=np.float32)
    z = Standardizer.fit(x).transform(x)
    assert np.isfinite(z).all()
    assert np.allclose(z, 0.0)


def test_los_estadisticos_salen_solo_del_entrenamiento() -> None:
    """Ajustarlos sobre el conjunto completo filtra la escala de validación a
    entrenamiento. Es una fuga sutil que el auditor de particiones no ve."""
    x_train, _ = _series(seed=2)
    x_val = x_train * 10.0 + 100.0

    estandarizador = Standardizer.fit(x_train)
    z_val = estandarizador.transform(x_val)

    # Si los estadísticos hubieran visto validación, quedaría centrada en cero.
    assert abs(float(z_val.mean())) > 1.0, "la normalización usó datos de validación"


# ---------------------------------------------------------------- modelo


def test_el_dispositivo_nunca_es_cuda() -> None:
    assert resolve_device() in {"mps", "cpu"}


def test_el_modelo_produce_un_logit_por_clase() -> None:
    import torch

    modelo = build_model(n_signals=3, n_classes=len(CLASES), config=TemporalConfig())
    salida = modelo(torch.zeros(5, 40, 3))
    assert salida.shape == (5, len(CLASES))


def test_el_recuento_de_parametros_es_positivo() -> None:
    modelo = build_model(3, 2, TemporalConfig(hidden_size=8))
    assert count_parameters(modelo) > 0


def test_una_configuracion_mas_ancha_tiene_mas_parametros() -> None:
    pequeno = count_parameters(build_model(3, 2, TemporalConfig(hidden_size=8)))
    grande = count_parameters(build_model(3, 2, TemporalConfig(hidden_size=32)))
    assert grande > pequeno


# ------------------------------------------------------------ entrenamiento


@pytest.fixture(scope="module")
def entrenado():
    x, y = _series(n=64, seed=3)
    xv, yv = _series(n=32, seed=4)
    return train_temporal(
        x,
        y,
        xv,
        yv,
        classes=CLASES,
        config=TemporalConfig(hidden_size=8, max_epochs=25, patience=25),
        device="cpu",
        verbose=False,
    )


def test_el_modelo_aprende_un_problema_separable(entrenado) -> None:
    xv, yv = _series(n=32, seed=4)
    assert float((entrenado.predict(xv) == yv).mean()) > 0.9


def test_las_probabilidades_suman_uno_y_respetan_el_orden_de_clases(entrenado) -> None:
    xv, _ = _series(n=32, seed=4)
    p = entrenado.predict_proba(xv)
    assert p.shape == (xv.shape[0], len(CLASES))
    assert np.allclose(p.sum(axis=1), 1.0)
    assert entrenado.classes == CLASES


def test_el_dispositivo_queda_registrado(entrenado) -> None:
    """Un resultado en CPU y otro en MPS no son intercambiables; ocultarlo los
    haría parecer comparables."""
    assert entrenado.device == "cpu"


def test_la_traza_del_entrenamiento_se_conserva(entrenado) -> None:
    h = entrenado.history
    assert len(h.train_loss) == len(h.val_loss) == len(h.val_macro_f1)
    assert 0 <= h.best_epoch < len(h.val_macro_f1)
    assert h.best_val_macro_f1 == max(h.val_macro_f1)


def test_se_restaura_el_mejor_estado_y_no_el_ultimo(entrenado) -> None:
    """Seguir entrenando pasado el óptimo empeora; quedarse con el último estado
    equivaldría a ignorar la parada temprana."""
    xv, yv = _series(n=32, seed=4)
    from sklearn.metrics import f1_score

    f1 = f1_score(yv, entrenado.predict(xv), average="macro", zero_division=0)
    assert f1 >= entrenado.history.best_val_macro_f1 - 1e-6
