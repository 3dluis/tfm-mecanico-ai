"""Monta el documento entregable sobre la plantilla oficial de la titulación.

**Por qué no basta con Pandoc.** Pandoc convierte el Markdown y, con
``--reference-doc``, hereda de la plantilla los estilos, la configuración de
página, los encabezados y los pies. Comprobado sobre la plantilla real, eso deja
fuera cuatro cosas que la entrega necesita:

1. **la portada institucional**, que Pandoc no copia porque de un documento de
   referencia solo toma el formato, nunca el contenido;
2. **los estilos propios de la titulación**: Pandoc escribe los apartados con el
   estilo estándar de Word y no con «Título Apartado», que es el que la plantilla
   define, y el cuerpo con sus propios estilos en lugar de «Normal»;
3. **los índices**, que son campos de Word y hay que insertarlos;
4. **la primera sección**, con su encabezado y su pie distintos del resto.

Este guion hace las cuatro. Trabaja **siempre sobre una copia**: la plantilla
original no se abre en escritura en ningún momento.

**Qué produce.** ``entregables/memoria.docx``. El PDF se genera desde Word, por
la razón que explica ``docs/entrega-docx.md``: cualquier otra vía vuelve a tocar
la paginación y el documento revisado deja de corresponderse con el entregado.

    uv run python scripts/montar_docx.py
    uv run python scripts/montar_docx.py --salida entregables/borrador.docx
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from mecanico_ia_exp.config import paths

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

#: Orden de montaje. Es el de la plantilla: resumen, capítulos, bibliografía y
#: anexos. Cambiarlo aquí cambia el documento, y no hay otro sitio donde mirarlo.
CAPITULOS: tuple[str, ...] = (
    "00_resumen.md",
    "cap1_introduccion.md",
    "cap2_objetivos.md",
    "cap3_marco_teorico.md",
    "cap4_marco_metodologico.md",
    "cap5_resultados.md",
    "cap6_conclusiones.md",
    "bibliografia.md",
    "anexos.md",
)

#: De qué estilo de Pandoc a qué estilo de la plantilla. Lo que no esté aquí se
#: queda como Pandoc lo dejó, y el informe de conformidad lo dirá.
EQUIVALENCIAS: dict[str, str] = {
    "Ttulo2": "TtuloApartado",
    "Heading2": "TtuloApartado",
    "Heading3": "Ttulosubapartado",
    "Heading4": "Ttulosubapartado",
    "BodyText": "Normal",
    "FirstParagraph": "Normal",
    "BlockText": "CitaLiteralAPA",
}

#: Estilos que este guion añade a la copia, porque la plantilla no los trae y los
#: índices de figuras y de tablas se construyen a partir de ellos.
ESTILOS_NUEVOS: dict[str, str] = {
    "PieDeFigura": "Pie de figura",
    "PieDeTabla": "Pie de tabla",
}

PLANTILLA_POR_DEFECTO = Path("../24-25 Plantilla TFM MUIA.docx")


def _pandoc() -> str:
    ruta = shutil.which("pandoc")
    if ruta is None:
        msg = "pandoc no está instalado. Ver docs/entrega-docx.md"
        raise RuntimeError(msg)
    return ruta


def version_de_pandoc() -> str:
    salida = subprocess.run(
        [_pandoc(), "--version"], capture_output=True, text=True, check=True
    ).stdout
    return salida.splitlines()[0].strip()


def convertir(plantilla: Path, destino: Path) -> Path:
    """Concatena los capítulos y los convierte con Pandoc."""
    memoria = paths.DOCS / "memoria"
    with tempfile.TemporaryDirectory() as temporal:
        combinado = Path(temporal) / "completo.md"
        combinado.write_text(
            "\n\n".join((memoria / nombre).read_text("utf-8") for nombre in CAPITULOS),
            encoding="utf-8",
        )
        subprocess.run(
            [
                _pandoc(),
                str(combinado),
                "-o",
                str(destino),
                f"--reference-doc={plantilla}",
                f"--resource-path={memoria}",
            ],
            check=True,
        )
    return destino


def _portada(xml_plantilla: str) -> str:
    """La primera sección de la plantilla, con su portada y su salto.

    Se corta en el párrafo que **contiene** el primer ``sectPr``: en OOXML el
    salto de sección vive dentro del último párrafo de la sección, de modo que
    cortar antes dejaría la portada sin su configuración de página.
    """
    cuerpo = xml_plantilla[xml_plantilla.index("<w:body>") + len("<w:body>") :]
    corte = cuerpo.index("<w:sectPr")
    fin = cuerpo.index("</w:p>", corte) + len("</w:p>")
    return cuerpo[:fin]


def _campo(instruccion: str, texto_provisional: str) -> str:
    """Un campo nativo de Word, de los que se actualizan con F9."""
    return (
        '<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
        f'<w:r><w:instrText xml:space="preserve"> {instruccion} </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        f"<w:r><w:t>{texto_provisional}</w:t></w:r>"
        '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>'
    )


def _indices() -> str:
    """Índice general, de figuras y de tablas, los tres como campos de Word.

    El de figuras y el de tablas se construyen **por estilo** y no por campos
    `SEQ`: la numeración de las figuras es literal en el texto fuente, donde una
    prueba comprueba que sea correlativa. La alternativa —numerar con `SEQ` y
    referenciar con `REF`— daría numeración automática a cambio de que el texto
    fuente dejara de ser legible por sí mismo, y de que cualquier campo sin
    actualizar mostrara un error en lugar de un número.
    """
    partes = [
        f'<w:p><w:pPr><w:pStyle w:val="TtuloTDC"/></w:pPr><w:r><w:t>{titulo}</w:t></w:r></w:p>'
        + _campo(instruccion, provisional)
        + '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
        for titulo, instruccion, provisional in (
            ("ÍNDICE", 'TOC \\o "1-3" \\h \\z \\u', "Actualice el índice desde Word (F9)."),
            (
                "ÍNDICE DE FIGURAS",
                'TOC \\h \\z \\t "PieDeFigura;1"',
                "Actualice el índice de figuras desde Word (F9).",
            ),
            (
                "ÍNDICE DE TABLAS",
                'TOC \\h \\z \\t "PieDeTabla;1"',
                "Actualice el índice de tablas desde Word (F9).",
            ),
        )
    ]
    return "".join(partes)


def _estilo_de_parrafo(parrafo: str) -> str | None:
    encontrado = re.search(r'<w:pStyle w:val="([^"]+)"', parrafo)
    return encontrado.group(1) if encontrado else None


def _texto_de_parrafo(parrafo: str) -> str:
    return "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", parrafo, re.S))


def _reescribir_estilo(parrafo: str, estilo: str) -> str:
    if '<w:pStyle w:val="' in parrafo:
        return re.sub(r'<w:pStyle w:val="[^"]+"', f'<w:pStyle w:val="{estilo}"', parrafo, count=1)
    if "<w:pPr>" in parrafo:
        return parrafo.replace("<w:pPr>", f'<w:pPr><w:pStyle w:val="{estilo}"/>', 1)
    return parrafo.replace("<w:p>", f'<w:p><w:pPr><w:pStyle w:val="{estilo}"/></w:pPr>', 1)


def adaptar_estilos(cuerpo: str) -> tuple[str, dict[str, int]]:
    """Traduce los estilos de Pandoc a los de la plantilla, párrafo a párrafo.

    Un párrafo con `Compact` dentro de una celda de tabla NO es un elemento de
    lista: Pandoc usa ese estilo para las dos cosas. Se distinguen por si el
    párrafo lleva numeración.
    """
    cuenta: dict[str, int] = {}
    salida: list[str] = []
    posicion = 0
    for encontrado in re.finditer(r"<w:p(?: [^>]*)?>.*?</w:p>|<w:p(?: [^>]*)?/>", cuerpo, re.S):
        salida.append(cuerpo[posicion : encontrado.start()])
        parrafo = encontrado.group(0)
        posicion = encontrado.end()
        estilo = _estilo_de_parrafo(parrafo)
        destino: str | None = None
        if estilo == "Compact":
            destino = "VietaNumeradaTFM" if "<w:numPr>" in parrafo else "Normal"
        elif estilo in EQUIVALENCIAS:
            destino = EQUIVALENCIAS[estilo]
        elif estilo in {"ImageCaption", "CaptionedFigure"}:
            destino = None  # se resuelve abajo, según lo que diga el párrafo
        texto = _texto_de_parrafo(parrafo)
        if re.match(r"^\s*Figura [A-Z0-9]+\.\d+\.", texto):
            destino = "PieDeFigura"
        elif re.match(r"^\s*Tabla \d+\.\d+\.", texto):
            destino = "PieDeTabla"
        if destino is not None and destino != estilo:
            parrafo = _reescribir_estilo(parrafo, destino)
            clave = f"{estilo or 'sin estilo'} → {destino}"
            cuenta[clave] = cuenta.get(clave, 0) + 1
        salida.append(parrafo)
    salida.append(cuerpo[posicion:])
    return "".join(salida), cuenta


def anadir_estilos(xml_estilos: str) -> str:
    """Añade a la COPIA los dos estilos de pie, basados en el Normal de la plantilla."""
    nuevos = []
    for identificador, nombre in ESTILOS_NUEVOS.items():
        if f'w:styleId="{identificador}"' in xml_estilos:
            continue
        nuevos.append(
            f'<w:style w:type="paragraph" w:customStyle="1" w:styleId="{identificador}">'
            f'<w:name w:val="{nombre}"/><w:basedOn w:val="Normal"/><w:qFormat/>'
            '<w:pPr><w:keepNext w:val="0"/><w:spacing w:before="60" w:after="240"/></w:pPr>'
            '<w:rPr><w:i/><w:sz w:val="18"/></w:rPr></w:style>'
        )
    return xml_estilos.replace("</w:styles>", "".join(nuevos) + "</w:styles>")


def montar(plantilla: Path, salida: Path) -> dict[str, object]:
    salida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporal:
        intermedio = Path(temporal) / "cuerpo.docx"
        convertir(plantilla, intermedio)

        with zipfile.ZipFile(plantilla) as fuente:
            xml_plantilla = fuente.read("word/document.xml").decode("utf-8")
        portada = _portada(xml_plantilla)

        with zipfile.ZipFile(intermedio) as convertido:
            partes = {nombre: convertido.read(nombre) for nombre in convertido.namelist()}

        documento = partes["word/document.xml"].decode("utf-8")
        inicio = documento.index("<w:body>") + len("<w:body>")
        cuerpo = documento[inicio : documento.rindex("</w:body>")]
        cuerpo, cambios = adaptar_estilos(cuerpo)
        partes["word/document.xml"] = (
            documento[:inicio]
            + portada
            + _indices()
            + cuerpo
            + documento[documento.rindex("</w:body>") :]
        ).encode("utf-8")
        partes["word/styles.xml"] = anadir_estilos(
            partes["word/styles.xml"].decode("utf-8")
        ).encode("utf-8")

        with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as destino:
            for nombre, contenido in partes.items():
                destino.writestr(nombre, contenido)

    return {"salida": salida, "cambios_de_estilo": cambios, "pandoc": version_de_pandoc()}


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument(
        "--plantilla",
        type=Path,
        default=paths.ROOT / PLANTILLA_POR_DEFECTO,
        help="plantilla oficial; NO se modifica, solo se lee",
    )
    analizador.add_argument(
        "--salida", type=Path, default=paths.ROOT / "entregables" / "memoria.docx"
    )
    args = analizador.parse_args(argv)

    plantilla = args.plantilla.resolve()
    if not plantilla.is_file():
        print(f"no encuentro la plantilla: {plantilla}", file=sys.stderr)
        return 2

    informe = montar(plantilla, args.salida)
    print(f"convertido con {informe['pandoc']}")
    print(f"plantilla leída: {plantilla.name}")
    print("\nestilos traducidos a los de la plantilla:")
    cambios = informe["cambios_de_estilo"]
    assert isinstance(cambios, dict)
    for clave, veces in sorted(cambios.items(), key=lambda par: -par[1]):
        print(f"  {veces:5d}  {clave}")
    salida = informe["salida"]
    assert isinstance(salida, Path)
    print(f"\n{salida.relative_to(paths.ROOT)}  ({salida.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
