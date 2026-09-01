"""Métricas de recuperación y coherencia del conjunto anotado."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from mecanico_ia_exp.evaluation.retrieval import (
    StrategyReport,
    dcg,
    evaluate_case,
    ndcg_at_k,
)

GOLDSET = Path("configs/goldset_mazda3_bk.yaml")


# ------------------------------------------------------------------ métricas


def test_una_recuperacion_perfecta_da_metricas_maximas() -> None:
    m = evaluate_case(
        case_id="c",
        retrieved_files=["a.pdf", "x.pdf"],
        relevant_files={"a.pdf"},
        k=10,
    )
    assert m.hit_rate == 1.0
    assert m.reciprocal_rank == 1.0
    assert m.recall_at_k == 1.0
    assert m.first_relevant_rank == 1


def test_no_encontrar_nada_da_metricas_nulas() -> None:
    m = evaluate_case(
        case_id="c", retrieved_files=["x.pdf", "y.pdf"], relevant_files={"a.pdf"}, k=10
    )
    assert m.hit_rate == 0.0
    assert m.reciprocal_rank == 0.0
    assert m.recall_at_k == 0.0
    assert m.first_relevant_rank is None


def test_el_rango_reciproco_penaliza_encontrarlo_tarde() -> None:
    temprano = evaluate_case(
        case_id="c", retrieved_files=["a.pdf", "x.pdf"], relevant_files={"a.pdf"}, k=10
    )
    tarde = evaluate_case(
        case_id="c",
        retrieved_files=["x.pdf", "y.pdf", "a.pdf"],
        relevant_files={"a.pdf"},
        k=10,
    )
    assert temprano.reciprocal_rank > tarde.reciprocal_rank
    assert tarde.reciprocal_rank == pytest.approx(1 / 3)


def test_el_recall_cuenta_ficheros_distintos_y_no_fragmentos() -> None:
    """Recuperar cinco fragmentos del mismo procedimiento es haberlo encontrado
    una vez, no cinco."""
    m = evaluate_case(
        case_id="c",
        retrieved_files=["a.pdf"] * 5,
        relevant_files={"a.pdf", "b.pdf"},
        k=10,
    )
    assert m.recall_at_k == 0.5


def test_el_ndcg_premia_el_orden() -> None:
    bueno = ndcg_at_k([2.0, 1.0, 0.0], k=3)
    malo = ndcg_at_k([0.0, 1.0, 2.0], k=3)
    assert bueno == pytest.approx(1.0)
    assert malo < bueno


def test_el_dcg_descuenta_por_posicion() -> None:
    assert dcg([1.0, 0.0]) > dcg([0.0, 1.0])


def test_sin_relevantes_el_ndcg_es_cero_y_no_indefinido() -> None:
    assert ndcg_at_k([0.0, 0.0], k=2) == 0.0


# --------------------------------------------------------------- distractores


def test_se_detecta_un_distractor_por_encima_de_la_evidencia_aplicable() -> None:
    """Es el fallo más grave: preferir un procedimiento de otro motor al que sí
    aplica."""
    m = evaluate_case(
        case_id="c",
        retrieved_files=["lf.pdf", "z6.pdf"],
        relevant_files={"z6.pdf"},
        distractor_files={"lf.pdf"},
        k=10,
    )
    assert m.distractors_retrieved == 1
    assert m.distractor_ranks == (1,)
    assert m.distractor_above_relevant is True


def test_un_distractor_por_debajo_no_se_marca_como_grave() -> None:
    m = evaluate_case(
        case_id="c",
        retrieved_files=["z6.pdf", "lf.pdf"],
        relevant_files={"z6.pdf"},
        distractor_files={"lf.pdf"},
        k=10,
    )
    assert m.distractors_retrieved == 1
    assert m.distractor_above_relevant is False


def test_un_distractor_sin_evidencia_aplicable_es_grave() -> None:
    """Si no se recupera nada aplicable, cualquier distractor recuperado manda."""
    m = evaluate_case(
        case_id="c",
        retrieved_files=["lf.pdf"],
        relevant_files={"z6.pdf"},
        distractor_files={"lf.pdf"},
        k=10,
    )
    assert m.distractor_above_relevant is True


# ------------------------------------------------------------------ agregado


def test_los_casos_sin_documento_relevante_no_hunden_la_media() -> None:
    """El caso de abstención no tiene documento que encontrar. Contarlo como un
    fallo de recuperación mezclaría dos cosas distintas: no encontrar la
    evidencia y que no exista."""
    informe = StrategyReport(strategy="s", k=10)
    informe.cases.append(
        evaluate_case(case_id="con", retrieved_files=["a.pdf"], relevant_files={"a.pdf"})
    )
    informe.cases.append(
        evaluate_case(case_id="sin", retrieved_files=["x.pdf"], relevant_files=set())
    )
    assert informe.hit_rate == 1.0
    assert len(informe.cases) == 2


def test_el_informe_serializa_con_el_detalle_por_caso() -> None:
    informe = StrategyReport(strategy="semantic", k=10)
    informe.cases.append(
        evaluate_case(case_id="c1", retrieved_files=["a.pdf"], relevant_files={"a.pdf"})
    )
    datos = informe.to_dict()
    assert datos["strategy"] == "semantic"
    assert len(datos["cases"]) == 1


# ------------------------------------------------------- conjunto anotado


@pytest.fixture(scope="module")
def gold() -> dict:
    return yaml.safe_load(GOLDSET.read_text(encoding="utf-8"))


def test_el_conjunto_anotado_declara_vehiculo_y_motor(gold: dict) -> None:
    assert gold["vehicle_id"] == "mazda-3-bk-2007"
    assert gold["engine_code"] == "Z6"


def test_cada_caso_declara_su_accion_esperada(gold: dict) -> None:
    for caso in gold["cases"]:
        assert caso["expected_action"] in {"EXPLAIN", "ABSTAIN"}


def test_hay_al_menos_un_caso_de_abstencion(gold: dict) -> None:
    """Un conjunto donde todo tiene respuesta no puede medir la abstención."""
    abstenciones = [c for c in gold["cases"] if c["expected_action"] == "ABSTAIN"]
    assert abstenciones, "el conjunto no contiene ningún caso sin evidencia suficiente"


def test_el_caso_de_abstencion_no_declara_documentos_relevantes(gold: dict) -> None:
    for caso in gold["cases"]:
        if caso["expected_action"] == "ABSTAIN":
            assert not caso["relevant_files"]


def test_los_casos_con_explicacion_declaran_documento_y_distractor(gold: dict) -> None:
    for caso in gold["cases"]:
        if caso["expected_action"] == "EXPLAIN":
            assert caso["relevant_files"], f"{caso['case_id']} sin documento relevante"
            assert caso["distractor_files"], f"{caso['case_id']} sin distractor"
            assert caso["dtc"], f"{caso['case_id']} sin DTC declarado"


def test_la_consulta_no_contiene_la_respuesta(gold: dict) -> None:
    """Si la consulta nombrara el DTC o la causa, la evaluación mediría la
    consulta y no la recuperación."""
    for caso in gold["cases"]:
        consulta = str(caso["query"]).upper()
        if caso["dtc"]:
            assert caso["dtc"] not in consulta, f"{caso['case_id']} filtra su DTC"
        for prohibido in ("THERMOSTAT", "MISFIRE", "VACUUM LEAK", "SENSOR DRIFT"):
            assert prohibido not in consulta, f"{caso['case_id']} nombra la causa: {prohibido}"


def test_relevantes_y_distractores_no_se_solapan(gold: dict) -> None:
    for caso in gold["cases"]:
        assert not set(caso["relevant_files"]) & set(caso["distractor_files"] or [])
