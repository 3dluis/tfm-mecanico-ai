"""Genera los ejemplos JSON de docs/data-architecture/examples/ desde instancias reales.

Los ejemplos nunca se escriben a mano: se construyen con los contratos (validados) y se
serializan — si un contrato cambia, `make data-docs` los regenera (requisito de
no-divergencia). Timestamps fijos para diffs estables.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import mecanico_contracts as mc

T0 = datetime(2026, 8, 12, 10, 0, 0, tzinfo=UTC)
OUT = Path(__file__).parents[1] / "docs" / "data-architecture" / "examples"


def dump(name: str, payload: object) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )


session = mc.TelemetrySession(
    session_id="sess-0001",
    source=mc.SessionSource.OBD_SIMULATOR,
    vehicle_id="veh-demo",
    device_id="rpi5-01",
    started_at=T0,
    sample_rate_hz=1.0,
    scenario_id="v-vacuum",
    generator_version="0.1.0",
    random_seed=211,
    software_version="23c2ca5",
)
point = mc.TelemetryPoint(
    session_id="sess-0001",
    seq=901,
    timestamp=T0,
    values={
        "RPM": 843.25,
        "SPEED": 0.0,
        "ENGINE_LOAD": 12.9,
        "COOLANT_TEMP": 88.0,
        "SHORT_FUEL_TRIM_1": 10.9,
        "LONG_FUEL_TRIM_1": 7.8,
        "INTAKE_PRESSURE": 46.0,
        "MAF": 4.9,
        "THROTTLE_POS": 15.7,
        "O2_B1S1": 0.44,
        "TIMING_ADVANCE": 14.0,
        "INTAKE_TEMP": 31.0,
    },
)
window = mc.TelemetryWindow(
    window_id="win-0042",
    session_id="sess-0001",
    seq_start=870,
    seq_end=929,
    start=T0,
    end=T0,
    size=60,
    stride=30,
)
anomaly = mc.DetectedAnomaly(
    anomaly_id="ano-0007",
    window_id="win-0042",
    session_id="sess-0001",
    inference_id="inf-0042",
    vehicle_id="veh-demo",
    detected_at=T0,
    detector=mc.DetectorKind.LOF,
    model_name="lof",
    model_version="0.2.0",
    score=12.78,
    threshold=0.163,
    involved_pids=["SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1", "INTAKE_PRESSURE", "RPM"],
    features={"total_trim_mean": 9.4, "INTAKE_PRESSURE_mean": 46.0, "RPM_std": 55.2},
)
dump(
    "telemetry-session.json",
    {
        "TelemetrySession": json.loads(session.model_dump_json()),
        "TelemetryPoint (uno de 1800)": json.loads(point.model_dump_json()),
        "TelemetryWindow": json.loads(window.model_dump_json()),
        "DetectedAnomaly": json.loads(anomaly.model_dump_json()),
    },
)

hyp = mc.DiagnosticHypothesis(
    hypothesis_id="hyp-01",
    case_id="case-0003",
    rank=1,
    suspected_component="colector de admisión / manguitos de vacío",
    failure_mode="vacuum_leak",
    cause="Fuga de vacío en el colector de admisión",
    mechanism=(
        "Aire no medido tras el MAF empobrece la mezcla; la ECU compensa con "
        "trims positivos, más en ralentí."
    ),
    status="supported",
    verified_against_telemetry=True,
    confidence=0.86,
)
evidence = mc.DiagnosticEvidence(
    evidence_id="ev-01",
    case_id="case-0003",
    hypothesis_id="hyp-01",
    kind=mc.EvidenceKind.TELEMETRY,
    role=mc.EvidenceRole.SUPPORTS,
    statement="[trims_positivos] total_trim_mean=+9.4% (esperado >+4% con fuga de vacío)",
    strength=0.9,
    produced_by="verify",
    created_at=T0,
)
case = mc.DiagnosticCase(
    case_id="case-0003",
    vehicle_id="veh-demo",
    session_id="sess-0001",
    status=mc.CaseStatus.CLOSED,
    severity=mc.Severity.MEDIUM,
    opened_at=T0,
    closed_at=T0,
    trigger_anomaly_ids=["ano-0007"],
    explanation="Diagnóstico más probable: fuga de vacío en admisión (confianza 0.86)…",
    provenance_id="prov-0003",
)
provenance = mc.ProvenanceRecord(
    provenance_id="prov-0003",
    subject_kind="diagnostic_case",
    subject_id="case-0003",
    vehicle_id="veh-demo",
    session_ids=["sess-0001"],
    window_ids=["win-0042"],
    fv_ids=["fv-0042"],
    inference_ids=["inf-0042"],
    anomaly_ids=["ano-0007"],
    model_refs=["lof@0.2.0"],
    document_chunk_ids=["doc-vacuum-leak#0"],
    case_memory_ids=[],
    agent_run_id="run-0003",
    prompt_version="p1",
    created_at=T0,
)
dump(
    "diagnostic-case.json",
    {
        "DiagnosticCase": json.loads(case.model_dump_json()),
        "DiagnosticHypothesis (rank 1 de 3)": json.loads(hyp.model_dump_json()),
        "DiagnosticEvidence (una de 5)": json.loads(evidence.model_dump_json()),
        "ProvenanceRecord": json.loads(provenance.model_dump_json()),
    },
)

pattern = mc.LearnedPattern(
    pattern_id="pat-0001",
    version=1,
    title="Patrón candidato: desacoplo RPM↔MAF con univariantes normales",
    description="Firma multivariable sin correspondencia con modos de fallo documentados; "
    "cada PID permanece en rango individual.",
    telemetry_signature={"corr_RPM_MAF": 0.21, "corr_ENGINE_LOAD_MAF": 0.18, "MAF_mean": 21.0},
    temporal_signature="colapso de correlación sostenido >5 min",
    affected_metrics=["RPM", "MAF", "ENGINE_LOAD"],
    suspected_failure_modes=["unknown_relational"],
    supporting_cases=["cmem-0009"],
    n_independent_sessions=1,
    n_distinct_vehicles=1,
    confidence=0.2,
    novelty_score=0.8,
    validation_level=mc.EpistemicLevel.SIMULATED,
    status=mc.PatternStatus.CANDIDATE,
    first_seen=T0,
    last_seen=T0,
    provenance_id="prov-0009",
)
dump("learned-pattern.json", {"LearnedPattern": json.loads(pattern.model_dump_json())})

manifest = mc.ModelManifest(
    model_id="0d1b6a4e-demo",
    name="lof",
    version="0.2.0",
    detector=mc.DetectorKind.LOF,
    algorithm="LocalOutlierFactor(n_neighbors=10, novelty=True)",
    artifact_filename="lof.onnx",
    artifact_format="onnx",
    artifact_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    runtime="onnxruntime>=1.17",
    expected_features=["RPM_mean", "…(42 en total; ver features.FEATURE_NAMES)"],
    window_size=60,
    window_stride=30,
    preprocessing="embedded",
    decision_threshold=0.1632,
    validation_metrics={"val_f1": 0.773, "val_fpr": 0.010},
    training_seed=42,
    trained_at=T0,
)
dump("model-manifest.json", {"ModelManifest": json.loads(manifest.model_dump_json())})

print(f"Ejemplos generados en {OUT}")
