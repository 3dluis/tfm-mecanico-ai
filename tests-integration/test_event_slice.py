"""Vertical slice de Event Intelligence (requisito 45 del plan F6).

Flujo validado de extremo a extremo:
  obd-lab (trip sintético + ground truth de eventos) → detector determinista (que NUNCA
  ve las etiquetas) → VehicleEvents → EventFeatureVectors → persistencia (esquema v3) →
  consulta vía Tool Registry → baseline de aceleraciones normales → comparación de una
  aceleración anómala (maf_drift) contra el baseline → DetectedAnomaly con
  anomaly_scope=EVENT trazable (event_id + baseline_id + seq del RAW).

Métricas del detector contra el ground truth: P/R/F1 por tipo con IoU temporal ≥ 0.5.
"""

import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest

from ai_models.evaluation.event_metrics import event_detection_report
from diagnostic_agent.events import (
    build_baseline,
    detect_events,
    event_feature_vector,
)
from diagnostic_agent.events.baseline import contextual_anomaly
from diagnostic_agent.events.tools import register_event_tools
from diagnostic_agent.runtime.tools import ToolExecutionError, ToolRegistry
from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.store import EdgeStoreV2
from mecanico_contracts import (
    AnomalyScope,
    CaseMemory,
    EpistemicLevel,
    ScenarioSpec,
    VehicleEvent,
)
from mecanico_contracts.events_model import ALL_EVENT_TYPES, EventFeatureVector
from obd_lab.events_gt import generate_with_events
from obd_lab.generate import generate_ticks

NOW = datetime(2026, 8, 12, tzinfo=UTC)
VEH = "veh-ev"
ACCEL_CTX = "ACCELERATION|0-40|warm|d8-30s"


def _spec(seed: int, fault: str | None = None) -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id=f"ev-{'maf' if fault else 'norm'}-{seed}",
        description="slice de eventos",
        category="known_fault" if fault else "normal",
        driving_profile="urban",
        duration_s=600,
        seed=seed,
        fault=fault,
        fault_params={"drift": 0.25} if fault else {},
        fault_start_s=0 if fault else None,
    )


def _accel_efvs(seed: int, fault: str | None = None) -> list[EventFeatureVector]:
    spec = _spec(seed, fault)
    ticks = generate_ticks(spec)
    events = detect_events(ticks, f"{spec.scenario_id}-seed{seed}", VEH)
    return [event_feature_vector(e, ticks) for e in events if e.event_type == "ACCELERATION"]


@pytest.fixture(scope="module")
def trip() -> tuple[list[dict[str, float]], list[VehicleEvent], list[VehicleEvent]]:
    """(ticks, ground_truth, detectados) de un trip urbano normal."""
    spec = _spec(7)
    ticks, gt = generate_with_events(spec, vehicle_id=VEH)
    pred = detect_events(ticks, f"{spec.scenario_id}-seed7", VEH)
    return ticks, gt, pred


def test_ground_truth_valido_y_jerarquico(trip) -> None:
    _, gt, _ = trip
    assert all(e.event_type in ALL_EVENT_TYPES for e in gt)
    trips = [e for e in gt if e.event_type == "TRIP"]
    assert len(trips) == 1 and trips[0].parent_event_id is None
    children = [e for e in gt if e.parent_event_id == trips[0].event_id]
    assert len(children) == len(gt) - 1  # todo cuelga del TRIP
    assert all(e.confidence == 1.0 for e in gt)  # ground truth por construcción
    assert all(e.detection_method == "ground_truth:phases" for e in gt)


def test_detector_es_determinista_y_no_ve_etiquetas(trip) -> None:
    ticks, _, pred = trip
    again = detect_events(ticks, "otra-sesion", VEH)
    key = [(e.event_type, e.seq_start, e.seq_end) for e in pred]
    assert key == [(e.event_type, e.seq_start, e.seq_end) for e in again]
    # El detector solo etiqueta clases honestas: fin de stream ≠ parada observada.
    stop = next(e for e in pred if e.event_type == "ENGINE_STOP")
    assert stop.event_class == "estimated" and stop.confidence <= 0.5
    assert all(e.evidence for e in pred)  # todo evento lleva evidencia verificable


def test_metricas_del_detector_contra_ground_truth(trip) -> None:
    _, gt, pred = trip
    report = event_detection_report(pred, gt, iou_threshold=0.5)
    f1 = {t: r.f1 for t, r in report.items()}
    assert f1["ENGINE_START"] == 1.0
    assert f1["TRIP"] == 1.0
    assert f1["IDLE"] >= 0.80
    assert f1["ACCELERATION"] >= 0.70
    assert f1["CONSTANT_SPEED"] >= 0.75
    assert f1["DECELERATION"] >= 0.75
    assert report["ACCELERATION"].mean_onset_error <= 2.0  # onset preciso en aceleraciones


def test_persistencia_y_tools_de_eventos(tmp_path: Path, trip) -> None:
    ticks, _, pred = trip
    store = EdgeStoreV2(tmp_path / "edge.sqlite3")
    session_id = pred[0].session_id
    store.add(
        dbs.SessionRow,
        _session_stub(session_id),
    )
    for e in pred:
        store.add(dbs.EventRow, e)
    efvs = [event_feature_vector(e, ticks) for e in pred if e.event_type == "ACCELERATION"]
    for v in efvs:
        store.add(dbs.EventFeatureRow, v)

    # Ida y vuelta por contrato (metadata↔meta y datetimes intactos).
    back = store.get(VehicleEvent, dbs.EventRow, event_id=pred[1].event_id)
    assert back is not None and back.event_type == pred[1].event_type
    assert back.seq_start == pred[1].seq_start

    registry = ToolRegistry()
    register_event_tools(registry, store)
    state = registry.execute("get_vehicle_state", "diagnostic", session_id=session_id)
    assert state["state"] == "ENGINE_STOP"  # último evento de la sesión
    accels = registry.execute(
        "query_vehicle_events", "recall", session_id=session_id, event_type="ACCELERATION"
    )
    assert len(accels) == len(efvs) and all(a["evidence"] for a in accels)
    comparables = registry.execute(
        "find_comparable_events",
        "diagnostic",
        context_signature=efvs[0].context_signature,
        exclude_event_id=efvs[0].event_id,
    )
    assert efvs[0].event_id not in {c["event_id"] for c in comparables}
    with pytest.raises(ToolExecutionError, match="sin permiso"):
        registry.execute("query_vehicle_events", "verification", session_id=session_id)


def test_anomalia_contextual_normal_vs_anomala(tmp_path: Path) -> None:
    """Comparación del requisito 45: aceleración normal vs anómala (maf_drift activo)."""
    train = [v for s in (1, 2, 3, 4, 5, 6) for v in _accel_efvs(s)]
    train_ctx = [v for v in train if v.context_signature == ACCEL_CTX]
    assert len(train_ctx) >= 20  # contexto estable entre semillas
    baseline = build_baseline(train_ctx, now=NOW)
    assert baseline.sample_count == len(train_ctx) and baseline.confidence == 1.0

    normal = [v for v in _accel_efvs(99) if v.context_signature == ACCEL_CTX]
    anomalous = [v for v in _accel_efvs(50, fault="maf_drift") if v.context_signature == ACCEL_CTX]
    assert normal and anomalous

    false_alarms = [v for v in normal if contextual_anomaly(v, baseline, now=NOW)]
    assert not false_alarms  # semilla normal held-out: cero falsas alarmas

    flagged = [(v, contextual_anomaly(v, baseline, now=NOW)) for v in anomalous]
    hits = [a for _, a in flagged if a is not None]
    assert len(hits) >= len(anomalous) - 1  # a lo sumo falla la 1ª (rampa del drift)
    anomaly = hits[-1]
    assert anomaly.anomaly_scope == AnomalyScope.EVENT
    assert anomaly.window_id is None and anomaly.event_id and anomaly.baseline_id
    # Firma esperable del maf_drift: trims compensando (docs/adr/0010).
    assert {"ltft_mean", "total_trim_mean"} & set(anomaly.involved_pids)

    # Persistencia: la anomalía EVENT convive con las WINDOW de F3 en la misma tabla.
    store = EdgeStoreV2(tmp_path / "edge.sqlite3")
    store.add(dbs.EventBaselineRow, baseline)
    store.add(dbs.AnomalyRow, anomaly)
    rows = store.raw_rows(dbs.AnomalyRow, anomaly_scope="event")
    assert len(rows) == 1 and rows[0].event_id == anomaly.event_id
    assert rows[0].baseline_id == baseline.baseline_id

    # Memoria episódica con eventos relacionados (requisito 23).
    cm = CaseMemory(
        case_memory_id=str(uuid.uuid4()),
        case_id=str(uuid.uuid4()),
        vehicle_id=VEH,
        symptom_text="trims positivos durante aceleraciones comparables",
        symptom_signature={"z:total_trim_mean": anomaly.features.get("z:total_trim_mean", 0.0)},
        related_event_ids=[anomaly.event_id or ""],
        diagnosis="deriva de MAF (candidata)",
        epistemic_level=EpistemicLevel.SYNTHETIC,
        created_at=NOW,
        updated_at=NOW,
    )
    store.add(dbs.CaseMemoryRow, cm)
    back = store.get(CaseMemory, dbs.CaseMemoryRow, case_memory_id=cm.case_memory_id)
    assert back is not None and back.related_event_ids == [anomaly.event_id]


def _session_stub(session_id: str):
    from mecanico_contracts import TelemetrySession
    from mecanico_contracts.data_enums import SessionSource

    return TelemetrySession(
        session_id=session_id,
        source=SessionSource.SYNTHETIC_GENERATOR,
        vehicle_id=VEH,
        device_id="obd-lab",
        started_at=NOW,
        sample_rate_hz=1.0,
        software_version="test",
    )
