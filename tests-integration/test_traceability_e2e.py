"""Validación del esquema v2: los 16 pasos del plan + trazabilidad inversa completa.

Capa de INTEGRACIÓN del monorepo (único lugar donde se permite importar varios
proyectos a la vez; los proyectos entre sí siguen sin conocerse — ADR-0006).

Flujo: sesión → raw → normalización → ventanas → features → LOF → inferencia →
anomalía → caso (agente v1 completo) → hipótesis/evidencias → AgentRun → CaseMemory →
LearnedPattern candidato → provenance → navegación LearnedPattern → raw OBDObservation.
"""

import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from ai_models.anomaly.baselines import make_baselines
from ai_models.data.dataset import build_dataset
from ai_models.evaluation.protocol import threshold_from_normal
from ai_models.export.onnx_export import export_sklearn_package
from diagnostic_agent.detection.detector import OnnxDetector, make_anomaly
from diagnostic_agent.reasoning.graph.agent_v1 import AgentConfig, DiagnosticAgentV1
from diagnostic_agent.reasoning.llm.generator import HeuristicHypothesizer
from diagnostic_agent.reasoning.rag.retriever import LexicalRetriever, ingest_corpus
from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.store import EdgeStoreV2
from mecanico_contracts import (
    DetectorKind,
    FeatureVector,
    MemoryMode,
    ModelInference,
    OBDReading,
    ScenarioSpec,
    SessionSource,
    TelemetryPoint,
    TelemetrySession,
    TelemetryWindow,
    TransportKind,
)
from mecanico_contracts.features import FEATURE_NAMES, extract_features
from obd_lab.generate import generate_ticks

EPOCH = datetime(2026, 8, 1, tzinfo=UTC)
CORPUS = Path(__file__).parents[1] / "diagnostic-agent" / "knowledge" / "corpus_v1.yaml"
WINDOW, STRIDE = 60, 30


@pytest.fixture(scope="module")
def model_package(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """LOF entrenado sobre la suite v1 y exportado como paquete (pasos previos)."""
    sessions = tmp_path_factory.mktemp("sessions")
    from obd_lab.generate import write_session

    for seed in (101, 102, 103):
        for profile in ("urban", "highway"):
            write_session(
                ScenarioSpec(
                    scenario_id=f"tr-{profile}",
                    description="train",
                    driving_profile=profile,
                    duration_s=900,
                    seed=seed,
                ),
                sessions / "train",
            )
    train = build_dataset(sessions / "train", size=WINDOW, stride=STRIDE)
    lof = next(d for d in make_baselines(42) if d.name == "lof")
    lof.fit(train.x)
    thr = threshold_from_normal(lof.scores(train.x), 0.01)
    return export_sklearn_package(
        lof.pipeline,
        DetectorKind.LOF,
        "lof",
        "0.9.9",
        thr,
        {"itest": 1.0},
        42,
        tmp_path_factory.mktemp("packages"),
    )


def _capture(store: EdgeStoreV2, spec: ScenarioSpec, session_id: str) -> None:
    """Pasos 1-3: sesión + raw + normalización, persistidos con la cadena completa."""
    store.add(
        dbs.SessionRow,
        TelemetrySession(
            session_id=session_id,
            source=SessionSource.SYNTHETIC_GENERATOR,
            vehicle_id="veh-itest",
            device_id="dev-itest",
            started_at=EPOCH,
            sample_rate_hz=1.0,
            scenario_id=spec.scenario_id,
            generator_version="0.1.0",
            random_seed=spec.seed,
            software_version="itest",
        ),
    )
    for i, tick in enumerate(generate_ticks(spec)):
        ts = EPOCH + timedelta(seconds=i)
        store.add_all(
            dbs.ObservationRow,
            [
                OBDReading(
                    timestamp=ts,
                    pid=pid,
                    value=v,
                    unit="canon",
                    vehicle_id="veh-itest",
                    device_id="dev-itest",
                    source=TransportKind.TCP,
                )
                for pid, v in tick.items()
            ],
            session_id=session_id,
        )
        store.add(
            dbs.PointRow,
            TelemetryPoint(session_id=session_id, seq=i, timestamp=ts, values=tick),
        )


def _detect(store: EdgeStoreV2, session_id: str, package: Path) -> list[str]:
    """Pasos 4-8: ventanas → features → LOF → inferencia → anomalías (persistido todo)."""
    detector = OnnxDetector(package)
    points = sorted(store.raw_rows(dbs.PointRow, session_id=session_id), key=lambda p: p.seq)
    anomaly_ids: list[str] = []
    for start in range(0, len(points) - WINDOW + 1, STRIDE):
        chunk = points[start : start + WINDOW]
        series = {pid: [p.values[pid] for p in chunk] for pid in chunk[0].values}
        window_id = str(uuid.uuid4())
        store.add(
            dbs.WindowRow,
            TelemetryWindow(
                window_id=window_id,
                session_id=session_id,
                seq_start=chunk[0].seq,
                seq_end=chunk[-1].seq,
                start=chunk[0].timestamp,
                end=chunk[-1].timestamp,
                size=WINDOW,
                stride=STRIDE,
            ),
        )
        feats = extract_features(series)
        fv_id = str(uuid.uuid4())
        store.add(
            dbs.FeatureVectorRow,
            FeatureVector(
                fv_id=fv_id,
                window_id=window_id,
                session_id=session_id,
                feature_set_version="fs1",
                values=feats,
            ),
        )
        vec = [feats[n] for n in FEATURE_NAMES]
        score, contrib = detector.score(vec)
        flagged = score > detector.manifest.decision_threshold
        inference_id = str(uuid.uuid4())
        store.add(
            dbs.InferenceRow,
            ModelInference(
                inference_id=inference_id,
                fv_id=fv_id,
                window_id=window_id,
                session_id=session_id,
                model_id=detector.manifest.model_id,
                model_name=detector.manifest.name,
                model_version=detector.manifest.version,
                score=score,
                threshold=detector.manifest.decision_threshold,
                flagged=flagged,
                executed_at=EPOCH,
            ),
        )
        if flagged and start >= 2 * STRIDE:  # gating de calentamiento
            anomaly = make_anomaly(
                detector.kind,
                score,
                detector.manifest.decision_threshold,
                contrib,
                vec,
                "veh-itest",
                window_id=window_id,
                model_name=detector.manifest.name,
                model_version=detector.manifest.version,
            )
            store.add(dbs.AnomalyRow, anomaly, inference_id=inference_id, session_id=session_id)
            anomaly_ids.append(anomaly.anomaly_id)
    return anomaly_ids


@pytest.fixture(scope="module")
def populated(model_package: Path, tmp_path_factory: pytest.TempPathFactory) -> EdgeStoreV2:
    """Ejecuta los pasos 1-12 con un fallo held-out (garantiza patrón candidato)."""
    store = EdgeStoreV2(tmp_path_factory.mktemp("db") / "edge.sqlite3")
    ingest_corpus(store, CORPUS)
    spec = ScenarioSpec(
        scenario_id="it-corrbreak",
        description="held-out integración",
        category="held_out",
        driving_profile="urban",
        duration_s=600,
        seed=911,
        fault="corr_break_rpm_maf",
        fault_start_s=120,
        fault_end_s=600,
    )
    session_id = "sess-itest-1"
    _capture(store, spec, session_id)
    anomaly_ids = _detect(store, session_id, model_package)
    assert anomaly_ids, "el detector debe marcar el fallo held-out en la integración"

    from mecanico_contracts import DetectedAnomaly

    anomaly = store.get(DetectedAnomaly, dbs.AnomalyRow, anomaly_id=anomaly_ids[-1])
    assert anomaly is not None
    agent = DiagnosticAgentV1(
        store,
        LexicalRetriever(store),
        HeuristicHypothesizer(),
        AgentConfig(memory_mode=MemoryMode.EPISODIC_SEMANTIC),
    )
    case = agent.run(anomaly)
    store.__dict__["_itest_case_id"] = case.case_id
    store.__dict__["_itest_session_id"] = session_id
    return store


# ------------------------------------------------------------------ pasos 1-15


def test_cadena_completa_persistida(populated: EdgeStoreV2) -> None:
    s = populated
    assert s.count(dbs.SessionRow) == 1
    assert s.count(dbs.ObservationRow) == 600 * 12  # raw
    assert s.count(dbs.PointRow) == 600  # normalized
    assert s.count(dbs.WindowRow) >= 18  # derived
    assert s.count(dbs.FeatureVectorRow) == s.count(dbs.WindowRow)
    assert s.count(dbs.InferenceRow) == s.count(dbs.WindowRow)  # toda inferencia persistida
    assert s.count(dbs.AnomalyRow) >= 1
    assert s.count(dbs.CaseRow) == 1
    assert s.count(dbs.HypothesisRow) >= 1
    assert s.count(dbs.EvidenceRow) >= 0
    assert s.count(dbs.AgentRunRow) == 1
    assert s.count(dbs.AgentStepRow) == 8  # los 8 nodos del grafo (decide añadido, ADR-0036)
    assert s.count(dbs.CaseMemoryRow) == 1
    assert s.count(dbs.LearnedPatternRow) == 1  # candidato (held-out no casó con fichas)
    assert s.count(dbs.ProvenanceRow) == 1


def test_caso_completo_recuperable(populated: EdgeStoreV2) -> None:
    from mecanico_contracts import AgentRun, DiagnosticCase, DiagnosticHypothesis

    case_id = populated.__dict__["_itest_case_id"]
    case = populated.get(DiagnosticCase, dbs.CaseRow, case_id=case_id)
    assert case is not None and case.status == "closed" and case.explanation
    hyps = populated.list_(DiagnosticHypothesis, dbs.HypothesisRow, case_id=case_id)
    assert hyps and hyps[0].rank >= 1
    run = populated.get(AgentRun, dbs.AgentRunRow, case_id=case_id)
    assert run is not None and run.graph_version == "g1" and run.latency_ms is not None


def test_patron_candidato_correcto(populated: EdgeStoreV2) -> None:
    from mecanico_contracts import LearnedPattern

    patterns = populated.list_(LearnedPattern, dbs.LearnedPatternRow)
    assert len(patterns) == 1
    p = patterns[0]
    assert p.status == "candidate"  # jamás VALIDATED automáticamente (ADR-0013)
    assert p.supporting_cases and p.novelty_score > 0.5


# ------------------------------------------ paso 16: trazabilidad inversa completa


def test_trazabilidad_learned_pattern_hasta_raw(populated: EdgeStoreV2) -> None:
    """LearnedPattern → CaseMemory → DiagnosticCase → anomalía → inferencia →
    FeatureVector → TelemetryWindow → TelemetryPoints → raw OBDObservations."""
    s = populated
    pattern = s.raw_rows(dbs.LearnedPatternRow)[0]
    case_memory_id = pattern.supporting_cases[0]
    cm = s.raw_rows(dbs.CaseMemoryRow, case_memory_id=case_memory_id)[0]
    case = s.raw_rows(dbs.CaseRow, case_id=cm.case_id)[0]
    anomaly = s.raw_rows(dbs.AnomalyRow, anomaly_id=case.trigger_anomaly_ids[0])[0]
    inference = s.raw_rows(dbs.InferenceRow, inference_id=anomaly.inference_id)[0]
    fv = s.raw_rows(dbs.FeatureVectorRow, fv_id=inference.fv_id)[0]
    window = s.raw_rows(dbs.WindowRow, window_id=fv.window_id)[0]
    points = [
        p
        for p in s.raw_rows(dbs.PointRow, session_id=window.session_id)
        if window.seq_start <= p.seq <= window.seq_end
    ]
    assert len(points) == window.size
    raw = s.raw_rows(dbs.ObservationRow, session_id=window.session_id)
    raw_in_window = [o for o in raw if points[0].timestamp <= o.timestamp <= points[-1].timestamp]
    assert len(raw_in_window) == window.size * 12  # 12 PIDs crudos por tick
    # La procedencia del caso enlaza el mismo run y la misma ventana
    prov = s.raw_rows(dbs.ProvenanceRow, subject_id=case.case_id)[0]
    assert anomaly.window_id in prov.window_ids or prov.anomaly_ids == [anomaly.anomaly_id]
    assert prov.agent_run_id is not None and prov.prompt_version == "p1"


def test_feedback_y_mantenimiento_integrables(populated: EdgeStoreV2) -> None:
    """Pasos complementarios: feedback de ground truth + intervención asociada."""
    from mecanico_contracts import (
        DiagnosticFeedback,
        FeedbackKind,
        FeedbackVerdict,
        MaintenanceEvent,
    )

    case_id = populated.__dict__["_itest_case_id"]
    populated.add(
        dbs.FeedbackRow,
        DiagnosticFeedback(
            feedback_id=str(uuid.uuid4()),
            case_id=case_id,
            kind=FeedbackKind.SIMULATOR_GROUND_TRUTH,
            verdict=FeedbackVerdict.CORRECT,
            true_cause="corr_break_rpm_maf (inyectado por obd-lab)",
            provided_by="obd-lab",
            created_at=EPOCH,
        ),
    )
    populated.add(
        dbs.MaintenanceRow,
        MaintenanceEvent(
            event_id=str(uuid.uuid4()),
            vehicle_id="veh-itest",
            performed_at=EPOCH,
            action="Sustitución del sensor MAF (simulada)",
            component="sensor MAF",
            related_case_id=case_id,
        ),
    )
    assert populated.count(dbs.FeedbackRow, case_id=case_id) == 1
    assert populated.count(dbs.MaintenanceRow, related_case_id=case_id) == 1
