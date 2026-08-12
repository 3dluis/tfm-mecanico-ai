"""Capa de transporte plugable hacia el adaptador OBD-II (ADR-0004).

Tres variantes de configuración; todas terminan en una conexión python-OBD:
- ``serial``: ruta de dispositivo (pty del emulador o /dev/rfcomm0|ttyUSB0 en real).
- ``tcp``: ``socket://host:puerto`` (emulador en Docker). Requiere ``baudrate`` explícito
  para omitir la auto-detección de python-OBD, que falla sobre TCP (verificado en Fase 2;
  ver ADR-0004 §Nota de implementación).
- ``bluetooth-rfcomm``: especificada y NO implementada en el TFM (limitación L3): en
  Raspberry Pi OS, ``rfcomm bind`` reduce el caso a ``serial``.
"""

from dataclasses import dataclass

from mecanico_contracts import TransportKind

#: Baudrate ficticio para transporte TCP: solo desactiva el probe de python-OBD.
_TCP_FAKE_BAUDRATE = 38400


@dataclass(frozen=True)
class TransportConfig:
    """Parámetros de conexión resueltos para python-OBD."""

    kind: TransportKind
    portstr: str
    baudrate: int | None

    @classmethod
    def from_settings(
        cls, transport: str, serial_port: str, emulator_host: str, emulator_port: int
    ) -> "TransportConfig":
        """Construye la configuración desde los settings del agente."""
        kind = TransportKind(transport)
        if kind is TransportKind.SERIAL:
            if not serial_port:
                msg = "MECANICO_SERIAL_PORT es obligatorio con transport=serial"
                raise ValueError(msg)
            return cls(kind, serial_port, None)
        if kind is TransportKind.TCP:
            return cls(kind, f"socket://{emulator_host}:{emulator_port}", _TCP_FAKE_BAUDRATE)
        msg = (
            "transport=bluetooth-rfcomm no está implementado en el prototipo (L3): "
            "emparejar con BlueZ y usar transport=serial con /dev/rfcomm0"
        )
        raise NotImplementedError(msg)
