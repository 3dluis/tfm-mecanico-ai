"""Pruebas de los contratos compartidos: construcción, inmutabilidad y export."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

import mecanico_contracts as mc
from mecanico_contracts.export_schemas import EXPORTABLE, export_all

NOW = datetime(2026, 8, 12, 12, 0, 0, tzinfo=UTC)


def _reading() -> mc.OBDReading:
    return mc.OBDReading(
        timestamp=NOW,
        pid="RPM",
        value=850.0,
        unit="rpm",
        vehicle_id="veh-1",
        device_id="dev-1",
        source=mc.TransportKind.TCP,
    )


def test_obd_reading_valido() -> None:
    r = _reading()
    assert r.schema_version == mc.SCHEMA_VERSION
    assert r.source == "tcp"


def test_contratos_son_inmutables() -> None:
    r = _reading()
    with pytest.raises(ValidationError):
        r.value = 900.0  # type: ignore[misc]


def test_extra_prohibido() -> None:
    with pytest.raises(ValidationError):
        mc.DTCRecord(
            timestamp=NOW,
            vehicle_id="veh-1",
            code="P0171",
            campo_inesperado=1,  # type: ignore[call-arg]
        )


def test_dtc_valida_formato() -> None:
    with pytest.raises(ValidationError):
        mc.DTCRecord(timestamp=NOW, vehicle_id="veh-1", code="XYZ")


def test_confianza_acotada() -> None:
    with pytest.raises(ValidationError):
        mc.DiagnosticHypothesis(
            hypothesis_id="h1",
            cause="fuga de vacío",
            mechanism="aire no medido empobrece la mezcla",
            supporting_evidence=["LTFT +18%"],
            verified_against_telemetry=True,
            confidence=1.5,
        )


def test_manifest_semver() -> None:
    with pytest.raises(ValidationError):
        mc.ModelManifest(
            name="iforest",
            version="1.0",
            detector=mc.DetectorKind.ISOLATION_FOREST,
            artifact_filename="m.onnx",
            artifact_sha256="a" * 64,
            expected_features=["rpm_mean"],
            window_size=60,
            decision_threshold=0.5,
        )


def test_export_schemas(tmp_path: Path) -> None:
    files = export_all(tmp_path)
    assert len(files) == len(EXPORTABLE)
    assert all(f.exists() and f.stat().st_size > 0 for f in files)


def test_serializacion_json_roundtrip() -> None:
    r = _reading()
    again = mc.OBDReading.model_validate_json(r.model_dump_json())
    assert again == r
