"""Métricas EVENT-LEVEL de detección de anomalías (F9, EXP-ANOM-003).

Complementan (nunca sustituyen) a las métricas tick-level: un evento largo mal
clasificado cuenta como UN error de evento, además de su análisis temporal. Definición:
entre los eventos detectados de una sesión, son POSITIVOS los que solapan el intervalo
real del fallo en ≥ ``overlap`` de su duración; el detector debe flaggear exactamente
esos. Un evento flaggeado sin fallo es un ``false event``.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class AnomalyEventReport:
    """Métricas por evento de un conjunto de sesiones."""

    tp: int = 0
    fp: int = 0
    fn: int = 0
    n_normal_sessions: int = 0
    fp_in_normal_sessions: int = 0

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def false_events_per_normal_session(self) -> float:
        if not self.n_normal_sessions:
            return 0.0
        return self.fp_in_normal_sessions / self.n_normal_sessions


def add_session(
    report: AnomalyEventReport,
    events: list[tuple[int, int, bool]],
    y_tick: np.ndarray,
    overlap: float = 0.5,
) -> None:
    """Acumula una sesión: ``events`` = (seq_start, seq_end, flagged) por evento detectado."""
    is_normal_session = not bool(y_tick.any())
    if is_normal_session:
        report.n_normal_sessions += 1
    for seq_start, seq_end, flagged in events:
        dur = max(1, seq_end - seq_start + 1)
        frac = float(y_tick[seq_start : seq_end + 1].sum()) / dur
        positive = frac >= overlap
        if positive and flagged:
            report.tp += 1
        elif positive:
            report.fn += 1
        elif flagged:
            report.fp += 1
            if is_normal_session:
                report.fp_in_normal_sessions += 1
