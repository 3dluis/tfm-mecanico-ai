#!/usr/bin/env bash
# Reproduce el bloque documental (E12, E15 oracular y no oracular, E13 con LoRA v2).
# Requiere PostgreSQL con pgvector, el índice cargado (scripts/ingest_mazda.py multilingual),
# el modelo base de Hugging Face y el adaptador models/slm_lora_v2 (ver data/README.md).
# Es el mismo orden que RERUN-A (docs/methodology/plan-reejecucion-canonica.md): B, D, F, I.
#
# Toda ejecución va con ETIQUETA y los registros publicados no se tocan.
set -euo pipefail
cd "$(dirname "$0")/.."

ETIQUETA="${1:-reproduccion}"
echo "Etiqueta de esta reproducción: ${ETIQUETA}"

uv run mecanico-exp doctor
uv run mecanico-exp eval-retrieval --etiqueta "${ETIQUETA}"
uv run mecanico-exp sufficiency --mode oracle --etiqueta "${ETIQUETA}"
uv run mecanico-exp sufficiency --mode non-oracle --etiqueta "${ETIQUETA}"
uv run mecanico-exp sufficiency --mode oracle --llm transformers-lora@slm_lora_v2 \
  --etiqueta "${ETIQUETA}"

echo
echo "¿Coinciden las cifras reproducidas con las publicadas?"
uv run python scripts/comparar_registro.py \
  experiments/E12_retrieval.json "experiments/E12_retrieval_${ETIQUETA}.json"

uv run python scripts/comparar_registro.py \
  experiments/E15_suficiencia.json "experiments/E15_suficiencia_${ETIQUETA}.json"
uv run python scripts/comparar_registro.py \
  experiments/E15_suficiencia_non_oracle.json \
  "experiments/E15_suficiencia_non_oracle_${ETIQUETA}.json"
uv run python scripts/comparar_registro.py \
  "experiments/E13_agente_transformers-lora@slm_lora_v2.json" \
  "experiments/E13_agente_transformers-lora@slm_lora_v2_${ETIQUETA}.json"
