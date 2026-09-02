"""Resumen comparable de las ejecuciones del agente.

Vive aquí y no en el cuaderno porque la comparación antes/después es un
resultado del experimento, y un resultado tiene que poder calcularse y testearse
fuera de una celda.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

COLUMNAS = ("proveedor", "válidas", "respetan veredicto", "citas inventadas", "esquema roto", "n")


def summarize_runs(runs: list[dict[str, Any]], *, proveedor: str) -> dict[str, Any]:
    """Cuenta lo que se mide en E13 a partir de los registros serializados."""
    n = len(runs)
    return {
        "proveedor": proveedor,
        "válidas": sum(1 for r in runs if r["valid"]),
        "respetan veredicto": sum(1 for r in runs if r["respected_verdict"]),
        "citas inventadas": sum(len(r["fake_citations"]) for r in runs),
        "esquema roto": sum(1 for r in runs if r["schema_error"]),
        "n": n,
    }


def compare_records(rutas: dict[str, Path]) -> pd.DataFrame:
    """Tabla antes/después a partir de los ficheros ``E13_agente_*.json``.

    ``rutas`` asocia una etiqueta legible a cada registro. Los que no existen se
    omiten en lugar de fallar: el cuaderno debe poder abrirse en una máquina
    donde no se haya ejecutado alguna de las pasadas.
    """
    filas = []
    for etiqueta, ruta in rutas.items():
        if not ruta.is_file():
            continue
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        filas.append(summarize_runs(datos["runs"], proveedor=etiqueta))
    return pd.DataFrame(filas, columns=list(COLUMNAS))


def per_case(rutas: dict[str, Path]) -> pd.DataFrame:
    """Caso a caso: qué redactó cada proveedor y si el esquema lo aceptó."""
    filas = []
    for etiqueta, ruta in rutas.items():
        if not ruta.is_file():
            continue
        for r in json.loads(ruta.read_text(encoding="utf-8"))["runs"]:
            filas.append(
                {
                    "proveedor": etiqueta,
                    "caso": r["case_id"],
                    "veredicto": r["verdict"],
                    "redactó": (r["output"] or {}).get("decision", "—"),
                    "esquema": "ok" if not r["schema_error"] else "FALLA",
                    "seg": r["latency_s"],
                }
            )
    return pd.DataFrame(filas)
