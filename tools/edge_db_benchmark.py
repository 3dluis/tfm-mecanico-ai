"""Benchmark Edge: SQLite vs PostgreSQL+pgvector con la MISMA carga (F11 §33-34).

Misma carga por el MISMO código (EdgeStoreV2 + TelemetryRepository; solo cambia el
motor): 8 h de snapshots reales de obd-lab (28 800 filas + enlaces N:M), las queries
principales documentadas, y un benchmark vectorial pequeño pero representativo
(1000 KnowledgeChunks + 500 CaseMemory + 100 LearnedPatterns, 384 dims, top-10):
pgvector (exacto e IVFFlat) frente a la alternativa realista del mundo SQLite
(vectores en fichero + búsqueda numpy en proceso).

Notas de honestidad: los vectores son SINTÉTICOS (miden el MOTOR, no la calidad de
recuperación); el hardware es el sandbox x86 (proxy del perfil RPi) y se registra; la
RAM de PostgreSQL se mide sumando el RSS de sus procesos; SQLite no añade procesos
(RAM marginal ≈ 0 sobre el propio agente).

Requiere: postgresql-16 + pgvector locales (o el perfil docker edge-postgres en el Mac).
Uso: python tools/edge_db_benchmark.py [--pg-url ...] [--out ...]
"""

import argparse
import json
import platform
import statistics
import subprocess
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.repositories import (
    PostgresTelemetryRepository,
    SQLiteTelemetryRepository,
)
from diagnostic_agent.storage.store import EdgeStoreV2
from mecanico_contracts import TelemetrySession
from mecanico_contracts.data_enums import SessionSource

EPOCH = datetime(2026, 1, 1, tzinfo=UTC)
VEH = "veh-bench"
DIMS = 384
N_CHUNKS, N_CASES, N_PATTERNS = 1000, 500, 100
TOPK, N_QUERIES = 10, 50


def _pg_rss_mb() -> float:
    out = subprocess.run(
        ["ps", "-C", "postgres", "-o", "rss="], capture_output=True, text=True, check=False
    ).stdout
    return round(sum(int(x) for x in out.split()) / 1024.0, 1) if out.strip() else 0.0


def build_workload(hours: float = 8.0):
    import sys

    sys.path.insert(0, str(Path(__file__).parent))
    from perf_snapshots import make_session_snapshots

    return make_session_snapshots(hours, seed=2000, vehicle_id=VEH)


def bench_engine(store: EdgeStoreV2, repo, blocks) -> dict:
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
                software_version="bench",
            ),
        )
    for _sid, _, _, events in blocks:  # eventos primero (FK de los enlaces N:M)
        store.add_all(dbs.EventRow, list(events))
    total = sum(len(s) for _, s, _, _ in blocks)
    t0 = time.perf_counter()
    for _sid, snaps, links, _ in blocks:
        repo.add_snapshots(snaps)
        repo.add_event_links(links)
    t_batch = time.perf_counter() - t0
    sample = blocks[0][1][:200]
    t0 = time.perf_counter()
    for s in sample:
        store.add(dbs.SnapshotRow, s.model_copy(update={"snapshot_id": s.snapshot_id + "-i"}))
    t_single = time.perf_counter() - t0

    def timed(fn) -> tuple[float, int]:
        t0 = time.perf_counter()
        rows = fn()
        return (time.perf_counter() - t0) * 1000, len(rows)

    q_session_ms, n1 = timed(lambda: repo.by_session(blocks[0][0]))
    q_range_ms, n2 = timed(lambda: repo.by_vehicle_range(VEH, EPOCH, EPOCH + timedelta(hours=2)))
    q_event_ms, n3 = timed(
        lambda: repo.by_event_type(VEH, "ACCELERATION", EPOCH, EPOCH + timedelta(hours=8))
    )
    # "diagnóstico": snapshots de UN evento vía N:M (join links→snapshots)
    from sqlalchemy import select
    from sqlalchemy.orm import Session as OrmSession

    with OrmSession(store.engine) as s:
        # evento determinista y comparable entre motores: el TRIP de la primera sesión
        some_event = s.execute(
            select(dbs.EventRow.event_id)
            .where(dbs.EventRow.session_id == blocks[0][0])
            .where(dbs.EventRow.event_type == "TRIP")
        ).scalar_one()
        t0 = time.perf_counter()
        joined = (
            s.execute(
                select(dbs.SnapshotRow)
                .join(
                    dbs.SnapshotEventLinkRow,
                    dbs.SnapshotEventLinkRow.snapshot_id == dbs.SnapshotRow.snapshot_id,
                )
                .where(dbs.SnapshotEventLinkRow.event_id == some_event)
            )
            .scalars()
            .all()
        )
        q_diag_ms = (time.perf_counter() - t0) * 1000
    return {
        "rows": total,
        "batch_insert_rows_per_s": round(total / t_batch),
        "single_insert_rows_per_s": round(len(sample) / t_single),
        "q_session_ms": round(q_session_ms, 1),
        "q_range2h_ms": round(q_range_ms, 1),
        "q_event_type_ms": round(q_event_ms, 1),
        "q_diagnostic_join_ms": round(q_diag_ms, 1),
        "q_rows": {"session": n1, "range2h": n2, "event": n3, "diag_join": len(joined)},
    }


def bench_vectors_pg(url: str) -> dict:
    import sqlalchemy

    engine = sqlalchemy.create_engine(url)
    rng = np.random.default_rng(42)
    vectors = rng.normal(size=(N_CHUNKS + N_CASES + N_PATTERNS, DIMS)).astype(np.float32)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    queries = rng.normal(size=(N_QUERIES, DIMS)).astype(np.float32)
    queries /= np.linalg.norm(queries, axis=1, keepdims=True)
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(sqlalchemy.text("DROP TABLE IF EXISTS bench_embeddings"))
        conn.execute(
            sqlalchemy.text(
                f"CREATE TABLE bench_embeddings (id serial PRIMARY KEY, kind text, "
                f"embedding vector({DIMS}))"
            )
        )
        conn.commit()
        t0 = time.perf_counter()
        kinds = ["chunk"] * N_CHUNKS + ["case"] * N_CASES + ["pattern"] * N_PATTERNS
        for kind, v in zip(kinds, vectors, strict=True):
            conn.execute(
                sqlalchemy.text("INSERT INTO bench_embeddings (kind, embedding) VALUES (:k, :v)"),
                {"k": kind, "v": str(v.tolist())},
            )
        conn.commit()
        t_load = time.perf_counter() - t0

        def run_queries() -> float:
            lats = []
            for q in queries:
                t0 = time.perf_counter()
                conn.execute(
                    sqlalchemy.text(
                        "SELECT id FROM bench_embeddings ORDER BY embedding <=> :q LIMIT :k"
                    ),
                    {"q": str(q.tolist()), "k": TOPK},
                ).fetchall()
                lats.append((time.perf_counter() - t0) * 1000)
            return statistics.median(lats)

        exact_ms = run_queries()
        conn.execute(
            sqlalchemy.text(
                "CREATE INDEX ON bench_embeddings USING ivfflat (embedding vector_cosine_ops) "
                "WITH (lists = 40)"
            )
        )
        conn.commit()
        ivf_ms = run_queries()
    return {
        "load_s": round(t_load, 2),
        "topk_exact_median_ms": round(exact_ms, 2),
        "topk_ivfflat_median_ms": round(ivf_ms, 2),
        "n_vectors": len(vectors),
        "dims": DIMS,
    }


def bench_vectors_numpy() -> dict:
    """Alternativa del mundo SQLite: vectores en memoria/fichero + numpy en proceso."""
    rng = np.random.default_rng(42)
    vectors = rng.normal(size=(N_CHUNKS + N_CASES + N_PATTERNS, DIMS)).astype(np.float32)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    queries = rng.normal(size=(N_QUERIES, DIMS)).astype(np.float32)
    queries /= np.linalg.norm(queries, axis=1, keepdims=True)
    lats = []
    for q in queries:
        t0 = time.perf_counter()
        sims = vectors @ q
        np.argpartition(-sims, TOPK)[:TOPK]
        lats.append((time.perf_counter() - t0) * 1000)
    return {
        "topk_bruteforce_median_ms": round(statistics.median(lats), 3),
        "ram_for_vectors_mb": round(vectors.nbytes / 1e6, 1),
        "n_vectors": len(vectors),
        "dims": DIMS,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pg-url",
        default="postgresql+psycopg://root@/mecanico_edge_bench?host=/var/run/postgresql",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parents[1] / "ai-models" / "experiments" / "edge_db_benchmark.json",
    )
    args = parser.parse_args()
    results: dict = {
        "measured_at": datetime.now(UTC).isoformat(),
        "hardware": f"{platform.machine()} sandbox 4CPU/8GB (proxy RPi; interpretar como x86)",
        "workload": "8h de snapshots obd-lab (28800 filas + N:M) por el MISMO código",
    }
    blocks = build_workload(8.0)

    # --- SQLite
    with TemporaryDirectory() as td:
        db = Path(td) / "bench.sqlite3"
        t0 = time.perf_counter()
        store = EdgeStoreV2(db)
        startup_ms = (time.perf_counter() - t0) * 1000
        repo = SQLiteTelemetryRepository(store)
        r = bench_engine(store, repo, blocks)
        r["startup_ms"] = round(startup_ms, 1)
        r["idle_extra_ram_mb"] = 0.0
        r["disk_mb"] = round(db.stat().st_size / 1e6, 2)
        r["vector"] = bench_vectors_numpy()
        results["sqlite"] = r

    # --- PostgreSQL + pgvector
    try:
        subprocess.run(["createdb", "mecanico_edge_bench"], check=False, capture_output=True)
        t0 = time.perf_counter()
        store_pg = EdgeStoreV2(url=args.pg_url)
        startup_ms = (time.perf_counter() - t0) * 1000
        repo_pg = PostgresTelemetryRepository(store_pg)
        r = bench_engine(store_pg, repo_pg, blocks)
        r["startup_ms_connect_migrate"] = round(startup_ms, 1)
        r["idle_ram_postgres_processes_mb"] = _pg_rss_mb()
        import sqlalchemy

        with store_pg.engine.connect() as conn:
            size = conn.execute(
                sqlalchemy.text("SELECT pg_database_size('mecanico_edge_bench')")
            ).scalar_one()
        r["disk_mb"] = round(int(size) / 1e6, 2)
        r["vector"] = bench_vectors_pg(args.pg_url)
        results["postgresql_pgvector"] = r
    except Exception as exc:  # sin postgres local: NUNCA se inventan números
        results["postgresql_pgvector"] = {
            "error": f"{type(exc).__name__}: {exc}",
            "nota": "ejecutar con el perfil docker edge-postgres (Mac) — sin resultados sintéticos",
        }

    args.out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
