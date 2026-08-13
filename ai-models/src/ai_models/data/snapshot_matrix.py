"""Camino wide para ML — VehicleTelemetrySnapshot → matriz columnar → ventanas (F13).

Materializa la ruta prevista en ADR-0025 (`snapshots → matriz → windowing → features → ML`)
y ataca el cuello de botella de lectura identificado en F11/F12 (materializar 86k objetos
Pydantic costó 1.2 GB de RSS): la matriz se rellena por columnas en un único recorrido y
el resto del pipeline trabaja solo con arrays NumPy.

Reglas que respeta:
- ADR-0027 (NULL ≠ 0): una señal ausente es ``NaN`` en la matriz, jamás 0. La validez por
  celda se conserva en una máscara explícita.
- ADR-0026 (sync:v1): no se mezclan snapshots con ``synchronization_version`` distinta.
- ADR-0025: el snapshot no contiene features; las features se calculan aguas abajo con el
  MISMO contrato ``mecanico_contracts.features`` que el camino long de F3, lo que hace la
  paridad verificable por construcción (EXP-ANOM-005).

Este módulo depende únicamente de ``mecanico_contracts`` (regla de dependencias §9.4).
"""

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np

from mecanico_contracts import PID_TO_SNAPSHOT_FIELD, VehicleTelemetrySnapshot
from mecanico_contracts.features import CANONICAL_PIDS

#: Orden EXACTO de columnas de la matriz wide = orden de CANONICAL_PIDS (contrato fs1).
MATRIX_PIDS: tuple[str, ...] = tuple(CANONICAL_PIDS)

#: Fracción mínima de celdas válidas (por señal y ventana) para aceptar la ventana.
#: 1.0 = paridad estricta con el camino long (que asume series completas del simulador).
DEFAULT_MIN_VALID_FRACTION = 1.0


@dataclass
class WideMatrix:
    """Serie temporal multivariable de UNA sesión en forma columnar.

    ``values[i, j]`` = señal ``MATRIX_PIDS[j]`` en el paso ``seq[i]``; NaN si la señal no
    estaba disponible (NULL ≠ 0). ``valid`` es la máscara de disponibilidad equivalente.
    """

    session_id: str
    values: np.ndarray  # (n_pasos, n_pids) float64, NaN = ausente
    valid: np.ndarray  # (n_pasos, n_pids) bool
    seq: np.ndarray  # (n_pasos,) int64 — sequence_number del snapshot
    interval_ms: int
    synchronization_version: str

    @property
    def pids(self) -> tuple[str, ...]:
        return MATRIX_PIDS

    @property
    def sample_rate_hz(self) -> float:
        return 1000.0 / self.interval_ms


def matrix_from_snapshots(snapshots: list[VehicleTelemetrySnapshot]) -> WideMatrix:
    """Convierte los snapshots de una sesión en matriz columnar (un solo recorrido).

    Exige homogeneidad: misma sesión, misma ``synchronization_version`` y mismo
    ``snapshot_interval_ms`` (ADR-0026: rejillas distintas no se mezclan sin declararlo).
    """
    if not snapshots:
        msg = "no hay snapshots: la matriz wide exige al menos un paso"
        raise ValueError(msg)
    ordered = sorted(snapshots, key=lambda s: s.sequence_number)
    first = ordered[0]
    for snap in ordered:
        if snap.session_id != first.session_id:
            msg = f"snapshots de sesiones distintas: {snap.session_id} != {first.session_id}"
            raise ValueError(msg)
        if snap.synchronization_version != first.synchronization_version:
            msg = (
                "synchronization_version mixta en la misma matriz: "
                f"{snap.synchronization_version} != {first.synchronization_version} (ADR-0026)"
            )
            raise ValueError(msg)
        if snap.snapshot_interval_ms != first.snapshot_interval_ms:
            msg = "snapshot_interval_ms mixto en la misma matriz (ADR-0026)"
            raise ValueError(msg)

    n = len(ordered)
    fields = [PID_TO_SNAPSHOT_FIELD[pid] for pid in MATRIX_PIDS]
    values = np.full((n, len(fields)), np.nan, dtype=np.float64)
    for i, snap in enumerate(ordered):
        for j, field_name in enumerate(fields):
            raw = getattr(snap, field_name)
            if raw is not None:
                values[i, j] = float(raw)
    return WideMatrix(
        session_id=first.session_id,
        values=values,
        valid=~np.isnan(values),
        seq=np.asarray([s.sequence_number for s in ordered], dtype=np.int64),
        interval_ms=first.snapshot_interval_ms,
        synchronization_version=first.synchronization_version,
    )


def iter_windows(
    matrix: WideMatrix,
    size: int,
    stride: int,
    min_valid_fraction: float = DEFAULT_MIN_VALID_FRACTION,
) -> Iterator[tuple[int, dict[str, list[float]]]]:
    """Ventanas deslizantes sobre la matriz, en el MISMO formato que consume fs1.

    Devuelve ``(indice_inicio, {pid: [valores]})`` — exactamente la estructura que espera
    ``mecanico_contracts.features.extract_features``, de modo que el camino wide y el
    camino long produzcan features idénticas por construcción.

    Una ventana se DESCARTA (no se imputa) si alguna señal tiene una fracción de celdas
    válidas inferior a ``min_valid_fraction``; el descarte se contabiliza aguas arriba
    mediante ``count_windows``/``count_discarded``. La imputación, si algún experimento
    la necesita, es una decisión de la fase de features, nunca de esta capa (ADR-0027).
    """
    if size <= 0 or stride <= 0:
        msg = "size y stride deben ser positivos"
        raise ValueError(msg)
    n = matrix.values.shape[0]
    for start in range(0, n - size + 1, stride):
        block_valid = matrix.valid[start : start + size]
        if float(block_valid.mean(axis=0).min()) < min_valid_fraction:
            continue
        block = matrix.values[start : start + size]
        yield (
            start,
            {pid: block[:, j].tolist() for j, pid in enumerate(MATRIX_PIDS)},
        )


def count_windows(n_steps: int, size: int, stride: int) -> int:
    """Número total de ventanas candidatas (antes del filtro de validez)."""
    if n_steps < size:
        return 0
    return (n_steps - size) // stride + 1


def count_discarded(
    matrix: WideMatrix,
    size: int,
    stride: int,
    min_valid_fraction: float = DEFAULT_MIN_VALID_FRACTION,
) -> int:
    """Ventanas descartadas por el criterio de validez (sin cap silencioso: se reporta)."""
    total = count_windows(matrix.values.shape[0], size, stride)
    kept = sum(1 for _ in iter_windows(matrix, size, stride, min_valid_fraction))
    return total - kept
