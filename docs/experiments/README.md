# Registro de experimentos

Un informe por fase, con el mismo esqueleto: qué se hizo, con qué entradas, qué
se obtuvo, qué se comprobó y qué queda abierto.

Convención de nombre: `E<n>_<tema>.md`.

| Fase | Informe | Estado |
|---|---|---|
| E1 entorno | [E1_entorno.md](E1_entorno.md) | cerrada |
| E2 datos sintéticos | [E2_datos_sinteticos.md](E2_datos_sinteticos.md) | cerrada |
| E3 datos reales | — | pendiente — validación externa desde ADR-003; falta decidir la fuente |
| E4 análisis exploratorio | [E4_eda_temporal.md](E4_eda_temporal.md) | cerrada |
| E5 preprocesamiento | [E5_preprocesamiento.md](E5_preprocesamiento.md) | cerrada |
| E6 baseline | [E6_baseline.md](E6_baseline.md) | cerrada |
| E7 modelo temporal | [E7_modelo_temporal.md](E7_modelo_temporal.md) | cerrada |
| E8 evaluación del modelo | — | pendiente |
| E9 atribución | [E9_atribucion.md](E9_atribucion.md) | cerrada |
| E10 corpus documental por vehículo | [E10_corpus_vehiculo.md](E10_corpus_vehiculo.md) | infraestructura cerrada, corpus vacío |
| E11 pgvector | [E11_carga_rag.md](E11_carga_rag.md) | cerrada |
| E12 evaluación de recuperación | [E12_evaluacion_recuperacion.md](E12_evaluacion_recuperacion.md) | cerrada |
| E13 integración del agente | [E13_agente_slm.md](E13_agente_slm.md) | cerrada — v2: 9/9 válidas, 0 citas inventadas, 0 fallos de esquema (4-09); 17/17 sobre el conjunto ampliado con recuperación canónica (14-09, [resultado-rerun-a.md](resultado-rerun-a.md)) |
| E14 trazabilidad | — | pendiente |
| E15 suficiencia | [E15_suficiencia.md](E15_suficiencia.md) | cerrada |
| E16 abstención | — | pendiente |
| E17 condiciones de evidencia | integrada en E15; diagnóstico del distractor en [resultado-rerun-a.md](resultado-rerun-a.md) | parcial — FULL, ABSENT y PARTIAL puntuadas; DISTRACTOR redundante con PARTIAL en dos de tres fallos |
| E18 ablaciones | — | pendiente |
| E19 evaluación final | — | pendiente |
| E20 demostración | — | pendiente |
| RERUN-A reejecución canónica | [resultado-rerun-a.md](resultado-rerun-a.md) | ejecutada el 13/14-09-2026: decisiones idénticas (15/17), conjuntos recuperados distintos en 10/17 casos |

Hallazgos y resultados intermedios: [hallazgo-lexical-support-confound.md](hallazgo-lexical-support-confound.md), [hallazgo-puerta-dtc-ausente.md](hallazgo-puerta-dtc-ausente.md), [hallazgo-filtro-motor.md](hallazgo-filtro-motor.md), [resultado-verificador-v2-1.md](resultado-verificador-v2-1.md), [resultado-no-oracular-y-adverso.md](resultado-no-oracular-y-adverso.md).

Cada ejecución con resultados numéricos guarda además su registro en
`experiments/` como JSON, con `experiment_id`, commit, versiones de dataset,
corpus, modelo, embeddings, proveedor y prompt, semilla, parámetros y métricas.

Ningún número llega a la memoria del TFM sin proceder de uno de esos registros.
