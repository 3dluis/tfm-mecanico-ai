#!/usr/bin/env bash
# Reconstruye los conjuntos que el repositorio no distribuye, y COMPRUEBA que
# salen idénticos a los que sostienen las cifras publicadas.
#
# Por qué hace falta. `data/raw/**` y `data/processed/**` están en `.gitignore`:
# `synthetic_v2` son 43 200 muestras y `synthetic_v3`, 129 600. Un clon no los
# trae, y sin ellos diez pruebas no pueden ejecutarse. No se distribuyen porque
# no hace falta: el generador es determinista y los reconstruye bit a bit.
#
# El esquema. `synthetic_v1`, `v2` y `v3` se generaron antes de que existieran
# las columnas de expresión efectiva del fallo. Reconstruirlos con el esquema
# vigente produce un `meta.parquet` distinto, y el manifiesto de E19 fija ese
# fichero POR HUELLA: la verificación de la congelación fallaría. Reproducir un
# conjunto congelado incluye reproducir su esquema, y por eso va
# `--esquema historico`.
#
# La comprobación. Al final se contrastan las cuatro huellas contra
# `configs/manifest_e19.json`. Si alguna difiere, el guion falla: un conjunto
# reconstruido que no coincide con el congelado no sirve para nada, y es mejor
# saberlo aquí que al ejecutar E19.
set -euo pipefail
cd "$(dirname "$0")/.."

CONJUNTO="${1:-synthetic_v2}"
SESIONES_POR_FALLO="${2:-12}"

echo "Reconstruyendo ${CONJUNTO} (${SESIONES_POR_FALLO} sesiones por condición)"
echo

if [ -f "data/raw/synthetic/${CONJUNTO}.parquet" ]; then
  echo "Ya está en disco: data/raw/synthetic/${CONJUNTO}.parquet"
  echo "No se regenera; los ejecutores se niegan a sobrescribir un conjunto existente."
else
  uv run mecanico-exp generate-synthetic \
    --dataset-id "${CONJUNTO}" \
    --sessions-per-fault "${SESIONES_POR_FALLO}" \
    --esquema historico
fi

echo
uv run mecanico-exp preprocess --dataset-id "${CONJUNTO}" --etiqueta reconstruccion

echo
uv run python scripts/verificar_reconstruccion.py "${CONJUNTO}"
