"""Ablaciones de E18 y selector de política del verificador.

Todo determinista y sin infraestructura: ni base de datos, ni modelo de
embeddings, ni bosque entrenado. Lo que estas pruebas interrogan son **reglas**
--qué observaciones se eligen, qué fragmentos pasan los filtros, qué decide cada
criterio degradado, cómo se nombra el artefacto y con qué denominadores se cuenta--
y ninguna de ellas necesita infraestructura para ser correcta o incorrecta.

El pre-registro vinculante es `docs/methodology/preregistro-e18-ablaciones.md`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
import pytest

from mecanico_ia_exp.abstention.sufficiency import (
    VERIFIER_VERSION,
    Decision,
    Reason,
    Sufficiency,
    SufficiencyThresholds,
    SufficiencyVerdict,
)
from mecanico_ia_exp.config import paths
from mecanico_ia_exp.evidence.assembly import observations_from_attribution
from mecanico_ia_exp.evidence.model import Claim, DocumentaryEvidence, EvidenceBundle
from mecanico_ia_exp.evidence.support import DtcRequirement
from mecanico_ia_exp.experiments.ablation_runner import (
    ABLACIONES,
    FUNCION_EXPLICADA_A1,
    atribucion_por_desviacion,
    decision_a3,
    decision_a4,
    desviaciones_tipificadas,
    documento_ablacion,
    estadisticos_sin_fallo,
    fila_de,
    recuperar_lexico,
    resumen_abstencion,
    veredicto_de_ablacion,
)
from mecanico_ia_exp.experiments.registro import CAMPOS_OBLIGATORIOS, escribir
from mecanico_ia_exp.experiments.retrieval_runner import ESTRATEGIAS, PROFUNDIDAD, TOP_K
from mecanico_ia_exp.experiments.sufficiency_runner import (
    CasoVerificado,
    documento_suficiencia,
    modo_de,
    requisito_dtc,
    sufijo_artefacto,
    validar_politica,
)
from mecanico_ia_exp.rag.store import RetrievedChunk
from mecanico_ia_exp.rag.vehicle import Applicability

EXACTA = frozenset({Applicability.EXACT_MATCH.value})

DESCRIPTORES = (
    "stft_bank1_mean",
    "maf_mean",
    "coolant_temperature_mean",
    "rpm_mean",
)


def _entrenamiento() -> tuple[npt.NDArray[np.float64], npt.NDArray[np.str_]]:
    """Cuatro ventanas sin fallo y dos con fallo, con valores elegidos a mano.

    Las de fallo llevan valores extremos a propósito: si entraran en la
    referencia, la media y la desviación cambiarían y el orden por |z| con ellas.
    """
    x = np.array(
        [
            [0.0, 10.0, 80.0, 800.0],
            [1.0, 10.0, 82.0, 800.0],
            [0.0, 10.0, 80.0, 820.0],
            [1.0, 10.0, 82.0, 820.0],
            [99.0, 999.0, 10.0, 5000.0],
            [-99.0, -999.0, 200.0, 0.0],
        ],
        dtype=np.float64,
    )
    y = np.array(
        [
            "F00_normal",
            "F00_normal",
            "F00_normal",
            "F00_normal",
            "F01_vacuum_leak",
            "F01_vacuum_leak",
        ],
        dtype=np.str_,
    )
    return x, y


# ---------------------------------------------------------------------------
# A1: observaciones por desviación tipificada
# ---------------------------------------------------------------------------


def test_a1_estadisticos_solo_de_la_clase_sin_fallo() -> None:
    x, y = _entrenamiento()
    media, desviacion = estadisticos_sin_fallo(x, y)
    assert media.tolist() == [0.5, 10.0, 81.0, 810.0]
    assert desviacion.tolist() == [0.5, 0.0, 1.0, 10.0]


def test_a1_sin_clase_sin_fallo_falla_en_lugar_de_inventar_referencia() -> None:
    x, _ = _entrenamiento()
    y = np.array(["F01_vacuum_leak"] * 6, dtype=np.str_)
    with pytest.raises(ValueError, match="F00_normal"):
        estadisticos_sin_fallo(x, y)


def test_a1_descriptor_constante_no_se_convierte_en_infinito() -> None:
    """Un descriptor sin variación en la normalidad no distingue nada: z = 0."""
    x, y = _entrenamiento()
    media, desviacion = estadisticos_sin_fallo(x, y)
    z = desviaciones_tipificadas(np.array([2.5, 1000.0, 78.0, 815.0]), media, desviacion)
    assert z[1] == 0.0
    assert np.isfinite(z).all()


def _atribucion_a1() -> Any:
    x, y = _entrenamiento()
    media, desviacion = estadisticos_sin_fallo(x, y)
    return atribucion_por_desviacion(
        x_caso=np.array([2.5, 1000.0, 78.0, 815.0], dtype=np.float64),
        media=media,
        desviacion=desviacion,
        feature_names=DESCRIPTORES,
        case_id="s1@120s",
        model_id="rf_prueba",
        predicted_class="F01_vacuum_leak",
        confidence=0.91,
        session_id="s1",
        window_start_s=120.0,
        window_end_s=239.0,
        seed=20260901,
    )


def test_a1_elige_las_tres_observaciones_por_valor_absoluto_de_z() -> None:
    """|z| = 4,0 (stft), 3,0 (refrigerante), 0,5 (régimen), 0,0 (caudalímetro)."""
    atribucion = _atribucion_a1()
    assert [a.importance for a in atribucion.top(4)] == [4.0, -3.0, 0.5, 0.0]
    observaciones = observations_from_attribution(atribucion)
    assert [o.signal for o in observaciones] == ["stft_bank1", "coolant_temperature", "rpm"]


def test_a1_la_direccion_sale_del_signo_de_la_desviacion() -> None:
    por_senal = {a.signal: a for a in _atribucion_a1().attributions}
    assert por_senal["stft_bank1"].direction == "increases"
    assert por_senal["coolant_temperature"].direction == "decreases"
    # Contribución indistinguible de cero: no observa nada y se descarta después.
    assert por_senal["maf"].direction == "neutral"


def test_a1_el_sustituto_declara_que_es_una_ablacion() -> None:
    """Un artefacto de A1 no puede pasar por una atribución de Shapley."""
    atribucion = _atribucion_a1()
    assert atribucion.explained_function == FUNCION_EXPLICADA_A1
    assert "ablacion_A1" in atribucion.explained_function
    assert atribucion.explainer.startswith("ablacion_A1")
    # Huella de la referencia: identifica contra qué se tipificó.
    assert len(atribucion.background_hash) == 16


def test_a1_conserva_la_estructura_que_assemble_espera() -> None:
    """Mismos campos que la atribución canónica: `assemble` no se toca."""
    from mecanico_ia_exp.xai.attribution import CaseAttribution

    atribucion = _atribucion_a1()
    assert isinstance(atribucion, CaseAttribution)
    assert set(atribucion.to_dict()) == {
        "explanation_id",
        "case_id",
        "model_id",
        "explained_function",
        "predicted_class",
        "confidence",
        "session_id",
        "window_start_s",
        "window_end_s",
        "explainer",
        "seed",
        "background_hash",
        "attributions",
    }


# ---------------------------------------------------------------------------
# A2: ruta léxica
# ---------------------------------------------------------------------------


def _chunk(
    chunk_id: str,
    *,
    dtc: tuple[str, ...] = ("P2187",),
    document_type: str = "WORKSHOP_MANUAL",
    score: float = 0.5,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=f"doc_{chunk_id}",
        vehicle_id="mazda-3-bk-2007",
        text="DETECTION CONDITION fuel trim",
        score=score,
        rank=1,
        chapter=None,
        section="DTC P2187",
        page_start=1,
        page_end=1,
        dtc_codes=dtc,
        vehicle_system="engine",
        engine_codes=("Z6",),
        source_file="srvc/x.pdf",
        document_type=document_type,
        authority_level="A",
        publisher="Mazda",
    )


class _AlmacenDoble:
    """Doble del almacén: anota la llamada y devuelve fragmentos fijos.

    No tiene `search`: si la ablación vectorizara la consulta, el doble fallaría
    por atributo inexistente, que es la forma más directa de comprobar que no lo
    hace.
    """

    def __init__(self, resultados: list[RetrievedChunk]) -> None:
        self.resultados = resultados
        self.llamadas: list[dict[str, Any]] = []

    def search_lexical(
        self,
        query_text: str,
        *,
        vehicle_id: str,
        top_k: int = 10,
        engine_codes: tuple[str, ...] | None = None,
        language: str = "en",
    ) -> list[RetrievedChunk]:
        self.llamadas.append(
            {
                "query_text": query_text,
                "vehicle_id": vehicle_id,
                "top_k": top_k,
                "engine_codes": engine_codes,
                "language": language,
            }
        )
        return list(self.resultados)


CASO_A2: dict[str, Any] = {
    "case_id": "C05_vacuum_leak",
    "fault_id": "F01_vacuum_leak",
    "query": "  Fuel trims   persistently positive\n  at idle ",
    "query_es": "Ajustes de combustible positivos en ralentí",
}


def test_a2_usa_la_busqueda_lexica_con_los_mismos_filtros_y_profundidad() -> None:
    doble = _AlmacenDoble([_chunk("ch1")])
    recuperar_lexico(
        store=doble,
        caso=CASO_A2,
        vehicle_id="mazda-3-bk-2007",
        engine_code="Z6",
        dtc_codes=("P2187",),
    )
    (llamada,) = doble.llamadas
    # La consulta es el texto del caso, normalizado igual que en la ruta semántica.
    assert llamada["query_text"] == "Fuel trims persistently positive at idle"
    assert llamada["vehicle_id"] == "mazda-3-bk-2007"
    assert llamada["top_k"] == PROFUNDIDAD
    assert llamada["engine_codes"] == ("Z6", "ZJ")


def test_a2_respeta_la_desactivacion_del_filtro_de_motor() -> None:
    doble = _AlmacenDoble([_chunk("ch1")])
    recuperar_lexico(
        store=doble,
        caso=CASO_A2,
        vehicle_id="v",
        engine_code="Z6",
        dtc_codes=(),
        apply_engine_filter=False,
    )
    assert doble.llamadas[0]["engine_codes"] is None


def test_a2_consulta_en_espanol_usa_el_texto_traducido() -> None:
    doble = _AlmacenDoble([])
    recuperar_lexico(
        store=doble, caso=CASO_A2, vehicle_id="v", engine_code="Z6", dtc_codes=(), language="es"
    )
    assert doble.llamadas[0]["query_text"] == CASO_A2["query_es"]
    assert doble.llamadas[0]["language"] == "es"


def test_a2_filtra_por_codigos_del_diagnostico_y_por_exclusiones() -> None:
    doble = _AlmacenDoble(
        [
            _chunk("ch_excluido", score=1.0),
            _chunk("ch1", score=0.3),
            _chunk("ch2", document_type="DTC_DOCUMENTATION", score=0.9),
            _chunk("ch_sin_codigo", dtc=(), score=0.8),
        ]
    )
    resultados = recuperar_lexico(
        store=doble,
        caso=CASO_A2,
        vehicle_id="v",
        engine_code="Z6",
        dtc_codes=("P2187",),
        exclude_chunks=("ch_excluido",),
    )
    # El procedimiento de taller va delante de la tabla de códigos: la
    # reordenación por autoridad es la misma que la de la estrategia guiada.
    assert [r.chunk_id for r in resultados] == ["ch1", "ch2"]
    assert [r.rank for r in resultados] == [1, 2]


def test_a2_sin_codigos_declarados_no_filtra_por_codigos() -> None:
    doble = _AlmacenDoble(
        [
            _chunk("ch1", score=0.3),
            _chunk("ch2", document_type="DTC_DOCUMENTATION", score=0.9),
            _chunk("ch_sin_codigo", dtc=(), score=0.8),
        ]
    )
    resultados = recuperar_lexico(
        store=doble, caso=CASO_A2, vehicle_id="v", engine_code="Z6", dtc_codes=()
    )
    assert [r.chunk_id for r in resultados] == ["ch1", "ch_sin_codigo", "ch2"]


def test_a2_recorta_al_mismo_top_k_que_la_estrategia_guiada() -> None:
    doble = _AlmacenDoble([_chunk(f"ch{i}", score=1.0 - i / 100) for i in range(TOP_K + 5)])
    resultados = recuperar_lexico(
        store=doble, caso=CASO_A2, vehicle_id="v", engine_code="Z6", dtc_codes=("P2187",)
    )
    assert len(resultados) == TOP_K


def test_a2_no_altera_las_estrategias_de_e12() -> None:
    """E12 está medido y publicado: su conjunto de estrategias no se amplía."""
    assert ESTRATEGIAS == (
        "semantic",
        "semantic+engine",
        "semantic+authority",
        "hybrid",
        "diagnosis-guided",
    )


# ---------------------------------------------------------------------------
# A3 y A4: reglas de decisión
# ---------------------------------------------------------------------------


def _bundle(*, confianza: float = 0.95, aplicables: int = 2) -> EvidenceBundle:
    documentos = [
        DocumentaryEvidence(
            chunk_id=f"ch{i}",
            document_id=f"doc{i}",
            vehicle_id="v",
            text="DETECTION CONDITION fuel trim",
            score=0.5,
            applicability=Applicability.EXACT_MATCH.value,
        )
        for i in range(aplicables)
    ]
    return EvidenceBundle(
        case_id="s1@120s",
        vehicle_id="v",
        predicted_class="F01_vacuum_leak",
        model_confidence=0.7,
        calibrated_confidence=confianza,
        documents=documentos,
        claims=[Claim("C01", "texto")],
    )


def _veredicto(
    decision: Decision,
    *,
    aplicables: int = 2,
    cobertura: float = 0.0,
    confianza: float = 0.95,
    case_id: str = "s1@120s",
    motivos: list[Reason] | None = None,
) -> SufficiencyVerdict:
    return SufficiencyVerdict(
        case_id=case_id,
        sufficiency=(
            Sufficiency.SUPPORTED
            if decision is Decision.EXPLAIN
            else Sufficiency.INSUFFICIENT_EVIDENCE
        ),
        decision=decision,
        reasons=motivos if motivos is not None else [Reason.LOW_CLAIM_COVERAGE],
        signals={
            "confidence": confianza,
            "n_documents_applicable": aplicables,
            "claim_coverage": cobertura,
        },
    )


@pytest.mark.parametrize(
    ("aplicables", "esperado"),
    [(0, Decision.ABSTAIN), (1, Decision.EXPLAIN), (7, Decision.EXPLAIN)],
)
def test_a3_decide_solo_por_existencia_de_fragmento_aplicable(
    aplicables: int, esperado: Decision
) -> None:
    decision, motivos = decision_a3(aplicables)
    assert decision is esperado
    assert motivos == ([] if esperado is Decision.EXPLAIN else [Reason.NO_DOCUMENTARY_EVIDENCE])


def test_a3_explica_donde_el_criterio_compuesto_se_abstiene() -> None:
    """Es el contraste que la ablación mide: siete fragmentos y cobertura 0,00."""
    canonico = _veredicto(Decision.ABSTAIN, aplicables=7, cobertura=0.0)
    veredicto = veredicto_de_ablacion(
        "A3",
        bundle=_bundle(aplicables=7),
        canonico=canonico,
        umbrales=SufficiencyThresholds(),
    )
    assert veredicto.decision is Decision.EXPLAIN
    assert veredicto.sufficiency is Sufficiency.SUPPORTED
    assert veredicto.reasons == []
    # Las señales medidas se conservan: la ablación cambia la regla, no la medida.
    assert veredicto.signals == canonico.signals


@pytest.mark.parametrize(
    ("confianza", "esperado"),
    [(0.9, Decision.EXPLAIN), (0.79, Decision.EXPLAIN), (0.7899, Decision.ABSTAIN)],
)
def test_a4_decide_solo_por_la_confianza_calibrada(confianza: float, esperado: Decision) -> None:
    decision, motivos = decision_a4(confianza, min_confidence=0.79)
    assert decision is esperado
    assert motivos == ([] if esperado is Decision.EXPLAIN else [Reason.LOW_CONFIDENCE])


def test_a4_ignora_cobertura_fragmentos_y_contradicciones() -> None:
    canonico = _veredicto(Decision.ABSTAIN, aplicables=0, cobertura=0.0)
    veredicto = veredicto_de_ablacion(
        "A4",
        bundle=_bundle(confianza=0.95, aplicables=0),
        canonico=canonico,
        umbrales=SufficiencyThresholds(),
    )
    assert veredicto.decision is Decision.EXPLAIN


def test_a4_se_abstiene_cuando_la_confianza_no_alcanza_el_umbral() -> None:
    canonico = _veredicto(Decision.EXPLAIN, aplicables=5, cobertura=1.0)
    veredicto = veredicto_de_ablacion(
        "A4",
        bundle=_bundle(confianza=0.60, aplicables=5),
        canonico=canonico,
        umbrales=SufficiencyThresholds(),
    )
    assert veredicto.decision is Decision.ABSTAIN
    assert veredicto.reasons == [Reason.LOW_CONFIDENCE]
    assert veredicto.missing_evidence == ["confianza 0.600 < 0.79"]


@pytest.mark.parametrize("ablacion", ["A1", "A2"])
def test_a1_y_a2_no_tocan_la_regla_de_decision(ablacion: str) -> None:
    """Cambian la evidencia que llega al verificador, no cómo decide."""
    canonico = _veredicto(Decision.ABSTAIN)
    assert (
        veredicto_de_ablacion(
            ablacion, bundle=_bundle(), canonico=canonico, umbrales=SufficiencyThresholds()
        )
        is canonico
    )


def test_ablacion_desconocida_falla() -> None:
    with pytest.raises(ValueError, match="ablación desconocida"):
        veredicto_de_ablacion(
            "A9",
            bundle=_bundle(),
            canonico=_veredicto(Decision.EXPLAIN),
            umbrales=SufficiencyThresholds(),
        )


# ---------------------------------------------------------------------------
# Política del verificador: validación y nombre del artefacto
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("politica", ["v2.1", "v2.2"])
def test_las_politicas_declaradas_se_aceptan(politica: str) -> None:
    assert validar_politica(politica) == politica


@pytest.mark.parametrize("politica", ["v2.3", "V2.2", "2.2", ""])
def test_una_politica_no_declarada_falla_en_el_borde(politica: str) -> None:
    with pytest.raises(ValueError, match="política de suficiencia desconocida"):
        validar_politica(politica)


def test_la_politica_canonica_no_cambia_el_nombre_del_artefacto() -> None:
    """`E15_suficiencia.json` sigue siendo el de v2.1 en modo oracular."""
    assert sufijo_artefacto("oracle", VERIFIER_VERSION) == ""
    assert sufijo_artefacto("non_oracle", VERIFIER_VERSION) == "_non_oracle"
    assert sufijo_artefacto("adverse", VERIFIER_VERSION) == "_adverse"


@pytest.mark.parametrize(
    ("modo", "esperado"),
    [
        ("oracle", "E15_suficiencia_v2_2"),
        ("non_oracle", "E15_suficiencia_non_oracle_v2_2"),
        ("adverse", "E15_suficiencia_adverse_v2_2"),
    ],
)
def test_una_politica_no_canonica_nunca_sobrescribe_los_registros_vigentes(
    modo: str, esperado: str
) -> None:
    assert f"E15_suficiencia{sufijo_artefacto(modo, 'v2.2')}" == esperado


def test_el_sufijo_valida_la_politica() -> None:
    with pytest.raises(ValueError, match="política de suficiencia desconocida"):
        sufijo_artefacto("oracle", "v3.0")


@pytest.mark.parametrize(
    ("oracle", "adverse", "esperado"),
    [(True, False, "oracle"), (False, False, "non_oracle"), (False, True, "adverse")],
)
def test_nombre_del_modo(oracle: bool, adverse: bool, esperado: str) -> None:
    assert modo_de(oracle=oracle, adverse=adverse) == esperado


def test_v2_1_exige_siempre_el_codigo_y_v2_2_lo_lee_de_la_declaracion() -> None:
    """El requisito explícito es lo único que v2.2 añade."""
    assert requisito_dtc("F00_normal", "v2.1") is DtcRequirement.DTC_REQUIRED
    assert requisito_dtc("F00_normal", "v2.2") is DtcRequirement.DTC_NOT_APPLICABLE
    assert requisito_dtc("F01_vacuum_leak", "v2.2") is DtcRequirement.DTC_REQUIRED
    assert requisito_dtc("F99_inexistente", "v2.2") is DtcRequirement.DTC_MAPPING_UNAVAILABLE
    assert requisito_dtc("F99_inexistente", "v2.1") is DtcRequirement.DTC_REQUIRED


# ---------------------------------------------------------------------------
# Resumen: las dos tasas con sus denominadores
# ---------------------------------------------------------------------------


def _caso(
    case_id_gold: str,
    *,
    ventana: str,
    condicion: str,
    esperado: str,
    decision: Decision,
) -> CasoVerificado:
    return CasoVerificado(
        gold={
            "case_id": case_id_gold,
            "fault_id": "F01_vacuum_leak",
            "corpus_variant": condicion,
            "expected_action": esperado,
        },
        case_id=ventana,
        bundle=_bundle(),
        verdict=_veredicto(decision, case_id=ventana),
        diagnosis_used="F01_vacuum_leak",
        dtc_requirement=DtcRequirement.DTC_REQUIRED.value,
    )


def _conjunto_de_diecisiete(
    *, explican_con_evidencia_completa: int = 3, distractor_explica: bool = False
) -> list[CasoVerificado]:
    """Reproduce la estructura del conjunto anotado: 17 casos sobre 5 ventanas.

    Cinco casos con evidencia completa, uno por ventana, y doce que aplican cuatro
    condiciones a tres de esas ventanas. Es la geometría que hace que los
    denominadores del capítulo 5 sean 5, 9 y 12.
    """
    casos: list[CasoVerificado] = []
    completos = ["wA", "wB", "wC", "wD", "wE"]
    for n, ventana in enumerate(completos, start=1):
        decision = Decision.EXPLAIN if n <= explican_con_evidencia_completa else Decision.ABSTAIN
        casos.append(
            _caso(
                f"C0{n}",
                ventana=ventana,
                condicion="FULL",
                esperado="EXPLAIN",
                decision=decision,
            )
        )
    for ventana in ("wA", "wB", "wC"):
        for condicion in ("ABSENT", "PARTIAL", "DISTRACTOR", "DISTRACTOR_NO_FILTER"):
            explica = distractor_explica and condicion == "DISTRACTOR"
            casos.append(
                _caso(
                    f"{ventana}_{condicion}",
                    ventana=ventana,
                    condicion=condicion,
                    esperado="ABSTAIN",
                    decision=Decision.EXPLAIN if explica else Decision.ABSTAIN,
                )
            )
    return casos


def test_los_denominadores_son_los_del_capitulo_5() -> None:
    resumen = resumen_abstencion(_conjunto_de_diecisiete())
    assert resumen["n_cases"] == 17
    fc = resumen["false_confidence"]
    # Casos que debían abstenerse, sin la condición con distractor y filtro.
    assert (fc["numerator"], fc["denominator"], fc["n_independent_windows"]) == (0, 9, 3)
    inclusivo = fc["including_distractor_with_filter"]
    assert (inclusivo["numerator"], inclusivo["denominator"]) == (0, 12)
    ai = resumen["unnecessary_abstention"]
    assert (ai["numerator"], ai["denominator"], ai["n_independent_windows"]) == (2, 5, 5)
    assert ai["rate"] == 0.4
    cobertura = resumen["coverage_full_evidence"]
    assert (cobertura["numerator"], cobertura["denominator"]) == (3, 5)
    assert cobertura["rate"] == 0.6


def test_la_falsa_confianza_distingue_el_subtotal_del_denominador_inclusivo() -> None:
    """Tres filas que no añaden distractor no pueden abaratar la tasa."""
    resumen = resumen_abstencion(_conjunto_de_diecisiete(distractor_explica=True))
    fc = resumen["false_confidence"]
    assert (fc["numerator"], fc["denominator"], fc["rate"]) == (0, 9, 0.0)
    inclusivo = fc["including_distractor_with_filter"]
    assert (inclusivo["numerator"], inclusivo["denominator"], inclusivo["rate"]) == (3, 12, 0.25)


def test_un_denominador_vacio_no_produce_una_tasa_inventada() -> None:
    resumen = resumen_abstencion([])
    assert resumen["false_confidence"]["rate"] is None
    assert resumen["unnecessary_abstention"]["rate"] is None
    assert resumen["coverage_full_evidence"]["rate"] is None


def test_el_resumen_lleva_la_decision_de_cada_caso() -> None:
    resumen = resumen_abstencion(_conjunto_de_diecisiete())
    assert resumen["decisions"]["C01"] == "EXPLAIN"
    assert resumen["decisions"]["wA_ABSENT"] == "ABSTAIN"
    assert resumen["metric_definition"].startswith("docs/memoria/cap4")


# ---------------------------------------------------------------------------
# Forma de los registros
# ---------------------------------------------------------------------------


def test_la_fila_por_caso_lleva_lo_que_el_preregistro_exige() -> None:
    caso = _caso(
        "C05", ventana="wA", condicion="FULL", esperado="EXPLAIN", decision=Decision.EXPLAIN
    )
    fila = fila_de(caso, grados=EXACTA)
    assert {
        "case_id",
        "condition",
        "calibrated_confidence",
        "n_documents_applicable",
        "claim_coverage",
        "expected_action",
        "decision",
        "reasons",
        "chunk_ids_to_verifier",
    } <= set(fila)
    # Los fragmentos que llegaron al verificador, en el orden en que llegaron.
    assert fila["chunk_ids_to_verifier"] == "ch0;ch1"


def test_el_registro_de_una_ablacion_se_identifica_y_resume(tmp_path: Path) -> None:
    documento = documento_ablacion(
        "A1",
        modo="oracle",
        oracle=True,
        dataset_id="synthetic_v2",
        umbrales=SufficiencyThresholds(),
        calibracion={"method": "isotonic, cv=5 sobre entrenamiento"},
        casos=_conjunto_de_diecisiete(),
        embedding_space_id="st/modelo/d384/v1",
    )
    escrito = escribir(tmp_path / "E18_ablacion_A1.json", documento, seed=20260901)
    leido = json.loads(escrito.read_text(encoding="utf-8"))
    assert set(leido) >= CAMPOS_OBLIGATORIOS
    assert leido["experiment_id"] == "E18_ablation_A1"
    assert leido["ablation_id"] == "A1"
    assert leido["ablation"] == ABLACIONES["A1"]
    assert leido["preregistration"].endswith("preregistro-e18-ablaciones.md")
    assert leido["verifier_version"] == VERIFIER_VERSION
    assert leido["summary"]["false_confidence"]["denominator"] == 9
    assert len(leido["cases"]) == 17
    assert {"bundle", "verdict", "support_checks"} <= set(leido["cases"][0])


def test_a2_no_declara_un_espacio_de_embeddings_que_no_uso() -> None:
    """La consulta de A2 no se vectoriza: declararlo sería afirmar lo que no pasó."""
    documento = documento_ablacion(
        "A2",
        modo="oracle",
        oracle=True,
        dataset_id="synthetic_v2",
        umbrales=SufficiencyThresholds(),
        calibracion={},
        casos=[],
        embedding_space_id=None,
    )
    assert documento["retrieval"]["query_vectorized"] is False
    assert documento["retrieval"]["route"] == "lexical_full_text"
    assert documento["retrieval"]["embedding_space_id"] is None


def test_el_registro_de_e15_conserva_la_forma_del_artefacto_vigente(tmp_path: Path) -> None:
    """El refactor no puede cambiar la forma del registro que el capítulo 5 cita.

    Se compara contra `experiments/E15_suficiencia.json`, que es el artefacto
    congelado de v2.1 en modo oracular, usando un caso de juguete: lo que se
    verifica es la **forma**, no las cifras, que exigirían ejecutar el experimento.
    """
    vigente = json.loads((paths.EXPERIMENTS / "E15_suficiencia.json").read_text(encoding="utf-8"))
    caso = _caso(
        "C05", ventana="wA", condicion="FULL", esperado="EXPLAIN", decision=Decision.EXPLAIN
    )
    documento = documento_suficiencia(
        modo="oracle",
        oracle=True,
        adverse=False,
        dataset_id="synthetic_v2",
        policy=VERIFIER_VERSION,
        umbrales=SufficiencyThresholds(),
        calibracion=vigente["calibration"],
        casos=[caso],
    )
    escrito = escribir(
        tmp_path / "E15_suficiencia.json",
        documento,
        seed=20260901,
        dataset_id="synthetic_v2",
        dataset_type="synthetic",
        embedding_model=vigente["embedding_model"],
        goldset=vigente["goldset"],
    )
    nuevo = json.loads(escrito.read_text(encoding="utf-8"))

    assert sorted(nuevo) == sorted(vigente)
    assert sorted(nuevo["cases"][0]) == sorted(vigente["cases"][0])
    assert sorted(nuevo["cases"][0]["bundle"]) == sorted(vigente["cases"][0]["bundle"])
    for campo in ("experiment_id", "mode", "oracle_channels_open", "evaluation_policy"):
        assert nuevo[campo] == vigente[campo]
    assert nuevo["vehicle_id"] == vigente["vehicle_id"]
    assert nuevo["verifier_version"] == vigente["verifier_version"]
    # Los umbrales del artefacto vigente son los que el código sigue usando.
    assert nuevo["thresholds"] == vigente["thresholds"]


def test_el_registro_de_e15_declara_la_politica_con_que_se_midio() -> None:
    documento = documento_suficiencia(
        modo="oracle",
        oracle=True,
        adverse=False,
        dataset_id="synthetic_v2",
        policy="v2.2",
        umbrales=SufficiencyThresholds(),
        calibracion={},
        casos=[],
    )
    assert documento["verifier_version"] == "v2.2"
