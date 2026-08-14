"""Ejecución SHAP sobre detectores — reglas de la Adenda XAI v1 §§15, 20-22 (ADR-0033).

- La función explicada se declara SIEMPRE (``reconstruction_error`` del AE): jamás se
  explican neuronas internas ni salidas implícitas.
- El explainer NO se fija a KernelExplainer: se usa ``shap.explainers.Permutation``
  (agnóstico, adecuado para 42 features tabulares y funciones black-box; el tipo y la
  versión reales se registran por experimento).
- Background: EXCLUSIVAMENTE muestras normales de TRAIN, selección determinista por
  semilla y hasheada. Nunca validation/test.
- shap es dependencia del grupo ``train``; import perezoso con error claro.
"""

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

from mecanico_contracts.features import FEATURE_NAMES


def _shap() -> Any:
    try:
        import shap
    except ImportError as exc:  # pragma: no cover - entorno sin grupo train
        msg = "shap no está instalado: usa `uv sync --all-packages --group train` (ADR-0032/0033)"
        raise RuntimeError(msg) from exc
    return shap


def select_background(
    train_x: np.ndarray, size: int = 100, seed: int = 42
) -> tuple[np.ndarray, dict[str, Any]]:
    """Background reproducible desde train-normal + metadatos de registro (adenda §21)."""
    rng = np.random.default_rng(seed)
    idx = rng.choice(train_x.shape[0], size=min(size, train_x.shape[0]), replace=False)
    bg = train_x[np.sort(idx)]
    meta = {
        "background_selection_method": "uniform-without-replacement(train-normal)",
        "background_size": int(bg.shape[0]),
        "selection_seed": seed,
        "background_hash": hashlib.sha256(np.ascontiguousarray(bg).tobytes()).hexdigest(),
    }
    return bg, meta


@dataclass
class ShapExplainer:
    """Envoltorio del explainer con registro completo (adenda §§15, 20)."""

    detector: Any  # expone scores(x) — la función explicada
    background: np.ndarray
    explained_output: str = "reconstruction_error"  # función declarada (adenda §20)
    max_evals: int = 200  # coste por muestra del Permutation explainer

    def __post_init__(self) -> None:
        shap = _shap()
        masker = shap.maskers.Independent(self.background, max_samples=self.background.shape[0])
        self._explainer = shap.explainers.Permutation(
            self.detector.scores, masker, max_evals=self.max_evals, seed=0
        )
        self.shap_version: str = shap.__version__
        self.explainer_type: str = "shap.explainers.Permutation"

    def explain(self, x: np.ndarray) -> np.ndarray:
        """Valores SHAP (n_muestras, n_features) para la función declarada."""
        return np.asarray(self._explainer(x, silent=True).values, dtype=np.float64)

    def registry_record(self) -> dict[str, Any]:
        return {
            "shap_version": self.shap_version,
            "explainer_type": self.explainer_type,
            "explained_output": self.explained_output,
            "max_evals": self.max_evals,
        }


def attributions_as_dict(
    values: np.ndarray, feature_names: Sequence[str] = FEATURE_NAMES
) -> dict[str, float]:
    """Fila SHAP → dict feature→valor (orden del esquema; fs1 por defecto)."""
    if values.shape[-1] != len(feature_names):
        msg = f"dimensión SHAP {values.shape} incompatible con el esquema ({len(feature_names)})"
        raise ValueError(msg)
    return {name: float(v) for name, v in zip(feature_names, values, strict=True)}


def explanation_artifact(
    *,
    window_id: str,
    session_id: str,
    model_id: str,
    anomaly_score: float,
    threshold: float,
    shap_values: dict[str, float],
    per_feature_error: dict[str, float],
    background_meta: dict[str, Any],
    explainer_record: dict[str, Any],
    k: int = 5,
) -> dict[str, Any]:
    """Artefacto de explicación local (contrato conceptual F15/adenda §5; JSON versionable)."""
    from ai_models.xai.metrics import top_k

    return {
        "window_id": window_id,
        "event_id": None,  # se rellenará cuando el consumidor sea el runtime de eventos
        "session_id": session_id,
        "model_id": model_id,
        "anomaly_score": round(anomaly_score, 6),
        "threshold": round(threshold, 6),
        "top_features": top_k(shap_values, k),
        "shap_values": {f: round(v, 6) for f, v in shap_values.items()},
        "reconstruction_error": {f: round(v, 6) for f, v in per_feature_error.items()},
        "reference_baseline": background_meta,
        "explainer": explainer_record,
    }
