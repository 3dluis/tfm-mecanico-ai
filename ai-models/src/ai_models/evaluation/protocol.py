"""Protocolo de evaluación (ADR-0011): honesto por construcción.

Reglas (justificación en docs/estado_del_arte/linea_b, B2-B4):
- El umbral se fija SOLO con datos normales de entrenamiento (percentil de FPR objetivo).
- Métricas point-wise SIN point-adjustment (Kim et al., AAAI 2022).
- Métricas por evento: un episodio de fallo cuenta como detectado si alguna ventana
  dentro de su intervalo supera el umbral; se reporta también el retardo de detección.
- Las anomalías held-out jamás intervienen en el ajuste (RI1).
"""

from dataclasses import dataclass

import numpy as np

from ai_models.data.dataset import WindowDataset


@dataclass
class PointMetrics:
    precision: float
    recall: float
    f1: float
    fp_rate_normal: float  # fracción de ventanas normales marcadas (falsas alarmas)


@dataclass
class EventMetrics:
    episodes_total: int
    episodes_detected: int
    mean_detection_delay_s: float | None  # desde el inicio del fallo a la 1ª ventana marcada


def threshold_from_normal(scores_normal: np.ndarray, target_fpr: float = 0.01) -> float:
    """Umbral = cuantil (1 - FPR objetivo) de los scores de ventanas normales de train."""
    return float(np.quantile(scores_normal, 1.0 - target_fpr))


def point_metrics(y_true: np.ndarray, flagged: np.ndarray) -> PointMetrics:
    tp = int(np.sum((y_true == 1) & flagged))
    fp = int(np.sum((y_true == 0) & flagged))
    fn = int(np.sum((y_true == 1) & ~flagged))
    n_norm = int(np.sum(y_true == 0))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return PointMetrics(
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1=round(f1, 4),
        fp_rate_normal=round(fp / n_norm, 4) if n_norm else 0.0,
    )


def event_metrics(ds: WindowDataset, flagged: np.ndarray) -> EventMetrics:
    """Métricas por episodio de fallo (un episodio = una sesión con fallo)."""
    delays: list[float] = []
    detected = 0
    episodes = 0
    for sid in sorted(set(ds.session_ids)):
        idx = [i for i, s in enumerate(ds.session_ids) if s == sid]
        y = ds.y[idx]
        if not y.any():
            continue  # sesión sin fallo: no es episodio
        episodes += 1
        fault_idx = [i for i in idx if ds.y[i] == 1]
        hit_starts = [ds.window_starts[i] for i in fault_idx if flagged[i]]
        if hit_starts:
            detected += 1
            fault_t0 = min(ds.window_starts[i] for i in fault_idx)
            delays.append(min(hit_starts) - fault_t0)
    return EventMetrics(
        episodes_total=episodes,
        episodes_detected=detected,
        mean_detection_delay_s=round(float(np.mean(delays)), 1) if delays else None,
    )
