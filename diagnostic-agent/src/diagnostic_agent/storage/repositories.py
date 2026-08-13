"""Repositorios abstractos del edge (F11 §36) — el runtime trabaja contra interfaces.

La lógica del agente NO depende de SQLite ni de PostgreSQL: depende de estos protocolos.
Implementaciones: ``SQLite*Repository`` (vigentes, sobre EdgeStoreV2) y
``PostgresTelemetryRepository`` (experimental, para el benchmark de
docs/data-architecture/12 — misma semántica, motor distinto). El modelo LÓGICO es único
y mapeable a Edge y Cloud sin cambiar semántica (F11 §38); la sincronización sigue
siendo el protocolo lógico Outbox→API→Cloud (idempotencia + schema_version + provenance,
docs/data-architecture/09) — NUNCA replicación física, ni siquiera Postgres→Postgres.
"""

from datetime import datetime
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.sql.elements import ColumnElement

from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.store import EdgeStoreV2
from mecanico_contracts import (
    AgentRun,
    AgentStep,
    CaseMemory,
    KnowledgeChunk,
    LearnedPattern,
    SnapshotEventLink,
    VehicleTelemetrySnapshot,
)


class TelemetryRepository(Protocol):
    """Persistencia y consulta de snapshots (batch primero, F11 §26)."""

    def add_snapshots(self, snapshots: list[VehicleTelemetrySnapshot]) -> None: ...

    def add_event_links(self, links: list[SnapshotEventLink]) -> None: ...

    def by_session(self, session_id: str) -> list[VehicleTelemetrySnapshot]: ...

    def by_vehicle_range(
        self, vehicle_id: str, t_from: datetime, t_to: datetime
    ) -> list[VehicleTelemetrySnapshot]: ...

    def by_event_type(
        self, vehicle_id: str, event_type: str, t_from: datetime, t_to: datetime
    ) -> list[VehicleTelemetrySnapshot]: ...


class MemoryRepository(Protocol):
    def add_case(self, case: CaseMemory) -> None: ...

    def cases_by_vehicle(self, vehicle_id: str) -> list[CaseMemory]: ...

    def add_pattern(self, pattern: LearnedPattern) -> None: ...


class KnowledgeRepository(Protocol):
    def chunks(self) -> list[KnowledgeChunk]: ...


class AgentRunRepository(Protocol):
    def add_run(self, run: AgentRun) -> None: ...

    def add_step(self, step: AgentStep) -> None: ...


class SQLiteTelemetryRepository:
    """Implementación vigente sobre EdgeStoreV2 (SQLite, esquema v4)."""

    def __init__(self, store: EdgeStoreV2) -> None:
        self.store = store

    def add_snapshots(self, snapshots: list[VehicleTelemetrySnapshot]) -> None:
        self.store.bulk_insert(dbs.SnapshotRow, list(snapshots))

    def add_event_links(self, links: list[SnapshotEventLink]) -> None:
        self.store.bulk_insert(dbs.SnapshotEventLinkRow, list(links))

    def by_session(self, session_id: str) -> list[VehicleTelemetrySnapshot]:
        return self.store.list_(
            VehicleTelemetrySnapshot, dbs.SnapshotRow, limit=1_000_000, session_id=session_id
        )

    def by_vehicle_range(
        self, vehicle_id: str, t_from: datetime, t_to: datetime
    ) -> list[VehicleTelemetrySnapshot]:
        return self._range_query(dbs.SnapshotRow.vehicle_id == vehicle_id, t_from, t_to)

    def by_event_type(
        self, vehicle_id: str, event_type: str, t_from: datetime, t_to: datetime
    ) -> list[VehicleTelemetrySnapshot]:
        return self._range_query(
            (dbs.SnapshotRow.vehicle_id == vehicle_id)
            & (dbs.SnapshotRow.primary_event_type == event_type),
            t_from,
            t_to,
        )

    def _range_query(
        self, condition: ColumnElement[bool], t_from: datetime, t_to: datetime
    ) -> list[VehicleTelemetrySnapshot]:
        from sqlalchemy.orm import Session as OrmSession

        from diagnostic_agent.storage.store import _to_contract

        with OrmSession(self.store.engine) as s:
            rows = (
                s.execute(
                    select(dbs.SnapshotRow)
                    .where(condition)
                    .where(dbs.SnapshotRow.timestamp_utc >= t_from)
                    .where(dbs.SnapshotRow.timestamp_utc <= t_to)
                    .order_by(dbs.SnapshotRow.timestamp_utc)
                )
                .scalars()
                .all()
            )
            return [_to_contract(VehicleTelemetrySnapshot, r) for r in rows]


class PostgresTelemetryRepository(SQLiteTelemetryRepository):
    """Misma semántica sobre PostgreSQL (F11 §36): construir con
    ``EdgeStoreV2(url="postgresql+psycopg://...")``. El nombre distinto existe para que
    el cableado del runtime declare explícitamente el motor elegido; el código es el
    mismo modelo lógico (los repositorios son la frontera, no el motor)."""


class SQLiteMemoryRepository:
    def __init__(self, store: EdgeStoreV2) -> None:
        self.store = store

    def add_case(self, case: CaseMemory) -> None:
        self.store.add(dbs.CaseMemoryRow, case)

    def cases_by_vehicle(self, vehicle_id: str) -> list[CaseMemory]:
        return self.store.list_(CaseMemory, dbs.CaseMemoryRow, vehicle_id=vehicle_id)

    def add_pattern(self, pattern: LearnedPattern) -> None:
        self.store.add(dbs.LearnedPatternRow, pattern)


class SQLiteKnowledgeRepository:
    def __init__(self, store: EdgeStoreV2) -> None:
        self.store = store

    def chunks(self) -> list[KnowledgeChunk]:
        return self.store.list_(KnowledgeChunk, dbs.KnowledgeChunkRow, limit=100_000)


class SQLiteAgentRunRepository:
    def __init__(self, store: EdgeStoreV2) -> None:
        self.store = store

    def add_run(self, run: AgentRun) -> None:
        self.store.add(dbs.AgentRunRow, run)

    def add_step(self, step: AgentStep) -> None:
        self.store.add(dbs.AgentStepRow, step)
