"""Comprueba que un conjunto reconstruido es el mismo que sostiene las cifras.

Un conjunto que se regenera y **no** coincide con el congelado no sirve para
nada: las pruebas pasarían midiendo otros datos, y la evaluación final habría
medido sobre unos ficheros creyéndolos otros. Eso es peor que no poder
reconstruirlo, porque no se nota.

Hay **dos** fuentes de huellas y no valen lo mismo, de modo que el guion dice
cuál usa:

* `configs/manifest_e19.json` — las de `synthetic_v2`, fijadas **antes** de abrir
  el conjunto de prueba. Garantía fuerte: coincidir significa que el conjunto es
  el que sostiene las cifras publicadas.
* `configs/huellas_datos_reconstruibles.json` — las de los demás conjuntos,
  tomadas **después** de medir, de los ficheros de la máquina del autor. Garantía
  débil: coincidir significa que la reconstrucción es igual a la del autor; no
  demuestra cuál produjo las cifras. Difereir, en cambio, sí informa.

Este guion no escribe ni actualiza ninguna de las dos: solo compara.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MANIFIESTO = RAIZ / "configs" / "manifest_e19.json"
RECONSTRUIBLES = RAIZ / "configs" / "huellas_datos_reconstruibles.json"


def huella_16(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()[:16]


def verificar(dataset_id: str) -> int:
    """Devuelve 0 si las cuatro huellas coinciden con las congeladas."""
    declarado = json.loads(MANIFIESTO.read_text("utf-8"))["controlled_state"]["dataset"]
    if declarado["dataset_id"] == dataset_id:
        esperadas: dict[str, str] = declarado["files"]
        fuente = "configs/manifest_e19.json, congeladas ANTES de abrir el conjunto de prueba"
        garantia_fuerte = True
    else:
        if not RECONSTRUIBLES.is_file():
            print(f"No hay huellas de referencia para «{dataset_id}»; nada que comparar.")
            return 0
        registro = json.loads(RECONSTRUIBLES.read_text("utf-8"))["conjuntos"]
        if dataset_id not in registro:
            print(
                f"No hay huellas de referencia para «{dataset_id}».\n"
                "Su reconstrucción se verifica con la auditoría del generador, no por huella."
            )
            return 0
        esperadas = registro[dataset_id]["ficheros"]
        fuente = (
            "configs/huellas_datos_reconstruibles.json, tomadas DESPUÉS de medir: "
            "comparan con la reconstrucción del autor, no demuestran cuál produjo las cifras"
        )
        garantia_fuerte = False

    print(f"Huellas de {dataset_id}, contra {fuente}:\n")

    problemas = 0
    for relativa, esperada in esperadas.items():
        fichero = RAIZ / relativa
        if not fichero.is_file():
            print(f"  FALTA    {relativa}")
            problemas += 1
            continue
        actual = huella_16(fichero)
        if actual == esperada:
            print(f"  OK       {relativa}  {actual}")
        else:
            print(f"  DIFIERE  {relativa}  esperada {esperada} · obtenida {actual}")
            problemas += 1

    print()
    if problemas:
        print(
            f"{problemas} de {len(esperadas)} ficheros no coinciden con el estado congelado.\n"
            "Causa más probable: el conjunto se generó con el esquema vigente en lugar del "
            "histórico. Los tres conjuntos anteriores al manifiesto de procedencia no llevan "
            "las columnas de expresión, y añadirlas cambia el meta.parquet.\n"
            "Regenérelo con «--esquema historico»; borre antes lo reconstruido."
        )
        return 1

    if garantia_fuerte:
        print(
            f"Los {len(esperadas)} ficheros coinciden bit a bit con el estado congelado de E19. "
            "El conjunto reconstruido es el mismo que sostiene las cifras publicadas."
        )
    else:
        print(
            f"Los {len(esperadas)} ficheros coinciden bit a bit con la reconstrucción del autor. "
            "No es una congelación previa: lo que esto dice es que el generador es determinista "
            "y que esta máquina produce lo mismo que aquella."
        )
    return 0


def main(argv: list[str]) -> int:
    return verificar(argv[0] if argv else "synthetic_v2")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
