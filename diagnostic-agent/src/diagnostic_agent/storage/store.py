"""Repositorio del edge sobre el esquema v2 + migración mínima versionada.

Migración: ``PRAGMA user_version`` marca la versión física; ``migrate()`` crea las tablas
que falten y sella la versión. Al ser SQLite embebido de un solo escritor, el mecanismo
formal (alembic) se pospone hasta que exista un despliegue con datos que conservar
(documentado en docs/data-architecture/03).
"""

import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session as OrmSession

from diagnostic_agent.storage.schema import SCHEMA_DB_VERSION, Base

M = TypeVar("M", bound=BaseModel)


def _to_row(row_cls: Any, contract: BaseModel, **extra: Any) -> Any:
    """Mapea un contrato Pydantic a su fila (nombres de campo idénticos por convención).

    Serializa en modo JSON (los dicts anidados quedan JSON-compatibles para columnas
    JSON) y reconstruye ``datetime`` para las columnas DateTime del esquema.
    """
    from datetime import datetime as _dt

    from sqlalchemy import DateTime as SaDateTime

    data = json.loads(contract.model_dump_json())
    data.update(extra)
    if "metadata" in data:  # SQLAlchemy reserva 'metadata'
        data["meta"] = data.pop("metadata")
    out: dict[str, Any] = {}
    for col in row_cls.__table__.columns:
        if col.key not in data:
            continue
        value = data[col.key]
        if isinstance(col.type, SaDateTime) and isinstance(value, str):
            value = _dt.fromisoformat(value)
        out[col.key] = value
    return row_cls(**out)


def _to_contract(model_cls: type[M], row: Any) -> M:
    """Reconstruye el contrato desde la fila (ignora columnas ajenas al contrato)."""
    data = {c.key: getattr(row, c.key) for c in row.__table__.columns}
    if "meta" in data:
        data["metadata"] = data.pop("meta")
    fields = set(model_cls.model_fields)
    return model_cls.model_validate({k: v for k, v in data.items() if k in fields})


class EdgeStoreV2:
    """Acceso a la base local del edge (esquema v2)."""

    def __init__(self, db_path: str | Path) -> None:
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{path}")
        self.migrate()

    # ------------------------------------------------------------- migración
    def migrate(self) -> int:
        """Crea tablas ausentes y sella ``user_version``; devuelve la versión final."""
        with self.engine.connect() as conn:
            current = conn.execute(text("PRAGMA user_version")).scalar() or 0
            if current > SCHEMA_DB_VERSION:
                msg = f"BD con esquema {current} más nuevo que el runtime ({SCHEMA_DB_VERSION})"
                raise RuntimeError(msg)
            Base.metadata.create_all(conn)
            conn.execute(text(f"PRAGMA user_version = {SCHEMA_DB_VERSION}"))
            conn.commit()
        return SCHEMA_DB_VERSION

    # ------------------------------------------------------------ operaciones
    def add(self, row_cls: type, contract: BaseModel, **extra: Any) -> None:
        with OrmSession(self.engine) as s:
            s.add(_to_row(row_cls, contract, **extra))
            s.commit()

    def add_all(self, row_cls: type, contracts: list[BaseModel], **extra: Any) -> None:
        with OrmSession(self.engine) as s:
            s.add_all(_to_row(row_cls, c, **extra) for c in contracts)
            s.commit()

    def get(self, model_cls: type[M], row_cls: type, **filters: Any) -> M | None:
        with OrmSession(self.engine) as s:
            row = s.execute(select(row_cls).filter_by(**filters)).scalars().first()
            return _to_contract(model_cls, row) if row else None

    def list_(
        self, model_cls: type[M], row_cls: type, limit: int = 1000, **filters: Any
    ) -> list[M]:
        with OrmSession(self.engine) as s:
            rows: Any = s.execute(select(row_cls).filter_by(**filters).limit(limit)).scalars().all()
            return [_to_contract(model_cls, r) for r in rows]

    def count(self, row_cls: type, **filters: Any) -> int:
        from sqlalchemy import func

        with OrmSession(self.engine) as s:
            q = select(func.count()).select_from(row_cls)
            if filters:
                q = q.filter_by(**filters)
            return int(s.execute(q).scalar_one())

    def raw_rows(self, row_cls: type, **filters: Any) -> list[Any]:
        """Filas ORM desacopladas (para consultas de trazabilidad ad hoc)."""
        with OrmSession(self.engine) as s:
            rows: list[Any] = list(s.execute(select(row_cls).filter_by(**filters)).scalars().all())
            s.expunge_all()
            return rows
