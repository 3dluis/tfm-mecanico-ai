"""Bucle de entrenamiento del modelo temporal.

La parada temprana se decide **sobre validación y con F1 macro**, no con la
pérdida ni con la exactitud: el reparto es 2:1 y ambas premiarían al modelo que
acierta la clase abundante.

El dispositivo empleado se devuelve y se registra. Un resultado obtenido en CPU y
otro en MPS no son intercambiables, y ocultar el fallback los haría parecer
comparables.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import numpy.typing as npt

from mecanico_ia_exp.models.temporal import (
    Standardizer,
    TemporalConfig,
    build_model,
    count_parameters,
    resolve_device,
)


@dataclass
class TrainingHistory:
    """Traza del entrenamiento, para poder ver si convergió o se disparó."""

    train_loss: list[float] = field(default_factory=list)
    val_loss: list[float] = field(default_factory=list)
    val_macro_f1: list[float] = field(default_factory=list)
    best_epoch: int = -1
    best_val_macro_f1: float = -1.0
    stopped_early: bool = False


@dataclass
class TrainedTemporalModel:
    """Modelo entrenado con todo lo necesario para volver a aplicarlo."""

    model: Any
    standardizer: Standardizer
    classes: tuple[str, ...]
    device: str
    config: TemporalConfig
    history: TrainingHistory
    n_parameters: int

    def predict_proba(self, x: npt.NDArray[np.float32]) -> npt.NDArray[np.float64]:
        """Probabilidades por clase, en el orden de ``classes``."""
        import torch

        self.model.eval()
        tensor = torch.from_numpy(self.standardizer.transform(x)).to(self.device)
        with torch.no_grad():
            logits = self.model(tensor)
            probabilidades = torch.softmax(logits, dim=1).cpu().numpy()
        return np.asarray(probabilidades, dtype=np.float64)

    def predict(self, x: npt.NDArray[np.float32]) -> npt.NDArray[np.str_]:
        indices = self.predict_proba(x).argmax(axis=1)
        return np.array([self.classes[i] for i in indices], dtype=np.str_)


def _set_seeds(seed: int) -> None:
    """Fija las semillas de todo lo que puede introducir azar.

    En MPS algunas reducciones no son bit a bit deterministas entre ejecuciones;
    la semilla acota la variación pero no la elimina del todo. Se hace constar
    para no prometer una reproducibilidad exacta que el dispositivo no ofrece.
    """
    import torch

    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.backends.mps.is_available():
        torch.mps.manual_seed(seed)


def train_temporal(
    x_train: npt.NDArray[np.float32],
    y_train: npt.NDArray[np.str_],
    x_val: npt.NDArray[np.float32],
    y_val: npt.NDArray[np.str_],
    *,
    classes: tuple[str, ...],
    config: TemporalConfig | None = None,
    device: str | None = None,
    verbose: bool = True,
) -> TrainedTemporalModel:
    """Entrena con parada temprana sobre el F1 macro de validación."""
    import torch
    from sklearn.metrics import f1_score
    from torch import nn

    cfg = config or TemporalConfig()
    _set_seeds(cfg.seed)
    dispositivo = device or resolve_device()

    # Los estadísticos salen SOLO de entrenamiento.
    estandarizador = Standardizer.fit(x_train)
    indice = {clase: i for i, clase in enumerate(classes)}

    xt = torch.from_numpy(estandarizador.transform(x_train)).to(dispositivo)
    yt = torch.tensor([indice[c] for c in y_train.tolist()], device=dispositivo)
    xv = torch.from_numpy(estandarizador.transform(x_val)).to(dispositivo)
    yv = torch.tensor([indice[c] for c in y_val.tolist()], device=dispositivo)

    modelo = build_model(x_train.shape[2], len(classes), cfg).to(dispositivo)

    # Pesos inversos a la frecuencia: el reparto es 2:1 y sin compensar la red
    # optimiza la clase abundante.
    cuentas = np.array([(y_train == c).sum() for c in classes], dtype=np.float64)
    pesos = torch.tensor(
        (cuentas.sum() / (len(classes) * np.maximum(cuentas, 1.0))).astype(np.float32),
        device=dispositivo,
    )
    criterio = nn.CrossEntropyLoss(weight=pesos)
    optimizador = torch.optim.AdamW(
        modelo.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay
    )

    historia = TrainingHistory()
    mejor_estado: dict[str, Any] | None = None
    sin_mejora = 0
    n = xt.shape[0]
    generador = torch.Generator().manual_seed(cfg.seed)

    for epoca in range(cfg.max_epochs):
        modelo.train()
        orden = torch.randperm(n, generator=generador).to(dispositivo)
        perdida_acumulada = 0.0
        for inicio in range(0, n, cfg.batch_size):
            lote = orden[inicio : inicio + cfg.batch_size]
            optimizador.zero_grad()
            perdida = criterio(modelo(xt[lote]), yt[lote])
            perdida.backward()
            optimizador.step()
            perdida_acumulada += float(perdida.item()) * lote.shape[0]

        modelo.eval()
        with torch.no_grad():
            logits_val = modelo(xv)
            perdida_val = float(criterio(logits_val, yv).item())
            predicho = logits_val.argmax(dim=1).cpu().numpy()
        f1 = float(f1_score(yv.cpu().numpy(), predicho, average="macro", zero_division=0))

        historia.train_loss.append(perdida_acumulada / n)
        historia.val_loss.append(perdida_val)
        historia.val_macro_f1.append(f1)

        if f1 > historia.best_val_macro_f1:
            historia.best_val_macro_f1 = f1
            historia.best_epoch = epoca
            mejor_estado = {k: v.detach().clone() for k, v in modelo.state_dict().items()}
            sin_mejora = 0
        else:
            sin_mejora += 1
            if sin_mejora >= cfg.patience:
                historia.stopped_early = True
                break

        if verbose and (epoca % 25 == 0 or epoca == cfg.max_epochs - 1):
            print(
                f"  época {epoca:3d}  pérdida {historia.train_loss[-1]:.4f}  "
                f"val {perdida_val:.4f}  F1 macro val {f1:.4f}"
            )

    # Se restaura el mejor estado, no el último: seguir entrenando después del
    # óptimo empeora, y quedarse con el último equivaldría a ignorar la parada.
    if mejor_estado is not None:
        modelo.load_state_dict(mejor_estado)

    return TrainedTemporalModel(
        model=modelo,
        standardizer=estandarizador,
        classes=classes,
        device=dispositivo,
        config=cfg,
        history=historia,
        n_parameters=count_parameters(modelo),
    )
