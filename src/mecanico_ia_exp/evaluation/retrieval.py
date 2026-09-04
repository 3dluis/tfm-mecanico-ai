"""Métricas de recuperación (grupo M2).

Se calculan sobre un conjunto anotado, no inspeccionando a ojo si la respuesta
parece razonable. Una respuesta bien redactada sobre evidencia equivocada parece
igual de razonable, y ese es justamente el fallo que este trabajo estudia.

Las métricas se reportan **por caso y por condición de corpus**, no solo en
agregado: el agregado promedia condiciones diseñadas para diferir y esconde lo
único que se quería observar.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RetrievalMetrics:
    """Métricas de una consulta contra su verdad de referencia."""

    case_id: str
    k: int
    n_relevant: int
    n_retrieved: int
    precision_at_k: float
    recall_at_k: float
    hit_rate: float
    reciprocal_rank: float
    ndcg_at_k: float
    first_relevant_rank: int | None
    distractors_retrieved: int
    distractor_ranks: tuple[int, ...] = ()
    distractor_above_relevant: bool = False
    """El distractor aparece por encima de la evidencia aplicable.

    Es el fallo más grave de esta fase: el sistema prefiere un procedimiento de
    otro motor a la evidencia que sí aplica.
    """

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "k": self.k,
            "n_relevant": self.n_relevant,
            "n_retrieved": self.n_retrieved,
            "precision_at_k": round(self.precision_at_k, 4),
            "recall_at_k": round(self.recall_at_k, 4),
            "hit_rate": round(self.hit_rate, 4),
            "reciprocal_rank": round(self.reciprocal_rank, 4),
            "ndcg_at_k": round(self.ndcg_at_k, 4),
            "first_relevant_rank": self.first_relevant_rank,
            "distractors_retrieved": self.distractors_retrieved,
            "distractor_ranks": list(self.distractor_ranks),
            "distractor_above_relevant": self.distractor_above_relevant,
        }


def dcg(ganancias: list[float]) -> float:
    """Ganancia acumulada descontada. El descuento es logarítmico: un acierto en
    la posición 1 vale más que el mismo acierto en la 10."""
    return sum(g / math.log2(i + 2) for i, g in enumerate(ganancias))


def ndcg_at_k(relevancias: list[float], k: int) -> float:
    """nDCG normalizado contra el orden ideal de las mismas relevancias."""
    obtenido = dcg(relevancias[:k])
    ideal = dcg(sorted(relevancias, reverse=True)[:k])
    return obtenido / ideal if ideal > 0 else 0.0


def evaluate_case(
    *,
    case_id: str,
    retrieved_files: list[str],
    relevant_files: set[str],
    supporting_files: set[str] = frozenset(),  # type: ignore[assignment]
    distractor_files: set[str] = frozenset(),  # type: ignore[assignment]
    k: int = 10,
) -> RetrievalMetrics:
    """Evalúa una recuperación contra su verdad de referencia.

    ``retrieved_files`` llega en orden de recuperación. La granularidad es el
    fichero de origen y no el fragmento: el manual trocea un mismo procedimiento
    en varios fragmentos, y acertar cualquiera de ellos es haber encontrado el
    procedimiento.

    Los ficheros de apoyo --tablas de DTC, lógica de detección-- cuentan con
    ganancia parcial en el nDCG: son pertinentes pero no sustentan por sí solos
    un diagnóstico.
    """
    top = retrieved_files[:k]
    aciertos = [f for f in top if f in relevant_files]

    relevancias = [
        2.0 if f in relevant_files else 1.0 if f in supporting_files else 0.0 for f in top
    ]

    primer_relevante = next((i + 1 for i, f in enumerate(top) if f in relevant_files), None)
    rangos_distractor = tuple(i + 1 for i, f in enumerate(top) if f in distractor_files)

    # Recall sobre ficheros distintos: recuperar cinco fragmentos del mismo
    # procedimiento es haberlo encontrado una vez, no cinco.
    recuperados_relevantes = {f for f in top if f in relevant_files}
    recall = len(recuperados_relevantes) / len(relevant_files) if relevant_files else 0.0

    return RetrievalMetrics(
        case_id=case_id,
        k=k,
        n_relevant=len(relevant_files),
        n_retrieved=len(top),
        precision_at_k=len(aciertos) / len(top) if top else 0.0,
        recall_at_k=recall,
        hit_rate=1.0 if primer_relevante is not None else 0.0,
        reciprocal_rank=1.0 / primer_relevante if primer_relevante else 0.0,
        ndcg_at_k=ndcg_at_k(relevancias, k),
        first_relevant_rank=primer_relevante,
        distractors_retrieved=len(rangos_distractor),
        distractor_ranks=rangos_distractor,
        distractor_above_relevant=bool(
            rangos_distractor
            and (primer_relevante is None or min(rangos_distractor) < primer_relevante)
        ),
    )


@dataclass
class StrategyReport:
    """Resultado agregado de una estrategia de recuperación."""

    strategy: str
    k: int
    cases: list[RetrievalMetrics] = field(default_factory=list)

    def _media(self, atributo: str, solo_con_relevantes: bool = True) -> float:
        elegidos = [c for c in self.cases if not solo_con_relevantes or c.n_relevant > 0]
        if not elegidos:
            return float("nan")
        total = sum(float(getattr(c, atributo)) for c in elegidos)
        return total / len(elegidos)

    @property
    def mean_precision(self) -> float:
        return self._media("precision_at_k")

    @property
    def mean_recall(self) -> float:
        return self._media("recall_at_k")

    @property
    def mrr(self) -> float:
        return self._media("reciprocal_rank")

    @property
    def hit_rate(self) -> float:
        return self._media("hit_rate")

    @property
    def mean_ndcg(self) -> float:
        return self._media("ndcg_at_k")

    @property
    def distractors_total(self) -> int:
        return sum(c.distractors_retrieved for c in self.cases)

    @property
    def distractor_above_relevant(self) -> int:
        return sum(1 for c in self.cases if c.distractor_above_relevant)

    def to_dict(self) -> dict[str, object]:
        return {
            "strategy": self.strategy,
            "k": self.k,
            # Evaluados frente a puntuados. Un caso sin ficheros relevantes en la
            # verdad de referencia --la condición de evidencia retirada-- **forma
            # parte del experimento** pero no puede contribuir a una métrica que
            # divide por relevantes. Excluirlo en silencio publicaba una media
            # sobre cinco casos bajo un rótulo que decía seis.
            "n_evaluated": len(self.cases),
            "n_scored": sum(1 for c in self.cases if c.n_relevant > 0),
            "n_excluded_from_metric": sum(1 for c in self.cases if c.n_relevant == 0),
            "exclusion_reason": "no relevant files in ground truth",
            "excluded_case_ids": [c.case_id for c in self.cases if c.n_relevant == 0],
            "n_cases": len(self.cases),
            "precision_at_k": round(self.mean_precision, 4),
            "recall_at_k": round(self.mean_recall, 4),
            "mrr": round(self.mrr, 4),
            "hit_rate": round(self.hit_rate, 4),
            "ndcg_at_k": round(self.mean_ndcg, 4),
            "distractors_retrieved": self.distractors_total,
            "cases_with_distractor_above_relevant": self.distractor_above_relevant,
            "cases": [c.to_dict() for c in self.cases],
        }
