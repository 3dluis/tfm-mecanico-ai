# ADR-0031 — Apertura de la línea experimental ML sobre la representación wide (F13)

**Estado:** Aceptada (decisión del autor, F13 · 2026-08-13)
**Relacionada con:** ADR-0009 (separación ML/LLM), ADR-0011 (protocolo de baselines),
ADR-0024 (tracking y selección), ADR-0025 (representación wide), ADR-0026 (sync:v1),
ADR-0027 (NULL ≠ 0), ADR-0030 (PostgreSQL + pgvector edge)

## Contexto

La PI (Opción B) exige análisis contextual y **longitudinal** de datos OBD-II. Tras F11/F12
existe una representación horizontal canónica (`VehicleTelemetrySnapshot`) y una plataforma
de persistencia oficial, pero el pipeline ML vigente (F3) sigue construyendo datasets por
el camino long (sesión → series → ventanas → fs1). F12 dejó declarado que la lectura
orientada a ML sobre snapshots era el «siguiente cuello de botella real a resolver antes de
entrenar sobre snapshots». Además, el autor ha decidido priorizar el entrenamiento de
modelos que aprendan el comportamiento del vehículo (autoencoders, modelos secuenciales,
embeddings y descubrimiento de patrones), líneas hasta ahora en estado PLANNED/COULD.

## Decisión

1. **Se abre formalmente la línea experimental ML de F13**, gobernada por
   `docs/experiments/protocolo_ml_v1.md` (exploratoria; la evidencia confirmatoria sigue
   sujeta al pre-registro pendiente de congelación).
2. **La entrada canónica de los experimentos ML es el snapshot wide** vía la matriz
   columnar `ai_models.data.snapshot_matrix` (NaN para NULL, máscara de validez, rechazo
   de rejillas mixtas). El camino long de F3 se conserva como referencia; ambos quedan
   validados por paridad exacta (EXP-ANOM-005), cumpliendo la condición de migración
   gradual de ADR-0025. No se adopta ningún modelo EAV/vertical para el pipeline de ML.
3. **El mapeo PID→campo de snapshot se promueve al contrato compartido**
   (`PID_TO_SNAPSHOT_FIELD`, contratos v0.5.1, cambio aditivo); el edge lo aliasa. Un test
   de integración garantiza que entrenamiento e inferencia usan la misma correspondencia.
4. **Se reactiva la línea de autoencoders/modelos temporales como exploratoria** (la
   había recortado el cronograma), manteniendo intacta la condición de adopción de
   ADR-0011: solo sustituyen a LOF si lo superan en held-out con FPR ≤. El orden es
   incremental: AE denso (EXP-ANOM-006) → LSTM/GRU-AE (EXP-ANOM-007, condicionado) →
   descubrimiento con embeddings + HDBSCAN (EXP-PAT-001/002). TCN/Transformer solo con
   necesidad comparativa declarada.
5. **Nomenclatura**: los experimentos de la línea usan las familias vigentes
   (`EXP-ANOM-*` para detección; nueva familia `EXP-PAT-*` para descubrimiento de
   patrones). La serie externa EXP-ML-001..014 queda mapeada en el protocolo §7. IDs
   ejecutados y reservados no se reutilizan.
6. **Ventanas temporales como hiperparámetro** ({10,30,60,120} s de partida, 1 Hz), con
   60/30 congelado para toda comparación con arms-freeze-v1.
7. **Semillas exploratorias de F13+: rango 401–599**, disjunto de todos los bloques
   reservados por el pre-registro.
8. **Embeddings de comportamiento en pgvector solo asociados a anomalías/casos/patrones
   candidatos** — la telemetría no se vectoriza (regla 8 de REGLAS.md). Indexar ventanas
   normales requeriría un ADR nuevo.

## Alternativas consideradas

- *Repetir los baselines tabulares como «nivel 1» de la nueva línea:* rechazada —
  EXP-ANOM-001 ya los comparó con este protocolo (IForest/z-score REJECTED); duplicaría
  identificadores y evidencia. El valor nuevo era validar el camino de datos, no re-elegir
  el modelo (por eso EXP-ANOM-005 es un experimento de paridad).
- *Construir el dataset ML leyendo directamente de PostgreSQL:* pospuesta — el
  entrenamiento no debe depender de la base (los experimentos leen JSONL/matriz); la
  lectura columnar SQL (`SELECT` por columnas / COPY) queda como optimización a medir
  cuando los volúmenes lo exijan.
- *MLflow como registro:* re-rechazada (ADR-0024): el registro filesystem + runs.jsonl
  cubre el esquema de reproducibilidad completo con coste mínimo.
- *Fijar ya fs2:* rechazada — las features nuevas se declaran como borrador justificado y
  solo se promueven con evidencia (protocolo §4).

## Consecuencias

- Los experimentos futuros de la línea comparten dataset, splits y protocolo con
  EXP-ANOM-001/002/003, preservando comparabilidad histórica.
- `ai_models.data` queda por fin versionado (la regla `data/` del `.gitignore` raíz lo
  ocultaba; corregida a `/data/`): el módulo `dataset.py` que importaban
  `evaluation/protocol.py` y `e1_baselines.py` entra en el repositorio.
- El coste del camino wide medido en EXP-ANOM-005 (~1 s extra por suite completa para
  construir snapshots+matriz) es aceptable; la lectura masiva desde PostgreSQL sigue
  pendiente y declarada.
- Riesgo declarado y vigente: profundizar en autoencoders puede consumir calendario de
  septiembre (F7); la condición de adopción de ADR-0011 y el orden incremental acotan ese
  riesgo.
