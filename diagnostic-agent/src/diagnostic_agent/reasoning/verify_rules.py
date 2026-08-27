"""Nodo verify: reglas DETERMINISTAS que contrastan hipótesis contra las features reales.

Responsabilidad estricta (requisito del autor): verify no usa LLM. Cada modo de fallo
define comprobaciones sobre el vector de features de la ventana anómala; cada
comprobación produce una ``DiagnosticEvidence`` con rol supports/contradicts y una
afirmación verificable. La decisión de estado de la hipótesis se deriva del balance.
"""

import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from mecanico_contracts import (
    DiagnosticEvidence,
    DiagnosticHypothesis,
    EvidenceKind,
    EvidenceRole,
    HypothesisStatus,
)

#: (nombre, predicado sobre features, plantilla de afirmación, peso, feature de anclaje)
#:
#: La *feature de anclaje* es lo que hace la evidencia rastreable **hasta el dato**: se
#: registra como ``reference_id`` de la ``DiagnosticEvidence``, de modo que una afirmación
#: telemétrica no solo se afirme, sino que apunte a la magnitud concreta del vector de
#: features que la sostiene (ADR-0036; métrica de profundidad de traza).
Check = tuple[str, Callable[[dict[str, float]], bool], str, float, str]

_RULES: dict[str, list[Check]] = {
    "vacuum_leak": [
        (
            "trims_positivos",
            lambda f: f.get("total_trim_mean", 0) > 4.0,
            "total_trim_mean={total_trim_mean:+.1f}% (esperado >+4% con fuga de vacío)",
            0.9,
            "total_trim_mean",
        ),
        (
            "map_elevado_baja_velocidad",
            lambda f: f.get("INTAKE_PRESSURE_mean", 0) > 30 and f.get("SPEED_mean", 99) < 30,
            "MAP medio={INTAKE_PRESSURE_mean:.0f} kPa con velocidad media {SPEED_mean:.0f} km/h",
            0.5,
            "INTAKE_PRESSURE_mean",
        ),
        (
            "ralenti_inestable",
            lambda f: f.get("RPM_std", 0) > 35 and f.get("SPEED_mean", 99) < 10,
            "RPM_std={RPM_std:.0f} en ralentí (inestabilidad)",
            0.4,
            "RPM_std",
        ),
    ],
    "maf_drift": [
        (
            "trims_positivos",
            lambda f: f.get("total_trim_mean", 0) > 4.0,
            "total_trim_mean={total_trim_mean:+.1f}% (compensación por MAF que subestima)",
            0.8,
            "total_trim_mean",
        ),
        (
            "maf_bajo_para_regimen",
            lambda f: (
                f.get("MAF_mean", 99)
                < 0.00035 * f.get("RPM_mean", 0) * f.get("ENGINE_LOAD_mean", 0)
            ),
            "MAF_mean={MAF_mean:.1f} g/s inferior al esperado para RPM×carga",
            0.7,
            "MAF_mean",
        ),
    ],
    "thermostat_stuck": [
        (
            "temperatura_baja",
            lambda f: f.get("COOLANT_TEMP_mean", 99) < 80.0,
            "COOLANT_TEMP_mean={COOLANT_TEMP_mean:.1f} °C (<80 °C: no alcanza régimen)",
            0.9,
            "COOLANT_TEMP_mean",
        ),
        (
            "meseta_estable",
            lambda f: f.get("COOLANT_TEMP_std", 99) < 2.0,
            "COOLANT_TEMP_std={COOLANT_TEMP_std:.2f} (meseta, no calentamiento en curso)",
            0.5,
            "COOLANT_TEMP_std",
        ),
    ],
    "o2_lag": [
        (
            "oscilacion_amortiguada",
            lambda f: f.get("O2_B1S1_std", 99) < 0.15,
            "O2_B1S1_std={O2_B1S1_std:.3f} V (oscilación amortiguada; sano ≈0.25)",
            0.8,
            "O2_B1S1_std",
        ),
        (
            "stft_ruidoso",
            lambda f: f.get("SHORT_FUEL_TRIM_1_std", 0) > 2.0,
            "STFT_std={SHORT_FUEL_TRIM_1_std:.1f}% (control de mezcla degradado)",
            0.4,
            "SHORT_FUEL_TRIM_1_std",
        ),
    ],
    "misfire": [
        (
            "rpm_inestable",
            lambda f: f.get("RPM_std", 0) > 60,
            "RPM_std={RPM_std:.0f} (caídas de régimen)",
            0.7,
            "RPM_std",
        ),
        (
            "o2_rico_intermitente",
            lambda f: f.get("O2_B1S1_mean", 0) > 0.55,
            "O2_B1S1_mean={O2_B1S1_mean:.2f} V (combustible sin quemar)",
            0.5,
            "O2_B1S1_mean",
        ),
    ],
}


def verify_hypothesis(
    hypothesis: DiagnosticHypothesis, features: dict[str, float], case_id: str
) -> tuple[HypothesisStatus, list[DiagnosticEvidence], float]:
    """Contrasta una hipótesis; devuelve (estado, evidencias, confianza ajustada)."""
    checks = _RULES.get(hypothesis.failure_mode)
    now = datetime.now(tz=UTC)
    evidences: list[DiagnosticEvidence] = []

    if checks is None:
        # Modo no cubierto por reglas (p. ej. unknown_relational): inconcluso por diseño.
        return HypothesisStatus.INCONCLUSIVE, [], min(hypothesis.confidence, 0.4)

    support, contradict = 0.0, 0.0
    for name, predicate, template, weight, anchor in checks:
        holds = predicate(features)
        role = EvidenceRole.SUPPORTS if holds else EvidenceRole.CONTRADICTS
        try:
            statement = template.format(**{k: features.get(k, 0.0) for k in features} | features)
        except (KeyError, IndexError):
            statement = template
        evidences.append(
            DiagnosticEvidence(
                evidence_id=str(uuid.uuid4()),
                case_id=case_id,
                hypothesis_id=hypothesis.hypothesis_id,
                kind=EvidenceKind.TELEMETRY,
                role=role,
                reference_id=anchor,
                statement=f"[{name}] {statement}",
                strength=weight,
                produced_by="verify",
                created_at=now,
            )
        )
        if holds:
            support += weight
        else:
            contradict += weight

    total = support + contradict
    ratio = support / total if total else 0.0
    if ratio >= 0.65:
        status = HypothesisStatus.SUPPORTED
    elif ratio <= 0.35:
        status = HypothesisStatus.CONTRADICTED
    else:
        status = HypothesisStatus.INCONCLUSIVE
    adjusted = round(min(1.0, hypothesis.confidence * 0.4 + ratio * 0.6), 3)
    return status, evidences, adjusted
