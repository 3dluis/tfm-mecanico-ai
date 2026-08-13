"""Ingesta por lotes y persistencia asíncrona (F12 §9/§10).

Problema: la adquisición OBD/IMU produce muestras continuamente y **no debe bloquearse**
esperando a la base. Además, un COMMIT por PID sería absurdo (una transacción por lectura).

Diseño:

```
Acquisition → Queue (acotada) → PersistenceWorker (hilo) → lote → PostgreSQL
```

- **Lote por tamaño o por tiempo**: lo que ocurra antes (``batch_size`` / ``flush_interval_s``).
- **Cola acotada** con política de contrapresión explícita:
  - ``BLOCK`` (por defecto): el productor espera — prioriza no perder datos.
  - ``DROP_OLDEST``: descarta lo más antiguo y CUENTA lo descartado — prioriza no
    congelar la adquisición. Nunca se descarta en silencio: ``dropped`` es observable.
- Un fallo temporal de persistencia **no detiene la adquisición**: el lote se reintenta con
  backoff acotado y, si se agota, se contabiliza en ``failed`` (visible en las métricas).

Escritura: ``executemany`` por defecto (SQLAlchemy core INSERT, portable y suficiente) y
``COPY`` opcional en PostgreSQL para lotes grandes — se MIDE cuál conviene (F12 §9), no se
presupone.
"""

import queue
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from diagnostic_agent.storage.store import EdgeStore, _to_row_dict


class Backpressure(StrEnum):
    BLOCK = "block"
    DROP_OLDEST = "drop_oldest"


@dataclass
class IngestStats:
    enqueued: int = 0
    written: int = 0
    batches: int = 0
    dropped: int = 0
    failed: int = 0
    last_batch_rows: int = 0
    last_write_ms: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "enqueued": self.enqueued,
            "written": self.written,
            "batches": self.batches,
            "dropped": self.dropped,
            "failed": self.failed,
            "last_batch_rows": self.last_batch_rows,
            "last_write_ms": round(self.last_write_ms, 2),
        }


def copy_rows(store: EdgeStore, row_cls: type, contracts: list[BaseModel]) -> int:
    """Inserción por lotes con COPY (PostgreSQL). Cae a executemany en SQLite legacy."""
    if not contracts:
        return 0
    if not store.is_postgres:
        store.bulk_insert(row_cls, contracts)
        return len(contracts)
    import json as _json

    rows = [_to_row_dict(row_cls, c) for c in contracts]
    sa_table: Any = row_cls.__table__  # type: ignore[attr-defined]
    cols = [c.key for c in sa_table.columns if c.key in rows[0]]
    table = f"{sa_table.schema}.{sa_table.name}"
    raw = store.engine.raw_connection()
    try:
        with raw.cursor() as cur:  # type: ignore[attr-defined]
            stmt = f"COPY {table} ({', '.join(cols)}) FROM STDIN"
            with cur.copy(stmt) as cp:
                for r in rows:
                    cp.write_row(
                        [_json.dumps(r[c]) if isinstance(r[c], dict | list) else r[c] for c in cols]
                    )
        raw.commit()
    finally:
        raw.close()
    return len(rows)


@dataclass
class PersistenceWorker:
    """Consumidor en hilo: agrupa contratos por tipo de fila y escribe por lotes."""

    store: EdgeStore
    batch_size: int = 500
    flush_interval_s: float = 2.0
    max_queue: int = 20_000
    backpressure: Backpressure = Backpressure.BLOCK
    max_retries: int = 3
    use_copy: bool = False
    stats: IngestStats = field(default_factory=IngestStats)
    _q: queue.Queue[tuple[type, BaseModel] | None] = field(init=False)
    _thread: threading.Thread | None = field(default=None, init=False)
    _stop: threading.Event = field(default_factory=threading.Event, init=False)

    def __post_init__(self) -> None:
        self._q = queue.Queue(maxsize=self.max_queue)

    # ------------------------------------------------------------- ciclo de vida
    def start(self) -> None:
        if self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="persistence-worker", daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 10.0) -> None:
        if self._thread is None:
            return
        self._q.put(None)
        self._stop.set()
        self._thread.join(timeout)
        self._thread = None

    def __enter__(self) -> "PersistenceWorker":
        self.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.stop()

    # ------------------------------------------------------------------ productor
    def submit(self, row_cls: type, contract: BaseModel) -> bool:
        """Encola un contrato. Devuelve False si se descartó (política DROP_OLDEST)."""
        item = (row_cls, contract)
        if self.backpressure is Backpressure.BLOCK:
            self._q.put(item)
            self.stats.enqueued += 1
            return True
        try:
            self._q.put_nowait(item)
        except queue.Full:
            try:
                self._q.get_nowait()  # descarta lo más antiguo, contabilizado
                self.stats.dropped += 1
            except queue.Empty:  # pragma: no cover - carrera improbable
                pass
            try:
                self._q.put_nowait(item)
            except queue.Full:  # pragma: no cover
                self.stats.dropped += 1
                return False
        self.stats.enqueued += 1
        return True

    def submit_many(self, row_cls: type, contracts: list[BaseModel]) -> int:
        return sum(1 for c in contracts if self.submit(row_cls, c))

    # ------------------------------------------------------------------ consumidor
    def _run(self) -> None:
        buffer: dict[type, list[BaseModel]] = {}
        pending = 0
        last_flush = time.monotonic()
        while True:
            timeout = max(0.05, self.flush_interval_s - (time.monotonic() - last_flush))
            try:
                item = self._q.get(timeout=timeout)
            except queue.Empty:
                item = None if self._stop.is_set() and pending == 0 else ()  # type: ignore[assignment]
            if item is None:  # señal de parada: vaciar y salir
                self._flush(buffer)
                return
            if item:
                row_cls, contract = item
                buffer.setdefault(row_cls, []).append(contract)
                pending += 1
            if pending >= self.batch_size or (
                pending and time.monotonic() - last_flush >= self.flush_interval_s
            ):
                self._flush(buffer)
                buffer, pending = {}, 0
                last_flush = time.monotonic()

    def _flush(self, buffer: dict[type, list[BaseModel]]) -> None:
        def write_copy(rc: type, cs: list[BaseModel]) -> Any:
            return copy_rows(self.store, rc, cs)

        writer: Callable[[type, list[BaseModel]], Any] = (
            write_copy if self.use_copy else self.store.bulk_insert
        )
        for row_cls, contracts in buffer.items():
            if not contracts:
                continue
            for attempt in range(self.max_retries):
                try:
                    t0 = time.perf_counter()
                    writer(row_cls, contracts)
                    self.stats.last_write_ms = (time.perf_counter() - t0) * 1000
                    self.stats.written += len(contracts)
                    self.stats.batches += 1
                    self.stats.last_batch_rows = len(contracts)
                    break
                except Exception:
                    if attempt == self.max_retries - 1:
                        self.stats.failed += len(contracts)
                    else:
                        time.sleep(0.2 * (2**attempt))
        buffer.clear()
