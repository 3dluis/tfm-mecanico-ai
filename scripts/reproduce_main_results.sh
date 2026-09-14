#!/usr/bin/env bash
# Reproduce el bloque documental (E12, E15 oracular y no oracular, E13 con LoRA v2).
# Requiere PostgreSQL con pgvector, el índice cargado (scripts/ingest_mazda.py multilingual),
# el modelo base de Hugging Face y el adaptador models/slm_lora_v2 (ver data/README.md).
# Es el mismo orden que RERUN-A (docs/methodology/plan-reejecucion-canonica.md): B, D, F, I.
set -euo pipefail
cd "$(dirname "$0")/.."

uv run mecanico-exp doctor
uv run mecanico-exp eval-retrieval
uv run mecanico-exp sufficiency --mode oracle
uv run mecanico-exp sufficiency --mode non-oracle
uv run mecanico-exp sufficiency --mode oracle --llm transformers-lora@slm_lora_v2

echo
echo "Diferencias con los registros versionados (vacío = idénticos):"
git --no-pager diff --stat -- experiments/E12_retrieval.json experiments/E15_suficiencia.json \
  experiments/E15_suficiencia_non_oracle.json "experiments/E13_agente_transformers-lora@slm_lora_v2.json" || true
echo "Los campos commit y executed_at cambian siempre; compare las métricas y las decisiones."
