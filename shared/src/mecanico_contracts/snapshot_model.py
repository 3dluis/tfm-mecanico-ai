"""VehicleTelemetrySnapshot — representación canónica HORIZONTAL de la telemetría (F11).

Clase de dato: **NORMALIZED WIDE / TIME-ALIGNED** (ADR-0025). Cada fila es el estado
multivariable observable del vehículo en un instante canónico. NO sustituye a
``OBDObservation`` (RAW LONG) ni a ``TelemetryPoint`` (NORMALIZED LONG): se deriva de
ellos y conserva la vuelta a las observaciones originales por (session_id,
sequence_number) + synchronization_version (ADR-0026).

Reglas duras:
- **NULL ≠ 0** (ADR-0027): una señal no disponible es ``None`` + quality flag
  (not_supported/not_polled/timeout/missing/invalid/stale), jamás 0.0.
- **Sin features**: rpm_mean_10s, correlaciones, std… pertenecen a FeatureVector/
  EventFeatureVector, nunca al snapshot (estado físico alineado ≠ cálculo derivado).
- ``quality_flags`` es COMPACTO: solo registra señales cuyo estado ≠ MEASURED (una fila
  con todas las señales medidas lleva el dict vacío).

Clasificación de campos (docs/data-architecture/11):
- OBD estándar (SAE J1979): rpm, vehicle_speed, throttle_position, engine_load,
  coolant_temperature, intake_air_temperature, maf, map_kpa, stft/ltft bank1/2,
  fuel_pressure, fuel_level, timing_advance, o2_sensor_1/2,
  commanded_equivalence_ratio, active_dtc_count, battery_voltage (control module
  voltage, PID 42).
- IMU (opcional; ADR-0020): acceleration_x/y/z, gyro_x/y/z.
- GPS (opcional, COULD; nunca obligatorio): gps_speed, gps_heading.
- Referencias/derivados de fila: primary_event_id/type y vehicle_state (referencias
  INFERRED denormalizadas para consulta rápida — la N:M completa vive en
  SnapshotEventLink), quality_score y missing_metric_count (metadatos de calidad).
"""

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from mecanico_contracts.models import ContractBase

#: Versión de la política de alineación temporal (ADR-0026). sync:v1 =
#: rejilla canónica de ``snapshot_interval_ms`` anclada al inicio de sesión; para cada
#: señal se toma la muestra más cercana dentro de ±``alignment_window_ms``; sin muestra
#: en ventana → None + flag 'missing'; muestra de la rejilla anterior reutilizada →
#: flag 'stale'. La frecuencia canónica NO está fijada: 1 Hz es la validada por la
#: adquisición actual; 5 Hz queda como candidato pendiente de validar (latencia ELM327,
#: nº de PIDs, hardware, almacenamiento).
SYNC_VERSION = "sync:v1"

#: PID canónico (nomenclatura python-OBD, ver ``features.CANONICAL_PIDS``) → campo del
#: snapshot. Es el mapeo ÚNICO entrenamiento↔inferencia↔persistencia: el snapshot builder
#: del edge (diagnostic_agent.telemetry.snapshots) y el camino wide de ML (ai_models.data)
#: deben usar exactamente esta correspondencia; su igualdad se verifica por test de
#: integración. Añadir un PID al ciclo de sondeo = añadir aquí su campo (cambio ADITIVO).
PID_TO_SNAPSHOT_FIELD: dict[str, str] = {
    "RPM": "rpm",
    "SPEED": "vehicle_speed",
    "THROTTLE_POS": "throttle_position",
    "ENGINE_LOAD": "engine_load",
    "COOLANT_TEMP": "coolant_temperature",
    "INTAKE_TEMP": "intake_air_temperature",
    "MAF": "maf",
    "INTAKE_PRESSURE": "map_kpa",
    "SHORT_FUEL_TRIM_1": "stft_bank1",
    "LONG_FUEL_TRIM_1": "ltft_bank1",
    "O2_B1S1": "o2_sensor_1",
    "TIMING_ADVANCE": "timing_advance",
}


class SignalQuality(StrEnum):
    """Estado de calidad por señal (solo se persisten los ≠ MEASURED)."""

    MEASURED = "measured"  # muestra real dentro de la ventana de alineación
    STALE = "stale"  # último valor reutilizado (fuera de ventana, dentro de tolerancia)
    NOT_SUPPORTED = "not_supported"  # el vehículo/ECU no expone el PID
    NOT_POLLED = "not_polled"  # soportado pero no incluido en el ciclo de sondeo
    TIMEOUT = "timeout"  # solicitado sin respuesta a tiempo
    MISSING = "missing"  # esperado y ausente en la ventana (pérdida puntual)
    INVALID = "invalid"  # respuesta fuera de rango físico / corrupta


class VehicleTelemetrySnapshot(ContractBase):
    """Estado multivariable del vehículo alineado a un instante canónico (WIDE)."""

    snapshot_id: str
    vehicle_id: str
    device_id: str
    session_id: str
    trip_id: str | None = Field(default=None, description="VehicleEvent TRIP contenedor")

    timestamp_utc: datetime = Field(description="Instante canónico (rejilla, UTC)")
    sequence_number: int = Field(ge=0, description="Índice en la rejilla de la sesión")
    snapshot_interval_ms: int = Field(gt=0, description="Paso de la rejilla (1000 = 1 Hz)")
    synchronization_version: str = Field(
        default=SYNC_VERSION, description="Política de alineación aplicada (ADR-0026)"
    )

    # --- referencias de contexto (denormalizadas para consulta; N:M en SnapshotEventLink)
    primary_event_id: str | None = Field(
        default=None, description="Evento hoja más específico activo en el instante"
    )
    primary_event_type: str | None = None
    vehicle_state: str | None = Field(
        default=None, description="Estado de la máquina de estados (OFF/IDLE/MOVING…)"
    )

    # --- OBD estándar (SAE J1979) — None = no disponible (ver quality_flags), NUNCA 0
    rpm: float | None = None
    vehicle_speed: float | None = Field(default=None, description="km/h")
    throttle_position: float | None = Field(default=None, description="%")
    engine_load: float | None = Field(default=None, description="%")
    coolant_temperature: float | None = Field(default=None, description="°C")
    intake_air_temperature: float | None = Field(default=None, description="°C")
    maf: float | None = Field(default=None, description="g/s")
    map_kpa: float | None = Field(default=None, description="kPa (nombre 'map' es builtin)")
    stft_bank1: float | None = Field(default=None, description="%")
    ltft_bank1: float | None = Field(default=None, description="%")
    stft_bank2: float | None = Field(default=None, description="% (motores 2 bancos)")
    ltft_bank2: float | None = None
    fuel_pressure: float | None = Field(default=None, description="kPa")
    fuel_level: float | None = Field(default=None, description="%")
    timing_advance: float | None = Field(default=None, description="° BTDC")
    battery_voltage: float | None = Field(default=None, description="V (PID 42)")
    o2_sensor_1: float | None = Field(default=None, description="V (B1S1)")
    o2_sensor_2: float | None = Field(default=None, description="V (B1S2)")
    commanded_equivalence_ratio: float | None = Field(default=None, description="λ (PID 44)")
    active_dtc_count: int | None = Field(default=None, ge=0)

    # --- IMU (opcional; simulada primero — ADR-0020)
    acceleration_x: float | None = Field(default=None, description="m/s²")
    acceleration_y: float | None = None
    acceleration_z: float | None = None
    gyro_x: float | None = Field(default=None, description="°/s")
    gyro_y: float | None = None
    gyro_z: float | None = None

    # --- GPS (opcional; jamás obligatorio)
    gps_speed: float | None = Field(default=None, description="km/h")
    gps_heading: float | None = Field(default=None, description="°")

    # --- calidad (ADR-0027)
    quality_score: float = Field(
        ge=0.0, le=1.0, description="señales medidas / señales esperadas en el ciclo"
    )
    missing_metric_count: int = Field(ge=0, default=0)
    quality_flags: dict[str, SignalQuality] = Field(
        default_factory=dict,
        description="SOLO señales ≠ measured (compacto); vacío = todo medido",
    )

    created_at: datetime


class SnapshotEventLink(ContractBase):
    """Pertenencia N:M snapshot↔evento SIN duplicar snapshots (F11 §11).

    Un instante puede pertenecer simultáneamente a TRIP + ACCELERATION + …; el
    ``primary_event_id`` del snapshot es solo el hoja más específico. Estrategia
    temporal alternativa (rango del evento sobre sequence_number) documentada en
    docs/data-architecture/11 §eventos — este enlace se materializa solo cuando la
    consulta lo justifica.
    """

    snapshot_id: str
    event_id: str
    event_type: str = Field(description="Denormalizado para filtrar sin join")
