"""Tests de la capa SHAP (requieren grupo train) — background, dimensiones, artefacto."""

import numpy as np
import pytest

pytest.importorskip("shap", reason="requiere `uv sync --group train` (ADR-0032/0033)")
pytest.importorskip("torch", reason="requiere `uv sync --group train`")

from ai_models.anomaly.autoencoder import AutoencoderDetector
from ai_models.xai.shap_runner import (
    ShapExplainer,
    attributions_as_dict,
    explanation_artifact,
    select_background,
)
from mecanico_contracts.features import FEATURE_NAMES


@pytest.fixture(scope="module")
def entorno() -> tuple:
    rng = np.random.default_rng(42)
    train = rng.normal(0.0, 1.0, size=(200, 42))
    det = AutoencoderDetector(seed=42, epochs=30)
    det.fit(train)
    bg, meta = select_background(train, size=50, seed=42)
    return train, det, bg, meta


def test_background_solo_train_y_reproducible(entorno) -> None:
    train, _det, bg, meta = entorno
    # todas las filas del background provienen de train (por identidad de fila)
    train_rows = {row.tobytes() for row in train}
    assert all(row.tobytes() in train_rows for row in bg)
    _bg2, meta2 = select_background(train, size=50, seed=42)
    assert meta["background_hash"] == meta2["background_hash"]  # determinista
    _bg3, meta3 = select_background(train, size=50, seed=7)
    assert meta["background_hash"] != meta3["background_hash"]  # depende de la semilla


def test_shap_dimensiones_y_funcion_declarada(entorno) -> None:
    _train, det, bg, _meta = entorno
    ex = ShapExplainer(det, bg, max_evals=100)
    x = np.random.default_rng(0).normal(4.0, 1.0, size=(2, 42))
    vals = ex.explain(x)
    assert vals.shape == (2, 42)
    rec = ex.registry_record()
    assert rec["explained_output"] == "reconstruction_error"
    assert rec["shap_version"] and rec["explainer_type"].startswith("shap.explainers")
    d = attributions_as_dict(vals[0])
    assert list(d) == list(FEATURE_NAMES)


def test_artefacto_de_explicacion_contrato_f15(entorno) -> None:
    _train, det, bg, meta = entorno
    ex = ShapExplainer(det, bg, max_evals=100)
    x = np.zeros((1, 42))
    art = explanation_artifact(
        window_id="s@0s",
        session_id="s",
        model_id="m@1",
        anomaly_score=0.5,
        threshold=0.3,
        shap_values=attributions_as_dict(ex.explain(x)[0]),
        per_feature_error=dict(zip(FEATURE_NAMES, det.per_feature_error(x)[0], strict=True)),
        background_meta=meta,
        explainer_record=ex.registry_record(),
    )
    for campo in (
        "window_id",
        "anomaly_score",
        "top_features",
        "shap_values",
        "reconstruction_error",
        "reference_baseline",
        "explainer",
    ):
        assert campo in art
    assert len(art["top_features"]) == 5
