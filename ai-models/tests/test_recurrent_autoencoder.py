"""Tests de los autoencoders recurrentes (LSTM/GRU) — F18, EXP-ANOM-009."""

import numpy as np
import pytest

pytest.importorskip("torch", reason="requiere `uv sync --group train` (ADR-0032)")

from ai_models.anomaly.recurrent_autoencoder import (
    PARAM_BUDGET,
    RecurrentAutoencoderDetector,
)

T, F = 30, 4


def _normal(n: int = 40, seed: int = 0) -> np.ndarray:
    """Secuencias normales: señales suaves con nivel y ruido estables."""
    rng = np.random.default_rng(seed)
    base = np.linspace(0, 4 * np.pi, T)
    out = np.empty((n, T, F))
    for i in range(n):
        for f in range(F):
            out[i, :, f] = 10.0 + f + np.sin(base + rng.uniform(0, 1)) + rng.normal(0, 0.05, T)
    return out


def _fitted(kind: str = "gru", epochs: int = 12, seed: int = 42) -> RecurrentAutoencoderDetector:
    det = RecurrentAutoencoderDetector(kind=kind, seed=seed, hidden=16, latent=4, epochs=epochs)
    det.fit(_normal())
    return det


@pytest.mark.parametrize("kind", ["lstm", "gru"])
def test_entrena_y_produce_scores_por_secuencia(kind: str) -> None:
    det = _fitted(kind)
    s = det.scores(_normal(n=5, seed=1))
    assert s.shape == (5,) and np.all(np.isfinite(s)) and np.all(s >= 0)
    assert det.loss_history and det.val_history
    assert det.n_parameters > 0 and det.n_parameters < PARAM_BUDGET
    assert det.registry_record()["within_param_budget"] is True


def test_kind_desconocido_falla() -> None:
    with pytest.raises(ValueError, match="kind desconocido"):
        RecurrentAutoencoderDetector(kind="rnn", epochs=1).fit(_normal(n=4))


def test_determinismo_por_semilla() -> None:
    x = _normal(n=6, seed=3)
    a = _fitted(seed=7).scores(x)
    b = _fitted(seed=7).scores(x)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, _fitted(seed=8).scores(x))


def test_error_temporal_tiene_resolucion_completa_y_agrega_coherentemente() -> None:
    det = _fitted()
    x = _normal(n=3, seed=5)
    e = det.per_step_feature_error(x)
    assert e.shape == (3, T, F)
    assert np.allclose(det.per_step_error(x), e.sum(axis=2))
    assert np.allclose(det.per_feature_error(x), e.sum(axis=1))
    # el score es el error medio ponderado por máscara (aquí todo válido)
    assert np.allclose(det.scores(x), e.sum(axis=(1, 2)) / (T * F))


def test_embed_devuelve_un_latente_por_secuencia() -> None:
    det = _fitted()
    z = det.embed(_normal(n=7, seed=2))
    assert z.shape == (7, 4)


def test_anomalia_puntual_eleva_el_score_y_se_localiza_en_el_instante_correcto() -> None:
    """Comprobación funcional mínima: el error temporal señala DÓNDE está la alteración."""
    det = _fitted(epochs=25)
    x = _normal(n=1, seed=11)
    anom = x.copy()
    anom[0, 20:24, 1] += 8.0
    assert det.scores(anom)[0] > det.scores(x)[0]
    per_step = det.per_step_error(anom)[0]
    assert 18 <= int(np.argmax(per_step)) <= 25
    assert int(np.argmax(det.per_feature_error(anom)[0])) == 1


def test_scaler_es_global_por_feature_no_por_secuencia() -> None:
    """Normalizar cada secuencia por separado borraría el desplazamiento de nivel."""
    det = RecurrentAutoencoderDetector(seed=1, hidden=8, latent=4, epochs=6)
    det.fit(_normal(n=20))
    shifted = _normal(n=1, seed=9) + 50.0  # mismo patrón, nivel muy distinto
    plain = _normal(n=1, seed=9)
    assert det.scores(shifted)[0] > det.scores(plain)[0], (
        "un desplazamiento global de nivel debe seguir siendo visible tras la normalización"
    )


def test_contrato_de_ausencias_identico_en_train_e_inferencia() -> None:
    """La máscara pondera el error y el relleno declarado no inventa señal (ADR-0027)."""
    x = _normal(n=12, seed=4)
    mask = np.ones_like(x, dtype=bool)
    mask[:, 5, 0] = False
    det = RecurrentAutoencoderDetector(seed=2, hidden=8, latent=4, epochs=6)
    det.fit(x, mask)
    e = det.per_step_feature_error(x, mask)
    assert np.all(e[:, 5, 0] == 0.0), "una celda ausente no puede aportar error"
    # el valor bajo la máscara es irrelevante: el contrato lo neutraliza igual en inferencia
    x_alt = x.copy()
    x_alt[:, 5, 0] = 999.0
    assert np.allclose(det.scores(x, mask), det.scores(x_alt, mask))
    # y una secuencia con NaN se trata exactamente igual que con la máscara
    x_nan = x.copy()
    x_nan[:, 5, 0] = np.nan
    assert np.allclose(det.scores(x_nan, mask), det.scores(x, mask))


def test_early_stopping_registra_su_mejor_epoca() -> None:
    det = RecurrentAutoencoderDetector(seed=3, hidden=8, latent=4, epochs=40, patience=2)
    det.fit(_normal(n=24))
    assert 0 <= det.best_epoch < len(det.val_history)
    assert len(det.loss_history) == len(det.val_history) <= 40


def test_sin_entrenar_falla_claro() -> None:
    det = RecurrentAutoencoderDetector()
    with pytest.raises(RuntimeError, match="sin entrenar"):
        det.scores(_normal(n=1))
    with pytest.raises(RuntimeError, match="sin entrenar"):
        det.embed(_normal(n=1))
