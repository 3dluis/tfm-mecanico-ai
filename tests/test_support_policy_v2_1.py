"""Política de suficiencia v2.1: la sección como unidad de papel.

Cada test corresponde a una condición de
`docs/methodology/politica-suficiencia-v2-1.md`. Los fragmentos están escritos con
la forma del manual real, y **ninguno reproduce un caso del conjunto anotado**:
los códigos son de frenos, `airbag` y red, y las señales no aparecen en ningún
caso del banco experimental. Si la regla necesitara conocer los casos, aquí
fallaría.

Nota sobre `tests/test_support_policy_v2.py`, que queda intacto como evidencia
congelada de v2: su constructor de fragmentos recibe la sección y **no la pasa**
al objeto. Por eso aquella suite ejercitó únicamente la clasificación por rasgos
del fragmento y nunca el encabezado. Se registra aquí en vez de corregirse allí.
"""

from __future__ import annotations

import pytest

from mecanico_ia_exp.evidence.model import Claim, DocumentaryEvidence
from mecanico_ia_exp.evidence.support import (
    SIN_CORRESPONDENCIA,
    ChunkRole,
    check_support,
    classify_chunk,
    classify_section,
)

CLAIM = Claim(claim_id="C01", text="El descriptor throttle_position (mean) toma el valor 3,2.")

TEXTO_PROCEDIMIENTO = (
    "Turn the ignition switch off. Disconnect the throttle position sensor connector. "
    "Measure the voltage at terminal A. Is the voltage within specification?\n"
    "Yes Go to the next step.\nNo Repair or replace the harness."
)
TEXTO_DETECCION = (
    "The PCM monitors the throttle position sensor signal while the vehicle is moving. "
    "The PCM determines that the circuit is malfunctioning when the value remains "
    "below the standard value."
)


def _fragmento(
    texto: str,
    seccion: str | None,
    dtc: tuple[str, ...] = ("B1234",),
) -> DocumentaryEvidence:
    """A diferencia del constructor de v2, este **sí** pasa la sección."""
    return DocumentaryEvidence(
        chunk_id="ch",
        document_id="doc",
        vehicle_id="v",
        text=texto,
        score=0.5,
        applicability="EXACT_MATCH",
        document_type="WORKSHOP_MANUAL",
        dtc_codes=dtc,
        section=seccion,
    )


# --- Grupo 1 · Las secciones que v2 corrigió siguen sin sostener ----------------
# Los seis casos que v2 corrigió aceptaban fragmentos de secciones tituladas
# `KOEO/KOER SELF-TEST` y `DTC DETECTION LOGIC AND CONDITIONS`. La propiedad
# estructural que sostiene aquella corrección se comprueba aquí con códigos y
# señales ajenos al banco; que además siga cumpliéndose en los diecisiete casos lo
# comprueba el experimento, no un test unitario.


@pytest.mark.parametrize(
    "seccion",
    [
        "KOEO/KOER SELF-TEST [ZJ, Z6]",
        "DTC DETECTION LOGIC AND CONDITIONS [ZJ, Z6]",
        "DTC TABLE [ZJ, Z6]",
        "ON-BOARD DIAGNOSTIC DTC LIST",
    ],
)
def test_las_secciones_que_v2_rechazo_siguen_sin_sostener(seccion: str) -> None:
    fragmento = _fragmento(
        f"B1234 throttle position sensor circuit.\n{TEXTO_DETECCION}\n{TEXTO_PROCEDIMIENTO}",
        seccion,
    )
    resultado = check_support(CLAIM, fragmento, signal="throttle_position", expected_dtc=("B1234",))
    assert resultado.mentions_signal and resultado.carries_expected_dtc
    assert not resultado.supports
    assert resultado.chunk_role != ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE.value


def test_ni_siquiera_con_pasos_de_inspeccion_una_seccion_de_listado_sostiene() -> None:
    """El encabezado manda sobre los rasgos del texto.

    Es lo que impide que una tabla que cite un paso de inspección pase por
    procedimiento, y es también el precio de la regla: si el manual titulase mal
    una sección, v2.1 la clasificaría mal.
    """
    fragmento = _fragmento(TEXTO_PROCEDIMIENTO, "DTC TABLE [ZJ, Z6]")
    assert classify_chunk(fragmento) == ChunkRole.CODE_DEFINITION_OR_TABLE


# --- Grupo 2 · Códigos y señales fuera del banco experimental -------------------
# El banco usa P2187, P0125 y P0133 con señales de combustible, temperatura y
# sonda. Nada de eso aparece aquí.


@pytest.mark.parametrize(
    ("codigo", "senal"),
    [
        ("B1234", "throttle_position"),
        ("C1500", "vehicle_speed"),
        ("U0100", "engine_load"),
        ("B2AAA", "ignition_timing"),
    ],
)
def test_la_regla_opera_sobre_codigos_y_senales_ajenos_al_banco(codigo: str, senal: str) -> None:
    """Códigos de frenos, dirección, red y `airbag`, y señales que ningún caso usa.

    Las cuatro señales están en el diccionario de vocabulario pero **fuera** de
    los tres fallos del banco, que usan ajuste de combustible, temperatura de
    refrigerante, presión de colector, sonda y régimen. Para señales fuera del
    diccionario la generalidad se comprueba en el test siguiente, al nivel donde
    la regla opera.
    """
    procedimiento = _fragmento(
        f"{codigo} {senal.replace('_', ' ')} circuit.\n{TEXTO_PROCEDIMIENTO}",
        f"DTC {codigo} [ZJ, Z6]",
        (codigo,),
    )
    resultado = check_support(CLAIM, procedimiento, signal=senal, expected_dtc=(codigo,))
    assert resultado.supports
    assert resultado.chunk_role == ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE.value

    tabla = _fragmento(
        f"{codigo} {senal.replace('_', ' ')} circuit low\n{TEXTO_PROCEDIMIENTO}",
        "DTC TABLE [ZJ, Z6]",
        (codigo,),
    )
    assert not check_support(CLAIM, tabla, signal=senal, expected_dtc=(codigo,)).supports


def test_la_clasificacion_generaliza_a_senales_fuera_del_diccionario() -> None:
    """La regla de papel es independiente del vocabulario de señales.

    Con una señal que el verificador no sabe traducir, la **clasificación** sigue
    siendo correcta y el soporte se deniega por la puerta de vocabulario, con su
    motivo propio. Separar las dos cosas es lo que permite decir que la regla
    estructural generaliza aunque el instrumento completo no pueda pronunciarse.
    """
    procedimiento = _fragmento(
        f"B1234 transmission fluid temperature sensor.\n{TEXTO_PROCEDIMIENTO}",
        "DTC B1234 [ZJ, Z6]",
    )
    assert classify_chunk(procedimiento) == ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE
    resultado = check_support(
        CLAIM, procedimiento, signal="transmission_fluid_temperature", expected_dtc=("B1234",)
    )
    assert not resultado.supports
    assert resultado.signal_mapping == SIN_CORRESPONDENCIA


# --- Grupo 3 · Ausencia de lógica específica de caso ----------------------------


@pytest.mark.parametrize(
    "termino",
    [
        "P2187",
        "long term fuel trim",
        "ltft_bank1",
        "thermostat",
        "engine coolant temperature",
        "oxygen sensor",
        "heated oxygen sensor",
    ],
)
def test_ningun_termino_del_banco_cambia_la_clasificacion(termino: str) -> None:
    """Sustituir el asunto no altera el papel.

    Si existiera una regla escrita para el termostato, la sonda, la fuga de vacío
    o `P2187`, el mismo texto con y sin esos términos se clasificaría distinto.
    Se clasifica igual.
    """
    neutro = _fragmento(TEXTO_PROCEDIMIENTO, "DTC B1234 [ZJ, Z6]")
    con_termino = _fragmento(
        TEXTO_PROCEDIMIENTO.replace("throttle position sensor", termino),
        "DTC B1234 [ZJ, Z6]",
    )
    assert classify_chunk(con_termino) == classify_chunk(neutro)


def test_el_codigo_del_banco_como_encabezado_no_recibe_trato_distinto() -> None:
    """`DTC P2187` y `DTC B1234` son el mismo tipo de encabezado para la regla."""
    assert classify_section("DTC P2187 [ZJ, Z6]") == classify_section("DTC B1234 [ZJ, Z6]")
    assert classify_section("DTC P2187 [ZJ, Z6]") == ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE


def test_el_codigo_de_la_seccion_no_tiene_que_coincidir_con_el_esperado() -> None:
    """La clasificación no mira qué código se busca: solo la forma del encabezado.

    La correspondencia entre el código esperado y el que porta el fragmento la
    comprueba `carries_expected_dtc`, que es una condición aparte.
    """
    ajeno = _fragmento(TEXTO_PROCEDIMIENTO, "DTC U0100 [ZJ, Z6]", ("U0100",))
    resultado = check_support(CLAIM, ajeno, signal="throttle_position", expected_dtc=("B1234",))
    assert resultado.chunk_role == ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE.value
    assert not resultado.carries_expected_dtc
    assert not resultado.supports


# --- Grupo 4 · Un procedimiento se distingue de cada clase de referencia --------


@pytest.mark.parametrize(
    ("seccion", "papel"),
    [
        ("DTC B1234 [ZJ, Z6]", ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE),
        ("DTC C1500", ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE),
        ("DTC TABLE [ZJ, Z6]", ChunkRole.CODE_DEFINITION_OR_TABLE),
        ("KOEO/KOER SELF-TEST [ZJ, Z6]", ChunkRole.CODE_DEFINITION_OR_TABLE),
        ("ON-BOARD DIAGNOSTIC DTC LIST", ChunkRole.CODE_DEFINITION_OR_TABLE),
        ("DTC INDEX", ChunkRole.CODE_DEFINITION_OR_TABLE),
        ("DTC DETECTION LOGIC AND CONDITIONS", ChunkRole.SUPPORTING_DIAGNOSTIC_REFERENCE),
        ("PCM MONITORING SYSTEM", ChunkRole.SUPPORTING_DIAGNOSTIC_REFERENCE),
        ("ON-BOARD DIAGNOSTIC TEST MODE", ChunkRole.SUPPORTING_DIAGNOSTIC_REFERENCE),
        ("BRAKE SYSTEM SPECIFICATIONS", ChunkRole.SUPPORTING_DIAGNOSTIC_REFERENCE),
        ("BRAKE PRESSURE SENSOR DESCRIPTION", ChunkRole.SUPPORTING_DIAGNOSTIC_REFERENCE),
    ],
)
def test_cada_clase_de_encabezado_recibe_su_papel(seccion: str, papel: ChunkRole) -> None:
    assert classify_section(seccion) == papel


def test_un_encabezado_que_no_declara_nada_devuelve_la_decision_al_fragmento() -> None:
    """El paso 2 de la regla: v2.1 añade un paso previo, no sustituye a v2.

    Es lo que sostiene que el único cambio entre las dos versiones sea la
    granularidad. Sin encabezado informativo, v2.1 decide exactamente lo que
    decidía v2.
    """
    assert classify_section("REMOVAL/INSTALLATION") is None
    assert classify_section(None) is None
    sin_encabezado = _fragmento(TEXTO_PROCEDIMIENTO, None)
    assert classify_chunk(sin_encabezado) == ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE
    solo_deteccion = _fragmento(TEXTO_DETECCION, None)
    assert classify_chunk(solo_deteccion) == ChunkRole.SUPPORTING_DIAGNOSTIC_REFERENCE
