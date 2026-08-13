"""Observabilidad básica de PostgreSQL en el edge (F12 §38).

No es una plataforma DBA: son las métricas mínimas para dimensionar la Raspberry Pi y
detectar degradación — tamaño, filas, conexiones, latencia de consulta y de búsqueda
vectorial, tamaño de WAL y ratio de cache. Todo medido, nada estimado.
"""

import time
from typing import Any

from sqlalchemy import text

from diagnostic_agent.storage.store import EdgeStore

_SNAPSHOTS = "telemetry.vehicle_telemetry_snapshots"


def collect(store: EdgeStore, *, sample_vector: list[float] | None = None) -> dict[str, Any]:
    """Métricas puntuales de la base del edge."""
    out: dict[str, Any] = {"engine": "postgresql" if store.is_postgres else "sqlite-legacy"}
    if not store.is_postgres:
        return out
    with store.engine.connect() as conn:
        out["db_size_bytes"] = int(
            conn.execute(text("SELECT pg_database_size(current_database())")).scalar_one()
        )
        out["snapshot_rows"] = int(
            conn.execute(text(f"SELECT count(*) FROM {_SNAPSHOTS}")).scalar_one()
        )
        out["connections"] = int(
            conn.execute(
                text("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
            ).scalar_one()
        )
        out["wal_bytes"] = int(
            conn.execute(text("SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0')")).scalar_one()
        )
        hit, read = conn.execute(
            text(
                "SELECT coalesce(sum(blks_hit),0), coalesce(sum(blks_read),0) "
                "FROM pg_stat_database WHERE datname = current_database()"
            )
        ).one()
        total = int(hit) + int(read)
        out["cache_hit_ratio"] = round(int(hit) / total, 4) if total else None
        t0 = time.perf_counter()
        conn.execute(text(f"SELECT count(*) FROM {_SNAPSHOTS} WHERE timestamp_utc > now()"))
        out["query_latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        if sample_vector is not None:
            t0 = time.perf_counter()
            conn.execute(
                text(
                    "SELECT chunk_id FROM knowledge.knowledge_chunks "
                    "WHERE embedding IS NOT NULL ORDER BY embedding <=> :q LIMIT 5"
                ),
                {"q": str(list(sample_vector))},
            ).all()
            out["vector_query_latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return out
