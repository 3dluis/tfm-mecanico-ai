"""Comportamiento del agente v1: fallo conocido → SUPPORTED; held-out → candidato.

También verifica la responsabilidad estricta de verify (evidencias a favor Y en contra)
y el efecto del memory_mode (recall solo consulta memoria si está habilitada).
"""

import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest

from diagnostic_agent.reasoning.graph.agent_v1 import AgentConfig, DiagnosticAgentV1
from diagnostic_agent.reasoning.llm.generator import HeuristicHypothesizer
from diagnostic_agent.reasoning.rag.retriever import LexicalRetriever, ingest_corpus
from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.store import EdgeStoreV2
from mecanico_contracts import (
    DetectedAnomaly,
    DetectorKind,
    MemoryMode,
)
from mecanico_contracts.features import FEATURE_NAMES

CORPUS = Path(__file__).parents[1] / "diagnostic-agent" / "knowledge" / "corpus_v1.yaml"
NOW = datetime(2026, 8, 12, tzinfo=UTC)


def _anomaly(features: dict[str, float], pids: list[str]) -> DetectedAnomaly:
    full = {n: features.get(n, 0.0) for n in FEATURE_NAMES}
    return DetectedAnomaly(
        anomaly_id=str(uuid.uuid4()),
        window_id=str(uuid.uuid4()),
        vehicle_id="veh-x",
        detected_at=NOW,
        detector=DetectorKind.LOF,
        model_name="lof",
        model_version="0.2.0",
        score=9.0,
        threshold=0.16,
        involved_pids=pids,
        features=full,
    )


#: Firma típica de fuga de vacío (trims+, MAP alto en ralentí, RPM inestable).
VACUUM = {
    "total_trim_mean": 9.4,
    "SHORT_FUEL_TRIM_1_mean": 5.1,
    "LONG_FUEL_TRIM_1_mean": 4.3,
    "INTAKE_PRESSURE_mean": 46.0,
    "SPEED_mean": 3.0,
    "RPM_std": 55.0,
    "RPM_mean": 840.0,
    "O2_B1S1_std": 0.24,
    "COOLANT_TEMP_mean": 88.0,
}
#: Firma held-out: todo en rango univariante, correlación rota.
HELD_OUT = {
    "corr_RPM_MAF": 0.21,
    "corr_ENGINE_LOAD_MAF": 0.18,
    "MAF_mean": 21.0,
    "RPM_mean": 2100.0,
    "RPM_std": 300.0,
    "SPEED_mean": 42.0,
    "total_trim_mean": 0.4,
    "COOLANT_TEMP_mean": 87.0,
    "O2_B1S1_std": 0.24,
    "INTAKE_PRESSURE_mean": 55.0,
}


@pytest.fixture()
def store(tmp_path: Path) -> EdgeStoreV2:
    s = EdgeStoreV2(tmp_path / "edge.sqlite3")
    ingest_corpus(s, CORPUS)
    return s


def _agent(store: EdgeStoreV2, mode: MemoryMode = MemoryMode.EPISODIC) -> DiagnosticAgentV1:
    return DiagnosticAgentV1(
        store, LexicalRetriever(store), HeuristicHypothesizer(), AgentConfig(memory_mode=mode)
    )


def test_fallo_conocido_hipotesis_soportada(store: EdgeStoreV2) -> None:
    case = _agent(store).run(_anomaly(VACUUM, ["SHORT", "LONG", "INTAKE", "RPM"]))
    hyps = store.raw_rows(dbs.HypothesisRow, case_id=case.case_id)
    top = min(hyps, key=lambda h: h.rank)
    assert top.failure_mode == "vacuum_leak"
    assert top.status == "supported"
    assert top.verified_against_telemetry
    evidences = store.raw_rows(dbs.EvidenceRow, hypothesis_id=top.hypothesis_id)
    assert any(e.role == "supports" for e in evidences)
    assert case.explanation and "fuga" in case.explanation.lower()


def test_held_out_produce_candidato_no_alucina(store: EdgeStoreV2) -> None:
    case = _agent(store, MemoryMode.EPISODIC_SEMANTIC).run(
        _anomaly(HELD_OUT, ["RPM", "MAF", "ENGINE_LOAD"])
    )
    hyps = store.raw_rows(dbs.HypothesisRow, case_id=case.case_id)
    top = min(hyps, key=lambda h: h.rank)
    assert top.status in ("inconclusive", "contradicted")  # no afirma lo que no puede verificar
    patterns = store.raw_rows(dbs.LearnedPatternRow)
    assert len(patterns) == 1 and patterns[0].status == "candidate"
    assert (
        "candidato" in (case.explanation or "").lower()
        or "no cubiert" in (case.explanation or "").lower()
    )


def test_memory_mode_none_no_consulta_memoria(store: EdgeStoreV2) -> None:
    _agent(store).run(_anomaly(VACUUM, ["RPM"]))  # siembra un caso en memoria
    agent = _agent(store, MemoryMode.NONE)
    case2 = agent.run(_anomaly(VACUUM, ["RPM"]))
    runs = store.raw_rows(dbs.AgentRunRow, case_id=case2.case_id)
    retrievals = store.raw_rows(dbs.RetrievalRow, run_id=runs[0].run_id)
    assert all(r.source == "rag" for r in retrievals)  # sin memoria episódica/semántica


def test_recall_recupera_caso_previo(store: EdgeStoreV2) -> None:
    _agent(store).run(_anomaly(VACUUM, ["RPM"]))
    agent = _agent(store, MemoryMode.EPISODIC)
    case2 = agent.run(_anomaly(VACUUM, ["RPM"]))
    runs = store.raw_rows(dbs.AgentRunRow, case_id=case2.case_id)
    episodic = [
        r
        for r in store.raw_rows(dbs.RetrievalRow, run_id=runs[0].run_id)
        if r.source == "episodic_memory"
    ]
    assert episodic and episodic[0].retrieved_ids  # el segundo caso recuerda al primero
