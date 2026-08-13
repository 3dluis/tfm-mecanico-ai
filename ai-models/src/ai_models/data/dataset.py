"""Construcción de datasets de features a partir de sesiones grabadas (formato común)."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from mecanico_contracts import RecordedSession
from mecanico_contracts.features import FEATURE_NAMES, feature_vector
from mecanico_contracts.session_io import read_session_series

#: Fracción mínima de solape ventana↔fallo para etiquetarla anómala.
_OVERLAP_LABEL = 0.5


@dataclass
class WindowDataset:
    """Ventanas de un split: matriz X, etiquetas y trazabilidad por sesión."""

    x: np.ndarray  # (n_ventanas, n_features)
    y: np.ndarray  # 1 = ventana con fallo activo, 0 = normal
    session_ids: list[str]
    categories: list[str]  # categoría del escenario de cada ventana
    window_starts: list[float]  # segundo de inicio de cada ventana

    @property
    def feature_names(self) -> list[str]:
        return list(FEATURE_NAMES)


def _windows_from_series(
    series: dict[str, list[float]], size: int, stride: int
) -> list[tuple[int, dict[str, list[float]]]]:
    n = min((len(v) for v in series.values() if v), default=0)
    out = []
    for start in range(0, n - size + 1, stride):
        out.append((start, {pid: vals[start : start + size] for pid, vals in series.items()}))
    return out


def _label(header: RecordedSession, start_s: float, size_s: float) -> int:
    sc = header.scenario
    if sc is None or sc.fault is None:
        return 0
    f0 = sc.fault_start_s if sc.fault_start_s is not None else 0.0
    f1 = sc.fault_end_s if sc.fault_end_s is not None else sc.duration_s
    overlap = max(0.0, min(start_s + size_s, f1) - max(start_s, f0))
    return int(overlap / size_s >= _OVERLAP_LABEL)


def build_dataset(session_dir: Path, size: int = 60, stride: int = 30) -> WindowDataset:
    """Convierte todas las sesiones de un directorio en un dataset de ventanas etiquetadas."""
    xs: list[list[float]] = []
    ys: list[int] = []
    sids: list[str] = []
    cats: list[str] = []
    starts: list[float] = []
    for path in sorted(session_dir.glob("*.jsonl")):
        header, series = read_session_series(path)
        rate = header.scenario.sample_rate_hz if header.scenario else 1.0
        for start_idx, window in _windows_from_series(series, size, stride):
            start_s = start_idx / rate
            xs.append(feature_vector(window))
            ys.append(_label(header, start_s, size / rate))
            sids.append(header.session_id)
            cats.append(header.scenario.category if header.scenario else "unknown")
            starts.append(start_s)
    return WindowDataset(
        x=np.asarray(xs, dtype=np.float64),
        y=np.asarray(ys, dtype=np.int64),
        session_ids=sids,
        categories=cats,
        window_starts=starts,
    )
