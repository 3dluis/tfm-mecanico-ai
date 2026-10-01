"""Verificador v2.2: la puerta de códigos con requisito explícito.

Ocho grupos, uno por cada categoría que el protocolo exige antes de medir con
este instrumento. La regla se documentó en
`docs/methodology/politica-puerta-dtc.md` antes de implementarse.

Ningún fragmento de aquí reproduce un caso del banco: los códigos son de frenos,
transmisión, red y `airbag`, y las señales se eligen fuera de los tres fallos.
"""

from __future__ import annotations

import pytest

from mecanico_ia_exp.evidence.model import Claim, DocumentaryEvidence
from mecanico_ia_exp.evidence.support import (
    SIN_CORRESPONDENCIA,
    ChunkRole,
    DtcRequirement,
    check_support,
    classify_section,
    dtc_requirement,
)

CLAIM = Claim(claim_id="C01", text="afirmación")

PASOS = (
    "Turn the ignition switch off. Disconnect the connector. Measure the resistance. "
    "Is the resistance within specification?\nYes Go to the next step.\nNo Replace the part."
)


def _frag(
    texto: str = PASOS,
    seccion: str | None = "DTC B1234 [ZJ, Z6]",
    dtc: tuple[str, ...] = ("B1234",),
    applicability: str = "EXACT_MATCH",
) -> DocumentaryEvidence:
    return DocumentaryEvidence(
        chunk_id="ch",
        document_id="doc",
        vehicle_id="v",
        text=texto,
        score=0.5,
        applicability=applicability,
        document_type="WORKSHOP_MANUAL",
        dtc_codes=dtc,
        section=seccion,
    )


# --- 1 · Clasificación por papel de sección ------------------------------------


@pytest.mark.parametrize(
    ("seccion", "papel"),
    [
        ("DTC B1234 [ZJ, Z6]", ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE),
        ("DTC U0100", ChunkRole.PROCEDURAL_DIAGNOSTIC_EVIDENCE),
        ("DTC DETECTION LOGIC AND CONDITIONS", ChunkRole.SUPPORTING_DIAGNOSTIC_REFERENCE),
        ("TRANSMISSION SPECIFICATIONS", ChunkRole.SUPPORTING_DIAGNOSTIC_REFERENCE),
    ],
)
def test_el_encabezado_de_seccion_decide_el_papel(seccion: str, papel: ChunkRole) -> None:
    assert classify_section(seccion) == papel


# --- 2 · Tabla frente a procedimiento ------------------------------------------


@pytest.mark.parametrize(
    "seccion", ["DTC TABLE [ZJ, Z6]", "KOEO/KOER SELF-TEST", "ON-BOARD DIAGNOSTIC DTC LIST"]
)
def test_una_tabla_no_sostiene_aunque_tenga_forma_de_procedimiento(seccion: str) -> None:
    """El encabezado manda sobre el texto: una tabla que cite un paso sigue siendo tabla."""
    resultado = check_support(
        CLAIM, _frag(seccion=seccion), signal="throttle_position", expected_dtc=("B1234",)
    )
    assert resultado.chunk_role == ChunkRole.CODE_DEFINITION_OR_TABLE.value
    assert not resultado.supports


def test_un_procedimiento_si_sostiene() -> None:
    resultado = check_support(
        CLAIM,
        _frag(texto=f"B1234 throttle position sensor.\n{PASOS}"),
        signal="throttle_position",
        expected_dtc=("B1234",),
    )
    assert resultado.supports
    assert resultado.dtc_requirement == DtcRequirement.DTC_REQUIRED.value


# --- 3 · Lista de códigos vacía -------------------------------------------------


def test_el_requisito_se_lee_de_la_declaracion_y_no_del_nombre() -> None:
    """La regla no conoce ningún diagnóstico: solo si está declarado y si trae códigos."""
    mapa = {"X_declarado_con_codigos": ("B1234",), "Y_declarado_sin_codigos": ()}
    assert dtc_requirement("X_declarado_con_codigos", mapa) is DtcRequirement.DTC_REQUIRED
    assert dtc_requirement("Y_declarado_sin_codigos", mapa) is DtcRequirement.DTC_NOT_APPLICABLE
    assert dtc_requirement("Z_no_declarado", mapa) is DtcRequirement.DTC_MAPPING_UNAVAILABLE


def test_dos_diagnosticos_declarados_igual_reciben_el_mismo_requisito() -> None:
    """Prueba de ausencia de lógica de caso: `F00_normal` no recibe trato propio."""
    mapa = {"F00_normal": (), "cualquier_otra_cosa": ()}
    assert dtc_requirement("F00_normal", mapa) == dtc_requirement("cualquier_otra_cosa", mapa)


def test_sin_codigos_aplicables_no_se_sostiene_y_se_declara() -> None:
    """El defecto que v2.2 corrige: la puerta desaparecía en vez de declararse.

    Sin esta regla, este fragmento sostenía la afirmación pasando solo tres de las
    cuatro condiciones. Ver `docs/experiments/hallazgo-puerta-dtc-ausente.md`.
    """
    resultado = check_support(
        CLAIM,
        _frag(texto=f"B1234 throttle position sensor.\n{PASOS}"),
        signal="throttle_position",
        expected_dtc=(),
        requisito=DtcRequirement.DTC_NOT_APPLICABLE,
    )
    assert not resultado.supports
    assert resultado.dtc_requirement == DtcRequirement.DTC_NOT_APPLICABLE.value


def test_codigos_no_declarados_se_distinguen_de_codigos_inaplicables() -> None:
    """Dos motivos distintos para dos situaciones distintas, no un silencio común."""
    frag = _frag(texto=f"B1234 throttle position sensor.\n{PASOS}")
    sin_declarar = check_support(
        CLAIM,
        frag,
        signal="throttle_position",
        expected_dtc=(),
        requisito=DtcRequirement.DTC_MAPPING_UNAVAILABLE,
    )
    no_aplica = check_support(
        CLAIM,
        frag,
        signal="throttle_position",
        expected_dtc=(),
        requisito=DtcRequirement.DTC_NOT_APPLICABLE,
    )
    assert not sin_declarar.supports and not no_aplica.supports
    assert sin_declarar.reason != no_aplica.reason
    assert sin_declarar.dtc_requirement != no_aplica.dtc_requirement


def test_el_requisito_opcional_no_descalifica_pero_se_registra() -> None:
    """Categoría definida y **sin uso** hoy. Se prueba para que no se adopte por descuido."""
    resultado = check_support(
        CLAIM,
        _frag(texto=f"B1234 throttle position sensor.\n{PASOS}", dtc=("U0100",)),
        signal="throttle_position",
        expected_dtc=("B1234",),
        requisito=DtcRequirement.DTC_OPTIONAL,
    )
    assert resultado.supports
    assert resultado.carries_expected_dtc is False


# --- 4 · Señal sin correspondencia ---------------------------------------------


def test_una_senal_sin_vocabulario_no_se_convierte_en_soporte() -> None:
    resultado = check_support(
        CLAIM,
        _frag(texto=f"B1234 transmission fluid temperature sensor.\n{PASOS}"),
        signal="transmission_fluid_temperature",
        expected_dtc=("B1234",),
    )
    assert not resultado.supports
    assert resultado.signal_mapping == SIN_CORRESPONDENCIA


# --- 5 · Motor incorrecto, 6 · sin metadatos de motor, 7 · multimotor ------------
# La aplicabilidad la decide la fase de recuperación y llega ya resuelta en el
# campo `applicability`. Estas pruebas fijan el contrato que el verificador
# cumple **hoy**, para que el rediseño de la política de aplicabilidad
# --`docs/experiments/hallazgo-filtro-motor.md`-- se mida contra una referencia
# escrita antes de cambiarla, y no contra el recuerdo de cómo era.


@pytest.mark.parametrize("applicability", ["INCOMPATIBLE", "PARTIAL_MATCH", "UNKNOWN"])
def test_el_verificador_no_filtra_por_aplicabilidad_por_si_mismo(applicability: str) -> None:
    """Contrato actual, declarado: `check_support` **no mira** la aplicabilidad.

    La descarta antes `build_claims`, que solo admite coincidencia exacta. Es el
    mecanismo real, y no el que la documentación anterior atribuía al filtro de
    motor: por eso esta prueba existe y por eso su nombre dice lo que dice.
    """
    resultado = check_support(
        CLAIM,
        _frag(texto=f"B1234 throttle position sensor.\n{PASOS}", applicability=applicability),
        signal="throttle_position",
        expected_dtc=("B1234",),
    )
    assert resultado.supports, "si esto cambia, la política de aplicabilidad se ha movido"


def test_un_fragmento_sin_metadatos_de_motor_llega_igual_al_verificador() -> None:
    """4 175 de 6 158 fragmentos del corpus no declaran motor. Hoy pasan todos."""
    resultado = check_support(
        CLAIM,
        _frag(texto=f"B1234 throttle position sensor.\n{PASOS}", applicability="UNKNOWN"),
        signal="throttle_position",
        expected_dtc=("B1234",),
    )
    assert resultado.supports


# --- 8 · Propagación del motivo al rastro de auditoría --------------------------


def test_el_motivo_no_afirma_haber_comprobado_un_codigo_que_no_comprobo() -> None:
    """El rastro de auditoría decía «y porta el código» sin haber mirado ninguno."""
    resultado = check_support(
        CLAIM,
        _frag(texto=f"B1234 throttle position sensor.\n{PASOS}"),
        signal="throttle_position",
        expected_dtc=(),
        requisito=DtcRequirement.DTC_NOT_APPLICABLE,
    )
    assert "porta el código" not in resultado.reason


def test_el_registro_publica_papel_correspondencia_y_requisito() -> None:
    d = check_support(
        CLAIM,
        _frag(texto=f"B1234 throttle position sensor.\n{PASOS}"),
        signal="throttle_position",
        expected_dtc=("B1234",),
    ).to_dict()
    for campo in ("chunk_role", "signal_mapping", "dtc_requirement", "supports", "reason"):
        assert campo in d, campo
    assert d["dtc_requirement"] == DtcRequirement.DTC_REQUIRED.value


# --- 9 · Regresión: el bypass, reproducido y cerrado ---------------------------


def test_regresion_el_bypass_se_reproduce_bajo_la_regla_anterior() -> None:
    """`EMPTY-DTC-GATE-BYPASS`, reproducido tal como ocurría.

    La regla anterior exigía `DTC_REQUIRED` siempre. Con la lista de códigos vacía
    la comprobación no se ejecutaba, de modo que un fragmento sostenía la
    afirmación cumpliendo tres de las cuatro condiciones. Esta prueba conserva ese
    comportamiento a la vista: sin ella, el cierre del hallazgo descansaría solo en
    la descripción de un registro.
    """
    bypass = check_support(
        CLAIM,
        _frag(texto=f"B1234 throttle position sensor.\n{PASOS}"),
        signal="throttle_position",
        expected_dtc=(),
        requisito=DtcRequirement.DTC_REQUIRED,
    )
    assert bypass.supports
    assert bypass.carries_expected_dtc is None


def test_regresion_el_requisito_derivado_cierra_el_bypass() -> None:
    """Y queda cerrado cuando el requisito se deriva de la declaración.

    Mismo fragmento, misma señal, misma lista vacía: lo único que cambia es de
    dónde sale el requisito. Un diagnóstico que el mapa no declara produce
    `DTC_MAPPING_UNAVAILABLE`, y entonces no hay soporte.
    """
    mapa = {"F01_declarado": ("B1234",)}
    requisito = dtc_requirement("F00_normal", mapa)
    assert requisito is DtcRequirement.DTC_MAPPING_UNAVAILABLE
    cerrado = check_support(
        CLAIM,
        _frag(texto=f"B1234 throttle position sensor.\n{PASOS}"),
        signal="throttle_position",
        expected_dtc=(),
        requisito=requisito,
    )
    assert not cerrado.supports
