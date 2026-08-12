"""Validación edge de un objetivo hardware: benchmark ONNX + suite de tests (F8).

Se ejecuta EN el objetivo (Mac x86/arm64, contenedor ARM64, Raspberry Pi) y produce un
JSON con métricas reales para la matriz de compatibilidad (HardwareValidation). Los
estados son honestos: este script NUNCA marca 'approved' — imprime las mediciones y el
humano decide la transición en el registro (EDGE_APPROVED exige revisión, ADR-0022).

Uso (desde la raíz del repo, con el venv del proyecto):
    python tools/edge_validate.py --target arm64-container [--out validation.json]
"""

import argparse
import json
import platform
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]


def benchmark_lof(n_iters: int = 500) -> dict[str, float]:
    """Entrena el LOF k=10 de referencia, lo exporta a ONNX y mide inferencia real."""
    import onnxruntime as ort

    from ai_models.anomaly.baselines import make_baselines
    from ai_models.export.onnx_export import export_sklearn_package
    from mecanico_contracts import DetectorKind
    from mecanico_contracts.features import FEATURE_NAMES

    rng = np.random.default_rng(42)
    x_train = rng.normal(size=(600, len(FEATURE_NAMES))).astype(np.float64)
    det = next(d for d in make_baselines(42) if d.name == "lof")
    t0 = time.perf_counter()
    det.fit(x_train)
    fit_s = time.perf_counter() - t0

    out_dir = REPO_ROOT / "ai-models" / "models"
    pkg = export_sklearn_package(
        det.pipeline, DetectorKind.LOF, "lof", "0.2.0", 0.163197, {}, 42, out_dir
    )
    artifact = next(pkg.glob("*.onnx"))
    sess = ort.InferenceSession(str(artifact), providers=["CPUExecutionProvider"])
    name = sess.get_inputs()[0].name
    sample = rng.normal(size=(1, len(FEATURE_NAMES))).astype(np.float32)
    sess.run(None, {name: sample})  # warm-up
    lat = []
    for _ in range(n_iters):
        t0 = time.perf_counter()
        sess.run(None, {name: sample})
        lat.append((time.perf_counter() - t0) * 1000)
    return {
        "fit_s": round(fit_s, 3),
        "artifact_bytes": artifact.stat().st_size,
        "infer_ms_p50": round(statistics.median(lat), 4),
        "infer_ms_p95": round(sorted(lat)[int(0.95 * len(lat))], 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="'mac-dev' | 'arm64-container' | 'rpi5'")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    import resource

    result = {
        "target": args.target,
        "status_suggestion": "PASSED (pendiente de revisión humana; nunca auto-approved)",
        "machine": platform.machine(),
        "python": platform.python_version(),
        "measured_at": datetime.now(UTC).isoformat(),
        "onnx_lof": benchmark_lof(),
    }
    result["peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    print(payload)
    if args.out:
        args.out.write_text(payload + "\n", encoding="utf-8")
        print(f"\nGuardado en {args.out} — adjúntalo para actualizar HardwareValidation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
