"""Contrato de features versionado — inventario formal de esquemas (F13, Protocolo ML v1).

La definición EJECUTABLE del esquema vigente ``fs1`` sigue viviendo en
``mecanico_contracts.features`` (ADR-0010: es contrato entrenamiento↔inferencia y alimenta
``ModelManifest.expected_features``). Este módulo NO la duplica: la describe — nombre,
procedencia, unidad, tipo, raw/derivada — para que cada experimento registre exactamente
qué entra al modelo y para que un esquema nuevo (fs2) se declare ANTES de implementarse.

Reglas:
- ``FS1`` se construye programáticamente desde el contrato compartido; un test verifica
  que nombres y orden coinciden con ``FEATURE_NAMES`` (si divergen, el build falla).
- ``FS2_DRAFT`` recoge las features candidatas YA identificadas por el análisis de errores
  del proyecto (ADR-0011 «estadísticos multiescala y correlaciones lag-1»; F9 «deriva LTFT
  relativa a la propia sesión»). Es un BORRADOR sin extracción implementada: prohibido
  entrenar con él hasta que exista implementación + versión de esquema promovida.
- Promover un esquema = implementarlo en ``shared`` (cambio aditivo de contrato), fijar
  ``feature_schema_version`` nuevo y regenerar schemas/diccionario (REGLAS.md regla 5).
"""

from dataclasses import dataclass
from enum import StrEnum

from mecanico_contracts.features import _CORR_PAIRS, CANONICAL_PIDS, FEATURE_NAMES

#: Unidad física canónica por PID (fuente: obd_lab.generate._UNITS, docs/03 §3.1).
PID_UNITS: dict[str, str] = {
    "RPM": "rpm",
    "SPEED": "kph",
    "ENGINE_LOAD": "percent",
    "COOLANT_TEMP": "degC",
    "INTAKE_TEMP": "degC",
    "MAF": "gps",
    "THROTTLE_POS": "percent",
    "SHORT_FUEL_TRIM_1": "percent",
    "LONG_FUEL_TRIM_1": "percent",
    "O2_B1S1": "volt",
    "TIMING_ADVANCE": "degree",
    "INTAKE_PRESSURE": "kilopascal",
}


class FeatureKind(StrEnum):
    """Procedencia de la feature respecto a la señal original."""

    RAW_STAT = "raw_stat"  # estadístico directo de una señal (mean/std/slope…)
    DERIVED = "derived"  # relación entre señales o transformación no trivial


@dataclass(frozen=True)
class FeatureSpec:
    """Descripción de una feature: qué es, de dónde sale y en qué unidades."""

    name: str
    source_pids: tuple[str, ...]
    unit: str  # unidad del valor de la feature ('' = adimensional)
    kind: FeatureKind
    windowed: bool  # True = se calcula sobre la ventana completa
    required: bool  # False = opcional (PID no garantizado en todos los vehículos)
    description: str


@dataclass(frozen=True)
class FeatureSchema:
    """Esquema de features versionado e inmutable."""

    schema_id: str  # p. ej. 'fs1'
    status: str  # 'vigente' | 'draft'
    normalization: str  # política de normalización acordada para el esquema
    specs: tuple[FeatureSpec, ...]

    @property
    def names(self) -> list[str]:
        return [s.name for s in self.specs]


def _fs1_specs() -> tuple[FeatureSpec, ...]:
    """Construye la descripción de fs1 desde el contrato compartido (sin duplicar orden)."""
    specs: list[FeatureSpec] = []
    for stat, desc in (
        ("mean", "media de la señal en la ventana"),
        ("std", "desviación típica muestral (ddof=1) en la ventana"),
        ("slope", "pendiente por mínimos cuadrados sobre el índice (unidad/muestra)"),
    ):
        for pid in CANONICAL_PIDS:
            specs.append(
                FeatureSpec(
                    name=f"{pid}_{stat}",
                    source_pids=(pid,),
                    unit=PID_UNITS[pid] if stat != "slope" else f"{PID_UNITS[pid]}/muestra",
                    kind=FeatureKind.RAW_STAT,
                    windowed=True,
                    required=True,
                    description=f"{desc} ({pid})",
                )
            )
    for a, b in _CORR_PAIRS:
        specs.append(
            FeatureSpec(
                name=f"corr_{a}_{b}",
                source_pids=(a, b),
                unit="",
                kind=FeatureKind.DERIVED,
                windowed=True,
                required=True,
                description=f"correlación de Pearson {a}↔{b} (0.0 si una serie es constante)",
            )
        )
    specs.append(
        FeatureSpec(
            name="total_trim_mean",
            source_pids=("SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1"),
            unit="percent",
            kind=FeatureKind.DERIVED,
            windowed=True,
            required=True,
            description="media por tick de STFT+LTFT (corrección total de mezcla)",
        )
    )
    return tuple(specs)


#: Esquema VIGENTE (42 features; congelado en arms-freeze-v1 para los brazos de F10).
FS1 = FeatureSchema(
    schema_id="fs1",
    status="vigente",
    normalization="embedded-standard-scaler",  # StandardScaler dentro del Pipeline/ONNX
    specs=_fs1_specs(),
)

#: BORRADOR fs2 — candidatas justificadas por el análisis de errores previo, NO implementadas.
#: Cada una responde a una limitación observada, no a exploración indiscriminada:
#: - std multiescala y correlaciones lag-1: ADR-0011 («señal intermitente por ventana en
#:   held-out temporales; margen para features temporales más ricas»).
#: - deriva LTFT relativa a la sesión: F9/EXP-ANOM-003 (varianza entre-sesiones del LTFT
#:   en autovía, ratio entre/intra 1.56, causa del FPR de eventos).
FS2_DRAFT = FeatureSchema(
    schema_id="fs2-draft",
    status="draft",
    normalization="por decidir (comparar StandardScaler vs RobustScaler en EXP-ANOM-006)",
    specs=tuple(
        [
            FeatureSpec(
                name=f"{pid}_std_15",
                source_pids=(pid,),
                unit=PID_UNITS[pid],
                kind=FeatureKind.RAW_STAT,
                windowed=True,
                required=True,
                description=f"desviación típica en sub-ventana de 15 muestras ({pid}), multiescala",
            )
            for pid in ("RPM", "MAF", "COOLANT_TEMP", "LONG_FUEL_TRIM_1")
        ]
        + [
            FeatureSpec(
                name=f"corr_lag1_{a}_{b}",
                source_pids=(a, b),
                unit="",
                kind=FeatureKind.DERIVED,
                windowed=True,
                required=True,
                description=f"correlación {a}(t)↔{b}(t-1): respuesta retardada entre señales",
            )
            for a, b in (("RPM", "MAF"), ("THROTTLE_POS", "MAF"))
        ]
        + [
            FeatureSpec(
                name="LTFT_session_drift",
                source_pids=("LONG_FUEL_TRIM_1",),
                unit="percent",
                kind=FeatureKind.DERIVED,
                windowed=True,
                required=True,
                description=(
                    "media de LTFT en la ventana menos media de LTFT del inicio de la "
                    "propia sesión (deriva relativa; candidata F9 contra el FPR de autovía)"
                ),
            )
        ]
    ),
)

#: Registro de esquemas conocidos por identificador.
SCHEMAS: dict[str, FeatureSchema] = {FS1.schema_id: FS1, FS2_DRAFT.schema_id: FS2_DRAFT}


def validate_fs1_against_contract() -> None:
    """Falla si la descripción fs1 diverge del contrato ejecutable compartido."""
    if FS1.names != list(FEATURE_NAMES):
        msg = "FS1 (descripción) no coincide con FEATURE_NAMES (contrato): revisar schema.py"
        raise RuntimeError(msg)
