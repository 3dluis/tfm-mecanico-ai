"""Modelo temporal: red recurrente con puertas sobre las series de la ventana.

**Por qué GRU y no LSTM ni CNN-1D.** Se elige una sola arquitectura, como fija el
plan. El conjunto de entrenamiento tiene 392 ventanas: el riesgo dominante es el
exceso de capacidad, no su falta. Una GRU tiene tres puertas frente a las cuatro
de una LSTM --alrededor de un 25 % menos de parámetros por unidad-- y con
secuencias de 120 pasos la memoria de largo alcance que aporta la LSTM no tiene
nada que aprovechar. Una CNN-1D captaría bien los episodios breves del fallo de
encendido, pero peor la deriva lenta del caudalímetro y el techo sostenido del
termostato, que son fenómenos de escala larga.

Se declara para poder contrastarlo: si el modelo no supera al baseline, la
conclusión no será «hacía falta otra arquitectura» sino que con estos datos la
complejidad añadida no está justificada.

**Normalización.** Los estadísticos se ajustan **solo con entrenamiento**.
Ajustarlos sobre el conjunto completo filtraría a entrenamiento la media y la
escala de validación y de test: es una fuga sutil, no la detecta el auditor de
particiones, y mejora las métricas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np
import numpy.typing as npt

if TYPE_CHECKING:  # pragma: no cover - solo para anotaciones
    import torch

_EPS = 1e-8


@dataclass(frozen=True)
class TemporalConfig:
    """Hiperparámetros del modelo temporal. Se registran con cada ejecución."""

    hidden_size: int = 48
    num_layers: int = 1
    dropout: float = 0.3
    bidirectional: bool = True
    learning_rate: float = 3e-3
    weight_decay: float = 1e-4
    batch_size: int = 32
    max_epochs: int = 300
    patience: int = 40
    """Épocas sin mejora en validación antes de parar."""
    seed: int = 20260901


@dataclass
class Standardizer:
    """Media y escala por señal, ajustadas solo con entrenamiento."""

    mean: npt.NDArray[np.float32]
    scale: npt.NDArray[np.float32]

    @classmethod
    def fit(cls, x: npt.NDArray[np.float32]) -> Standardizer:
        """``x`` es (n, pasos, señales); se resume sobre ventanas y pasos."""
        media = x.mean(axis=(0, 1), dtype=np.float64)
        escala = x.std(axis=(0, 1), dtype=np.float64)
        # Una señal constante tendría escala cero: se deja a uno para no dividir
        # por cero y para que su valor normalizado quede en cero.
        escala = np.where(escala < _EPS, 1.0, escala)
        return cls(mean=media.astype(np.float32), scale=escala.astype(np.float32))

    def transform(self, x: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
        return ((x - self.mean) / self.scale).astype(np.float32)


def resolve_device() -> str:
    """Dispositivo de cómputo. Nunca asume CUDA; el fallback se reporta."""
    import torch

    return "mps" if torch.backends.mps.is_available() else "cpu"


def build_model(n_signals: int, n_classes: int, config: TemporalConfig) -> Any:
    """Construye la red. Devuelve un ``torch.nn.Module``."""
    import torch
    from torch import nn

    class GRUClassifier(nn.Module):
        """GRU bidireccional con agregación por media y máximo sobre el tiempo.

        La cabeza combina las dos agregaciones a propósito: la media capta
        niveles sostenidos --el techo del termostato, la deriva del
        caudalímetro-- y el máximo capta episodios breves --el fallo de
        encendido--. E4 y E5 mostraron que las condiciones se manifiestan de
        ambas formas, y quedarse solo con el último estado oculto perdería una
        de las dos.
        """

        def __init__(self) -> None:
            super().__init__()
            self.gru = nn.GRU(
                input_size=n_signals,
                hidden_size=config.hidden_size,
                num_layers=config.num_layers,
                batch_first=True,
                bidirectional=config.bidirectional,
                dropout=config.dropout if config.num_layers > 1 else 0.0,
            )
            direcciones = 2 if config.bidirectional else 1
            ancho = config.hidden_size * direcciones
            self.dropout = nn.Dropout(config.dropout)
            self.head = nn.Linear(ancho * 2, n_classes)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            salidas, _ = self.gru(x)
            media = salidas.mean(dim=1)
            maximo = salidas.max(dim=1).values
            logits: torch.Tensor = self.head(self.dropout(torch.cat([media, maximo], dim=1)))
            return logits

    return GRUClassifier()


def count_parameters(model: Any) -> int:
    """Parámetros entrenables. Se registra: con 392 ventanas, el tamaño importa."""
    return int(sum(p.numel() for p in model.parameters() if p.requires_grad))
