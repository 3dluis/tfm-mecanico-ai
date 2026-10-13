"""Destinos de escritura: ni sobrescribir una ejecución, ni tocar lo histórico.

Dos problemas distintos, con la misma raíz: **rutas de salida fijas**.

El primero es que una ejecución nueva pise a la anterior. ``run_baseline``
escribía en seis rutas fijas --un registro, tres tablas y dos figuras-- de modo
que reejecutar E6 para obtener predicciones por ventana habría borrado el
registro histórico y sus artefactos en lugar de producir una verificación
comparable. Se resuelve con una **etiqueta de ejecución** que entra en el nombre
de todos los artefactos, y con la negativa a escribir si alguno existe ya.

El segundo es más amplio: ``tables/``, ``figures/`` y ``data/`` están fuera del
control de versiones, así que Git no puede avisar de que un artefacto histórico
cambió. La única protección posible es un **censo de huellas** tomado antes y
comprobado después. Eso es lo que hace ``verificar_historicos``: no evita el
daño, lo hace **detectable**, que es la diferencia entre una promesa y una
comprobación.

## Fallo cerrado

Un artefacto declarado que **falta** es un fallo, no un hueco: significa que algo
lo borró. Un registro que no se puede leer es también un fallo. La función no
devuelve «no sé»: devuelve la lista de desviaciones, y quien la llama se detiene
si no está vacía.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from mecanico_ia_exp.config import paths

#: Censo de artefactos que ninguna ejecución nueva puede modificar.
REGISTRO_HISTORICO: Path = paths.CONFIGS / "artefactos_historicos.json"

#: Qué se declara histórico. Son patrones y no una lista escrita a mano para que
#: el censo no se quede corto al añadirse un artefacto; lo que fija el contenido
#: es el censo ya escrito, no el patrón.
PATRONES_HISTORICOS: tuple[str, ...] = (
    "experiments/*.json",
    "experiments/pre_mixed_embedding_fix/*.json",
    "tables/*.csv",
    "figures/*.png",
    "data/raw/synthetic/*.parquet",
    "data/raw/synthetic/*.meta.json",
    "models/*.npy",
    "models/*/finetune_config.json",
    "artifacts/metrics/*.json",
    "artifacts/tables/*.csv",
    "configs/manifest_e19.json",
    "configs/congelacion-e19.anchor.json",
    # El conjunto anotado va censado porque el manifiesto de E19 lo fija **por
    # huella**: editarlo rompería la verificación de la congelación. El rediseño
    # de la condición con distractor tiene que escribir un fichero nuevo.
    "configs/goldset_mazda3_bk.yaml",
    "configs/politica_suficiencia*.json",
)


class ArtefactoOcupadoError(RuntimeError):
    """Una ruta de salida ya existe y la ejecución no puede sobrescribirla."""


class HistoricoAlteradoError(RuntimeError):
    """Un artefacto declarado histórico cambió, falta o no se puede leer."""


def huella(ruta: Path) -> str:
    """SHA-256 completo. Entero y no truncado: aquí el coste es irrelevante."""
    digest = hashlib.sha256()
    with ruta.open("rb") as flujo:
        for bloque in iter(lambda: flujo.read(1 << 20), b""):
            digest.update(bloque)
    return digest.hexdigest()


def exigir_libres(destinos: dict[str, Path]) -> dict[str, Path]:
    """Falla si alguno de los destinos existe ya.

    Se comprueban **todos a la vez y antes de escribir el primero**: descubrir a
    mitad de una ejecución que se está pisando un artefacto anterior ya sería
    tarde, porque los anteriores ya estarían escritos.
    """
    ocupados = {clave: ruta for clave, ruta in destinos.items() if ruta.exists()}
    if ocupados:
        listado = "\n".join(f"  - {clave}: {ruta}" for clave, ruta in sorted(ocupados.items()))
        msg = (
            f"{len(ocupados)} destino(s) ya existen y no se sobrescriben:\n{listado}\n"
            "Dale a esta ejecución su propia etiqueta en lugar de sustituir lo anterior."
        )
        raise ArtefactoOcupadoError(msg)
    return destinos


def censar(
    patrones: Iterable[str] = PATRONES_HISTORICOS, *, raiz: Path | None = None
) -> dict[str, str]:
    """Huella de cada artefacto que encaja en los patrones, por ruta relativa."""
    base = raiz or paths.ROOT
    censo: dict[str, str] = {}
    for patron in patrones:
        for ruta in sorted(base.glob(patron)):
            if ruta.is_file():
                censo[str(ruta.relative_to(base))] = huella(ruta)
    return censo


def escribir_censo(destino: Path | None = None, *, raiz: Path | None = None) -> Path:
    """Escribe el censo con la fecha en que se tomó.

    **Sobrescribe a propósito**, al contrario que todo lo demás en este módulo:
    el censo no es evidencia experimental, es el instrumento que la vigila, y
    tiene que poder ampliarse cuando se declara histórico un artefacto nuevo.
    Lo que no puede cambiar es la huella de lo ya censado, y de eso se encarga
    ``verificar_historicos``.
    """
    ruta = destino or REGISTRO_HISTORICO
    censo = censar(raiz=raiz)
    contenido = {
        "tomado_el": datetime.now(UTC).isoformat(),
        "para_que": (
            "detectar que una ejecución nueva modificó un artefacto histórico; "
            "tables/, figures/ y data/ están fuera de Git y no tienen otra protección"
        ),
        "patrones": list(PATRONES_HISTORICOS),
        "n_artefactos": len(censo),
        "huellas_sha256": censo,
    }
    paths.ensure(ruta.parent)
    ruta.write_text(json.dumps(contenido, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return ruta


@dataclass(frozen=True)
class Desviacion:
    """Un artefacto histórico que no está como se declaró."""

    ruta: str
    motivo: str

    def __str__(self) -> str:
        return f"{self.ruta}: {self.motivo}"


def verificar_historicos(
    censo: Path | None = None, *, raiz: Path | None = None
) -> list[Desviacion]:
    """Compara el estado actual contra el censo.

    Un artefacto **nuevo** que encaje en los patrones no es una desviación: el
    censo vigila lo que ya existía, y producir artefactos nuevos es lo que una
    ejecución nueva hace.
    """
    ruta = censo or REGISTRO_HISTORICO
    base = raiz or paths.ROOT
    if not ruta.is_file():
        return [Desviacion(str(ruta), "no existe el censo de artefactos históricos")]
    try:
        contenido = json.loads(ruta.read_text("utf-8"))
        declaradas: dict[str, str] = contenido["huellas_sha256"]
    except (json.JSONDecodeError, KeyError, OSError) as error:
        return [Desviacion(str(ruta), f"el censo no se puede leer: {error}")]

    desviaciones: list[Desviacion] = []
    for relativa, esperada in sorted(declaradas.items()):
        fichero = base / relativa
        if not fichero.is_file():
            desviaciones.append(Desviacion(relativa, "falta"))
            continue
        try:
            actual = huella(fichero)
        except OSError as error:
            desviaciones.append(Desviacion(relativa, f"no se puede leer: {error}"))
            continue
        if actual != esperada:
            desviaciones.append(Desviacion(relativa, f"cambió: {esperada[:16]} → {actual[:16]}"))
    return desviaciones


def exigir_historicos_intactos(censo: Path | None = None, *, raiz: Path | None = None) -> int:
    """Se detiene si algún artefacto histórico cambió. Devuelve cuántos verificó."""
    desviaciones = verificar_historicos(censo, raiz=raiz)
    if desviaciones:
        listado = "\n".join(f"  - {d}" for d in desviaciones)
        msg = f"{len(desviaciones)} artefacto(s) histórico(s) alterado(s):\n{listado}"
        raise HistoricoAlteradoError(msg)
    ruta = censo or REGISTRO_HISTORICO
    return len(json.loads(ruta.read_text("utf-8"))["huellas_sha256"])
