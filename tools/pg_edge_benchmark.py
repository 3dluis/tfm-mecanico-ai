"""Dimensionamiento de PostgreSQL en el edge (F12 §39). NO decide la arquitectura.

PostgreSQL + pgvector ya está adoptado (ADR-0030); esto mide para **dimensionar**:
volúmenes de 1 h / 8 h / 24 h de ``VehicleTelemetrySnapshot`` a 1 Hz, midiendo filas,
disco, **WAL generado**, throughput de inserción (batch vs COPY vs unitario), latencia de
las consultas principales, RAM de los procesos postgres y CPU.

Los resultados se escriben en ``ai-models/experiments/pg_edge_benchmark.json``. Nunca se
inventan: si no hay PostgreSQL, el script falla — no produce números sintéticos.

Uso: python tools/pg_edge_benchmark.py [--hours 1 8 24] [--pg-url ...]
"""

import argparse
import json
import os
import platform
import resource
import subprocess
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import text

from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.ingest import copy_rows
from diagnostic_agent.storage.partitions import list_partitions
from diagnostic_agent.storage.repositories import PostgresTelemetryRepository
from diagnostic_agent.storage.store import EdgeStore
from mecanico_contracts import TelemetrySession
from mecanico_contracts.data_enums import SessionSource

EPOCH = datetime(2026, 8, 1, tzinfo=UTC)
VEH = "veh-pgbench"


def _pg_rss_mb() -> float:
    out = subprocess.run(
        ["ps", "-C", "postgres", "-o", "rss="], capture_output=True, text=True, check=False
    ).stdout
    return round(sum(int(x) for x in out.split()) / 1024.0, 1) if out.strip() else 0.0


def _wal_bytes(store: EdgeStore) -> int:
    with store.engine.connect() as c:
        return int(
            c.execute(text("SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0')")).scalar_one()
        )


def _db_bytes(store: EdgeStore) -> int:
    with store.engine.connect() as c:
        return int(c.execute(text("SELECT pg_database_size(current_database())")).scalar_one())


def _reset(store: EdgeStore) -> None:
    from diagnostic_agent.storage.schema import SCHEMAS

    with store.engine.begin() as conn:
        for s in SCHEMAS:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{s}" CASCADE'))
    store.migrate()


def run_volume(store: EdgeStore, hours: float, use_copy: bool) -> dict:
    import sys

    sys.path.insert(0, str(Path(__file__).parent))
    from perf_snapshots import make_session_snapshots

    _reset(store)
    blocks = make_session_snapshots(hours, seed=3000, vehicle_id=VEH, epoch=EPOCH)
    for sid, _, _, _ in blocks:
        store.add(
            dbs.SessionRow,
            TelemetrySession(
                session_id=sid,
                source=SessionSource.SYNTHETIC_GENERATOR,
                vehicle_id=VEH,
                device_id="obd-lab",
                started_at=EPOCH,
                sample_rate_hz=1.0,
                software_version="pgbench",
            ),
        )
    for _sid, _, _, events in blocks:
        store.add_all(dbs.EventRow, list(events))

    repo = PostgresTelemetryRepository(store)
    total = sum(len(s) for _, s, _, _ in blocks)
    wal0, cpu0 = _wal_bytes(store), resource.getrusage(resource.RUSAGE_SELF).ru_utime

    t0 = time.perf_counter()
    for _sid, snaps, links, _ in blocks:
        if use_copy:
            copy_rows(store, dbs.SnapshotRow, list(snaps))
            copy_rows(store, dbs.SnapshotEventLinkRow, list(links))
        else:
            repo.add_snapshots(snaps)
            repo.add_event_links(links)
    t_batch = time.perf_counter() - t0
    wal_batch = _wal_bytes(store) - wal0

    sample = blocks[0][1][:200]
    t0 = time.perf_counter()
    for s in sample:
        store.add(dbs.SnapshotRow, s.model_copy(update={"snapshot_id": s.snapshot_id + "-i"}))
    t_single = time.perf_counter() - t0

    def timed(fn) -> tuple[float, int]:
        t = time.perf_counter()
        rows = fn()
        return (time.perf_counter() - t) * 1000, len(rows)

    q_session_ms, n1 = timed(lambda: repo.by_session(blocks[0][0]))
    q_range_ms, n2 = timed(
        lambda: repo.by_vehicle_range(VEH, EPOCH, EPOCH + timedelta(hours=hours))
    )
    q_event_ms, n3 = timed(
        lambda: repo.by_event_type(VEH, "ACCELERATION", EPOCH, EPOCH + timedelta(hours=hours))
    )
    trip_event = next(e for e in blocks[0][3] if e.event_type == "TRIP")
    q_diag_ms, n4 = timed(lambda: repo.snapshots_of_event(trip_event.event_id))
    with store.engine.connect() as c:
        c.execute(text("ANALYZE telemetry.vehicle_telemetry_snapshots"))
    return {
        "hours": hours,
        "write_path": "COPY" if use_copy else "executemany",
        "snapshots": total,
        "db_size_mb": round(_db_bytes(store) / 1e6, 2),
        "wal_generated_mb": round(wal_batch / 1e6, 2),
        "batch_insert_rows_per_s": round(total / t_batch),
        "single_insert_rows_per_s": round(len(sample) / t_single),
        "q_session_ms": round(q_session_ms, 1),
        "q_session_rows": n1,
        "q_vehicle_range_ms": round(q_range_ms, 1),
        "q_vehicle_range_rows": n2,
        "q_event_type_ms": round(q_event_ms, 1),
        "q_event_type_rows": n3,
        "q_diagnostic_join_ms": round(q_diag_ms, 1),
        "q_diagnostic_rows": n4,
        "partitions": [
            {"name": n, "mb": round(b / 1e6, 2)} for n, b in list_partitions(store.engine)
        ],
        "postgres_rss_mb": _pg_rss_mb(),
        "client_cpu_user_s_cum": round(resource.getrusage(resource.RUSAGE_SELF).ru_utime - cpu0, 1),
        "client_peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", nargs="*", type=float, default=[1, 8, 24])
    ap.add_argument("--pg-url", default=os.environ.get("MECANICO_DB_URL"))
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parents[1] / "ai-models" / "experiments" / "pg_edge_benchmark.json",
    )
    args = ap.parse_args()
    store = EdgeStore(url=args.pg_url) if args.pg_url else EdgeStore()
    with store.engine.connect() as c:
        version = c.execute(text("SHOW server_version")).scalar_one()
        settings = {
            k: c.execute(text(f"SHOW {k}")).scalar_one()
            for k in ("shared_buffers", "work_mem", "max_connections", "wal_compression")
        }
    results = {
        "measured_at": datetime.now(UTC).isoformat(),
        "hardware": f"{platform.machine()} sandbox 4CPU/8GB (proxy RPi 5 — interpretar como x86)",
        "postgres_version": version,
        "settings": settings,
        "frequency_hz": 1.0,
        "volumes": [run_volume(store, h, use_copy=False) for h in args.hours],
        "copy_vs_executemany_8h": [
            run_volume(store, 8.0, use_copy=True),
        ],
    }
    args.out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
