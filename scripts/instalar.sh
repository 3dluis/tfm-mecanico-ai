#!/usr/bin/env bash
# Prepara el entorno para ejecutar los notebooks de este paquete.
#
# Qué hace: comprueba el intérprete, comprueba `uv`, instala las dependencias
# declaradas y verifica que lo esencial se importa y que los recursos están.
#
# Qué NO hace: no descarga modelos, no contacta con ningún servicio y no
# modifica nada fuera de este directorio.
#
# **Necesita internet UNA vez**, para descargar las dependencias de Python. A
# partir de ahí, la modalidad DEMO se ejecuta sin red.
set -euo pipefail

cd "$(dirname "$0")/.."
raiz="$(pwd)"
echo "paquete: ${raiz}"
echo

fallo() { echo "  ERROR  $1" >&2; exit 1; }

echo "1 · intérprete de Python"
if ! command -v python3 >/dev/null 2>&1; then
    fallo "no hay python3 en el PATH. Hace falta Python 3.11 o superior."
fi
version="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
echo "     python3 ${version}"
python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' \
    || fallo "hace falta Python 3.11 o superior; hay ${version}"

echo "2 · gestor de entorno uv"
if ! command -v uv >/dev/null 2>&1; then
    echo "     uv no está instalado."
    echo "     Instálalo con:  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "     o con:          pipx install uv"
    fallo "uv es necesario: el entorno se fija con uv.lock y no con versiones sueltas"
fi
echo "     $(uv --version)"

echo "3 · dependencias (necesita internet la primera vez)"
echo "     extras: ml (modelos y SHAP), nb (Jupyter y gráficas), docx"
uv sync --extra ml --extra nb --extra docx 2>&1 | tail -3 \
    || fallo "la instalación falló. Revisa la conexión y vuelve a ejecutar."

echo "4 · comprobación de imports"
uv run python - <<'PY'
import importlib, sys

ESENCIALES = ["numpy", "pandas", "matplotlib", "seaborn", "sklearn", "mecanico_ia_exp"]
OPCIONALES = ["shap", "torch", "plotly"]

faltan = [m for m in ESENCIALES if importlib.util.find_spec(m) is None]
if faltan:
    print(f"     FALTAN módulos esenciales: {', '.join(faltan)}", file=sys.stderr)
    raise SystemExit(1)
print(f"     esenciales: {', '.join(ESENCIALES)}")
sin = [m for m in OPCIONALES if importlib.util.find_spec(m) is None]
if sin:
    print(f"     opcionales ausentes (solo afectan a la modalidad FULL): {', '.join(sin)}")
PY

echo "5 · recursos del paquete"
uv run python scripts/verificar_entrega.py --rapido || fallo "faltan recursos del paquete"

echo
echo "Listo. Para leer sin ejecutar nada:   notebooks/html/*.html"
echo "Para ejecutar los notebooks DEMO:     bash scripts/ejecutar_notebooks.sh"
