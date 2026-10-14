"""Que las seis afirmaciones corregidas no vuelvan al texto como afirmaciones.

**Por qué esta prueba existe.** Las seis frases que la corrección del 13 de
octubre de 2026 retiró no se borraron: cada una se cita dentro de la nota que la
corrige, para que la evolución del trabajo quede visible. Eso crea un riesgo
concreto: una edición futura podría reintroducir la frase como afirmación, y a
simple vista el documento se vería igual.

La prueba distingue las dos situaciones por la forma: dentro de una nota la línea
empieza por ``>``; como afirmación, no. Si alguna de las seis aparece fuera de una
cita, falla y dice cuál.

No comprueba el estilo ni la prosa: comprueba que no se vuelva a afirmar algo que
los artefactos contradicen.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from mecanico_ia_exp.config import paths

#: (frase retirada, por qué era falsa). La segunda mitad entra en el mensaje de
#: fallo, para que quien lo lea sepa por qué no puede escribirla.
RETIRADAS: tuple[tuple[str, str], ...] = (
    (
        "permanece cerrado y no se ha consultado",
        "el conjunto de prueba se abrió cinco veces (registro-aperturas-test.md)",
    ),
    (
        "que sigue cerrado",
        "el conjunto de prueba se abrió cinco veces",
    ),
    (
        "cerrado por construcción",
        "el cierre es del código, no del estado del conjunto",
    ),
    (
        "quedan pendientes",
        "la evaluación final se ejecutó el 12-10-2026 (E19_evaluacion_final_v3.json)",
    ),
    (
        "seguirá sin poder interpretarse",
        "P1 se ejecutó el 13-10-2026 (E15_suficiencia_distractor_v2.json)",
    ),
    (
        "necesita un rediseño antes de sostener",
        "el rediseño se hizo y se ejecutó",
    ),
    (
        "del que salen E6, E7 y la evaluación final",
        "las tres ejecuciones declaran dataset_id synthetic_v2, que sí se reconstruye",
    ),
    (
        "el fallo de encendido y el termostato bloqueado abierto",
        "el termostato es el fallo con la firma MÁS clara en medias (69,2 frente a 81,4 °C);"
        " el segundo invisible es la sonda lambda de respuesta lenta",
    ),
)

CAPITULOS = ("cap5_resultados.md", "cap6_conclusiones.md")


def _lineas(nombre: str) -> list[tuple[int, str]]:
    ruta = paths.ROOT / "docs" / "memoria" / nombre
    return list(enumerate(ruta.read_text("utf-8").splitlines(), 1))


@pytest.mark.parametrize("nombre", CAPITULOS)
def test_ninguna_frase_retirada_vuelve_como_afirmacion(nombre: str) -> None:
    fuera_de_cita = []
    for numero, linea in _lineas(nombre):
        if linea.lstrip().startswith(">"):
            continue  # dentro de la nota que la corrige: ahí debe estar
        for frase, motivo in RETIRADAS:
            if frase in linea:
                fuera_de_cita.append(f"{nombre}:{numero} «{frase}» — {motivo}")
    assert not fuera_de_cita, "frases retiradas usadas como afirmación:\n  " + "\n  ".join(
        fuera_de_cita
    )


@pytest.mark.parametrize("nombre", CAPITULOS)
def test_las_correcciones_conservan_lo_que_el_texto_decia(nombre: str) -> None:
    """Una corrección que borra el texto anterior pierde la trazabilidad."""
    texto = (paths.ROOT / "docs" / "memoria" / nombre).read_text("utf-8")
    assert "Corrección del 13 de octubre de 2026" in texto
    # Desde la revisión de autonomía documental, la nota ya no lleva la ruta del
    # documento interno: lleva el identificador de la corrección, y el anexo C
    # dice dónde está cada uno. La trazabilidad no desaparece, cambia de sitio.
    identificadores = re.findall(r"`F-\d`", texto)
    assert identificadores, (
        f"{nombre}: ninguna nota cita el identificador de su corrección, y sin él"
        " la nota no se puede rastrear"
    )
    anexos = (paths.ROOT / "docs" / "memoria" / "anexos.md").read_text("utf-8")
    assert "`F-1` a `F-8`" in anexos, (
        "el anexo C tiene que decir dónde están los documentos de las correcciones"
    )


def test_la_propuesta_del_paso_a_tiene_las_cinco_columnas_exigidas() -> None:
    propuesta = paths.ROOT / "docs" / "audits" / "correccion-cap5-cap6-paso-a.md"
    assert propuesta.is_file()
    texto = propuesta.read_text("utf-8")
    for columna in (
        "Afirmación original",
        "Evidencia disponible",
        "Motivo de invalidez",
        "Redacción corregida",
        "Impacto sobre las conclusiones",
    ):
        assert columna in texto, f"la propuesta no declara «{columna}»"
    # Las seis, cada una con su identificador.
    for identificador in ("F-1", "F-2", "F-3", "F-4", "F-5", "F-6"):
        assert f"## {identificador} " in texto, f"falta el apartado de {identificador}"


def test_la_propuesta_de_figuras_declara_f7_y_f8_con_las_mismas_columnas() -> None:
    """Las dos añadidas el 13-10-2026 siguen el mismo procedimiento que las seis."""
    propuesta = paths.ROOT / "docs" / "audits" / "propuesta-figuras-cap5-cap6.md"
    assert propuesta.is_file()
    texto = propuesta.read_text("utf-8")
    for columna in (
        "Afirmación actual",
        "Evidencia disponible",
        "Motivo de invalidez",
        "Redacción corregida propuesta",
        "Impacto sobre las conclusiones",
    ):
        assert columna in texto, f"la propuesta no declara «{columna}»"
    for identificador in ("F-7", "F-8"):
        assert f"`{identificador}`" in texto, f"falta el apartado de {identificador}"


def test_los_tres_conjuntos_quedan_atribuidos_a_su_ejecucion() -> None:
    """F-7: quien lea el capítulo 6 tiene que poder saber qué conjunto sostiene qué."""
    texto = (paths.ROOT / "docs" / "memoria" / "cap6_conclusiones.md").read_text("utf-8")
    assert "se midieron sobre `synthetic_v2`" in texto
    assert "`synthetic_v3` no es reconstruible" in texto


def test_ninguna_cifra_de_las_tablas_cambia_con_la_correccion() -> None:
    """La corrección es de texto. Si toca una cifra, se ha desbordado."""
    texto = (Path(paths.ROOT) / "docs" / "memoria" / "cap5_resultados.md").read_text("utf-8")
    # Las cifras de las tablas 5.1, 5.2, 5.6 y 5.7 que el capítulo cita en prosa.
    for cifra in ("0,878", "0,286", "0,144", "0,085", "0,79", "17/17", "15/17"):
        assert cifra in texto, f"la cifra {cifra} ha desaparecido del capítulo 5"
