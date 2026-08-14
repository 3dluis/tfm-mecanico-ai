"""Ground truth sintético de atribución — mapeo fallo → conjunto de features fs1.

Implementa la tabla de la Adenda XAI v1 §7 (ADR-0033): para cada fallo del catálogo de
inyección, el conjunto de features fs1 que un mecanismo de explicación DEBERÍA señalar,
derivado de las transformaciones reales de ``obd_lab.injection.faults`` (qué PIDs toca)
y del contrato de features (``ai_models.features.schema``: qué features nacen de cada
PID). Para anomalías relacionales el GT es un CONJUNTO (atribución distribuida =
correcta); no se reduce artificialmente a una sola feature.

El mapeo se congela en la config del experimento antes de calcular métricas.
"""

from ai_models.features.schema import FS1
from mecanico_contracts.features import FEATURE_NAMES

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

#: Features de correlación añadidas explícitamente al GT de fallos RELACIONALES
#: (la firma vive en la relación, no solo en las señales; adenda §7).
FAULT_RELATIONAL_FEATURES: dict[str, frozenset[str]] = {
    "corr_break_rpm_maf": frozenset({"corr_RPM_MAF", "corr_ENGINE_LOAD_MAF"}),
    "load_coolant_decouple": frozenset({"corr_ENGINE_LOAD_COOLANT_TEMP"}),
    "vacuum_leak": frozenset({"total_trim_mean"}),
    "maf_drift": frozenset({"total_trim_mean", "corr_RPM_MAF", "corr_ENGINE_LOAD_MAF"}),
}


def gt_features_for(fault: str) -> frozenset[str]:
    """Conjunto GT de features fs1 para un fallo del catálogo.

    Una feature entra al GT si alguno de sus PIDs origen está afectado por el fallo, más
    las features relacionales declaradas. Lanza KeyError para fallos fuera del catálogo
    (el mapeo debe ser explícito, nunca inferido en caliente).
    """
    pids = FAULT_AFFECTED_PIDS[fault]
    base = {spec.name for spec in FS1.specs if any(p in pids for p in spec.source_pids)}
    base |= FAULT_RELATIONAL_FEATURES.get(fault, frozenset())
    unknown = base - set(FEATURE_NAMES)
    if unknown:
        msg = f"GT contiene features fuera de fs1: {sorted(unknown)}"
        raise RuntimeError(msg)
    return frozenset(base)
