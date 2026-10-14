"""Que los índices del PDF salgan de la estructura real y no de una suposición.

**Por qué existe.** Los tres índices son campos nativos y la conversión
desatendida a PDF no los evalúa, de modo que el PDF de revisión salía con el
aviso de actualización donde debían ir las entradas. La solución escribe el
**resultado en caché** del campo —lo mismo que escribe Word al pulsar `F9`— con
las páginas medidas sobre el PDF.

El riesgo de ese enfoque es evidente y hay que cubrirlo: un índice generado que
no coincida con el documento es peor que un índice vacío, porque **miente con
aspecto de dato**. De ahí estas comprobaciones.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import Any

import pytest

from mecanico_ia_exp.config import paths


def _modulo() -> Any:
    especificacion = importlib.util.spec_from_file_location(
        "indices_pdf", paths.ROOT / "scripts" / "indices_pdf.py"
    )
    assert especificacion is not None and especificacion.loader is not None
    modulo = importlib.util.module_from_spec(especificacion)
    sys.modules["indices_pdf"] = modulo
    especificacion.loader.exec_module(modulo)
    return modulo


INDICES = _modulo()

DOCUMENTO = (
    '<w:p><w:pPr><w:pStyle w:val="Ttulo1"/></w:pPr><w:r><w:t>Capítulo 1</w:t></w:r></w:p>'
    '<w:p><w:pPr><w:pStyle w:val="TtuloApartado"/></w:pPr><w:r><w:t>Un apartado</w:t></w:r></w:p>'
    '<w:p><w:pPr><w:pStyle w:val="PieDeFigura"/></w:pPr>'
    "<w:r><w:t>Figura 5.1. Algo</w:t></w:r></w:p>"
    '<w:p><w:pPr><w:pStyle w:val="PieDeTabla"/></w:pPr>'
    "<w:r><w:t>Tabla 5.1. Otra cosa</w:t></w:r></w:p>"
    '<w:p><w:pPr><w:pStyle w:val="Normal"/></w:pPr><w:r><w:t>Texto corriente</w:t></w:r></w:p>'
)


def test_la_estructura_recoge_encabezados_y_pies_y_nada_mas() -> None:
    entradas = INDICES.estructura(DOCUMENTO)
    assert [(e.indice, e.texto, e.nivel) for e in entradas] == [
        ("general", "Capítulo 1", 1),
        ("general", "Un apartado", 2),
        ("figuras", "Figura 5.1. Algo", 1),
        ("tablas", "Tabla 5.1. Otra cosa", 1),
    ]


def test_el_cuerpo_empieza_despues_del_ultimo_indice() -> None:
    """Sin esto, cada entrada se encuentra dentro del propio índice.

    Es el defecto que tuvo la primera versión: el índice general remitía a la
    página 3 para absolutamente todo, porque ahí estaba el texto que buscaba.
    """
    paginas = ["portada", "ÍNDICE ...", "ÍNDICE DE FIGURAS ...", "ÍNDICE DE TABLAS ...", "Resumen"]
    assert INDICES.primera_pagina_del_cuerpo(paginas) == 5


def test_la_medicion_no_retrocede() -> None:
    """El documento es lineal: un encabezado no puede estar antes que el anterior."""
    paginas = ["ÍNDICE", "Capítulo 1 y también Un apartado", "más texto", "Un apartado otra vez"]
    entradas = [
        INDICES.Entrada("general", "Capítulo 1", 1),
        INDICES.Entrada("general", "Un apartado", 2),
    ]
    medidas = INDICES.medir(entradas, paginas)
    assert [e.pagina for e in medidas] == [2, 2]
    assert medidas[1].pagina >= medidas[0].pagina


def test_la_verificacion_detecta_una_pagina_equivocada() -> None:
    paginas = ["ÍNDICE", "aquí está Capítulo 1", "aquí no"]
    buenas = [INDICES.Entrada("general", "Capítulo 1", 1, 2)]
    malas = [INDICES.Entrada("general", "Capítulo 1", 1, 3)]
    fuera = [INDICES.Entrada("general", "Capítulo 1", 1, 99)]
    assert INDICES.verificar(buenas, paginas) == []
    assert INDICES.verificar(malas, paginas), "una página equivocada tiene que detectarse"
    assert INDICES.verificar(fuera, paginas), "una página fuera del documento, también"


def test_el_relleno_conserva_el_campo() -> None:
    """Lo que se escribe es el resultado en caché, no texto que sustituya al campo."""
    documento = (
        "<w:p><w:r><w:t>"
        + INDICES.PROVISIONALES["general"]
        + "</w:t></w:r></w:p>"
        + "<w:p><w:r><w:t>"
        + INDICES.PROVISIONALES["figuras"]
        + "</w:t></w:r></w:p>"
        + "<w:p><w:r><w:t>"
        + INDICES.PROVISIONALES["tablas"]
        + "</w:t></w:r></w:p>"
    )
    entradas = [
        INDICES.Entrada("general", "Capítulo 1", 1, 7),
        INDICES.Entrada("figuras", "Figura 5.1. Algo", 1, 9),
        INDICES.Entrada("tablas", "Tabla 5.1. Otra cosa", 1, 11),
    ]
    resultado, rellenados = INDICES.rellenar(documento, entradas)
    assert rellenados == 3
    assert 'w:fldCharType="begin"' in resultado, "el campo tiene que seguir siendo un campo"
    assert 'w:fldCharType="separate"' in resultado
    assert 'w:fldCharType="end"' in resultado
    assert "TOC " in resultado, "la instrucción del campo tiene que conservarse"
    assert "Capítulo 1" in resultado and ">7<" in resultado
    assert INDICES.PROVISIONALES["general"] not in resultado


def test_el_texto_escapa_lo_que_rompe_el_xml() -> None:
    entrada = INDICES.Entrada("general", "Modelos & datos <de prueba>", 1, 3)
    parrafo = INDICES._parrafo_de_entrada(entrada)
    assert "&amp;" in parrafo and "&lt;" in parrafo and "&gt;" in parrafo
    assert "<de prueba>" not in parrafo


@pytest.mark.parametrize("indice", ["general", "figuras", "tablas"])
def test_cada_indice_tiene_su_instruccion_de_campo(indice: str) -> None:
    assert indice in INDICES._INSTRUCCIONES
    assert INDICES._INSTRUCCIONES[indice].startswith("TOC ")


def test_el_entregable_lleva_los_tres_indices_rellenos() -> None:
    """Sobre el PDF entregado, si está: ninguna de las tres puede quedar vacía."""
    import re
    import subprocess

    pdf = paths.ROOT / "entregables" / "memoria.pdf"
    if not pdf.is_file():
        pytest.skip("el PDF no está en este clon")
    texto = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True
    ).stdout
    for aviso in INDICES.PROVISIONALES.values():
        assert aviso not in texto, f"el PDF entregado conserva el aviso «{aviso}»"
    # Y las entradas están: al menos una línea con puntos conductores y página.
    assert len(re.findall(r"\.{6,}\s*\d+", texto)) > 100, (
        "el PDF no tiene entradas de índice con su número de página"
    )
