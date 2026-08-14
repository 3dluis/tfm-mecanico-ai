"""Métricas XAI de la Adenda XAI v1 §8 (ADR-0033) — definiciones congeladas.

Todas las funciones operan sobre rankings de atribución (|atribución| descendente) y
conjuntos GT de features; ninguna conoce SHAP ni el modelo (separación método↔métrica).
"""

from math import comb

import numpy as np
from scipy.stats import spearmanr


def top_k(attributions: dict[str, float], k: int) -> list[str]:
    """Top-K features por |atribución| (orden determinista: valor desc, nombre asc)."""
    return [
        name for name, _v in sorted(attributions.items(), key=lambda kv: (-abs(kv[1]), kv[0]))[:k]
    ]


def attribution_recall_at_k(attributions: dict[str, float], gt: frozenset[str], k: int) -> float:
    """AR@K = |GT ∩ Top-K| / min(|GT|, K)  (Adenda §8)."""
    if not gt:
        msg = "GT vacío: AR@K no está definido"
        raise ValueError(msg)
    hits = len(gt & set(top_k(attributions, k)))
    return hits / min(len(gt), k)


def attribution_precision_at_k(attributions: dict[str, float], gt: frozenset[str], k: int) -> float:
    """Precision@K = |GT ∩ Top-K| / K — SOLO válida si |GT| ≥ K (Adenda §8)."""
    if len(gt) < k:
        msg = f"Precision@{k} no aplica con |GT|={len(gt)} < K (definición congelada)"
        raise ValueError(msg)
    return len(gt & set(top_k(attributions, k))) / k


def random_recall_baseline(n_features: int, gt_size: int, k: int) -> float:
    """Esperanza de AR@K eligiendo K features al azar sin reemplazo (hipergeométrica).

    E[|GT ∩ TopK_aleatorio|] = K·|GT|/n; AR esperada = eso / min(|GT|, K). Baseline
    obligatorio de la adenda: un AR@K solo es interpretable frente a este valor.
    """
    if not (0 < gt_size <= n_features and 0 < k <= n_features):
        msg = "parámetros fuera de rango para el baseline aleatorio"
        raise ValueError(msg)
    expected_hits = k * gt_size / n_features
    return expected_hits / min(gt_size, k)


def random_recall_pvalue(n_features: int, gt_size: int, k: int, hits: int) -> float:
    """P(X ≥ hits) bajo selección aleatoria (hipergeométrica exacta) — apoyo a HX-XAI-1."""
    total = comb(n_features, k)
    acc = 0
    for x in range(hits, min(gt_size, k) + 1):
        acc += comb(gt_size, x) * comb(n_features - gt_size, k - x)
    return acc / total


def jaccard_at_k(a: dict[str, float], b: dict[str, float], k: int) -> float:
    """Jaccard entre Top-K de dos rankings (agreement / estabilidad, Adenda §§8-10)."""
    sa, sb = set(top_k(a, k)), set(top_k(b, k))
    union = sa | sb
    return len(sa & sb) / len(union) if union else 1.0


def rank_correlation(a: dict[str, float], b: dict[str, float]) -> float:
    """Spearman entre |atribuciones| de dos métodos sobre el MISMO conjunto de features."""
    names = sorted(set(a) & set(b))
    if len(names) < 3:
        msg = "se necesitan ≥3 features comunes para correlación de rango"
        raise ValueError(msg)
    rho = spearmanr([abs(a[n]) for n in names], [abs(b[n]) for n in names]).statistic
    return float(rho)


#: Cortes de la clasificación cualitativa de agreement (Adenda §8; exploratorios).
AGREE_THRESHOLD = 0.6
DISAGREE_THRESHOLD = 0.2


def agreement_class(jaccard5: float) -> str:
    """AGREE (≥0.6) · PARTIAL_AGREEMENT (0.2–0.6) · DISAGREE (<0.2) sobre Jaccard@5."""
    if jaccard5 >= AGREE_THRESHOLD:
        return "AGREE"
    if jaccard5 >= DISAGREE_THRESHOLD:
        return "PARTIAL_AGREEMENT"
    return "DISAGREE"


def stability_jaccard(rankings: list[dict[str, float]], k: int) -> float:
    """Estabilidad = Jaccard@K medio entre todos los pares de rankings (seeds/perturbación)."""
    if len(rankings) < 2:
        msg = "se necesitan ≥2 rankings para medir estabilidad"
        raise ValueError(msg)
    vals = [
        jaccard_at_k(rankings[i], rankings[j], k)
        for i in range(len(rankings))
        for j in range(i + 1, len(rankings))
    ]
    return float(np.mean(vals))
