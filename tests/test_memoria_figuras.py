"""Que cada figura de la memoria exista, esté numerada y diga de dónde sale.

**Por qué esta prueba existe.** Una figura en un documento científico es una
afirmación más, y se cae por los mismos sitios: un fichero que no viaja con el
repositorio, una numeración que se descoloca al insertar una figura en medio, un
pie que no dice de qué experimento sale, o una imagen puesta sin interpretación.
Ninguna de esas cuatro cosas la detecta una lectura rápida del documento.

No comprueba si la figura es buena ni si el texto que la acompaña es correcto:
comprueba que no falte nada de lo que el documento promete sobre ella.
"""

from __future__ import annotations

import re
import struct
from pathlib import Path

import pytest

from mecanico_ia_exp.config import paths

CAPITULOS = ("cap5_resultados.md", "cap6_conclusiones.md")

#: «**Figura 5.3. Título.**» en una línea propia.
TITULO = re.compile(r"^\*\*Figura (\d+)\.(\d+)\. (.+?)\*\*$", re.MULTILINE)
#: «![texto alternativo](ruta)»
IMAGEN = re.compile(r"^!\[(.*?)\]\((.+?)\)$", re.MULTILINE)
#: El pie de procedencia, en cursiva y empezando por «Fuente:».
FUENTE = re.compile(r"^\*Fuente: (.+?)\*$", re.MULTILINE | re.DOTALL)

#: Lo que el pie tiene que declarar. «Conjunto» admite la forma negativa para
#: las figuras que no salen de ningún conjunto de datos, como el recorrido.
CAMPOS_DEL_PIE = ("Experimento", "Protocolo", "Artefacto")


def _texto(nombre: str) -> str:
    return (paths.ROOT / "docs" / "memoria" / nombre).read_text("utf-8")


def _dpi(ruta: Path) -> int:
    datos = ruta.read_bytes()
    posicion = datos.find(b"pHYs")
    if posicion < 0:
        return 0
    x, _, unidad = struct.unpack(">IIB", datos[posicion + 4 : posicion + 13])
    return round(x * 0.0254) if unidad == 1 else 0


@pytest.mark.parametrize("nombre", CAPITULOS)
def test_la_numeracion_de_las_figuras_sigue_el_orden_de_lectura(nombre: str) -> None:
    """Insertar una figura en medio descoloca las siguientes y nadie lo nota."""
    numeros = [(int(c), int(f)) for c, f, _ in TITULO.findall(_texto(nombre))]
    assert numeros, f"{nombre} no tiene ninguna figura"
    capitulo = numeros[0][0]
    esperado = [(capitulo, i) for i in range(1, len(numeros) + 1)]
    assert numeros == esperado, (
        f"la numeración de {nombre} no es correlativa: {['.'.join(map(str, n)) for n in numeros]}"
    )


@pytest.mark.parametrize("nombre", CAPITULOS)
def test_cada_figura_existe_y_tiene_resolucion_de_impresion(nombre: str) -> None:
    rutas = [r for _, r in IMAGEN.findall(_texto(nombre))]
    assert rutas, f"{nombre} no referencia ninguna imagen"
    for ruta in rutas:
        assert not ruta.startswith(("/", "~", "file:")), f"ruta local en {nombre}: {ruta}"
        fichero = (paths.ROOT / "docs" / "memoria" / ruta).resolve()
        assert fichero.is_file(), f"{nombre} referencia una figura que no existe: {ruta}"
        assert _dpi(fichero) >= 200, (
            f"{ruta} está por debajo de 200 ppp y va a un documento impreso"
        )


@pytest.mark.parametrize("nombre", CAPITULOS)
def test_cada_figura_lleva_titulo_imagen_pie_e_interpretacion(nombre: str) -> None:
    texto = _texto(nombre)
    titulos = list(TITULO.finditer(texto))
    imagenes = list(IMAGEN.finditer(texto))
    assert len(titulos) == len(imagenes), (
        f"{nombre}: {len(titulos)} títulos de figura y {len(imagenes)} imágenes"
    )
    # Las tablas del capítulo usan el mismo pie, de modo que cada figura se
    # empareja con el primer «Fuente:» que aparece DESPUÉS de su imagen.
    for titulo, imagen in zip(titulos, imagenes, strict=True):
        etiqueta = titulo.group(0)[:48]
        assert titulo.end() < imagen.start(), f"{etiqueta}: la imagen va después del título"
        fuente = FUENTE.search(texto, imagen.end())
        assert fuente is not None, f"{etiqueta}: no tiene pie de procedencia"
        assert imagen.group(1).strip(), f"{etiqueta}: la imagen no tiene texto alternativo"
        pie = fuente.group(1)
        for campo in CAMPOS_DEL_PIE:
            assert campo in pie, f"{etiqueta}: el pie no declara «{campo}»"
        assert "Conjunto" in pie or "Sin conjunto" in pie, (
            f"{etiqueta}: el pie no dice de qué conjunto sale, ni declara que no sale de ninguno"
        )
        # La interpretación va después del pie, antes del siguiente título.
        siguiente = texto.find("**Figura ", fuente.end())
        hasta = siguiente if siguiente > 0 else len(texto)
        interpretacion = texto[fuente.end() : hasta].strip()
        assert len(interpretacion) > 400, (
            f"{etiqueta}: lleva {len(interpretacion)} caracteres de interpretación."
            " Una figura sin interpretación no entra en la memoria"
        )


def test_toda_figura_de_la_memoria_sale_del_guion_que_las_genera() -> None:
    """Si una figura no está en el registro, nadie puede regenerarla."""
    guion = (paths.ROOT / "scripts" / "figuras_memoria.py").read_text("utf-8")
    for nombre in CAPITULOS:
        for _, ruta in IMAGEN.findall(_texto(nombre)):
            tronco = Path(ruta).stem
            assert f'"{tronco}"' in guion, (
                f"{tronco} no está en el registro de scripts/figuras_memoria.py"
            )


@pytest.mark.parametrize("nombre", CAPITULOS)
def test_toda_figura_se_menciona_en_el_cuerpo_por_su_numero(nombre: str) -> None:
    """La plantilla exige mencionarlas por número, nunca por su posición.

    Una figura que el texto no nombra queda huérfana: el lector no sabe en qué
    momento del argumento debe mirarla, y una reordenación posterior no se nota.
    """
    texto = _texto(nombre)
    sin_mencion = []
    for capitulo, numero, _ in TITULO.findall(texto):
        etiqueta = f"Figura {capitulo}.{numero}"
        # El título propio no cuenta: se busca una mención en prosa.
        menciones = len(re.findall(rf"{etiqueta}\b", texto))
        if menciones < 2:
            sin_mencion.append(etiqueta)
    assert not sin_mencion, (
        f"{nombre}: estas figuras no se mencionan en el texto: {', '.join(sin_mencion)}"
    )
