"""Acceso a la base del edge. **PostgreSQL + pgvector es la plataforma oficial** (ADR-0030).

- Motor por defecto: PostgreSQL (URL en ``MECANICO_DB_URL``; ver ``DEFAULT_PG_URL``).
- SQLite queda como **LEGACY / TEST COMPATIBILITY**: sigue funcionando (los schemas
  lógicos se aplanan con ``schema_translate_map``) para tests rápidos y para el corte
  controlado, y se retirará cuando se cumplan las condiciones del informe de F12.
- Migraciones: **Alembic** es el mecanismo oficial en PostgreSQL (``make db-upgrade``).
  ``migrate()`` (create_all + particiones) se conserva para tests y arranque en seco;
  ``PRAGMA user_version`` solo aplica al camino SQLite.
- Pool CONSERVADOR por defecto (Raspberry Pi): 5 conexiones, sin overflow agresivo.
"""

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session as OrmSession

from diagnostic_agent.storage.partitions import ensure_partitions
from diagnostic_agent.storage.schema import SCHEMA_DB_VERSION, SCHEMAS, Base

#: URL por defecto del edge (sobrescribible con MECANICO_DB_URL).
DEFAULT_PG_URL = "postgresql+psycopg://mecanico:mecanico@localhost:15432/mecanico_edge"

#: SQLite legacy: todos los schemas lógicos se aplanan a la única base del fichero.
SQLITE_SCHEMA_MAP: dict[str, None] = dict.fromkeys(SCHEMAS)

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


def _to_row_dict(row_cls: Any, contract: BaseModel, **extra: Any) -> dict[str, Any]:
    """Como _to_row pero devuelve el dict de columnas (para INSERT por lotes)."""
    from datetime import datetime as _dt

    from sqlalchemy import DateTime as SaDateTime

    data = json.loads(contract.model_dump_json())
    data.update(extra)
    if "metadata" in data:
        data["meta"] = data.pop("metadata")
    out: dict[str, Any] = {}
    for col in row_cls.__table__.columns:
        if col.key not in data:
            continue
        value = data[col.key]
        if isinstance(col.type, SaDateTime) and isinstance(value, str):
            value = _dt.fromisoformat(value)
        out[col.key] = value
    return out


def _to_contract(model_cls: type[M], row: Any) -> M:
    """Reconstruye el contrato desde la fila (ignora columnas ajenas al contrato)."""
    data = {c.key: getattr(row, c.key) for c in row.__table__.columns}
    if "meta" in data:
        data["metadata"] = data.pop("meta")
    fields = set(model_cls.model_fields)
    return model_cls.model_validate({k: v for k, v in data.items() if k in fields})


class EdgeStore:
    """Acceso a la base del edge (PostgreSQL oficial; SQLite legacy).

    ``EdgeStore()`` sin argumentos → PostgreSQL de ``MECANICO_DB_URL``/``DEFAULT_PG_URL``.
    ``EdgeStore(db_path=...)`` → SQLite LEGACY (tests y compatibilidad).
    """

    def __init__(
        self,
        db_path: str | Path | None = None,
        url: str | None = None,
        *,
        pool_size: int = 5,
        max_overflow: int = 2,
        migrate: bool = True,
    ) -> None:
        if db_path is not None:
            path = Path(db_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            engine = create_engine(f"sqlite:///{path}")
            self._is_sqlite = True
        else:
            url = url or os.environ.get("MECANICO_DB_URL", DEFAULT_PG_URL)
            self._is_sqlite = url.startswith("sqlite")
            engine = (
                create_engine(url)
                if self._is_sqlite
                # pool conservador: el edge es una Raspberry Pi, no un servidor.
                else create_engine(url, pool_size=pool_size, max_overflow=max_overflow)
            )
        self.engine = (
            engine.execution_options(schema_translate_map=SQLITE_SCHEMA_MAP)
            if self._is_sqlite
            else engine
        )
        if migrate:
            self.migrate()

    @property
    def is_postgres(self) -> bool:
        return not self._is_sqlite

    # ------------------------------------------------------------- migración
    def migrate(self) -> int:
        """Crea schemas/extensión/tablas/particiones ausentes y sella la versión física.

        En despliegue real el camino oficial es Alembic (``make db-upgrade``); esta
        función es idempotente y sirve para tests y para arrancar en seco.
        """
        with self.engine.connect() as conn:
            if self._is_sqlite:
                current = conn.execute(text("PRAGMA user_version")).scalar() or 0
                if current > SCHEMA_DB_VERSION:
                    msg = f"BD con esquema {current} más nuevo que el runtime ({SCHEMA_DB_VERSION})"
                    raise RuntimeError(msg)
            else:
                for schema in SCHEMAS:
                    conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
            Base.metadata.create_all(conn)
            if self._is_sqlite:
                conn.execute(text(f"PRAGMA user_version = {SCHEMA_DB_VERSION}"))
            conn.commit()
        if not self._is_sqlite:
            ensure_partitions(self.engine)
        return SCHEMA_DB_VERSION

    # ------------------------------------------------- transacciones y outbox
    @contextmanager
    def transaction(self) -> Iterator[OrmSession]:
        """Unidad de trabajo: escritura de negocio + outbox en la MISMA transacción.

        Base de la sincronización idempotente (F12 §33/§42): si el commit falla, no queda
        ni el hecho ni su sobre de sincronización — nunca uno sin el otro.
        """
        session = OrmSession(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def add_with_outbox(
        self,
        row_cls: type,
        contract: BaseModel,
        *,
        entity: str,
        entity_id: str,
        priority: int = 5,
        **extra: Any,
    ) -> None:
        """Escribe la entidad y su sobre de outbox atómicamente (F12 §33)."""
        import hashlib
        import uuid
        from datetime import UTC, datetime

        from diagnostic_agent.storage import schema as dbs

        payload = json.loads(contract.model_dump_json())
        checksum = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        with self.transaction() as s:
            s.add(_to_row(row_cls, contract, **extra))
            s.add(
                dbs.OutboxRow(
                    envelope_id=str(uuid.uuid4()),
                    entity=entity,
                    entity_id=entity_id,
                    priority=priority,
                    payload=payload,
                    checksum=checksum,
                    created_at=datetime.now(UTC),
                    attempts=0,
                )
            )

    # ------------------------------------------------------------ operaciones
    def add(self, row_cls: type, contract: BaseModel, **extra: Any) -> None:
        with OrmSession(self.engine) as s:
            s.add(_to_row(row_cls, contract, **extra))
            s.commit()

    def add_all(self, row_cls: type, contracts: list[BaseModel], **extra: Any) -> None:
        with OrmSession(self.engine) as s:
            s.add_all(_to_row(row_cls, c, **extra) for c in contracts)
            s.commit()

    def bulk_insert(self, row_cls: type, contracts: list[BaseModel], **extra: Any) -> None:
        """Inserción por lotes vía core INSERT (camino rápido para snapshots, F11 §26)."""
        if not contracts:
            return
        from sqlalchemy import insert

        rows = [_to_row_dict(row_cls, c, **extra) for c in contracts]
        with OrmSession(self.engine) as s:
            s.execute(insert(row_cls), rows)
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


#: Alias LEGACY del nombre histórico (F3-F11). Se conserva para no romper scripts y
#: experimentos ya registrados; el nombre oficial desde F12 es ``EdgeStore``.
EdgeStoreV2 = EdgeStore
