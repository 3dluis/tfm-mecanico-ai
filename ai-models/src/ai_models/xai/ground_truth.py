"""Ground truth sintético de atribución — mapeo fallo → conjunto de features del esquema.

Implementa la tabla de la Adenda XAI v1 §7 (ADR-0033): para cada fallo del catálogo de
inyección, el conjunto de features que un mecanismo de explicación DEBERÍA señalar,
derivado de las transformaciones reales de ``obd_lab.injection.faults`` (qué PIDs toca)
y del contrato de features (``ai_models.features.schema``: qué features nacen de cada
PID). Para anomalías relacionales el GT es un CONJUNTO (atribución distribuida =
correcta); no se reduce artificialmente a una sola feature.

Generalización F17 (EXP-ANOM-008): el GT se parametriza por ``FeatureSchema`` — la regla
base (feature ∈ GT si algún PID origen está afectado) es idéntica para todos los
esquemas; SOLO el complemento relacional se declara explícitamente por esquema (nunca se
infiere en caliente). fs1 sigue siendo el valor por defecto.

El mapeo se congela en la config del experimento antes de calcular métricas.
"""

from ai_models.features.schema import FS1, FeatureSchema

#: PIDs afectados por cada fallo (firma de la transformación del catálogo, adenda §7).
FAULT_AFFECTED_PIDS: dict[str, frozenset[str]] = {
    "vacuum_leak": frozenset({"SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1", "INTAKE_PRESSURE", "RPM"}),
    "maf_drift": frozenset({"MAF", "SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1"}),
    "thermostat_stuck": frozenset({"COOLANT_TEMP"}),
    "o2_lag": frozenset({"O2_B1S1", "SHORT_FUEL_TRIM_1"}),
    "misfire": frozenset({"RPM", "ENGINE_LOAD", "O2_B1S1"}),
    "corr_break_rpm_maf": frozenset({"RPM", "MAF"}),
    "load_coolant_decouple": frozenset({"COOLANT_TEMP", "ENGINE_LOAD"}),
    "joint_slow_drift": frozenset({"MAF", "TIMING_ADVANCE"}),
}

#: Features de correlación añadidas explícitamente al GT de fallos RELACIONALES, POR
#: ESQUEMA (la firma vive en la relación, no solo en las señales; adenda §7). En
#: fs2-lite los absolutos sustituidos se traducen a sus contrapartes de deriva y se
#: añaden las lag-1 pertinentes (misma justificación: la firma es relacional).
FAULT_RELATIONAL_FEATURES_BY_SCHEMA: dict[str, dict[str, frozenset[str]]] = {
    "fs1": {
        "corr_break_rpm_maf": frozenset({"corr_RPM_MAF", "corr_ENGINE_LOAD_MAF"}),
        "load_coolant_decouple": frozenset({"corr_ENGINE_LOAD_COOLANT_TEMP"}),
        "vacuum_leak": frozenset({"total_trim_mean"}),
        "maf_drift": frozenset({"total_trim_mean", "corr_RPM_MAF", "corr_ENGINE_LOAD_MAF"}),
    },
    "fs2-lite": {
        "corr_break_rpm_maf": frozenset(
            {"corr_RPM_MAF", "corr_ENGINE_LOAD_MAF", "corr_lag1_RPM_MAF"}
        ),
        "load_coolant_decouple": frozenset({"corr_ENGINE_LOAD_COOLANT_TEMP"}),
        "vacuum_leak": frozenset({"total_trim_session_drift"}),
        "maf_drift": frozenset(
            {
                "total_trim_session_drift",
                "corr_RPM_MAF",
                "corr_ENGINE_LOAD_MAF",
                "corr_lag1_RPM_MAF",
                "corr_lag1_THROTTLE_POS_MAF",
            }
        ),
    },
}

#: Alias de compatibilidad (F15/F16 y sus tests referencian el mapeo fs1 directamente).
FAULT_RELATIONAL_FEATURES: dict[str, frozenset[str]] = FAULT_RELATIONAL_FEATURES_BY_SCHEMA["fs1"]


def gt_features_for(fault: str, schema: FeatureSchema = FS1) -> frozenset[str]:
    """Conjunto GT de features del esquema para un fallo del catálogo.

    Una feature entra al GT si alguno de sus PIDs origen está afectado por el fallo, más
    las features relacionales declaradas para ese esquema. Lanza KeyError para fallos
    fuera del catálogo o esquemas sin mapeo relacional declarado (el mapeo debe ser
    explícito, nunca inferido en caliente).
    """
    pids = FAULT_AFFECTED_PIDS[fault]
    relational = FAULT_RELATIONAL_FEATURES_BY_SCHEMA[schema.schema_id]
    base = {spec.name for spec in schema.specs if any(p in pids for p in spec.source_pids)}
    base |= relational.get(fault, frozenset())
    unknown = base - set(schema.names)
    if unknown:
        msg = f"GT contiene features fuera de {schema.schema_id}: {sorted(unknown)}"
        raise RuntimeError(msg)
    return frozenset(base)
