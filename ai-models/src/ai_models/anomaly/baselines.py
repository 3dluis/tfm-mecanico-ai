"""Baselines de detección de anomalías (ADR-0011): simples y explicables primero.

Todos comparten la interfaz: ``fit(X_normal)`` y ``scores(X) -> np.ndarray`` con
semántica *mayor = más anómalo* (se invierte el signo de sklearn donde haga falta).
Referencias verificadas en docs/estado_del_arte/linea_b (Leys 2013; Liu 2008/2012;
Breunig 2000; Schölkopf 2001; Chandola 2009).
"""

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM


class Detector(Protocol):
    """Interfaz común de los baselines."""

    name: str

    def fit(self, x: np.ndarray) -> None: ...

    def scores(self, x: np.ndarray) -> np.ndarray: ...


@dataclass
class RobustZScore:
    """Máximo |z modificado| (mediana/MAD) por ventana. Totalmente explicable."""

    name: str = "robust_zscore"
    median_: np.ndarray = field(default_factory=lambda: np.empty(0))
    mad_: np.ndarray = field(default_factory=lambda: np.empty(0))

    def fit(self, x: np.ndarray) -> None:
        self.median_ = np.median(x, axis=0)
        mad = np.median(np.abs(x - self.median_), axis=0)
        # Suelo del MAD (evita z explosivos en features casi constantes): proporcional a
        # la escala robusta de la feature (IQR) con mínimo absoluto.
        iqr = np.quantile(x, 0.75, axis=0) - np.quantile(x, 0.25, axis=0)
        self.mad_ = np.maximum.reduce([mad, 0.1 * iqr, np.full_like(mad, 1e-3)])

    def scores(self, x: np.ndarray) -> np.ndarray:
        z = 0.6745 * (x - self.median_) / self.mad_
        return np.asarray(np.max(np.abs(z), axis=1))


@dataclass
class SkDetector:
    """Envoltorio homogéneo (scaler + modelo sklearn) con score invertido."""

    name: str
    pipeline: Pipeline

    def fit(self, x: np.ndarray) -> None:
        self.pipeline.fit(x)

    def scores(self, x: np.ndarray) -> np.ndarray:
        return np.asarray(-self.pipeline.decision_function(x))


def make_baselines(seed: int) -> list[Detector]:
    """Catálogo de baselines de la iteración (orden: más simple → más complejo)."""
    return [
        RobustZScore(),
        SkDetector(
            "isolation_forest",
            Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "model",
                        IsolationForest(
                            n_estimators=300,
                            max_samples=0.8,
                            max_features=0.5,
                            random_state=seed,
                        ),
                    ),
                ]
            ),
        ),
        SkDetector(
            "lof",
            Pipeline(
                [
                    ("scaler", StandardScaler()),
                    ("model", LocalOutlierFactor(n_neighbors=10, novelty=True)),
                ]
            ),
        ),
        SkDetector(
            "ocsvm",
            Pipeline(
                [
                    ("scaler", StandardScaler()),
                    ("model", OneClassSVM(nu=0.01, kernel="rbf", gamma=0.005)),
                ]
            ),
        ),
    ]
