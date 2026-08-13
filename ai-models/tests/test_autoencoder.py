"""Tests del detector autoencoder (F14, EXP-ANOM-006). Se saltan sin el grupo `train`."""

import numpy as np
import pytest

torch = pytest.importorskip("torch", reason="requiere `uv sync --group train` (ADR-0032)")

from ai_models.anomaly.autoencoder import AutoencoderDetector  # noqa: E402


@pytest.fixture(scope="module")
def datos() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)
    train = rng.normal(0.0, 1.0, size=(240, 42))
    outliers = rng.normal(6.0, 1.0, size=(20, 42))  # claramente fuera de la normalidad
    return train, outliers


@pytest.fixture(scope="module")
def entrenado(datos: tuple[np.ndarray, np.ndarray]) -> AutoencoderDetector:
    det = AutoencoderDetector(seed=42, epochs=40)
    det.fit(datos[0])
    return det


def test_protocolo_detector(entrenado: AutoencoderDetector, datos) -> None:
    """Cumple el Protocol de baselines: name, scores 1-D, mayor = más anómalo."""
    train, outliers = datos
    assert entrenado.name == "autoencoder_standard"
    s_norm = entrenado.scores(train)
    s_out = entrenado.scores(outliers)
    assert s_norm.shape == (len(train),)
    assert float(s_out.mean()) > float(s_norm.mean()) * 5  # outliers reconstruyen mucho peor


def test_determinismo_por_semilla(datos) -> None:
    train, outliers = datos
    a = AutoencoderDetector(seed=42, epochs=15)
    b = AutoencoderDetector(seed=42, epochs=15)
    a.fit(train)
    b.fit(train)
    assert np.allclose(a.scores(outliers), b.scores(outliers))
    c = AutoencoderDetector(seed=7, epochs=15)
    c.fit(train)
    assert not np.allclose(a.scores(outliers), c.scores(outliers))


def test_scaler_solo_train(entrenado: AutoencoderDetector, datos) -> None:
    """El scaler se ajusta con train y NO cambia al puntuar otros datos (ADR-0011)."""
    _train, outliers = datos
    mean_before = entrenado._scaler.mean_.copy()
    entrenado.scores(outliers)
    assert np.array_equal(mean_before, entrenado._scaler.mean_)


def test_presupuesto_de_parametros(entrenado: AutoencoderDetector) -> None:
    """AE pequeño por diseño (Protocolo ML v1 §5: <<100k parámetros)."""
    assert 0 < entrenado.n_parameters < 100_000


def test_embed_y_error_por_feature(entrenado: AutoencoderDetector, datos) -> None:
    _train, outliers = datos
    z = entrenado.embed(outliers)
    assert z.shape == (len(outliers), entrenado.latent)
    pfe = entrenado.per_feature_error(outliers)
    assert pfe.shape == (len(outliers), 42)
    # coherencia: la media por fila del error por feature ES el score
    assert np.allclose(pfe.mean(axis=1), entrenado.scores(outliers))


def test_scaler_robusto() -> None:
    det = AutoencoderDetector(seed=42, epochs=5, scaler_kind="robust")
    assert det.name == "autoencoder_robust"
    with pytest.raises(ValueError, match="scaler_kind"):
        AutoencoderDetector(scaler_kind="minmax")._make_scaler()


def test_sin_entrenar_falla_claro() -> None:
    det = AutoencoderDetector()
    with pytest.raises(RuntimeError, match="fit"):
        det.scores(np.zeros((3, 42)))
