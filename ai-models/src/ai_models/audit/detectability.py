"""Métricas de auditoría de detectabilidad y cobertura — F19 (AUDIT-DATA-001).

**Definiciones y umbrales CONGELADOS antes de medir** (regla del autor: la clasificación
debe derivarse de métricas, no de inspección visual, y no puede fijarse a posteriori).

Este módulo NO es un detector: no se ajusta a nada, no tiene umbral operativo y no compite
con LOF ni con los autoencoders. Es instrumentación estadística para responder una
pregunta previa a cualquier modelo: **¿la anomalía sintética es distinguible del
comportamiento normal generado?** (Protocolo ML v1 §11: la evidencia negativa sobre el
propio banco de pruebas es un resultado legítimo.)

Distinción metodológica que esta auditoría hace operativa (F19 §18):

```
model failure           el fenómeno es distinguible y el modelo no lo detecta
dataset coverage failure  el comportamiento existe en test pero falta en train
anomaly construction failure  el fenómeno no es distinguible por construcción
```

Depende solo de numpy/scipy (regla de dependencias §9.4): no importa obd-lab.
"""

from dataclasses import dataclass
from typing import Any

import numpy as np

# ---------------------------------------------------------------------- umbrales
#: Cortes EXPLORATORIOS de la clasificación de detectabilidad (congelados en F19).
#: AUC = probabilidad de que una muestra anómala puntúe por encima de una normal en la
#: mejor dimensión disponible; |d| = tamaño de efecto de Cohen (0.2 pequeño, 0.5 medio,
#: 0.8 grande, convención habitual). Se documentan como exploratorios y revisables.
AUC_DETECTABLE = 0.90
AUC_WEAK = 0.70
AUC_INDISTINGUISHABLE = 0.60
D_LARGE = 0.8
D_NEGLIGIBLE = 0.2

#: Cobertura de un comportamiento normal en una partición (conteo de sesiones/ventanas).
COVERAGE_BUCKETS = ((0, "ABSENT"), (2, "RARE"), (9, "FEW"))  # >9 → REPRESENTED

DETECTABILITY_CLASSES = (
    "DETECTABLE",
    "WEAKLY_DETECTABLE",
    "INDISTINGUISHABLE",
    "INVALID_BY_CONSTRUCTION",
    "NEEDS_MORE_EVIDENCE",
)


# ------------------------------------------------------------- distancias por señal
def cohens_d(normal: np.ndarray, anomalous: np.ndarray) -> float:
    """Tamaño de efecto de Cohen con desviación combinada (0.0 si no hay dispersión)."""
    a, b = np.asarray(normal, float), np.asarray(anomalous, float)
    if a.size < 2 or b.size < 2:
        msg = "se necesitan ≥2 muestras por grupo para el tamaño de efecto"
        raise ValueError(msg)
    va, vb = a.var(ddof=1), b.var(ddof=1)
    pooled = np.sqrt(((a.size - 1) * va + (b.size - 1) * vb) / (a.size + b.size - 2))
    if pooled < 1e-12:
        return 0.0 if abs(b.mean() - a.mean()) < 1e-12 else float("inf")
    return float((b.mean() - a.mean()) / pooled)


def standardized_shift(normal: np.ndarray, anomalous: np.ndarray) -> float:
    """Desplazamiento de medias en unidades de la desviación NORMAL (σ del baseline)."""
    a, b = np.asarray(normal, float), np.asarray(anomalous, float)
    sd = a.std(ddof=1)
    if sd < 1e-12:
        return 0.0 if abs(b.mean() - a.mean()) < 1e-12 else float("inf")
    return float((b.mean() - a.mean()) / sd)


def auc(normal: np.ndarray, anomalous: np.ndarray) -> float:
    """AUC por rangos (Mann–Whitney): P(anómala > normal), con empates a 0.5.

    Es la medida de separabilidad principal de la auditoría: 0.5 = indistinguible,
    1.0 = perfectamente separable. No requiere entrenar nada.
    """
    a, b = np.asarray(normal, float).ravel(), np.asarray(anomalous, float).ravel()
    if a.size == 0 or b.size == 0:
        msg = "AUC no definida con un grupo vacío"
        raise ValueError(msg)
    allv = np.concatenate([a, b])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(allv.size, float)
    ranks[order] = np.arange(1, allv.size + 1, dtype=float)
    # corrección de empates: rango medio
    uniq, inv, counts = np.unique(allv, return_inverse=True, return_counts=True)
    if (counts > 1).any():
        sums = np.zeros(uniq.size)
        np.add.at(sums, inv, ranks)
        ranks = (sums / counts)[inv]
    rb = ranks[a.size :].sum()
    return float((rb - b.size * (b.size + 1) / 2) / (a.size * b.size))


def overlap_coefficient(normal: np.ndarray, anomalous: np.ndarray, bins: int = 50) -> float:
    """Solape de distribuciones (OVL) por histograma común: 1.0 = idénticas, 0.0 = disjuntas."""
    a, b = np.asarray(normal, float).ravel(), np.asarray(anomalous, float).ravel()
    lo, hi = float(min(a.min(), b.min())), float(max(a.max(), b.max()))
    if hi - lo < 1e-12:
        return 1.0
    edges = np.linspace(lo, hi, bins + 1)
    ha, _ = np.histogram(a, bins=edges, density=False)
    hb, _ = np.histogram(b, bins=edges, density=False)
    pa, pb = ha / max(ha.sum(), 1), hb / max(hb.sum(), 1)
    return float(np.minimum(pa, pb).sum())


def signal_to_normal_ratio(delta: float, normal_std: float) -> float:
    """Intensidad de la inyección relativa a la variabilidad normal (|Δ| / σ_normal).

    < 1.0 significa que el efecto introducido es MENOR que el ruido operativo normal de
    esa misma señal: la anomalía queda enterrada por construcción.
    """
    if normal_std < 1e-12:
        return float("inf") if abs(delta) > 1e-12 else 0.0
    return float(abs(delta) / normal_std)


def quantization_absorption(delta: float, step: float) -> float:
    """Cuántos cuantos del sensor cubre la inyección (<1 = absorbida por la discretización)."""
    if step <= 0:
        msg = "el paso de cuantización debe ser positivo"
        raise ValueError(msg)
    return float(abs(delta) / step)


# ------------------------------------------------------- distancias multivariables
def mahalanobis_scores(reference: np.ndarray, x: np.ndarray, ridge: float = 1e-6) -> np.ndarray:
    """Distancia de Mahalanobis de cada fila de ``x`` al conjunto ``reference``.

    Covarianza regularizada y pseudo-inversa: el objetivo es medir separabilidad, no
    construir un detector competitivo (regla F19 §4).
    """
    ref = np.asarray(reference, float)
    mu = ref.mean(axis=0)
    cov = np.cov(ref, rowvar=False)
    cov = np.atleast_2d(cov) + ridge * np.eye(ref.shape[1])
    inv = np.linalg.pinv(cov)
    d = np.asarray(x, float) - mu
    return np.asarray(np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", d, inv, d), 0.0)))


def correlation_shift(
    a1: np.ndarray, b1: np.ndarray, a2: np.ndarray, b2: np.ndarray
) -> dict[str, float]:
    """Cambio de la correlación de un par de señales entre normal (1) y anómalo (2)."""

    def _corr(x: np.ndarray, y: np.ndarray) -> float:
        x, y = np.asarray(x, float), np.asarray(y, float)
        if x.std() < 1e-12 or y.std() < 1e-12:
            return 0.0
        return float(np.corrcoef(x, y)[0, 1])

    r_norm, r_anom = _corr(a1, b1), _corr(a2, b2)
    return {
        "corr_normal": round(r_norm, 4),
        "corr_anomalous": round(r_anom, 4),
        "corr_shift": round(r_anom - r_norm, 4),
    }


def nearest_neighbour_ratio(reference: np.ndarray, x: np.ndarray) -> float:
    """Distancia media al vecino más cercano del conjunto normal, en unidades de la
    distancia típica intra-normal (>1 = las anómalas caen fuera de la nube normal)."""
    ref, q = np.asarray(reference, float), np.asarray(x, float)
    d_ref = np.linalg.norm(ref[:, None, :] - ref[None, :, :], axis=-1)
    np.fill_diagonal(d_ref, np.inf)
    base = float(np.median(d_ref.min(axis=1)))
    d_q = np.linalg.norm(q[:, None, :] - ref[None, :, :], axis=-1).min(axis=1)
    if base < 1e-12:
        return float("inf") if float(np.median(d_q)) > 1e-12 else 1.0
    return float(np.median(d_q) / base)


# ---------------------------------------------------------------- clasificación
@dataclass(frozen=True)
class DetectabilityVerdict:
    """Clasificación de una anomalía con la evidencia que la sustenta."""

    label: str
    auc_best: float
    cohens_d_best: float
    rationale: str

    def __post_init__(self) -> None:
        if self.label not in DETECTABILITY_CLASSES:
            msg = f"clase desconocida: {self.label}"
            raise ValueError(msg)


def classify_detectability(
    *,
    auc_best: float,
    d_best: float,
    absorbed_by_quantization: bool = False,
    ground_truth_broken: bool = False,
) -> DetectabilityVerdict:
    """Aplica los umbrales CONGELADOS (§17 de la instrucción F19).

    Prioridad: los fallos de construcción (inyección absorbida por la cuantización o
    ground truth que no sobrevive al pipeline) dominan sobre las métricas, porque en ese
    caso el número medido no es interpretable como capacidad de detección.
    """
    if ground_truth_broken:
        return DetectabilityVerdict(
            "INVALID_BY_CONSTRUCTION",
            auc_best,
            d_best,
            "el ground truth no sobrevive al pipeline: la etiqueta no describe lo que ocurre",
        )
    if absorbed_by_quantization:
        return DetectabilityVerdict(
            "INVALID_BY_CONSTRUCTION",
            auc_best,
            d_best,
            "la inyección es inferior al paso de cuantización del sensor: se pierde al codificar",
        )
    if auc_best >= AUC_DETECTABLE and abs(d_best) >= D_LARGE:
        return DetectabilityVerdict(
            "DETECTABLE", auc_best, d_best, "separación alta y tamaño de efecto grande"
        )
    if auc_best >= AUC_WEAK:
        return DetectabilityVerdict(
            "WEAKLY_DETECTABLE", auc_best, d_best, "separación moderada; margen estrecho"
        )
    if auc_best < AUC_INDISTINGUISHABLE and abs(d_best) < D_LARGE:
        return DetectabilityVerdict(
            "INDISTINGUISHABLE",
            auc_best,
            d_best,
            "separación próxima al azar: el efecto no supera la variabilidad normal",
        )
    return DetectabilityVerdict(
        "NEEDS_MORE_EVIDENCE", auc_best, d_best, "zona intermedia o señales contradictorias"
    )


# -------------------------------------------------------------------- cobertura
def coverage_bucket(count: int) -> str:
    """ABSENT (0) · RARE (1-2) · FEW (3-9) · REPRESENTED (≥10) — exploratorio, no umbral."""
    if count < 0:
        msg = "el conteo de cobertura no puede ser negativo"
        raise ValueError(msg)
    for limit, name in COVERAGE_BUCKETS:
        if count <= limit:
            return name
    return "REPRESENTED"


def coverage_gap(train_count: int, test_count: int) -> dict[str, Any]:
    """Detecta 'comportamiento normal presente en test pero ausente/raro en train'."""
    tr, te = coverage_bucket(train_count), coverage_bucket(test_count)
    gap = te in ("FEW", "REPRESENTED", "RARE") and tr in ("ABSENT", "RARE") and test_count > 0
    return {
        "train_count": train_count,
        "test_count": test_count,
        "train_bucket": tr,
        "test_bucket": te,
        "coverage_gap": bool(gap),
    }
