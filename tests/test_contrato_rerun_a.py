"""Contrato de RERUN-A: una sola variable.

La afirmación entera del experimento —«lo único que cambia es el aislamiento del
espacio vectorial»— descansa en configuración, no en aritmética. Estas pruebas la
fijan: si alguien mueve una de esas piezas, falla aquí y no en la interpretación
de un resultado seis pasos más tarde.

Pre-registro: `docs/methodology/preregistro-rerun-a.md`.
"""

from __future__ import annotations

import hashlib
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
    # Se lee la **copia congelada**, no el artefacto vivo: la reejecución
    # sobrescribe el vivo, y entonces esta prueba compararía el conjunto consigo
    # mismo y dejaría de comprobar nada.
    congelado = RAIZ / "experiments" / "pre_mixed_embedding_fix" / "E12_retrieval.json"
    artefacto = json.loads(congelado.read_text(encoding="utf-8"))
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
    # La huella se **recalcula** desde el contenido con la forma canónica que el
    # propio fichero declara. La primera versión copiaba un literal que ningún
    # código comprobaba, y por ese hueco se coló una entrada ausente.
    doc = json.loads((RAIZ / "configs" / "e12_legacy_dtc_map.json").read_text(encoding="utf-8"))
    cuerpo = json.dumps(doc["map"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    assert hashlib.sha256(cuerpo.encode()).hexdigest()[:16] == doc["map_sha256_16"], (
        "la huella declarada no corresponde al contenido del mapa"
    )
    assert huella == doc["map_sha256_16"]


def test_el_mapa_congelado_cubre_todos_los_fallos_de_los_seis_casos() -> None:
    """La prueba estructural que faltaba, y que habría evitado `RAG-MAJ-074`.

    Mi primera versión del mapa congelado **omitía** `F04_o2_lag`, porque la
    construí desde una extracción por expresión regular que se saltó esa entrada.
    Con esa omisión, el caso de la sonda habría recibido lista vacía y **degradado
    a la estrategia mixta**: su recuperación habría cambiado por una causa ajena a
    la variable manipulada, y la caída se habría leído como efecto del espacio
    vectorial.

    Comprueba la propiedad, no el contenido: **todo fallo de los seis casos tiene
    entrada en el mapa**. Falla ante cualquier omisión futura, no solo ante esta.
    """
    import yaml

    from mecanico_ia_exp.experiments.retrieval_runner import (
        CONJUNTO_E12_ORIGINAL,
        cargar_mapa_legacy,
    )

    gold = yaml.safe_load((RAIZ / "configs" / "goldset_mazda3_bk.yaml").read_text(encoding="utf-8"))
    por_id = {c["case_id"]: c for c in gold["cases"]}
    legacy, _ = cargar_mapa_legacy()
    sin_entrada = [
        (c, por_id[c]["fault_id"])
        for c in CONJUNTO_E12_ORIGINAL
        if por_id[c]["fault_id"] not in legacy
    ]
    assert not sin_entrada, (
        f"casos cuyo fallo no está en el mapa congelado: {sin_entrada}. "
        "Degradarían a `hybrid` y su recuperación cambiaría por una causa ajena "
        "a la variable manipulada"
    )


def test_el_mapa_congelado_reproduce_el_del_commit_de_la_ejecucion() -> None:
    """Contra el módulo real del commit, extraído por AST.

    Es la comprobación que no hice y que dejó pasar la omisión: verificar el
    congelado contra su fuente en lugar de contra mi propia extracción.
    """
    import ast
    import subprocess

    from mecanico_ia_exp.experiments.retrieval_runner import cargar_mapa_legacy

    doc = json.loads((RAIZ / "configs" / "e12_legacy_dtc_map.json").read_text(encoding="utf-8"))
    fuente = subprocess.run(
        [
            "git",
            "show",
            f"{doc['source_commit']}:src/mecanico_ia_exp/experiments/retrieval_runner.py",
        ],
        capture_output=True,
        text=True,
        cwd=RAIZ,
    ).stdout
    if not fuente:
        pytest.skip("el commit de origen no está disponible en este clon")
    original = None
    for n in ast.walk(ast.parse(fuente)):
        if isinstance(n, ast.AnnAssign) and getattr(n.target, "id", "") == "DIAGNOSTICO_A_DTC":
            original = {k: tuple(v) for k, v in ast.literal_eval(n.value).items()}
    legacy, _ = cargar_mapa_legacy()
    assert legacy == original, (
        "el mapa congelado no coincide con el del commit que produjo el artefacto"
    )


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
    # El mapa se declara **por experimento**: E12 usa el congelado y la suficiencia
    # el vigente. Un solo valor invitaría a «corregir» E15 e introducir allí la
    # misma variable que se está eliminando de E12.
    assert set(estado["dtc_map"]) == {"E12_CANONICAL", "E15_E17"}
    assert estado["dtc_map"]["E12_CANONICAL"]["n_entries"] == 5
    assert m["DENOMINATORS"]["E12"] == {
        "n_evaluated": 6,
        "n_scored": 5,
        "n_excluded_from_metric": 1,
        "excluded": ["C06_vacuum_leak_evidencia_retirada"],
        "reason": "no relevant files in ground truth",
    }


# --- Fidelidad, no solo integridad --------------------------------------------
# Lección del quinto pase: una huella demuestra que el valor declarado no ha
# cambiado, no que sea el valor correcto. El mapa congelado tenía huella válida y
# le faltaba una entrada. Estas pruebas comparan cada pieza del manifiesto con su
# **fuente**, no consigo misma.


def _manifiesto() -> dict[str, object]:
    return json.loads((RAIZ / "configs" / "manifest_rerun_a.json").read_text(encoding="utf-8"))


def test_el_identificador_de_espacio_es_el_que_produce_el_codigo() -> None:
    """Lo escribí a mano y no coincidía: sobraba el dispositivo y la versión era
    otra. Un identificador inventado no identifica nada."""
    from mecanico_ia_exp.rag.embeddings import get_provider

    ident = get_provider("multilingual").identity
    real = f"{ident.provider}/{ident.model}/d{ident.dimension}/v{ident.version}"
    emb = _manifiesto()["CONTROLLED_STATE"]["embedding"]  # type: ignore[index]
    assert emb["provider_identity_string"] == real, (
        f"el manifiesto declara {emb['provider_identity_string']!r} y el código produce {real!r}"
    )


def test_el_dispositivo_de_embeddings_esta_declarado_como_estado_controlado() -> None:
    """Quinta variable derivada, detectada antes de medir.

    El dispositivo forma parte de la identidad del proveedor y queda en el índice,
    pero la búsqueda filtra por **nombre de modelo**, no por la identidad completa:
    vectores calculados en dispositivos distintos conviven bajo el mismo espacio y
    el filtro no los separa. No son idénticos bit a bit.
    """
    from mecanico_ia_exp.rag.embeddings import get_provider

    emb = _manifiesto()["CONTROLLED_STATE"]["embedding"]  # type: ignore[index]
    assert "device" in emb, "el dispositivo no está en el manifiesto"
    declarado = emb["device"]["value"]  # type: ignore[index]
    actual = get_provider("multilingual").identity.provider.split("[")[1].rstrip("]")
    assert declarado == actual, (
        f"el manifiesto fija el dispositivo {declarado!r} y esta máquina usa {actual!r}: "
        "los vectores no serían bit a bit los del índice"
    )


def test_el_conjunto_anotado_del_manifiesto_reproduce_su_huella() -> None:
    """Fidelidad del conjunto: se recalcula desde el fichero, no se copia."""
    import yaml

    m = _manifiesto()
    casos = m["CONTROLLED_STATE"]["case_set"]["value"]  # type: ignore[index]
    gold = yaml.safe_load((RAIZ / "configs" / "goldset_mazda3_bk.yaml").read_text(encoding="utf-8"))
    seis = [c for c in gold["cases"] if c["case_id"] in casos]
    cuerpo = json.dumps(
        seis, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    )
    esperado = hashlib.sha256(cuerpo.encode()).hexdigest()[:16]
    anotado = m["CONTROLLED_STATE"]["annotated_set"]  # type: ignore[index]
    assert anotado["six_cases_hash"] == esperado, (
        "la huella del conjunto anotado no reproduce el contenido de los seis casos"
    )
    assert anotado["n_cases"] == 6
