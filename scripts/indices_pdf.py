"""Rellena el resultado en caché de los tres índices, medido sobre el PDF.

**El problema.** Los tres índices del documento son **campos nativos**: están
vacíos hasta que una aplicación los evalúa. Word los rellena al abrir el fichero;
la conversión desatendida de LibreOffice **no**, de modo que el PDF de revisión
salía con «Actualice el índice desde Word (F9)» donde debería llevar sus
entradas. Para quien recibe el PDF, eso es un documento sin índices.

**La solución, y por qué no es texto estático.** Un campo de Word guarda su
**resultado en caché** entre las marcas `separate` y `end`: es lo que la
aplicación muestra mientras no se actualice, y es lo que Word escribe cuando se
pulsa `F9`. Aquí se escribe ese mismo resultado. El campo sigue siendo un campo,
el DOCX sigue siendo editable y actualizable, y el PDF muestra las entradas.

**De dónde salen las entradas y las páginas.** De la estructura real del
documento —los párrafos con estilo de encabezado y los pies de figura y de
tabla— y de **la página en que el PDF los imprime**, medida sobre el PDF. No se
inventa ninguna numeración.

**Por qué itera.** Rellenar un índice lo hace crecer, y al crecer desplaza las
páginas de todo lo que viene detrás. La primera medición queda obsoleta por su
propio efecto. Se repite hasta que dos pasadas seguidas dan las mismas páginas,
que es el punto fijo, y al final se **verifica** que cada entrada está en la
página que declara.

    uv run python scripts/indices_pdf.py entregables/memoria.docx
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from mecanico_ia_exp.config import paths

#: Estilos de encabezado de la plantilla y su nivel en el índice general.
NIVELES: dict[str, int] = {"Ttulo1": 1, "TtuloApartado": 2, "Ttulosubapartado": 3}

#: Qué índice recoge cada estilo de pie.
PIES: dict[str, str] = {"PieDeFigura": "figuras", "PieDeTabla": "tablas"}

#: El texto provisional de cada campo, que es lo que se sustituye.
PROVISIONALES: dict[str, str] = {
    "general": "Actualice el índice desde Word (F9).",
    "figuras": "Actualice el índice de figuras desde Word (F9).",
    "tablas": "Actualice el índice de tablas desde Word (F9).",
}

#: Posición del tabulador de la derecha, en vigésimas de punto: el ancho útil de
#: la página con los márgenes del cuerpo de la plantilla.
TABULADOR = 8505

MAXIMO_DE_PASADAS = 6


@dataclass(frozen=True)
class Entrada:
    indice: str
    texto: str
    nivel: int
    pagina: int = 0


def _xml(ruta: Path, nombre: str) -> str:
    with zipfile.ZipFile(ruta) as fichero:
        return fichero.read(nombre).decode("utf-8")


def _texto_de_parrafo(parrafo: str) -> str:
    bruto = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", parrafo, re.S))
    return re.sub(r"\s+", " ", bruto).replace("&amp;", "&").strip()


def estructura(documento: str) -> list[Entrada]:
    """Encabezados y pies, en el orden en que aparecen en el documento."""
    entradas: list[Entrada] = []
    for parrafo in re.findall(r"<w:p\b.*?</w:p>", documento, re.S):
        estilo = re.search(r'<w:pStyle w:val="([^"]+)"', parrafo)
        if estilo is None:
            continue
        nombre = estilo.group(1)
        texto = _texto_de_parrafo(parrafo)
        if not texto:
            continue
        if nombre in NIVELES:
            entradas.append(Entrada("general", texto, NIVELES[nombre]))
        elif nombre in PIES:
            entradas.append(Entrada(PIES[nombre], texto, 1))
    return entradas


def paginas_del_pdf(ruta: Path) -> list[str]:
    """El texto de cada página, normalizado para poder buscar en él."""
    salida = subprocess.run(
        ["pdftotext", "-layout", str(ruta), "-"], capture_output=True, text=True, check=True
    ).stdout
    return [re.sub(r"\s+", " ", p) for p in salida.split("\f")]


def _buscar(texto: str, paginas: list[str], desde: int) -> int:
    """La primera página, a partir de `desde`, en que aparece ese texto.

    Se busca hacia delante desde la última entrada encontrada porque el
    documento es lineal: un encabezado no puede estar antes que el anterior. Eso
    evita que una mención del mismo texto en el índice se confunda con el sitio
    donde de verdad empieza el apartado.
    """
    aguja = re.sub(r"\s+", " ", texto)[:70]
    for numero in range(max(desde, 1), len(paginas) + 1):
        if aguja and aguja in paginas[numero - 1]:
            return numero
    return 0


def primera_pagina_del_cuerpo(paginas: list[str]) -> int:
    """Dónde acaban los índices y empieza el documento.

    Sin esto, la primera entrada se encuentra **dentro del propio índice** —ahí
    está su texto— y todas las demás, que se buscan hacia delante, se quedan
    pegadas a esa misma página. El síntoma es inconfundible: un índice en que
    todo remite a la página 3.
    """
    ultima = 0
    for numero, pagina in enumerate(paginas, 1):
        if "ÍNDICE DE TABLAS" in pagina or "ÍNDICE DE FIGURAS" in pagina or "ÍNDICE" in pagina:
            ultima = numero
    return ultima + 1


def medir(entradas: list[Entrada], paginas: list[str]) -> list[Entrada]:
    inicio = primera_pagina_del_cuerpo(paginas)
    medidas: list[Entrada] = []
    ultima = {"general": inicio, "figuras": inicio, "tablas": inicio}
    for entrada in entradas:
        pagina = _buscar(entrada.texto, paginas, ultima[entrada.indice])
        if pagina:
            ultima[entrada.indice] = pagina
        medidas.append(
            Entrada(entrada.indice, entrada.texto, entrada.nivel, pagina or ultima[entrada.indice])
        )
    return medidas


def _escapar(texto: str) -> str:
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _parrafo_de_entrada(entrada: Entrada) -> str:
    """Una línea del índice: texto, puntos conductores y número de página."""
    estilo = f"TDC{min(entrada.nivel, 4)}" if entrada.indice == "general" else "TDC1"
    return (
        f'<w:p><w:pPr><w:pStyle w:val="{estilo}"/>'
        f'<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="{TABULADOR}"/></w:tabs></w:pPr>'
        f'<w:r><w:t xml:space="preserve">{_escapar(entrada.texto)}</w:t></w:r>'
        f"<w:r><w:tab/></w:r>"
        f"<w:r><w:t>{entrada.pagina}</w:t></w:r></w:p>"
    )


def rellenar(documento: str, entradas: list[Entrada]) -> tuple[str, int]:
    """Sustituye el resultado en caché de cada campo por sus entradas."""
    rellenados = 0
    for indice, provisional in PROVISIONALES.items():
        propias = [e for e in entradas if e.indice == indice]
        if not propias:
            continue
        # El párrafo del campo se reemplaza entero por el encabezado del campo,
        # las entradas y su cierre: así el campo sigue siendo un campo.
        patron = re.compile(
            r"<w:p>(?:(?!</w:p>).)*?" + re.escape(provisional) + r"(?:(?!</w:p>).)*?</w:p>", re.S
        )
        instruccion = _INSTRUCCIONES[indice]
        reemplazo = (
            '<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> ' + instruccion + " </w:instrText></w:r>"
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r></w:p>'
            + "".join(_parrafo_de_entrada(e) for e in propias)
            + '<w:p><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>'
        )
        documento, n = patron.subn(reemplazo.replace("\\", "\\\\"), documento, count=1)
        rellenados += n
    return documento, rellenados


#: Las instrucciones de campo, que se conservan para que `F9` siga funcionando.
_INSTRUCCIONES: dict[str, str] = {
    "general": 'TOC \\o "1-3" \\h \\z \\u',
    "figuras": 'TOC \\h \\z \\t "PieDeFigura;1"',
    "tablas": 'TOC \\h \\z \\t "PieDeTabla;1"',
}


def _reescribir(origen: Path, destino: Path, documento: str) -> None:
    with (
        zipfile.ZipFile(origen) as entrada,
        zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as salida,
    ):
        for elemento in entrada.infolist():
            datos = entrada.read(elemento.filename)
            if elemento.filename == "word/document.xml":
                datos = documento.encode("utf-8")
            salida.writestr(elemento, datos)


def _a_pdf(docx: Path, directorio: Path) -> Path:
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(directorio), str(docx)],
        capture_output=True,
        check=True,
    )
    return directorio / f"{docx.stem}.pdf"


def verificar(entradas: list[Entrada], paginas: list[str]) -> list[str]:
    """Cada entrada tiene que estar en la página que dice. Sin excepciones."""
    fallos: list[str] = []
    for entrada in entradas:
        if not 1 <= entrada.pagina <= len(paginas):
            fallos.append(f"{entrada.texto[:50]} → página {entrada.pagina} fuera del documento")
            continue
        aguja = re.sub(r"\s+", " ", entrada.texto)[:70]
        if aguja and aguja not in paginas[entrada.pagina - 1]:
            fallos.append(f"{entrada.texto[:50]} → dice página {entrada.pagina} y no está ahí")
    return fallos


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("docx", type=Path)
    analizador.add_argument("--pdf", type=Path, default=None)
    args = analizador.parse_args(argv)

    if not args.docx.is_file():
        print(f"no existe: {args.docx}", file=sys.stderr)
        return 2
    if shutil.which("pdftotext") is None or shutil.which("soffice") is None:
        print("hacen falta `pdftotext` y `soffice`. Ver docs/entrega-docx.md", file=sys.stderr)
        return 2

    original = _xml(args.docx, "word/document.xml")
    entradas = estructura(original)
    print(f"estructura del documento: {len(entradas)} entradas")
    for indice in ("general", "figuras", "tablas"):
        print(f"  {indice:8s} {sum(1 for e in entradas if e.indice == indice):3d}")

    with tempfile.TemporaryDirectory() as temporal:
        trabajo = Path(temporal)
        candidato = args.docx
        anteriores: list[int] = []
        for pasada in range(1, MAXIMO_DE_PASADAS + 1):
            pdf = _a_pdf(candidato, trabajo)
            paginas = paginas_del_pdf(pdf)
            medidas = medir(entradas, paginas)
            numeros = [e.pagina for e in medidas]
            print(f"  pasada {pasada}: {len(paginas)} páginas", end="")
            if numeros == anteriores:
                print(" · las páginas no se mueven: punto fijo")
                break
            print(" · se repite, las páginas cambiaron")
            anteriores = numeros
            documento, rellenados = rellenar(original, medidas)
            if rellenados != 3:
                print(f"\nsolo se rellenaron {rellenados} de 3 índices", file=sys.stderr)
                return 1
            candidato = trabajo / "con_indices.docx"
            _reescribir(args.docx, candidato, documento)
        else:
            print("\nlas páginas no se estabilizan", file=sys.stderr)
            return 1

        destino_pdf = args.pdf or args.docx.with_suffix(".pdf")
        pdf_final = _a_pdf(candidato, trabajo)
        paginas = paginas_del_pdf(pdf_final)
        fallos = verificar(medir(entradas, paginas), paginas)
        if fallos:
            print(f"\n{len(fallos)} entradas no están donde dicen:", file=sys.stderr)
            for fallo in fallos[:10]:
                print(f"  {fallo}", file=sys.stderr)
            return 1
        shutil.copy2(pdf_final, destino_pdf)
        # El DOCX se queda con el mismo resultado en caché. Sigue siendo un campo
        # —`F9` lo recalcula— y así el índice se ve también en Word, en Pages o
        # en cualquier visor que no evalúe campos. Las páginas guardadas son las
        # de esta composición; Word, que puede paginar distinto, las recalcula al
        # abrir el fichero porque el documento lo pide con `w:updateFields`.
        shutil.copy2(candidato, args.docx)

    try:
        mostrada = destino_pdf.relative_to(paths.ROOT)
    except ValueError:
        mostrada = destino_pdf
    print(f"\n  {mostrada} con los tres índices rellenos y verificados")
    print(f"  {args.docx.name} conserva sus campos y lleva el mismo resultado en caché")
    print("  `F9` en Word los vuelve a calcular sobre su propia paginación")
    return 0


if __name__ == "__main__":
    sys.exit(main())
