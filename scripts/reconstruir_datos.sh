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

# `synthetic_v3` NO se reconstruye, y el guion se niega en lugar de producir un
# conjunto distinto con el mismo nombre. Es PRE-CALIBRACIÓN: se generó el 1 de
# septiembre a las 14:58 locales y la calibración del generador contra el manual
# es de las 15:46 del mismo día. Medido el 13-10-2026 al validar un clon limpio:
# cero de 216 sesiones idénticas, diferencia máxima en rpm de 1 983. El ventanado
# y el reparto sí reproducen —dependen de identificadores e instantes, no de
# valores—, lo que hace el fallo peor: `meta.parquet` coincide y las pruebas
# parecerían pasar midiendo otras señales.
# Está en `configs/datos_no_reconstruibles.json`, y el riesgo 16 de
# `docs/diseno-pi1/11-riesgos-metodologicos.md` ya decía que v3 no se regenera.
# Ampliado el 13-10-2026: `synthetic_v1` está en el mismo caso y no se había
# comprobado. Medido muestra a muestra con
# `scripts/medir_reconstruccion_cruda.py`: cero de 36 sesiones idénticas,
# diferencia máxima de 1 973 rpm. De él salen las figuras y las tablas de E4,
# el análisis exploratorio que el capítulo 5 cita. El control de esa misma
# medición sobre `synthetic_v2` da 72 de 72 idénticas.
case "${CONJUNTO}" in
  synthetic_v1|synthetic_v3)
    echo "${CONJUNTO} NO se reconstruye: es pre-calibración." >&2
    echo "El generador publicado produce otras señales; ver configs/datos_no_reconstruibles.json" >&2
    echo "Compruébelo con: uv run python scripts/medir_reconstruccion_cruda.py ${CONJUNTO}" >&2
    echo "Las pruebas que lo necesitan están declaradas como de recursos no distribuidos." >&2
    exit 2
    ;;
esac

# Cada conjunto tiene su número de sesiones por condición, y equivocarlo produce
# otro conjunto con el mismo nombre. Se deduce del nombre salvo que se indique.
case "${CONJUNTO}" in
  synthetic_v2) POR_DEFECTO=12 ;;
  *)            POR_DEFECTO=12 ;;
esac
SESIONES_POR_FALLO="${2:-${POR_DEFECTO}}"

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
