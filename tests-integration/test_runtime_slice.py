"""Vertical slice del Edge Agent Runtime (requisito 25 del plan F5).

Flujo validado: anomalía simulada → Supervisor → recall → knowledge → diagnostic →
verification (insuficiente: ventana en marcha no discrimina la fuga de vacío) → critic
(pide medición en ralentí) → Telemetry tool (obd-lab genera la ventana de ralentí con el
fallo activo) → re-verificación → PROBABLE → report etiquetado → CaseMemory.

También: stop conditions (sin provider → INSUFFICIENT_DATA), flags A3 (sin memoria) y
bloqueo de herramientas VEHICLE_WRITE.
"""

import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest

from diagnostic_agent.reasoning.llm.generator import HeuristicHypothesizer
from diagnostic_agent.reasoning.rag.retriever import LexicalRetriever, ingest_corpus
from diagnostic_agent.runtime.config import RuntimeConfig
from diagnostic_agent.runtime.supervisor import EdgeAgentRuntime
from diagnostic_agent.runtime.tools import RiskLevel, ToolRegistry, ToolSpec
from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.store import EdgeStoreV2
from mecanico_contracts import (
    DetectedAnomaly,
    DetectorKind,
    MemoryMode,
    ScenarioSpec,
)
from mecanico_contracts.features import FEATURE_NAMES, extract_features
from obd_lab.generate import generate_ticks

CORPUS = Path(__file__).parents[1] / "diagnostic-agent" / "knowledge" / "corpus_v1.yaml"
NOW = datetime(2026, 8, 12, tzinfo=UTC)


def _driving_vacuum_anomaly() -> DetectedAnomaly:
    """Ventana REAL de obd-lab: urbano en marcha con fuga de vacío activa.

    En marcha, la firma es ambigua (map_elevado y ralentí_inestable no aplican) →
    verify debe quedar INCONCLUSIVE y el loop debe pedir una medición en ralentí.
    """
    spec = ScenarioSpec(
        scenario_id="rt-vacuum-drive",
        description="vacuum en marcha",
        category="known_fault",
        driving_profile="highway",
        duration_s=300,
        seed=4242,
        fault="vacuum_leak",
        fault_params={"severity": 0.9},
        fault_start_s=0,
    )
    ticks = generate_ticks(spec)
    window = {pid: [t[pid] for t in ticks[200:260]] for pid in ticks[0]}
    feats = extract_features(window)
    full = {n: feats.get(n, 0.0) for n in FEATURE_NAMES}
    return DetectedAnomaly(
        anomaly_id=str(uuid.uuid4()),
        window_id=str(uuid.uuid4()),
        vehicle_id="veh-rt",
        detected_at=NOW,
        detector=DetectorKind.LOF,
        model_name="lof",
        model_version="0.2.0",
        score=8.0,
        threshold=0.16,
        involved_pids=["SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1", "INTAKE_PRESSURE", "RPM"],
        features=full,
    )


def _idle_provider(request: dict) -> dict[str, list[float]]:
    """Provider de mediciones: obd-lab genera la ventana solicitada con el MISMO fallo."""
    spec = ScenarioSpec(
        scenario_id="rt-vacuum-idle",
        description="medición dirigida",
        category="known_fault",
        driving_profile=str(request.get("profile", "idle")),
        duration_s=120,
        seed=4243,
        fault="vacuum_leak",
        fault_params={"severity": 0.9},
        fault_start_s=0,
    )
    ticks = generate_ticks(spec)
    return {pid: [t[pid] for t in ticks[60:120]] for pid in ticks[0]}


@pytest.fixture()
def store(tmp_path: Path) -> EdgeStoreV2:
    s = EdgeStoreV2(tmp_path / "edge.sqlite3")
    ingest_corpus(s, CORPUS)
    return s


def _runtime(store: EdgeStoreV2, config: RuntimeConfig | None = None, provider=_idle_provider):
    return EdgeAgentRuntime(
        store,
        LexicalRetriever(store),
        HeuristicHypothesizer(),
        config or RuntimeConfig(),
        provider,
    )


def test_slice_loop_completo_con_reverificacion(store: EdgeStoreV2) -> None:
    result = _runtime(store).run(_driving_vacuum_anomaly())
    assert result.outcome == "probable"
    assert result.iterations == 2  # exigió la medición en ralentí (2ª iteración)
    assert result.tool_calls >= 3  # retrieve + measurement + features (+ memoria)
    assert result.top_hypothesis is not None
    assert result.top_hypothesis.failure_mode == "vacuum_leak"
    assert result.top_hypothesis.status == "supported"
    # Report etiquetado (observado/inferido/probable/no confirmado)
    text = result.case.explanation or ""
    for label in ("OBSERVADO", "INFERIDO", "PROBABLE", "NO CONFIRMADO"):
        assert label in text
    # Traza persistida: run + steps (incluye telemetry) + memoria episódica
    runs = store.raw_rows(dbs.AgentRunRow, case_id=result.case.case_id)
    assert runs and runs[0].graph_version == "rt1" and runs[0].result_status == "probable"
    steps = store.raw_rows(dbs.AgentStepRow, run_id=runs[0].run_id)
    assert len(steps) >= 7
    assert store.count(dbs.CaseMemoryRow, case_id=result.case.case_id) == 1
    assert store.count(dbs.ProvenanceRow, subject_id=result.case.case_id) == 1


def test_sin_provider_termina_en_insufficient_data(store: EdgeStoreV2) -> None:
    result = _runtime(store, provider=None).run(_driving_vacuum_anomaly())
    assert result.outcome in ("insufficient_data", "inconclusive")
    assert result.iterations == 1  # no pudo iterar: honestidad, no fallo


def test_arquitectura_a3_no_consulta_memoria(store: EdgeStoreV2) -> None:
    cfg = RuntimeConfig.architecture("A3")
    result = _runtime(store, cfg).run(_driving_vacuum_anomaly())
    runs = store.raw_rows(dbs.AgentRunRow, case_id=result.case.case_id)
    retrievals = store.raw_rows(dbs.RetrievalRow, run_id=runs[0].run_id)
    assert all(r.source == "rag" for r in retrievals)
    assert runs[0].memory_mode == MemoryMode.NONE.value
    assert result.iterations == 1  # A3 sin loop


def test_registry_bloquea_vehicle_write() -> None:
    reg = ToolRegistry()
    with pytest.raises(ValueError, match="VEHICLE_WRITE"):
        reg.register(
            ToolSpec(
                "clear_dtc",
                "borra códigos",
                {},
                {},
                5.0,
                ("telemetry",),
                "vehicle_write",
                False,
                RiskLevel.VEHICLE_WRITE,
                lambda: None,
            )
        )


def test_registry_respeta_permisos(store: EdgeStoreV2) -> None:
    rt = _runtime(store)
    from diagnostic_agent.runtime.tools import ToolExecutionError

    with pytest.raises(ToolExecutionError, match="sin permiso"):
        rt.registry.execute("request_measurement", "critic", request={})
