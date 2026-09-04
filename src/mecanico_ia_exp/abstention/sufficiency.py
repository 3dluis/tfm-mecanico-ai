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

#: Versión de la política de suficiencia. Cambia cuando cambia **qué cuenta como
#: soporte**, no cuando cambia un umbral. Va al registro: sin ella, dos
#: ejecuciones con políticas distintas son indistinguibles desde el artefacto, y
#: la comparación entre versiones deja de ser posible.
VERIFIER_VERSION = "v1"


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

    min_confidence: float = 0.79
    """Punto de operación seleccionado sobre validación con criterio registrado.

    **No es una calibración ciega, y la versión anterior de este texto lo
    presentaba como si lo fuera.** La secuencia real, con sus artefactos:

    1. `docs/methodology/criterio-umbral.md`, escrito y comiteado **antes** del
       barrido: el umbral más bajo cuya precisión de decisión sobre validación
       alcance 0,93. La cifra 0,93 es una política declarada —como máximo siete
       errores por cada cien explicaciones emitidas—, no un hallazgo.
    2. Barrido completo en pasos de 0,01 sobre las 98 ventanas de validación
       (12 sesiones), registrado en `experiments/E15b_barrido_umbral.json` y
       `tables/E15b_barrido_umbral.csv`. **El conjunto de test no interviene.**
    3. El criterio original seleccionó **0,72**, con precisión 0,930233, es decir
       80 aciertos de 86: cumplía por **una ventana**, y los umbrales de 0,74 a
       0,78 dejaban de cumplir. Un punto aislado, no una meseta.
    4. `docs/methodology/criterio-umbral-enmienda-01.md` (ENM-U01) añade una
       exigencia de estabilidad definida de forma general: un umbral es estable
       si él y todos los de la rejilla hasta `t + 0,05` alcanzan el objetivo.
    5. La regla enmendada selecciona **0,79**, primer punto del tramo
       [0,79 · 0,86], de anchura 0,07. Precisión 0,938272 (76 de 81), cobertura
       0,8265 por ventana y 0,8252 por sesión.

    El valor anterior era 0,80, y **no procedía de ninguno de los dos criterios**:
    procedía de una tabla de cuatro puntos sin registro. Que 0,79 y 0,80 estén
    contiguos es una coincidencia de la curva, no una confirmación.

    Sensibilidad por remuestreo de las 12 sesiones (1 000 réplicas): en 0,79 la
    precisión mediana es 0,939 con intervalo [0,847 · 1,000], y alcanza el
    objetivo en el 60 % de las réplicas. Con doce sesiones la incertidumbre es
    grande y se declara; el remuestreo describe el punto elegido, no lo elige.
    """

    min_retrieval_score: float = 0.0
    """**Desactivado a propósito.** La puntuación de similitud no discrimina el
    soporte, y se midió:

    | | fragmentos | mediana |
    |---|---|---|
    | Sostienen la afirmación | 9 | 0,459 |
    | No la sostienen | 37 | 0,443 |

    El 38 % de los fragmentos que **no** sostienen puntúan por encima de la
    mediana de los que **sí**. Un umbral sobre esa puntuación filtraría por azar
    y daría apariencia de rigor.

    Es la tercera vez que aparece lo mismo por caminos distintos: en el orden de
    los resultados (E11), en la evaluación de la recuperación (E12) y ahora en el
    criterio de suficiencia. **La similitud no es evidencia.**

    Lo que sí discrimina es la verificación de soporte, que ya se aplica antes de
    llegar aquí. El parámetro se conserva --puede volver a tener sentido con otro
    modelo de embeddings-- pero por defecto no decide nada.
    """
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
