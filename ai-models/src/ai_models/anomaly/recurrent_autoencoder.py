"""Autoencoders recurrentes (LSTM / GRU) sobre secuencias crudas — F18, EXP-ANOM-009.

Nivel 3 del Protocolo ML v1: la entrada es la trayectoria ``[T × PID]``, no un vector de
estadísticos. Hipótesis HX-ML-3 (config `exp-anom-009.yaml`, congelada antes de ejecutar):
la memoria recurrente permite distinguir fenómenos que la ventana resumida no puede —
adaptación discreta legítima del trim frente a deriva anómala persistente, y derivas
lentas de baja amplitud.

Decisiones de diseño DECLARADAS (auditables, no implícitas):

1. **Normalización**: el scaler se ajusta SOLO con train y es **global por feature**
   (media/desviación sobre todos los pasos de todas las secuencias de train). NO se
   normaliza cada secuencia por separado: eso eliminaría precisamente el nivel absoluto
   y la deriva que se quiere detectar (auditoría explícita en el runner).
2. **Ausencias (ADR-0027)**: la máscara viaja con los datos. El relleno declarado es 0 en
   el espacio ESTANDARIZADO (equivale a la media de train, el valor menos informativo) y
   el error se pondera por la máscara, de modo que una celda ausente no inventa error.
   El contrato es IDÉNTICO en entrenamiento e inferencia (test). La fracción de ausencias
   se reporta aparte para que un dropout anómalo sea visible como señal propia y no
   quede disuelto en la imputación.
3. **Determinismo**: semilla en torch + generador explícito del barajado.
4. **Early stopping** sobre una fracción de validación interna tomada del PROPIO train
   (nunca validation/test del protocolo).
5. **Presupuesto edge**: arquitecturas pequeñas (<150k parámetros por defecto);
   ``n_parameters``, ``model_size_bytes`` y la latencia por secuencia se registran.

El error de reconstrucción se conserva con resolución temporal completa
(``per_step_feature_error`` → ``error[t][f]``), que es lo que la adenda XAI temporal
compara contra la matriz de atribución.
"""

from dataclasses import dataclass, field
from typing import Any

import numpy as np

#: Presupuesto de parámetros declarado en la config (superarlo exige documentarlo).
PARAM_BUDGET = 150_000


def _torch() -> Any:
    """Import perezoso de torch (grupo `train`); error claro si falta."""
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - entorno sin grupo train
        msg = "torch no está instalado: usa `uv sync --all-packages --group train` (ADR-0032)"
        raise RuntimeError(msg) from exc
    return torch


def _build_model(
    kind: str, n_features: int, hidden: int, latent: int, layers: int, dropout: float
) -> Any:
    torch = _torch()
    nn = torch.nn
    if kind not in ("lstm", "gru"):
        msg = f"kind desconocido: {kind} (solo 'lstm' | 'gru')"
        raise ValueError(msg)
    rnn_cls = nn.LSTM if kind == "lstm" else nn.GRU

    class _RecurrentAE(nn.Module):  # type: ignore[misc, name-defined]
        """Encoder recurrente → vector latente → decoder recurrente (seq2seq de reconstrucción)."""

        def __init__(self) -> None:
            super().__init__()
            self.encoder = rnn_cls(
                n_features,
                hidden,
                num_layers=layers,
                batch_first=True,
                dropout=dropout if layers > 1 else 0.0,
            )
            self.to_latent = nn.Linear(hidden, latent)
            self.from_latent = nn.Linear(latent, hidden)
            self.decoder = rnn_cls(
                hidden,
                hidden,
                num_layers=layers,
                batch_first=True,
                dropout=dropout if layers > 1 else 0.0,
            )
            self.out = nn.Linear(hidden, n_features)

        def encode(self, x: Any) -> Any:
            out, _state = self.encoder(x)
            return self.to_latent(out[:, -1, :])  # último estado = resumen de la trayectoria

        def forward(self, x: Any) -> Any:
            z = self.encode(x)
            seq_len = x.shape[1]
            # el latente se repite en cada paso: el decoder reconstruye la secuencia entera
            h = self.from_latent(z).unsqueeze(1).repeat(1, seq_len, 1)
            dec, _state = self.decoder(h)
            return self.out(dec)

    return _RecurrentAE()


@dataclass
class RecurrentAutoencoderDetector:
    """Detector por reconstrucción de secuencias (mayor score = más anómalo)."""

    kind: str = "lstm"  # 'lstm' | 'gru'
    seed: int = 42
    hidden: int = 32
    latent: int = 8
    layers: int = 1
    dropout: float = 0.0
    epochs: int = 60
    batch_size: int = 32
    lr: float = 1e-3
    val_fraction: float = 0.15  # partición interna de train para early stopping
    patience: int = 8
    _model: Any = field(default=None, repr=False)
    _mean: np.ndarray | None = field(default=None, repr=False)
    _std: np.ndarray | None = field(default=None, repr=False)
    loss_history: list[float] = field(default_factory=list, init=False)
    val_history: list[float] = field(default_factory=list, init=False)
    best_epoch: int = field(default=-1, init=False)

    @property
    def name(self) -> str:
        return f"{self.kind}_ae"

    @property
    def n_parameters(self) -> int:
        if self._model is None:
            return 0
        return int(sum(p.numel() for p in self._model.parameters()))

    @property
    def model_size_bytes(self) -> int:
        if self._model is None:
            return 0
        return int(sum(p.numel() * p.element_size() for p in self._model.parameters()))

    # ------------------------------------------------------------------ normalización
    def _fit_scaler(self, x: np.ndarray, mask: np.ndarray) -> None:
        """Media/desviación GLOBAL por feature sobre train (no por secuencia: ver §1)."""
        flat = x.reshape(-1, x.shape[-1])
        m = mask.reshape(-1, x.shape[-1])
        mean = np.array(
            [flat[m[:, j], j].mean() if m[:, j].any() else 0.0 for j in range(x.shape[-1])]
        )
        std = np.array(
            [flat[m[:, j], j].std() if m[:, j].any() else 1.0 for j in range(x.shape[-1])]
        )
        self._mean, self._std = mean, np.where(std < 1e-12, 1.0, std)

    def _transform(self, x: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Estandariza y aplica el relleno declarado (0 = media de train) sobre lo ausente."""
        if self._mean is None or self._std is None:
            msg = "detector sin entrenar: llama a fit() primero"
            raise RuntimeError(msg)
        xs = np.asarray((np.nan_to_num(x, nan=0.0) - self._mean) / self._std, dtype=np.float64)
        xs[~mask] = 0.0  # contrato de ausencia IDÉNTICO en train e inferencia
        return np.asarray(xs, dtype=np.float32)

    # ---------------------------------------------------------------------- entrenamiento
    def fit(self, x: np.ndarray, mask: np.ndarray | None = None) -> None:
        """Entrena SOLO con secuencias normales de train (scaler incluido, ADR-0011)."""
        torch = _torch()
        torch.manual_seed(self.seed)
        mask = np.ones_like(x, dtype=bool) if mask is None else mask
        self._fit_scaler(x, mask)
        xs = self._transform(x, mask)
        w = mask.astype(np.float32)
        self._model = _build_model(
            self.kind, x.shape[-1], self.hidden, self.latent, self.layers, self.dropout
        )
        opt = torch.optim.Adam(self._model.parameters(), lr=self.lr)
        data = torch.from_numpy(xs)
        weights = torch.from_numpy(w)
        gen = torch.Generator().manual_seed(self.seed)
        n = data.shape[0]
        n_val = max(1, int(n * self.val_fraction))
        perm0 = torch.randperm(n, generator=gen)
        val_idx, tr_idx = perm0[:n_val], perm0[n_val:]
        best, best_state, since = float("inf"), None, 0
        for _epoch in range(self.epochs):
            self._model.train()
            perm = tr_idx[torch.randperm(tr_idx.shape[0], generator=gen)]
            total, batches = 0.0, 0
            for start in range(0, perm.shape[0], self.batch_size):
                idx = perm[start : start + self.batch_size]
                batch, bw = data[idx], weights[idx]
                opt.zero_grad()
                rec = self._model(batch)
                loss = (((rec - batch) ** 2) * bw).sum() / bw.sum().clamp(min=1.0)
                loss.backward()
                opt.step()
                total += float(loss.item())
                batches += 1
            self.loss_history.append(total / max(batches, 1))
            self._model.eval()
            with torch.no_grad():
                vb, vw = data[val_idx], weights[val_idx]
                vrec = self._model(vb)
                vloss = float((((vrec - vb) ** 2) * vw).sum() / vw.sum().clamp(min=1.0))
            self.val_history.append(vloss)
            if vloss < best - 1e-6:
                best, since = vloss, 0
                self.best_epoch = len(self.val_history) - 1
                best_state = {k: v.clone() for k, v in self._model.state_dict().items()}
            else:
                since += 1
                if since >= self.patience:
                    break
        if best_state is not None:
            self._model.load_state_dict(best_state)
        self._model.eval()

    # -------------------------------------------------------------------------- inferencia
    def _reconstruct(self, x: np.ndarray, mask: np.ndarray | None) -> tuple[Any, Any, Any]:
        torch = _torch()
        if self._model is None:
            msg = "detector sin entrenar: llama a fit() primero"
            raise RuntimeError(msg)
        mask = np.ones_like(x, dtype=bool) if mask is None else mask
        xs = self._transform(x, mask)
        with torch.no_grad():
            t = torch.from_numpy(xs)
            rec = self._model(t).numpy()
        return xs, rec, mask

    def scores(self, x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        """Error de reconstrucción medio por secuencia, ponderado por la máscara."""
        xs, rec, m = self._reconstruct(x, mask)
        err = ((xs - rec) ** 2) * m
        denom = np.maximum(m.sum(axis=(1, 2)), 1.0)
        return np.asarray(err.sum(axis=(1, 2)) / denom, dtype=np.float64)

    def scores_standardized(self, xs: np.ndarray) -> np.ndarray:
        """Score sobre entradas YA estandarizadas (misma función explicada que el XAI).

        Necesario para que explainers model-agnostic (Permutation) actúen en el MISMO
        espacio en que actúan los de gradiente: si uno explicara el espacio crudo y otro
        el estandarizado, su comparación no sería válida.
        """
        torch = _torch()
        if self._model is None:
            msg = "detector sin entrenar: llama a fit() primero"
            raise RuntimeError(msg)
        with torch.no_grad():
            t = torch.from_numpy(np.asarray(xs, dtype=np.float32))
            rec = self._model(t).numpy()
        xs64 = np.asarray(xs, dtype=np.float64)
        return np.asarray(((xs64 - rec) ** 2).mean(axis=(1, 2)), dtype=np.float64)

    def per_step_feature_error(self, x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        """``error[muestra, t, f]`` — resolución temporal completa (adenda XAI temporal)."""
        xs, rec, m = self._reconstruct(x, mask)
        return np.asarray(((xs - rec) ** 2) * m, dtype=np.float64)

    def per_step_error(self, x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        """``error[muestra, t]`` — agregado por instante (derivado, no sustituto)."""
        return np.asarray(self.per_step_feature_error(x, mask).sum(axis=2), dtype=np.float64)

    def per_feature_error(self, x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        """``error[muestra, f]`` — agregado por señal (derivado, no sustituto)."""
        return np.asarray(self.per_step_feature_error(x, mask).sum(axis=1), dtype=np.float64)

    def embed(self, x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        """Vector latente por secuencia (entrada de la línea EXP-PAT-*, D2)."""
        torch = _torch()
        if self._model is None:
            msg = "detector sin entrenar: llama a fit() primero"
            raise RuntimeError(msg)
        mask_ = np.ones_like(x, dtype=bool) if mask is None else mask
        xs = self._transform(x, mask_)
        with torch.no_grad():
            z = self._model.encode(torch.from_numpy(xs)).numpy()
        return np.asarray(z, dtype=np.float64)

    def registry_record(self) -> dict[str, Any]:
        """Metadatos edge-aware del brazo (ARM64 real sigue PENDIENTE de validación)."""
        return {
            "kind": self.kind,
            "hidden": self.hidden,
            "latent": self.latent,
            "layers": self.layers,
            "dropout": self.dropout,
            "n_parameters": self.n_parameters,
            "model_size_bytes": self.model_size_bytes,
            "within_param_budget": self.n_parameters < PARAM_BUDGET,
            "epochs_run": len(self.loss_history),
            "best_epoch": self.best_epoch,
        }
