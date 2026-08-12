"""Exportación de modelos a paquete distribuible: ONNX + ModelManifest (ADR-0009)."""

import hashlib
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from skl2onnx import to_onnx
from sklearn.pipeline import Pipeline

from mecanico_contracts import DetectorKind, ModelManifest
from mecanico_contracts.features import FEATURE_NAMES


def export_sklearn_package(
    pipeline: Pipeline,
    detector: DetectorKind,
    name: str,
    version: str,
    threshold: float,
    validation_metrics: dict[str, float],
    seed: int,
    out_root: Path,
    window_size: int = 60,
    window_stride: int = 30,
) -> Path:
    """Convierte un pipeline sklearn (scaler+modelo) a paquete ONNX con manifiesto."""
    sample = np.zeros((1, len(FEATURE_NAMES)), dtype=np.float32)
    onnx_model = to_onnx(pipeline, X=sample)

    package_dir = out_root / f"model-{name}-{version}"
    package_dir.mkdir(parents=True, exist_ok=True)
    artifact = package_dir / f"{name}.onnx"
    artifact.write_bytes(onnx_model.SerializeToString())

    manifest = ModelManifest(
        model_id=str(uuid.uuid4()),
        name=name,
        version=version,
        detector=detector,
        algorithm=repr(pipeline.named_steps["model"]),
        artifact_filename=artifact.name,
        artifact_format="onnx",
        artifact_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
        runtime="onnxruntime>=1.17",
        expected_features=list(FEATURE_NAMES),
        window_size=window_size,
        window_stride=window_stride,
        preprocessing="embedded",  # el StandardScaler viaja dentro del grafo ONNX
        decision_threshold=threshold,
        score_direction="higher_is_anomalous",
        validation_metrics=validation_metrics,
        training_seed=seed,
        trained_at=datetime.now(tz=UTC),
    )
    (package_dir / "manifest.json").write_text(
        json.dumps(json.loads(manifest.model_dump_json()), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return package_dir
