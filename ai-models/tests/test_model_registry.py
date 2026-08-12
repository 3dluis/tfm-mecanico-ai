"""Tests del Model Registry (F7, ADR-0022)."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from ai_models.registry import ModelRegistry, sha256_of
from mecanico_contracts import ModelRegistryEntry, ModelStatus, ModelType

NOW = datetime(2026, 8, 12, tzinfo=UTC)
REPO_REGISTRY = Path(__file__).resolve().parents[1] / "registry"


def _entry(status: ModelStatus = ModelStatus.EXPERIMENTAL) -> ModelRegistryEntry:
    return ModelRegistryEntry(
        model_id="test-model",
        name="test",
        model_family="lof",
        model_type=ModelType.ML,
        version="0.0.1",
        status=status,
        created_at=NOW,
    )


def test_roundtrip_y_transicion_valida(tmp_path: Path) -> None:
    reg = ModelRegistry(tmp_path)
    reg.register(_entry())
    assert reg.get("test-model", "0.0.1").status == ModelStatus.EXPERIMENTAL
    reg.update_status("test-model", "0.0.1", ModelStatus.CANDIDATE)
    assert reg.get("test-model", "0.0.1").status == ModelStatus.CANDIDATE


def test_transicion_ilegal_rechazada(tmp_path: Path) -> None:
    reg = ModelRegistry(tmp_path)
    reg.register(_entry())
    # EDGE_APPROVED exige pasar por CANDIDATE/VALIDATED (nunca solo métricas offline).
    with pytest.raises(ValueError, match="no permitida"):
        reg.update_status("test-model", "0.0.1", ModelStatus.EDGE_APPROVED)


def test_checksum_verificable(tmp_path: Path) -> None:
    artifact = tmp_path / "m.onnx"
    artifact.write_bytes(b"onnx-bytes")
    reg = ModelRegistry(tmp_path / "reg")
    reg.register(_entry().model_copy(update={"checksum": sha256_of(artifact)}))
    assert reg.verify_artifact("test-model", "0.0.1", artifact)
    artifact.write_bytes(b"tampered")
    assert not reg.verify_artifact("test-model", "0.0.1", artifact)


def test_registro_del_repo_es_integro_y_reconstruible(tmp_path: Path) -> None:
    """El registro commiteado parsea como contratos, es íntegro y es reproducible."""
    reg = ModelRegistry(REPO_REGISTRY)
    assert reg.check() == []
    entries = reg.entries()
    assert len(entries) >= 7
    lof = reg.get("anom-lof", "0.1.0")
    # Valores REALES de F3 importados sin recalcular (e1_results.csv).
    run = next(r for r in reg.training_runs("EXP-ANOM-001") if r.model_id == "anom-lof")
    assert run.metrics["test_f1"] == 0.6448
    assert run.metrics["test_fpr"] == 0.0345
    assert run.metrics["test_recall_heldout"] == 0.25
    assert run.seed == 42 and run.git_commit == "69a1e4d"
    assert lof.status == ModelStatus.SUPERSEDED  # 0.1.0 sucedido por 0.2.0 (ONNX)
    assert reg.get("anom-lof", "0.2.0").status == ModelStatus.VALIDATED
    # Reconstrucción determinista byte a byte.
    import importlib.util

    script = REPO_REGISTRY.parent / "experiments" / "register_f3.py"
    spec = importlib.util.spec_from_file_location("register_f3", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rebuilt = mod.build(tmp_path)
    original = (REPO_REGISTRY / "models" / "anom-lof@0.2.0.json").read_text()
    assert (tmp_path / "models" / "anom-lof@0.2.0.json").read_text() == original
    assert rebuilt.check() == []
