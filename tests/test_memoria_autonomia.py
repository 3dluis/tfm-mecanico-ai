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


def test_cada_pie_remite_a_la_correspondencia_en_lugar_de_a_una_ruta() -> None:
    for nombre in ("cap5_resultados.md", "cap6_conclusiones.md", "anexos.md"):
        texto = _texto(nombre)
        pies = [linea for linea in texto.splitlines() if linea.startswith("*Fuente:")]
        con_artefacto = [p for p in pies if "Artefacto" in p]
        assert con_artefacto, f"{nombre}: ningún pie declara su artefacto"
        for pie in con_artefacto:
            assert "tabla C.5" in pie, (
                f"{nombre}: un pie declara el artefacto sin remitir a la tabla C.5: {pie[:90]}"
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
