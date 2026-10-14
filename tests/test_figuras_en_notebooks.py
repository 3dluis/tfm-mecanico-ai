"""Que ninguna figura de la memoria exista solo como imagen.

**Por qué esta prueba existe.** Una figura de un trabajo científico es una
afirmación, y una afirmación cuyo origen no se puede examinar no se distingue de
una ilustración. El riesgo que cubre no es que alguien invente un gráfico: es que
una figura acabe produciéndose en un guion de exportación, fuera de todo análisis,
y que el lector no tenga dónde ver de qué datos sale ni qué se puede concluir de
ella. El 14 de octubre de 2026, once de las veintitrés figuras estaban en esa
situación, y cuatro más se dibujaban **dos veces** con código distinto.

**Qué comprueba.** Que cada figura del documento tenga un notebook que la
produzca invocando la misma función que la produce para la memoria, y que ese
notebook contenga la explicación científica que la sostiene: objetivo, datos,
qué muestra, qué se interpreta y qué no se puede afirmar.

**Qué no comprueba.** Que la explicación sea buena. Eso lo juzga quien la lea.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from typing import Any

import pytest

from mecanico_ia_exp.config import paths

GUIONES = paths.ROOT / "scripts" / "notebooks"
NOTEBOOKS = paths.ROOT / "notebooks"
HTML = paths.ROOT / "docs" / "notebooks" / "html"
FIGURAS_DIR = paths.ROOT / "artifacts" / "figures" / "memoria"
MATRIZ = paths.ROOT / "docs" / "figuras-tfm.md"

#: Las cinco familias de explicación que toda figura debe tener cerca, con las
#: formas que los notebooks usan para cada una. Se admiten varias porque la
#: redacción es de quien escribe: lo que se exige es que la pregunta esté
#: respondida, no que lo esté con una fórmula concreta.
FAMILIAS: dict[str, tuple[str, ...]] = {
    "objetivo del análisis": (
        "Qué queremos investigar",
        "Objetivo del análisis",
        "Objetivo de este análisis",
        "Objetivo.",
        "Por qué está aquí",
        "Qué investiga",
    ),
    "datos y metodología": (
        "Datos y metodología",
        "Qué datos utilizamos",
        "Procedencia de los datos",
        "Qué datos representa",
        "Qué es esta figura",
        "El conjunto",
    ),
    "qué muestra": ("Qué muestra", "Lo observado", "Qué muestran"),
    "qué se interpreta": ("Qué podemos interpretar", "Interpretación"),
    "qué no se puede afirmar": (
        "Qué no podemos afirmar",
        "Limitaciones",
        "Qué permanece sin demostrar",
    ),
}

#: Cuánto texto alrededor de la invocación se considera «su apartado».
VENTANA_ANTES = 4000
VENTANA_DESPUES = 4500


def _registro() -> list[Any]:
    """El registro de figuras, importado del guion que las produce."""
    especificacion = importlib.util.spec_from_file_location(
        "figuras_memoria", paths.ROOT / "scripts" / "figuras_memoria.py"
    )
    assert especificacion is not None and especificacion.loader is not None
    modulo = importlib.util.module_from_spec(especificacion)
    sys.modules["figuras_memoria"] = modulo
    especificacion.loader.exec_module(modulo)
    return list(modulo.FIGURAS)


FIGURAS = _registro()
IDENTIFICADORES = [f.identificador for f in FIGURAS]


def _clave(figura: Any) -> str:
    """Lo que hay que encontrar en el notebook: la función, o el fichero copiado."""
    return figura.dibuja.__name__ if figura.dibuja is not None else figura.copia_de.stem


def _ipynb_del_guion(guion: str) -> str:
    """El `.ipynb` que escribe un guion, leído de su propia llamada a `escribir`.

    No se deduce del prefijo: `n05_suficiencia.py` escribe
    `05_suficiencia_y_abstencion.ipynb`, y hay notebooks antiguos con el mismo
    prefijo que harían coincidir a cualquiera.
    """
    texto = (GUIONES / f"n{guion}.py").read_text("utf-8")
    encontrado = re.search(r'escribir\(\s*"([^"]+\.ipynb)"', texto)
    assert encontrado, f"{guion}: no se ve qué notebook escribe"
    return encontrado.group(1)


def _apartado(figura: Any) -> tuple[str, str]:
    """El notebook que produce la figura y el texto que rodea a su invocación."""
    clave = _clave(figura)
    for ruta in sorted(GUIONES.glob("n*.py")):
        texto = ruta.read_text("utf-8")
        if clave not in texto:
            continue
        posicion = texto.index(clave)
        return ruta.stem[1:], texto[max(0, posicion - VENTANA_ANTES) : posicion + VENTANA_DESPUES]
    return "", ""


@pytest.mark.parametrize("identificador", IDENTIFICADORES)
def test_toda_figura_tiene_notebook_que_la_produce(identificador: str) -> None:
    """Ninguna figura puede existir solo en el guion de exportación."""
    figura = next(f for f in FIGURAS if f.identificador == identificador)
    notebook, _ = _apartado(figura)
    assert notebook, (
        f"la figura {identificador} no aparece en ningún notebook: la produce "
        f"«{_clave(figura)}» y ningún guion de `scripts/notebooks/` la invoca"
    )


@pytest.mark.parametrize("identificador", IDENTIFICADORES)
def test_el_notebook_explica_la_figura(identificador: str) -> None:
    """Invocar la función no basta: hay que decir qué es y qué no se puede concluir."""
    figura = next(f for f in FIGURAS if f.identificador == identificador)
    notebook, apartado = _apartado(figura)
    assert notebook, f"{identificador}: sin notebook"
    faltan = [
        familia
        for familia, formas in FAMILIAS.items()
        if not any(f"**{forma}" in apartado for forma in formas)
    ]
    assert not faltan, (
        f"la figura {identificador}, en el notebook {notebook}, no declara: " + ", ".join(faltan)
    )


@pytest.mark.parametrize("identificador", IDENTIFICADORES)
def test_el_notebook_declarado_es_el_que_la_produce(identificador: str) -> None:
    """El campo del registro tiene que decir la verdad, o no sirve de nada."""
    figura = next(f for f in FIGURAS if f.identificador == identificador)
    notebook, _ = _apartado(figura)
    assert notebook == figura.notebook, (
        f"{identificador}: el registro declara «{figura.notebook}» y quien la "
        f"produce es «{notebook}»"
    )


def test_ninguna_figura_se_dibuja_dos_veces() -> None:
    """Dos implementaciones de una figura son dos verdades posibles.

    Se busca código de dibujo en los notebooks que no venga del paquete. Un
    notebook puede dibujar figuras propias —las que no van al documento— pero no
    puede redibujar una que el paquete ya produce.
    """
    del_paquete = {_clave(f) for f in FIGURAS if f.dibuja is not None}
    sospechosas: list[str] = []
    for ruta in sorted(GUIONES.glob("n*.py")):
        texto = ruta.read_text("utf-8")
        for funcion in del_paquete:
            if funcion not in texto:
                continue
            posicion = texto.index(funcion)
            # El tramo examinado es **su celda**, que acaba en el cierre de la
            # cadena. Buscar el siguiente `plt.show()` del fichero metería en la
            # ventana celdas posteriores y daría un falso positivo.
            cierre = texto.find('"""),', posicion)
            tramo = texto[posicion : cierre if cierre > 0 else posicion + 600]
            if "plt.subplots" in tramo or "fig.suptitle" in tramo:
                sospechosas.append(f"{ruta.name}: {funcion}")
    assert not sospechosas, (
        "hay notebooks que redibujan una figura que el paquete ya produce:\n  "
        + "\n  ".join(sospechosas)
    )


@pytest.mark.parametrize("identificador", IDENTIFICADORES)
def test_toda_figura_esta_en_la_matriz_de_trazabilidad(identificador: str) -> None:
    texto = MATRIZ.read_text("utf-8")
    assert f"| {identificador} |" in texto, (
        f"la figura {identificador} no tiene fila en la matriz de trazabilidad"
    )


def test_la_matriz_del_documento_coincide_con_la_emitida() -> None:
    """La matriz se emite del registro; si alguien la edita a mano, se separan."""
    emitida = sys.modules["figuras_memoria"].trazabilidad()
    documento = MATRIZ.read_text("utf-8")
    # La columna de páginas depende del PDF, que no viaja con el repositorio.
    for linea in emitida.splitlines():
        if not linea.startswith("| 5.") and not linea.startswith("| 6."):
            continue
        sin_pagina = linea.rsplit("|", 2)[0]
        assert sin_pagina in documento, (
            "la matriz del documento no coincide con la emitida; "
            f"falta o difiere: {sin_pagina[:70]}"
        )


@pytest.mark.parametrize(
    "identificador", [f.identificador for f in FIGURAS if f.estatuto == "HISTORICA"]
)
def test_la_figura_historica_declara_por_que_no_se_regenera(identificador: str) -> None:
    """Una figura que no se puede rehacer tiene que decirlo donde se usa."""
    figura = next(f for f in FIGURAS if f.identificador == identificador)
    assert figura.motivo_de_la_copia, f"{identificador}: sin motivo declarado"
    _, apartado = _apartado(figura)
    señales = ("histórico", "histórica", "no se puede regenerar", "no se puede redibujar")
    assert any(s in apartado for s in señales), (
        f"{identificador}: su notebook no declara que es un artefacto histórico"
    )


@pytest.mark.parametrize(
    "identificador", [f.identificador for f in FIGURAS if f.estatuto == "CONCEPTUAL"]
)
def test_el_diagrama_conceptual_no_se_presenta_como_medicion(identificador: str) -> None:
    """Un diagrama no es evidencia, y su apartado tiene que decirlo."""
    figura = next(f for f in FIGURAS if f.identificador == identificador)
    _, apartado = _apartado(figura)
    señales = ("conceptual", "documental", "no es un resultado", "ninguna medición")
    assert any(s in apartado for s in señales), (
        f"{identificador}: su notebook no lo identifica como diagrama, "
        "de modo que podría leerse como una medición"
    )
    assert "sin conjunto" in figura.conjunto or figura.particion == "—", (
        f"{identificador}: un diagrama conceptual no debería declarar partición"
    )


@pytest.mark.parametrize("identificador", IDENTIFICADORES)
def test_la_figura_existe_y_su_huella_esta_registrada(identificador: str) -> None:
    figura = next(f for f in FIGURAS if f.identificador == identificador)
    png = FIGURAS_DIR / f"{figura.nombre}.png"
    if not png.is_file():
        pytest.skip(f"{identificador}: la figura no está en disco en este clon")
    assert figura.huella() != "—", f"{identificador}: sin huella"
    assert figura.huella() in MATRIZ.read_text("utf-8"), (
        f"{identificador}: su huella no coincide con la de la matriz; "
        "el artefacto del que sale cambió, o la matriz está sin regenerar"
    )


@pytest.mark.parametrize("identificador", IDENTIFICADORES)
def test_la_figura_del_documento_es_la_que_el_registro_produce(identificador: str) -> None:
    """La memoria no puede llevar una imagen distinta de la registrada."""
    figura = next(f for f in FIGURAS if f.identificador == identificador)
    letra = figura.identificador.split(".")[0]
    fuente = "anexos.md" if letra.isalpha() else f"cap{letra}_*.md"
    capitulos = list((paths.ROOT / "docs" / "memoria").glob(fuente))
    assert capitulos, f"{identificador}: no se encuentra su capítulo"
    texto = "".join(c.read_text("utf-8") for c in capitulos)
    assert f"{figura.nombre}.png" in texto, (
        f"{identificador}: el documento no referencia {figura.nombre}.png"
    )


def test_los_html_entregados_contienen_sus_visualizaciones() -> None:
    """Un HTML sin imágenes es un notebook que no se ejecutó."""
    if not HTML.is_dir():
        pytest.skip("los HTML no están en este clon")
    vacios = []
    for ruta in sorted(HTML.glob("*.html")):
        if ruta.read_text("utf-8", errors="replace").count("data:image/png") == 0:
            vacios.append(ruta.name)
    assert not vacios, (
        "estos HTML no contienen ninguna imagen, de modo que su notebook no se "
        "ejecutó al exportarlos: " + ", ".join(vacios)
    )


def test_el_montaje_se_detiene_si_falta_una_figura() -> None:
    """La generación documental no puede sustituir en silencio una figura ausente."""
    especificacion = importlib.util.spec_from_file_location(
        "montar_docx", paths.ROOT / "scripts" / "montar_docx.py"
    )
    assert especificacion is not None and especificacion.loader is not None
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    assert hasattr(modulo, "comprobar_figuras"), (
        "el montador no comprueba las figuras antes de escribir el documento"
    )


def test_los_notebooks_entregados_se_generan_de_su_guion() -> None:
    """Cada notebook de la entrega tiene un guion que lo escribe."""
    entregados = [
        "00_introduccion",
        "01_exploracion_obd",
        "02_comparacion_modelos",
        "03_analisis_e19",
        "04_explicabilidad",
        "05_suficiencia_y_abstencion",
        "06_expresion_del_fallo",
    ]
    for nombre in entregados:
        assert (NOTEBOOKS / f"{nombre}.ipynb").is_file(), f"falta el notebook {nombre}"
        guiones = list(GUIONES.glob(f"n{nombre[:2]}_*.py"))
        assert guiones, f"{nombre}: ningún guion lo genera"


@pytest.mark.parametrize("identificador", IDENTIFICADORES)
def test_la_figura_aparece_en_el_notebook_ejecutado(identificador: str) -> None:
    """El .ipynb versionado tiene que llevar la celda que la produce."""
    figura = next(f for f in FIGURAS if f.identificador == identificador)
    notebook, _ = _apartado(figura)
    assert notebook
    ruta = NOTEBOOKS / _ipynb_del_guion(notebook)
    assert ruta.is_file(), f"{identificador}: no existe el notebook {ruta.name}"
    contenido = json.loads(ruta.read_text("utf-8"))
    fuente = "".join(
        "".join(celda["source"]) for celda in contenido["cells"] if celda["cell_type"] == "code"
    )
    assert _clave(figura) in fuente, (
        f"{identificador}: el notebook {ruta.name} no contiene la celda "
        f"que la produce; ¿se regeneró desde su guion?"
    )


def test_ninguna_figura_queda_sin_estatuto() -> None:
    validos = {"COMPLETA", "HISTORICA", "CONCEPTUAL"}
    invalidas = [f.identificador for f in FIGURAS if f.estatuto not in validos]
    assert not invalidas, "figuras con estatuto no reconocido: " + ", ".join(invalidas)


def test_ninguna_figura_es_no_conforme() -> None:
    """El criterio del autor: una figura sin correspondencia no entra en la memoria."""
    no_conformes = []
    for figura in FIGURAS:
        notebook, apartado = _apartado(figura)
        if not notebook or not apartado:
            no_conformes.append(figura.identificador)
    assert not no_conformes, (
        "estas figuras no tienen correspondencia verificable con ningún notebook "
        "y no pueden aparecer en la memoria: " + ", ".join(no_conformes)
    )
