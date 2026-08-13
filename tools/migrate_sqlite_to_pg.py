"""Migración controlada de datos SQLite (legacy) → PostgreSQL + pgvector (F12 §24).

Copia tabla a tabla en orden de dependencias, por lotes, con verificación de conteos.
No transforma semántica: el modelo lógico es el MISMO en ambos motores; lo único que
cambia es el motor y la ubicación en schemas lógicos.

Idempotencia: se puede reejecutar; las filas ya presentes (misma PK) se omiten con
``ON CONFLICT DO NOTHING`` en PostgreSQL.

Uso:
    python tools/migrate_sqlite_to_pg.py --sqlite edge.sqlite3 [--pg-url ...] [--batch 1000]
"""

import argparse
import json
from pathlib import Path
from typing import Any

from sqlalchemy import insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session as OrmSession

from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.store import EdgeStore

#: Orden de copia: respeta las claves ajenas (padres antes que hijos).
ORDER: list[type] = [
    dbs.SessionRow,
    dbs.ObservationRow,
    dbs.PointRow,
    dbs.WindowRow,
    dbs.FeatureVectorRow,
    dbs.EventRow,
    dbs.EventFeatureRow,
    dbs.EventBaselineRow,
    dbs.SnapshotRow,
    dbs.SnapshotEventLinkRow,
    dbs.InferenceRow,
    dbs.AnomalyRow,
    dbs.CaseRow,
    dbs.HypothesisRow,
    dbs.EvidenceRow,
    dbs.ProvenanceRow,
    dbs.CaseMemoryRow,
    dbs.LearnedPatternRow,
    dbs.PatternRelationRow,
    dbs.FeedbackRow,
    dbs.MaintenanceRow,
    dbs.AgentRunRow,
    dbs.AgentStepRow,
    dbs.RetrievalRow,
    dbs.KnowledgeDocumentRow,
    dbs.KnowledgeChunkRow,
    dbs.OutboxRow,
]


def _row_dict(row: Any, row_cls: type) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for col in row_cls.__table__.columns:
        value = getattr(row, col.key)
        # SQLite guarda los embeddings como JSON; PostgreSQL espera lista para vector(N)
        if col.key.startswith("embedding") and isinstance(value, str):
            value = json.loads(value)
        out[col.key] = value
    return out


def migrate(sqlite_path: Path, pg_url: str | None = None, batch: int = 1000) -> dict[str, Any]:
    src = EdgeStore(db_path=sqlite_path, migrate=False)
    dst = EdgeStore(url=pg_url) if pg_url else EdgeStore()
    report: dict[str, Any] = {"tables": {}, "ok": True}
    for row_cls in ORDER:
        with OrmSession(src.engine) as s_src:
            rows = list(s_src.execute(select(row_cls)).scalars().all())
            payload = [_row_dict(r, row_cls) for r in rows]
        copied = 0
        if payload:
            with OrmSession(dst.engine) as s_dst:
                for i in range(0, len(payload), batch):
                    chunk = payload[i : i + batch]
                    stmt = (
                        pg_insert(row_cls).on_conflict_do_nothing()
                        if dst.is_postgres
                        else insert(row_cls)
                    )
                    s_dst.execute(stmt, chunk)
                    copied += len(chunk)
                s_dst.commit()
        dst_count = dst.count(row_cls)
        entry = {"source": len(payload), "copied": copied, "destination": dst_count}
        entry["match"] = dst_count >= len(payload)
        report["tables"][row_cls.__tablename__] = entry
        report["ok"] = report["ok"] and bool(entry["match"])
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sqlite", type=Path, required=True)
    ap.add_argument("--pg-url", default=None)
    ap.add_argument("--batch", type=int, default=1000)
    args = ap.parse_args()
    report = migrate(args.sqlite, args.pg_url, args.batch)
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
