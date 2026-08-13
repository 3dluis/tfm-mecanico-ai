"""Congelación de los brazos de detección (F10) → manifiesto con checksums.

Fija las versiones EXACTAS de AM-W-v1 (LOF), event-baseline-z@0.2.0 y AM-WE-d antes del
experimento confirmatorio PROTO-CONF-001: código fuente (sha256), configs/suites,
umbrales, features, preprocesado, datasets y firma de contexto. Tras la congelación,
cualquier mejora es una VERSIÓN NUEVA — estos brazos no se retocan después de ver el
test confirmatorio.

Uso: python tools/freeze_arms.py   → ai-models/registry/frozen/arms-freeze-v1.json
El manifiesto es determinista para un commit dado (el commit se registra dentro).
"""

import hashlib
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
OUT = REPO_ROOT / "ai-models" / "registry" / "frozen" / "arms-freeze-v1.json"

#: Ficheros cuyo sha256 define el comportamiento de los brazos congelados.
FROZEN_FILES = [
    # detección por ventana (AM-W-v1)
    "ai-models/src/ai_models/anomaly/baselines.py",  # LOF k=10 exacto
    "shared/src/mecanico_contracts/features.py",  # fs1 (42 features) + preprocesado
    "ai-models/src/ai_models/evaluation/protocol.py",  # regla de umbral 1% FPR
    # detección por evento (event-baseline-z@0.2.0)
    "diagnostic-agent/src/diagnostic_agent/events/detector.py",  # ed:1
    "diagnostic-agent/src/diagnostic_agent/events/features.py",  # efv:1 + context_signature
    "diagnostic-agent/src/diagnostic_agent/events/baseline.py",  # scoring media/σ + suelos
    # datos de ajuste (el confirmatorio usa OTROS datos)
    "obd-lab/scenarios/suite_v1.yaml",
    "obd-lab/scenarios/suite_v1_train_ext.yaml",
    # generador (determina los bytes de las sesiones)
    "obd-lab/src/obd_lab/signals.py",
    "obd-lab/src/obd_lab/generate.py",
    "obd-lab/src/obd_lab/emulator/encoding.py",
    "obd-lab/src/obd_lab/injection/faults.py",
    # harness R2 congelado + benchmark inmutable
    "tools/llm_smoke_deep.py",
    "tools/bench_agent_diagnostics.py",
    "benchmarks/agent-diagnostics/cases_v1.yaml",
]

FROZEN_SPEC = {
    "freeze_id": "arms-freeze-v1",
    "frozen_for": "PROTO-CONF-001 (docs/experiments/preregistered/)",
    "rule": (
        "Estos brazos NO se afinan tras ver el test confirmatorio; cualquier mejora "
        "posterior es una versión nueva (decisión del autor, F10 §7)."
    ),
    "arms": {
        "AM-W-v1": {
            "model": "anom-lof@0.1.0",
            "algorithm": "LocalOutlierFactor(n_neighbors=10, novelty=True) + StandardScaler",
            "features": "fs1 (42 features, ventana 60 ticks / stride 30)",
            "preprocessing": "embedded-standard-scaler + cuantización J1979 + warmup gating",
            "train_data": "obd-lab-suite-v1@1 split train (6 sesiones normales)",
            "threshold": 0.163197,
            "threshold_rule": "cuantil (1 - 0.01) de scores de train normal",
            "normalization": "StandardScaler ajustado solo con train",
        },
        "AM-E-v0.2.0": {
            "model": "event-baseline-z@0.2.0",
            "detector": "ed:1 (máquina de estados; umbrales DetectorConfig por defecto)",
            "features": "efv:1 (20 features por evento) · preprocessing pp:1",
            "context_signature": (
                "event_type|banda_velocidad(0-40/40-80/80-120)"
                "|térmico(cold/warming/warm)|duración(d0-8s/d8-30s/d30s+)"
            ),
            "grouping": "event_type + context_signature (MIN_SAMPLES=5)",
            "scoring": "media/σ con suelos max(std, 0.05|mean|, 1e-3) — robusto RECHAZADO",
            "train_data": "obd-lab-suite-v1@1.1 train ampliado (22 sesiones normales)",
            "threshold": 57.496,
            "threshold_rule": "cuantil 1% FPR de scores LOSO sobre train normal",
        },
        "AM-WE-d": {
            "model": "anom-combined-we@0.2.0",
            "combination": (
                "OR por tick de AM-W-v1 y AM-E-v0.2.0 (estrategia explícita y "
                "auditable; sin umbral propio; configurable vía RuntimeConfig.anomaly_mode)"
            ),
        },
    },
}


def main() -> int:
    files = {}
    for rel in FROZEN_FILES:
        p = REPO_ROOT / rel
        files[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    git = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    manifest = {**FROZEN_SPEC, "git_commit_at_freeze": git or "sin-git", "sha256": files}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(f"Congelación escrita: {OUT} ({len(files)} ficheros)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
