"""Ejecuta los notebooks de la entrega y los exporta a HTML.

**Para qué.** El tribunal tiene que poder **leer** los notebooks sin instalar
nada ni ejecutar una celda. El `.ipynb` versionado va sin salidas a propósito
—guardar las de la máquina del autor las haría pasar por las del lector—, así
que el HTML se genera aquí, ejecutando desde un kernel limpio, y queda como
copia legible con sus figuras y sus tablas dentro.

**Qué no es.** No sustituye a la ejecución. El HTML enseña **una** ejecución, la
de quien lo generó, con su commit impreso en la primera celda. Quien quiera
verificar, ejecuta.

**Dónde escribe.** En `docs/notebooks/html/`. Ni en `experiments/`, ni en
`tables/`, ni en `figures/`: los notebooks no pueden tocar los artefactos
históricos, y su exportación tampoco.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
NOTEBOOKS = RAIZ / "notebooks"
DESTINO = RAIZ / "docs" / "notebooks" / "html"

ENTREGADOS = (
    "00_introduccion.ipynb",
    "01_exploracion_obd.ipynb",
    "02_comparacion_modelos.ipynb",
    "03_analisis_e19.ipynb",
    "04_explicabilidad.ipynb",
    "05_suficiencia_y_abstencion.ipynb",
)


def exportar(nombre: str) -> Path:
    """Ejecuta un notebook con kernel propio y escribe su HTML."""
    import nbformat
    from nbclient import NotebookClient
    from nbconvert import HTMLExporter

    cuaderno = nbformat.read(NOTEBOOKS / nombre, as_version=4)
    NotebookClient(
        cuaderno,
        timeout=900,
        kernel_name="python3",
        resources={"metadata": {"path": str(NOTEBOOKS)}},
    ).execute()

    exportador = HTMLExporter()
    # `lab` incrusta los estilos en el fichero: el HTML tiene que abrirse sin
    # red y sin ficheros al lado, porque va a viajar suelto.
    exportador.template_name = "lab"
    cuerpo, _ = exportador.from_notebook_node(cuaderno)

    DESTINO.mkdir(parents=True, exist_ok=True)
    salida = DESTINO / f"{Path(nombre).stem}.html"
    salida.write_text(cuerpo, "utf-8")
    print(f"{nombre:34s} → {salida.relative_to(RAIZ)}  ({len(cuerpo) / 1024:.0f} KB)")
    return salida


def main(nombres: tuple[str, ...] = ENTREGADOS) -> int:
    for nombre in nombres:
        if not (NOTEBOOKS / nombre).is_file():
            print(f"falta {nombre}", file=sys.stderr)
            return 1
        exportar(nombre)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(tuple(sys.argv[1:]) or ENTREGADOS))
