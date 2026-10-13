"""Las tres categorías de prueba, y qué hace falta para cada una.

**El problema que resuelve.** Un clon recién hecho deja doce pruebas detenidas.
Documentarlo no basta: una prueba detenida no es una prueba satisfactoria, y
quien reciba el repositorio tiene derecho a saber, sin leer prosa, cuáles puede
ejecutar ahora mismo, cuáles necesitan una preparación reproducible y cuáles
dependen de algo que no se distribuye.

Las tres categorías, por marcador:

* **inmediatas** — sin marcador. Se ejecutan con un clon y `uv sync`. Si una
  falla, el repositorio está roto.
* **con preparación** — `conjunto`, `notebook`. Necesitan un paso previo que
  **está automatizado y es verificable**: `scripts/reconstruir_datos.sh`
  reconstruye el conjunto y contrasta sus cuatro huellas contra las congeladas.
* **con recursos externos** — `db`, `llm`, `slow`. Dependen del corpus
  documental, de una base PostgreSQL o de los pesos del adaptador. No se
  distribuyen, y así está declarado.

El guion **comprueba**, no describe: mira si la preparación está hecha, ejecuta
lo que corresponde y devuelve un código distinto de cero si algo de la primera
categoría falla.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

#: Marcador → (categoría, qué hace falta, cómo se consigue)
CATEGORIAS: dict[str, tuple[str, str, str]] = {
    "": (
        "inmediatas",
        "nada: un clon y `uv sync --extra nb --extra ml`",
        "—",
    ),
    "conjunto": (
        "con preparación",
        "synthetic_v2 preprocesado, que no se distribuye por tamaño",
        "bash scripts/reconstruir_datos.sh",
    ),
    "notebook": (
        "con preparación",
        "un kernel de Jupyter; los notebooks se ejecutan enteros",
        "uv sync --extra nb",
    ),
    "db": (
        "con recursos externos",
        "PostgreSQL con pgvector y el índice cargado",
        "bash scripts/init_db.sh && uv run python scripts/ingest_mazda.py multilingual",
    ),
    "llm": (
        "con recursos externos",
        "un proveedor de lenguaje; para el local, los pesos del adaptador",
        "no se distribuyen: ver data/README.md",
    ),
    "slow": (
        "con recursos externos",
        "tiempo: entrenamientos y corpus completo",
        "—",
    ),
}

#: Los ficheros cuya ausencia detiene las pruebas de la categoría `conjunto`.
DEL_CONJUNTO = (
    "data/processed/synthetic_v2_x.npy",
    "data/processed/synthetic_v2_features.npy",
    "data/processed/synthetic_v2_meta.parquet",
    "data/processed/synthetic_v2_preprocess.json",
)


def _contar(expresion: str) -> int:
    """Cuántas pruebas selecciona una expresión de marcadores."""
    salida = subprocess.run(
        ["uv", "run", "pytest", "--collect-only", "-q", "-m", expresion],
        capture_output=True,
        text=True,
        cwd=RAIZ,
        check=False,
    ).stdout
    # `-q --collect-only` imprime «fichero.py: N» por fichero. Se suman.
    total = 0
    for linea in salida.splitlines():
        if ".py:" in linea:
            cola = linea.rsplit(":", 1)[-1].strip()
            if cola.isdigit():
                total += int(cola)
    return total


def _preparacion_hecha() -> bool:
    return all((RAIZ / r).is_file() for r in DEL_CONJUNTO)


def informar(ejecutar: bool) -> int:
    marcadores = [m for m in CATEGORIAS if m]
    sin_marcador = " and ".join(f"not {m}" for m in marcadores)

    inmediatas = _contar(sin_marcador)
    con_preparacion = _contar("conjunto or notebook")
    externas = _contar("db or llm or slow")

    print("CATEGORÍAS DE PRUEBA\n")
    print(f"  inmediatas             {inmediatas:>4}   un clon y `uv sync`")
    print(
        f"  con preparación        {con_preparacion:>4}   "
        "reconstrucción automática y verificable"
    )
    print(f"  con recursos externos  {externas:>4}   corpus, base de datos o pesos no distribuidos")
    print(f"  {'─' * 44}")
    print(f"  total                  {inmediatas + con_preparacion + externas:>4}\n")

    listo = _preparacion_hecha()
    print(f"preparación del conjunto: {'HECHA' if listo else 'PENDIENTE'}")
    if not listo:
        faltan = [r for r in DEL_CONJUNTO if not (RAIZ / r).is_file()]
        print(f"  faltan {len(faltan)} de {len(DEL_CONJUNTO)} ficheros")
        print("  bash scripts/reconstruir_datos.sh")
        print("  genera, preprocesa y COMPRUEBA las cuatro huellas contra las congeladas")

    if not ejecutar:
        return 0

    print("\nEJECUCIÓN\n")
    codigo = subprocess.run(
        ["uv", "run", "pytest", "-m", sin_marcador, "-q"], cwd=RAIZ, check=False
    ).returncode
    if codigo:
        print("\nFALLO en las pruebas inmediatas: el repositorio está roto.")
        return 1
    print("\nlas pruebas inmediatas pasan.")

    if listo:
        codigo = subprocess.run(
            ["uv", "run", "pytest", "-m", "conjunto or notebook", "-q"], cwd=RAIZ, check=False
        ).returncode
        if codigo:
            print("\nFALLO en las pruebas con preparación, y la preparación estaba hecha.")
            return 1
        print("las pruebas con preparación pasan.")
    else:
        print(
            "las pruebas con preparación NO se han ejecutado porque falta la reconstrucción.\n"
            "No se declara que pasen: no se han ejecutado."
        )
        return 2

    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--ejecutar",
        action="store_true",
        help="además de informar, ejecuta cada categoría y falla si la primera no pasa",
    )
    parser.add_argument("--json", action="store_true", help="emitir el recuento en JSON")
    args = parser.parse_args(argv)

    if args.json:
        marcadores = [m for m in CATEGORIAS if m]
        print(
            json.dumps(
                {
                    "inmediatas": _contar(" and ".join(f"not {m}" for m in marcadores)),
                    "con_preparacion": _contar("conjunto or notebook"),
                    "con_recursos_externos": _contar("db or llm or slow"),
                    "preparacion_hecha": _preparacion_hecha(),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0
    return informar(args.ejecutar)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
