# 01 — Modelo conceptual

[← Índice](README.md)

## Por qué este modelo

La pregunta de investigación exige poder afirmar, con evidencia auditable, tres cosas:
(1) *qué observó* el sistema (telemetría), (2) *qué infirió y por qué* (detección y
diagnóstico), y (3) *qué aprendió con el tiempo* (memoria evolutiva). El modelo conceptual
se organiza en cuatro dominios de información conectados por trazabilidad obligatoria.

## Dominio 1 — Telemetría (los hechos)

```
TelemetrySession ──< OBDObservation(=OBDReading)  [RAW LONG]
        │
        └──< TelemetryPoint [NORMALIZED LONG]
                    │
                    ├──< VehicleTelemetrySnapshot [NORMALIZED WIDE / TIME-ALIGNED]
                    │            └──> TelemetryWindow / VehicleEvent   (camino wide, PARALELO)
                    │
                    └──< TelemetryWindow [DERIVED]                      (camino F3 VIGENTE)
                                    │
                                    └── FeatureVector [DERIVED]
                                            │
                                            └── ModelInference [INFERRED]
                                                    │
                                                    └── DetectedAnomaly [INFERRED]
```

**`VehicleTelemetrySnapshot`** ([11](11_vehicle_telemetry_snapshot.md), ADR-0025) es la
representación **canónica horizontal**: una fila = el estado multivariable observable del
vehículo en un instante de la rejilla canónica (`rpm | speed | maf | map | stft | ltft | …`),
alineado por la política `sync:v1` (ADR-0026). **No sustituye** a `OBDObservation` (RAW LONG)
ni a `TelemetryPoint` (NORMALIZED LONG), y **no es una inferencia**: es el mismo hecho
observado, pivotado y alineado, con vuelta garantizada a las observaciones de origen
(`session_id + sequence_number`, verificado en `tests-integration/test_snapshot_e2e.py`).
Nunca contiene features derivadas (medias, desviaciones, correlaciones): esas viven en
`FeatureVector`/`EventFeatureVector`. Una señal no disponible es `NULL` con su *quality flag*,
**jamás 0** (ADR-0027). Su papel en la PI es habilitar el análisis **longitudinal y
multivariable** (meses de snapshots → eventos comparables → baselines por vehículo →
evolución del comportamiento antes de que aparezca un DTC), sin afirmar todavía que mejore
los resultados: eso lo deciden los experimentos.

`TelemetrySession` es la entidad central de contexto: registra **origen** (`SessionSource`:
REAL_VEHICLE / OBD_SIMULATOR / DATASET_REPLAY / SYNTHETIC_GENERATOR / BENCH_TEST), semilla,
escenario, dataset, versiones de generador y software — todo lo necesario para reproducir un
experimento exactamente. Cada eslabón referencia al anterior por id: desde una anomalía se
reconstruye la cadena completa hasta las observaciones crudas
(verificado por `tests-integration/test_traceability_e2e.py`).

## Dominio 2 — Diagnóstico (el razonamiento)

```
DetectedAnomaly ──> DiagnosticCase ──< DiagnosticHypothesis (rank, estado, confianza)
                          │                     │
                          │                     └──< DiagnosticEvidence (supports/contradicts)
                          ├──< AgentRun ──< AgentStep · RetrievalEvent
                          └──  ProvenanceRecord (obligatoria)
```

Un caso puede tener varias hipótesis en competencia; cada una acumula evidencias **a favor y
en contra** producidas por el nodo determinista `verify`. El diagnóstico nunca es solo texto:
la explicación final se compone desde estas estructuras.

## Dominio 3 — Memoria (el aprendizaje)

Tres niveles con papel distinto ([06](06_memoria_evolutiva.md)): **working** (estado del grafo;
persiste solo su traza como `AgentRun`/`AgentStep`), **episódica** (`CaseMemory`: experiencias
recuperables por similitud, con nivel epistemológico), **semántica/evolutiva**
(`LearnedPattern` + `PatternRelation`: patrones consolidados de múltiples casos — la memoria
evolutiva de la PI). `DiagnosticFeedback` y `MaintenanceEvent` cierran el lazo con la verdad
externa.

## Dominio 4 — Conocimiento y modelos (los recursos)

`KnowledgeDocument`/`KnowledgeChunk` (corpus RAG citable) y `ModelManifest` (gobernanza del
ciclo de modelos ML, ADR-0009). Ambos son consumidos, nunca modificados, por el agente.

## Invariantes del modelo

1. Todo dato pertenece a una clase y las clases solo fluyen hacia delante (nada INFERRED
   alimenta la cadena como si fuera RAW). Taxonomía vigente: **RAW LONG** (`OBDObservation`) ·
   **NORMALIZED LONG** (`TelemetryPoint`) · **NORMALIZED WIDE/ALIGNED**
   (`VehicleTelemetrySnapshot`) · **DERIVED** (`TelemetryWindow`, `VehicleEvent`,
   `EventFeatureVector`, `FeatureVector`) · **INFERRED** (`ModelInference`, `DetectedAnomaly`,
   `DiagnosticHypothesis`).
2. Todo artefacto INFERRED de cara al usuario (caso, patrón) lleva `ProvenanceRecord`.
3. La detección de anomalías es siempre matemática; el LLM razona sobre anomalías ya
   detectadas (separación ML/LLM, ADR-0009).
4. Los ids son globalmente únicos (UUID) — prerequisito de la sincronización idempotente.
5. `schema_version` viaja en todo mensaje y fila.
6. El peso de la experiencia depende de su origen: `EpistemicLevel` en memoria
   (SIMULATED < … < HUMAN_VALIDATED).

Diagrama ER completo: [diagrams/er-model.mmd](diagrams/er-model.mmd).
