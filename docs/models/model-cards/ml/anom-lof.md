# Model Card — anom-lof (LOF k=10)

**Fuente de métricas:** `ai-models/registry/training-runs/TR-E1-LOF.json` ·
`e1_results.csv` · informe F3 §4 · ADR-0011. Sin recálculo.

## Identificación
- **model_id:** `anom-lof` · **name:** lof · **versions:** 0.1.0 (E1, SUPERSEDED) /
  **0.2.0 (paquete ONNX, VALIDATED — modelo por defecto del edge)**
- **model_type:** ml · **model_family:** lof · **purpose:** detección no supervisada de
  anomalías multivariables sobre ventanas de telemetría (60 s, stride 30)
- **owner/component:** `diagnostic-agent:detection` (inferencia) / `ai-models` (ciclo de vida)

## Origen
- **algorithm:** LocalOutlierFactor(n_neighbors=10, novelty=True), scikit-learn;
  scaler estándar embebido en el pipeline · **training_method:** ajuste no supervisado
  solo con ventanas normales · **adaptation_method:** n/a

## Datos (linaje)
- **dataset:** `obd-lab-suite-v1@1` · **split:** `suite-v1-split-1`
  (normal→train/val; known_fault+held_out→SOLO test; held-out jamás usado para ajustar)

## Features y configuración
- **features:** `fs1` (42 features canónicas) · **preprocessing:** embedded-standard-scaler
- **hyperparameters:** k=10, novelty=True · **seed:** 42 · **git:** 69a1e4d
- **threshold:** 0.163197 — cuantil de train-normal a 1 % FPR objetivo (ADR-0011);
  sin point-adjustment · **scoring:** mayor = más anómalo

## Artefacto
- **format:** ONNX (skl2onnx) · **path:** `make export` → `models/model-lof-0.2.0/`
  (reproducible con seed 42; checksum en el manifest al exportar) · **framework:**
  scikit-learn → onnxruntime · **paridad sklearn↔ONNX:** exacta (test F3/F4)

## Hardware
- **training/evaluation:** sandbox-x86 (límites 4 CPU/8 GB, perfil RPi emulado)
- **edge_validation:** sandbox-x86 APPROVED (pipeline vivo emulador→ONNX);
  arm64-container NOT_TESTED (pendiente A2/A3) · rpi5 NOT_TESTED (L2)

## Métricas (test; protocolo ADR-0011)
| métrica | valor |
|---|---|
| F1 | **0.6448** · FPR **0.0345** |
| recall fallos conocidos | 0.975 |
| recall held-out (point-wise) | 0.25 |
| episodios held-out detectados | **4/6** · retardo medio 37.5 s |
| inferencia | 0.007 ms/ventana (x86) · fit 0.075 s · RSS pico 171.5 MB |

## Evaluaciones posteriores
- **EXP-ANOM-002 (F8, marco por tick):** F1 test 0.67 · FPR 0.067 · 4/6 episodios ·
  held-out 2/4 · retardo 15 s — sigue siendo el mejor detector individual; el umbral
  train-only reprodujo exactamente el de E1 (0.1632). Punto débil confirmado: apenas
  delimita el desacoplo RPM/MAF urbano (R=0.25), donde el brazo de eventos localiza
  R=0.73 → complementariedad documentada en la
  [comparación v1](../../comparisons/anomaly_window_vs_event_v1.md).

## Limitaciones y modos de fallo conocidos (✍)
- El recall point-wise held-out (0.25) es bajo: detecta los EPISODIOS pero no todos sus
  puntos — por eso el protocolo prioriza métricas por episodio.
- Umbral calibrado sobre datos sintéticos cuantizados; requiere recalibración con datos
  reales (HCRL/vehículo) antes de cualquier afirmación fuera del simulador.
- Sensible a la densidad local: contextos de conducción no vistos en train (p. ej.
  montaña) pueden producir falsos positivos (riesgo OOD).
- Ventanas de warm-up: las 2 primeras ventanas de cada sesión se descartan (gating F3).
- **Unsupported:** clasificación del TIPO de fallo (solo detecta desviación); decisiones
  de seguridad en tiempo real.

## Legal
- **license:** scikit-learn BSD-3 · **source:** implementación propia sobre sklearn ·
  **references:** informe F3 (interno); Breunig et al. 2000 (LOF) — cita formal en EdA.
