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
uv run mecanico-exp sufficiency --mode oracle
uv run mecanico-exp sufficiency --mode non-oracle
uv run mecanico-exp sufficiency --mode oracle --llm transformers-lora@slm_lora_v2

echo
echo "¿Coinciden las cifras reproducidas con las publicadas?"
uv run python scripts/comparar_registro.py \
  experiments/E12_retrieval.json "experiments/E12_retrieval_${ETIQUETA}.json"

echo
echo "Los registros de E15 y E13 llevan su propio sufijo de modo; compárelos con:"
echo "  git --no-pager diff --stat -- experiments/E15_suficiencia.json \\"
echo "    experiments/E15_suficiencia_non_oracle.json \\"
echo "    'experiments/E13_agente_transformers-lora@slm_lora_v2.json'"
