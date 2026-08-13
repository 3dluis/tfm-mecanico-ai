# EXP-ANOM-005 — Paridad del camino wide (snapshot → matriz → ventanas → fs1)

**Fase 13 · 2026-08-13 · exploratorio · runner `ai-models/experiments/e4_wide_parity.py`
· config `ai-models/configs/exp-anom-005.yaml` · seed 42 · sandbox-x86 (4 CPU / 8 GB)**

## Objetivo

Verificar que el camino wide canónico (sesión → `VehicleTelemetrySnapshot` con `sync:v1`
identidad → matriz columnar `ai_models.data.snapshot_matrix` → ventanas 60/30 → features
fs1) produce EXACTAMENTE el mismo dataset y las mismas métricas que el camino long vigente
de F3 (`ai_models.data.dataset.build_dataset`). ADR-0025 condicionaba la migración de
consumidores del snapshot a que «ambos estén validados»: este experimento es esa
validación para el consumidor ML, y es la precondición de toda la línea F13 (autoencoders,
ventanas como hiperparámetro, embeddings) para no perder comparabilidad con
EXP-ANOM-001/002/003.

## Protocolo

Idéntico a E1/ADR-0011 (umbral = cuantil 1 % FPR sobre train normal; métricas point-wise
sin point-adjustment + por episodio; held-out jamás interviene en el ajuste). La única
variable independiente es el CAMINO de construcción del dataset; modelos, hiperparámetros,
semilla, split y features son los de EXP-ANOM-001. Criterio de éxito pre-declarado en la
config: paridad exacta (no aproximada) de features, etiquetas, offsets, umbrales y
métricas.

## Datos

obd-lab-suite-v1@1 (21 sesiones, split suite-v1-split-1 congelado), regenerada por semilla
(reproducibilidad byte a byte del emulador). Ninguna semilla reservada del pre-registro se
ha tocado.

## Resultados

**Paridad de dataset (features byte a byte):**

| Split | long | wide | `max_abs_feature_diff` | etiquetas/sesiones/offsets | descartadas por validez | coste snapshots+matriz |
|---|---|---|---|---|---|---|
| train | (324, 42) | (324, 42) | 0.0 | idénticos | 0 | 0.34 s |
| validation | (403, 42) | (403, 42) | 0.0 | idénticos | 0 | 0.32 s |
| test | (472, 42) | (472, 42) | 0.0 | idénticos | 0 | 0.38 s |

**Paridad de métricas (camino wide; idénticas dígito a dígito a las del camino long en la
misma ejecución y a las registradas de EXP-ANOM-001):**

| Modelo | Umbral | val F1 | val FPR | test F1 | test FPR | Episodios | Retardo | Held-out R | ms/ventana |
|---|---|---|---|---|---|---|---|---|---|
| robust_zscore | 316.683652 | 0.5253 | 0.0515 | 0.4425 | 0.1034 | 2/6 | 75.0 s | 0.0 | 0.000 |
| isolation_forest | 0.067288 | 0.0188 | 0.0103 | 0.0 | 0.0172 | 0/6 | — | 0.0 | 0.070 |
| lof | **0.163197** | 0.7733 | 0.0103 | 0.6448 | 0.0345 | 4/6 | 37.5 s | 0.25 | 0.004 |
| ocsvm | 0.000241 | 0.8152 | 0.0464 | 0.6835 | 0.0862 | 6/6 | 225.0 s | 0.35 | 0.002 |

RSS pico del runner: 183.1 MB. El umbral de LOF (0.163197) coincide exactamente con el
congelado en `arms-freeze-v1.json`, lo que ancla la cadena completa de reproducción
(semillas → emulador → snapshots → matriz → features → modelo → umbral).

## Interpretación

La paridad es exacta por construcción y ahora está verificada por ejecución: la matriz
columnar reproduce las mismas ventanas que el pivot long, y `feature_vector` es la única
definición de features en juego (contrato compartido). Esto significa que (1) el snapshot
wide puede sustituir al camino long como base de los experimentos ML **sin ninguna
discontinuidad estadística** — cualquier diferencia futura entre un modelo nuevo y los
baselines será atribuible al modelo, nunca al camino de datos; (2) el coste añadido del
camino wide es ~1 s por suite completa (construcción de snapshots + matriz), despreciable
frente al entrenamiento; (3) la política de validez de ventanas (descarte contabilizado,
sin imputación) no descartó nada en datos de simulador — se ejercita en tests con datos
degradados, y será relevante con datos reales/replay.

Nota honesta: este experimento NO mide la lectura desde PostgreSQL (los snapshots se
construyen en memoria desde JSONL); el cuello de botella de lectura masiva ORM→Pydantic
identificado en F11/F12 sigue pendiente para volúmenes de meses.

## Limitaciones

Entorno emulado, 1 Hz, 12 PIDs completos (sin missing reales); sandbox x86 (ARM64/RPi5
sin validar); la paridad se ha verificado para fs1/60/30 — esquemas o rejillas nuevos
deberán re-ejecutar el runner (make experiments-wide).

## Decisión

- El camino wide queda **VALIDADO como entrada canónica para ML** (ADR-0031).
- La selección de modelos vigente NO cambia (LOF k=10 sigue SELECTED; IForest/z-score
  siguen REJECTED; este experimento no re-evalúa modelos).
- Próximo experimento: **EXP-ANOM-006** (autoencoder multivariable pequeño sobre el camino
  wide, con barrido de ventana {10,30,60,120} s), según protocolo ML v1 §5.
