"""Soporte para los notebooks: procedencia, modalidad y salida aislada.

Los notebooks no duplican lógica científica: importan del paquete. Lo que sí
necesitan, y no existía, son tres cosas que **no** deben escribirse a mano en
cada uno:

1. **Resolver la raíz del repositorio** sin rutas absolutas ni suposiciones
   sobre el directorio desde el que se abrió Jupyter.
2. **Leer los artefactos que un clon del repositorio sí trae.** `tables/` y
   `figures/` están fuera del control de versiones; `artifacts/` es su copia
   versionada, y es la única de las dos que el jurado tiene. Un notebook que
   leyera de `tables/` funcionaría en la máquina del autor y fallaría en la del
   tribunal.
3. **Escribir en un directorio propio.** Ningún notebook puede sobrescribir un
   artefacto histórico, y la forma de garantizarlo no es la buena intención: es
   que la función que da la ruta de salida devuelva siempre un directorio
   distinto de donde viven los artefactos.

## La modalidad, y por qué va declarada

Cuatro cosas distintas se confunden con facilidad, y la confusión es grave en un
documento que se entrega como evidencia:

* **REPRODUCCIÓN** — el notebook vuelve a ejecutar el cálculo y obtiene el mismo
  número que está publicado.
* **REANÁLISIS** — el notebook calcula algo **nuevo** sobre datos ya existentes.
  El número no está publicado y no puede presentarse como si lo estuviera.
* **VISUALIZACIÓN DE EVIDENCIA HISTÓRICA** — el notebook **lee** un artefacto
  congelado y lo muestra. No reproduce nada: si el artefacto estuviera mal, el
  notebook lo mostraría igual de mal.
* **DEMOSTRACIÓN ILUSTRATIVA** — el notebook genera un ejemplo para explicar un
  concepto. No es evidencia de nada.

Cada notebook declara la suya al principio con ``declarar_modalidad``, y la
declaración se imprime: queda en la salida, no solo en una celda de texto que
puede quedar desactualizada.
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from mecanico_ia_exp.config import paths

#: Las cuatro modalidades, con lo que cada una autoriza a afirmar.
MODALIDADES: dict[str, str] = {
    "REPRODUCCIÓN": ("se vuelve a ejecutar el cálculo y se comprueba que da la cifra publicada"),
    "REANÁLISIS": (
        "se calcula algo nuevo sobre datos existentes; la cifra NO está publicada y no "
        "puede citarse como si lo estuviera"
    ),
    "VISUALIZACIÓN DE EVIDENCIA HISTÓRICA": (
        "se lee un artefacto congelado y se muestra; no se reproduce nada"
    ),
    "DEMOSTRACIÓN ILUSTRATIVA": (
        "se genera un ejemplo para explicar un concepto; no es evidencia de ningún resultado"
    ),
}

#: Dónde escriben los notebooks. Fuera de `experiments/`, `tables/`, `figures/`
#: y `data/`, que es donde viven los artefactos que no se pueden tocar.
SALIDA = paths.ROOT / "notebooks" / "salida"

#: Copia versionada de los artefactos. **Es la que el jurado tiene.**
ARTEFACTOS = paths.ROOT / "artifacts"


class ArtefactoNoDisponibleError(FileNotFoundError):
    """El artefacto que el notebook necesita no está en este clon del repositorio.

    Se distingue de un error genérico a propósito: el mensaje tiene que decir si
    falta porque no se versiona --y entonces el notebook es FULL-- o porque algo
    se borró.
    """


def raiz() -> Path:
    """La raíz del repositorio, sin rutas absolutas escritas a mano."""
    return paths.ROOT


@dataclass(frozen=True)
class Modalidad:
    """La modalidad declarada de un notebook, con lo que autoriza a afirmar."""

    nombre: str
    que_autoriza: str
    detalle: str

    def __str__(self) -> str:
        return f"MODALIDAD: {self.nombre}\n  {self.que_autoriza}\n  {self.detalle}"


def declarar_modalidad(nombre: str, detalle: str = "") -> Modalidad:
    """Declara la modalidad del notebook y la imprime.

    Falla si el nombre no es una de las cuatro: una modalidad inventada no
    significa nada y lo que se busca es exactamente lo contrario.
    """
    if nombre not in MODALIDADES:
        msg = f"Modalidad desconocida: {nombre!r}; las declaradas son {sorted(MODALIDADES)}"
        raise ValueError(msg)
    modalidad = Modalidad(nombre, MODALIDADES[nombre], detalle)
    print(modalidad)
    return modalidad


def entorno() -> dict[str, str]:
    """Lo que hace falta para saber si una ejecución es comparable con otra."""
    commit = _git("rev-parse", "--short", "HEAD")
    sucio = _git("status", "--porcelain")
    return {
        "python": sys.version.split()[0],
        "plataforma": f"{platform.system()} {platform.machine()}",
        "commit": commit or "desconocido (sin historial de Git)",
        "arbol": "limpio" if sucio == "" else ("sucio" if sucio else "indeterminado"),
    }


def _git(*args: str) -> str | None:
    try:
        salida = subprocess.run(
            ["git", "-C", str(paths.ROOT), *args],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return salida.stdout.strip() if salida.returncode == 0 else None


def imprimir_entorno() -> None:
    """Deja el entorno en la salida del notebook, no solo en una celda de texto."""
    for clave, valor in entorno().items():
        print(f"{clave:12s} {valor}")


# ------------------------------------------------------- lectura de artefactos


def registro(nombre: str) -> dict[str, Any]:
    """Lee un registro de ``experiments/`` por su nombre, con o sin extensión.

    Los registros JSON **sí** están versionados: son la evidencia de toda cifra
    publicada, y es lo único que un notebook necesita para mostrarla sin
    recalcularla.
    """
    archivo = paths.EXPERIMENTS / (nombre if nombre.endswith(".json") else f"{nombre}.json")
    if not archivo.is_file():
        msg = (
            f"No está el registro {archivo.name} en experiments/. "
            "Los registros JSON se versionan, así que su ausencia significa que algo se borró, "
            "no que haga falta generarlo."
        )
        raise ArtefactoNoDisponibleError(msg)
    return dict(json.loads(archivo.read_text("utf-8")))


def tabla(nombre: str) -> pd.DataFrame:
    """Lee una tabla de ``artifacts/tables/``, que es la copia versionada."""
    archivo = ARTEFACTOS / "tables" / (nombre if nombre.endswith(".csv") else f"{nombre}.csv")
    if not archivo.is_file():
        disponibles = sorted(p.name for p in (ARTEFACTOS / "tables").glob("*.csv"))
        msg = (
            f"No está la tabla {archivo.name} en artifacts/tables/.\n"
            f"Hay {len(disponibles)} tablas versionadas; si la que falta se genera en una fase "
            "que este clon no puede ejecutar, el notebook es de modo FULL y debe declararlo.\n"
            f"Disponibles: {', '.join(disponibles[:8])}…"
        )
        raise ArtefactoNoDisponibleError(msg)
    return pd.read_csv(archivo)


def figura(nombre: str) -> Path:
    """Ruta de una figura publicada en ``artifacts/figures/``."""
    archivo = ARTEFACTOS / "figures" / (nombre if nombre.endswith(".png") else f"{nombre}.png")
    if not archivo.is_file():
        msg = f"No está la figura {archivo.name} en artifacts/figures/"
        raise ArtefactoNoDisponibleError(msg)
    return archivo


def muestra_redistribuible() -> pd.DataFrame:
    """El conjunto de 18 sesiones que **sí** viaja con el repositorio.

    `data/raw/**` está fuera del control de versiones, así que `synthetic_v2` y
    `synthetic_v3` no están en un clon. Esta muestra sí, y además es
    **regenerable**: sale de ``build_balanced_specs(seed=20260901,
    sessions_per_fault=3)`` y se ha comprobado que coincide bit a bit con el
    fichero versionado.
    """
    archivo = paths.ROOT / "data" / "samples" / "synthetic_sample.parquet"
    if not archivo.is_file():
        msg = (
            "No está data/samples/synthetic_sample.parquet, que sí se versiona. "
            "Se puede regenerar con build_balanced_specs(seed=20260901, sessions_per_fault=3)."
        )
        raise ArtefactoNoDisponibleError(msg)
    return pd.read_parquet(archivo)


# --------------------------------------------------------------------- salida


def salida(subdirectorio: str = "") -> Path:
    """Directorio donde el notebook puede escribir, creado si no existe.

    **Nunca** devuelve una ruta dentro de `experiments/`, `tables/`, `figures/`
    ni `data/`. Esa es la garantía, y no depende de que quien escriba el
    notebook se acuerde.
    """
    destino = SALIDA / subdirectorio if subdirectorio else SALIDA
    destino.mkdir(parents=True, exist_ok=True)
    return destino


# --------------------------------------------------- figuras con procedencia

#: Toda figura de un notebook lleva al pie de qué experimento y de qué conjunto
#: sale. No es decoración: una figura suelta, sin esa línea, no se puede citar.
PIE_DE_FIGURA = "{experimento} · {dataset} · {procedencia}"


def lienzo(
    *,
    experimento: str,
    dataset: str,
    procedencia: str,
    titulo: str,
    filas: int = 1,
    columnas: int = 1,
    ancho: float = 9.0,
    alto: float = 3.2,
    para_la_memoria: bool = False,
) -> tuple[Any, Any]:
    """Crea una figura con el estilo del laboratorio y su procedencia al pie.

    ``procedencia`` dice **de dónde salen los números**: el registro, la tabla o
    la celda que los calculó. Es el campo que permite al lector ir a
    comprobarlos, y por eso es obligatorio en lugar de opcional.

    **``para_la_memoria``.** Una figura que va al documento no puede llevar
    dentro su título ni su procedencia: los lleva el documento, como texto
    editable que entra en el índice de figuras y se corrige sin regenerar el
    PNG. Con esta bandera el lienzo sale limpio —solo el gráfico— y los dos
    campos siguen siendo obligatorios aquí porque es el notebook quien tiene que
    declararlos: se imprimen debajo de la celda en lugar de dentro de la imagen.

    Para una figura que vive **solo** en el notebook la bandera sobra: ahí no hay
    pie de figura que lleve el título, y dentro de la imagen es donde se lee.
    """
    import matplotlib.pyplot as plt

    from mecanico_ia_exp.visualization.style import INK_MUTED, apply_style

    apply_style()
    fig, ejes = plt.subplots(
        filas, columnas, figsize=(ancho, alto * filas), constrained_layout=True
    )
    procedencia_completa = PIE_DE_FIGURA.format(
        experimento=experimento, dataset=dataset, procedencia=procedencia
    )
    if para_la_memoria:
        print(f"{titulo}\n{procedencia_completa}")
        return fig, ejes
    fig.suptitle(titulo, fontsize=10, fontweight="bold", x=0.0, ha="left")
    fig.supxlabel(procedencia_completa, fontsize=6.5, color=INK_MUTED, x=0.0, ha="left")
    return fig, ejes


def exportar(fig: Any, nombre: str, *, subdirectorio: str = "") -> Path:
    """Guarda la figura en PNG de alta resolución **y** en SVG vectorial.

    Las dos, porque sirven a cosas distintas: el PNG se ve en el notebook y el
    SVG es el que entra en el documento final sin perder calidad. Van al
    directorio de salida del notebook, **nunca** a `artifacts/figures/`, que
    guarda las figuras publicadas y no se sobrescribe.
    """
    destino = salida(subdirectorio)
    png = destino / (nombre if nombre.endswith(".png") else f"{nombre}.png")
    svg = png.with_suffix(".svg")
    fig.savefig(png, dpi=200, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    print(f"exportada: {png.relative_to(paths.ROOT)} y {svg.name}")
    return png
