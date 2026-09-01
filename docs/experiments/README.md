# Registro de experimentos

Un informe por fase, con el mismo esqueleto: qué se hizo, con qué entradas, qué
se obtuvo, qué se comprobó y qué queda abierto.

Convención de nombre: `E<n>_<tema>.md`.

| Fase | Informe | Estado |
|---|---|---|
| E1 entorno | [E1_entorno.md](E1_entorno.md) | cerrada |
| E2 datos sintéticos | — | pendiente |
| E3 datos reales | — | pendiente |
| E4 análisis exploratorio | — | pendiente |
| E5 preprocesamiento | — | pendiente |
| E6 baseline | — | pendiente |
| E7 modelo temporal | — | pendiente |
| E8 evaluación del modelo | — | pendiente |
| E9 atribución | — | pendiente |
| E10 corpus | — | pendiente |
| E11 pgvector | — | pendiente |
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
