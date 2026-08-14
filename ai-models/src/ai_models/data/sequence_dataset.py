"""Dataset secuencial crudo ``[T × PID]`` para modelos temporales (F18, EXP-ANOM-009).

Tercer nivel de representación del Protocolo ML v1: donde el camino de features resume
la ventana en estadísticos (fs1) o en derivadas de sesión (fs2-lite), aquí la entrada del
modelo es la **trayectoria** — la secuencia de señales en orden temporal, sin resumir.
La motivación es el hallazgo de EXP-ANOM-008: la patología del FPR y las anomalías lentas
no detectadas son fenómenos de contexto temporal que una ventana resumida no puede
distinguir por construcción.

Reglas heredadas que se mantienen:
- Fuente canónica = ``VehicleTelemetrySnapshot`` → ``WideMatrix`` (ADR-0025); este módulo
  parte de la matriz, de modo que las secuencias y las ventanas fs1 provienen del MISMO
  camino verificado en EXP-ANOM-005.
- **NULL ≠ 0** (ADR-0027): la ausencia viaja en una máscara explícita ``mask[t, f]``,
  jamás como valor. Este módulo NO imputa: la política de relleno pertenece al modelo y
  se declara allí (y la máscara se conserva para que el contrato sea idéntico en
  entrenamiento e inferencia).
- Etiquetado idéntico al de las ventanas estáticas (solape ≥ 0.5 con el intervalo
  inyectado), para que la comparación entre niveles de representación sea legítima.

El manifiesto versionado (``sequence_manifest``) registra procedencia, hash, longitudes y
duración real en segundos: la longitud de secuencia nunca se declara solo en pasos.
"""

import hashlib
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ai_models.data.snapshot_matrix import MATRIX_PIDS, WideMatrix

#: Fracción mínima de solape secuencia↔fallo para etiquetarla anómala (igual que fs1).
OVERLAP_LABEL = 0.5


def iter_sequences(
    matrix: WideMatrix, steps: int, stride: int
) -> Iterator[tuple[int, np.ndarray, np.ndarray]]:
    """Secuencias deslizantes ``(indice_inicio, values[T, F], mask[T, F])``.

    A diferencia de ``iter_windows``, aquí NO se descartan secuencias por celdas
    ausentes: la máscara viaja con los datos y la decisión de qué hacer con la ausencia
    es del modelo (que debe aplicar el mismo contrato en train e inferencia).
    """
    if steps <= 0 or stride <= 0:
        msg = "steps y stride deben ser positivos"
        raise ValueError(msg)
    n = matrix.values.shape[0]
    for start in range(0, n - steps + 1, stride):
        yield (
            start,
            matrix.values[start : start + steps].copy(),
            matrix.valid[start : start + steps].copy(),
        )


def label_for(
    start_s: float,
    duration_s: float,
    fault_start_s: float | None,
    fault_end_s: float | None,
    session_duration_s: float,
) -> int:
    """1 si la secuencia solapa ≥ OVERLAP_LABEL con el intervalo inyectado."""
    if fault_start_s is None and fault_end_s is None:
        return 0
    f0 = fault_start_s if fault_start_s is not None else 0.0
    f1 = fault_end_s if fault_end_s is not None else session_duration_s
    overlap = max(0.0, min(start_s + duration_s, f1) - max(start_s, f0))
    return int(overlap / duration_s >= OVERLAP_LABEL)


@dataclass
class SequenceDataset:
    """Secuencias crudas de un split, con máscara, etiquetas y trazabilidad completa."""

    x: np.ndarray  # (n_seq, steps, n_pids) float64, NaN donde falta la señal
    mask: np.ndarray  # (n_seq, steps, n_pids) bool — True = valor observado
    y: np.ndarray  # 1 = secuencia con fallo activo (solape ≥ 0.5)
    session_ids: list[str]
    categories: list[str]
    starts_s: list[float]  # instante inicial de cada secuencia dentro de su sesión
    faults: list[str | None]
    fault_intervals: list[tuple[float, float] | None]
    sample_rate_hz: float
    steps: int
    pids: tuple[str, ...] = MATRIX_PIDS

    @property
    def duration_s(self) -> float:
        """Duración REAL de cada secuencia en segundos (nunca solo pasos)."""
        return self.steps / self.sample_rate_hz

    @property
    def n_features(self) -> int:
        return len(self.pids)

    @property
    def missing_fraction(self) -> float:
        """Fracción de celdas ausentes (0.0 en datos simulados completos)."""
        return float(1.0 - self.mask.mean()) if self.mask.size else 0.0

    def filled(self, fill: float = 0.0) -> np.ndarray:
        """Copia con las celdas ausentes sustituidas por ``fill`` (la máscara NO se pierde).

        Se ofrece como utilidad explícita para modelos que no aceptan NaN; el llamante
        declara el relleno y conserva ``mask`` para ponderar el error. Nunca se usa para
        «tapar» ausencias en las métricas.
        """
        out = self.x.copy()
        out[~self.mask] = fill
        return out


def sequences_from_matrices(
    items: list[tuple[WideMatrix, dict[str, Any]]], steps: int, stride: int
) -> SequenceDataset:
    """Construye el dataset desde matrices ya materializadas + metadatos de escenario.

    ``items`` = lista de ``(WideMatrix, meta)`` donde ``meta`` aporta lo que la matriz no
    conoce: ``category``, ``fault``, ``fault_start_s``, ``fault_end_s``, ``duration_s``.
    """
    xs, masks, ys, sids, cats, starts = [], [], [], [], [], []
    faults: list[str | None] = []
    intervals: list[tuple[float, float] | None] = []
    rate: float | None = None
    for matrix, meta in items:
        r = matrix.sample_rate_hz
        if rate is None:
            rate = r
        elif abs(r - rate) > 1e-9:
            msg = f"sample_rate mixto en el mismo dataset secuencial: {r} != {rate}"
            raise ValueError(msg)
        dur = steps / r
        for start_idx, vals, valid in iter_sequences(matrix, steps, stride):
            start_s = start_idx / r
            xs.append(vals)
            masks.append(valid)
            ys.append(
                label_for(
                    start_s,
                    dur,
                    meta.get("fault_start_s"),
                    meta.get("fault_end_s"),
                    meta.get("duration_s", 0.0),
                )
            )
            sids.append(matrix.session_id)
            cats.append(meta.get("category", "unknown"))
            starts.append(start_s)
            faults.append(meta.get("fault"))
            if meta.get("fault") is None:
                intervals.append(None)
            else:
                f0 = meta.get("fault_start_s") or 0.0
                f1 = meta.get("fault_end_s") or meta.get("duration_s", 0.0)
                intervals.append((float(f0), float(f1)))
    if rate is None:
        msg = "no hay matrices: dataset secuencial vacío"
        raise ValueError(msg)
    return SequenceDataset(
        x=np.asarray(xs, dtype=np.float64),
        mask=np.asarray(masks, dtype=bool),
        y=np.asarray(ys, dtype=np.int64),
        session_ids=sids,
        categories=cats,
        starts_s=starts,
        faults=faults,
        fault_intervals=intervals,
        sample_rate_hz=rate,
        steps=steps,
    )


def sequence_manifest(
    ds: SequenceDataset, *, dataset_id: str, source: str, provenance: str, seeds: list[int]
) -> dict[str, Any]:
    """Manifiesto versionado del dataset secuencial (hash + procedencia + longitudes)."""
    digest = hashlib.sha256()
    digest.update(np.ascontiguousarray(ds.x).tobytes())
    digest.update(np.ascontiguousarray(ds.mask).tobytes())
    digest.update(np.ascontiguousarray(ds.y).tobytes())
    return {
        "dataset_id": dataset_id,
        "derived_from": source,
        "provenance": provenance,
        "dataset_hash": digest.hexdigest(),
        "n_sequences": int(ds.x.shape[0]),
        "n_sessions": len(set(ds.session_ids)),
        "sessions": sorted(set(ds.session_ids)),
        "seeds": sorted(seeds),
        "sampling_rate_hz": ds.sample_rate_hz,
        "sequence_steps": ds.steps,
        "sequence_duration_seconds": ds.duration_s,
        "pids": list(ds.pids),
        "n_anomalous_sequences": int(ds.y.sum()),
        "missing_fraction": round(ds.missing_fraction, 6),
        "faults": sorted({f for f in ds.faults if f}),
    }


@dataclass
class OverlapReport:
    """Resultado de la auditoría anti-leakage entre particiones."""

    shared_sessions: list[str] = field(default_factory=list)
    shared_step_ranges: int = 0

    @property
    def clean(self) -> bool:
        return not self.shared_sessions and self.shared_step_ranges == 0


def audit_overlap(a: SequenceDataset, b: SequenceDataset) -> OverlapReport:
    """Comprueba que dos particiones no comparten sesiones NI tramos temporales.

    El split es por sesión, así que compartir sesión ya sería leakage; se comprueba
    además el solape de tramos ``[start, start+steps)`` por si alguna vez se dividiera
    una misma trayectoria entre particiones (prohibido por el protocolo).
    """
    shared = sorted(set(a.session_ids) & set(b.session_ids))
    ranges = 0
    if shared:
        spans_b: dict[str, list[tuple[float, float]]] = {}
        for sid, st in zip(b.session_ids, b.starts_s, strict=True):
            spans_b.setdefault(sid, []).append((st, st + b.duration_s))
        for sid, st in zip(a.session_ids, a.starts_s, strict=True):
            if sid not in spans_b:
                continue
            a0, a1 = st, st + a.duration_s
            ranges += sum(1 for b0, b1 in spans_b[sid] if a0 < b1 and b0 < a1)
    return OverlapReport(shared_sessions=shared, shared_step_ranges=ranges)
