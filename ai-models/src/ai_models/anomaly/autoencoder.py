"""Autoencoder denso multivariable para detección por reconstrucción (F14, EXP-ANOM-006).

Nivel 2 del Protocolo ML v1: AE pequeño (<<100k parámetros, patrón tipo USAD simplificado,
línea B7 del estado del arte) sobre vectores de features fs1 por ventana. Cumple el
``Detector`` Protocol de ``baselines`` (mayor score = más anómalo, score = error de
reconstrucción MSE), y añade lo que los baselines no dan: ``embed`` (representación
latente para la línea de descubrimiento EXP-PAT-*) y ``per_feature_error``
(explicabilidad, Protocolo ML v1 §13).

Reglas: el scaler se ajusta SOLO con train y se persiste con el detector; determinismo
por semilla (torch.manual_seed + generadores explícitos); entrenamiento en CPU (el
tamaño del problema no justifica GPU y el objetivo de inferencia es edge). torch es
dependencia del grupo ``train`` (ADR-0032): este módulo se importa de forma perezosa y
los tests se saltan si torch no está instalado.
"""

from dataclasses import dataclass, field
from itertools import pairwise
from typing import Any

import numpy as np
from sklearn.preprocessing import RobustScaler, StandardScaler

#: Arquitectura por defecto (entrada fs1=42): 42→32→16→8→16→32→42 ≈ 4.3k parámetros.
DEFAULT_HIDDEN: tuple[int, ...] = (32, 16)
DEFAULT_LATENT = 8


def _torch() -> Any:
    """Import perezoso de torch (grupo `train`); error claro si falta."""
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - entorno sin grupo train
        msg = "torch no está instalado: usa `uv sync --all-packages --group train` (ADR-0032)"
        raise RuntimeError(msg) from exc
    return torch


def _build_model(n_features: int, hidden: tuple[int, ...], latent: int) -> Any:
    torch = _torch()
    nn = torch.nn
    enc_dims = [n_features, *hidden, latent]
    dec_dims = [latent, *reversed(hidden), n_features]
    enc_layers: list[Any] = []
    for a, b in pairwise(enc_dims):
        enc_layers += [nn.Linear(a, b), nn.ReLU()]
    enc_layers.pop()  # sin activación en el cuello de botella
    dec_layers: list[Any] = []
    for a, b in pairwise(dec_dims):
        dec_layers += [nn.Linear(a, b), nn.ReLU()]
    dec_layers.pop()  # salida lineal (features estandarizadas)

    class _AE(nn.Module):  # type: ignore[misc, name-defined]
        def __init__(self) -> None:
            super().__init__()
            self.encoder = nn.Sequential(*enc_layers)
            self.decoder = nn.Sequential(*dec_layers)

        def forward(self, x: Any) -> Any:
            return self.decoder(self.encoder(x))

    return _AE()


@dataclass
class AutoencoderDetector:
    """Detector por reconstrucción compatible con el protocolo de ``baselines``."""

    seed: int = 42
    hidden: tuple[int, ...] = DEFAULT_HIDDEN
    latent: int = DEFAULT_LATENT
    epochs: int = 200
    batch_size: int = 32
    lr: float = 1e-3
    scaler_kind: str = "standard"  # 'standard' | 'robust' (comparación Protocolo ML v1 §4)
    _model: Any = field(default=None, repr=False)
    _scaler: Any = field(default=None, repr=False)
    train_loss: float = field(default=float("nan"), init=False)

    @property
    def name(self) -> str:
        return f"autoencoder_{self.scaler_kind}"

    @property
    def n_parameters(self) -> int:
        if self._model is None:
            return 0
        return int(sum(p.numel() for p in self._model.parameters()))

    def _make_scaler(self) -> Any:
        if self.scaler_kind == "standard":
            return StandardScaler()
        if self.scaler_kind == "robust":
            return RobustScaler()
        msg = f"scaler_kind desconocido: {self.scaler_kind}"
        raise ValueError(msg)

    def fit(self, x: np.ndarray) -> None:
        """Entrena SOLO con ventanas normales de train (scaler incluido, ADR-0011)."""
        torch = _torch()
        torch.manual_seed(self.seed)
        self._scaler = self._make_scaler()
        xs = self._scaler.fit_transform(x).astype(np.float32)
        self._model = _build_model(x.shape[1], self.hidden, self.latent)
        opt = torch.optim.Adam(self._model.parameters(), lr=self.lr)
        loss_fn = torch.nn.MSELoss()
        data = torch.from_numpy(xs)
        gen = torch.Generator().manual_seed(self.seed)
        self._model.train()
        last = float("nan")
        for _epoch in range(self.epochs):
            perm = torch.randperm(data.shape[0], generator=gen)
            total, batches = 0.0, 0
            for start in range(0, data.shape[0], self.batch_size):
                batch = data[perm[start : start + self.batch_size]]
                opt.zero_grad()
                loss = loss_fn(self._model(batch), batch)
                loss.backward()
                opt.step()
                total += float(loss.item())
                batches += 1
            last = total / max(batches, 1)
        self.train_loss = last
        self._model.eval()

    def _reconstruct(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        torch = _torch()
        if self._model is None or self._scaler is None:
            msg = "detector sin entrenar: llama a fit() primero"
            raise RuntimeError(msg)
        xs = self._scaler.transform(x).astype(np.float32)
        with torch.no_grad():
            rec = self._model(torch.from_numpy(xs)).numpy()
        return xs, rec

    def scores(self, x: np.ndarray) -> np.ndarray:
        """Error de reconstrucción MSE por muestra (mayor = más anómalo)."""
        xs, rec = self._reconstruct(x)
        return np.asarray(((xs - rec) ** 2).mean(axis=1), dtype=np.float64)

    def per_feature_error(self, x: np.ndarray) -> np.ndarray:
        """Error cuadrático por feature (explicabilidad §13): (n_muestras, n_features)."""
        xs, rec = self._reconstruct(x)
        return np.asarray((xs - rec) ** 2, dtype=np.float64)

    def embed(self, x: np.ndarray) -> np.ndarray:
        """Embedding latente por muestra (entrada de la línea EXP-PAT-*)."""
        torch = _torch()
        if self._model is None or self._scaler is None:
            msg = "detector sin entrenar: llama a fit() primero"
            raise RuntimeError(msg)
        xs = self._scaler.transform(x).astype(np.float32)
        with torch.no_grad():
            z = self._model.encoder(torch.from_numpy(xs)).numpy()
        return np.asarray(z, dtype=np.float64)
