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
    # Reconstrucción determinista byte a byte (F3 + F8).
    import importlib.util

    for script_name in ("register_f3.py", "register_e2.py", "register_e3.py", "register_f10.py"):
        script = REPO_REGISTRY.parent / "experiments" / script_name
        spec = importlib.util.spec_from_file_location(script.stem, script)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rebuilt = mod.build(tmp_path)
    for rel in (
        "models/anom-lof@0.2.0.json",
        "evaluations/EV-E2-AM-E-test.json",
        "models/event-baseline-z@0.2.0.json",
        "evaluations/EV-E3-AM-WE-d-test.json",
    ):
        assert (tmp_path / rel).read_text() == (REPO_REGISTRY / rel).read_text()
    assert rebuilt.check() == []
    # Ciclo de vida F9: 0.1.0 sucedidas por 0.2.0 sin reetiquetar evaluaciones E2.
    assert reg.get("event-baseline-z", "0.1.0").status == ModelStatus.SUPERSEDED
    assert reg.get("event-baseline-z", "0.2.0").status == ModelStatus.CANDIDATE
    # F10: clasificación exploratoria + promoción CANDIDATE con nota de evidencia.
    assert reg.get_experiment("EXP-ANOM-002").study_type == "exploratory"
    assert reg.get_experiment("EXP-ANOM-003").study_type == "exploratory"
    combined = reg.get("anom-combined-we", "0.2.0")
    assert combined.status == ModelStatus.CANDIDATE
    assert "EXPLORATORIA" in (combined.notes or "")
    # EXP-ANOM-002: la conclusión mantiene LOF como seleccionado (sin supersession).
    e2 = reg.get_experiment("EXP-ANOM-002")
    assert e2.selected_model_id == "anom-lof"
    combined_evals = {e.evaluation_id for e in reg.evaluations("anom-combined-we")}
    assert {"EV-E2-AM-WE-validation", "EV-E2-AM-WE-test"} <= combined_evals  # E2 intactas
    assert "EV-E3-AM-WE-d-test" in combined_evals  # E3 añade sin reetiquetar
