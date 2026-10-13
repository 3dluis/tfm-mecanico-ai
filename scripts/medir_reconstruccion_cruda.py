"""¿Reproduce el generador publicado las señales de un conjunto ya generado?

**Por qué existe.** El guion de reconstrucción comprueba las huellas de los
ficheros **procesados**, y el 13 de octubre de 2026 se vio que eso no basta: el
ventanado y el reparto de `synthetic_v3` reproducen bit a bit aunque sus señales
sean otras, porque dependen de identificadores e instantes y no de valores. Una
reconstrucción equivocada pasaba las pruebas midiendo otros datos.

Esta medición va al otro extremo de la cadena: regenera cada sesión con el plan
y la semilla declarados y la compara **muestra a muestra** con la que hay en
disco. No escribe nada y no toca ningún artefacto.

**Qué mide.** Cuántas sesiones salen idénticas, cuántas no y cuál es la mayor
diferencia encontrada en una señal numérica.

    uv run python scripts/medir_reconstruccion_cruda.py synthetic_v1 --por-fallo 6
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

import numpy as np
import pandas as pd

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.obd.synthetic import build_balanced_specs, generate_session

#: Sesiones por condición con que se generó cada conjunto. Equivocarlo produce
#: otro conjunto con el mismo nombre, que es justo el fallo que esto detecta.
POR_FALLO: dict[str, int] = {"synthetic_v1": 6, "synthetic_v2": 12, "synthetic_v3": 36}

#: Semilla del plan de sesiones. Es la misma en los tres conjuntos.
SEMILLA = 20260901

TOLERANCIA = 1e-9


@dataclass(frozen=True)
class Resultado:
    conjunto: str
    sesiones: int
    identicas: int
    diferencia_maxima: float
    peor_sesion: str

    @property
    def reconstruible(self) -> bool:
        return self.identicas == self.sesiones


def medir(conjunto: str, por_fallo: int) -> Resultado:
    ruta = paths.ROOT / "data" / "raw" / "synthetic" / f"{conjunto}.parquet"
    if not ruta.is_file():
        msg = f"no está en disco: {ruta.relative_to(paths.ROOT)}"
        raise FileNotFoundError(msg)

    viejo = pd.read_parquet(ruta)
    # Las columnas de expresión efectiva del fallo no existían cuando se
    # generaron estos conjuntos: se comparan solo las señales que ambos tienen.
    numericas = [
        c
        for c in viejo.columns
        if pd.api.types.is_numeric_dtype(viejo[c]) and not pd.api.types.is_bool_dtype(viejo[c])
    ]

    especificaciones = build_balanced_specs(seed=SEMILLA, sessions_per_fault=por_fallo)
    identicas = 0
    diferencia_maxima = 0.0
    peor = ""
    for especificacion in especificaciones:
        nueva = generate_session(especificacion, con_expresion=False)
        vieja = viejo[viejo.session_id == especificacion.session_id].reset_index(drop=True)
        columnas = [c for c in numericas if c in nueva.columns]
        a = nueva[columnas].to_numpy(float)
        b = vieja[columnas].to_numpy(float)
        if a.shape == b.shape and np.allclose(a, b, atol=TOLERANCIA, equal_nan=True):
            identicas += 1
            continue
        if a.shape == b.shape:
            diferencia = float(np.nanmax(np.abs(a - b)))
            if diferencia > diferencia_maxima:
                diferencia_maxima, peor = diferencia, especificacion.session_id

    return Resultado(
        conjunto=conjunto,
        sesiones=len(especificaciones),
        identicas=identicas,
        diferencia_maxima=diferencia_maxima,
        peor_sesion=peor,
    )


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("conjuntos", nargs="*", default=sorted(POR_FALLO))
    analizador.add_argument("--por-fallo", type=int, default=0)
    args = analizador.parse_args(argv)

    salida = 0
    for conjunto in args.conjuntos:
        por_fallo = args.por_fallo or POR_FALLO.get(conjunto, 12)
        try:
            resultado = medir(conjunto, por_fallo)
        except FileNotFoundError as error:
            print(f"{conjunto:14s} {error}")
            continue
        estado = "RECONSTRUIBLE" if resultado.reconstruible else "NO RECONSTRUIBLE"
        print(
            f"{conjunto:14s} {estado:18s} "
            f"idénticas {resultado.identicas} de {resultado.sesiones}"
            + (
                ""
                if resultado.reconstruible
                else f" · diferencia máxima {resultado.diferencia_maxima:.2f} "
                f"en {resultado.peor_sesion}"
            )
        )
        if not resultado.reconstruible:
            salida = 1
    return salida


if __name__ == "__main__":
    sys.exit(main())
