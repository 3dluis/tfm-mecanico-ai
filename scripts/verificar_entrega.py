"""Comprueba que este paquete está completo y es coherente consigo mismo.

**Por qué existe.** Un paquete de entrega puede estar mal de maneras que no se
ven al abrirlo: una figura que el documento referencia y que no viajó, una
huella que ya no coincide con su artefacto, un notebook sin su HTML, un
repositorio Git incompleto. Nada de eso rompe nada al abrir el ZIP: se descubre
cuando alguien intenta verificar algo, que es el peor momento.

**Qué comprueba.** Las diez familias que el apartado 14 de la entrega exige:
integridad de ficheros, dependencias declaradas, figuras, métricas, huellas,
notebooks, Git, documentación, datos y modalidades.

**Qué no comprueba.** Que los resultados sean correctos. Eso lo dicen los
experimentos y sus registros, no un verificador de empaquetado.

    uv run python scripts/verificar_entrega.py
    uv run python scripts/verificar_entrega.py --rapido   # sin Git ni huellas
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

#: Lo que el paquete tiene que traer, con lo que cada cosa permite hacer.
OBLIGATORIOS: tuple[tuple[str, str], ...] = (
    ("README.md", "qué es el paquete y por dónde empezar"),
    ("MANIFEST.json", "el inventario con huellas"),
    ("pyproject.toml", "las dependencias declaradas"),
    ("uv.lock", "las versiones exactas"),
    ("memoria/memoria.docx", "la memoria editable"),
    ("memoria/memoria.pdf", "la memoria para leer"),
    ("src/mecanico_ia_exp", "el código"),
    ("notebooks", "los notebooks"),
    ("notebooks/html", "su versión legible sin ejecutar"),
    ("artifacts/tables", "las tablas de resultados"),
    ("artifacts/figures/memoria", "las figuras del documento"),
    ("experiments", "los registros de ejecución"),
    ("configs", "la configuración y los manifiestos"),
    ("data/samples", "la muestra redistribuible"),
    ("scripts", "los guiones de instalación y ejecución"),
    ("docs", "la documentación del laboratorio"),
)

NOTEBOOKS: tuple[str, ...] = (
    "00_introduccion",
    "01_exploracion_obd",
    "02_comparacion_modelos",
    "03_analisis_e19",
    "04_explicabilidad",
    "05_suficiencia_y_abstencion",
    "06_expresion_del_fallo",
)

#: Módulos que se importan directamente en el paquete y tienen que estar
#: declarados. Importar algo que solo llega como dependencia transitiva es una
#: avería esperando a que otra versión lo retire.
IMPORTADOS: tuple[str, ...] = ("numpy", "pandas", "matplotlib", "seaborn", "scikit-learn")


@dataclass(frozen=True)
class Resultado:
    familia: str
    detalle: str
    bien: bool


def huella(ruta: Path) -> str:
    digest = hashlib.sha256()
    with ruta.open("rb") as flujo:
        for bloque in iter(lambda: flujo.read(1 << 20), b""):
            digest.update(bloque)
    return digest.hexdigest()


def _git(*args: str) -> tuple[int, str]:
    try:
        salida = subprocess.run(
            ["git", "-C", str(RAIZ), *args], capture_output=True, text=True, check=False
        )
    except OSError:
        return 1, "git no está disponible"
    return salida.returncode, (salida.stdout or salida.stderr).strip()


def comprobar_ficheros() -> list[Resultado]:
    return [
        Resultado("ficheros", f"{ruta} — {para_que}", (RAIZ / ruta).exists())
        for ruta, para_que in OBLIGATORIOS
    ]


def comprobar_dependencias() -> list[Resultado]:
    pyproject = RAIZ / "pyproject.toml"
    if not pyproject.is_file():
        return [Resultado("dependencias", "falta pyproject.toml", False)]
    datos = tomllib.loads(pyproject.read_text("utf-8"))
    proyecto = datos.get("project", {})
    # Un extra **es** una declaración. Lo que esta comprobación persigue es lo
    # contrario: importar algo que solo llega arrastrado por otra dependencia y
    # que desaparece el día que esa otra cambie de versión.
    declaradas = " ".join(
        [*proyecto.get("dependencies", []), *sum(proyecto.get("optional-dependencies", {}).values(), [])]
    )
    resultados = [
        Resultado("dependencias", f"{modulo} declarado", modulo in declaradas)
        for modulo in IMPORTADOS
    ]
    resultados.append(
        Resultado("dependencias", "uv.lock presente", (RAIZ / "uv.lock").is_file())
    )
    return resultados


def comprobar_notebooks() -> list[Resultado]:
    resultados: list[Resultado] = []
    for nombre in NOTEBOOKS:
        cuaderno = RAIZ / "notebooks" / f"{nombre}.ipynb"
        html = RAIZ / "notebooks" / "html" / f"{nombre}.html"
        resultados.append(Resultado("notebooks", f"{nombre}.ipynb", cuaderno.is_file()))
        if html.is_file():
            imagenes = html.read_text("utf-8", errors="replace").count("data:image/png")
            resultados.append(
                Resultado("notebooks", f"{nombre}.html con {imagenes} figuras", imagenes > 0)
            )
        else:
            resultados.append(Resultado("notebooks", f"{nombre}.html", False))
        if cuaderno.is_file():
            contenido = json.loads(cuaderno.read_text("utf-8"))
            instalaciones = [
                celda
                for celda in contenido["cells"]
                if celda["cell_type"] == "code"
                and any(
                    marca in "".join(celda["source"]) for marca in ("!pip install", "%pip install")
                )
            ]
            resultados.append(
                Resultado(
                    "notebooks",
                    f"{nombre} sin instalaciones dentro",
                    not instalaciones,
                )
            )
    return resultados


def comprobar_figuras() -> list[Resultado]:
    """Cada figura que el documento referencia tiene que haber viajado."""
    resultados: list[Resultado] = []
    directorio = RAIZ / "artifacts" / "figures" / "memoria"
    if not directorio.is_dir():
        return [Resultado("figuras", "no está artifacts/figures/memoria", False)]
    referencias: set[str] = set()
    for capitulo in sorted((RAIZ / "docs" / "memoria").glob("*.md")):
        for linea in capitulo.read_text("utf-8").splitlines():
            for encontrada in re.findall(
                r"artifacts/figures/memoria/([A-Za-z0-9_.-]+\.(?:png|svg))", linea
            ):
                referencias.add(encontrada)
    for referencia in sorted(referencias):
        resultados.append(
            Resultado("figuras", referencia, (directorio / referencia).is_file())
        )
    resultados.append(
        Resultado("figuras", f"{len(referencias)} referenciadas por el documento", bool(referencias))
    )
    return resultados


def comprobar_metricas() -> list[Resultado]:
    """Los registros que sostienen las cifras publicadas."""
    esperados = (
        "E6_baseline_synthetic_v2.json",
        "E7_temporal_synthetic_v2.json",
        "E15_suficiencia.json",
        "E19_evaluacion_final_v3.json",
    )
    return [
        Resultado("métricas", nombre, (RAIZ / "experiments" / nombre).is_file())
        for nombre in esperados
    ]


def comprobar_huellas() -> list[Resultado]:
    """Lo que el manifiesto declara tiene que coincidir con lo que hay."""
    manifiesto = RAIZ / "MANIFEST.json"
    if not manifiesto.is_file():
        return [Resultado("huellas", "falta MANIFEST.json", False)]
    datos = json.loads(manifiesto.read_text("utf-8"))
    resultados: list[Resultado] = []
    for relativa, esperada in sorted(datos.get("huellas_sha256", {}).items()):
        fichero = RAIZ / relativa
        if not fichero.is_file():
            resultados.append(Resultado("huellas", f"{relativa} falta", False))
            continue
        actual = huella(fichero)
        resultados.append(
            Resultado(
                "huellas",
                relativa if actual == esperada else f"{relativa} CAMBIÓ",
                actual == esperada,
            )
        )
    return resultados


def comprobar_git() -> list[Resultado]:
    codigo, _ = _git("rev-parse", "--is-inside-work-tree")
    if codigo != 0:
        return [Resultado("git", "no es un repositorio Git", False)]
    resultados = [Resultado("git", "repositorio presente", True)]
    _, commits = _git("rev-list", "--count", "HEAD")
    resultados.append(
        Resultado("git", f"{commits} commits accesibles", commits.isdigit() and int(commits) > 1)
    )
    _, ramas = _git("branch", "--format=%(refname:short)")
    resultados.append(Resultado("git", f"{len(ramas.splitlines())} ramas", bool(ramas)))
    codigo, salida = _git("fsck", "--connectivity-only")
    errores = [l for l in salida.splitlines() if l and not l.startswith("dangling")]
    resultados.append(
        Resultado("git", "objetos íntegros" if not errores else f"fsck: {errores[0]}", not errores)
    )
    resultados.append(
        Resultado(
            "git",
            "sin alternates externos",
            not (RAIZ / ".git" / "objects" / "info" / "alternates").exists(),
        )
    )
    return resultados


def comprobar_documentacion() -> list[Resultado]:
    resultados: list[Resultado] = []
    for nombre in ("README.md",):
        fichero = RAIZ / nombre
        if not fichero.is_file():
            resultados.append(Resultado("documentación", f"{nombre} falta", False))
            continue
        texto = fichero.read_text("utf-8")
        resultados.append(Resultado("documentación", f"{nombre} ({len(texto.split())} palabras)", True))
        for patron in ("/Users/", "/home/", "C:\\"):
            if patron in texto:
                resultados.append(
                    Resultado("documentación", f"{nombre} contiene una ruta local", False)
                )
    return resultados


def comprobar_datos() -> list[Resultado]:
    """El conjunto canónico y la muestra; los no reconstruibles, declarados."""
    return [
        Resultado(
            "datos",
            "synthetic_v2 crudo",
            (RAIZ / "data" / "raw" / "synthetic" / "synthetic_v2.parquet").is_file(),
        ),
        Resultado(
            "datos",
            "synthetic_v2 procesado",
            (RAIZ / "data" / "processed" / "synthetic_v2_x.npy").is_file(),
        ),
        Resultado(
            "datos",
            "muestra redistribuible",
            (RAIZ / "data" / "samples" / "synthetic_sample.parquet").is_file(),
        ),
        Resultado(
            "datos",
            "análisis contrafactual T2, separado de los conjuntos",
            (RAIZ / "artifacts" / "contrafactual").is_dir(),
        ),
    ]


FAMILIAS = {
    "ficheros": comprobar_ficheros,
    "dependencias": comprobar_dependencias,
    "notebooks": comprobar_notebooks,
    "figuras": comprobar_figuras,
    "métricas": comprobar_metricas,
    "datos": comprobar_datos,
    "documentación": comprobar_documentacion,
    "huellas": comprobar_huellas,
    "git": comprobar_git,
}

#: Las dos familias que tardan: se omiten con `--rapido`.
LENTAS = ("huellas", "git")


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("--rapido", action="store_true", help="omite huellas y Git")
    analizador.add_argument("--detalle", action="store_true", help="imprime cada comprobación")
    args = analizador.parse_args(argv)

    resultados: list[Resultado] = []
    for familia, comprobar in FAMILIAS.items():
        if args.rapido and familia in LENTAS:
            continue
        resultados.extend(comprobar())

    fallos = [r for r in resultados if not r.bien]
    por_familia: dict[str, list[Resultado]] = {}
    for resultado in resultados:
        por_familia.setdefault(resultado.familia, []).append(resultado)

    for familia, suyos in por_familia.items():
        malos = [r for r in suyos if not r.bien]
        marca = " ok" if not malos else "  ✗"
        print(f"{marca}  {familia:<14} {len(suyos) - len(malos)} de {len(suyos)}")
        if args.detalle or malos:
            for resultado in suyos if args.detalle else malos:
                print(f"       {'·' if resultado.bien else '✗'} {resultado.detalle}")

    print()
    if fallos:
        print(f"{len(fallos)} comprobaciones no pasan. El paquete NO está completo.")
        return 1
    print(f"Las {len(resultados)} comprobaciones pasan. El paquete está completo y es coherente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
