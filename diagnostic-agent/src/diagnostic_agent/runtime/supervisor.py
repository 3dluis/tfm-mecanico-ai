"""Edge Agent Runtime v1 (vertical slice, ADR-0015/0016/0017).

Supervisor LangGraph con política de decisión determinista, agentes como roles lógicos
(reutilizan los componentes de F3/F4: memoria, retriever, hipotetizadores, verify_rules),
Tool Registry auditado, loop con stop conditions y persistencia completa en el modelo de
datos v2 (AgentRun/AgentStep/RetrievalEvent/caso/hipótesis/evidencia/provenance).
"""

import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from diagnostic_agent.reasoning.llm.generator import PROMPT_VERSION, Hypothesizer
from diagnostic_agent.reasoning.memory.episodic import EpisodicMemory, SemanticMemory
from diagnostic_agent.reasoning.rag.retriever import LexicalRetriever
from diagnostic_agent.reasoning.verify_rules import verify_hypothesis
from diagnostic_agent.runtime.config import GRAPH_VERSION, RuntimeConfig
from diagnostic_agent.runtime.tools import RiskLevel, ToolRegistry, ToolSpec
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
    DetectedAnomaly,
    DiagnosticCase,
    DiagnosticEvidence,
    DiagnosticHypothesis,
    EvidenceRole,
    HypothesisStatus,
    LearnedPattern,
    MemoryMode,
    PatternStatus,
    ProvenanceRecord,
    RetrievalEvent,
    Severity,
)
from mecanico_contracts.features import extract_features

#: Provider de mediciones dirigidas: request → series por PID (ventana nueva).
#: En producción envuelve AcquisitionClient; en experimentos, el generador de obd-lab.
MeasurementProvider = Callable[[dict[str, Any]], dict[str, list[float]]]

_OUTCOMES = ("confirmed", "probable", "inconclusive", "insufficient_data", "escalate", "failed")


class RuntimeState(TypedDict, total=False):
    """DiagnosticState del Supervisor (working memory; docs/agent-runtime/03)."""

    case_id: str
    vehicle_id: str
    session_id: str | None
    objective: str
    telemetry_context: dict[str, Any]
    detected_anomalies: list[dict[str, Any]]
    dtcs: list[str]
    active_hypotheses: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    retrieved_documents: list[str]
    retrieved_cases: list[dict[str, Any]]
    recall_done: bool
    retrieve_done: bool
    pending_questions: list[str]
    current_plan: list[str]
    iteration: int
    llm_calls: int
    confidence: float
    status: str
    next_action: str
    outcome: str


@dataclass
class SliceResult:
    """Resultado del runtime para evaluación."""

    case: DiagnosticCase
    outcome: str
    iterations: int
    tool_calls: int
    top_hypothesis: DiagnosticHypothesis | None


class EdgeAgentRuntime:
    """Supervisor + roles. Los agentes NO se llaman entre sí: solo el Supervisor enruta."""

    def __init__(
        self,
        store: EdgeStoreV2,
        retriever: LexicalRetriever,
        hypothesizer: Hypothesizer,
        config: RuntimeConfig | None = None,
        measurement_provider: MeasurementProvider | None = None,
    ) -> None:
        self.store = store
        self.retriever = retriever
        self.hypothesizer = hypothesizer
        self.config = config or RuntimeConfig()
        self.episodic = EpisodicMemory(store)
        self.semantic = SemanticMemory(store)
        self.provider = measurement_provider
        self.registry = self._build_registry()
        self._steps: list[AgentStep] = []
        self._retrievals: list[RetrievalEvent] = []
        self._run_id = ""
        self._t_start = 0.0
        self._anomaly: DetectedAnomaly | None = None

    # ------------------------------------------------------------ tool registry
    def _build_registry(self) -> ToolRegistry:
        reg = ToolRegistry()
        reg.register(
            ToolSpec(
                "retrieve_chunks",
                "Recupera fragmentos del corpus técnico local",
                {"query": "str", "k": "int"},
                {"chunks": "list"},
                5.0,
                ("knowledge",),
                "local_write",
                True,
                RiskLevel.SAFE_LOCAL,
                lambda query, k=3: self.retriever.search(query, k),
            )
        )
        reg.register(
            ToolSpec(
                "search_case_memory",
                "Casos episódicos similares (× peso epistemológico)",
                {"signature": "dict", "k": "int"},
                {"cases": "list"},
                5.0,
                ("recall",),
                "local_write",
                True,
                RiskLevel.SAFE_LOCAL,
                lambda signature, k=3: self.episodic.similar_cases(signature, k),
            )
        )
        reg.register(
            ToolSpec(
                "search_learned_patterns",
                "Patrones consolidados similares",
                {"signature": "dict", "k": "int"},
                {"patterns": "list"},
                5.0,
                ("recall",),
                "local_write",
                True,
                RiskLevel.SAFE_LOCAL,
                lambda signature, k=2: self.semantic.similar_patterns(signature, k),
            )
        )
        reg.register(
            ToolSpec(
                "request_measurement",
                "Adquisición dirigida de una ventana nueva (p. ej. en ralentí)",
                {"request": "dict"},
                {"window": "dict[pid, list[float]]"},
                90.0,
                ("telemetry",),
                "none",
                False,
                RiskLevel.READ_ONLY,
                self._measure,
            )
        )
        reg.register(
            ToolSpec(
                "calculate_feature",
                "Features canónicas de una ventana",
                {"window": "dict"},
                {"features": "dict"},
                5.0,
                ("telemetry", "verification"),
                "none",
                True,
                RiskLevel.SAFE_LOCAL,
                extract_features,
            )
        )
        return reg

    def _measure(self, request: dict[str, Any]) -> dict[str, list[float]]:
        if self.provider is None:
            msg = "sin proveedor de mediciones (INSUFFICIENT_DATA)"
            raise RuntimeError(msg)
        return self.provider(request)

    # ------------------------------------------------------------------- pasos
    def _record(
        self, node: AgentNode, t0: float, inputs: dict[str, Any], outputs: dict[str, Any]
    ) -> None:
        tools_in_window = [r.tool for r in self.registry.history[len(self._steps) * 0 :]]
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
                tools_used=tools_in_window[-3:],
                metrics={"tool_calls_total": float(self.registry.total_calls)},
            )
        )

    # ------------------------------------------------------------------- roles
    def _supervisor(self, state: RuntimeState) -> RuntimeState:
        """Política de decisión determinista v1 (docs/agent-runtime/03)."""
        s = self.config.stop
        elapsed = time.perf_counter() - self._t_start
        budget_out = (
            state.get("iteration", 0) >= s.max_iterations
            or elapsed >= s.max_execution_time_s
            or self.registry.total_calls >= s.max_tool_calls
            or state.get("llm_calls", 0) >= s.max_llm_calls
        )
        hyps = state.get("active_hypotheses", [])
        verified = [h for h in hyps if h.get("verified")]
        top_ok = self._top_supported(state) is not None

        if budget_out:
            action = "report"
        elif not state.get("recall_done") and self.config.memory_mode is not MemoryMode.NONE:
            action = "recall"
        elif not state.get("retrieve_done"):
            action = "retrieve"
        elif not hyps:
            action = "hypothesize"
        elif not verified:
            action = "verify"
        elif self.config.enable_critic and state.get("status") != "critiqued":
            action = "critic"
        elif (
            self.config.enable_loop
            and not top_ok
            and state.get("pending_questions")
            and self.provider is not None
        ):
            action = "telemetry"
        else:
            action = "report"
        return {"next_action": action}

    def _top_supported(self, state: RuntimeState) -> dict[str, Any] | None:
        s = self.config.stop
        for h in state.get("active_hypotheses", []):
            support = [
                e
                for e in state.get("evidence", [])
                if e["hypothesis_id"] == h["hypothesis_id"] and e["role"] == "supports"
            ]
            if (
                h.get("status") == HypothesisStatus.SUPPORTED.value
                and len(support) >= s.minimum_evidence
                and h.get("confidence", 0.0) >= s.minimum_confidence
            ):
                return h
        return None

    def _recall(self, state: RuntimeState) -> RuntimeState:
        t0 = time.time()
        signature = {
            k: v for k, v in state["telemetry_context"]["features"].items() if abs(v) > 1e-9
        }
        cases = self.registry.execute("search_case_memory", "recall", signature=signature)
        out_cases = [
            {
                "case_memory_id": c.case_memory_id,
                "diagnosis": c.diagnosis,
                "epistemic_level": c.epistemic_level.value,
                "score": score,
            }
            for c, score in cases
        ]
        patterns: list[dict[str, Any]] = []
        if self.config.memory_mode is MemoryMode.EPISODIC_SEMANTIC:
            found = self.registry.execute("search_learned_patterns", "recall", signature=signature)
            patterns = [
                {"pattern_id": p.pattern_id, "title": p.title, "score": sc} for p, sc in found
            ]
        self._retrievals.append(
            RetrievalEvent(
                retrieval_id=str(uuid.uuid4()),
                run_id=self._run_id,
                step_id=f"seq-{len(self._steps)}",
                source="episodic_memory",
                query="similitud de firma",
                retrieved_ids=[c["case_memory_id"] for c in out_cases],
                scores=[c["score"] for c in out_cases],
                created_at=datetime.now(tz=UTC),
            )
        )
        self._record(
            AgentNode.RECALL,
            t0,
            {"memory_mode": self.config.memory_mode.value},
            {"n_cases": len(out_cases), "n_patterns": len(patterns)},
        )
        return {"retrieved_cases": out_cases + patterns, "recall_done": True}

    def _retrieve(self, state: RuntimeState) -> RuntimeState:
        t0 = time.time()
        hits = self.registry.execute("retrieve_chunks", "knowledge", query=state["objective"])
        chunk_ids = [cid for cid, _s, _m in hits]
        self._retrievals.append(
            RetrievalEvent(
                retrieval_id=str(uuid.uuid4()),
                run_id=self._run_id,
                step_id=f"seq-{len(self._steps)}",
                source="rag",
                query=state["objective"],
                retrieved_ids=chunk_ids,
                scores=[s for _c, s, _m in hits],
                created_at=datetime.now(tz=UTC),
            )
        )
        self._record(
            AgentNode.RETRIEVE, t0, {"query": state["objective"][:120]}, {"chunk_ids": chunk_ids}
        )
        return {"retrieved_documents": chunk_ids, "retrieve_done": True}

    def _hypothesize(self, state: RuntimeState) -> RuntimeState:
        t0 = time.time()
        features = state["telemetry_context"]["features"]
        chunks: list[tuple[str, str, dict[str, str]]] = [
            (cid, self.retriever.chunk_text(cid), {}) for cid in state["retrieved_documents"]
        ]
        # Reconstruir metadata de chunks para el generador heurístico
        chunks = [
            (
                cid,
                text,
                next(
                    (m for c2, _s, m in self.retriever.search(state["objective"], 5) if c2 == cid),
                    {},
                ),
            )
            for cid, text, _ in chunks
        ]
        hyps, _metrics = self.hypothesizer.generate(
            state["telemetry_context"]["pids"],
            features,
            state.get("dtcs", []),
            chunks,
            self.config.stop.max_hypotheses,
        )
        hyps = [h.model_copy(update={"case_id": state["case_id"]}) for h in hyps]
        self._record(
            AgentNode.HYPOTHESIZE,
            t0,
            {"generator": self.hypothesizer.name},
            {"failure_modes": [h.failure_mode for h in hyps]},
        )
        return {
            "active_hypotheses": [h.model_dump(mode="json") | {"verified": False} for h in hyps],
            "llm_calls": state.get("llm_calls", 0)
            + (0 if self.hypothesizer.name == "heuristic" else 1),
        }

    def _verify(self, state: RuntimeState) -> RuntimeState:
        t0 = time.time()
        features = state["telemetry_context"]["features"]
        new_hyps: list[dict[str, Any]] = []
        new_evidence = list(state.get("evidence", []))
        for h_raw in state["active_hypotheses"]:
            hyp = DiagnosticHypothesis.model_validate(
                {k: v for k, v in h_raw.items() if k != "verified"}
            )
            status, evs, adjusted = verify_hypothesis(hyp, features, state["case_id"])
            new_hyps.append(
                hyp.model_copy(
                    update={
                        "status": status.value,
                        "confidence": adjusted,
                        "verified_against_telemetry": bool(evs),
                    }
                ).model_dump(mode="json")
                | {"verified": True}
            )
            new_evidence.extend(e.model_dump(mode="json") for e in evs)
        order = {"supported": 0, "inconclusive": 1, "proposed": 2, "contradicted": 3}
        new_hyps.sort(key=lambda h: (order.get(h["status"], 9), -h["confidence"]))
        for rank, h in enumerate(new_hyps, start=1):
            h["rank"] = rank
        self._record(
            AgentNode.VERIFY,
            t0,
            {"n": len(new_hyps)},
            {"statuses": [h["status"] for h in new_hyps]},
        )
        return {
            "active_hypotheses": new_hyps,
            "evidence": new_evidence,
            "confidence": new_hyps[0]["confidence"] if new_hyps else 0.0,
            "status": "verified",
        }

    def _critic(self, state: RuntimeState) -> RuntimeState:
        """Crítica con criterios ESTRUCTURADOS (no opinión): docs/agent-runtime/04."""
        t0 = time.time()
        questions: list[str] = []
        top = state["active_hypotheses"][0] if state.get("active_hypotheses") else None
        checks = {
            "top_supported": bool(top and top["status"] == "supported"),
            "sin_afirmaciones_sin_evidencia": all(
                any(e["hypothesis_id"] == h["hypothesis_id"] for e in state.get("evidence", []))
                for h in state.get("active_hypotheses", [])
                if h["status"] == "supported"
            ),
            "contradicciones_tratadas": True,
        }
        if top and top["status"] != "supported":
            # criterio: ¿qué condición discriminaría entre las hipótesis activas?
            active_modes = {
                h["failure_mode"]
                for h in state.get("active_hypotheses", [])
                if h["status"] != "contradicted"
            }
            if "vacuum_leak" in active_modes:
                # ralentí discrimina fuga de vacío (trims/MAP/inestabilidad a baja carga)
                # frente a deriva de MAF (trims en todos los regímenes)
                questions.append("medir en ralentí (discrimina fuga de vacío vs deriva MAF)")
            else:
                questions.append("ampliar ventana de observación para la hipótesis top")
        contradicted = [
            e
            for e in state.get("evidence", [])
            if e["hypothesis_id"] == (top or {}).get("hypothesis_id")
            and e["role"] == EvidenceRole.CONTRADICTS.value
        ]
        self._record(
            AgentNode.TRIAGE,
            t0,
            {"checks": checks},
            {
                "needs_iteration": bool(questions),
                "questions": questions,
                "n_contradicting_top": len(contradicted),
            },
        )
        return {"pending_questions": questions, "status": "critiqued"}

    def _telemetry(self, state: RuntimeState) -> RuntimeState:
        """Adquisición dirigida (loop): responde a la primera pending_question."""
        t0 = time.time()
        question = state["pending_questions"][0]
        request = {"profile": "idle" if "ralentí" in question else "urban", "duration_s": 60}
        window = self.registry.execute("request_measurement", "telemetry", request=request)
        features = self.registry.execute("calculate_feature", "telemetry", window=window)
        ctx = dict(state["telemetry_context"])
        ctx["features"] = features
        ctx["acquired_windows"] = ctx.get("acquired_windows", 0) + 1
        self._record(
            AgentNode.RECALL,
            t0,
            {"request": request},
            {
                "acquired": True,
                "notable": {
                    k: round(v, 2) for k, v in features.items() if abs(v) > 1e-9 and "corr" not in k
                },
            },
        )
        # invalidar verificación previa: las hipótesis deben re-contrastarse con la nueva ventana
        hyps = [dict(h) | {"verified": False} for h in state.get("active_hypotheses", [])]
        return {
            "telemetry_context": ctx,
            "active_hypotheses": hyps,
            "pending_questions": state["pending_questions"][1:],
            "iteration": state.get("iteration", 0) + 1,
            "status": "reverify",
        }

    def _report(self, state: RuntimeState) -> RuntimeState:
        t0 = time.time()
        top = state["active_hypotheses"][0] if state.get("active_hypotheses") else None
        top_ok = self._top_supported(state)
        if top_ok is not None:
            outcome = "probable"
        elif top and top["status"] in ("inconclusive", "contradicted"):
            outcome = "inconclusive"
        elif (self.provider is None and state.get("pending_questions")) or top is None:
            outcome = "insufficient_data"
        else:
            outcome = "inconclusive"
        self._record(
            AgentNode.REPORT, t0, {"outcome": outcome}, {"iterations": state.get("iteration", 0)}
        )
        return {"outcome": outcome, "status": "reported"}

    def _memorize(self, state: RuntimeState) -> RuntimeState:
        t0 = time.time()
        now = datetime.now(tz=UTC)
        top = state["active_hypotheses"][0] if state.get("active_hypotheses") else None
        signature = {
            k: v for k, v in state["telemetry_context"]["features"].items() if abs(v) > 1e-9
        }
        cm = CaseMemory(
            case_memory_id=str(uuid.uuid4()),
            case_id=state["case_id"],
            vehicle_id=state["vehicle_id"],
            symptom_text=state["objective"],
            symptom_signature=signature,
            diagnosis=(top or {}).get("cause", "sin diagnóstico"),
            epistemic_level=self.config.epistemic_level,
            created_at=now,
            updated_at=now,
        )
        self.episodic.remember(cm)
        candidate_id = None
        if state["outcome"] in ("inconclusive", "insufficient_data") and top is not None:
            pattern = LearnedPattern(
                pattern_id=str(uuid.uuid4()),
                version=1,
                title=(
                    f"Patrón candidato ({state['outcome']}): "
                    f"{', '.join(state['telemetry_context']['pids'][:3])}"
                ),
                description=(
                    f"Runtime {GRAPH_VERSION}: episodio sin diagnóstico soportado "
                    f"(caso {state['case_id']})."
                ),
                telemetry_signature=signature,
                affected_metrics=state["telemetry_context"]["pids"],
                suspected_failure_modes=[h["failure_mode"] for h in state["active_hypotheses"]],
                supporting_cases=[cm.case_memory_id],
                n_independent_sessions=1,
                n_distinct_vehicles=1,
                confidence=0.2,
                novelty_score=0.7,
                validation_level=self.config.epistemic_level,
                status=PatternStatus.CANDIDATE,
                first_seen=now,
                last_seen=now,
            )
            self.semantic.register_candidate(pattern)
            candidate_id = pattern.pattern_id
        self._record(
            AgentNode.MEMORIZE,
            t0,
            {},
            {"case_memory_id": cm.case_memory_id, "candidate_pattern": candidate_id},
        )
        return {}

    # --------------------------------------------------------------------- run
    def _route(self, state: RuntimeState) -> str:
        return state["next_action"]

    def _build_graph(self) -> Any:
        g: StateGraph[Any] = StateGraph(RuntimeState)
        g.add_node("supervisor", self._supervisor)
        for name, fn in [
            ("recall", self._recall),
            ("retrieve", self._retrieve),
            ("hypothesize", self._hypothesize),
            ("verify", self._verify),
            ("critic", self._critic),
            ("telemetry", self._telemetry),
            ("report", self._report),
        ]:
            g.add_node(name, fn)
            if name != "report":
                g.add_edge(name, "supervisor")
        g.add_node("memorize", self._memorize)
        g.set_entry_point("supervisor")
        g.add_conditional_edges(
            "supervisor",
            self._route,
            {
                n: n
                for n in (
                    "recall",
                    "retrieve",
                    "hypothesize",
                    "verify",
                    "critic",
                    "telemetry",
                    "report",
                )
            },
        )
        g.add_edge("report", "memorize")
        g.add_edge("memorize", END)
        return g.compile()

    def run(self, anomaly: DetectedAnomaly, objective: str | None = None) -> SliceResult:
        """Ejecuta el runtime sobre una anomalía; persiste caso y traza completa."""
        started = datetime.now(tz=UTC)
        self._t_start = time.perf_counter()
        self._run_id = str(uuid.uuid4())
        self._steps, self._retrievals = [], []
        self._anomaly = anomaly
        case = DiagnosticCase(
            case_id=str(uuid.uuid4()),
            vehicle_id=anomaly.vehicle_id,
            session_id=anomaly.session_id,
            opened_at=started,
            trigger_anomaly_ids=[anomaly.anomaly_id],
        )
        init: RuntimeState = {
            "case_id": case.case_id,
            "vehicle_id": anomaly.vehicle_id,
            "session_id": anomaly.session_id,
            "objective": objective
            or f"investigar anomalía en {', '.join(anomaly.involved_pids)} "
            f"(trims={anomaly.features.get('total_trim_mean', 0):+.1f}%, "
            f"corr_rpm_maf={anomaly.features.get('corr_RPM_MAF', 0):.2f})",
            "telemetry_context": {
                "features": dict(anomaly.features),
                "pids": list(anomaly.involved_pids),
            },
            "detected_anomalies": [anomaly.model_dump(mode="json")],
            "iteration": 1,
            "llm_calls": 0,
            "status": "investigating",
            "current_plan": ["recall", "retrieve", "hypothesize", "verify", "critic", "report"],
        }
        final: RuntimeState = self._build_graph().invoke(init, {"recursion_limit": 60})

        ended = datetime.now(tz=UTC)
        hyps_final = final.get("active_hypotheses") or []
        top = hyps_final[0] if hyps_final else None
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
            document_chunk_ids=final.get("retrieved_documents", []),
            case_memory_ids=[
                c["case_memory_id"]
                for c in final.get("retrieved_cases", [])
                if "case_memory_id" in c
            ],
            agent_run_id=self._run_id,
            prompt_version=PROMPT_VERSION,
            created_at=ended,
        )
        severity = Severity.MEDIUM if final.get("outcome") == "probable" else Severity.LOW
        explanation = self._compose_explanation(final)
        closed = case.model_copy(
            update={
                "status": CaseStatus.CLOSED,
                "closed_at": ended,
                "severity": severity,
                "explanation": explanation,
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
            latency_ms=round((time.perf_counter() - self._t_start) * 1000, 1),
            config={
                "router": self.config.model_router,
                "flags": {"critic": self.config.enable_critic, "loop": self.config.enable_loop},
                "stop": self.config.stop.__dict__,
            },
            result_status=final.get("outcome", "failed"),
        )
        self.store.add(CaseRow, closed)
        self.store.add(AgentRunRow, run)
        self.store.add_all(AgentStepRow, list(self._steps))
        self.store.add_all(RetrievalRow, list(self._retrievals))
        self.store.add_all(
            HypothesisRow,
            [
                DiagnosticHypothesis.model_validate({k: v for k, v in h.items() if k != "verified"})
                for h in final.get("active_hypotheses", [])
            ],
        )
        self.store.add_all(
            EvidenceRow,
            [DiagnosticEvidence.model_validate(e) for e in final.get("evidence", [])],
        )
        self.store.add(ProvenanceRow, provenance)
        return SliceResult(
            case=closed,
            outcome=final.get("outcome", "failed"),
            iterations=final.get("iteration", 1),
            tool_calls=self.registry.total_calls,
            top_hypothesis=DiagnosticHypothesis.model_validate(
                {k: v for k, v in top.items() if k != "verified"}
            )
            if top
            else None,
        )

    def _compose_explanation(self, final: RuntimeState) -> str:
        """Report Agent v1 (plantilla): etiqueta observado/inferido/probable/desconocido."""
        hyps_final = final.get("active_hypotheses") or []
        top = hyps_final[0] if hyps_final else None
        anomaly = final["detected_anomalies"][0]
        observed = f"OBSERVADO: anomalía en {', '.join(anomaly['involved_pids'][:4])}."
        inferred = (
            f"INFERIDO: score {anomaly['score']:.2f} (umbral {anomaly['threshold']:.2f}) "
            f"por {anomaly['model_name'] or anomaly['detector']}."
        )
        if final.get("outcome") == "probable" and top:
            support = [
                e["statement"]
                for e in final.get("evidence", [])
                if e["hypothesis_id"] == top["hypothesis_id"] and e["role"] == "supports"
            ]
            verdict = (
                f"PROBABLE: {top['cause']} (componente {top['suspected_component']}, "
                f"confianza {top['confidence']:.2f}). Evidencia: " + "; ".join(support[:3]) + "."
            )
        else:
            verdict = (
                f"DESCONOCIDO: sin hipótesis suficientemente respaldada "
                f"(resultado {final.get('outcome')}); episodio registrado para consolidación."
            )
        return (
            f"{observed} {inferred} {verdict} NO CONFIRMADO: la confirmación requiere "
            "validación externa. Prototipo de investigación: no sustituye el diagnóstico "
            "profesional."
        )
