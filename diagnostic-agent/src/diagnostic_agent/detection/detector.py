"""Detección de anomalías en runtime (ML matemático; el LLM jamás participa aquí).

Dos detectores:
- ``ZScoreDetector``: baseline explicable (mediana/MAD del entrenamiento vía manifiesto
  ligero JSON); sirve de referencia mínima y de respaldo sin ONNX.
- ``OnnxDetector``: ejecuta un paquete de modelo (IForest/AE exportado) con onnxruntime.

Ambos producen ``DetectedAnomaly`` con los PIDs más implicados para la explicabilidad
posterior del agente.
"""

import uuid
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import onnxruntime as ort

from diagnostic_agent.models_runtime.loader import verify_package
from mecanico_contracts import DetectedAnomaly, DetectorKind, ModelManifest
from mecanico_contracts.features import FEATURE_NAMES

#: Nº de features que se reportan como más implicadas en una anomalía.
_TOP_K = 5


def _top_pids(feature_names: list[str], contributions: np.ndarray) -> list[str]:
    """PIDs (deduplicados) de las features con mayor contribución absoluta."""
    order = np.argsort(-np.abs(contributions))
    pids: list[str] = []
    for idx in order:
        pid = feature_names[int(idx)].split("_")[0]
        if pid == "corr":  # corr_A_B → implicar ambos
            parts = feature_names[int(idx)].split("_")
            for p in (parts[1], parts[3] if len(parts) > 3 else parts[2]):
                if p not in pids:
                    pids.append(p)
        elif pid not in pids:
            pids.append(pid)
        if len(pids) >= _TOP_K:
            break
    return pids[:_TOP_K]


class ZScoreDetector:
    """Z-score robusto (mediana/MAD) sobre el vector de features (Leys et al., 2013)."""

    kind = DetectorKind.ZSCORE

    def __init__(self, medians: list[float], mads: list[float], threshold: float) -> None:
        self.median = np.asarray(medians, dtype=np.float64)
        self.mad = np.maximum(np.asarray(mads, dtype=np.float64), 1e-9)
        self.threshold = threshold

    def score(self, feature_vec: list[float]) -> tuple[float, np.ndarray]:
        """Score = máximo |z modificado|; contribución = |z| por feature."""
        x = np.asarray(feature_vec, dtype=np.float64)
        z = 0.6745 * (x - self.median) / self.mad
        return float(np.max(np.abs(z))), np.abs(z)


class OnnxDetector:
    """Detector servido con ONNX Runtime desde un paquete verificado (ADR-0009)."""

    def __init__(self, package_dir: Path) -> None:
        self.manifest: ModelManifest = verify_package(package_dir)
        self._sess = ort.InferenceSession(
            str(package_dir / self.manifest.artifact_filename),
            providers=["CPUExecutionProvider"],
        )
        self._input_name = self._sess.get_inputs()[0].name

    @property
    def kind(self) -> DetectorKind:
        return self.manifest.detector

    def score(self, feature_vec: list[float]) -> tuple[float, np.ndarray]:
        """Score del modelo (mayor = más anómalo) + contribución aproximada.

        skl2onnx exporta IsolationForest con salida ``scores`` donde el score de sklearn
        (decision_function) es mayor = más normal; se invierte el signo para cumplir
        ``score_direction=higher_is_anomalous`` del manifiesto.
        """
        x = np.asarray([feature_vec], dtype=np.float32)
        outputs = self._sess.run(None, {self._input_name: x})
        raw = float(np.ravel(outputs[-1])[0])  # último output = scores en skl2onnx
        score = -raw
        # Contribución aproximada: desviación normalizada respecto al vector nulo del scaler
        # embebido no es accesible desde ONNX; se usa |valor| estandarizado por percentiles
        # del propio vector como heurística de implicación.
        contrib = np.abs(np.asarray(feature_vec, dtype=np.float64))
        return score, contrib


def make_anomaly(
    detector_kind: DetectorKind,
    score: float,
    threshold: float,
    contributions: np.ndarray,
    features: list[float],
    vehicle_id: str,
    window_id: str,
    model_name: str | None = None,
    model_version: str | None = None,
) -> DetectedAnomaly:
    """Construye el contrato ``DetectedAnomaly`` a partir de un scoring positivo."""
    return DetectedAnomaly(
        anomaly_id=str(uuid.uuid4()),
        window_id=window_id,
        vehicle_id=vehicle_id,
        detected_at=datetime.now(tz=UTC),
        detector=detector_kind,
        model_name=model_name,
        model_version=model_version,
        score=round(score, 6),
        threshold=threshold,
        involved_pids=_top_pids(FEATURE_NAMES, contributions),
        features=dict(zip(FEATURE_NAMES, [round(f, 6) for f in features], strict=True)),
    )
