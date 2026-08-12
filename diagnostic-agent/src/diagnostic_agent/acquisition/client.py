"""Cliente de adquisición OBD-II: sondeo de PIDs a frecuencia configurable."""

import logging
import time
from collections.abc import Iterator
from datetime import UTC, datetime

import obd

from diagnostic_agent.acquisition.transport import TransportConfig
from mecanico_contracts import OBDReading
from mecanico_contracts.features import CANONICAL_PIDS

logger = logging.getLogger(__name__)


class AcquisitionClient:
    """Sondea el subconjunto canónico de PIDs y emite ``OBDReading`` validados."""

    def __init__(
        self,
        transport: TransportConfig,
        vehicle_id: str,
        device_id: str,
        pids: list[str] | None = None,
    ) -> None:
        self.transport = transport
        self.vehicle_id = vehicle_id
        self.device_id = device_id
        self.pids = pids or list(CANONICAL_PIDS)
        self._conn: obd.OBD | None = None

    # ------------------------------------------------------------------ ciclo
    def connect(self) -> bool:
        """Abre la conexión; devuelve True si el handshake ELM327 tuvo éxito."""
        kwargs: dict[str, object] = {"fast": False, "timeout": 2.0}
        if self.transport.baudrate is not None:
            kwargs["baudrate"] = self.transport.baudrate
        self._conn = obd.OBD(self.transport.portstr, **kwargs)
        ok = bool(self._conn.is_connected())
        logger.info(
            "OBD %s via %s (%s)",
            "conectado" if ok else "SIN conexión",
            self.transport.kind.value,
            self._conn.protocol_name() if ok else "-",
        )
        return ok

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # -------------------------------------------------------------------- poll
    def poll_once(self) -> list[OBDReading]:
        """Una pasada por todos los PIDs; omite (y registra) los que no respondan."""
        if self._conn is None:
            msg = "poll_once() sin conexión: llama a connect() primero"
            raise RuntimeError(msg)
        now = datetime.now(tz=UTC)
        out: list[OBDReading] = []
        for pid in self.pids:
            cmd = getattr(obd.commands, pid, None)
            if cmd is None:
                continue
            rsp = self._conn.query(cmd, force=True)
            if rsp is None or rsp.is_null():
                logger.debug("PID sin respuesta: %s", pid)
                continue
            value = rsp.value
            magnitude = float(value.magnitude) if hasattr(value, "magnitude") else float(value)
            out.append(
                OBDReading(
                    timestamp=now,
                    pid=pid,
                    value=magnitude,
                    unit=str(getattr(value, "units", "")) or "raw",
                    vehicle_id=self.vehicle_id,
                    device_id=self.device_id,
                    source=self.transport.kind,
                )
            )
        return out

    def stream(
        self, sample_rate_hz: float = 1.0, max_ticks: int | None = None
    ) -> Iterator[list[OBDReading]]:
        """Flujo de pasadas de sondeo a la frecuencia dada (compensando el coste del poll)."""
        period = 1.0 / sample_rate_hz
        ticks = 0
        while max_ticks is None or ticks < max_ticks:
            t0 = time.perf_counter()
            yield self.poll_once()
            ticks += 1
            elapsed = time.perf_counter() - t0
            if elapsed < period:
                time.sleep(period - elapsed)
