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
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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
    # La ficha `*.meta.json` **no** se censa: lleva `created_at`, de modo que una
    # reconstrucción legítima la cambia siempre y la vigilancia daría una alarma
    # en cada reconstrucción. Una alarma que salta siempre deja de mirarse. Lo
    # que sí se vigila es el parquet, que **sí** es reproducible bit a bit: ahí
    # están los datos, y una sustitución silenciosa de la ficha sin tocar el
    # parquet no cambiaría ninguna cifra medida.
    "models/*.npy",
    "models/*/finetune_config.json",
    # Los ejemplos con que se ajustó el adaptador. Están fuera del control de
    # versiones y son lo que haría irreproducible el ajuste si cambiaran sin
    # que nadie lo notara.
    "data/processed/slm_finetune/*.jsonl",
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


def _versionados(raiz: Path) -> frozenset[str]:
    """Qué rutas lleva Git. Fuera de un repositorio, el conjunto vacío.

    Importa para no confundir dos cosas muy distintas: un artefacto **que falta
    porque no se versiona** —`tables/`, `figures/` y `data/` están en
    `.gitignore`, de modo que un clon recién hecho no los tiene— y un artefacto
    **que falta porque algo lo borró**. Lo primero es el estado normal de una
    copia limpia; lo segundo es la alarma que este censo existe para dar.
    """
    try:
        salida = subprocess.run(
            ["git", "-C", str(raiz), "ls-files"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return frozenset()
    if salida.returncode != 0:
        return frozenset()
    return frozenset(linea for linea in salida.stdout.splitlines() if linea)


def censar(
    patrones: Iterable[str] = PATRONES_HISTORICOS, *, raiz: Path | None = None
) -> dict[str, dict[str, object]]:
    """Huella de cada artefacto que encaja en los patrones, por ruta relativa.

    Cada entrada dice además si **Git lleva ese fichero**, que es lo que
    permite después distinguir una ausencia esperada de una alarma.
    """
    base = raiz or paths.ROOT
    seguidos = _versionados(base)
    censo: dict[str, dict[str, object]] = {}
    for patron in patrones:
        for ruta in sorted(base.glob(patron)):
            if ruta.is_file():
                relativa = str(ruta.relative_to(base))
                censo[relativa] = {
                    "sha256": huella(ruta),
                    "versionado": relativa in seguidos,
                }
    return censo


def escribir_censo(
    destino: Path | None = None, *, raiz: Path | None = None, aceptar_cambios: bool = False
) -> Path:
    """Amplía el censo, **comprobando antes que lo ya censado no ha cambiado**.

    El censo tiene que poder crecer cuando se declara histórico un artefacto
    nuevo. Lo que no puede hacer es **absorber un cambio**: si un artefacto
    censado se alteró y se reescribe el censo sin mirar, la huella nueva pasa a
    ser la esperada y la verificación posterior lo da por intacto. El censo
    habría dejado de vigilar justo lo que existe para vigilar, y en silencio.

    Por eso esta función verifica primero y se niega si encuentra una
    desviación. ``aceptar_cambios`` existe para el único caso legítimo —el autor
    decide que un artefacto cambió a propósito— y obliga a pedirlo
    explícitamente.
    """
    ruta = destino or REGISTRO_HISTORICO
    if ruta.is_file() and not aceptar_cambios:
        desviaciones = verificar_historicos(ruta, raiz=raiz)
        if desviaciones:
            listado = "\n".join(f"  - {d}" for d in desviaciones)
            msg = (
                f"No se reescribe el censo: {len(desviaciones)} artefacto(s) censado(s) han "
                f"cambiado o faltan.\n{listado}\n"
                "Reescribirlo ahora convertiría la huella alterada en la esperada y la "
                "verificación posterior daría el artefacto por intacto. Si el cambio es "
                "deliberado, pásalo con aceptar_cambios=True y déjalo escrito en el informe "
                "de la fase."
            )
            raise HistoricoAlteradoError(msg)

    censo = censar(raiz=raiz)
    # Y se **conservan** las entradas de lo que esta copia no tiene porque no se
    # versiona. Sin esto, ampliar el censo desde un clon recién hecho borraría
    # las huellas de los 67 artefactos que viven fuera de Git --que son
    # precisamente los que nada más protege-- y el censo saldría más corto sin
    # que nadie lo notara.
    if ruta.is_file():
        try:
            previas: dict[str, Any] = json.loads(ruta.read_text("utf-8"))["huellas_sha256"]
        except (json.JSONDecodeError, KeyError, OSError):
            previas = {}
        base = raiz or paths.ROOT
        conservadas = 0
        for relativa, entrada in previas.items():
            if relativa in censo or (base / relativa).is_file():
                continue
            if isinstance(entrada, dict) and not entrada.get("versionado", True):
                censo[relativa] = entrada
                conservadas += 1
        if conservadas:
            print(
                f"censo: conservadas {conservadas} huella(s) de artefactos que esta copia "
                "no tiene porque no se versionan"
            )
    contenido = {
        "tomado_el": datetime.now(UTC).isoformat(),
        "cambios_aceptados_a_proposito": aceptar_cambios,
        "para_que": (
            "detectar que una ejecución nueva modificó un artefacto histórico; "
            "tables/, figures/ y data/ están fuera de Git y no tienen otra protección"
        ),
        "sobre_las_ausencias": (
            "un artefacto con versionado=false que falta NO es una desviación: es el "
            "estado normal de un clon recién hecho, porque Git no lo lleva. Uno con "
            "versionado=true que falta sí lo es, y cualquiera que haya cambiado también"
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

    Qué cuenta como desviación, y qué no:

    * un artefacto **que cambió** siempre lo es, esté versionado o no;
    * un artefacto **versionado que falta** lo es: Git lo lleva, así que su
      ausencia significa que algo lo borró;
    * un artefacto **no versionado que falta no lo es**. `tables/`, `figures/`
      y `data/` están en `.gitignore`, de modo que un clon recién hecho no los
      tiene. Tratar esa ausencia como alarma haría que la verificación fallara
      en la máquina del tribunal sin que nada estuviera mal, que es la forma más
      segura de que nadie la mire;
    * un artefacto **nuevo** tampoco lo es: el censo vigila lo que ya existía, y
      producir artefactos nuevos es lo que una ejecución nueva hace.
    """
    ruta = censo or REGISTRO_HISTORICO
    base = raiz or paths.ROOT
    if not ruta.is_file():
        return [Desviacion(str(ruta), "no existe el censo de artefactos históricos")]
    try:
        contenido = json.loads(ruta.read_text("utf-8"))
        declaradas: dict[str, Any] = contenido["huellas_sha256"]
    except (json.JSONDecodeError, KeyError, OSError) as error:
        return [Desviacion(str(ruta), f"el censo no se puede leer: {error}")]

    desviaciones: list[Desviacion] = []
    for relativa, entrada in sorted(declaradas.items()):
        # Censos anteriores guardaban la huella suelta; se siguen leyendo.
        if isinstance(entrada, str):
            esperada, versionado = entrada, True
        else:
            esperada = str(entrada["sha256"])
            versionado = bool(entrada.get("versionado", True))

        fichero = base / relativa
        if not fichero.is_file():
            if versionado:
                desviaciones.append(Desviacion(relativa, "falta, y Git lo lleva"))
            continue
        try:
            actual = huella(fichero)
        except OSError as error:
            desviaciones.append(Desviacion(relativa, f"no se puede leer: {error}"))
            continue
        if actual != esperada:
            desviaciones.append(Desviacion(relativa, f"cambió: {esperada[:16]} → {actual[:16]}"))
    return desviaciones


def ausentes_por_no_versionarse(
    censo: Path | None = None, *, raiz: Path | None = None
) -> list[str]:
    """Los artefactos censados que este clon no tiene porque Git no los lleva.

    No son un problema: son la lista de lo que haría falta regenerar para poder
    verificarlos. Se devuelve aparte para poder informarla sin confundirla con
    una alarma.
    """
    ruta = censo or REGISTRO_HISTORICO
    base = raiz or paths.ROOT
    if not ruta.is_file():
        return []
    declaradas: dict[str, Any] = json.loads(ruta.read_text("utf-8"))["huellas_sha256"]
    return sorted(
        relativa
        for relativa, entrada in declaradas.items()
        if isinstance(entrada, dict)
        and not entrada.get("versionado", True)
        and not (base / relativa).is_file()
    )


def exigir_historicos_intactos(censo: Path | None = None, *, raiz: Path | None = None) -> int:
    """Se detiene si algún artefacto histórico cambió. Devuelve cuántos verificó."""
    desviaciones = verificar_historicos(censo, raiz=raiz)
    if desviaciones:
        listado = "\n".join(f"  - {d}" for d in desviaciones)
        msg = f"{len(desviaciones)} artefacto(s) histórico(s) alterado(s):\n{listado}"
        raise HistoricoAlteradoError(msg)
    ruta = censo or REGISTRO_HISTORICO
    return len(json.loads(ruta.read_text("utf-8"))["huellas_sha256"])
