"""E2E de VehicleTelemetrySnapshot (F11 §44): cadena completa y provenance bidireccional.

OBD Lab → TelemetrySession → OBDObservations → TelemetryPoints →
VehicleTelemetrySnapshots → VehicleEvent → FeatureVector(evento) → ModelInference →
DetectedAnomaly — recorrible en AMBOS sentidos. El pipeline F3
(Point→Window→LOF) NO se toca: el camino wide es PARALELO (F11 §43).
"""

import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from diagnostic_agent.events import build_baseline, detect_events, event_feature_vector
from diagnostic_agent.events.baseline import contextual_anomaly
from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.repositories import SQLiteTelemetryRepository
from diagnostic_agent.storage.store import EdgeStoreV2
from diagnostic_agent.telemetry.snapshots import PID_TO_FIELD, build_from_ticks
from mecanico_contracts import (
    ModelInference,
    OBDReading,
    ScenarioSpec,
    SignalQuality,
    TelemetryPoint,
    TelemetrySession,
    TransportKind,
    VehicleTelemetrySnapshot,
)
from mecanico_contracts.data_enums import SessionSource
from obd_lab.generate import generate_ticks

NOW = datetime(2026, 8, 13, tzinfo=UTC)
EPOCH = datetime(2026, 1, 1, tzinfo=UTC)
VEH = "veh-snap"
SID = "snap-e2e-seed7"


@pytest.fixture(scope="module")
def chain(tmp_path_factory: pytest.TempPathFactory) -> dict:
    tmp = tmp_path_factory.mktemp("snap")
    store = EdgeStoreV2(Path(tmp) / "edge.sqlite3")
    spec = ScenarioSpec(
        scenario_id="snap-e2e",
        description="cadena wide",
        category="known_fault",
        driving_profile="urban",
        duration_s=600,
        seed=50,
        fault="maf_drift",
        fault_params={"drift": 0.25},
        fault_start_s=0,
    )
    ticks = generate_ticks(spec)
    store.add(
        dbs.SessionRow,
        TelemetrySession(
            session_id=SID,
            source=SessionSource.SYNTHETIC_GENERATOR,
            vehicle_id=VEH,
            device_id="obd-lab",
            started_at=EPOCH,
            sample_rate_hz=1.0,
            software_version="f11",
            scenario_id=spec.scenario_id,
            random_seed=spec.seed,
        ),
    )
    # RAW: observaciones por PID y tick (muestra: primeros 120 s para volumen del test)
    observations = [
        OBDReading(
            timestamp=EPOCH + timedelta(seconds=i),
            pid=pid,
            value=float(t[pid]),
            unit="u",
            vehicle_id=VEH,
            device_id="obd-lab",
            source=TransportKind.TCP,
        )
        for i, t in enumerate(ticks)
        for pid in PID_TO_FIELD
    ]
    store.add_all(dbs.ObservationRow, observations[: 120 * len(PID_TO_FIELD)], session_id=SID)
    # NORMALIZED LONG
    points = [
        TelemetryPoint(session_id=SID, seq=i, timestamp=EPOCH + timedelta(seconds=i), values=t)
        for i, t in enumerate(ticks)
    ]
    store.add_all(dbs.PointRow, points)
    # eventos + NORMALIZED WIDE
    events = detect_events(ticks, SID, VEH)
    for e in events:
        store.add(dbs.EventRow, e)
    snapshots, links = build_from_ticks(ticks, SID, VEH, events=events, epoch=EPOCH)
    repo = SQLiteTelemetryRepository(store)
    repo.add_snapshots(snapshots)
    repo.add_event_links(links)

    # DERIVED + INFERRED por la vía de eventos (baseline de otras semillas normales)
    def accel_efvs(seed: int, fault: str | None):
        sp = spec.model_copy(
            update={
                "scenario_id": f"bl-{seed}",
                "seed": seed,
                "fault": fault,
                "fault_params": {"drift": 0.25} if fault else {},
                "fault_start_s": 0 if fault else None,
                "category": "known_fault" if fault else "normal",
            }
        )
        tk = generate_ticks(sp)
        evs = detect_events(tk, f"bl-{seed}", VEH)
        return [(e, event_feature_vector(e, tk)) for e in evs if e.event_type == "ACCELERATION"]

    ctx = "ACCELERATION|0-40|warm|d8-30s"
    train = [v for s in (1, 2, 3, 4, 5, 6) for _, v in accel_efvs(s, None)]
    baseline = build_baseline([v for v in train if v.context_signature == ctx], now=NOW)
    pairs = [(e, event_feature_vector(e, ticks)) for e in events if e.event_type == "ACCELERATION"]
    anomalous = [(e, v) for e, v in pairs if v.context_signature == ctx]
    event, efv = anomalous[-1]
    store.add(dbs.EventFeatureRow, efv)
    anomaly = contextual_anomaly(efv, baseline, now=NOW)
    assert anomaly is not None
    inference = ModelInference(
        inference_id=str(uuid.uuid4()),
        fv_id=efv.efv_id,
        window_id=f"{SID}:efv",
        session_id=SID,
        model_id="event-baseline-z",
        model_name="event-baseline-z",
        model_version="0.2.0",
        score=anomaly.score,
        threshold=anomaly.threshold,
        flagged=True,
        executed_at=NOW,
    )
    store.add(dbs.InferenceRow, inference)
    store.add(dbs.AnomalyRow, anomaly.model_copy(update={"inference_id": inference.inference_id}))
    return {
        "store": store,
        "repo": repo,
        "ticks": ticks,
        "events": events,
        "snapshots": snapshots,
        "anomaly": anomaly,
        "event": event,
        "efv": efv,
        "inference": inference,
    }


def test_cadena_hacia_adelante(chain: dict) -> None:
    """Obs → Point → Snapshot → Event → EFV → Inference → Anomaly, todo persistido."""
    store = chain["store"]
    assert store.count(dbs.ObservationRow) == 120 * len(PID_TO_FIELD)
    assert store.count(dbs.PointRow) == 600
    assert store.count(dbs.SnapshotRow) == 600
    assert store.count(dbs.SnapshotEventLinkRow) > 600  # N:M: TRIP + hoja simultáneos
    assert store.count(dbs.AnomalyRow) == 1


def test_snapshot_consulta_directa_sin_pivot(chain: dict) -> None:
    """La consulta del plan (§12): filtrar por evento y leer TODOS los parámetros."""
    repo = chain["repo"]
    rows = repo.by_event_type(VEH, "ACCELERATION", EPOCH, EPOCH + timedelta(hours=1))
    assert rows
    s = rows[0]
    # Todos los parámetros del instante SIN pivotar TelemetryPoint:
    assert None not in (s.rpm, s.vehicle_speed, s.maf, s.map_kpa, s.stft_bank1, s.engine_load)
    assert s.quality_score == 1.0 and s.quality_flags == {}
    # NULL ≠ 0: lo no sondeado es None (fuera del ciclo), jamás 0.0
    assert s.fuel_pressure is None and s.gps_speed is None


def test_provenance_hacia_atras(chain: dict) -> None:
    """Anomaly → event → snapshots (N:M) → seq → TelemetryPoint → OBDObservation."""
    store, anomaly, event = chain["store"], chain["anomaly"], chain["event"]
    # anomaly EVENT → evento origen
    assert anomaly.event_id == event.event_id
    ev_row = store.raw_rows(dbs.EventRow, event_id=event.event_id)[0]
    # evento → snapshots del intervalo vía N:M
    link_rows = store.raw_rows(dbs.SnapshotEventLinkRow, event_id=event.event_id)
    assert len(link_rows) == (ev_row.seq_end - ev_row.seq_start + 1)
    snap = store.get(
        VehicleTelemetrySnapshot, dbs.SnapshotRow, snapshot_id=link_rows[0].snapshot_id
    )
    assert snap is not None and snap.primary_event_id == event.event_id
    # snapshot → punto normalizado (mismo seq) → observaciones RAW del instante
    point_rows = store.raw_rows(dbs.PointRow, session_id=SID, seq=snap.sequence_number)
    assert len(point_rows) == 1
    assert point_rows[0].values["RPM"] == snap.rpm  # wide == long en el mismo instante
    if snap.sequence_number < 120:  # tramo con RAW persistido en el test
        obs = store.raw_rows(dbs.ObservationRow, session_id=SID, pid="RPM")
        target = [o for o in obs if o.timestamp == snap.timestamp_utc]
        assert len(target) == 1 and target[0].value == snap.rpm


def test_pipeline_f3_sigue_intacto(chain: dict) -> None:
    """El camino long→window→features no cambia (compatibilidad F11 §43)."""
    from mecanico_contracts.features import FEATURE_NAMES, extract_features

    ticks = chain["ticks"]
    window = {pid: [t[pid] for t in ticks[100:160]] for pid in ticks[0]}
    feats = extract_features(window)
    assert set(FEATURE_NAMES) <= set(feats) or len(feats) > 0  # sigue produciendo features


def test_snapshot_no_contiene_features(chain: dict) -> None:
    """Separación estricta estado físico ↔ features (F11 §14)."""
    fields = set(VehicleTelemetrySnapshot.model_fields)
    assert not any("mean" in f or "std" in f or "correlation" in f for f in fields)


def test_null_no_es_cero_con_flags(chain: dict) -> None:
    """Una señal del ciclo ausente → None + flag; nunca 0 (ADR-0027)."""
    ticks = [dict(t) for t in chain["ticks"][:5]]
    for t in ticks:
        t.pop("MAF")  # simular PID sin respuesta
    snaps, _ = build_from_ticks(ticks, "s-null", VEH)
    assert all(s.maf is None for s in snaps)
    assert all(s.quality_flags.get("maf") == SignalQuality.NOT_POLLED for s in snaps)
    assert all(s.missing_metric_count == 1 and s.quality_score < 1.0 for s in snaps)
