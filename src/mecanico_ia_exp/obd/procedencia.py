"""Manifiesto de procedencia por sesión: con qué configuración exacta se generó.

La ficha de ``data/metadata.py`` responde a la pregunta por conjunto --cuántas
sesiones, qué señales, qué semilla global-- y eso bastaba mientras el plan de
generación fuera el equilibrado por omisión, determinista y derivable de la
semilla global. **Deja de bastar en cuanto se varía un parámetro por sesión.**

Lo que no quedaba registrado y aquí sí: la semilla individual de cada sesión, su
duración, su temperatura ambiente, el instante de aparición del fallo y los
parámetros con que se aplicó.

## Por qué las huellas y no la versión declarada

``GENERATOR_VERSION`` fue ``"1.0.0"`` para ``synthetic_v2`` y para
``synthetic_v3``, que salen de generadores distintos --el segundo con las
constantes calibradas contra el manual--. Una constante escrita a mano no sirve
como identidad: lo que identifica el fenómeno generado es la **huella de los
módulos que lo producen**.

El fichero de calibración figura entre ellas con una salvedad escrita: documenta
la procedencia de las constantes, pero **ningún módulo lo lee**. Sus valores
están copiados a mano en ``obd/engine.py``, de modo que la huella que de verdad
fija el fenómeno es la de ese módulo. La del YAML se registra para detectar que
los dos se separen.

## La prueba que lo justifica

Un manifiesto que no permita regenerar una sesión no sirve de nada.
``reconstruir`` devuelve la especificación de una sesión a partir del
manifiesto, y la comprobación es regenerar con ella y obtener la misma serie.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.obd.expresion import RATIO_DECLARADO, SIGMA_GENERADOR, tolerancias
from mecanico_ia_exp.obd.signals import SIGNAL_NAMES
from mecanico_ia_exp.obd.synthetic import GENERATOR_VERSION, SessionSpec

#: Módulos cuya huella identifica el fenómeno generado, y el fichero de
#: calibración, que lo documenta sin que ningún módulo lo lea.
FUENTES_DEL_GENERADOR: tuple[str, ...] = (
    "src/mecanico_ia_exp/obd/engine.py",
    "src/mecanico_ia_exp/obd/synthetic.py",
    "src/mecanico_ia_exp/obd/faults.py",
    "src/mecanico_ia_exp/obd/regimes.py",
    "src/mecanico_ia_exp/obd/signals.py",
    "src/mecanico_ia_exp/obd/expresion.py",
    "configs/calibracion_mazda3_bk.yaml",
)

#: El fichero de calibración no lo lee ningún módulo. Se declara para que la
#: salvedad viaje con el manifiesto y no solo con esta docstring.
CALIBRACION_NO_LEIDA = "configs/calibracion_mazda3_bk.yaml"


class ProcedenciaIncompletaError(RuntimeError):
    """El manifiesto no permite reconstruir lo que dice reconstruir."""


def ruta_de(dataset_id: str) -> Path:
    """Dónde vive el manifiesto de un conjunto. Junto a su parquet, no aparte."""
    return paths.DATA_RAW_SYNTHETIC / f"{dataset_id}.provenance.json"


def huella_16(ruta: Path) -> str:
    """Primeros dieciséis caracteres del SHA-256 de un fichero."""
    return hashlib.sha256(ruta.read_bytes()).hexdigest()[:16]


def _git(*args: str) -> str | None:
    try:
        salida = subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return salida.stdout.strip() if salida.returncode == 0 else None


def _arbol_sucio() -> bool | None:
    """``None`` significa que no se pudo determinar, que no es lo mismo que limpio."""
    estado = _git("status", "--porcelain")
    return None if estado is None else bool(estado.strip())


def huellas_del_generador(raiz: Path | None = None) -> dict[str, str]:
    """Huella de cada fuente del generador.

    Una fuente que falte es un error y no un hueco: sin ella el manifiesto no
    identifica el generador, que es lo único que este fichero existe para hacer.
    """
    base = raiz or paths.ROOT
    huellas: dict[str, str] = {}
    for relativa in FUENTES_DEL_GENERADOR:
        ruta = base / relativa
        if not ruta.is_file():
            msg = f"Falta una fuente del generador: {relativa}"
            raise ProcedenciaIncompletaError(msg)
        huellas[relativa] = huella_16(ruta)
    return huellas


def _ficha_de_sesion(spec: SessionSpec, n_samples: int) -> dict[str, Any]:
    """Todo lo que hace falta para regenerar una sesión, y nada más."""
    return {
        "session_id": spec.session_id,
        "seed": spec.seed,
        "regime": spec.regime,
        "duration_s": spec.duration_s,
        "sample_rate_hz": spec.sample_rate_hz,
        "fault_id": spec.fault_id,
        "fault_onset_s": spec.fault_onset_s,
        "ambient_temp_c": spec.ambient_temp_c,
        "fault_params": dict(spec.fault_params),
        "n_samples": n_samples,
    }


def construir(
    specs: list[SessionSpec],
    datos: pd.DataFrame,
    *,
    dataset_id: str,
    seed: int,
    ratio_expresion: float = RATIO_DECLARADO,
    artefactos: dict[str, Path] | None = None,
    raiz: Path | None = None,
) -> dict[str, Any]:
    """Construye el manifiesto de un conjunto ya generado."""
    por_sesion = datos.groupby("session_id", sort=False).size().to_dict()
    faltan = [s.session_id for s in specs if s.session_id not in por_sesion]
    if faltan:
        msg = f"Especificaciones sin datos generados: {faltan}"
        raise ProcedenciaIncompletaError(msg)

    tasas = {s.sample_rate_hz for s in specs}
    return {
        "dataset_id": dataset_id,
        "dataset_type": "synthetic",
        "created_at": datetime.now(UTC).isoformat(),
        "generator": {
            "module": "mecanico_ia_exp.obd.synthetic",
            "declared_version": GENERATOR_VERSION,
            "declared_version_no_identifica": (
                "fue la misma para synthetic_v2 y synthetic_v3, que son fenómenos distintos; "
                "la identidad son las huellas"
            ),
            "commit": _git("rev-parse", "HEAD"),
            "dirty": _arbol_sucio(),
            "source_fingerprints_16": huellas_del_generador(raiz),
            "calibracion_no_leida_por_ningun_modulo": CALIBRACION_NO_LEIDA,
        },
        "expression": {
            "ratio_declarado": ratio_expresion,
            "sigma_generador": dict(SIGMA_GENERADOR),
            "umbral_por_senal": tolerancias(ratio_expresion),
            "definicion": (
                "fault_expressed = la trayectoria recortada difiere de su contrafactual, "
                "con la misma semilla y el mismo estado del motor, en al menos un umbral "
                "de alguna señal; fault_deviation_max guarda la magnitud en esos umbrales"
            ),
        },
        "global_seed": seed,
        "sampling_rate_hz": tasas.pop() if len(tasas) == 1 else -1.0,
        "signals": list(SIGNAL_NAMES),
        "n_sessions": len(specs),
        "n_samples": len(datos),
        "sessions": [_ficha_de_sesion(s, int(por_sesion[s.session_id])) for s in specs],
        "temporal_distribution": {
            "by_regime": dict(sorted(Counter(s.regime for s in specs).items())),
            "by_condition": dict(sorted(Counter(s.fault_id for s in specs).items())),
        },
        "artifact_fingerprints_16": {
            nombre: huella_16(ruta) for nombre, ruta in sorted((artefactos or {}).items())
        },
    }


def reconstruir(manifiesto: dict[str, Any], session_id: str) -> SessionSpec:
    """Devuelve la especificación de una sesión tal como el manifiesto la guarda.

    Es la operación que da sentido al fichero: si de aquí no sale una
    especificación que regenere la misma serie, el manifiesto no documenta la
    procedencia aunque lo diga en su nombre.
    """
    for ficha in manifiesto["sessions"]:
        if ficha["session_id"] == session_id:
            return SessionSpec(
                session_id=ficha["session_id"],
                regime=ficha["regime"],
                duration_s=ficha["duration_s"],
                seed=ficha["seed"],
                fault_id=ficha["fault_id"],
                fault_onset_s=ficha["fault_onset_s"],
                ambient_temp_c=ficha["ambient_temp_c"],
                sample_rate_hz=ficha["sample_rate_hz"],
                fault_params=tuple(sorted(ficha["fault_params"].items())),
            )
    disponibles = len(manifiesto["sessions"])
    msg = f"El manifiesto no contiene {session_id!r}; tiene {disponibles} sesiones"
    raise ProcedenciaIncompletaError(msg)


def escribir(destino: Path, manifiesto: dict[str, Any]) -> Path:
    """Escribe el manifiesto, **negándose a sobrescribir** uno existente.

    Un manifiesto sobrescrito es procedencia perdida sin aviso, que es
    exactamente lo que este fichero existe para impedir.
    """
    if destino.exists():
        msg = f"Ya existe un manifiesto en {destino}; no se sobrescribe"
        raise FileExistsError(msg)
    paths.ensure(destino.parent)
    destino.write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return destino
