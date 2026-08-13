"""Performance test de VehicleTelemetrySnapshot en SQLite (F11 §27).

Inserta volúmenes equivalentes a 1 h / 8 h / 24 h de telemetría simulada a 1 Hz
(frecuencia validada; 5 Hz sigue siendo candidato) y mide: tamaño de BD, throughput de
insert individual y por lotes, latencia de las queries principales, CPU y RAM. Los
resultados se escriben a ``ai-models/experiments/perf_snapshots.json`` — NUNCA se
inventan: este script debe ejecutarse de verdad y el hardware queda registrado.

Uso: python tools/perf_snapshots.py [--hours 1 8 24] [--out ...]
"""

import argparse
import json
import platform
import resource
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from diagnostic_agent.events import detect_events
from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.repositories import SQLiteTelemetryRepository
from diagnostic_agent.storage.store import EdgeStoreV2
from diagnostic_agent.telemetry.snapshots import build_from_ticks
from mecanico_contracts import ScenarioSpec, TelemetrySession
from mecanico_contracts.data_enums import SessionSource

EPOCH = datetime(2026, 1, 1, tzinfo=UTC)
VEH = "veh-perf"


def make_session_snapshots(hours: float, seed: int, vehicle_id: str = VEH):
    """Genera snapshots realistas (ticks obd-lab + eventos detectados) por bloques."""
    out = []
    remaining = int(hours * 3600)
    block = 1800  # sesiones de 30 min encadenadas (límite del generador por spec)
    idx = 0
    while remaining > 0:
        dur = min(block, remaining)
        spec = ScenarioSpec(
            scenario_id=f"perf-{seed}-{idx}",
            description="perf",
            category="normal",
            driving_profile="urban" if idx % 2 == 0 else "highway",
            duration_s=dur,
            seed=seed + idx,
        )
        from obd_lab.generate import generate_ticks

        ticks = generate_ticks(spec)
        sid = f"perf-{seed}-{idx}"
        events = detect_events(ticks, sid, vehicle_id)
        snaps, links = build_from_ticks(
            ticks, sid, vehicle_id, events=events, epoch=EPOCH + timedelta(seconds=idx * block)
        )
        out.append((sid, snaps, links, events))
        remaining -= dur
        idx += 1
    return out


def run_volume(hours: float) -> dict:
    with TemporaryDirectory() as td:
        db_path = Path(td) / "perf.sqlite3"
        store = EdgeStoreV2(db_path)
        repo = SQLiteTelemetryRepository(store)
        blocks = make_session_snapshots(hours, seed=1000)
        total = sum(len(s) for _, s, _, _ in blocks)

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
                    software_version="perf",
                ),
            )
        for _sid, _, _, events in blocks:  # eventos primero (FK de los enlaces N:M)
            store.add_all(dbs.EventRow, list(events))
        # batch insert (camino prioritario)
        t0 = time.perf_counter()
        for _sid, snaps, links, _ in blocks:
            repo.add_snapshots(snaps)
            repo.add_event_links(links)
        t_batch = time.perf_counter() - t0
        # insert individual (referencia; muestra de 200)
        sample = blocks[0][1][:200]
        t0 = time.perf_counter()
        for s in sample:
            store.add(dbs.SnapshotRow, s.model_copy(update={"snapshot_id": s.snapshot_id + "-i"}))
        t_single = time.perf_counter() - t0

        # queries principales (documentadas en docs/data-architecture/11 §queries)
        t0 = time.perf_counter()
        by_session = repo.by_session(blocks[0][0])
        q_session_ms = (time.perf_counter() - t0) * 1000
        t0 = time.perf_counter()
        rng = repo.by_vehicle_range(VEH, EPOCH, EPOCH + timedelta(hours=hours))
        q_range_ms = (time.perf_counter() - t0) * 1000
        t0 = time.perf_counter()
        acc = repo.by_event_type(VEH, "ACCELERATION", EPOCH, EPOCH + timedelta(hours=hours))
        q_event_ms = (time.perf_counter() - t0) * 1000

        ru = resource.getrusage(resource.RUSAGE_SELF)
        return {
            "hours": hours,
            "snapshots": total,
            "db_size_mb": round(db_path.stat().st_size / 1e6, 2),
            "batch_insert_rows_per_s": round(total / t_batch),
            "single_insert_rows_per_s": round(len(sample) / t_single),
            "q_session_ms": round(q_session_ms, 1),
            "q_session_rows": len(by_session),
            "q_vehicle_range_ms": round(q_range_ms, 1),
            "q_vehicle_range_rows": len(rng),
            "q_event_type_ms": round(q_event_ms, 1),
            "q_event_type_rows": len(acc),
            "cpu_user_s_cum": round(ru.ru_utime, 1),
            "peak_rss_mb": round(ru.ru_maxrss / 1024.0, 1),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", nargs="*", type=float, default=[1, 8, 24])
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parents[1] / "ai-models" / "experiments" / "perf_snapshots.json",
    )
    args = parser.parse_args()
    results = {
        "measured_at": datetime.now(UTC).isoformat(),
        "hardware": f"{platform.machine()} (sandbox 4 CPU/8GB proxy RPi — interpretar como x86)",
        "frequency_hz": 1.0,
        "note": "5 Hz sigue siendo candidato SIN validar (ADR-0026)",
        "volumes": [run_volume(h) for h in args.hours],
    }
    args.out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
