"""Genera la trayectoria contrafactual de sesiones existentes de `synthetic_v2`.

**Qué es un contrafactual aquí.** No es una sesión nueva ni una simulación
aparte. El motor de señales avanza su estado **al margen del fallo**: `tick()`
devuelve el valor que la sesión habría tenido en ese instante sin avería, y la
función de fallo recibe una copia de ese valor. La trayectoria sana de una
sesión averiada es, por tanto, el valor que el generador ya calcula en cada
muestra. Reproducirla exige la misma semilla, el mismo régimen, la misma
temperatura ambiente, la misma duración y la misma cadencia: nada más.

**Qué hace este guion.** Para cada sesión seleccionada:

1. **la verifica antes de nada**: la regenera con el esquema histórico y la
   compara muestra a muestra con `synthetic_v2.parquet`. Si no sale idéntica,
   se detiene y no escribe nada;
2. genera la trayectoria con fallo y su contrafactual con el fallo desactivado;
3. comprueba que **antes del instante de entrada** las dos son idénticas, que es
   la propiedad que hace comparable la pareja;
4. escribe el resultado en `artifacts/contrafactual/`, con su configuración, su
   procedencia y su huella.

**Qué no hace.** No desarrolla un generador nuevo, no modifica el generador
histórico, no toca el conjunto congelado y no escribe en `data/`. El resultado
es un **artefacto derivado para análisis visual**: no entra en entrenamiento,
validación ni prueba, no modifica ninguna métrica y no es una evaluación nueva.

    uv run python scripts/contrafactual_t2.py
    uv run python scripts/contrafactual_t2.py --solo F05_misfire
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.obd.faults import FAULTS, NORMAL_ID
from mecanico_ia_exp.obd.signals import SIGNAL_NAMES
from mecanico_ia_exp.obd.synthetic import SessionSpec, build_balanced_specs, generate_session

#: Plan de sesiones de `synthetic_v2`. Equivocar cualquiera de los dos produce
#: otro conjunto con el mismo nombre.
SEMILLA_DEL_PLAN = 20260901
SESIONES_POR_FALLO = 12

#: Dónde vive el conjunto congelado contra el que se verifica.
CRUDO = paths.ROOT / "data" / "raw" / "synthetic" / "synthetic_v2.parquet"

#: Directorio propio. No se escribe en `data/` ni en `artifacts/tables/`.
SALIDA = paths.ROOT / "artifacts" / "contrafactual"

#: Ficheros que definen el generador. Su huella queda en la procedencia para que
#: un cambio futuro en el mecanismo sea detectable desde el artefacto.
FUENTES_DEL_GENERADOR: tuple[str, ...] = (
    "src/mecanico_ia_exp/obd/synthetic.py",
    "src/mecanico_ia_exp/obd/signals.py",
    "src/mecanico_ia_exp/obd/faults.py",
    "src/mecanico_ia_exp/obd/expresion.py",
)

TOLERANCIA = 1e-9


class ReconstruccionFallidaError(RuntimeError):
    """La sesión original no se reproduce, de modo que no hay pareja comparable."""


@dataclass(frozen=True)
class Pareja:
    """Una sesión averiada y su contrafactual, ya verificados."""

    spec: SessionSpec
    con_fallo: pd.DataFrame
    sin_fallo: pd.DataFrame
    particion: str

    @property
    def señales_alteradas(self) -> tuple[str, ...]:
        """Señales cuya diferencia supera la tolerancia numérica en algún instante."""
        a = self.con_fallo[list(SIGNAL_NAMES)].to_numpy(float)
        b = self.sin_fallo[list(SIGNAL_NAMES)].to_numpy(float)
        maximos = np.nanmax(np.abs(a - b), axis=0)
        return tuple(s for s, m in zip(SIGNAL_NAMES, maximos, strict=True) if m > TOLERANCIA)


def _huella_de_bytes(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def _huella_de_fichero(ruta: Path) -> str:
    return _huella_de_bytes(ruta.read_bytes())


def _commit() -> str:
    try:
        salida = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=paths.ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "desconocido"
    return salida.stdout.strip()


def _particiones() -> dict[str, str]:
    meta = pd.read_parquet(paths.DATA_PROCESSED / "synthetic_v2_meta.parquet")
    emparejado = meta[["session_id", "partition"]].drop_duplicates()
    return {str(f.session_id): str(f.partition) for f in emparejado.itertuples()}


def verificar_original(spec: SessionSpec, crudo: pd.DataFrame) -> pd.DataFrame:
    """Regenera la sesión y la compara muestra a muestra con la congelada.

    Devuelve la sesión regenerada **con** las columnas de expresión, que el
    conjunto congelado no tiene porque no existían cuando se generó. La
    comparación se hace solo sobre las columnas numéricas que ambos comparten,
    que son las señales: es lo que el modelo consume y lo que la figura dibuja.
    """
    vieja = crudo[crudo.session_id == spec.session_id].reset_index(drop=True)
    if vieja.empty:
        msg = f"{spec.session_id} no está en el conjunto congelado"
        raise ReconstruccionFallidaError(msg)

    historica = generate_session(spec, con_expresion=False)
    columnas = [
        c
        for c in vieja.columns
        if c in historica.columns
        and pd.api.types.is_numeric_dtype(vieja[c])
        and not pd.api.types.is_bool_dtype(vieja[c])
    ]
    a = historica[columnas].to_numpy(float)
    b = vieja[columnas].to_numpy(float)
    if a.shape != b.shape:
        msg = f"{spec.session_id}: la forma no coincide, {a.shape} frente a {b.shape}"
        raise ReconstruccionFallidaError(msg)
    if not np.allclose(a, b, atol=TOLERANCIA, equal_nan=True):
        peor = float(np.nanmax(np.abs(a - b)))
        msg = f"{spec.session_id}: no se reproduce, diferencia máxima {peor:.6g}"
        raise ReconstruccionFallidaError(msg)

    return generate_session(spec)


def construir_pareja(spec: SessionSpec, crudo: pd.DataFrame, particion: str) -> Pareja:
    """Verifica la original y calcula su contrafactual, con la comprobación de la transición."""
    con_fallo = verificar_original(spec, crudo)
    sin_fallo = generate_session(replace(spec, fault_id=NORMAL_ID, fault_onset_s=0.0))

    # La propiedad que hace comparable la pareja: antes de que el fallo entre,
    # las dos trayectorias tienen que ser **la misma**. Si no lo son, el motor
    # no es independiente del fallo y la comparación no aísla nada.
    antes = con_fallo.timestamp < spec.fault_onset_s
    if bool(antes.any()):
        a = con_fallo.loc[antes, list(SIGNAL_NAMES)].to_numpy(float)
        b = sin_fallo.loc[antes, list(SIGNAL_NAMES)].to_numpy(float)
        if not np.allclose(a, b, atol=TOLERANCIA, equal_nan=True):
            peor = float(np.nanmax(np.abs(a - b)))
            msg = (
                f"{spec.session_id}: las dos trayectorias difieren ANTES del instante de "
                f"entrada ({peor:.6g}); el contrafactual no sería comparable"
            )
            raise ReconstruccionFallidaError(msg)

    return Pareja(spec=spec, con_fallo=con_fallo, sin_fallo=sin_fallo, particion=particion)


def seleccionar(specs: list[SessionSpec], particiones: dict[str, str]) -> list[SessionSpec]:
    """Una sesión por condición de fallo, con regla declarada y sin elegir a ojo.

    **La regla.** De cada condición se toma, en orden alfabético de identificador,
    la primera sesión **de entrenamiento** en la que el fallo llega a expresarse
    según el criterio de `obd/expresion.py`. Se restringe a entrenamiento para no
    abrir la partición reservada ni la de validación por una figura. Si en
    ninguna se expresa, se toma la primera de entrenamiento y la figura lo
    declara: es el caso del límite físico del termostato, que es un resultado y
    no un defecto de la selección.
    """
    elegidas: list[SessionSpec] = []
    for fault_id in FAULTS:
        candidatas = sorted(
            (
                s
                for s in specs
                if s.fault_id == fault_id and particiones.get(s.session_id) == "train"
            ),
            key=lambda s: s.session_id,
        )
        if not candidatas:
            continue
        con_expresion = [s for s in candidatas if bool(generate_session(s).fault_expressed.any())]
        elegidas.append(con_expresion[0] if con_expresion else candidatas[0])
    return elegidas


def escribir(parejas: list[Pareja]) -> tuple[Path, Path]:
    """Un parquet con las dos trayectorias de cada sesión y su ficha de procedencia."""
    SALIDA.mkdir(parents=True, exist_ok=True)
    marcos: list[pd.DataFrame] = []
    for pareja in parejas:
        for traza, marco in (("con_fallo", pareja.con_fallo), ("contrafactual", pareja.sin_fallo)):
            copia = marco.copy()
            copia.insert(0, "traza", traza)
            marcos.append(copia)
    tabla = pd.concat(marcos, ignore_index=True)

    destino = SALIDA / "T2_contrafactual_synthetic_v2.parquet"
    tabla.to_parquet(destino, index=False)

    ficha = {
        "que_es": (
            "Trayectorias con fallo y sus contrafactuales sin fallo, de sesiones de "
            "entrenamiento de synthetic_v2. ARTEFACTO DERIVADO PARA ANALISIS VISUAL."
        ),
        "que_no_es": [
            "no entra en entrenamiento, validacion ni prueba",
            "no modifica ninguna metrica historica",
            "no se usa para ajustar ningun modelo",
            "no es una evaluacion nueva ni independiente",
            "no es un conjunto de datos: no tiene particiones ni ventanado",
        ],
        "generado_el": datetime.now(UTC).isoformat(timespec="seconds"),
        "commit": _commit(),
        "conjunto_de_origen": "synthetic_v2",
        "plan": {"semilla": SEMILLA_DEL_PLAN, "sesiones_por_fallo": SESIONES_POR_FALLO},
        "mecanismo": (
            "El motor de senales avanza al margen del fallo: la trayectoria sana es el valor "
            "que generate_session pasa a la funcion de fallo. El contrafactual se obtiene con "
            "la misma especificacion y fault_id=F00_normal. No hay generador nuevo."
        ),
        "verificacion": (
            "Cada sesion original se regenero con el esquema historico y se comparo muestra a "
            "muestra con synthetic_v2.parquet: identicas con tolerancia 1e-9. Y las dos "
            "trayectorias de cada pareja son identicas antes del instante de entrada."
        ),
        "huella_del_conjunto_de_origen": {
            "data/raw/synthetic/synthetic_v2.parquet": _huella_de_fichero(CRUDO)
        },
        "huellas_del_generador": {
            ruta: _huella_de_fichero(paths.ROOT / ruta) for ruta in FUENTES_DEL_GENERADOR
        },
        "sesiones": [
            {
                "session_id": p.spec.session_id,
                "fault_id": p.spec.fault_id,
                "regime": p.spec.regime,
                "particion_de_origen": p.particion,
                "seed": p.spec.seed,
                "duration_s": p.spec.duration_s,
                "sample_rate_hz": p.spec.sample_rate_hz,
                "ambient_temp_c": p.spec.ambient_temp_c,
                "fault_onset_s": p.spec.fault_onset_s,
                "senales_alteradas": list(p.señales_alteradas),
                "muestras_con_expresion": int(p.con_fallo.fault_expressed.sum()),
                "muestras_totales": len(p.con_fallo),
            }
            for p in parejas
        ],
        "huella_sha256": _huella_de_fichero(destino),
        "filas": len(tabla),
    }
    ficha_ruta = SALIDA / "T2_contrafactual_synthetic_v2.procedencia.json"
    ficha_ruta.write_text(json.dumps(ficha, indent=2, ensure_ascii=True) + "\n", "utf-8")
    return destino, ficha_ruta


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("--solo", default=None, help="una sola condición, por identificador")
    args = analizador.parse_args(argv)

    if not CRUDO.is_file():
        print(f"no está en disco: {CRUDO.relative_to(paths.ROOT)}", file=sys.stderr)
        return 2

    crudo = pd.read_parquet(CRUDO)
    particiones = _particiones()
    specs = build_balanced_specs(seed=SEMILLA_DEL_PLAN, sessions_per_fault=SESIONES_POR_FALLO)
    elegidas = seleccionar(specs, particiones)
    if args.solo is not None:
        elegidas = [s for s in elegidas if s.fault_id == args.solo]
        if not elegidas:
            print(f"ninguna sesión seleccionada para {args.solo}", file=sys.stderr)
            return 1

    parejas: list[Pareja] = []
    for spec in elegidas:
        try:
            pareja = construir_pareja(spec, crudo, particiones.get(spec.session_id, "?"))
        except ReconstruccionFallidaError as error:
            print(f"  DETENIDO  {error}", file=sys.stderr)
            print(
                "\nNo se escribe nada. La sesión original no se reproduce de forma "
                "verificable, de modo que no se puede presentar una comparación pareada "
                "como si lo fuera.",
                file=sys.stderr,
            )
            return 1
        parejas.append(pareja)
        print(
            f"  {spec.fault_id:22s} {spec.session_id:34s} "
            f"expresa {int(pareja.con_fallo.fault_expressed.sum()):3d}/"
            f"{len(pareja.con_fallo)} muestras · altera "
            f"{len(pareja.señales_alteradas)} señales"
        )

    destino, ficha = escribir(parejas)
    print(f"\n  escrito  {destino.relative_to(paths.ROOT)}")
    print(f"  ficha    {ficha.relative_to(paths.ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
