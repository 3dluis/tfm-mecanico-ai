"""Agente de diagnóstico v1 (LangGraph) sobre la arquitectura de datos v2 (ADR-0014).

Responsabilidades estrictas por nodo (requisito del autor):
  triage      organiza anomalía y contexto (determinista)
  recall      recupera casos/patrones similares según memory_mode (auditado)
  retrieve    recupera documentación técnica (auditado)
  hypothesize propone hipótesis estructuradas (LLM plugable; único nodo generativo)
  verify      contrasta CADA hipótesis contra features reales (determinista)
  decide      descompone la explicación en afirmaciones, verifica su soporte documental
              y decide entre explicar o ABSTENERSE (determinista, ADR-0036)
  report      compone la explicación final o la declaración de evidencia insuficiente
  memorize    persiste el episodio; NO promociona conocimiento (solo CANDIDATE).
              FUERA DEL ALCANCE EXPERIMENTAL de la PI v4: se desactiva con
              ``AgentConfig.memory_enabled=False`` (docs/alineacion_v4/05_fuera_de_alcance.md)

Todo queda persistido: AgentRun, AgentStep (E/S estructuradas, sin chain-of-thought),
RetrievalEvent, DiagnosticCase/Hypothesis/Evidence y ProvenanceRecord.
"""

import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from diagnostic_agent.reasoning.grounding import (
    DEFAULT_MIN_RETRIEVAL_SCORE,
    DEFAULT_SUFFICIENCY_RATIO,
    DEFAULT_SUPPORT_THRESHOLD,
    Claim,
    EvidenceRef,
    assess_support,
    decide_sufficiency,
    decompose_explanation,
    supports,
)
from diagnostic_agent.reasoning.llm.generator import PROMPT_VERSION, Hypothesizer
from diagnostic_agent.reasoning.memory.episodic import EpisodicMemory, SemanticMemory
from diagnostic_agent.reasoning.rag.retriever import LexicalRetriever
from diagnostic_agent.reasoning.verify_rules import verify_hypothesis
from diagnostic_agent.storage.schema import (
    AgentRunRow,
    AgentStepRow,
    CaseRow,
    EvidenceRow,
    HypothesisRow,
    ProvenanceRow,
    RetrievalRow,
)
from diagnostic_agent.storage.store import EdgeStoreV2
from mecanico_contracts import (
    AgentNode,
    AgentRun,
    AgentStep,
    CaseMemory,
    CaseStatus,
    ClaimKind,
    DetectedAnomaly,
    DiagnosticCase,
    DiagnosticEvidence,
    DiagnosticHypothesis,
    EpistemicLevel,
    EvidenceKind,
    EvidenceRole,
    ExplanationDecision,
    HypothesisStatus,
    LearnedPattern,
    MemoryMode,
    PatternStatus,
    ProvenanceRecord,
    RetrievalEvent,
    Severity,
)

GRAPH_VERSION = "g1"


@dataclass
class AgentConfig:
    """Configuración de una ejecución.

    Las tres banderas de abajo definen los brazos del experimento central (ADR-0036,
    `docs/alineacion_v4/03_diseno_experimental.md` §1.2):

    ===========  ==================  ================  ==================================
    Brazo        ``use_retrieval``   ``verify_support``  ``abstention_enabled``
    ===========  ==================  ================  ==================================
    **B1**       False               False             False
    **B2**       True                False             False
    **B3**       True                True              True
    ===========  ==================  ================  ==================================

    ``memory_enabled`` queda **fuera del alcance experimental** de la PI v4 y por defecto
    sigue activo para no romper el comportamiento existente; los experimentos lo apagan.
    """

    memory_mode: MemoryMode = MemoryMode.EPISODIC
    epistemic_level: EpistemicLevel = EpistemicLevel.SIMULATED
    max_hypotheses: int = 3
    use_retrieval: bool = True
    verify_support: bool = True
    abstention_enabled: bool = True
    memory_enabled: bool = True
    support_threshold: float = DEFAULT_SUPPORT_THRESHOLD
    sufficiency_ratio: float = DEFAULT_SUFFICIENCY_RATIO
    min_retrieval_score: float = DEFAULT_MIN_RETRIEVAL_SCORE
    extra: dict[str, Any] = field(default_factory=dict)


class AgentState(TypedDict, total=False):
    """Working memory del grafo (efímera; su traza persiste como AgentStep)."""

    anomaly: dict[str, Any]
    query: str
    pids: list[str]
    features: dict[str, float]
    dtcs: list[str]
    recalled_cases: list[dict[str, Any]]
    recalled_patterns: list[dict[str, Any]]
    retrieved: list[tuple[str, str, dict[str, str]]]
    hypotheses: list[dict[str, Any]]
    evidences: list[dict[str, Any]]
    explanation: str
    severity: str
    memorized_case_id: str
    candidate_pattern_id: str
    retrieval_scores: list[float]
    decision: str
    supported_ratio: float
    unsupported_claims: int
    citation_correctness: float
    citation_completeness: float
    trace_depth: float
    missing_evidence: list[str]


class DiagnosticAgentV1:
    """Orquesta el grafo y persiste toda la traza."""

    def __init__(
        self,
        store: EdgeStoreV2,
        retriever: LexicalRetriever,
        hypothesizer: Hypothesizer,
        config: AgentConfig | None = None,
    ) -> None:
        self.store = store
        self.retriever = retriever
        self.hypothesizer = hypothesizer
        self.config = config or AgentConfig()
        self.episodic = EpisodicMemory(store)
        self.semantic = SemanticMemory(store)
        self._steps: list[AgentStep] = []
        self._retrievals: list[RetrievalEvent] = []
        self._run_id = ""
        self._case: DiagnosticCase | None = None
        self._llm_metrics: dict[str, Any] = {}

    # ------------------------------------------------------------------ nodos
    def _record(
        self,
        node: AgentNode,
        t0: float,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        **kw: Any,
    ) -> None:
        self._steps.append(
            AgentStep(
                step_id=str(uuid.uuid4()),
                run_id=self._run_id,
                node=node,
                seq=len(self._steps),
                started_at=datetime.fromtimestamp(t0, tz=UTC),
                ended_at=datetime.now(tz=UTC),
                inputs=inputs,
                outputs=outputs,
                **kw,
            )
        )

    def _triage(self, state: AgentState) -> AgentState:
        t0 = time.time()
        anomaly = state["anomaly"]
        features: dict[str, float] = anomaly["features"]
        pids: list[str] = anomaly["involved_pids"]
        notable = {k: round(v, 2) for k, v in features.items() if abs(v) > 1e-9}
        query = (
            f"anomalía en {', '.join(pids)}; "
            f"trims={features.get('total_trim_mean', 0):+.1f}% "
            f"coolant={features.get('COOLANT_TEMP_mean', 0):.0f}C "
            f"rpm_std={features.get('RPM_std', 0):.0f} o2_std={features.get('O2_B1S1_std', 0):.2f} "
            f"presion admision={features.get('INTAKE_PRESSURE_mean', 0):.0f} kPa "
            f"correlacion rpm maf={features.get('corr_RPM_MAF', 0):.2f}"
        )
        out: AgentState = {
            "query": query,
            "pids": pids,
            "features": features,
            "dtcs": state.get("dtcs", []),
        }
        self._record(
            AgentNode.TRIAGE,
            t0,
            {"anomaly_id": anomaly["anomaly_id"], "detector": anomaly["detector"]},
            {"query": query, "n_notable_features": len(notable)},
        )
        return out

    def _recall(self, state: AgentState) -> AgentState:
        t0 = time.time()
        mode = self.config.memory_mode
        cases: list[dict[str, Any]] = []
        patterns: list[dict[str, Any]] = []
        if mode in (MemoryMode.EPISODIC, MemoryMode.EPISODIC_SEMANTIC):
            found = self.episodic.similar_cases(state["features"])
            cases = [
                {
                    "case_memory_id": c.case_memory_id,
                    "diagnosis": c.diagnosis,
                    "epistemic_level": c.epistemic_level.value,
                    "score": s,
                }
                for c, s in found
            ]
            self._retrievals.append(
                RetrievalEvent(
                    retrieval_id=str(uuid.uuid4()),
                    run_id=self._run_id,
                    step_id=f"seq-{len(self._steps)}",
                    source="episodic_memory",
                    query="similitud de firma sintomática",
                    retrieved_ids=[c["case_memory_id"] for c in cases],
                    scores=[c["score"] for c in cases],
                    created_at=datetime.now(tz=UTC),
                )
            )
        if mode is MemoryMode.EPISODIC_SEMANTIC:
            pfound = self.semantic.similar_patterns(state["features"])
            patterns = [
                {"pattern_id": p.pattern_id, "title": p.title, "status": p.status.value, "score": s}
                for p, s in pfound
            ]
            self._retrievals.append(
                RetrievalEvent(
                    retrieval_id=str(uuid.uuid4()),
                    run_id=self._run_id,
                    step_id=f"seq-{len(self._steps)}",
                    source="semantic_memory",
                    query="similitud de firma de telemetría",
                    retrieved_ids=[p["pattern_id"] for p in patterns],
                    scores=[p["score"] for p in patterns],
                    created_at=datetime.now(tz=UTC),
                )
            )
        self._record(
            AgentNode.RECALL,
            t0,
            {"memory_mode": mode.value},
            {"n_cases": len(cases), "n_patterns": len(patterns)},
        )
        return {"recalled_cases": cases, "recalled_patterns": patterns}

    def _retrieve(self, state: AgentState) -> AgentState:
        t0 = time.time()
        if not self.config.use_retrieval:
            # Brazo B1: el generador trabaja sin evidencia recuperada. No es un fallo de
            # recuperación, es la condición experimental — y así se registra en la traza.
            self._record(
                AgentNode.RETRIEVE,
                t0,
                {"query": state["query"], "use_retrieval": False},
                {"chunk_ids": []},
            )
            return {"retrieved": [], "retrieval_scores": []}
        hits = self.retriever.search(state["query"], k=3)
        chunks = [(cid, self.retriever.chunk_text(cid), meta) for cid, _s, meta in hits]
        self._retrievals.append(
            RetrievalEvent(
                retrieval_id=str(uuid.uuid4()),
                run_id=self._run_id,
                step_id=f"seq-{len(self._steps)}",
                source="rag",
                query=state["query"],
                retrieved_ids=[cid for cid, _, _ in chunks],
                scores=[s for _, s, _ in hits],
                created_at=datetime.now(tz=UTC),
            )
        )
        self._record(
            AgentNode.RETRIEVE,
            t0,
            {"query": state["query"]},
            {"chunk_ids": [cid for cid, _, _ in chunks]},
            tools_used=["lexical_retriever"],
        )
        return {"retrieved": chunks, "retrieval_scores": [s for _, s, _ in hits]}

    def _hypothesize(self, state: AgentState) -> AgentState:
        t0 = time.time()
        assert self._case is not None
        hyps, metrics = self.hypothesizer.generate(
            state["pids"],
            state["features"],
            state.get("dtcs", []),
            state["retrieved"],
            self.config.max_hypotheses,
        )
        self._llm_metrics = metrics
        hyps = [h.model_copy(update={"case_id": self._case.case_id}) for h in hyps]
        self._record(
            AgentNode.HYPOTHESIZE,
            t0,
            {"n_context_chunks": len(state["retrieved"]), "generator": self.hypothesizer.name},
            {"failure_modes": [h.failure_mode for h in hyps]},
            tools_used=[self.hypothesizer.name],
        )
        return {"hypotheses": [h.model_dump(mode="json") for h in hyps]}

    def _verify(self, state: AgentState) -> AgentState:
        t0 = time.time()
        assert self._case is not None
        verified: list[dict[str, Any]] = []
        evidences: list[dict[str, Any]] = []
        for h_raw in state["hypotheses"]:
            hyp = DiagnosticHypothesis.model_validate(h_raw)
            status, evs, adjusted = verify_hypothesis(hyp, state["features"], self._case.case_id)
            verified.append(
                hyp.model_copy(
                    update={
                        "status": status.value,
                        "confidence": adjusted,
                        "verified_against_telemetry": bool(evs),
                    }
                ).model_dump(mode="json")
            )
            evidences.extend(e.model_dump(mode="json") for e in evs)
        order = {"supported": 0, "inconclusive": 1, "proposed": 2, "contradicted": 3}
        verified.sort(key=lambda h: (order.get(h["status"], 9), -h["confidence"]))
        for rank, h in enumerate(verified, start=1):
            h["rank"] = rank
        self._record(
            AgentNode.VERIFY,
            t0,
            {"n_hypotheses": len(verified)},
            {"statuses": [h["status"] for h in verified], "n_evidences": len(evidences)},
        )
        return {"hypotheses": verified, "evidences": evidences}

    def _decide(self, state: AgentState) -> AgentState:
        """Descompone la explicación en afirmaciones, verifica su soporte y decide.

        Es el nodo que responde a la pregunta de investigación: aquí se establece la
        correspondencia afirmación→evidencia→dato y aquí se decide si el sistema tiene
        derecho a explicar. Todo determinista; ningún modelo de lenguaje interviene.
        """
        t0 = time.time()
        assert self._case is not None
        top = state["hypotheses"][0] if state["hypotheses"] else None
        documents = {cid: text for cid, text, _ in state.get("retrieved", [])}
        scores = state.get("retrieval_scores", [])

        if top is None:
            verdict = decide_sufficiency(
                assess_support([], documents={}, features={}),
                retrieved_scores=scores,
                enabled=self.config.abstention_enabled,
            )
            self._record(
                AgentNode.DECIDE, t0, {"n_hypotheses": 0}, {"decision": verdict.decision.value}
            )
            return {
                "decision": verdict.decision.value,
                "supported_ratio": 0.0,
                "unsupported_claims": 0,
                "citation_correctness": 0.0,
                "citation_completeness": 0.0,
                "trace_depth": 0.0,
                "missing_evidence": list(verdict.missing),
            }

        telemetry_statements = [
            (str(e["statement"]), e.get("reference_id"))
            for e in state.get("evidences", [])
            if e["hypothesis_id"] == top["hypothesis_id"] and e["role"] == EvidenceRole.SUPPORTS
        ]
        claims = decompose_explanation(
            cause=str(top["cause"]),
            mechanism=str(top["mechanism"]),
            telemetry_statements=telemetry_statements,
        )
        self._attach_refs(claims, documents)

        assessment = assess_support(
            claims,
            documents=documents,
            features=state.get("features", {}),
            threshold=self.config.support_threshold,
        )
        # Sin verificación del soporte (brazo B2) las afirmaciones se dan por buenas: es
        # exactamente la diferencia que H-GRD mide.
        if not self.config.verify_support:
            for claim in assessment.claims:
                claim.supported = True

        statuses = [h["status"] for h in state["hypotheses"]]
        verdict = decide_sufficiency(
            assessment,
            retrieved_scores=scores,
            contradicted=top["status"] == HypothesisStatus.CONTRADICTED.value,
            telemetry_supported=top["status"] == HypothesisStatus.SUPPORTED.value,
            ambiguous=statuses.count(HypothesisStatus.SUPPORTED.value) > 1,
            ratio_threshold=self.config.sufficiency_ratio,
            min_retrieval_score=self.config.min_retrieval_score,
            enabled=self.config.abstention_enabled,
        )
        self._persist_claim_evidence(assessment.claims, top["hypothesis_id"], state)
        out: AgentState = {
            "decision": verdict.decision.value,
            "supported_ratio": round(assessment.supported_ratio, 4),
            "unsupported_claims": assessment.unsupported_count,
            "citation_correctness": round(assessment.citation_correctness, 4),
            "citation_completeness": round(assessment.citation_completeness, 4),
            "trace_depth": round(assessment.trace_depth, 4),
            "missing_evidence": list(verdict.missing),
        }
        self._record(
            AgentNode.DECIDE,
            t0,
            {"n_claims": len(assessment.claims), "n_chunks": len(documents)},
            {k: v for k, v in out.items() if k != "missing_evidence"},
        )
        return out

    def _attach_refs(self, claims: list[Claim], documents: dict[str, str]) -> None:
        """Asigna a cada afirmación documental la referencia de evidencia que le corresponde.

        La referencia se elige **por contenido** —el fragmento recuperado con mayor solape
        léxico con la afirmación— y no por posición en la lista recuperada. Esa distinción
        es la que hace que el control de atribución trivial del experimento (que cita
        siempre el primer resultado) sea una comparación real y no una tautología.

        Las afirmaciones telemétricas ya llegan ancladas a su feature desde el verificador
        (``reference_id``), de modo que la traza alcanza el dato y no se detiene en el
        documento.
        """
        for claim in claims:
            if claim.kind is not ClaimKind.DOCUMENTARY:
                continue
            best: tuple[float, str] | None = None
            for chunk_id, text in documents.items():
                _, overlap = supports(claim.text, text, self.config.support_threshold)
                if best is None or overlap > best[0]:
                    best = (overlap, chunk_id)
            if best is not None and best[0] > 0.0:
                claim.refs.append(
                    EvidenceRef(
                        ref_id=best[1],
                        kind=ClaimKind.DOCUMENTARY,
                        source_id=self.retriever.document_id(best[1]),
                        score=best[0],
                    )
                )

    def _persist_claim_evidence(
        self, claims: list[Claim], hypothesis_id: str, state: AgentState
    ) -> None:
        """Persiste la evidencia documental por afirmación (trazabilidad auditable)."""
        assert self._case is not None
        now = datetime.now(tz=UTC)
        rows = state.setdefault("evidences", [])
        for claim in claims:
            if claim.kind is not ClaimKind.DOCUMENTARY:
                continue
            ref = claim.refs[0] if claim.refs else None
            rows.append(
                DiagnosticEvidence(
                    evidence_id=str(uuid.uuid4()),
                    case_id=self._case.case_id,
                    hypothesis_id=hypothesis_id,
                    kind=EvidenceKind.DOCUMENT,
                    role=EvidenceRole.SUPPORTS if claim.supported else EvidenceRole.NEUTRAL,
                    reference_id=ref.ref_id if ref else None,
                    statement=f"[claim] {claim.text[:240]}"
                    + ("" if claim.supported else f" — NO SUSTENTADA: {claim.reason}"),
                    strength=round(ref.score, 3) if ref else 0.0,
                    produced_by="decide",
                    created_at=now,
                ).model_dump(mode="json")
            )

    def _report(self, state: AgentState) -> AgentState:
        t0 = time.time()
        top = state["hypotheses"][0] if state["hypotheses"] else None
        decision = state.get("decision", ExplanationDecision.SUPPORTED.value)
        if decision == ExplanationDecision.INSUFFICIENT_EVIDENCE.value:
            # Abstención declarada: salida CORRECTA del sistema, no un fallo. Se dice qué
            # falta, para que el usuario sepa qué haría falta para poder responder.
            severity = Severity.INFO
            faltan = state.get("missing_evidence", [])
            detalle = (
                " Evidencia que faltó: " + "; ".join(faltan[:3]) + "."
                if faltan
                else " No se recuperó evidencia que sostenga ninguna explicación."
            )
            explanation = (
                "EVIDENCIA INSUFICIENTE: no puede sostenerse una explicación diagnóstica "
                "con la evidencia disponible." + detalle + " No se emite un diagnóstico "
                "explicado; se recomienda ampliar la documentación o recoger más "
                "telemetría. Aviso: prototipo de investigación, no sustituye el "
                "diagnóstico profesional."
            )
        elif top is None:
            explanation, severity = "Sin hipótesis generadas.", Severity.INFO
        elif decision == ExplanationDecision.INCONCLUSIVE.value:
            severity = Severity.LOW
            explanation = (
                "NO CONCLUYENTE: varias explicaciones alcanzan un soporte comparable y la "
                "evidencia recuperada no permite diferenciarlas. Candidatas: "
                + "; ".join(f"{h['cause']} ({h['status']})" for h in state["hypotheses"][:3])
                + ". Aviso: prototipo de investigación, no sustituye el diagnóstico "
                "profesional."
            )
        elif top["status"] == HypothesisStatus.SUPPORTED.value:
            support = [
                e["statement"]
                for e in state["evidences"]
                if e["hypothesis_id"] == top["hypothesis_id"] and e["role"] == "supports"
            ]
            severity = Severity.HIGH if top["failure_mode"] == "misfire" else Severity.MEDIUM
            explanation = (
                f"Diagnóstico más probable: {top['cause']} (componente: "
                f"{top['suspected_component']}; confianza {top['confidence']:.2f}). "
                f"Mecanismo: {top['mechanism']} Evidencia verificada sobre telemetría: "
                + "; ".join(support[:3])
                + ". Aviso: prototipo de investigación, no sustituye el diagnóstico profesional."
            )
        else:
            severity = Severity.LOW
            explanation = (
                "Anomalía confirmada por el detector matemático pero sin correspondencia "
                "verificada con los modos de fallo documentados (mejor hipótesis: "
                f"{top['cause']}, estado {top['status']}). El episodio queda registrado como "
                "patrón candidato para consolidación futura; se recomienda monitorización "
                f"dirigida de {', '.join(state['pids'][:3])}."
            )
        self._record(
            AgentNode.REPORT,
            t0,
            {"top_status": top["status"] if top else None, "decision": decision},
            {"severity": severity.value, "explanation_chars": len(explanation)},
        )
        return {"explanation": explanation, "severity": severity.value}

    def _memorize(self, state: AgentState) -> AgentState:
        """Persiste el episodio en la memoria de casos.

        **Fuera del alcance experimental de la PI v4** (ADR-0036,
        `docs/alineacion_v4/05_fuera_de_alcance.md` §1): la memoria no participa en la
        evaluación y los experimentos ejecutan con ``memory_enabled=False``. El nodo se
        conserva funcional y cubierto por tests para no romper el trabajo previo ni la
        continuación futura.
        """
        t0 = time.time()
        assert self._case is not None
        if not self.config.memory_enabled:
            self._record(AgentNode.MEMORIZE, t0, {"memory_enabled": False}, {"skipped": True})
            return {}
        now = datetime.now(tz=UTC)
        top = state["hypotheses"][0] if state["hypotheses"] else None
        diagnosis = top["cause"] if top else "sin diagnóstico"
        signature = {k: v for k, v in state["features"].items() if abs(v) > 1e-9}
        case_memory = CaseMemory(
            case_memory_id=str(uuid.uuid4()),
            case_id=self._case.case_id,
            vehicle_id=self._case.vehicle_id,
            symptom_text=state["query"],
            symptom_signature=signature,
            related_dtcs=state.get("dtcs", []),
            anomaly_detector=state["anomaly"]["detector"],
            diagnosis=diagnosis,
            epistemic_level=self.config.epistemic_level,
            created_at=now,
            updated_at=now,
        )
        self.episodic.remember(case_memory)
        out: AgentState = {"memorized_case_id": case_memory.case_memory_id}

        # Registro de patrón CANDIDATE si el episodio no casó con nada documentado.
        # Única transición permitida (ADR-0013): la promoción posterior NO es automática.
        if top and top["status"] in ("inconclusive", "contradicted"):
            pattern = LearnedPattern(
                pattern_id=str(uuid.uuid4()),
                version=1,
                title=f"Patrón candidato: anomalía en {', '.join(state['pids'][:3])}",
                description=(
                    "Firma multivariable detectada sin correspondencia verificada con los "
                    "modos de fallo documentados (origen: caso "
                    f"{self._case.case_id})."
                ),
                telemetry_signature=signature,
                affected_metrics=state["pids"],
                suspected_failure_modes=[h["failure_mode"] for h in state["hypotheses"]],
                supporting_cases=[case_memory.case_memory_id],
                n_independent_sessions=1,
                n_distinct_vehicles=1,
                confidence=0.2,
                novelty_score=0.8,
                validation_level=self.config.epistemic_level,
                status=PatternStatus.CANDIDATE,
                first_seen=now,
                last_seen=now,
            )
            self.semantic.register_candidate(pattern)
            out["candidate_pattern_id"] = pattern.pattern_id
        self._record(
            AgentNode.MEMORIZE,
            t0,
            {"epistemic_level": self.config.epistemic_level.value},
            {
                "case_memory_id": case_memory.case_memory_id,
                "candidate_pattern": out.get("candidate_pattern_id"),
            },
        )
        return out

    # -------------------------------------------------------------------- run
    def _build_graph(self) -> Any:
        g: StateGraph[Any] = StateGraph(AgentState)
        g.add_node("triage", self._triage)
        g.add_node("recall", self._recall)
        g.add_node("retrieve", self._retrieve)
        g.add_node("hypothesize", self._hypothesize)
        g.add_node("verify", self._verify)
        g.add_node("decide", self._decide)
        g.add_node("report", self._report)
        g.add_node("memorize", self._memorize)
        g.set_entry_point("triage")
        for a, b in [
            ("triage", "recall"),
            ("recall", "retrieve"),
            ("retrieve", "hypothesize"),
            ("hypothesize", "verify"),
            ("verify", "decide"),
            ("decide", "report"),
            ("report", "memorize"),
        ]:
            g.add_edge(a, b)
        g.add_edge("memorize", END)
        return g.compile()

    def run(self, anomaly: DetectedAnomaly, dtcs: list[str] | None = None) -> DiagnosticCase:
        """Ejecuta el grafo sobre una anomalía y persiste caso + traza completa."""
        started = datetime.now(tz=UTC)
        t0 = time.perf_counter()
        self._run_id = str(uuid.uuid4())
        self._steps, self._retrievals, self._llm_metrics = [], [], {}
        case = DiagnosticCase(
            case_id=str(uuid.uuid4()),
            vehicle_id=anomaly.vehicle_id,
            session_id=None,
            opened_at=started,
            trigger_anomaly_ids=[anomaly.anomaly_id],
        )
        self._case = case

        graph = self._build_graph()
        final: AgentState = graph.invoke(
            {"anomaly": anomaly.model_dump(mode="json"), "dtcs": dtcs or []}
        )

        # --- persistencia estructurada
        ended = datetime.now(tz=UTC)
        provenance = ProvenanceRecord(
            provenance_id=str(uuid.uuid4()),
            subject_kind="diagnostic_case",
            subject_id=case.case_id,
            vehicle_id=case.vehicle_id,
            window_ids=[anomaly.window_id] if anomaly.window_id else [],
            anomaly_ids=[anomaly.anomaly_id],
            model_refs=[f"{anomaly.model_name}@{anomaly.model_version}"]
            if anomaly.model_name
            else [],
            document_chunk_ids=[cid for cid, _, _ in final.get("retrieved", [])],
            case_memory_ids=[c["case_memory_id"] for c in final.get("recalled_cases", [])],
            agent_run_id=self._run_id,
            prompt_version=PROMPT_VERSION,
            created_at=ended,
        )
        closed_case = case.model_copy(
            update={
                "status": CaseStatus.CLOSED,
                "closed_at": ended,
                "severity": Severity(final.get("severity", "info")),
                "explanation": final.get("explanation"),
                "decision": ExplanationDecision(
                    final.get("decision", ExplanationDecision.SUPPORTED.value)
                ),
                "supported_claim_ratio": final.get("supported_ratio"),
                "provenance_id": provenance.provenance_id,
            }
        )
        run = AgentRun(
            run_id=self._run_id,
            case_id=case.case_id,
            graph_version=GRAPH_VERSION,
            llm_model=self.hypothesizer.name,
            prompt_version=PROMPT_VERSION,
            memory_mode=self.config.memory_mode,
            started_at=started,
            ended_at=ended,
            latency_ms=round((time.perf_counter() - t0) * 1000, 1),
            tokens_in=self._llm_metrics.get("tokens_in"),
            tokens_out=self._llm_metrics.get("tokens_out"),
            result_status=(
                "abstained"
                if final.get("decision") == ExplanationDecision.INSUFFICIENT_EVIDENCE.value
                else ("ok" if final.get("hypotheses") else "no_hypothesis")
            ),
        )
        self.store.add(CaseRow, closed_case)
        self.store.add(AgentRunRow, run)
        self.store.add_all(AgentStepRow, list(self._steps))
        self.store.add_all(RetrievalRow, list(self._retrievals))
        self.store.add_all(
            HypothesisRow,
            [DiagnosticHypothesis.model_validate(h) for h in final.get("hypotheses", [])],
        )
        self.store.add_all(
            EvidenceRow,
            [DiagnosticEvidence.model_validate(e) for e in final.get("evidences", [])],
        )
        self.store.add(ProvenanceRow, provenance)
        return closed_case
