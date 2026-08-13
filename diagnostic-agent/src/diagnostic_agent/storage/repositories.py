"""Repositorios del edge — el runtime trabaja SIEMPRE contra estas interfaces (F12 §21).

Regla de seguridad (F12 §20): el agente nunca ejecuta SQL arbitrario generado por el LLM.
La cadena es ``Agent → Tool (entradas/salidas tipadas) → Repository → PostgreSQL``; los
repositorios son la ÚNICA frontera con el motor y no aceptan SQL del exterior.

Implementación oficial: **PostgreSQL + pgvector** (ADR-0030). Los alias ``SQLite*`` se
conservan clasificados LEGACY / TEST COMPATIBILITY hasta cumplir las condiciones de
retirada del informe de F12: el mismo código sirve a ambos motores porque la diferencia
se resuelve en el esquema (tipo ``Embedding``) y en la consulta vectorial.
"""

from collections.abc import Sequence
from datetime import datetime
from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy.sql.elements import ColumnElement

from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.store import EdgeStore, _to_contract
from mecanico_contracts import (
    AgentRun,
    AgentStep,
    CaseMemory,
    DetectedAnomaly,
    DiagnosticCase,
    EventFeatureVector,
    KnowledgeChunk,
    LearnedPattern,
    ModelInference,
    SnapshotEventLink,
    VehicleEvent,
    VehicleTelemetrySnapshot,
)

Vector = Sequence[float]


# --------------------------------------------------------------------- protocolos


class TelemetryRepository(Protocol):
    """Persistencia y consulta de snapshots (batch primero, F12 §9)."""

    def add_snapshots(self, snapshots: list[VehicleTelemetrySnapshot]) -> None: ...

    def add_event_links(self, links: list[SnapshotEventLink]) -> None: ...

    def by_session(self, session_id: str) -> list[VehicleTelemetrySnapshot]: ...

    def by_vehicle_range(
        self, vehicle_id: str, t_from: datetime, t_to: datetime
    ) -> list[VehicleTelemetrySnapshot]: ...

    def by_event_type(
        self, vehicle_id: str, event_type: str, t_from: datetime, t_to: datetime
    ) -> list[VehicleTelemetrySnapshot]: ...


class EventRepository(Protocol):
    def add_events(self, events: list[VehicleEvent]) -> None: ...

    def add_event_features(self, features: list[EventFeatureVector]) -> None: ...

    def events_by_session(self, session_id: str) -> list[VehicleEvent]: ...


class DiagnosticRepository(Protocol):
    def add_anomaly(self, anomaly: DetectedAnomaly) -> None: ...

    def add_case(self, case: DiagnosticCase) -> None: ...

    def anomalies_by_session(self, session_id: str) -> list[DetectedAnomaly]: ...


class MemoryRepository(Protocol):
    def add_case(self, case: CaseMemory, embedding: Vector | None = None) -> None: ...

    def cases_by_vehicle(self, vehicle_id: str) -> list[CaseMemory]: ...

    def similar_cases(
        self, embedding: Vector, k: int = 5, **filters: Any
    ) -> list[tuple[CaseMemory, float]]: ...

    def add_pattern(self, pattern: LearnedPattern, embedding: Vector | None = None) -> None: ...

    def similar_patterns(
        self, embedding: Vector, k: int = 5, **filters: Any
    ) -> list[tuple[LearnedPattern, float]]: ...


class KnowledgeRepository(Protocol):
    def chunks(self) -> list[KnowledgeChunk]: ...

    def add_chunk(self, chunk: KnowledgeChunk, embedding: Vector | None = None) -> None: ...

    def search(
        self, embedding: Vector, k: int = 5, **filters: Any
    ) -> list[tuple[KnowledgeChunk, float]]: ...


class AgentRunRepository(Protocol):
    def add_run(self, run: AgentRun) -> None: ...

    def add_step(self, step: AgentStep) -> None: ...

    def steps_of(self, run_id: str) -> list[AgentStep]: ...


class ModelRepository(Protocol):
    def add_inference(self, inference: ModelInference) -> None: ...

    def inferences_by_session(self, session_id: str) -> list[ModelInference]: ...


# ------------------------------------------------------------------ implementación


class _Base:
    def __init__(self, store: EdgeStore) -> None:
        self.store = store

    @property
    def _pg(self) -> bool:
        return self.store.is_postgres


class PostgresTelemetryRepository(_Base):
    """Implementación OFICIAL de telemetría (PostgreSQL + pgvector, ADR-0030)."""

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

    def snapshots_of_event(self, event_id: str) -> list[VehicleTelemetrySnapshot]:
        """Consulta de diagnóstico: snapshots de UN evento por la relación N:M."""
        with OrmSession(self.store.engine) as s:
            rows = (
                s.execute(
                    select(dbs.SnapshotRow)
                    .join(
                        dbs.SnapshotEventLinkRow,
                        dbs.SnapshotEventLinkRow.snapshot_id == dbs.SnapshotRow.snapshot_id,
                    )
                    .where(dbs.SnapshotEventLinkRow.event_id == event_id)
                    .order_by(dbs.SnapshotRow.timestamp_utc)
                )
                .scalars()
                .all()
            )
            return [_to_contract(VehicleTelemetrySnapshot, r) for r in rows]

    def _range_query(
        self, condition: ColumnElement[bool], t_from: datetime, t_to: datetime
    ) -> list[VehicleTelemetrySnapshot]:
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


class PostgresEventRepository(_Base):
    def add_events(self, events: list[VehicleEvent]) -> None:
        self.store.add_all(dbs.EventRow, list(events))

    def add_event_features(self, features: list[EventFeatureVector]) -> None:
        self.store.add_all(dbs.EventFeatureRow, list(features))

    def events_by_session(self, session_id: str) -> list[VehicleEvent]:
        return self.store.list_(VehicleEvent, dbs.EventRow, limit=100_000, session_id=session_id)


class PostgresDiagnosticRepository(_Base):
    def add_anomaly(self, anomaly: DetectedAnomaly) -> None:
        self.store.add(dbs.AnomalyRow, anomaly)

    def add_case(self, case: DiagnosticCase) -> None:
        self.store.add(dbs.CaseRow, case)

    def anomalies_by_session(self, session_id: str) -> list[DetectedAnomaly]:
        return self.store.list_(
            DetectedAnomaly, dbs.AnomalyRow, limit=100_000, session_id=session_id
        )


def _cosine_distance(a: Vector, b: Vector) -> float:
    num = sum(x * y for x, y in zip(a, b, strict=False))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return 1.0 - (num / (na * nb)) if na and nb else 1.0


class _VectorMixin(_Base):
    """Búsqueda vectorial con FILTRADO relacional en la MISMA consulta (F12 §15).

    PostgreSQL: ``WHERE <filtros> ORDER BY embedding <=> :q LIMIT k`` — exactamente la
    ventaja que motivó la adopción. Estrategia inicial: búsqueda EXACTA sin índice;
    HNSW/IVFFlat solo cuando el volumen lo justifique (F12 §14, no optimizar antes).
    SQLite legacy: misma semántica con coseno en proceso sobre las filas ya filtradas.
    """

    def _vector_search(
        self,
        row_cls: Any,
        model_cls: Any,
        embedding: Vector,
        k: int,
        filters: dict[str, Any],
    ) -> list[tuple[Any, float]]:
        conds = [
            getattr(row_cls, key) == value for key, value in filters.items() if value is not None
        ]
        with OrmSession(self.store.engine) as s:
            if self._pg:
                distance = row_cls.embedding.cosine_distance(list(embedding))
                stmt = select(row_cls, distance.label("d")).where(row_cls.embedding.isnot(None))
                for c in conds:
                    stmt = stmt.where(c)
                rows = s.execute(stmt.order_by(distance).limit(k)).all()
                return [(_to_contract(model_cls, r[0]), float(r[1])) for r in rows]
            stmt2 = select(row_cls).where(row_cls.embedding.isnot(None))
            for c in conds:
                stmt2 = stmt2.where(c)
            scored = [
                (_to_contract(model_cls, row), _cosine_distance(embedding, row.embedding))
                for row in s.execute(stmt2).scalars().all()
            ]
            scored.sort(key=lambda t: t[1])
            return scored[:k]


class PostgresMemoryRepository(_VectorMixin):
    """Memoria episódica y evolutiva con embeddings en la MISMA base (F12 §16/§17)."""

    def add_case(self, case: CaseMemory, embedding: Vector | None = None) -> None:
        extra: dict[str, Any] = {"embedding": list(embedding)} if embedding is not None else {}
        self.store.add(dbs.CaseMemoryRow, case, **extra)

    def cases_by_vehicle(self, vehicle_id: str) -> list[CaseMemory]:
        return self.store.list_(CaseMemory, dbs.CaseMemoryRow, vehicle_id=vehicle_id)

    def similar_cases(
        self, embedding: Vector, k: int = 5, **filters: Any
    ) -> list[tuple[CaseMemory, float]]:
        return self._vector_search(dbs.CaseMemoryRow, CaseMemory, embedding, k, filters)

    def add_pattern(self, pattern: LearnedPattern, embedding: Vector | None = None) -> None:
        extra: dict[str, Any] = {"embedding": list(embedding)} if embedding is not None else {}
        self.store.add(dbs.LearnedPatternRow, pattern, **extra)

    def similar_patterns(
        self, embedding: Vector, k: int = 5, **filters: Any
    ) -> list[tuple[LearnedPattern, float]]:
        return self._vector_search(dbs.LearnedPatternRow, LearnedPattern, embedding, k, filters)


class PostgresKnowledgeRepository(_VectorMixin):
    """RAG local directamente sobre PostgreSQL + pgvector — sin segunda base vectorial."""

    def chunks(self) -> list[KnowledgeChunk]:
        return self.store.list_(KnowledgeChunk, dbs.KnowledgeChunkRow, limit=100_000)

    def add_chunk(self, chunk: KnowledgeChunk, embedding: Vector | None = None) -> None:
        extra: dict[str, Any] = {"embedding": list(embedding)} if embedding is not None else {}
        self.store.add(dbs.KnowledgeChunkRow, chunk, **extra)

    def search(
        self, embedding: Vector, k: int = 5, **filters: Any
    ) -> list[tuple[KnowledgeChunk, float]]:
        return self._vector_search(dbs.KnowledgeChunkRow, KnowledgeChunk, embedding, k, filters)


class PostgresAgentRunRepository(_Base):
    def add_run(self, run: AgentRun) -> None:
        self.store.add(dbs.AgentRunRow, run)

    def add_step(self, step: AgentStep) -> None:
        self.store.add(dbs.AgentStepRow, step)

    def steps_of(self, run_id: str) -> list[AgentStep]:
        return self.store.list_(AgentStep, dbs.AgentStepRow, limit=10_000, run_id=run_id)


class PostgresModelRepository(_Base):
    def add_inference(self, inference: ModelInference) -> None:
        self.store.add(dbs.InferenceRow, inference)

    def inferences_by_session(self, session_id: str) -> list[ModelInference]:
        return self.store.list_(
            ModelInference, dbs.InferenceRow, limit=100_000, session_id=session_id
        )


# ------------------------------------------------- LEGACY / TEST COMPATIBILITY
# El mismo código atiende el camino SQLite (schemas aplanados + embeddings en JSON).
# Estos alias existen para no romper scripts/experimentos previos y se retirarán con
# SQLite cuando se cumplan las condiciones del informe de F12.

SQLiteTelemetryRepository = PostgresTelemetryRepository
SQLiteMemoryRepository = PostgresMemoryRepository
SQLiteKnowledgeRepository = PostgresKnowledgeRepository
SQLiteAgentRunRepository = PostgresAgentRunRepository
