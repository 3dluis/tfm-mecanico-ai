#!/usr/bin/env bash
# Reproduce el bloque de telemetría del TFM (E2 → E5 → E6 → E15b) sobre synthetic_v2 y compara
# con los registros versionados. No necesita PostgreSQL ni el manual de taller.
#
# Toda ejecución va con ETIQUETA: la reproducción escribe sus propios artefactos y **no toca**
# los publicados. Antes se comparaba con `git diff`, lo que exigía sobrescribir el registro para
# comprobar que se reproducía; es decir, destruir el resultado para verificarlo.
#
# synthetic_v2 no se regenera: ya está en disco y los ejecutores se niegan a sobrescribirlo,
# porque sostiene las cifras de E6, E7, E9, E15 y E19. Para generarlo desde cero en una copia
# que no lo tenga, descomente la línea indicada.
set -euo pipefail
cd "$(dirname "$0")/.."

ETIQUETA="${1:-reproduccion}"
echo "Etiqueta de esta reproducción: ${ETIQUETA}"

uv run mecanico-exp doctor --no-db

# Solo si data/raw/synthetic/synthetic_v2.parquet NO existe en esta copia:
# uv run mecanico-exp generate-synthetic --dataset-id synthetic_v2 --sessions-per-fault 12

uv run mecanico-exp preprocess --dataset-id synthetic_v2 --etiqueta "${ETIQUETA}"
uv run mecanico-exp train-baseline --dataset-id synthetic_v2 --etiqueta "${ETIQUETA}"
uv run mecanico-exp threshold-sweep --dataset-id synthetic_v2 --etiqueta "${ETIQUETA}"

echo
echo "¿Coinciden las cifras reproducidas con las publicadas?"
uv run python scripts/comparar_registro.py \
  experiments/E6_baseline_synthetic_v2.json \
  "experiments/E6_${ETIQUETA}_baseline_synthetic_v2.json"
uv run python scripts/comparar_registro.py \
  experiments/E15b_barrido_umbral.json \
  "experiments/E15b_barrido_umbral_${ETIQUETA}.json"
