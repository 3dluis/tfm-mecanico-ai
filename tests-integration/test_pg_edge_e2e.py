"""E2E REAL sobre PostgreSQL + pgvector (F12 §41): cadena completa y provenance inversa.

Session → Observation → TelemetryPoint → VehicleTelemetrySnapshot → Event → EventFeature
→ ModelInference → DetectedAnomaly → DiagnosticCase → CaseMemory → LearnedPattern,
recorrible hacia atrás. Además: particionado real, búsqueda vectorial con filtrado
relacional, atomicidad negocio+outbox y migración SQLite→PostgreSQL.

Se SALTA (skip) si no hay PostgreSQL disponible — nunca se simulan resultados.
"""

import os
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import text

from diagnostic_agent.events import detect_events
from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.metrics import collect
from diagnostic_agent.storage.partitions import list_partitions
from diagnostic_agent.storage.repositories import (
    PostgresKnowledgeRepository,
    PostgresMemoryRepository,
    PostgresTelemetryRepository,
)
from diagnostic_agent.storage.store import EdgeStore
from diagnostic_agent.telemetry.snapshots import PID_TO_FIELD, build_from_ticks
from mecanico_contracts import (
    CaseMemory,
    DetectedAnomaly,
    DiagnosticCase,
    FeatureVector,
    KnowledgeChunk,
    KnowledgeDocument,
    LearnedPattern,
    ModelInference,
    OBDReading,
    ScenarioSpec,
    TelemetryPoint,
    TelemetrySession,
    TelemetryWindow,
    TransportKind,
    VehicleTelemetrySnapshot,
)
from mecanico_contracts.data_enums import EpistemicLevel, SessionSource
from obd_lab.generate import generate_ticks

PG_URL = os.environ.get(
    "MECANICO_TEST_DB_URL",
    os.environ.get("MECANICO_DB_URL", ""),
)
EPOCH = datetime(2026, 8, 1, tzinfo=UTC)
NOW = datetime(2026, 8, 13, tzinfo=UTC)
VEH = "veh-pg"
SID = "pg-e2e-1"
DIM = 384


def _pg_available(url: str) -> bool:
    if not url or url.startswith("sqlite"):
        return False
    try:
        store = EdgeStore(url=url, migrate=False)
        with store.engine.connect() as c:
            c.execute(text("select 1"))
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _pg_available(PG_URL),
    reason="PostgreSQL no disponible (define MECANICO_TEST_DB_URL para ejecutarlo)",
)


def _vec(seed: int) -> list[float]:
    """Vector determinista y normalizado (sin dependencias de modelo real)."""
    import math

    raw = [math.sin(seed * 0.7 + i * 0.013) for i in range(DIM)]
    norm = math.sqrt(sum(v * v for v in raw))
    return [v / norm for v in raw]


@pytest.fixture(scope="module")
def pg() -> dict:
    store = EdgeStore(url=PG_URL, migrate=False)
    with store.engine.begin() as conn:  # base limpia para el módulo
        for schema in (
            "telemetry",
            "events",
            "diagnostics",
            "models",
            "memory",
            "knowledge",
            "agent",
            "sync",
            "core",
        ):
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
    store = EdgeStore(url=PG_URL)

    spec = ScenarioSpec(
        scenario_id="pg-e2e",
        description="cadena completa PostgreSQL",
        category="known_fault",
        driving_profile="urban",
        duration_s=300,
        seed=77,
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
            software_version="f12",
            scenario_id=spec.scenario_id,
            random_seed=spec.seed,
        ),
    )
    store.add_all(
        dbs.ObservationRow,
        [
            OBDReading(
                timestamp=EPOCH + timedelta(seconds=i),
                pid=pid,
                value=float(t[pid]),
                unit="u",
                vehicle_id=VEH,
                device_id="obd-lab",
                source=TransportKind.TCP,
            )
            for i, t in enumerate(ticks[:60])
            for pid in PID_TO_FIELD
        ],
        session_id=SID,
    )
    store.add_all(
        dbs.PointRow,
        [
            TelemetryPoint(session_id=SID, seq=i, timestamp=EPOCH + timedelta(seconds=i), values=t)
            for i, t in enumerate(ticks)
        ],
    )
    events = detect_events(ticks, SID, VEH)
    store.add_all(dbs.EventRow, list(events))
    snapshots, links = build_from_ticks(ticks, SID, VEH, events=events, epoch=EPOCH)
    repo = PostgresTelemetryRepository(store)
    repo.add_snapshots(snapshots)
    repo.add_event_links(links)

    # PostgreSQL SÍ exige las claves ajenas (SQLite no las aplicaba): la ventana y el
    # vector de features deben existir antes que la inferencia — integridad real.
    store.add(
        dbs.WindowRow,
        TelemetryWindow(
            window_id=f"{SID}:w1",
            session_id=SID,
            seq_start=0,
            seq_end=59,
            start=EPOCH,
            end=EPOCH + timedelta(seconds=59),
            size=60,
            stride=30,
        ),
    )
    store.add(
        dbs.FeatureVectorRow,
        FeatureVector(
            fv_id="fv-pg-1",
            window_id=f"{SID}:w1",
            session_id=SID,
            feature_set_version="fs:1",
            values={"rpm_mean": 1200.0},
        ),
    )
    inference = ModelInference(
        inference_id=str(uuid.uuid4()),
        fv_id="fv-pg-1",
        window_id=f"{SID}:w1",
        session_id=SID,
        model_id="lof-v1",
        model_name="lof",
        model_version="1.0.0",
        score=0.9,
        threshold=0.163197,
        flagged=True,
        executed_at=NOW,
    )
    store.add(dbs.InferenceRow, inference)
    anomaly = DetectedAnomaly(
        anomaly_id=str(uuid.uuid4()),
        session_id=SID,
        vehicle_id=VEH,
        detected_at=NOW,
        window_id=f"{SID}:w1",
        inference_id=inference.inference_id,
        score=0.9,
        threshold=0.163197,
        detector="lof",
        involved_pids=["MAF"],
    )
    store.add(dbs.AnomalyRow, anomaly)
    case = DiagnosticCase(
        case_id=str(uuid.uuid4()),
        vehicle_id=VEH,
        session_id=SID,
        trigger_anomaly_ids=[anomaly.anomaly_id],
        opened_at=NOW,
        status="open",
    )
    store.add(dbs.CaseRow, case)
    return {
        "store": store,
        "repo": repo,
        "events": events,
        "snapshots": snapshots,
        "anomaly": anomaly,
        "case": case,
        "inference": inference,
        "ticks": ticks,
    }


def test_cadena_completa_persistida(pg: dict) -> None:
    store = pg["store"]
    assert store.count(dbs.PointRow) == 300
    assert store.count(dbs.SnapshotRow) == 300
    assert store.count(dbs.SnapshotEventLinkRow) > 300
    assert store.count(dbs.AnomalyRow) == 1
    assert store.count(dbs.CaseRow) == 1


def test_particionado_real_encaminando_filas(pg: dict) -> None:
    """Las filas caen en la partición del mes; la tabla padre las ve todas."""
    store = pg["store"]
    parts = list_partitions(store.engine)
    assert any(p[0] == "snapshots_2026_08" for p in parts)
    with store.engine.connect() as c:
        in_month = c.execute(text("SELECT count(*) FROM telemetry.snapshots_2026_08")).scalar_one()
        total = c.execute(
            text("SELECT count(*) FROM telemetry.vehicle_telemetry_snapshots")
        ).scalar_one()
        default_rows = c.execute(
            text("SELECT count(*) FROM telemetry.snapshots_default")
        ).scalar_one()
    assert in_month == total == 300
    assert default_rows == 0


def test_provenance_inversa_en_postgresql(pg: dict) -> None:
    """Anomaly → inference → snapshot(N:M) → point → observation, con igualdad de valores."""
    store, repo = pg["store"], pg["repo"]
    anomaly = store.get(DetectedAnomaly, dbs.AnomalyRow, anomaly_id=pg["anomaly"].anomaly_id)
    assert anomaly is not None and anomaly.inference_id == pg["inference"].inference_id
    event = next(e for e in pg["events"] if e.event_type == "ACCELERATION")
    snaps = repo.snapshots_of_event(event.event_id)
    assert snaps, "la relación N:M debe devolver los snapshots del evento"
    snap = snaps[0]
    point_rows = store.raw_rows(dbs.PointRow, session_id=SID, seq=snap.sequence_number)
    assert len(point_rows) == 1
    assert point_rows[0].values["RPM"] == snap.rpm
    if snap.sequence_number < 60:
        obs = [
            o
            for o in store.raw_rows(dbs.ObservationRow, session_id=SID, pid="RPM")
            if o.timestamp == snap.timestamp_utc
        ]
        assert len(obs) == 1 and obs[0].value == snap.rpm


def test_busqueda_vectorial_con_filtro_relacional(pg: dict) -> None:
    """pgvector + WHERE en la MISMA consulta (la ventaja que motivó la adopción)."""
    store = pg["store"]
    know = PostgresKnowledgeRepository(store)
    mem = PostgresMemoryRepository(store)
    store.add(
        dbs.KnowledgeDocumentRow,
        KnowledgeDocument(
            document_id="doc-1",
            title="Manual MAF",
            source="test",
            license="CC-BY",
            ingested_at=NOW,
        ),
    )
    for i in range(5):
        know.add_chunk(
            KnowledgeChunk(chunk_id=f"ch-{i}", document_id="doc-1", seq=i, text=f"texto {i}"),
            embedding=_vec(i),
        )
    hits = know.search(_vec(3), k=2)
    assert hits and hits[0][0].chunk_id == "ch-3"
    assert hits[0][1] < 1e-6  # distancia coseno ~0 contra sí mismo

    for i, veh in enumerate(("veh-A", "veh-B")):
        mem.add_case(
            CaseMemory(
                case_memory_id=f"cm-{i}",
                case_id=pg["case"].case_id,
                vehicle_id=veh,
                symptom_text="MAF baja en aceleración",
                symptom_signature={"maf_mean": 2.1},
                diagnosis="sensor MAF sucio",
                epistemic_level=EpistemicLevel.SIMULATED,
                created_at=NOW,
                updated_at=NOW,
            ),
            embedding=_vec(10 + i),
        )
    filtered = mem.similar_cases(_vec(11), k=5, vehicle_id="veh-B")
    assert len(filtered) == 1 and filtered[0][0].vehicle_id == "veh-B"

    mem.add_pattern(
        LearnedPattern(
            pattern_id="lp-1",
            title="deriva de MAF",
            description="MAF cae progresivamente en aceleraciones comparables",
            telemetry_signature={"maf_slope": -0.4},
            affected_metrics=["MAF"],
            version=1,
            first_seen=NOW,
            last_seen=NOW,
        ),
        embedding=_vec(20),
    )
    assert mem.similar_patterns(_vec(20), k=1)[0][0].pattern_id == "lp-1"


def test_outbox_en_la_misma_transaccion(pg: dict) -> None:
    """Escritura de negocio + sobre de outbox = una sola transacción (F12 §33)."""
    store = pg["store"]
    before = store.count(dbs.OutboxRow)
    case = DiagnosticCase(
        case_id=str(uuid.uuid4()),
        vehicle_id=VEH,
        session_id=SID,
        trigger_anomaly_ids=[pg["anomaly"].anomaly_id],
        opened_at=NOW,
        status="open",
    )
    store.add_with_outbox(
        dbs.CaseRow, case, entity="DiagnosticCase", entity_id=case.case_id, priority=1
    )
    assert store.count(dbs.OutboxRow) == before + 1
    row = store.raw_rows(dbs.OutboxRow, entity_id=case.case_id)[0]
    assert row.priority == 1 and row.checksum and row.payload["case_id"] == case.case_id

    # Si la escritura de negocio falla, NO debe quedar el sobre huérfano.
    bad = case.model_copy(update={"case_id": case.case_id})  # PK duplicada → IntegrityError
    with pytest.raises(Exception):  # noqa: B017
        store.add_with_outbox(dbs.CaseRow, bad, entity="DiagnosticCase", entity_id=bad.case_id)
    assert store.count(dbs.OutboxRow) == before + 1


def test_metricas_basicas_disponibles(pg: dict) -> None:
    m = collect(pg["store"], sample_vector=_vec(1))
    assert m["engine"] == "postgresql"
    assert m["snapshot_rows"] == 300
    assert m["db_size_bytes"] > 0 and m["wal_bytes"] > 0
    assert m["vector_query_latency_ms"] >= 0


def test_migracion_sqlite_a_postgresql(tmp_path: Path) -> None:
    """Migración controlada de datos legacy: conteos y provenance preservados (F12 §24)."""
    import sys

    sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))
    from migrate_sqlite_to_pg import migrate

    legacy = EdgeStore(db_path=tmp_path / "legacy.sqlite3")
    sid = "legacy-1"
    legacy.add(
        dbs.SessionRow,
        TelemetrySession(
            session_id=sid,
            source=SessionSource.SYNTHETIC_GENERATOR,
            vehicle_id="veh-legacy",
            device_id="obd-lab",
            started_at=EPOCH,
            sample_rate_hz=1.0,
            software_version="legacy",
        ),
    )
    ticks = generate_ticks(
        ScenarioSpec(
            scenario_id="legacy",
            description="d",
            category="normal",
            driving_profile="urban",
            duration_s=60,
            seed=5,
        )
    )
    snaps, links = build_from_ticks(ticks, sid, "veh-legacy", epoch=EPOCH)
    PostgresTelemetryRepository(legacy).add_snapshots(snaps)
    PostgresTelemetryRepository(legacy).add_event_links(links)

    report = migrate(tmp_path / "legacy.sqlite3", PG_URL)
    assert report["ok"], report
    assert report["tables"]["vehicle_telemetry_snapshots"]["source"] == 60

    dst = EdgeStore(url=PG_URL, migrate=False)
    migrated = dst.list_(VehicleTelemetrySnapshot, dbs.SnapshotRow, limit=100, session_id=sid)
    assert len(migrated) == 60
    assert migrated[0].rpm == snaps[0].rpm  # los valores sobreviven al cambio de motor
