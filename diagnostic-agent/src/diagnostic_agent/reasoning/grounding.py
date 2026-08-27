"""Soporte, trazabilidad y suficiencia de la evidencia (ADR-0036, PI v4).

Este módulo implementa el tramo que la pregunta de investigación interroga:

1. **Descomposición** de una explicación en *afirmaciones* atómicas, cada una clasificada
   según qué evidencia necesita (documental, telemétrica o genérica).
2. **Verificación del soporte** de cada afirmación contra la evidencia realmente
   recuperada: la referencia debe existir, resolver y que su contenido sostenga lo
   afirmado. No basta con citar.
3. **Política de suficiencia**: decide si la evidencia disponible permite explicar o si
   procede **abstenerse**. La abstención es una salida correcta, no un fallo.

Todo es **determinista**: ningún paso usa un modelo de lenguaje. Las métricas de
trazabilidad del experimento (corrección y completitud de la citación, profundidad de
traza) se derivan de estas estructuras sin depender de un juez.
"""

import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass, field

from mecanico_contracts import ClaimKind, ExplanationDecision

#: Umbral por defecto de solape léxico para considerar que un fragmento sostiene una
#: afirmación documental. Valor congelado en `docs/alineacion_v4/03_diseno_experimental.md`.
DEFAULT_SUPPORT_THRESHOLD = 0.30

#: Fracción mínima de afirmaciones sustentadas para emitir explicación (política B3).
DEFAULT_SUFFICIENCY_RATIO = 0.60

#: Score mínimo de recuperación para que un fragmento cuente como evidencia disponible.
DEFAULT_MIN_RETRIEVAL_SCORE = 0.02

_STOP = {
    "de",
    "la",
    "el",
    "en",
    "y",
    "a",
    "los",
    "las",
    "del",
    "que",
    "con",
    "por",
    "un",
    "una",
    "se",
    "su",
    "al",
    "es",
    "o",
    "para",
    "mas",
    "entre",
    "sin",
    "sobre",
    "como",
    "muy",
    "esperado",
    "medio",
    "media",
    "puede",
    "ser",
    "hay",
    "este",
    "esta",
    "sus",
}


def _tokens(text: str) -> set[str]:
    """Tokenización normalizada (sin acentos, sin vacías, ≥3 caracteres)."""
    norm = unicodedata.normalize("NFKD", text.lower())
    norm = "".join(c for c in norm if not unicodedata.combining(c))
    return {t for t in re.findall(r"[a-z0-9_]+", norm) if t not in _STOP and len(t) > 2}


@dataclass(frozen=True)
class EvidenceRef:
    """Referencia citable a una unidad de evidencia.

    ``ref_id`` es un ``chunk_id`` del corpus (evidencia documental) o la clave de una
    feature (evidencia telemétrica). ``source_id`` es el ``document_id`` o el
    identificador del vector de features, y es lo que permite **rastrear hasta el dato**.
    """

    ref_id: str
    kind: ClaimKind
    source_id: str | None = None
    score: float = 0.0


@dataclass
class Claim:
    """Afirmación atómica de una explicación, con su referencia de evidencia."""

    text: str
    kind: ClaimKind
    refs: list[EvidenceRef] = field(default_factory=list)
    #: Rellenado por :func:`assess_support`.
    supported: bool = False
    #: Motivo cuando no está sustentada (para el análisis de errores).
    reason: str = ""

    @property
    def requires_evidence(self) -> bool:
        return self.kind is not ClaimKind.GENERIC

    @property
    def is_cited(self) -> bool:
        return bool(self.refs)


@dataclass
class SupportAssessment:
    """Resultado de verificar el soporte de todas las afirmaciones de una explicación."""

    claims: list[Claim]

    @property
    def requiring(self) -> list[Claim]:
        return [c for c in self.claims if c.requires_evidence]

    @property
    def supported_ratio(self) -> float:
        """*Groundedness*: fracción de afirmaciones que requieren evidencia y la tienen."""
        req = self.requiring
        if not req:
            return 1.0
        return sum(1 for c in req if c.supported) / len(req)

    @property
    def unsupported_count(self) -> int:
        """Métrica primaria heredada de H-EXP: afirmaciones no sustentadas."""
        return sum(1 for c in self.requiring if not c.supported)

    @property
    def citation_completeness(self) -> float:
        """Fracción de afirmaciones que requieren evidencia y que llevan referencia."""
        req = self.requiring
        if not req:
            return 1.0
        return sum(1 for c in req if c.is_cited) / len(req)

    @property
    def citation_correctness(self) -> float:
        """Fracción de afirmaciones citadas cuya referencia sostiene lo afirmado."""
        cited = [c for c in self.requiring if c.is_cited]
        if not cited:
            return 0.0
        return sum(1 for c in cited if c.supported) / len(cited)

    @property
    def trace_depth(self) -> float:
        """Fracción de afirmaciones sustentadas cuya referencia alcanza el dato de origen."""
        sup = [c for c in self.requiring if c.supported]
        if not sup:
            return 0.0
        return sum(1 for c in sup if any(r.source_id for r in c.refs)) / len(sup)


@dataclass(frozen=True)
class SufficiencyVerdict:
    """Decisión de la política de suficiencia."""

    decision: ExplanationDecision
    supported_ratio: float
    threshold: float
    #: Qué evidencia faltó, para declararlo al usuario cuando se abstiene.
    missing: tuple[str, ...] = ()

    @property
    def abstained(self) -> bool:
        return self.decision is ExplanationDecision.INSUFFICIENT_EVIDENCE


def decompose_explanation(
    *,
    cause: str = "",
    mechanism: str = "",
    telemetry_statements: Sequence[tuple[str, str | None]] = (),
    generic_statements: Sequence[str] = (),
) -> list[Claim]:
    """Descompone una explicación en afirmaciones atómicas, de forma determinista.

    El procedimiento está **congelado antes de ejecutar** los experimentos: la causa
    propuesta y el mecanismo causal se parten por frases —afirmaciones **documentales**,
    que requieren respaldo del corpus—, cada comprobación del verificador es una
    afirmación **telemétrica** con la feature que la ancla, y los avisos y
    recomendaciones son **genéricos** y no requieren evidencia. Cambiar este
    procedimiento invalidaría la comparación entre brazos, porque el denominador de la
    proporción de afirmaciones sustentadas dejaría de ser el mismo.
    """
    claims: list[Claim] = []
    for block in (cause, mechanism):
        for sentence in re.split(r"(?<=[.;])\s+", block.strip()):
            cleaned = sentence.strip()
            if len(cleaned) > 8:
                claims.append(Claim(text=cleaned, kind=ClaimKind.DOCUMENTARY))
    for text, anchor in telemetry_statements:
        refs = (
            [EvidenceRef(ref_id=anchor, kind=ClaimKind.TELEMETRIC, source_id=anchor)]
            if anchor
            else []
        )
        claims.append(Claim(text=text, kind=ClaimKind.TELEMETRIC, refs=refs))
    claims.extend(Claim(text=s, kind=ClaimKind.GENERIC) for s in generic_statements)
    return claims


def supports(claim_text: str, evidence_text: str, threshold: float) -> tuple[bool, float]:
    """¿El texto de la evidencia sostiene la afirmación? Solape léxico determinista.

    Se mide la fracción de términos significativos de la afirmación presentes en la
    evidencia. Es una aproximación deliberadamente conservadora y **auditable**: no
    pretende entender el texto, sino comprobar que la cita habla de lo que se afirma. Su
    limitación se declara como amenaza a la validez del constructo.
    """
    ct = _tokens(claim_text)
    if not ct:
        return False, 0.0
    overlap = len(ct & _tokens(evidence_text)) / len(ct)
    return overlap >= threshold, round(overlap, 4)


def assess_support(
    claims: list[Claim],
    *,
    documents: dict[str, str],
    features: dict[str, float],
    threshold: float = DEFAULT_SUPPORT_THRESHOLD,
) -> SupportAssessment:
    """Verifica el soporte de cada afirmación y anota por qué falla cuando falla.

    ``documents`` mapea ``chunk_id`` → texto recuperado; ``features`` es el vector de la
    ventana anómala. Una afirmación documental solo se considera sustentada si **alguna**
    de sus referencias resuelve a un fragmento recuperado cuyo contenido la sostiene.
    """
    for claim in claims:
        if not claim.requires_evidence:
            claim.supported = True
            continue
        if not claim.refs:
            claim.supported, claim.reason = False, "sin referencia de evidencia"
            continue
        for ref in claim.refs:
            if ref.kind is ClaimKind.DOCUMENTARY:
                text = documents.get(ref.ref_id)
                if text is None:
                    claim.reason = f"la referencia {ref.ref_id} no resuelve"
                    continue
                ok, _ = supports(claim.text, text, threshold)
                if ok:
                    claim.supported, claim.reason = True, ""
                    break
                claim.reason = f"la referencia {ref.ref_id} no sostiene la afirmación"
            else:
                if ref.ref_id in features:
                    claim.supported, claim.reason = True, ""
                    break
                claim.reason = f"la feature {ref.ref_id} no está en la ventana"
    return SupportAssessment(claims=claims)


def decide_sufficiency(
    assessment: SupportAssessment,
    *,
    retrieved_scores: Sequence[float] = (),
    contradicted: bool = False,
    telemetry_supported: bool = True,
    ambiguous: bool = False,
    ratio_threshold: float = DEFAULT_SUFFICIENCY_RATIO,
    min_retrieval_score: float = DEFAULT_MIN_RETRIEVAL_SCORE,
    enabled: bool = True,
) -> SufficiencyVerdict:
    """Decide entre explicar y abstenerse.

    Con ``enabled=False`` la política queda desactivada y el agente **siempre explica**:
    es el brazo B2 del experimento (RAG sin abstención), que sirve para medir cuánto
    aporta poder no responder.

    El orden de comprobación es deliberado. Primero la recuperación: si nada relevante se
    recuperó, la evidencia es insuficiente con independencia de lo que el generador haya
    producido — es el caso del Escenario B con el corpus sin los documentos del mecanismo.
    Después el soporte agregado. Solo entonces la contradicción y la ambigüedad, porque
    **ambas presuponen que hay evidencia con la que contradecir o dudar**: declarar
    «evidencia contradictoria» cuando en realidad no se sostiene nada sería afirmar más de
    lo que se sabe.

    Segunda limitación, del constructo: una afirmación documental que **cita literalmente**
    el fragmento del que procede queda sustentada por construcción. El soporte documental,
    por sí solo, se aprueba con solo copiar el corpus. Por eso la decisión exige el doble
    anclaje —documental y telemétrico— y por eso la corrección de la citación se compara
    contra un control de atribución trivial en el experimento.

    Limitación conocida y deliberadamente no ocultada: esta política evalúa el soporte de
    lo que el sistema *afirma*, no si lo afirmado es lo correcto. Si al retirar del corpus
    el mecanismo de un caso el generador propone un mecanismo **adyacente** que el corpus
    sí documenta, la explicación puede resultar sustentada y aun así ser un diagnóstico
    equivocado. Ese es exactamente el fallo que la tasa de falsa aceptación (M17) mide en
    el experimento, y por eso la construcción del corpus C-B retira el mecanismo del caso
    **y sus sinónimos técnicos**, no solo un documento.
    """
    ratio = assessment.supported_ratio
    if not enabled:
        return SufficiencyVerdict(ExplanationDecision.SUPPORTED, ratio, ratio_threshold)

    usable = [s for s in retrieved_scores if s >= min_retrieval_score]
    if retrieved_scores and not usable:
        return SufficiencyVerdict(
            ExplanationDecision.INSUFFICIENT_EVIDENCE,
            ratio,
            ratio_threshold,
            ("ningún fragmento recuperado alcanza el umbral de relevancia",),
        )
    if not retrieved_scores:
        return SufficiencyVerdict(
            ExplanationDecision.INSUFFICIENT_EVIDENCE,
            ratio,
            ratio_threshold,
            ("la recuperación no devolvió evidencia documental",),
        )
    if ratio < ratio_threshold:
        missing = tuple(
            f"{c.text[:80]} → {c.reason}" for c in assessment.requiring if not c.supported
        )[:5]
        return SufficiencyVerdict(
            ExplanationDecision.INSUFFICIENT_EVIDENCE, ratio, ratio_threshold, missing
        )
    if contradicted:
        return SufficiencyVerdict(ExplanationDecision.CONTRADICTED, ratio, ratio_threshold)
    if not telemetry_supported:
        # Doble anclaje: una explicación sostenida solo por el documento, sin que el
        # verificador determinista confirme la firma en la telemetría del caso, no está
        # sostenida. Sin esta condición bastaría con citar el corpus para parecer
        # sustentado, que es la forma más fácil de aprobar una métrica de soporte sin
        # decir nada del vehículo.
        return SufficiencyVerdict(
            ExplanationDecision.INSUFFICIENT_EVIDENCE,
            ratio,
            ratio_threshold,
            ("la telemetría del caso no confirma la firma del mecanismo propuesto",),
        )
    if ambiguous:
        return SufficiencyVerdict(ExplanationDecision.INCONCLUSIVE, ratio, ratio_threshold)
    return SufficiencyVerdict(ExplanationDecision.SUPPORTED, ratio, ratio_threshold)
