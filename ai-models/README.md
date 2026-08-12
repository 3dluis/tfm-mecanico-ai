# ai-models

Investigación, experimentación, entrenamiento, evaluación, comparación y exportación de modelos.
**Nunca se ejecuta en el edge** (ADR-0009): el edge consume artefactos ONNX + manifiesto.

**Propósito formal (F7, docs/models/):** único entorno de datasets, experimentos,
entrenamiento, evaluación, exportación y empaquetado de modelos. NO contiene lógica de
ejecución del Agent Runtime (regla: ai-models entrena, diagnostic-agent infiere).

Estructura: src/ai_models/{data/ · anomaly/ · evaluation/ · export/ · tracking · registry} ·
experiments/ (reproducibles por semilla) · configs/ (experimentos declarativos YAML) ·
registry/ (catálogo JSON: modelos, experimentos, training runs) · notebooks/ (solo
exploración: notebook ≠ pipeline) · models/ (artefactos exportados, no versionados).
La estructura evoluciona gradualmente sin mover archivos funcionales de F3 (F7 §42).

Protocolo de evaluación: F1 por eventos sin point-adjustment, escenarios held-out
(ver docs/estado_del_arte/linea_b y docs/04 RI1).

## Registro de experimentos

Todo run se registra en `experiments/runs.jsonl` (suite, git sha, modelo, parámetros,
semilla, umbral, métricas por split y categoría, latencia, RSS). Resultados de baselines:
`experiments/e1_results.csv` y ADR-0011. Ciclo de promoción de modelos: ADR-0009 +
[data-architecture/07](../docs/data-architecture/07_provenance_versionado.md).

## Model Registry (F7, ADR-0022)

Catálogo en `registry/` (filesystem + JSON): entradas de modelo con ciclo de vida y
capacidades, experimentos y training runs como contratos de `mecanico_contracts`.
Acceso/validación: `ai_models.registry.ModelRegistry` (transiciones de estado guardadas,
checksums, integridad referencial). Reconstrucción determinista de los resultados F3:
`python experiments/register_f3.py`. Estrategia completa, cards e inventario:
[docs/models/](../docs/models/README.md).
