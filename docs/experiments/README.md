# Registro de experimentos

Un informe por fase, con el mismo esqueleto: qué se hizo, con qué entradas, qué
se obtuvo, qué se comprobó y qué queda abierto.

Convención de nombre: `E<n>_<tema>.md`.

| Fase | Informe | Estado |
|---|---|---|
| E1 entorno | [E1_entorno.md](E1_entorno.md) | cerrada |
| E2 datos sintéticos | [E2_datos_sinteticos.md](E2_datos_sinteticos.md) | cerrada |
| E3 datos reales | — | **bloqueada** — falta decidir la fuente |
| E4 análisis exploratorio | [E4_eda_temporal.md](E4_eda_temporal.md) | cerrada |
| E5 preprocesamiento | [E5_preprocesamiento.md](E5_preprocesamiento.md) | cerrada |
| E6 baseline | [E6_baseline.md](E6_baseline.md) | cerrada |
| E7 modelo temporal | [E7_modelo_temporal.md](E7_modelo_temporal.md) | cerrada |
| E8 evaluación del modelo | — | pendiente |
| E9 atribución | — | pendiente |
| E10 corpus documental por vehículo | [E10_corpus_vehiculo.md](E10_corpus_vehiculo.md) | infraestructura cerrada, corpus vacío |
| E11 pgvector | [E11_carga_rag.md](E11_carga_rag.md) | cerrada |
| E12 evaluación de recuperación | — | pendiente |
| E13 integración del agente | — | pendiente |
| E14 trazabilidad | — | pendiente |
| E15 suficiencia | — | pendiente |
| E16 abstención | — | pendiente |
| E17 condiciones de evidencia | — | pendiente |
| E18 ablaciones | — | pendiente |
| E19 evaluación final | — | pendiente |
| E20 demostración | — | pendiente |

Cada ejecución con resultados numéricos guarda además su registro en
`experiments/` como JSON, con `experiment_id`, commit, versiones de dataset,
corpus, modelo, embeddings, proveedor y prompt, semilla, parámetros y métricas.

Ningún número llega a la memoria del TFM sin proceder de uno de esos registros.
