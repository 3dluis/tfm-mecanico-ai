"""Verificador de suficiencia de evidencia.

**Determinista y fuera del modelo de lenguaje.** El LLM no decide si hay
evidencia suficiente: recibe la decisión tomada y redacta en consecuencia. Si
decidiera él, la respuesta a la pregunta de investigación dependería de su
disposición a admitir que no sabe algo, que es justo lo que no se puede dar por
supuesto.

El criterio es una **conjunción**, no un promedio ponderado. Un promedio deja que
un valor alto compense a uno inaceptablemente bajo, y aquí ningún factor es
compensable: sin cobertura de afirmaciones no hay explicación que sostener, por
muy confiado que esté el modelo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from mecanico_ia_exp.evidence.model import (
    Claim,
    EvidenceBundle,
    SupportStatus,
)
from mecanico_ia_exp.rag.vehicle import Applicability


class Sufficiency(StrEnum):
    SUPPORTED = "SUPPORTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class Decision(StrEnum):
    EXPLAIN = "EXPLAIN"
    ABSTAIN = "ABSTAIN"


#: Motivos por los que la evidencia puede resultar insuficiente. Se devuelven
#: TODOS los que se cumplen, no el primero: saber que falla una sola condición no
#: es lo mismo que saber que fallan cuatro.
class Reason(StrEnum):
    LOW_CONFIDENCE = "LOW_MODEL_CONFIDENCE"
    NO_DOCUMENTARY_EVIDENCE = "NO_APPLICABLE_DOCUMENTARY_EVIDENCE"
    LOW_RETRIEVAL_SUPPORT = "LOW_RETRIEVAL_SUPPORT"
    TOO_FEW_CHUNKS = "TOO_FEW_SUPPORTING_CHUNKS"
    TOO_FEW_SOURCES = "TOO_FEW_DISTINCT_SOURCES"
    LOW_CLAIM_COVERAGE = "LOW_CLAIM_COVERAGE"
    CONTRADICTION = "CONTRADICTION_DETECTED"
    NO_OBSERVATIONAL_EVIDENCE = "NO_OBSERVATIONAL_EVIDENCE"


@dataclass(frozen=True)
class SufficiencyThresholds:
    """Umbrales del criterio.

    **Se calibran únicamente con validación.** Ajustarlos mirando el test
    convertiría las cifras finales en una descripción de datos ya vistos en lugar
    de una predicción.
    """

    min_confidence: float = 0.60
    min_retrieval_score: float = 0.35
    min_supporting_chunks: int = 2
    min_distinct_sources: int = 1
    min_claim_coverage: float = 0.80
    allow_compatible_applicability: bool = False
    """Política declarada. Por defecto solo la coincidencia exacta sostiene."""

    @property
    def accepted_applicability(self) -> frozenset[str]:
        grados = {Applicability.EXACT_MATCH.value}
        if self.allow_compatible_applicability:
            grados.add(Applicability.COMPATIBLE.value)
        return frozenset(grados)

    def to_dict(self) -> dict[str, Any]:
        return {
            "min_confidence": self.min_confidence,
            "min_retrieval_score": self.min_retrieval_score,
            "min_supporting_chunks": self.min_supporting_chunks,
            "min_distinct_sources": self.min_distinct_sources,
            "min_claim_coverage": self.min_claim_coverage,
            "allow_compatible_applicability": self.allow_compatible_applicability,
            "accepted_applicability": sorted(self.accepted_applicability),
        }


@dataclass
class SufficiencyVerdict:
    """Resultado de la verificación, con todo lo que llevó a él."""

    case_id: str
    sufficiency: Sufficiency
    decision: Decision
    reasons: list[Reason] = field(default_factory=list)
    signals: dict[str, Any] = field(default_factory=dict)
    missing_evidence: list[str] = field(default_factory=list)

    @property
    def supported(self) -> bool:
        return self.sufficiency is Sufficiency.SUPPORTED

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "sufficiency": self.sufficiency.value,
            "decision": self.decision.value,
            "reasons": [r.value for r in self.reasons],
            "signals": self.signals,
            "missing_evidence": self.missing_evidence,
        }

    def __str__(self) -> str:
        if self.supported:
            return f"{self.case_id}: SUPPORTED → EXPLAIN"
        motivos = ", ".join(r.value for r in self.reasons)
        return f"{self.case_id}: INSUFFICIENT_EVIDENCE → ABSTAIN ({motivos})"


def claim_coverage(claims: list[Claim]) -> float:
    """Proporción de afirmaciones que llevan evidencia de ambas clases.

    Exigir ambas no es rigor gratuito. Una afirmación con solo observación
    describe sin interpretar --«el ajuste está en +6 %»--; una con solo documento
    interpreta sin mirar el coche --«una fuga produce ajustes positivos»--. La
    afirmación diagnóstica necesita las dos.

    Y no basta con que la cita exista: tiene que **sostener** lo afirmado. Solo
    cuentan las afirmaciones cuyo estado es ``SUPPORTED``, que es el que
    ``check_support`` concede tras comprobar que el fragmento habla de la señal
    en contenido diagnóstico del vehículo.
    """
    if not claims:
        return 0.0
    completas = sum(
        1
        for c in claims
        if c.has_observational and c.has_documentary and c.support_status is SupportStatus.SUPPORTED
    )
    return completas / len(claims)


def detect_contradictions(bundle: EvidenceBundle) -> list[str]:
    """Contradicciones detectables de forma determinista.

    Solo se declara contradicción sobre lo que se puede comprobar sin
    interpretar el texto: afirmaciones marcadas como contradichas, y evidencia
    documental que el validador de aplicabilidad ha rechazado pero que alguna
    afirmación cita igualmente.

    No se intenta detectar contradicción semántica entre fragmentos: eso exigiría
    un juicio que este componente no puede hacer de forma verificable, y fingir
    que sí lo hace sería peor que no hacerlo.
    """
    encontradas: list[str] = []
    for claim in bundle.claims:
        if claim.support_status is SupportStatus.CONTRADICTED:
            encontradas.append(f"afirmación {claim.claim_id} marcada como contradicha")

    inaplicables = {
        d.chunk_id
        for d in bundle.documents
        if d.applicability in {Applicability.INCOMPATIBLE.value, Applicability.UNKNOWN.value}
    }
    for claim in bundle.claims:
        citados = set(claim.chunk_ids) & inaplicables
        if citados:
            encontradas.append(
                f"afirmación {claim.claim_id} cita evidencia no aplicable: {sorted(citados)}"
            )
    return encontradas


class EvidenceVerifier:
    """Decide si la evidencia disponible sostiene una explicación."""

    def __init__(self, thresholds: SufficiencyThresholds | None = None) -> None:
        self.thresholds = thresholds or SufficiencyThresholds()

    def verify(self, bundle: EvidenceBundle) -> SufficiencyVerdict:
        t = self.thresholds
        grados = t.accepted_applicability

        aplicables = bundle.applicable_documents(grados)
        fuentes = bundle.distinct_sources(grados)
        mejor_score = max((d.score for d in aplicables), default=0.0)
        cobertura = claim_coverage(bundle.claims)
        contradicciones = detect_contradictions(bundle)

        señales: dict[str, Any] = {
            "confidence": round(bundle.confidence, 4),
            "model_confidence": round(bundle.model_confidence, 4),
            "calibrated": bundle.calibrated_confidence is not None,
            "n_observations": len(bundle.observations),
            "n_documents_retrieved": len(bundle.documents),
            "n_documents_applicable": len(aplicables),
            "n_distinct_sources": len(fuentes),
            "best_retrieval_score": round(mejor_score, 4),
            "claim_coverage": round(cobertura, 4),
            "n_claims": len(bundle.claims),
            "contradictions": contradicciones,
        }

        motivos: list[Reason] = []
        faltante: list[str] = []

        if bundle.confidence < t.min_confidence:
            motivos.append(Reason.LOW_CONFIDENCE)
            faltante.append(f"confianza {bundle.confidence:.3f} < {t.min_confidence:.2f}")
        if not bundle.observations:
            motivos.append(Reason.NO_OBSERVATIONAL_EVIDENCE)
            faltante.append("ninguna observación del vehículo")
        if not aplicables:
            motivos.append(Reason.NO_DOCUMENTARY_EVIDENCE)
            faltante.append("ningún fragmento documental aplicable a este vehículo")
        else:
            if mejor_score < t.min_retrieval_score:
                motivos.append(Reason.LOW_RETRIEVAL_SUPPORT)
                faltante.append(f"mejor puntuación {mejor_score:.3f} < {t.min_retrieval_score:.2f}")
            if len(aplicables) < t.min_supporting_chunks:
                motivos.append(Reason.TOO_FEW_CHUNKS)
                faltante.append(
                    f"{len(aplicables)} fragmentos aplicables < {t.min_supporting_chunks}"
                )
            if len(fuentes) < t.min_distinct_sources:
                motivos.append(Reason.TOO_FEW_SOURCES)
                faltante.append(f"{len(fuentes)} documentos distintos < {t.min_distinct_sources}")
        if cobertura < t.min_claim_coverage:
            motivos.append(Reason.LOW_CLAIM_COVERAGE)
            faltante.append(f"cobertura {cobertura:.2f} < {t.min_claim_coverage:.2f}")
        if contradicciones:
            motivos.append(Reason.CONTRADICTION)
            faltante.extend(contradicciones)

        suficiente = not motivos
        return SufficiencyVerdict(
            case_id=bundle.case_id,
            sufficiency=Sufficiency.SUPPORTED if suficiente else Sufficiency.INSUFFICIENT_EVIDENCE,
            decision=Decision.EXPLAIN if suficiente else Decision.ABSTAIN,
            reasons=motivos,
            signals=señales,
            missing_evidence=faltante,
        )
