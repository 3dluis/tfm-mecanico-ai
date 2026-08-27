"""Memoria episódica y semántica: recuperación por similitud con ponderación epistemológica.

ADR-0013: un caso simulado jamás pesa como uno validado por humanos. La similitud de la
firma numérica se multiplica por el peso del nivel epistemológico del caso.


FUERA DEL ALCANCE EXPERIMENTAL de la PI v4 (ADR-0036): la memoria no participa en la
evaluación del TFM y los experimentos se ejecutan con ``AgentConfig.memory_enabled=False``.
El módulo se conserva funcional y cubierto por tests; su evaluación queda como
continuación del trabajo (docs/alineacion_v4/05_fuera_de_alcance.md §1).
"""

import math
from datetime import UTC, datetime

from diagnostic_agent.storage.schema import CaseMemoryRow, LearnedPatternRow
from diagnostic_agent.storage.store import EdgeStoreV2
from mecanico_contracts import CaseMemory, EpistemicLevel, LearnedPattern, PatternStatus

#: Peso epistemológico (ADR-0013 §3): lo simulado informa, lo validado decide.
EPISTEMIC_WEIGHT: dict[EpistemicLevel, float] = {
    EpistemicLevel.SIMULATED: 0.5,
    EpistemicLevel.SYNTHETIC: 0.5,
    EpistemicLevel.PUBLIC_DATASET: 0.7,
    EpistemicLevel.REAL_UNVALIDATED: 0.8,
    EpistemicLevel.HUMAN_VALIDATED: 1.0,
}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    common = set(a) & set(b)
    if not common:
        return 0.0
    num = sum(a[k] * b[k] for k in common)
    da = math.sqrt(sum(v * v for v in a.values()))
    db = math.sqrt(sum(v * v for v in b.values()))
    return num / (da * db) if da and db else 0.0


class EpisodicMemory:
    """Casos históricos recuperables por similitud de firma sintomática."""

    def __init__(self, store: EdgeStoreV2) -> None:
        self.store = store

    def similar_cases(
        self, signature: dict[str, float], k: int = 3, min_score: float = 0.05
    ) -> list[tuple[CaseMemory, float]]:
        results: list[tuple[CaseMemory, float]] = []
        for case in self.store.list_(CaseMemory, CaseMemoryRow):
            sim = _cosine(signature, case.symptom_signature)
            weight = EPISTEMIC_WEIGHT[case.epistemic_level]
            score = sim * weight
            if score >= min_score:
                results.append((case, round(score, 4)))
        results.sort(key=lambda x: -x[1])
        return results[:k]

    def remember(self, case: CaseMemory) -> None:
        self.store.add(CaseMemoryRow, case)


class SemanticMemory:
    """Patrones consolidados (solo lectura para el agente; la consolidación es un
    proceso aparte y la promoción a VALIDATED nunca es automática — ADR-0013)."""

    def __init__(self, store: EdgeStoreV2) -> None:
        self.store = store

    def similar_patterns(
        self, signature: dict[str, float], k: int = 2, min_score: float = 0.05
    ) -> list[tuple[LearnedPattern, float]]:
        results: list[tuple[LearnedPattern, float]] = []
        for pattern in self.store.list_(LearnedPattern, LearnedPatternRow):
            if pattern.status in (PatternStatus.REJECTED, PatternStatus.RETIRED):
                continue
            score = _cosine(signature, pattern.telemetry_signature)
            if score >= min_score:
                results.append((pattern, round(score, 4)))
        results.sort(key=lambda x: -x[1])
        return results[:k]

    def register_candidate(self, pattern: LearnedPattern) -> None:
        """Registra un patrón CANDIDATE (única transición permitida en esta fase)."""
        if pattern.status is not PatternStatus.CANDIDATE:
            msg = "solo se permite registrar patrones en estado CANDIDATE (ADR-0013)"
            raise ValueError(msg)
        self.store.add(LearnedPatternRow, pattern)

    def touch(self, pattern_id: str) -> None:
        """Actualiza last_seen (evidencia acumulándose; sin cambio de estado)."""
        from sqlalchemy.orm import Session as OrmSession

        with OrmSession(self.store.engine) as s:
            row = s.get(LearnedPatternRow, pattern_id)
            if row is not None:
                row.last_seen = datetime.now(tz=UTC)
                s.commit()
