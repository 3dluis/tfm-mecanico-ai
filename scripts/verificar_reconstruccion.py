"""Comprueba que un conjunto reconstruido es el mismo que sostiene las cifras.

Un conjunto que se regenera y **no** coincide con el congelado no sirve para
nada: las pruebas pasarían midiendo otros datos, y la evaluación final habría
medido sobre unos ficheros creyéndolos otros. Eso es peor que no poder
reconstruirlo, porque no se nota.

Las huellas de referencia salen de `configs/manifest_e19.json`, que las fijó
**antes** de abrir el conjunto de prueba. Este guion no las escribe ni las
actualiza: solo compara.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MANIFIESTO = RAIZ / "configs" / "manifest_e19.json"


def huella_16(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()[:16]


def verificar(dataset_id: str) -> int:
    """Devuelve 0 si las cuatro huellas coinciden con las congeladas."""
    declarado = json.loads(MANIFIESTO.read_text("utf-8"))["controlled_state"]["dataset"]
    if declarado["dataset_id"] != dataset_id:
        print(
            f"El manifiesto de E19 congela «{declarado['dataset_id']}», no «{dataset_id}».\n"
            "Para los demás conjuntos no hay huellas de referencia y esta comprobación no "
            "aplica: su reconstrucción se verifica con la auditoría del generador."
        )
        return 0

    esperadas: dict[str, str] = declarado["files"]
    print(f"Huellas de {dataset_id}, contra las congeladas en configs/manifest_e19.json:\n")

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

    print(
        f"Los {len(esperadas)} ficheros coinciden bit a bit con el estado congelado de E19. "
        "El conjunto reconstruido es el mismo que sostiene las cifras publicadas."
    )
    return 0


def main(argv: list[str]) -> int:
    return verificar(argv[0] if argv else "synthetic_v2")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
