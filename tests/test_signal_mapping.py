"""Ausencia de correspondencia de señal, declarada en lugar de silenciada.

El verificador traduce el identificador de una señal al vocabulario del manual
con un diccionario construido a mano. Para una señal que no está en él, un fallo
de coincidencia significaba lo mismo que «el manual no habla de esto», y son dos
cosas distintas: la segunda es un resultado sobre el corpus, la primera es un
límite del instrumento.
"""

from __future__ import annotations

from mecanico_ia_exp.evidence.model import Claim, DocumentaryEvidence
from mecanico_ia_exp.evidence.support import (
    MAPEADA,
    SIN_CORRESPONDENCIA,
    TERMINOS_SENAL,
    check_support,
    signal_mapping,
)

CLAIM = Claim(claim_id="C01", text="afirmación")

PROCEDIMIENTO = DocumentaryEvidence(
    chunk_id="ch",
    document_id="doc",
    vehicle_id="v",
    text=(
        "B1234 transmission fluid temperature sensor circuit.\n"
        "Turn the ignition switch off. Disconnect the sensor connector. Measure the "
        "resistance. Is the resistance within specification?\nYes Go to the next step.\n"
        "No Replace the sensor."
    ),
    score=0.9,
    applicability="EXACT_MATCH",
    document_type="WORKSHOP_MANUAL",
    dtc_codes=("B1234",),
    section="DTC B1234 [ZJ, Z6]",
)


def test_el_diccionario_cubre_doce_senales() -> None:
    """Cifra declarada en la memoria y en `docs/methodology/limitacion-vocabulario-senales.md`."""
    assert len(TERMINOS_SENAL) == 12


def test_una_senal_del_conjunto_esta_mapeada() -> None:
    assert signal_mapping("ltft_bank1") == MAPEADA
    assert signal_mapping("rpm+maf") == MAPEADA


def test_una_senal_ajena_al_diccionario_se_declara_sin_correspondencia() -> None:
    assert signal_mapping("transmission_fluid_temperature") == SIN_CORRESPONDENCIA
    assert signal_mapping("rpm+transmission_fluid_temperature") == SIN_CORRESPONDENCIA


def test_sin_correspondencia_no_se_convierte_en_soporte_silencioso() -> None:
    """El fragmento es un procedimiento válido y porta el código esperado.

    Aun así no sostiene, porque el verificador no puede comprobar que hable de la
    señal. Lo que importa es que **lo dice**, en vez de devolver el mismo «no
    menciona la señal» que devolvería si el manual callara de verdad.
    """
    resultado = check_support(
        CLAIM,
        PROCEDIMIENTO,
        signal="transmission_fluid_temperature",
        expected_dtc=("B1234",),
    )
    assert not resultado.supports
    assert resultado.signal_mapping == SIN_CORRESPONDENCIA
    assert SIN_CORRESPONDENCIA in resultado.reason
    assert "no es prueba de ausencia" in resultado.reason


def test_se_distingue_de_la_ausencia_real_de_evidencia() -> None:
    """Mismo fragmento, señal mapeada de la que el manual no habla.

    Aquí el veredicto negativo **sí** es un resultado sobre el corpus, y el
    registro lo separa del caso anterior.
    """
    resultado = check_support(
        CLAIM, PROCEDIMIENTO, signal="throttle_position", expected_dtc=("B1234",)
    )
    assert not resultado.supports
    assert resultado.signal_mapping == MAPEADA
    assert not resultado.mentions_signal
    assert SIN_CORRESPONDENCIA not in resultado.reason


def test_el_registro_publica_la_correspondencia() -> None:
    """Queda en el artefacto, no solo en memoria: es auditable después."""
    d = check_support(
        CLAIM, PROCEDIMIENTO, signal="transmission_fluid_temperature", expected_dtc=("B1234",)
    ).to_dict()
    assert d["signal_mapping"] == SIN_CORRESPONDENCIA
