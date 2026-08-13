"""Ingesta asíncrona por lotes: la adquisición no se bloquea por la base (F12 §9/§10)."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.ingest import Backpressure, PersistenceWorker
from diagnostic_agent.storage.store import EdgeStore
from mecanico_contracts import TelemetrySession, VehicleTelemetrySnapshot
from mecanico_contracts.data_enums import SessionSource

EPOCH = datetime(2026, 8, 1, tzinfo=UTC)
SID = "ingest-1"


def _snapshot(i: int) -> VehicleTelemetrySnapshot:
    return VehicleTelemetrySnapshot(
        snapshot_id=f"snap-{i}",
        vehicle_id="veh-i",
        device_id="obd-lab",
        session_id=SID,
        timestamp_utc=EPOCH + timedelta(seconds=i),
        sequence_number=i,
        snapshot_interval_ms=1000,
        quality_score=1.0,
        rpm=800.0 + i,
        created_at=EPOCH,
    )


def _store(tmp_path: Path) -> EdgeStore:
    store = EdgeStore(db_path=tmp_path / "ingest.sqlite3")
    store.add(
        dbs.SessionRow,
        TelemetrySession(
            session_id=SID,
            source=SessionSource.SYNTHETIC_GENERATOR,
            vehicle_id="veh-i",
            device_id="obd-lab",
            started_at=EPOCH,
            sample_rate_hz=1.0,
            software_version="test",
        ),
    )
    return store


def test_worker_escribe_por_lotes_no_por_fila(tmp_path: Path) -> None:
    store = _store(tmp_path)
    with PersistenceWorker(store, batch_size=100, flush_interval_s=0.2) as w:
        for i in range(300):
            w.submit(dbs.SnapshotRow, _snapshot(i))
    assert store.count(dbs.SnapshotRow) == 300
    # 300 filas en muy pocos lotes: jamás un COMMIT por muestra.
    assert w.stats.batches <= 5
    assert w.stats.written == 300 and w.stats.failed == 0


def test_backpressure_drop_oldest_cuenta_lo_descartado(tmp_path: Path) -> None:
    """Con cola llena se descarta lo más viejo, pero NUNCA en silencio."""
    store = _store(tmp_path)
    w = PersistenceWorker(
        store, batch_size=1000, max_queue=10, backpressure=Backpressure.DROP_OLDEST
    )
    for i in range(50):  # sin arrancar el consumidor: la cola se llena de verdad
        w.submit(dbs.SnapshotRow, _snapshot(i))
    assert w.stats.dropped > 0
    assert w.stats.enqueued + w.stats.dropped >= 50
    w.start()
    w.stop()
    assert store.count(dbs.SnapshotRow) <= 10  # solo lo que sobrevivió en la cola


def test_fallo_de_persistencia_no_mata_la_adquisicion(tmp_path: Path) -> None:
    """Un lote inválido se contabiliza como fallido; el worker sigue aceptando datos."""
    store = _store(tmp_path)
    with PersistenceWorker(store, batch_size=2, flush_interval_s=0.1, max_retries=1) as w:
        w.submit(dbs.SnapshotRow, _snapshot(1).model_copy(update={"session_id": "no-existe"}))
        w.submit(dbs.SnapshotRow, _snapshot(2))
        w.submit(dbs.SnapshotRow, _snapshot(3))
    assert w.stats.written + w.stats.failed == 3
