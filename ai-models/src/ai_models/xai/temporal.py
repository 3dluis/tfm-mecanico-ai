"""XAI temporal — atribución feature×tiempo (Adenda XAI v1, extensión temporal F18).

**Definiciones CONGELADAS antes de ejecutar EXP-ANOM-009** (regla del autor: «solo si
pueden definirse antes de mirar resultados; no inventar métricas retrospectivamente»).

Representación canónica: matriz ``A[t, f]`` (``n_steps`` × ``n_features``) de atribución
del score explicado sobre una secuencia. Los agregados NO la sustituyen: se DERIVAN de
ella (regla del autor F18):

- atribución por feature   ``a_f = Σ_t |A[t, f]|``   → «¿qué señal?»
- atribución por instante  ``a_t = Σ_f |A[t, f]|``   → «¿cuándo?»
- ranking de celdas Top-K ``(t, f)`` por ``|A[t, f]|`` → «¿qué combinación señal-momento?»

Ground truth temporal para datos sintéticos (provenance SIMULATED): el catálogo de
inyección declara qué PIDs toca cada fallo (``FAULT_AFFECTED_PIDS``, ya congelado en F16)
y el escenario declara el intervalo inyectado ``[fault_start_s, fault_end_s]``. Para el
nivel secuencial las features SON los PIDs, de modo que el GT de features no necesita
traducción de esquema (a diferencia de fs1/fs2-lite).

Métricas (las tres comparten la forma del baseline aleatorio hipergeométrico ya congelado
en ``metrics.random_recall_baseline``, de modo que un valor solo es interpretable frente
a su azar):

- **FAR@K** (Feature Attribution Recall) — ``|GT_f ∩ TopK_f| / min(|GT_f|, K)`` sobre el
  agregado por feature. Azar: ``n = n_features``.
- **TAR@K** (Temporal Attribution Recall) — ``|GT_t ∩ TopK_t| / min(|GT_t|, K)`` sobre el
  agregado por instante, con ``GT_t`` = pasos de la secuencia dentro del intervalo
  inyectado. Azar: ``n = n_steps``.
- **FTH@K** (Feature-Time Hit) — fracción de celdas Top-K que caen en la región correcta
  ``GT_f × GT_t``, normalizada como las anteriores. Azar: ``n = n_steps · n_features``.

Ninguna de estas métricas mide causalidad: sigue vigente la regla de capas
``atribución XAI ≠ causalidad mecánica ≠ diagnóstico confirmado`` (ADR-0033). En modelos
temporales la atribución puede REPARTIRSE entre features y entre pasos (especialmente en
anomalías relacionales): un valor intermedio no implica fallo del explicador.
"""

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from ai_models.xai.ground_truth import FAULT_AFFECTED_PIDS


def _abs_matrix(a: np.ndarray) -> np.ndarray:
    if a.ndim != 2:
        msg = f"la atribución temporal debe ser (n_steps, n_features); recibido {a.shape}"
        raise ValueError(msg)
    return np.abs(np.asarray(a, dtype=np.float64))


def aggregate_by_feature(a: np.ndarray, feature_names: Sequence[str]) -> dict[str, float]:
    """``a_f = Σ_t |A[t, f]|`` — vista secundaria «¿qué señal?» (derivada, no sustituta)."""
    m = _abs_matrix(a)
    if m.shape[1] != len(feature_names):
        msg = f"dimensión de features {m.shape[1]} != {len(feature_names)} nombres"
        raise ValueError(msg)
    return {name: float(m[:, j].sum()) for j, name in enumerate(feature_names)}


def aggregate_by_time(a: np.ndarray) -> dict[int, float]:
    """``a_t = Σ_f |A[t, f]|`` — vista secundaria «¿cuándo?» (clave = índice de paso)."""
    m = _abs_matrix(a)
    return {t: float(m[t, :].sum()) for t in range(m.shape[0])}


def top_k_steps(a: np.ndarray, k: int) -> list[int]:
    """Top-K instantes por atribución agregada (desempate determinista: índice asc)."""
    agg = aggregate_by_time(a)
    return [t for t, _v in sorted(agg.items(), key=lambda kv: (-kv[1], kv[0]))[:k]]


def top_k_cells(a: np.ndarray, feature_names: Sequence[str], k: int) -> list[tuple[int, str]]:
    """Top-K celdas ``(paso, feature)`` por ``|A[t, f]|`` (desempate: paso asc, nombre asc)."""
    m = _abs_matrix(a)
    if m.shape[1] != len(feature_names):
        msg = f"dimensión de features {m.shape[1]} != {len(feature_names)} nombres"
        raise ValueError(msg)
    cells = [(t, feature_names[f], m[t, f]) for t in range(m.shape[0]) for f in range(m.shape[1])]
    cells.sort(key=lambda c: (-c[2], c[0], c[1]))
    return [(t, f) for t, f, _v in cells[:k]]


@dataclass(frozen=True)
class TemporalGroundTruth:
    """GT de atribución para una secuencia con fallo inyectado (datos SIMULATED)."""

    fault: str
    features: frozenset[str]  # PIDs afectados por la transformación del catálogo
    time_steps: frozenset[int]  # pasos de ESTA secuencia dentro del intervalo inyectado
    anomaly_start_s: float
    anomaly_end_s: float

    @property
    def n_cells(self) -> int:
        return len(self.features) * len(self.time_steps)


def temporal_gt_for(
    fault: str,
    *,
    sequence_start_s: float,
    n_steps: int,
    sample_rate_hz: float,
    fault_start_s: float,
    fault_end_s: float,
) -> TemporalGroundTruth:
    """GT temporal de una secuencia concreta (KeyError si el fallo no está en el catálogo).

    Un paso ``t`` entra en ``time_steps`` si su instante absoluto
    ``sequence_start_s + t/sample_rate_hz`` cae dentro de ``[fault_start_s, fault_end_s)``.
    El mapeo fallo→PIDs es el congelado en F16: no se infiere en caliente.
    """
    pids = FAULT_AFFECTED_PIDS[fault]
    if sample_rate_hz <= 0:
        msg = "sample_rate_hz debe ser positivo"
        raise ValueError(msg)
    steps = {
        t
        for t in range(n_steps)
        if fault_start_s <= sequence_start_s + t / sample_rate_hz < fault_end_s
    }
    return TemporalGroundTruth(
        fault=fault,
        features=frozenset(pids),
        time_steps=frozenset(steps),
        anomaly_start_s=fault_start_s,
        anomaly_end_s=fault_end_s,
    )


def _recall(hits: int, gt_size: int, k: int) -> float:
    if gt_size <= 0:
        msg = "GT vacío: la métrica no está definida"
        raise ValueError(msg)
    return hits / min(gt_size, k)


def feature_attribution_recall_at_k(
    a: np.ndarray, feature_names: Sequence[str], gt_features: frozenset[str], k: int
) -> float:
    """FAR@K sobre el agregado por feature (mismo criterio que AR@K de la adenda §8)."""
    agg = aggregate_by_feature(a, feature_names)
    top = [n for n, _v in sorted(agg.items(), key=lambda kv: (-kv[1], kv[0]))[:k]]
    return _recall(len(gt_features & set(top)), len(gt_features), k)


def temporal_attribution_recall_at_k(a: np.ndarray, gt_steps: frozenset[int], k: int) -> float:
    """TAR@K: ¿los instantes más atribuidos caen dentro del intervalo inyectado?"""
    return _recall(len(gt_steps & set(top_k_steps(a, k))), len(gt_steps), k)


def feature_time_hit_at_k(
    a: np.ndarray,
    feature_names: Sequence[str],
    gt_features: frozenset[str],
    gt_steps: frozenset[int],
    k: int,
) -> float:
    """FTH@K: celdas Top-K que caen en la región correcta ``GT_f × GT_t``."""
    cells = top_k_cells(a, feature_names, k)
    hits = sum(1 for t, f in cells if f in gt_features and t in gt_steps)
    return _recall(hits, len(gt_features) * len(gt_steps), k)


def cell_stability_jaccard(
    matrices: Sequence[np.ndarray], feature_names: Sequence[str], k: int
) -> float:
    """Estabilidad = Jaccard@K medio entre Top-K de celdas de varias matrices (seeds/ruido)."""
    if len(matrices) < 2:
        msg = "se necesitan ≥2 matrices para medir estabilidad"
        raise ValueError(msg)
    tops = [set(top_k_cells(m, feature_names, k)) for m in matrices]
    vals = [
        len(tops[i] & tops[j]) / len(tops[i] | tops[j]) if tops[i] | tops[j] else 1.0
        for i in range(len(tops))
        for j in range(i + 1, len(tops))
    ]
    return float(np.mean(vals))
