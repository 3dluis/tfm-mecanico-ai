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
import json
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
    "TextoDeTabla": "Texto de tabla",
}

PLANTILLA_POR_DEFECTO = Path("../24-25 Plantilla TFM MUIA.docx")

#: Marcadores de la plantilla y de qué campo del fichero de portada sale cada
#: uno. Un campo vacío deja el marcador a la vista: un documento que enseña
#: «[Director/a]» avisa de que falta un dato; uno que lo borra, no.
MARCADORES: dict[str, str] = {
    "[Título del trabajo de fin de master]": "titulo",
    "[Título del TFM]": "titulo",
    "[NOMBRE Y APELLIDOS DEL ESTUDIANTE]": "autor",
    "[Apellidos, Nombre autor]": "apellidos_nombre",
    "[Director/a]": "director",
    "[Fecha (mes y año)]": "fecha",
}


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


def _declaraciones_de_espacio(xml: str) -> dict[str, str]:
    """Los prefijos de espacio de nombres que declara la raíz del documento."""
    raiz = xml[xml.index("<w:document") : xml.index(">", xml.index("<w:document")) + 1]
    return dict(re.findall(r'xmlns:(\w+)="([^"]+)"', raiz))


def _unir_espacios_de_nombres(destino: str, origen: str) -> str:
    """Añade a la raíz del destino los prefijos que solo declara el origen.

    La portada de la plantilla usa prefijos —`w14`, `wp14`, `mc`— que Pandoc no
    declara. Pegarla sin traerlos produce un fichero que supera cualquier
    comprobación estructural y que **ningún programa puede abrir**: el error es
    «prefijo sin vincular», y aparece al cargarlo, no al escribirlo.
    """
    faltan = {
        prefijo: uri
        for prefijo, uri in _declaraciones_de_espacio(origen).items()
        if prefijo not in _declaraciones_de_espacio(destino)
    }
    if not faltan:
        return destino
    corte = destino.index(">", destino.index("<w:document"))
    anadido = "".join(f' xmlns:{prefijo}="{uri}"' for prefijo, uri in sorted(faltan.items()))
    return destino[:corte] + anadido + destino[corte:]


def _sin_comentarios(xml: str) -> str:
    """Quita las marcas de comentario de la portada.

    Los comentarios de la plantilla apuntan a identificadores que el documento
    convertido no tiene, y una referencia a un comentario inexistente basta para
    que Word se niegue a abrir el fichero.
    """
    xml = re.sub(r"<w:commentRange(?:Start|End)[^>]*/>", "", xml)
    xml = re.sub(
        r"<w:r\b[^>]*>(?:(?!</w:r>).)*?<w:commentReference[^>]*/>.*?</w:r>", "", xml, flags=re.S
    )
    return re.sub(r"<w:commentReference[^>]*/>", "", xml)


def _portada(xml_plantilla: str) -> str:
    """La primera sección de la plantilla, con su portada y su salto.

    Se corta en el párrafo que **contiene** el primer ``sectPr``: en OOXML el
    salto de sección vive dentro del último párrafo de la sección, de modo que
    cortar antes dejaría la portada sin su configuración de página.
    """
    cuerpo = xml_plantilla[xml_plantilla.index("<w:body>") + len("<w:body>") :]
    corte = cuerpo.index("<w:sectPr")
    fin = cuerpo.index("</w:p>", corte) + len("</w:p>")
    return _sin_comentarios(cuerpo[:fin])


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


def _mantener_con_el_siguiente(parrafo: str) -> str:
    """Pega un párrafo al que le sigue, para que no los separe un salto de página.

    Es el defecto más visible de un documento montado sin cuidado: una figura al
    final de una página y su pie al principio de la siguiente.
    """
    if "<w:keepNext/>" in parrafo:
        return parrafo
    if "<w:pPr>" in parrafo:
        return parrafo.replace("<w:pPr>", "<w:pPr><w:keepNext/>", 1)
    return parrafo.replace("<w:p>", "<w:p><w:pPr><w:keepNext/></w:pPr>", 1)


#: Identificador de lista que la plantilla asigna a «Título Apartado». Las
#: instancias nuevas, una por capítulo, se derivan de su misma lista abstracta.
NUMERACION_DE_APARTADOS = 14
PRIMER_NUMERO_NUEVO = 900


def _numeracion_por_capitulo(parrafo: str, numero: int, nivel: int) -> str:
    """Hace que los apartados vuelvan a empezar en 1 en cada capítulo.

    La plantilla numera «Título Apartado» con una única lista continua, de modo
    que el primer apartado del capítulo 5 sale como «17». Cada capítulo recibe
    aquí su propia instancia de la misma lista abstracta, con el inicio forzado.
    """
    propiedades = f'<w:numPr><w:ilvl w:val="{nivel}"/><w:numId w:val="{numero}"/></w:numPr>'
    if "<w:numPr>" in parrafo:
        return re.sub(r"<w:numPr>.*?</w:numPr>", propiedades, parrafo, count=1, flags=re.S)
    if "<w:pPr>" in parrafo:
        encontrado = re.search(r'(<w:pPr>(?:<w:pStyle w:val="[^"]+"/>)?)', parrafo)
        assert encontrado is not None
        return parrafo.replace(encontrado.group(1), encontrado.group(1) + propiedades, 1)
    return parrafo


def instancias_de_numeracion(capitulos: int) -> str:
    """Una instancia de lista por capítulo, cada una empezando en 1."""
    niveles = "".join(
        f'<w:lvlOverride w:ilvl="{nivel}"><w:startOverride w:val="1"/></w:lvlOverride>'
        for nivel in range(3)
    )
    return "".join(
        f'<w:num w:numId="{PRIMER_NUMERO_NUEVO + i}">'
        f'<w:abstractNumId w:val="{{abstracto}}"/>{niveles}</w:num>'
        for i in range(capitulos)
    )


def adaptar_estilos(cuerpo: str) -> tuple[str, dict[str, int]]:
    """Traduce los estilos de Pandoc a los de la plantilla, párrafo a párrafo.

    Un párrafo con `Compact` dentro de una celda de tabla NO es un elemento de
    lista: Pandoc usa ese estilo para las dos cosas. Se distinguen por si el
    párrafo lleva numeración.
    """
    cuenta: dict[str, int] = {}
    salida: list[str] = []
    posicion = 0
    capitulo = 0
    en_bibliografia = False
    for encontrado in re.finditer(r"<w:p(?: [^>]*)?>.*?</w:p>|<w:p(?: [^>]*)?/>", cuerpo, re.S):
        salida.append(cuerpo[posicion : encontrado.start()])
        parrafo = encontrado.group(0)
        posicion = encontrado.end()
        # Un párrafo dentro de una celda no es un párrafo del cuerpo: hereda su
        # espaciado y lo que debería ser una fila ocupa media página.
        anterior = cuerpo[: encontrado.start()]
        en_tabla = anterior.count("<w:tbl>") > anterior.count("</w:tbl>")
        estilo = _estilo_de_parrafo(parrafo)
        # El pie que Pandoc escribe bajo cada imagen repite su texto alternativo,
        # que ya viaja dentro de la imagen para los lectores de pantalla. El
        # documento tiene su propio título encima y su procedencia debajo.
        if estilo == "ImageCaption":
            cuenta["pies duplicados retirados"] = cuenta.get("pies duplicados retirados", 0) + 1
            continue
        destino: str | None = None
        if en_tabla:
            destino = "TextoDeTabla"
        elif estilo == "Compact":
            destino = "VietaNumeradaTFM" if "<w:numPr>" in parrafo else "Normal"
        elif estilo in EQUIVALENCIAS:
            destino = EQUIVALENCIAS[estilo]
        elif estilo in {"ImageCaption", "CaptionedFigure"}:
            destino = None  # se resuelve abajo, según lo que diga el párrafo
        texto = "" if en_tabla else _texto_de_parrafo(parrafo)
        if re.match(r"^\s*Figura [A-Z0-9]+\.\d+\.", texto):
            destino = "PieDeFigura"
        elif re.match(r"^\s*Tabla [A-Z0-9]+\.\d+\.", texto):
            destino = "PieDeTabla"
        if estilo == "Ttulo1":
            capitulo += 1
            # Las referencias llevan sangría francesa, que es un estilo propio de
            # la plantilla y no algo que la conversión pueda deducir del texto.
            en_bibliografia = _texto_de_parrafo(parrafo).strip().lower().startswith("bibliograf")
        elif en_bibliografia and destino == "Normal":
            destino = "BibliografaAPA"
        if destino in {"TtuloApartado", "Ttulosubapartado"} and capitulo:
            parrafo = _numeracion_por_capitulo(
                parrafo,
                PRIMER_NUMERO_NUEVO + capitulo - 1,
                0 if destino == "TtuloApartado" else 1,
            )
        if destino is not None and destino != estilo:
            parrafo = _reescribir_estilo(parrafo, destino)
            clave = f"{estilo or 'sin estilo'} → {destino}"
            cuenta[clave] = cuenta.get(clave, 0) + 1
        # El título de una figura, y la imagen que le sigue, se pegan a lo que
        # viene detrás: título, imagen y pie viajan juntos o no viajan.
        if destino in {"PieDeFigura", "PieDeTabla"} or "<w:drawing>" in parrafo:
            parrafo = _mantener_con_el_siguiente(parrafo)
            cuenta["pegados al siguiente"] = cuenta.get("pegados al siguiente", 0) + 1
        salida.append(parrafo)
    salida.append(cuerpo[posicion:])
    cuenta["capítulos con numeración propia"] = capitulo
    return "".join(salida), cuenta


def anadir_estilos(xml_estilos: str) -> str:
    """Añade a la COPIA los dos estilos de pie, basados en el Normal de la plantilla."""
    # Cada estilo nuevo con su propia definición: el pie va en negrita y pegado a
    # lo que le sigue; el texto de tabla, sin espaciado, porque heredar el del
    # cuerpo convierte una tabla de seis filas en dos páginas.
    definiciones = {
        "PieDeFigura": (
            '<w:pPr><w:keepNext/><w:spacing w:before="240" w:after="60"/></w:pPr>'
            '<w:rPr><w:b/><w:sz w:val="19"/></w:rPr>'
        ),
        "PieDeTabla": (
            '<w:pPr><w:keepNext/><w:spacing w:before="240" w:after="60"/></w:pPr>'
            '<w:rPr><w:b/><w:sz w:val="19"/></w:rPr>'
        ),
        "TextoDeTabla": (
            '<w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
            '<w:jc w:val="left"/><w:ind w:firstLine="0"/></w:pPr>'
            '<w:rPr><w:sz w:val="18"/></w:rPr>'
        ),
    }
    nuevos = []
    for identificador, nombre in ESTILOS_NUEVOS.items():
        if f'w:styleId="{identificador}"' in xml_estilos:
            continue
        nuevos.append(
            f'<w:style w:type="paragraph" w:customStyle="1" w:styleId="{identificador}">'
            f'<w:name w:val="{nombre}"/><w:basedOn w:val="Normal"/><w:qFormat/>'
            + definiciones[identificador]
            + "</w:style>"
        )
    return xml_estilos.replace("</w:styles>", "".join(nuevos) + "</w:styles>")


def rellenar_marcadores(xml: str, datos: dict[str, str]) -> tuple[str, int]:
    """Sustituye los marcadores de la plantilla por los datos de la portada."""
    sustituidos = 0
    for marcador, campo in MARCADORES.items():
        valor = (datos.get(campo) or "").strip()
        if not valor or marcador not in xml:
            continue
        sustituidos += xml.count(marcador)
        xml = xml.replace(marcador, valor)
    return xml, sustituidos


def anadir_numeracion(xml_numeracion: str, capitulos: int) -> str:
    """Añade una instancia de lista por capítulo, derivada de la de la plantilla."""
    if not capitulos:
        return xml_numeracion
    encontrado = re.search(
        rf'<w:num w:numId="{NUMERACION_DE_APARTADOS}"[^>]*>\s*<w:abstractNumId w:val="(\d+)"',
        xml_numeracion,
    )
    if encontrado is None:
        return xml_numeracion
    instancias = instancias_de_numeracion(capitulos).format(abstracto=encontrado.group(1))
    return xml_numeracion.replace("</w:numbering>", instancias + "</w:numbering>")


def montar(plantilla: Path, salida: Path, datos: dict[str, str] | None = None) -> dict[str, object]:
    datos = datos or {}
    salida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporal:
        intermedio = Path(temporal) / "cuerpo.docx"
        convertir(plantilla, intermedio)

        with zipfile.ZipFile(plantilla) as fuente:
            xml_plantilla = fuente.read("word/document.xml").decode("utf-8")
        portada = _portada(xml_plantilla)

        with zipfile.ZipFile(intermedio) as convertido:
            partes = {nombre: convertido.read(nombre) for nombre in convertido.namelist()}

        documento = _unir_espacios_de_nombres(
            partes["word/document.xml"].decode("utf-8"), xml_plantilla
        )
        inicio = documento.index("<w:body>") + len("<w:body>")
        cuerpo = documento[inicio : documento.rindex("</w:body>")]
        cuerpo, cambios = adaptar_estilos(cuerpo)
        documento_final = (
            documento[:inicio]
            + portada
            + _indices()
            + cuerpo
            + documento[documento.rindex("</w:body>") :]
        )
        documento_final, sustituidos = rellenar_marcadores(documento_final, datos)
        partes["word/document.xml"] = documento_final.encode("utf-8")
        partes["word/styles.xml"] = anadir_estilos(
            partes["word/styles.xml"].decode("utf-8")
        ).encode("utf-8")
        partes["word/numbering.xml"] = anadir_numeracion(
            partes["word/numbering.xml"].decode("utf-8"),
            int(cambios.get("capítulos con numeración propia", 0)),
        ).encode("utf-8")
        for cabecera in ("word/header1.xml", "word/header2.xml", "word/header3.xml"):
            if cabecera in partes:
                texto, mas = rellenar_marcadores(partes[cabecera].decode("utf-8"), datos)
                partes[cabecera] = texto.encode("utf-8")
                sustituidos += mas
        for pie in ("word/footer1.xml", "word/footer2.xml", "word/footer3.xml", "word/footer4.xml"):
            if pie in partes:
                texto, mas = rellenar_marcadores(partes[pie].decode("utf-8"), datos)
                partes[pie] = texto.encode("utf-8")
                sustituidos += mas
        cambios["marcadores sustituidos"] = sustituidos

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

    portada = paths.CONFIGS / "portada-tfm.json"
    datos = json.loads(portada.read_text("utf-8")) if portada.is_file() else {}
    pendientes = [
        campo for campo in set(MARCADORES.values()) if not (datos.get(campo) or "").strip()
    ]
    informe = montar(plantilla, args.salida, datos)
    print(f"convertido con {informe['pandoc']}")
    print(f"plantilla leída: {plantilla.name}")
    print("\nestilos traducidos a los de la plantilla:")
    cambios = informe["cambios_de_estilo"]
    assert isinstance(cambios, dict)
    for clave, veces in sorted(cambios.items(), key=lambda par: -par[1]):
        print(f"  {veces:5d}  {clave}")
    salida = informe["salida"]
    assert isinstance(salida, Path)
    if pendientes:
        print(
            "\nmarcadores SIN rellenar, porque su dato no consta: " + ", ".join(sorted(pendientes))
        )
        print("  se dejan a la vista en el documento, para que no pasen inadvertidos")
    print(f"\n{salida.relative_to(paths.ROOT)}  ({salida.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
