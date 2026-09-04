"""Contrato de RERUN-A: una sola variable.

La afirmación entera del experimento —«lo único que cambia es el aislamiento del
espacio vectorial»— descansa en configuración, no en aritmética. Estas pruebas la
fijan: si alguien mueve una de esas piezas, falla aquí y no en la interpretación
de un resultado seis pasos más tarde.

Pre-registro: `docs/methodology/preregistro-rerun-a.md`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]


# --- El verificador canónico -------------------------------------------------


def test_la_politica_canonica_es_v2_1() -> None:
    """v2.2 está implementada y **sin medir**: introducirla ahora cambiaría dos
    variables en la misma ejecución y la atribución causal se perdería."""
    from mecanico_ia_exp.abstention.sufficiency import POLITICAS, VERIFIER_VERSION

    assert VERIFIER_VERSION == "v2.1", (
        "RERUN-A exige v2.1. v2.2 se mide en RERUN-B, sobre recuperación ya canónica"
    )
    assert VERIFIER_VERSION in POLITICAS


def test_bajo_v2_1_la_puerta_de_codigos_se_comporta_como_su_artefacto() -> None:
    """El requisito explícito es lo único que v2.2 añade.

    Con v2.1 activo, un fragmento sin códigos esperados no puede recibir los
    motivos que v2.2 introdujo: si los recibiera, el artefacto congelado de v2.1
    dejaría de ser reproducible.
    """
    from mecanico_ia_exp.evidence.model import Claim, DocumentaryEvidence
    from mecanico_ia_exp.evidence.support import DtcRequirement, check_support

    fragmento = DocumentaryEvidence(
        chunk_id="ch",
        document_id="doc",
        vehicle_id="v",
        text=(
            "B1234 throttle position sensor.\nTurn the ignition switch off. Measure the "
            "resistance. Is the resistance within specification?\nYes Go to the next step."
        ),
        score=0.5,
        applicability="EXACT_MATCH",
        document_type="WORKSHOP_MANUAL",
        dtc_codes=("B1234",),
        section="DTC B1234 [ZJ, Z6]",
    )
    resultado = check_support(
        Claim("C01", "t", ()),
        fragmento,
        signal="throttle_position",
        expected_dtc=("B1234",),
        requisito=DtcRequirement.DTC_REQUIRED,
    )
    assert resultado.supports
    assert resultado.dtc_requirement == DtcRequirement.DTC_REQUIRED.value


def test_el_umbral_y_la_semilla_no_se_mueven() -> None:
    """Las constantes que el pre-registro declara controladas."""
    from mecanico_ia_exp.abstention.sufficiency import SufficiencyThresholds

    u = SufficiencyThresholds()
    assert u.min_confidence == 0.79
    assert u.min_claim_coverage == 0.8
    assert u.accepted_applicability == frozenset({"EXACT_MATCH"})


# --- El conjunto de recuperación ---------------------------------------------


def test_el_conjunto_de_recuperacion_es_el_original_de_seis() -> None:
    """Reejecutar sobre los diecisiete cambiaría **dos** variables.

    El conjunto anotado creció después de aquella ejecución. La ampliación es un
    experimento distinto, con otra pregunta y otro identificador.
    """
    from mecanico_ia_exp.experiments.retrieval_runner import CONJUNTO_E12_ORIGINAL

    assert len(CONJUNTO_E12_ORIGINAL) == 6
    artefacto = json.loads(
        (RAIZ / "experiments" / "E12_retrieval.json").read_text(encoding="utf-8")
    )
    del_artefacto = tuple(c["case_id"] for c in artefacto["strategies"][0]["cases"])
    assert del_artefacto == CONJUNTO_E12_ORIGINAL, (
        "el conjunto declarado no coincide con el del artefacto que se quiere replicar"
    )


# --- Las líneas base como control de integridad ------------------------------


def test_las_lineas_base_invariantes_estan_declaradas_como_vector() -> None:
    """Su valor no puede depender del número de condiciones.

    Expresadas como razones sobre las ejecuciones totales, retirar una condición
    las cambia **por construcción** y la regla de parada saltaría sin que nada
    fuera mal.
    """
    texto = (RAIZ / "docs" / "methodology" / "preregistro-rerun-a.md").read_text(encoding="utf-8")
    assert "B = [" in texto, "las invariantes deben declararse como vector ordenado"
    assert "por (fallo, condición)" in texto or "por fallo y condición" in texto


@pytest.mark.parametrize("retirado", ["p = 0,008", "p = 0.008"])
def test_el_valor_p_retirado_no_reaparece(retirado: str) -> None:
    """`RETRACTED_INVALID_INFERENCE`: no debe poder volver desde ningún documento
    vivo. Se permite únicamente donde se declara su retirada."""
    permitidos = {
        "preregistro-rerun-a.md",
        "08_decisiones_autor_20260904.md",
        "estados-provisionales.md",
    }
    ofensores = []
    for f in (RAIZ / "docs").rglob("*.md"):
        if f.name in permitidos or "revision" in f.parts:
            continue
        if retirado in f.read_text(encoding="utf-8"):
            ofensores.append(str(f.relative_to(RAIZ)))
    assert not ofensores, f"el valor p retirado reaparece en: {ofensores}"


# --- El estado experimental enumerado -----------------------------------------
# Tres intentos revelaron tres variables derivadas que la frase «todo lo demás
# idéntico» no cubría. Estas pruebas comprueban **comportamiento observable**: qué
# fallaría si el defecto reapareciera, no si existe una constante.


def test_rerun_a_usa_el_mapa_de_codigos_congelado() -> None:
    """El defecto que reaparecería: buscar C01 con cuatro códigos donde el
    artefacto original usó dos.

    Falla si alguien reejecuta con el mapa vigente en lugar del congelado, que es
    exactamente lo que estaba a punto de ocurrir.
    """
    from mecanico_ia_exp.experiments.retrieval_runner import (
        DIAGNOSTICO_A_DTC,
        cargar_mapa_legacy,
    )

    legacy, huella = cargar_mapa_legacy()
    assert legacy["F02_maf_drift"] == ("P0101", "P0102"), (
        "el mapa congelado ha cambiado: RERUN-A dejaría de reproducir el artefacto"
    )
    assert DIAGNOSTICO_A_DTC["F02_maf_drift"] != legacy["F02_maf_drift"], (
        "el mapa vigente y el congelado coinciden: si es a propósito, actualiza el "
        "manifiesto; si no, alguien editó uno de los dos"
    )
    assert huella == "04088d9f0435c7f0"


def test_la_busqueda_acotada_usa_el_mapa_que_se_le_pasa() -> None:
    """Comportamiento, no configuración: qué códigos llegan a la consulta.

    Si `dtc_map` se ignorase, la estrategia acotaría con el mapa vigente y el
    contraste cambiaría dos variables sin que nada fallara.
    """

    class EspiaCodigos:
        def __init__(self) -> None:
            self.codigos: tuple[str, ...] | None = None

        def search(self, _v: object, **kw: object) -> list[object]:
            if "dtc_codes" in kw:
                self.codigos = kw["dtc_codes"]  # type: ignore[assignment]
            return []

        def search_lexical(self, *_a: object, **_k: object) -> list[object]:
            return []

    class Proveedor:
        class _Id:
            provider, model, dimension, version = "p", "m", 384, "1"

        identity = _Id()

        def embed_one(self, _t: str) -> object:
            import numpy as np

            return np.zeros(384, dtype=np.float32)

    from mecanico_ia_exp.experiments.retrieval_runner import cargar_mapa_legacy, recuperar

    legacy, _ = cargar_mapa_legacy()
    espia = EspiaCodigos()
    recuperar(
        "diagnosis-guided",
        store=espia,  # type: ignore[arg-type]
        provider=Proveedor(),  # type: ignore[arg-type]
        caso={"case_id": "C01_maf_drift", "fault_id": "F02_maf_drift", "query": "maf low"},
        vehicle_id="mazda-3-bk-2007",
        engine_code="Z6",
        dtc_map=legacy,
    )
    assert espia.codigos == ("P0101", "P0102"), (
        f"la búsqueda acotó con {espia.codigos}, no con el mapa congelado"
    )


def test_un_caso_sin_relevantes_se_evalua_pero_no_se_puntua() -> None:
    """El sexto caso forma parte del experimento y no puede contribuir a una
    métrica que divide por relevantes. Decir «N = 5» lo borraría; decir «N = 6»
    atribuiría a seis una media de cinco."""
    from mecanico_ia_exp.evaluation.retrieval import RetrievalMetrics, StrategyReport

    informe = StrategyReport(strategy="semantic", k=10)
    informe.cases.extend(
        [
            RetrievalMetrics(
                case_id="con_relevantes",
                k=10,
                n_relevant=1,
                n_retrieved=10,
                precision_at_k=0.1,
                recall_at_k=1.0,
                hit_rate=1.0,
                reciprocal_rank=1.0,
                ndcg_at_k=1.0,
                first_relevant_rank=1,
                distractors_retrieved=0,
            ),
            RetrievalMetrics(
                case_id="evidencia_retirada",
                k=10,
                n_relevant=0,
                n_retrieved=10,
                precision_at_k=0.0,
                recall_at_k=0.0,
                hit_rate=0.0,
                reciprocal_rank=0.0,
                ndcg_at_k=0.0,
                first_relevant_rank=None,
                distractors_retrieved=0,
            ),
        ]
    )
    d = informe.to_dict()
    assert d["n_evaluated"] == 2
    assert d["n_scored"] == 1
    assert d["n_excluded_from_metric"] == 1
    assert d["excluded_case_ids"] == ["evidencia_retirada"]
    assert d["exclusion_reason"]


def test_el_diseno_inferencial_retirado_esta_prohibido_por_diseno() -> None:
    """No basta prohibir el número: hay que prohibir la combinación que lo produce.

    `5**-2 = 0,040` está por debajo de 0,05, así que prohibir solo `0,008` dejaba
    viva una ruta a un resultado significativo con el mismo diseño inválido.
    """
    texto = (RAIZ / "docs" / "methodology" / "preregistro-rerun-a.md").read_text(encoding="utf-8")
    assert "RETRACTED_TEST_DESIGN" in texto
    for elemento in ("unidad de permutación", "K", "estadístico", "hipótesis"):
        assert elemento in texto, f"el diseño retirado no declara {elemento}"
    assert 5**-2 < 0.05, "aritmética de la cláusula de fragilidad"
    assert "0,040" in texto, "la ruta de 0,040 debe estar declarada, no solo la de 0,008"


def test_los_criterios_del_distractor_leen_el_artefacto_pre_registrado() -> None:
    """Apuntaban al artefacto de recuperación, que tras acotarlo a seis casos no
    contiene ninguna condición de distractor. Elegir la otra fuente después de ver
    el resultado sería el grado de libertad que la enmienda cierra."""
    texto = (RAIZ / "docs" / "methodology" / "preregistro-rerun-a.md").read_text(encoding="utf-8")
    assert "bundle.documents" in texto
    assert "E15_suficiencia.json" in texto
    assert "PENDING_CANONICAL_DIAGNOSIS" in texto or "PENDING_CANONICAL" in texto


def test_el_manifiesto_enumera_el_estado_y_la_variable_manipulada() -> None:
    """La frase «todo lo demás idéntico» dejó pasar tres variables derivadas.

    Falla si el manifiesto pierde cualquiera de las piezas de estado que un
    cambio silencioso podría mover.
    """
    m = json.loads((RAIZ / "configs" / "manifest_rerun_a.json").read_text(encoding="utf-8"))
    assert m["MANIPULATED_VARIABLE"]["name"] == "embedding_space_enforcement"
    assert m["EXPECTED_DIRECTION"] == "NONE"
    estado = m["CONTROLLED_STATE"]
    for clave in (
        "case_set",
        "dtc_map",
        "annotated_set",
        "corpus",
        "embedding",
        "retrieval",
        "verifier",
        "thresholds",
        "classifier",
        "seed",
        "baseline_vector",
    ):
        assert clave in estado, f"el manifiesto no fija {clave}"
    assert estado["verifier"]["version"] == "v2.1"
    assert estado["dtc_map"]["hash"] == "04088d9f0435c7f0"
    assert m["DENOMINATORS"]["E12"] == {
        "n_evaluated": 6,
        "n_scored": 5,
        "n_excluded_from_metric": 1,
        "excluded": ["C06_vacuum_leak_evidencia_retirada"],
        "reason": "no relevant files in ground truth",
    }
