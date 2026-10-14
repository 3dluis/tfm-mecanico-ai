"""Inspecciona un DOCX y dice qué conserva de lo que la entrega exige.

**Por qué existe.** Una conversión automática de Markdown a DOCX conserva el
texto y pierde, calladamente, casi todo lo demás: los estilos de la plantilla, el
índice automático, el índice de figuras, los pies, las referencias cruzadas y los
márgenes. Que el fichero se abra no significa que esté bien, y leerlo por encima
tampoco lo dice. Esto lo abre, lo descomprime y lo cuenta.

**Qué no hace.** No genera el DOCX ni lo corrige. Informa, y devuelve 1 si falta
algo que la entrega exige, para que sirva de puerta en una comprobación.

    uv run python scripts/verificar_docx.py memoria.docx
    uv run python scripts/verificar_docx.py memoria.docx --plantilla "ruta/plantilla.docx"
"""

from __future__ import annotations

import argparse
import html
import re
import struct
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

#: Estilos propios de la plantilla de la titulación. Si el documento no usa
#: ninguno, la conversión ha escrito con los estilos de Word y el formato
#: institucional se ha perdido aunque el texto se vea parecido.
ESTILOS_DE_LA_PLANTILLA = (
    "Ttulo1",
    "TtuloApartado",
    "Ttulosubapartado",
    "VietaTFM",
    "VietaNumeradaTFM",
    "BibliografaAPA",
    "CitaLiteralAPA",
)

#: Lo que la entrega exige y esta comprobación sabe medir.
EXIGIDO = (
    "estilos de la plantilla",
    "índice automático",
    "índice de figuras",
    "índice de tablas",
    "pies de figura",
    "imágenes incrustadas",
    "resolución de impresión",
)


@dataclass(frozen=True)
class Hallazgo:
    concepto: str
    valor: str
    cumple: bool | None  # None = informativo, no exigido


def _xml(fichero: zipfile.ZipFile, nombre: str) -> str:
    try:
        return fichero.read(nombre).decode("utf-8", "replace")
    except KeyError:
        return ""


def _dpi_png(datos: bytes) -> int:
    posicion = datos.find(b"pHYs")
    if posicion < 0:
        return 0
    x, _, unidad = struct.unpack(">IIB", datos[posicion + 4 : posicion + 13])
    return round(x * 0.0254) if unidad == 1 else 0


def inspeccionar(
    ruta: Path,
    estilos_exigidos: tuple[str, ...],
    imagenes_de_la_plantilla: frozenset[bytes] = frozenset(),
) -> list[Hallazgo]:
    hallazgos: list[Hallazgo] = []
    with zipfile.ZipFile(ruta) as fichero:
        documento = _xml(fichero, "word/document.xml")
        estilos = _xml(fichero, "word/styles.xml")

        usados = set(re.findall(r'<w:pStyle w:val="([^"]+)"', documento))
        propios = sorted(usados & set(estilos_exigidos))
        hallazgos.append(
            Hallazgo(
                "estilos de la plantilla",
                f"{len(propios)} de {len(estilos_exigidos)} en uso: "
                f"{', '.join(propios) or 'ninguno'}",
                bool(propios),
            )
        )
        declarados = set(re.findall(r'<w:style [^>]*w:styleId="([^"]+)"', estilos))
        faltan = sorted(set(estilos_exigidos) - declarados)
        hallazgos.append(
            Hallazgo(
                "estilos declarados en el fichero",
                "todos" if not faltan else f"faltan {', '.join(faltan)}",
                not faltan,
            )
        )

        campos = re.findall(r"<w:instrText[^>]*>(.*?)</w:instrText>", documento, re.S)
        texto_campos = " ".join(campos)
        hallazgos.append(
            Hallazgo(
                "índice automático",
                "campo TOC presente" if "TOC" in texto_campos else "no hay ningún campo TOC",
                "TOC" in texto_campos,
            )
        )

        # Un índice de ilustraciones puede construirse por rótulo (\\c) o por
        # estilo de párrafo (\\t): las dos formas son campos nativos de Word. El
        # texto del campo viene escapado en el XML, de modo que se desescapa
        # antes de buscar: «\\t "PieDeFigura;1"» llega como «&quot;».
        campos_legibles = html.unescape(texto_campos)

        def _hay_indice(*claves: str) -> bool:
            """Un campo TOC construido por rótulo (\\c) o por estilo (\\t)."""
            return any(
                f'\\c "{clave}' in campos_legibles or f'\\t "{clave}' in campos_legibles
                for clave in claves
            )

        indice_figuras = _hay_indice("Figura", "PieDeFigura") or (
            'w:val="Tabladeilustraciones"' in documento
        )
        hallazgos.append(
            Hallazgo(
                "índice de figuras",
                "presente" if indice_figuras else "no se encuentra",
                indice_figuras,
            )
        )
        indice_tablas = _hay_indice("Tabla", "PieDeTabla")
        hallazgos.append(
            Hallazgo(
                "índice de tablas",
                "presente" if indice_tablas else "no se encuentra",
                indice_tablas,
            )
        )
        referencias = texto_campos.count("REF ")
        hallazgos.append(
            Hallazgo(
                "referencias cruzadas",
                f"{referencias} campos REF",
                None,
            )
        )

        parrafos = re.findall(r"<w:p[ >].*?</w:p>", documento, re.S)
        textos = ["".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S)).strip() for p in parrafos]
        pies = [t for t in textos if re.match(r"^Figura (?:[A-Z]|\d+)\.\d+\.", t)]
        hallazgos.append(
            Hallazgo("pies de figura", f"{len(pies)} con la forma «Figura N.M.»", bool(pies))
        )
        fuentes = [t for t in textos if t.startswith("Fuente:")]
        hallazgos.append(
            Hallazgo("líneas de procedencia", f"{len(fuentes)} que empiezan por «Fuente:»", None)
        )

        medios = [n for n in fichero.namelist() if n.startswith("word/media/")]
        # Las imágenes de la plantilla —logotipos de la portada y de los
        # encabezados— traen la resolución de la plantilla y no son figuras del
        # trabajo. Solo se mide la resolución de lo que el cuerpo referencia.
        relaciones = _xml(fichero, "word/_rels/document.xml.rels")
        usados = set(re.findall(r'r:(?:id|embed)="(rId\d+)"', documento))
        del_cuerpo = {
            f"word/{destino}"
            for identificador, destino in re.findall(
                r'Id="(rId\d+)"[^>]*Target="(media/[^"]+)"', relaciones
            )
            if identificador in usados
        }
        hallazgos.append(
            Hallazgo(
                "imágenes incrustadas",
                f"{len(medios)} en el fichero, {len(del_cuerpo)} referenciadas desde el cuerpo",
                bool(del_cuerpo),
            )
        )
        bajas = []
        de_la_plantilla = 0
        for nombre in sorted(del_cuerpo):
            if not nombre.lower().endswith(".png") or nombre not in medios:
                continue
            datos = fichero.read(nombre)
            # Un logotipo de la portada no es una figura del trabajo: si el
            # fichero es byte a byte el de la plantilla, su resolución es la que
            # la titulación entrega y no algo que este documento pueda corregir.
            if datos in imagenes_de_la_plantilla:
                de_la_plantilla += 1
                continue
            puntos = _dpi_png(datos)
            if puntos and puntos < 200:
                bajas.append(f"{Path(nombre).name} a {puntos} ppp")
        if de_la_plantilla:
            hallazgos.append(
                Hallazgo(
                    "imágenes de la plantilla",
                    f"{de_la_plantilla} sin medir: vienen de la plantilla sin modificar",
                    None,
                )
            )
        hallazgos.append(
            Hallazgo(
                "resolución de impresión",
                "todas a 200 ppp o más" if not bajas else "; ".join(bajas),
                not bajas,
            )
        )

        tablas = documento.count("<w:tbl>")
        hallazgos.append(Hallazgo("tablas", f"{tablas}", None))

        margenes = re.search(r"<w:pgMar ([^/>]+)/>", documento)
        hallazgos.append(
            Hallazgo(
                "márgenes de sección",
                margenes.group(1).strip() if margenes else "no declarados",
                bool(margenes),
            )
        )
        palabras = sum(len(t.split()) for t in textos)
        hallazgos.append(Hallazgo("palabras", f"{palabras}", None))
    return hallazgos


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("docx", type=Path)
    analizador.add_argument(
        "--plantilla",
        type=Path,
        default=None,
        help="plantilla oficial de la que tomar la lista de estilos exigidos",
    )
    args = analizador.parse_args(argv)

    if not args.docx.is_file():
        print(f"no existe: {args.docx}", file=sys.stderr)
        return 2

    exigidos = ESTILOS_DE_LA_PLANTILLA
    imagenes_de_la_plantilla: frozenset[bytes] = frozenset()
    if args.plantilla is not None and args.plantilla.is_file():
        with zipfile.ZipFile(args.plantilla) as plantilla:
            estilos = _xml(plantilla, "word/styles.xml")
            imagenes_de_la_plantilla = frozenset(
                plantilla.read(nombre)
                for nombre in plantilla.namelist()
                if nombre.startswith("word/media/")
            )
        personalizados = re.findall(
            r'<w:style [^>]*w:styleId="([^"]+)"[^>]*>(?:(?!</w:style>).)*?<w:qFormat/>',
            estilos,
            re.S,
        )
        if personalizados:
            exigidos = tuple(sorted(set(personalizados) - {"Normal"}))
        print(f"estilos tomados de la plantilla: {', '.join(exigidos)}\n")

    hallazgos = inspeccionar(args.docx, exigidos, imagenes_de_la_plantilla)
    ancho = max(len(h.concepto) for h in hallazgos)
    fallos = 0
    for hallazgo in hallazgos:
        if hallazgo.cumple is None:
            marca = "  ·"
        elif hallazgo.cumple:
            marca = " ok"
        else:
            marca = "  ✗"
            if hallazgo.concepto in EXIGIDO:
                fallos += 1
        print(f"{marca}  {hallazgo.concepto:<{ancho}}  {hallazgo.valor}")

    print()
    if fallos:
        print(f"{fallos} de lo exigido no está en el documento.")
    else:
        print("El documento conserva todo lo que esta comprobación sabe medir.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
