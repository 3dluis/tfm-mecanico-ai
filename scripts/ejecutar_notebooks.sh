#!/usr/bin/env bash
# Ejecuta los siete notebooks de la entrega desde un kernel limpio.
#
# Cada uno se ejecuta **aislado**: no hay estado compartido entre ellos y el
# orden no importa, porque ninguno depende de que otro se haya ejecutado antes.
# Si uno falla, se dice cuál y se sigue con los demás, y el guion termina con
# código distinto de cero.
#
# Las salidas van a `notebooks/salida/ejecutados/`. Los `.ipynb` del paquete
# **no se modifican**: viajan sin salidas a propósito, para que las que se vean
# sean las de quien ejecuta y no las del autor.
set -uo pipefail

cd "$(dirname "$0")/.."
destino="notebooks/salida/ejecutados"
mkdir -p "${destino}"

NOTEBOOKS=(
    00_introduccion
    01_exploracion_obd
    02_comparacion_modelos
    03_analisis_e19
    04_explicabilidad
    05_suficiencia_y_abstencion
    06_expresion_del_fallo
)

fallidos=()
for nombre in "${NOTEBOOKS[@]}"; do
    origen="notebooks/${nombre}.ipynb"
    if [[ ! -f "${origen}" ]]; then
        echo "  FALTA     ${origen}" >&2
        fallidos+=("${nombre}")
        continue
    fi
    printf '  %-32s ' "${nombre}"
    inicio=$(date +%s)
    if uv run jupyter nbconvert --to notebook --execute \
            --ExecutePreprocessor.timeout=900 \
            --output-dir "${destino}" --output "${nombre}.ipynb" \
            "${origen}" >"${destino}/${nombre}.log" 2>&1; then
        echo "ok  ($(( $(date +%s) - inicio )) s)"
    else
        echo "FALLÓ"
        echo "      última línea del registro:" >&2
        tail -3 "${destino}/${nombre}.log" | sed 's/^/      /' >&2
        fallidos+=("${nombre}")
    fi
done

echo
if (( ${#fallidos[@]} )); then
    echo "${#fallidos[@]} de ${#NOTEBOOKS[@]} notebooks fallaron: ${fallidos[*]}" >&2
    echo "Los registros completos están en ${destino}/" >&2
    exit 1
fi
echo "Los ${#NOTEBOOKS[@]} notebooks se ejecutaron sin error."
echo "Resultados en ${destino}/"
