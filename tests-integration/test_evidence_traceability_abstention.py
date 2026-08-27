"""Evidencia, trazabilidad y abstención: pruebas del núcleo científico de la PI v4.

Cada prueba declara su **objetivo científico**: a qué hipótesis del pre-registro
enmendado (ENM-001) sirve y qué comportamiento demostraría o refutaría. No son pruebas de
regresión de implementación, sino evidencia automatizada de que el artefacto exhibe —o no—
las propiedades que la pregunta de investigación interroga.

Mecanismo experimental (ADR-0036): la disponibilidad de evidencia se manipula por
**exclusión controlada de documentos del corpus** (``ingest_corpus(exclude_document_ids=…)``).
El caso, el modelo, la semilla y el vector de features son idénticos entre escenarios; lo
único que cambia es qué documentación puede recuperarse.

    Escenario A (corpus C-A)  — la documentación del mecanismo está presente.
    Escenario B (corpus C-B)  — la documentación del mecanismo se ha retirado.
    Escenario B' (corpus C-B') — solo queda documentación genérica, no concluyente.

Brazos (``AgentConfig``): B1 sin recuperación · B2 con recuperación y sin verificación ni
abstención · B3 con recuperación, verificación del soporte y abstención.
"""

import uuid
from collections.abc import Collection
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from diagnostic_agent.reasoning.graph.agent_v1 import AgentConfig, DiagnosticAgentV1
from diagnostic_agent.reasoning.grounding import supports
from diagnostic_agent.reasoning.llm.generator import HeuristicHypothesizer
from diagnostic_agent.reasoning.rag.retriever import LexicalRetriever, ingest_corpus
from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.store import EdgeStoreV2
from mecanico_contracts import DetectedAnomaly, DetectorKind, ExplanationDecision, MemoryMode
from mecanico_contracts.features import FEATURE_NAMES

CORPUS = Path(__file__).parents[1] / "diagnostic-agent" / "knowledge" / "corpus_v1.yaml"
NOW = datetime(2026, 8, 27, tzinfo=UTC)

#: Documento que describe el mecanismo del caso evaluado.
DOC_MECANISMO = "doc-vacuum-leak"
#: Familia completa del mecanismo: el documento del caso **y sus sinónimos técnicos**, esto
#: es, los que describen la misma firma (trims positivos) por otra causa. Retirar la familia
#: entera es lo que construye el corpus C-B: retirar solo un documento dejaría al generador
#: proponer un mecanismo adyacente documentado, que es un diagnóstico equivocado con
#: afirmaciones sustentadas y no una abstención (ver el test de sustitución al final).
FAMILIA_MECANISMO = {DOC_MECANISMO, "doc-maf-drift", "doc-fuel-trim-interpretation"}
#: Documentación genérica que menciona los mismos PID sin establecer la relación causal.
DOC_GENERICO = "doc-fuel-trim-interpretation"

#: Firma de fuga de vacío: trims positivos, MAP alto a baja velocidad, ralentí inestable.
VACUUM = {
    "total_trim_mean": 9.4,
    "SHORT_FUEL_TRIM_1_mean": 5.1,
    "LONG_FUEL_TRIM_1_mean": 4.3,
    "INTAKE_PRESSURE_mean": 46.0,
    "SPEED_mean": 3.0,
    "RPM_std": 55.0,
    "RPM_mean": 840.0,
    "O2_B1S1_std": 0.24,
    "COOLANT_TEMP_mean": 88.0,
}
PIDS = ["SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1", "INTAKE_PRESSURE", "RPM"]

#: Documento distractor: plausible, del mismo dominio, irrelevante para este caso (CN3).
DISTRACTOR: dict[str, object] = {
    "id": "doc-distractor-neumaticos",
    "title": "Presión de neumáticos y consumo",
    "metadata": {"failure_mode": "tyre_pressure", "component": "neumáticos"},
    "text": (
        "Una presión de inflado baja aumenta la resistencia a la rodadura y el consumo de "
        "combustible. El sistema de monitorización de presión avisa por debajo del umbral "
        "del fabricante. Comprobaciones: medir en frío y comparar con la placa del pilar. "
        "No altera los ajustes de combustible ni la presión del colector de admisión."
    ),
}


def _anomaly(features: dict[str, float]) -> DetectedAnomaly:
    return DetectedAnomaly(
        anomaly_id=str(uuid.uuid4()),
        window_id=str(uuid.uuid4()),
        vehicle_id="veh-evid",
        detected_at=NOW,
        detector=DetectorKind.LOF,
        model_name="lof",
        model_version="0.2.0",
        score=9.0,
        threshold=0.16,
        involved_pids=PIDS,
        features={n: features.get(n, 0.0) for n in FEATURE_NAMES},
    )


def _store(
    tmp_path: Path,
    *,
    exclude: Collection[str] = (),
    extra: list[dict[str, object]] | None = None,
) -> EdgeStoreV2:
    """Construye una variante de corpus con exclusión controlada y devuelve el store."""
    corpus_path = CORPUS
    if extra:
        raw = yaml.safe_load(CORPUS.read_text(encoding="utf-8"))
        raw["documents"].extend(extra)
        corpus_path = tmp_path / "corpus_variant.yaml"
        corpus_path.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    store = EdgeStoreV2(tmp_path / f"edge-{uuid.uuid4().hex[:8]}.sqlite3")
    ingest_corpus(store, corpus_path, exclude_document_ids=exclude)
    return store


def _agent(store: EdgeStoreV2, **cfg: object) -> DiagnosticAgentV1:
    base = {"memory_mode": MemoryMode.NONE, "memory_enabled": False}
    return DiagnosticAgentV1(
        store,
        LexicalRetriever(store),
        HeuristicHypothesizer(),
        AgentConfig(**{**base, **cfg}),  # type: ignore[arg-type]
    )


def _claims(store: EdgeStoreV2, case_id: str) -> list[dbs.EvidenceRow]:
    rows = store.raw_rows(dbs.EvidenceRow, case_id=case_id)
    return [r for r in rows if r.produced_by == "decide"]


# --------------------------------------------------------------------------- 1
def test_escenario_a_evidencia_suficiente_produce_explicacion_sustentada(tmp_path: Path) -> None:
    """Objetivo científico: H-MAIN (i)–(iii) y H-GRD en el Escenario A.

    Con la documentación del mecanismo presente en el corpus, el agente debe diagnosticar
    correctamente, emitir explicación (no abstenerse) y sostener la mayoría de sus
    afirmaciones. Una abstención aquí sería una **falsa abstención** (métrica M16).
    """
    store = _store(tmp_path)
    case = _agent(store).run(_anomaly(VACUUM))

    assert case.decision is ExplanationDecision.SUPPORTED
    assert case.supported_claim_ratio is not None
    assert case.supported_claim_ratio >= 0.60  # umbral de suficiencia pre-registrado
    top = min(store.raw_rows(dbs.HypothesisRow, case_id=case.case_id), key=lambda h: h.rank)
    assert top.failure_mode == "vacuum_leak"
    assert case.explanation and "fuga" in case.explanation.lower()


# --------------------------------------------------------------------------- 2
def test_escenario_a_trazabilidad_afirmacion_evidencia_dato(tmp_path: Path) -> None:
    """Objetivo científico: H-TRC — la trazabilidad es efectiva, no declarativa.

    Cada afirmación documental sustentada debe llevar una referencia que **resuelva** a un
    fragmento realmente recuperado y cuyo contenido la **sostenga**; y las afirmaciones
    telemétricas deben anclar en una feature existente del vector de la ventana. Es la
    diferencia entre citar y estar sustentado (métricas M11 y M13).
    """
    store = _store(tmp_path)
    retriever = LexicalRetriever(store)
    case = _agent(store).run(_anomaly(VACUUM))
    anomaly_features = {n: VACUUM.get(n, 0.0) for n in FEATURE_NAMES}

    documentales = _claims(store, case.case_id)
    assert documentales, "la explicación debe descomponerse en afirmaciones citables"
    sustentadas = [c for c in documentales if c.role == "supports"]
    assert sustentadas, "en el Escenario A alguna afirmación documental debe estar sustentada"
    for claim in sustentadas:
        assert claim.reference_id, "toda afirmación sustentada lleva referencia"
        texto = retriever.chunk_text(claim.reference_id)
        assert texto, f"la referencia {claim.reference_id} debe resolver a un fragmento real"
        enunciado = claim.statement.removeprefix("[claim] ")
        ok, _ = supports(enunciado, texto, 0.30)
        assert ok, "el contenido citado debe sostener la afirmación, no solo acompañarla"
        assert retriever.document_id(claim.reference_id), "la traza alcanza el documento origen"

    telemetricas = [
        r
        for r in store.raw_rows(dbs.EvidenceRow, case_id=case.case_id)
        if r.produced_by == "verify" and r.role == "supports"
    ]
    assert telemetricas, "el verificador debe producir evidencia telemétrica"
    for ev in telemetricas:
        assert ev.reference_id in anomaly_features, "la traza llega hasta el dato, no al texto"


# --------------------------------------------------------------------------- 3
def test_escenario_b_evidencia_retirada_produce_abstencion(tmp_path: Path) -> None:
    """Objetivo científico: H-MAIN (iv) y H-ABS — el núcleo de la pregunta.

    Mismo caso, mismo modelo, mismas features: lo único que cambia es que el documento que
    describe el mecanismo se ha retirado del corpus. La salida correcta es declarar la
    insuficiencia (M15), no producir una explicación plausible.
    """
    store = _store(tmp_path, exclude=FAMILIA_MECANISMO)
    presentes = LexicalRetriever(store).document_ids()
    assert not (set(FAMILIA_MECANISMO) & presentes)  # control de la variante, verificado

    case = _agent(store).run(_anomaly(VACUUM))
    assert case.decision is ExplanationDecision.INSUFFICIENT_EVIDENCE
    assert "evidencia insuficiente" in (case.explanation or "").lower()
    runs = store.raw_rows(dbs.AgentRunRow, case_id=case.case_id)
    assert runs[0].result_status == "abstained"


# --------------------------------------------------------------------------- 4
def test_escenario_b_no_emite_afirmaciones_no_respaldadas(tmp_path: Path) -> None:
    """Objetivo científico: H-MAIN (iii) — no completar el hueco de evidencia.

    Al abstenerse, el sistema no debe nombrar el mecanismo ausente como si lo hubiera
    diagnosticado, y **ninguna afirmación marcada como sustentada puede serlo sin que su
    referencia exista y la respalde**. Es la contrapartida de la tasa de falsa aceptación
    (M17): completar el hueco significaría emitir el mecanismo retirado, o presentar como
    respaldada una afirmación cuya referencia no la respalda.

    Nótese qué **no** se comprueba aquí: que no quede ninguna afirmación documental
    sustentada. Puede quedarlas, porque una afirmación que cita literalmente un fragmento
    del corpus queda sustentada por construcción (limitación del constructo declarada en
    ``grounding.decide_sufficiency``). Lo que la abstención garantiza es que ese soporte
    documental aislado no se convierta en un diagnóstico emitido.
    """
    store = _store(tmp_path, exclude=FAMILIA_MECANISMO)
    retriever = LexicalRetriever(store)
    case = _agent(store).run(_anomaly(VACUUM))

    texto = (case.explanation or "").lower()
    assert case.decision is ExplanationDecision.INSUFFICIENT_EVIDENCE
    assert "fuga de vacío" not in texto
    assert "maf" not in texto  # tampoco el mecanismo adyacente retirado
    assert "diagnóstico más probable" not in texto

    for claim in _claims(store, case.case_id):
        if claim.role != "supports":
            continue
        assert claim.reference_id, "una afirmación sustentada sin referencia sería no respaldada"
        fragmento = retriever.chunk_text(claim.reference_id)
        assert fragmento, "la referencia debe resolver a un fragmento presente en el corpus"
        ok, _ = supports(claim.statement.removeprefix("[claim] "), fragmento, 0.30)
        assert ok, "ninguna afirmación puede marcarse como sustentada sin que su cita la sostenga"


# --------------------------------------------------------------------------- 5
def test_escenario_b_prima_evidencia_parcial_comportamiento_seguro(tmp_path: Path) -> None:
    """Objetivo científico: H-ABS en su variante dura (corpus C-B′).

    La recuperación **sí** devuelve resultados —documentación genérica sobre los mismos
    PID—, pero ninguno establece la relación causa→síntoma. Separa «no recupera nada,
    luego se abstiene» de «recupera algo irrelevante y sabe que no le basta»: el segundo
    es el comportamiento que la pregunta de investigación exige.
    """
    store = _store(tmp_path, exclude={DOC_MECANISMO, "doc-maf-drift", "doc-relational-anomalies"})
    presentes = LexicalRetriever(store).document_ids()
    assert DOC_GENERICO in presentes and DOC_MECANISMO not in presentes  # control verificado

    case = _agent(store).run(_anomaly(VACUUM))
    assert case.decision in (
        ExplanationDecision.INSUFFICIENT_EVIDENCE,
        ExplanationDecision.INCONCLUSIVE,
        ExplanationDecision.CONTRADICTED,
    ), "con evidencia parcial el sistema no debe emitir una explicación como sostenida"
    assert "fuga de vacío" not in (case.explanation or "").lower()


# --------------------------------------------------------------------------- 6
def test_corpus_con_distractor_no_ancla_en_evidencia_irrelevante(tmp_path: Path) -> None:
    """Objetivo científico: control negativo CN3 — resistencia al distractor documental.

    Se añade al corpus un documento plausible del mismo dominio pero irrelevante para el
    caso. Ninguna afirmación sustentada debe anclarse en él (métrica M14, anclaje en
    distractor ≈ 0), y el diagnóstico no debe desviarse.
    """
    store = _store(tmp_path, extra=[DISTRACTOR])
    case = _agent(store).run(_anomaly(VACUUM))

    documentales = _claims(store, case.case_id)
    anclajes = {c.reference_id for c in documentales if c.role == "supports" and c.reference_id}
    assert anclajes, "debe haber afirmaciones sustentadas en el Escenario A con distractor"
    distractor_id = str(DISTRACTOR["id"])
    assert all(not str(a).startswith(distractor_id) for a in anclajes), (
        "ninguna afirmación puede sostenerse en el documento distractor"
    )
    top = min(store.raw_rows(dbs.HypothesisRow, case_id=case.case_id), key=lambda h: h.rank)
    assert top.failure_mode == "vacuum_leak"
    assert case.decision is ExplanationDecision.SUPPORTED


# --------------------------------------------------------------------------- brazos
@pytest.mark.parametrize(
    ("brazo", "cfg"),
    [
        ("B1", {"use_retrieval": False, "verify_support": False, "abstention_enabled": False}),
        ("B2", {"use_retrieval": True, "verify_support": False, "abstention_enabled": False}),
        ("B3", {"use_retrieval": True, "verify_support": True, "abstention_enabled": True}),
    ],
)
def test_brazos_del_experimento_son_distinguibles(
    tmp_path: Path, brazo: str, cfg: dict[str, bool]
) -> None:
    """Objetivo científico: los tres brazos existen y se comportan como su definición.

    Sin esta comprobación, una comparación entre brazos podría estar midiendo la misma
    configuración tres veces. B1 no recupera nada; B2 recupera y **siempre explica**, aun
    sin evidencia; solo B3 puede abstenerse. La diferencia B2↔B3 en el Escenario B es
    exactamente lo que H-ABS mide.
    """
    store = _store(tmp_path, exclude=FAMILIA_MECANISMO)
    case = _agent(store, **cfg).run(_anomaly(VACUUM))
    runs = store.raw_rows(dbs.AgentRunRow, case_id=case.case_id)
    retrievals = [
        r for r in store.raw_rows(dbs.RetrievalRow, run_id=runs[0].run_id) if r.source == "rag"
    ]

    if brazo == "B1":
        assert not retrievals or not retrievals[0].retrieved_ids
    else:
        assert retrievals, "B2 y B3 deben registrar un evento de recuperación"

    if brazo == "B3":
        assert case.decision is ExplanationDecision.INSUFFICIENT_EVIDENCE
    else:
        assert case.decision is not ExplanationDecision.INSUFFICIENT_EVIDENCE, (
            "sin política de abstención el sistema explica igualmente: es el brazo de control"
        )


# --------------------------------------------------------------------- limitación
def test_sustitucion_por_mecanismo_adyacente_es_un_riesgo_documentado(tmp_path: Path) -> None:
    """Objetivo científico: acotar qué NO garantiza la política de abstención.

    Si del corpus se retira únicamente el documento del mecanismo del caso, pero queda un
    mecanismo **adyacente** que produce la misma firma y sí está documentado, el generador
    puede proponerlo y sostenerlo con evidencia real. El resultado es una explicación
    sustentada y trazable, y aun así un diagnóstico equivocado.

    Esta prueba fija ese comportamiento por escrito, no lo corrige: es precisamente lo que
    la tasa de falsa aceptación (M17) debe medir en el experimento, y la razón por la que
    el corpus C-B se construye retirando la familia del mecanismo y no un solo documento
    (`docs/alineacion_v4/03_diseno_experimental.md` §1.1). La política de suficiencia
    responde por el **soporte** de lo afirmado, nunca por su verdad.
    """
    store = _store(tmp_path, exclude={DOC_MECANISMO})
    assert "doc-maf-drift" in LexicalRetriever(store).document_ids()

    case = _agent(store).run(_anomaly(VACUUM))
    top = min(store.raw_rows(dbs.HypothesisRow, case_id=case.case_id), key=lambda h: h.rank)
    assert top.failure_mode != "vacuum_leak", (
        "sin su documento, el mecanismo del caso no puede ser propuesto desde el corpus"
    )
    if case.decision is ExplanationDecision.SUPPORTED:
        # comportamiento conocido: sustitución sostenida. Debe seguir siendo trazable.
        sustentadas = [c for c in _claims(store, case.case_id) if c.role == "supports"]
        assert all(c.reference_id for c in sustentadas), (
            "aun equivocándose, toda afirmación sustentada conserva su referencia"
        )
