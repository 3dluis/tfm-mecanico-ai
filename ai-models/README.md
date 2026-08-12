# ai-models

Investigación, experimentación, entrenamiento, evaluación, comparación y exportación de modelos.
**Nunca se ejecuta en el edge** (ADR-0009): el edge consume artefactos ONNX + manifiesto.

Estructura: data/ · preprocessing/ · features/ · anomaly/ · clustering/ · evaluation/ · export/ ·
notebooks/ · experiments/ (uno por hipótesis H1–H4, reproducibles por semilla).

Protocolo de evaluación: F1 por eventos sin point-adjustment, escenarios held-out
(ver docs/estado_del_arte/linea_b y docs/04 RI1).

## Registro de experimentos

Todo run se registra en `experiments/runs.jsonl` (suite, git sha, modelo, parámetros,
semilla, umbral, métricas por split y categoría, latencia, RSS). Resultados de baselines:
`experiments/e1_results.csv` y ADR-0011. Ciclo de promoción de modelos: ADR-0009 +
[data-architecture/07](../docs/data-architecture/07_provenance_versionado.md).
