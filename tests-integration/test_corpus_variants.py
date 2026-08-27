"""Pruebas del corpus C-A y de sus variantes de disponibilidad de evidencia (R3, PI v4).

Cada prueba declara el objetivo científico que sostiene. El conjunto verifica que la
**variable independiente principal** del experimento central está bien construida: que la
evidencia está donde debe estar en el Escenario A, que no está en el Escenario B, y que la
diferencia entre ambos no puede detectarse por una señal superficial.
"""

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).parents[1]
CORPUS_DIR = REPO_ROOT / "diagnostic-agent" / "knowledge" / "corpus_v2"
BUILD_DIR = CORPUS_DIR / "build"
FREEZE = REPO_ROOT / "ai-models" / "configs" / "corpus-v2-freeze.json"

sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "diagnostic-agent" / "src"))

pytestmark = pytest.mark.skipif(
    not FREEZE.exists() or not BUILD_DIR.exists(),
    reason="corpus v2 no construido (make corpus-build)",
)

#: Consultas por SÍNTOMA, nunca por el nombre del fallo: usar el nombre reproduciría la
#: circularidad que invalidó el corpus v1 (auditoría R3 §2.1 y §5.5).
CONSULTAS_POR_SINTOMA = {
    "vacuum_leak": (
        "ajustes de combustible positivos mucho mayores en ralenti presion del colector "
        "alta regimen inestable"
    ),
    "maf_drift": (
        "correccion de combustible positiva tambien a velocidad de crucero flujo de aire "
        "inferior al esperado para regimen y carga"
    ),
    "o2_lag": (
        "senal de la sonda de oxigeno amortiguada transiciones lentas ajuste a corto plazo "
        "con mucha dispersion"
    ),
    "thermostat_stuck": (
        "temperatura del refrigerante estabilizada por debajo de la banda de regulacion "
        "tras conduccion suficiente"
    ),
    "misfire": (
        "caidas breves y abruptas del regimen con reaccion de la carga y excursiones de la "
        "sonda de oxigeno"
    ),
}


def _load_manifest() -> dict[str, Any]:
    return json.loads(FREEZE.read_text(encoding="utf-8"))


def _load_chunks(variant: str) -> list[tuple[str, str]]:
    payload = yaml.safe_load((BUILD_DIR / f"{variant}.yaml").read_text(encoding="utf-8"))
    return [
        (f"{doc['document_id']}#{chunk['seq']}", chunk["text"])
        for doc in payload["documents"]
        for chunk in doc["chunks"]
    ]


def _search(chunks: list[tuple[str, str]], query: str, k: int = 3) -> list[str]:
    """Misma puntuación léxica que ``LexicalRetriever``, sin necesidad de base de datos."""
    from diagnostic_agent.reasoning.rag.retriever import _tokens

    q = Counter(_tokens(query))
    scored: list[tuple[str, float]] = []
    for chunk_id, text in chunks:
        c = Counter(_tokens(text))
        overlap = sum(min(q[t], c[t]) for t in q)
        denom = (sum(q.values()) * max(1, len(c))) ** 0.5
        if denom and overlap:
            scored.append((chunk_id, overlap / denom))
    scored.sort(key=lambda x: -x[1])
    return [chunk_id for chunk_id, _ in scored[:k]]


def test_congelacion_intacta() -> None:
    """El corpus congelado no ha cambiado: reproducibilidad del experimento."""
    from build_corpus import verify

    ok, problems = verify()
    assert ok, f"corpus alterado respecto al manifiesto: {problems}"


def test_corpus_suficientemente_grande() -> None:
    """top_k=3 debe ser informativo: la auditoría R3 §2.2 lo exigía sobre 7 chunks."""
    manifest = _load_manifest()
    chunks = manifest["variants"]["corpus-CA"]["chunks"]
    assert chunks >= 300, f"C-A tiene {chunks} chunks; con top_k=3 el ranking no discrimina"


def test_ningun_documento_declara_modo_de_fallo() -> None:
    """Anti-circularidad: el corpus no puede llevar la clave de respuestas en metadatos."""
    payload = yaml.safe_load((BUILD_DIR / "corpus-CA.yaml").read_text(encoding="utf-8"))
    for document in payload["documents"]:
        assert "failure_mode" not in document["metadata"], document["document_id"]


@pytest.mark.parametrize("mechanism", sorted(CONSULTAS_POR_SINTOMA))
def test_escenario_a_recupera_evidencia_pertinente(mechanism: str) -> None:
    """Escenario A: con C-A, la consulta por síntoma recupera evidencia de referencia.

    Objetivo científico: valida que M3/M4 pueden ser distintos de cero, es decir, que el
    Escenario A es realmente una condición de evidencia suficiente.
    """
    referencia = set(_load_manifest()["evidence_reference"]["by_mechanism"][mechanism])
    recuperado = _search(_load_chunks("corpus-CA"), CONSULTAS_POR_SINTOMA[mechanism])
    assert referencia & set(recuperado), (
        f"{mechanism}: ningún chunk de referencia entre los 3 primeros de C-A"
    )


@pytest.mark.parametrize("mechanism", sorted(CONSULTAS_POR_SINTOMA))
def test_escenario_b_sin_evidencia_pertinente(mechanism: str) -> None:
    """Escenario B: con C-B, ningún chunk recuperado pertenece a la evidencia de referencia.

    Objetivo científico: es la verificación del control de disponibilidad. La métrica M6
    vale 1 por construcción en el Escenario B; si esta prueba fallara, el contraste entre
    escenarios no mediría lo que afirma medir.
    """
    referencia = set(_load_manifest()["evidence_reference"]["by_mechanism"][mechanism])
    recuperado = _search(_load_chunks(f"corpus-CB-{mechanism}"), CONSULTAS_POR_SINTOMA[mechanism])
    assert not (referencia & set(recuperado)), (
        f"{mechanism}: C-B devuelve evidencia de referencia; la exclusión no es efectiva"
    )


@pytest.mark.parametrize("mechanism", sorted(CONSULTAS_POR_SINTOMA))
def test_escenario_b_duro_recupera_pero_no_lo_causal(mechanism: str) -> None:
    """Escenario B duro: C-B′ devuelve resultados, pero ninguno es un documento causal.

    Objetivo científico: separa «no recupera nada, luego se abstiene» de «recupera algo
    irrelevante y sabe que no le basta», que es la condición decisiva de H-ABS.
    """
    causal = set(
        yaml.safe_load((CORPUS_DIR / "mechanisms.yaml").read_text(encoding="utf-8"))["mechanisms"][
            mechanism
        ]["causal"]
    )
    recuperado = _search(_load_chunks(f"corpus-CBp-{mechanism}"), CONSULTAS_POR_SINTOMA[mechanism])
    assert recuperado, f"{mechanism}: C-B′ no devuelve nada; debe devolver material no concluyente"
    assert not {chunk_id.split("#")[0] for chunk_id in recuperado} & causal, (
        f"{mechanism}: C-B′ conserva un documento causal"
    )


def test_variantes_indistinguibles_por_tamano() -> None:
    """La exclusión no puede detectarse por el tamaño del corpus.

    Objetivo científico: mitiga la amenaza a la validez nº 5. Si C-B fuese notablemente más
    corto, el sistema podría abstenerse por esa señal superficial y no por la evidencia.
    """
    variants = _load_manifest()["variants"]
    counts = {name: entry["chunks"] for name, entry in variants.items()}
    assert len(set(counts.values())) == 1, f"recuentos de chunks desiguales: {counts}"


def test_evidencia_de_referencia_cubre_los_mecanismos_del_banco() -> None:
    """Todo mecanismo con caso en el banco congelado tiene evidencia de referencia."""
    cases = yaml.safe_load(
        (REPO_ROOT / "benchmarks" / "agent-diagnostics" / "cases_v2.yaml").read_text("utf-8")
    )
    del_banco = {
        case["ground_truth"]["failure_mode"]
        for case in cases["cases"]
        if case["ground_truth"]["failure_mode"]
    }
    declarados = set(_load_manifest()["evidence_reference"]["by_mechanism"])
    assert del_banco <= declarados, f"sin evidencia de referencia: {del_banco - declarados}"
