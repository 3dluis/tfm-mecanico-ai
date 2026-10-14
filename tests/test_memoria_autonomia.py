"""Que la memoria se entienda sin abrir el repositorio.

**Por qué esta prueba existe.** El tribunal lee un documento, no un repositorio.
Una frase como «los detalles están en `docs/...`» traslada al lector la parte que
el documento debía explicar, y lo hace de forma que ninguna revisión de estilo
detecta: la frase está bien escrita y la ruta es correcta.

La prueba distingue dos cosas que se parecen y no son lo mismo. Una **ruta de
procedencia** dice de dónde salió una figura y no obliga a nadie a salir del
documento. Una **remisión** dice que lo que falta está en otro sitio, y sí obliga.
Lo primero se permite, y solo en el anexo de reproducibilidad; lo segundo, en
ningún sitio del cuerpo.
"""

from __future__ import annotations

import re

import pytest

from mecanico_ia_exp.config import paths

#: Los capítulos, donde el criterio es estricto. Los anexos van aparte.
CUERPO = (
    "00_resumen.md",
    "cap1_introduccion.md",
    "cap2_objetivos.md",
    "cap3_marco_teorico.md",
    "cap4_marco_metodologico.md",
    "cap5_resultados.md",
    "cap6_conclusiones.md",
)

#: Directorios del repositorio que no deben aparecer citados en el cuerpo.
DIRECTORIOS = ("docs/", "experiments/", "configs/", "artifacts/", "scripts/", "src/", "data/")

#: Formas con que una frase delega en un fichero lo que debería explicar.
REMISIONES = re.compile(
    r"(está en|están en|se encuentra[n]? en|los detalles|el detalle"
    r"|véase|ver|consúltese)\s+`[^`]+`",
    re.IGNORECASE,
)


def _texto(nombre: str) -> str:
    return (paths.ROOT / "docs" / "memoria" / nombre).read_text("utf-8")


@pytest.mark.parametrize("nombre", CUERPO)
def test_ningun_capitulo_cita_una_ruta_del_repositorio(nombre: str) -> None:
    """Las rutas de los artefactos viven en el anexo C, no en los capítulos."""
    encontradas = []
    for numero, linea in enumerate(_texto(nombre).splitlines(), 1):
        # La ruta de la imagen en Markdown no es texto que el lector vea: es
        # cómo la figura entra en el documento.
        sin_imagenes = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", linea)
        for cita in re.findall(r"`([^`]+)`", sin_imagenes):
            if any(cita.startswith(d) or f"/{d}" in cita for d in DIRECTORIOS):
                encontradas.append(f"{nombre}:{numero} → {cita}")
    assert not encontradas, (
        "el cuerpo del trabajo cita rutas del repositorio; su sitio es la tabla C.5:\n  "
        + "\n  ".join(encontradas)
    )


@pytest.mark.parametrize("nombre", CUERPO)
def test_ninguna_frase_delega_en_un_fichero_lo_que_debe_explicar(nombre: str) -> None:
    delegaciones = []
    for numero, linea in enumerate(_texto(nombre).splitlines(), 1):
        for encontrado in REMISIONES.finditer(linea):
            cita = encontrado.group(0)
            if any(d in cita for d in DIRECTORIOS) or cita.rstrip("`").endswith(
                (".md", ".json", ".csv", ".py", ".ipynb", ".yaml", ".parquet")
            ):
                delegaciones.append(f"{nombre}:{numero} → {cita[:70]}")
    assert not delegaciones, (
        "hay frases que remiten a un fichero en lugar de explicar:\n  " + "\n  ".join(delegaciones)
    )


def test_el_anexo_de_reproducibilidad_conserva_la_correspondencia() -> None:
    """Quitar las rutas del cuerpo solo vale si están en otro sitio del documento."""
    anexos = _texto("anexos.md")
    assert "Tabla C.5" in anexos, "falta la tabla de correspondencia"
    for referencia in ("Figura 5.1", "Figura 6.1", "Figura A.1", "Figura B.1", "Tabla 5.8"):
        assert referencia in anexos, f"la tabla C.5 no recoge {referencia}"
    assert "artifacts/figures/memoria/" in anexos, (
        "la tabla C.5 tiene que decir dónde viven los ficheros"
    )


def test_ningun_pie_interrumpe_la_narrativa_con_una_remision_tecnica() -> None:
    """El pie declara la procedencia científica, no la operativa.

    Hasta el 14 de octubre de 2026 cada pie terminaba remitiendo a la tabla de
    correspondencia del anexo C. La regla cambió: la memoria se lee como una
    investigación y la procedencia técnica —qué fichero, qué guion, qué
    registro— vive en la documentación de reproducibilidad, no dentro del pie.

    Lo que el pie **sí** conserva, y otra prueba comprueba, es el experimento,
    el conjunto, la partición y el protocolo: eso es ciencia, no operación.
    """
    operativas = ("Artefacto:", "tabla C.5", "el guion que lo genera", "notebook")
    for nombre in ("cap5_resultados.md", "cap6_conclusiones.md", "anexos.md"):
        for pie in [x for x in _texto(nombre).splitlines() if x.startswith("*Fuente:")]:
            encontradas = [frase for frase in operativas if frase in pie]
            assert not encontradas, (
                f"{nombre}: un pie remite a {', '.join(encontradas)}, "
                f"que es procedencia operativa y no científica: {pie[:90]}"
            )


def _pies_de_figura_o_tabla(texto: str) -> list[str]:
    """Los `*Fuente:` que cierran una figura o una tabla, y no otros.

    En el anexo de reproducibilidad hay notas de procedencia que cierran un
    apartado y no ilustran nada: no tienen experimento porque no son evidencia.
    Se reconocen los de figura y tabla por el encabezado que los precede.
    """
    pies: list[str] = []
    pendiente = ""
    for linea in texto.splitlines():
        encabezado = re.match(r"\*\*(?:Figura|Tabla) ([A-Z0-9]+)\.", linea)
        if encabezado:
            pendiente = encabezado.group(1)
        elif linea.startswith("*Fuente:"):
            # El anexo C documenta la reproducción, no la evidencia: sus tablas
            # enumeran órdenes, guiones y lo que no se puede reproducir, y no
            # salen de ningún experimento.
            if pendiente and pendiente != "C":
                pies.append(linea)
            pendiente = ""
    return pies


def test_cada_pie_declara_su_procedencia_cientifica() -> None:
    """Quitar la remisión técnica no puede quitar de dónde sale la figura."""
    for nombre in ("cap5_resultados.md", "cap6_conclusiones.md", "anexos.md"):
        pies = _pies_de_figura_o_tabla(_texto(nombre))
        assert pies, f"{nombre}: ningún pie de figura o tabla"
        for pie in pies:
            if "elaboración propia a partir de" in pie or pie == "*Fuente: elaboración propia.*":
                # Un pie de tabla cuyos registros nombra la propia tabla en una
                # de sus columnas no necesita repetirlos debajo.
                continue
            assert "Experimento" in pie or "Experimentos" in pie, (
                f"{nombre}: un pie no dice de qué experimento sale: {pie[:90]}"
            )


def test_la_memoria_no_contiene_rutas_locales() -> None:
    """Una ruta de esta máquina en el documento entregado es un defecto de entrega."""
    for nombre in (*CUERPO, "anexos.md", "bibliografia.md"):
        texto = _texto(nombre)
        for patron in ("/Users/", "/home/", "C:\\", "file://"):
            assert patron not in texto, f"{nombre} contiene una ruta local: {patron}"


def test_los_ficheros_que_el_anexo_cita_existen() -> None:
    """El anexo C sí puede citar rutas; lo que no puede es citar rutas falsas."""
    anexos = _texto("anexos.md")
    faltan = []
    for cita in re.findall(r"`((?:scripts|configs|docs|artifacts|experiments)/[\w/.\-]+)`", anexos):
        if cita.endswith("/"):
            destino = paths.ROOT / cita
            if not destino.is_dir():
                faltan.append(cita)
        elif not (paths.ROOT / cita).exists():
            faltan.append(cita)
    assert not faltan, "el anexo cita rutas que no existen: " + ", ".join(sorted(set(faltan)))
