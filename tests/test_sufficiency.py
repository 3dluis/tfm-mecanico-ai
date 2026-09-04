"""Verificador de suficiencia y verificación de soporte.

Todo determinista: ni una llamada a un modelo de lenguaje.
"""

from __future__ import annotations

import pytest

from mecanico_ia_exp.abstention.sufficiency import (
    Decision,
    EvidenceVerifier,
    Reason,
    Sufficiency,
    SufficiencyThresholds,
    claim_coverage,
    detect_contradictions,
)
from mecanico_ia_exp.evidence.model import (
    Claim,
    DocumentaryEvidence,
    EvidenceBundle,
    Observation,
    SupportStatus,
)
from mecanico_ia_exp.evidence.support import (
    check_support,
    is_diagnostic_content,
    mentions_signal,
)
from mecanico_ia_exp.rag.vehicle import Applicability

EXACTA = frozenset({Applicability.EXACT_MATCH.value})


def _obs(oid: str = "OBS001", signal: str = "stft_bank1") -> Observation:
    return Observation(
        observation_id=oid,
        signal=signal,
        statistic="mean",
        value=6.2,
        direction="increases",
        importance=0.4,
        session_id="s1",
        window_start_s=120.0,
        window_end_s=239.0,
    )


def _doc(**cambios: object) -> DocumentaryEvidence:
    base: dict[str, object] = {
        "chunk_id": "ch1",
        "document_id": "manual",
        "vehicle_id": "v",
        "text": "DTC P2187 Fuel system too lean at idle. DETECTION CONDITION "
        "PCM monitors short term fuel trim and long term fuel trim.",
        "score": 0.52,
        "applicability": Applicability.EXACT_MATCH.value,
        "document_type": "WORKSHOP_MANUAL",
        "authority_level": "A",
        "publisher": "Mazda",
        "section": "DTC P2187 [ZJ, Z6]",
        "page_start": 1,
        "dtc_codes": ("P2187",),
    }
    base.update(cambios)
    return DocumentaryEvidence(**base)  # type: ignore[arg-type]


def _bundle(**cambios: object) -> EvidenceBundle:
    base: dict[str, object] = {
        "case_id": "c1",
        "vehicle_id": "v",
        "predicted_class": "F01_vacuum_leak",
        "model_confidence": 0.9,
        "calibrated_confidence": 0.9,
        "observations": [_obs()],
        "documents": [_doc(), _doc(chunk_id="ch2")],
        "claims": [Claim("C01", "texto", ("OBS001",), ("ch1", "ch2"), SupportStatus.SUPPORTED)],
    }
    base.update(cambios)
    return EvidenceBundle(**base)  # type: ignore[arg-type]


# --------------------------------------------------------------- soporte


def test_se_reconoce_la_senal_por_el_vocabulario_del_manual() -> None:
    """El manual dice «short term fuel trim», no «stft_bank1»."""
    assert mentions_signal("PCM monitors short term fuel trim", "stft_bank1")
    assert mentions_signal("the HO2S signal", "oxygen_sensor")
    assert mentions_signal("engine coolant temperature", "coolant_temperature")
    assert not mentions_signal("brake pedal position", "oxygen_sensor")


def test_una_pareja_de_correlacion_se_reconoce_por_cualquiera_de_sus_señales() -> None:
    assert mentions_signal("mass air flow sensor", "rpm+maf")


def test_una_descripcion_de_funcionamiento_no_es_contenido_diagnostico() -> None:
    """E12 lo midió: la recuperación devuelve arriba «HO2S FUNCTION», que explica
    cómo funciona el sensor y no sostiene que esté averiado."""
    funcion = _doc(
        section="HEATED OXYGEN SENSOR (HO2S) FUNCTION",
        text="Detects the oxygen concentration in the exhaust gas.",
        dtc_codes=(),
    )
    assert not is_diagnostic_content(funcion)


def test_un_procedimiento_con_dtc_es_contenido_diagnostico() -> None:
    assert is_diagnostic_content(_doc())


def test_un_fragmento_que_no_menciona_la_senal_no_sostiene_la_afirmacion() -> None:
    claim = Claim("C01", "el ajuste está desplazado", ("OBS001",))
    ajeno = _doc(text="Inspect the brake fluid level and the parking brake travel.")
    resultado = check_support(claim, ajeno, signal="stft_bank1")
    assert not resultado.supports
    assert "no menciona la señal" in resultado.reason


def test_un_fragmento_sin_el_codigo_esperado_no_sostiene_la_afirmacion() -> None:
    """Citar no es sostener: el fragmento puede hablar de la señal y de otro fallo."""
    claim = Claim("C01", "texto", ("OBS001",))
    otro = _doc(dtc_codes=("P0300",), section="DTC P0300 [ZJ, Z6]")
    resultado = check_support(claim, otro, signal="stft_bank1", expected_dtc=("P2187",))
    assert not resultado.supports
    assert resultado.carries_expected_dtc is False


def test_un_fragmento_pertinente_si_sostiene_la_afirmacion() -> None:
    claim = Claim("C01", "texto", ("OBS001",))
    resultado = check_support(claim, _doc(), signal="stft_bank1", expected_dtc=("P2187",))
    assert resultado.supports
    assert resultado.mentions_signal and resultado.is_diagnostic


# ------------------------------------------------------------- cobertura


def test_la_cobertura_exige_soporte_verificado_y_no_solo_una_cita() -> None:
    """Es la diferencia entre citar y sostener, que es el fallo que se estudia."""
    citada = Claim("C01", "t", ("OBS001",), ("ch1",), SupportStatus.PARTIALLY_SUPPORTED)
    sostenida = Claim("C02", "t", ("OBS001",), ("ch1",), SupportStatus.SUPPORTED)
    assert claim_coverage([citada]) == 0.0
    assert claim_coverage([sostenida]) == 1.0
    assert claim_coverage([citada, sostenida]) == 0.5


def test_sin_afirmaciones_la_cobertura_es_cero() -> None:
    assert claim_coverage([]) == 0.0


# --------------------------------------------------------- contradicciones


def test_se_detecta_una_afirmacion_que_cita_evidencia_no_aplicable() -> None:
    bundle = _bundle(
        documents=[_doc(applicability=Applicability.INCOMPATIBLE.value)],
        claims=[Claim("C01", "t", ("OBS001",), ("ch1",), SupportStatus.SUPPORTED)],
    )
    contradicciones = detect_contradictions(bundle)
    assert contradicciones
    assert "no aplicable" in contradicciones[0]


def test_una_afirmacion_marcada_como_contradicha_se_detecta() -> None:
    bundle = _bundle(claims=[Claim("C01", "t", ("OBS001",), ("ch1",), SupportStatus.CONTRADICTED)])
    assert detect_contradictions(bundle)


# ------------------------------------------------------------ verificador


def test_supported_evidence() -> None:
    """Con todo en orden, la decisión es explicar."""
    veredicto = EvidenceVerifier().verify(_bundle())
    assert veredicto.sufficiency is Sufficiency.SUPPORTED
    assert veredicto.decision is Decision.EXPLAIN
    assert not veredicto.reasons


def test_insufficient_evidence_sin_documentacion_aplicable() -> None:
    """El caso central: se retira la evidencia y la decisión cambia."""
    veredicto = EvidenceVerifier().verify(_bundle(documents=[], claims=[]))
    assert veredicto.sufficiency is Sufficiency.INSUFFICIENT_EVIDENCE
    assert veredicto.decision is Decision.ABSTAIN
    assert Reason.NO_DOCUMENTARY_EVIDENCE in veredicto.reasons


def test_abstention_por_confianza_insuficiente() -> None:
    veredicto = EvidenceVerifier().verify(_bundle(model_confidence=0.3, calibrated_confidence=0.3))
    assert Reason.LOW_CONFIDENCE in veredicto.reasons
    assert veredicto.decision is Decision.ABSTAIN


def test_sin_observaciones_no_hay_explicacion_que_sostener() -> None:
    veredicto = EvidenceVerifier().verify(_bundle(observations=[]))
    assert Reason.NO_OBSERVATIONAL_EVIDENCE in veredicto.reasons


def test_se_devuelven_todos_los_motivos_y_no_solo_el_primero() -> None:
    """Saber que falla una condición no es lo mismo que saber que fallan cuatro."""
    veredicto = EvidenceVerifier().verify(
        _bundle(
            model_confidence=0.1,
            calibrated_confidence=0.1,
            observations=[],
            documents=[],
            claims=[],
        )
    )
    assert len(veredicto.reasons) >= 3


def test_el_criterio_es_conjuntivo_y_no_compensable() -> None:
    """Una confianza altísima no compensa la ausencia de documentación.

    Con un promedio ponderado, 0,99 de confianza taparía un cero en cobertura.
    """
    veredicto = EvidenceVerifier().verify(
        _bundle(model_confidence=0.99, calibrated_confidence=0.99, documents=[], claims=[])
    )
    assert veredicto.decision is Decision.ABSTAIN


def test_cinco_fragmentos_del_mismo_documento_no_son_cinco_fuentes() -> None:
    bundle = _bundle(
        documents=[_doc(chunk_id=f"ch{i}") for i in range(5)],
    )
    assert len(bundle.distinct_sources(EXACTA)) == 1


def test_la_evidencia_no_aplicable_no_cuenta_como_apoyo() -> None:
    bundle = _bundle(
        documents=[
            _doc(chunk_id="a", applicability=Applicability.PARTIAL_MATCH.value),
            _doc(chunk_id="b", applicability=Applicability.UNKNOWN.value),
        ],
        claims=[],
    )
    veredicto = EvidenceVerifier().verify(bundle)
    assert Reason.NO_DOCUMENTARY_EVIDENCE in veredicto.reasons


def test_la_politica_de_compatibilidad_debe_declararse() -> None:
    """COMPATIBLE solo vale bajo política explícita."""
    bundle = _bundle(
        documents=[
            _doc(chunk_id="a", applicability=Applicability.COMPATIBLE.value),
            _doc(chunk_id="b", applicability=Applicability.COMPATIBLE.value),
        ],
    )
    estricto = EvidenceVerifier(SufficiencyThresholds())
    permisivo = EvidenceVerifier(SufficiencyThresholds(allow_compatible_applicability=True))
    assert Reason.NO_DOCUMENTARY_EVIDENCE in estricto.verify(bundle).reasons
    assert Reason.NO_DOCUMENTARY_EVIDENCE not in permisivo.verify(bundle).reasons


def test_se_usa_la_confianza_calibrada_cuando_existe() -> None:
    """E6 midió que el bosque está infraconfiado; sin calibrar, el criterio se
    abstendría de más."""
    bundle = _bundle(model_confidence=0.55, calibrated_confidence=0.88)
    assert bundle.confidence == pytest.approx(0.88)
    assert EvidenceVerifier().verify(bundle).decision is Decision.EXPLAIN


def test_sin_calibrar_se_usa_la_confianza_cruda() -> None:
    bundle = _bundle(model_confidence=0.55, calibrated_confidence=None)
    assert bundle.confidence == pytest.approx(0.55)


def test_el_veredicto_explica_que_falta_y_no_solo_que_falla() -> None:
    """Un rechazo que no dice qué falta no es auditable."""
    veredicto = EvidenceVerifier().verify(_bundle(documents=[], claims=[]))
    assert veredicto.missing_evidence
    assert any("documental" in m for m in veredicto.missing_evidence)


def test_el_veredicto_registra_todas_las_señales_del_criterio() -> None:
    señales = EvidenceVerifier().verify(_bundle()).signals
    for clave in (
        "confidence",
        "n_observations",
        "n_documents_applicable",
        "n_distinct_sources",
        "best_retrieval_score",
        "claim_coverage",
    ):
        assert clave in señales


# ------------------------------------------------------------ trazabilidad


def test_una_observacion_se_rastrea_hasta_la_ventana_del_dato() -> None:
    traza = _obs().trace()
    assert "stft_bank1" in traza and "sesión s1" in traza and "120-239 s" in traza


def test_un_fragmento_se_cita_con_editor_y_pagina() -> None:
    traza = _doc().trace()
    assert "Mazda" in traza and "página 1" in traza and "ch1" in traza


# ------------------------------------------- umbrales calibrados y no elegidos


def test_el_umbral_de_confianza_esta_calibrado_sobre_validacion() -> None:
    """0,80 es el umbral más bajo con precisión >= 0,93 en validación.

    No es una cifra redonda elegida a ojo: sale de un barrido documentado en el
    docstring de SufficiencyThresholds, donde consta además que ningún umbral
    alcanza 0,95 --la precisión se estanca en 0,93-0,94--.
    """
    assert SufficiencyThresholds().min_confidence == 0.80


def test_el_umbral_de_puntuacion_esta_desactivado_a_proposito() -> None:
    """La puntuación de similitud NO discrimina el soporte.

    Medido: los fragmentos que sostienen una afirmación tienen mediana 0,459 y
    los que no, 0,443. El 38 % de los que no sostienen puntúan por encima de la
    mediana de los que sí. Un umbral ahí filtraría por azar.
    """
    assert SufficiencyThresholds().min_retrieval_score == 0.0


def test_una_puntuacion_baja_no_impide_explicar_por_si_sola() -> None:
    """Con el umbral desactivado, lo que decide es el soporte verificado."""
    bundle = _bundle(documents=[_doc(score=0.05), _doc(chunk_id="ch2", score=0.05)])
    assert EvidenceVerifier().verify(bundle).decision is Decision.EXPLAIN


# --------------------------------------------- las cuatro condiciones de corpus


def test_distractor_handling() -> None:
    """Un procedimiento de otro motor no sostiene, aunque hable de lo mismo.

    Es la prueba más dura del diseño: mismo código de diagnóstico, contenido casi
    idéntico, motor inaplicable. Un sistema guiado por similitud lo aceptaría.
    """
    distractor = _doc(
        chunk_id="lf1",
        applicability=Applicability.PARTIAL_MATCH.value,
        section="DTC P2187 [LF]",
    )
    bundle = _bundle(
        documents=[
            distractor,
            _doc(chunk_id="lf2", applicability=Applicability.PARTIAL_MATCH.value),
        ],
        claims=[],
    )
    veredicto = EvidenceVerifier().verify(bundle)
    assert veredicto.decision is Decision.ABSTAIN
    assert Reason.NO_DOCUMENTARY_EVIDENCE in veredicto.reasons


def test_evidencia_parcial_no_basta() -> None:
    """Que el corpus mencione el código no es que documente el diagnóstico.

    Una tabla de DTC dice que ese código existe; no dice cómo se comprueba. La
    verificación de soporte la rechaza por no ser contenido diagnóstico.
    """
    tabla = _doc(
        chunk_id="tabla",
        section="DTC TABLE [ZJ, Z6]",
        text="P2187 Fuel system too lean at idle ON 2 Fuel system",
        dtc_codes=("P2187",),
    )
    claim = Claim("C01", "el ajuste está desplazado", ("OBS001",))
    resultado = check_support(claim, tabla, signal="stft_bank1", expected_dtc=("P2187",))
    assert not resultado.supports


def test_las_cuatro_condiciones_se_distinguen_por_lo_que_falta() -> None:
    """Cada condición produce un motivo de abstención distinto, y eso importa:
    un veredicto que dijera siempre lo mismo no permitiría saber qué faltó."""
    sin_nada = EvidenceVerifier().verify(_bundle(documents=[], claims=[]))
    solo_inaplicable = EvidenceVerifier().verify(
        _bundle(
            documents=[_doc(applicability=Applicability.PARTIAL_MATCH.value)],
            claims=[],
        )
    )
    sin_soporte = EvidenceVerifier().verify(
        _bundle(claims=[Claim("C01", "t", ("OBS001",), (), SupportStatus.PARTIALLY_SUPPORTED)])
    )
    assert Reason.NO_DOCUMENTARY_EVIDENCE in sin_nada.reasons
    assert Reason.NO_DOCUMENTARY_EVIDENCE in solo_inaplicable.reasons
    assert Reason.LOW_CLAIM_COVERAGE in sin_soporte.reasons


# ------------------------------------------ barrido del umbral (E15b, RX-04)


def test_el_barrido_del_umbral_no_puede_tocar_el_conjunto_de_test() -> None:
    """Un umbral seleccionado con el test convierte la evaluación final en una
    descripción de lo ya visto. La garantía se comprueba en el código, no se
    confía a la disciplina de quien lo ejecuta."""
    from pathlib import Path

    fuente = Path("src/mecanico_ia_exp/experiments/threshold_runner.py").read_text(encoding="utf-8")
    assert 'load_partition("test"' not in fuente
    assert 'load_partition("validation"' in fuente


def test_el_registro_del_barrido_declara_que_no_uso_el_test() -> None:
    import json
    from pathlib import Path

    ruta = Path("experiments/E15b_barrido_umbral.json")
    if not ruta.is_file():
        pytest.skip("el barrido no se ha ejecutado en esta máquina")
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    assert datos["test_used"] is False
    assert datos["partition"] == "validation"
    # El criterio declara que no es un pre-registro ciego. Ocultarlo sería peor
    # que la propia limitación.
    assert datos["criterion"]["blind_preregistration"] is False
    assert datos["n_sessions"] == 12
