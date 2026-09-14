#!/usr/bin/env bash
# Reproduce el bloque de telemetría del TFM (E2 → E5 → E6 → E15b) sobre synthetic_v2 y compara
# el registro de E6 con el versionado. No necesita PostgreSQL ni el manual de taller.
# Envoltorio literal de los comandos de docs/EXPERIMENTO_PASO_A_PASO.md; no añade lógica.
set -euo pipefail
cd "$(dirname "$0")/.."

uv run mecanico-exp doctor --no-db
uv run mecanico-exp generate-synthetic --dataset-id synthetic_v2 --sessions-per-fault 12
uv run mecanico-exp preprocess --dataset-id synthetic_v2
uv run mecanico-exp train-baseline --dataset-id synthetic_v2
uv run mecanico-exp threshold-sweep --dataset-id synthetic_v2

echo
echo "Diferencias entre el registro reproducido y el versionado (vacío = idénticos):"
git --no-pager diff --stat -- experiments/E6_baseline_synthetic_v2.json experiments/E15b_barrido_umbral.json || true
echo "Detalle: git diff -- experiments/E6_baseline_synthetic_v2.json"
