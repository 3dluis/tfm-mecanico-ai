# PROTO-CONF-001 — Protocolo confirmatorio de H-EVT (pre-registro v1.0)

**Estado: PRE-REGISTRADO — NO EJECUTADO.** Este protocolo queda congelado en el commit
que lo introduce (el manifiesto `ai-models/registry/frozen/arms-freeze-v1.json` fija
además los brazos con checksums). **Regla: no se modifica retroactivamente**; cualquier
cambio necesario ANTES de ejecutar produce PROTO-CONF-001 v1.1/v2 con su justificación.
Tras ejecutar, el protocolo y sus resultados son inmutables.

## 1. Pregunta experimental (alineada con H-EVT / PI.2)

> ¿Mejora la combinación de un detector no supervisado basado en ventanas temporales y
> un detector contextual basado en eventos vehiculares la detección de anomalías —
> en particular las relacionales/multivariables no documentadas — respecto al detector
> basado únicamente en ventanas, manteniendo una tasa de falsas alarmas equivalente?

Redacción académica evaluada: se formula sobre la COMBINACIÓN (hallazgo exploratorio
F8/F9) y no sobre la sustitución (refutada exploratoriamente en EXP-ANOM-002); usa
exclusivamente la nomenclatura de la alineación v2 (H-EVT; correspondencia §6).

## 2. Hipótesis (congeladas)

- **H-EVT-C1 (principal):** AM-WE-d detecta ≥ episodios held-out relacionales que AM-W
  en el conjunto confirmatorio, con FPR tick-level ≤ FPR(AM-W) + 0.02 absoluto.
- **H-EVT-C2 (secundaria):** el recall tick-level de AM-WE-d supera al de AM-W en ≥ 0.03
  absoluto en el agregado confirmatorio.
- **H-EVT-C3 (calidad del brazo de eventos):** AM-E-v0.2.0 mantiene FPR tick-level
  ≤ 0.02 y event precision ≥ 0.90 sobre normales confirmatorias.
- **H0 correspondientes:** ausencia de dichas diferencias/límites. La NO confirmación se
  documenta con el mismo detalle que la confirmación.

## 3. Variables

Independiente: brazo de detección (AM-W | AM-E-v0.2.0 | AM-WE-d — congelados).
Dependientes primarias/secundarias en §6. Controladas: datos (§7), semillas, hardware,
versiones (§10). No se introducen covariables post-hoc.

## 4. Modelos, features, thresholds (CONGELADOS — freeze-v1)

Exactamente los del manifiesto `arms-freeze-v1.json` (sha256 por fichero + commit):
AM-W-v1 = LOF k=10 + scaler, features fs1, umbral **0.163197** (cuantil 1 % FPR de
train v1); AM-E-v0.2.0 = ed:1 + efv:1/pp:1 + context_signature v1 + media/σ con suelos,
baselines de train v1.1, umbral **57.496** (cuantil 1 % FPR LOSO); AM-WE-d = OR por
tick. **Ningún reajuste tras ver datos confirmatorios**; si un brazo se retoca, es una
versión nueva y este protocolo no le aplica.

## 5. Datasets y splits

- **DEVELOPMENT (ajuste):** suite v1 train (6) + validación (7) + train-ext v1.1 (16).
- **EXPLORATORY (ya gastado en E1/E2/E3):** suite v1 test (8 sesiones, seeds 301–322) —
  NO cuenta como evidencia confirmatoria.
- **CONFIRMATORY (este protocolo):** `suite_conf_v1.yaml` — 15 sesiones nuevas, seeds
  901–925 disjuntas, con parámetros de fallo NO usados en ajuste (severity 0.5, drift
  0.12), held-out relacional replicado en ambos perfiles (2 urbano + 1 autovía) y los
  dos held-out nunca detectados (coolfreeze, jointdrift) como test de techo.
  **Regla de ocultación:** estas sesiones no se generan ni evalúan hasta la ejecución
  del protocolo; ninguna decisión de ajuste puede depender de ellas.

## 6. Métricas

**Primarias:** FPR tick-level sobre sesiones normales confirmatorias; recall de
episodios held-out relacionales (c-corrbreak-*); recall tick-level agregado.
**Secundarias:** P/F1 tick-level; event precision/recall/F1 y false-events-por-sesión
normal (brazos de eventos); retardo de detección por episodio; episodios conocidos
detectados; cobertura de scoring; coste computacional (t_features, t_scoring, e2e, RSS).
Las métricas tick-level se reportan SIEMPRE, favorables o no.

## 7. Criterios de exclusión y calidad de datos

Se excluye una sesión confirmatoria solo por defecto TÉCNICO de generación (serie vacía
o NaN) — documentándolo; jamás por su resultado. Sin point-adjustment. Warm-up gating
idéntico al congelado (2 primeras ventanas). Ningún dato confirmatorio se re-genera con
otra semilla tras haber sido evaluado.

## 8. Criterios de éxito y análisis

- **Confirmación:** H-EVT-C1 y C3 se cumplen (C2 informa pero no decide).
- **Refutación parcial/total:** se documenta igual; AM-WE-d NO se promueve a VALIDATED y
  vuelve a iteración exploratoria con versión nueva.
- **Análisis estadístico:** con 15 sesiones (5 held-out) el análisis es de recuento e
  intervalos exactos (Clopper-Pearson 95 % para FPR por tick agregado; conteo de
  episodios con lectura direccional declarada). Sin tests de significación sobre 5
  episodios — la limitación se declara; la replicación (real/HCRL) queda para fases
  posteriores. Comparaciones solo entre los tres brazos pre-declarados.
- **Reglas de parada:** una sola ejecución del protocolo, sin repeticiones ni reintentos;
  si el runner falla técnicamente, se corrige el fallo técnico y se re-ejecuta ÍNTEGRO
  documentando el motivo (el fallo técnico no puede depender de métricas).

## 9. Resultado y promociones

Si se confirma: `anom-combined-we@0.2.0` CANDIDATE→VALIDATED y `event-baseline-z@0.2.0`
CANDIDATE→VALIDATED (la aprobación final sigue siendo del autor). EDGE_APPROVED sigue
requiriendo además la matriz hardware (ARM64/RPi) — independiente de este protocolo.

## 10. Hardware y software

Ejecución en sandbox-x86 (4 CPU/8 GB, proxy del perfil RPi; las latencias se interpretan
como x86). Software congelado por commit del freeze + `pyproject.toml` (Python 3.11,
scikit-learn/onnxruntime/numpy en las versiones del lockfile del entorno). El runner
será `experiments/e4_confirmatory.py`, que deberá: cargar el freeze, verificar los
sha256 ANTES de ejecutar (aborta si difieren), generar suite_conf_v1, evaluar los 3
brazos y registrar `EXP-ANOM-004` con `study_type='confirmatory'`.

## 11. Desviaciones

Cualquier desviación durante la ejecución se registra en el informe de resultados
(docs/experiments/results/) con timestamp y motivo. Una desviación que afecte al diseño
invalida la condición confirmatoria del run.
