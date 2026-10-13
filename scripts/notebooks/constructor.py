"""Constructor de los notebooks del TFM.

**Por qué un constructor y no editar el `.ipynb` a mano.** Cada notebook tiene
dieciséis secciones obligatorias y una cantidad de prosa considerable. Escribir
eso dentro del JSON de un notebook —con su `source` troceado en listas de
cadenas, sus `outputs` y sus metadatos— es incómodo de revisar en un `diff` y
fácil de romper. Aquí el notebook se declara como una secuencia de celdas en
Python, y el `.ipynb` es su resultado.

Los `.ipynb` **se versionan igualmente**: son el entregable, y quien los abra en
Jupyter no necesita saber que existe este script. Si alguien edita un notebook a
mano, lo que manda es el `.ipynb`; este constructor sirve para la primera
escritura y para rehacerla cuando el cambio es estructural.

Los notebooks se escriben **sin salidas**: se ejecutan desde un kernel limpio, y
guardar salidas de la máquina del autor en el fichero las haría pasar por
resultado de la ejecución del lector.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[2]
DESTINO = RAIZ / "notebooks"

#: Preámbulo común. Resuelve la raíz sin rutas absolutas y sin suponer desde
#: dónde se abrió Jupyter, que es la única forma de que el notebook funcione en
#: la máquina del tribunal igual que en la del autor.
PREAMBULO = """\
# Anclaje de la raíz del repositorio. No hay rutas absolutas en ningún notebook:
# la raíz se deduce de dónde está este fichero, de modo que da igual desde qué
# directorio se haya abierto Jupyter.
import sys
from pathlib import Path

RAIZ = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

from mecanico_ia_exp.notebooks import soporte

soporte.imprimir_entorno()"""


def md(texto: str) -> dict[str, Any]:
    """Celda de texto."""
    return {
        "cell_type": "markdown",
        "id": "",
        "metadata": {},
        "source": texto.rstrip("\n").splitlines(True),
    }


def code(texto: str) -> dict[str, Any]:
    """Celda de código, **sin salidas**."""
    return {
        "cell_type": "code",
        "id": "",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": texto.rstrip("\n").splitlines(True),
    }


def escribir(nombre: str, celdas: list[dict[str, Any]]) -> Path:
    """Escribe el notebook con el kernel del proyecto declarado.

    Los identificadores de celda se asignan aquí, por posición: ``nbformat`` los
    exige desde la versión 4.5 y generarlos al azar haría que reconstruir el
    notebook produjera un `diff` completo sin haber cambiado nada.
    """
    for i, celda in enumerate(celdas):
        celda["id"] = f"c{i:03d}"
    notebook = {
        "cells": celdas,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (mecanico-ia-exp)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    destino = DESTINO / nombre
    destino.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", "utf-8")
    codigo = sum(1 for c in celdas if c["cell_type"] == "code")
    print(f"{nombre:34s} {len(celdas):3d} celdas ({codigo} de código)")
    return destino
