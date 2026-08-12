"""Tests del runtime de detección: validaciones del cargador y ventanas."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from diagnostic_agent.models_runtime.loader import ModelPackageError, verify_package
from diagnostic_agent.telemetry.windows import WindowBuilder, is_valid
from mecanico_contracts import DetectorKind, ModelManifest, OBDReading, TransportKind

NOW = datetime(2026, 8, 12, tzinfo=UTC)


def _reading(pid: str, value: float) -> OBDReading:
    return OBDReading(
        timestamp=NOW,
        pid=pid,
        value=value,
        unit="x",
        vehicle_id="v",
        device_id="d",
        source=TransportKind.TCP,
    )


def test_validacion_de_rangos() -> None:
    assert is_valid(_reading("RPM", 800))
    assert not is_valid(_reading("RPM", 9500))
    assert not is_valid(_reading("COOLANT_TEMP", 200))


def test_window_builder_emite_con_stride() -> None:
    wb = WindowBuilder(size=10, stride=5)
    emitted = 0
    for i in range(30):
        if wb.push_tick([_reading("RPM", 800 + i)]) is not None:
            emitted += 1
    assert emitted == 5  # ventanas en t=10,15,20,25,30


def _manifest(**overrides: object) -> dict[str, object]:
    from mecanico_contracts.features import FEATURE_NAMES

    base = ModelManifest(
        model_id="m1",
        name="x",
        version="0.1.0",
        detector=DetectorKind.LOF,
        algorithm="LOF",
        artifact_filename="x.onnx",
        artifact_sha256="0" * 64,
        expected_features=list(FEATURE_NAMES),
        window_size=60,
        decision_threshold=0.5,
    ).model_dump(mode="json")
    base.update(overrides)
    return base


def test_loader_rechaza_hash_incorrecto(tmp_path: Path) -> None:
    (tmp_path / "x.onnx").write_bytes(b"artefacto")
    (tmp_path / "manifest.json").write_text(json.dumps(_manifest()), encoding="utf-8")
    with pytest.raises(ModelPackageError, match="sha256"):
        verify_package(tmp_path)


def test_loader_rechaza_features_incompatibles(tmp_path: Path) -> None:
    import hashlib

    (tmp_path / "x.onnx").write_bytes(b"artefacto")
    sha = hashlib.sha256(b"artefacto").hexdigest()
    (tmp_path / "manifest.json").write_text(
        json.dumps(_manifest(artifact_sha256=sha, expected_features=["otra_feature"])),
        encoding="utf-8",
    )
    with pytest.raises(ModelPackageError, match="features"):
        verify_package(tmp_path)
