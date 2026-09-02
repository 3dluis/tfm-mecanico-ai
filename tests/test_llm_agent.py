"""Esquema del agente, barrera contra citas inventadas, proveedores y datos de ajuste."""

from __future__ import annotations

import json
import random

import pytest

from mecanico_ia_exp.abstention.sufficiency import (
    Decision as VerdictDecision,
)
from mecanico_ia_exp.abstention.sufficiency import (
    Reason,
    Sufficiency,
    SufficiencyVerdict,
)
from mecanico_ia_exp.evidence.model import (
    Claim,
    DocumentaryEvidence,
    EvidenceBundle,
    Observation,
    SupportStatus,
)
from mecanico_ia_exp.llm.agent import run_agent
from mecanico_ia_exp.llm.provider import EchoProvider, LLMResponse, get_llm
from mecanico_ia_exp.llm.schema import (
    AbstainOutput,
    ExplainOutput,
    verify_citations,
)
from mecanico_ia_exp.llm.training_data import (
    build_example,
    build_target,
    verify_no_manual_content_in_targets,
)


def _obs(oid: str = "OBS001") -> Observation:
    return Observation(
        observation_id=oid,
        signal="stft_bank1",
        statistic="mean",
        value=6.2,
        direction="increases",
        importance=0.4,
        session_id="s1",
        window_start_s=120.0,
        window_end_s=239.0,
    )


def _doc(chunk_id: str = "ch1", aplicabilidad: str = "EXACT_MATCH") -> DocumentaryEvidence:
    return DocumentaryEvidence(
        chunk_id=chunk_id,
        document_id="manual",
        vehicle_id="v",
        text="DTC P2187 Fuel system too lean at idle. PCM monitors short term fuel trim.",
        score=0.5,
        applicability=aplicabilidad,
        document_type="WORKSHOP_MANUAL",
        publisher="Mazda",
        section="DTC P2187 [ZJ, Z6]",
        page_start=1,
        dtc_codes=("P2187",),
    )


def _bundle(con_docs: bool = True) -> EvidenceBundle:
    docs = [_doc("ch1"), _doc("ch2")] if con_docs else []
    claims = [Claim("C01", "t", ("OBS001",), ("ch1",), SupportStatus.SUPPORTED)] if con_docs else []
    return EvidenceBundle(
        case_id="c1",
        vehicle_id="v",
        predicted_class="F01_vacuum_leak",
        model_confidence=0.9,
        calibrated_confidence=0.9,
        observations=[_obs()],
        documents=docs,
        claims=claims,
    )


def _veredicto(decision: str) -> SufficiencyVerdict:
    if decision == "EXPLAIN":
        return SufficiencyVerdict("c1", Sufficiency.SUPPORTED, VerdictDecision.EXPLAIN)
    return SufficiencyVerdict(
        "c1",
        Sufficiency.INSUFFICIENT_EVIDENCE,
        VerdictDecision.ABSTAIN,
        reasons=[Reason.NO_DOCUMENTARY_EVIDENCE],
        missing_evidence=["ningún fragmento aplicable"],
    )


# ------------------------------------------------------------------ esquema


def test_la_abstencion_es_una_forma_valida_del_esquema() -> None:
    """Si solo pudiera explicar, abstenerse le exigiría desobedecer el formato."""
    salida = AbstainOutput.model_validate(
        {
            "decision": "ABSTAIN",
            "reason": "INSUFFICIENT_EVIDENCE",
            "missing_evidence": ["x"],
        }
    )
    assert salida.decision.value == "ABSTAIN"


def test_una_afirmacion_causal_se_rechaza() -> None:
    """La evidencia sostiene observaciones, no causas demostradas."""
    with pytest.raises(ValueError, match="causa demostrada"):
        ExplainOutput.model_validate(
            {
                "decision": "EXPLAIN",
                "diagnosis": "condición observada",
                "confidence": 0.5,
                "claims": [
                    {
                        "claim_id": "C01",
                        "text": "El fallo está causado por una fuga de vacío en el colector.",
                        "observational_evidence": ["OBS001"],
                        "documentary_evidence": ["ch1"],
                    }
                ],
            }
        )


def test_una_afirmacion_observacional_se_admite() -> None:
    salida = ExplainOutput.model_validate(
        {
            "decision": "EXPLAIN",
            "diagnosis": "condición observada",
            "confidence": 0.5,
            "claims": [
                {
                    "claim_id": "C01",
                    "text": "Los ajustes de combustible están desplazados al alza en la ventana.",
                    "observational_evidence": ["OBS001"],
                    "documentary_evidence": ["ch1"],
                }
            ],
        }
    )
    assert len(salida.claims) == 1


def test_identificadores_de_afirmacion_repetidos_se_rechazan() -> None:
    claim = {
        "claim_id": "C01",
        "text": "Texto suficientemente largo aquí.",
        "observational_evidence": ["OBS001"],
        "documentary_evidence": ["ch1"],
    }
    with pytest.raises(ValueError, match="repetidos"):
        ExplainOutput.model_validate(
            {
                "decision": "EXPLAIN",
                "diagnosis": "condición observada",
                "confidence": 0.5,
                "claims": [claim, claim],
            }
        )


# ---------------------------------------------------------- citas inventadas


def test_no_fake_citations() -> None:
    """Un identificador con la forma correcta que no corresponde a nada se
    parece a una cita y resuelve a la nada. Debe detectarse."""
    salida = ExplainOutput.model_validate(
        {
            "decision": "EXPLAIN",
            "diagnosis": "condición observada",
            "confidence": 0.5,
            "claims": [
                {
                    "claim_id": "C01",
                    "text": "Texto suficientemente largo aquí.",
                    "observational_evidence": ["OBS001", "OBS999"],
                    "documentary_evidence": ["ch1", "ch:inventado"],
                }
            ],
        }
    )
    inventadas = verify_citations(
        salida, available_chunks={"ch1"}, available_observations={"OBS001"}
    )
    assert len(inventadas) == 2
    assert any("ch:inventado" in i for i in inventadas)
    assert any("OBS999" in i for i in inventadas)


def test_una_abstencion_no_cita_nada_y_no_puede_inventar() -> None:
    salida = AbstainOutput(reason="INSUFFICIENT_EVIDENCE")  # type: ignore[arg-type]
    assert verify_citations(salida, available_chunks=set(), available_observations=set()) == []


# ------------------------------------------------------------- proveedores


def test_el_proveedor_por_defecto_no_necesita_modelo() -> None:
    assert isinstance(get_llm(), EchoProvider)


def test_un_proveedor_desconocido_se_rechaza() -> None:
    with pytest.raises(ValueError, match="desconocido"):
        get_llm("inexistente")


def test_la_identidad_registra_lo_reproducible() -> None:
    datos = EchoProvider().identity.as_dict()
    assert set(datos) >= {"llm_provider", "llm_model", "temperature", "prompt_version"}


def test_se_extrae_el_json_aunque_venga_envuelto() -> None:
    """Un modelo pequeño envuelve el JSON en texto o vallas con frecuencia."""
    r = LLMResponse(
        text='Aquí va:\n```json\n{"decision": "ABSTAIN", "a": {"b": 1}}\n```',
        identity=EchoProvider().identity,
    )
    assert r.as_json()["decision"] == "ABSTAIN"


def test_sin_json_falla_con_mensaje_claro() -> None:
    r = LLMResponse(text="no hay nada", identity=EchoProvider().identity)
    with pytest.raises(ValueError, match="JSON"):
        r.as_json()


# ------------------------------------------------------------------ agente


def test_el_agente_con_evidencia_explica_y_cita_lo_entregado() -> None:
    ejecucion = run_agent(EchoProvider(), _bundle(True), _veredicto("EXPLAIN"))
    assert ejecucion.valid
    assert ejecucion.respected_verdict
    assert ejecucion.fake_citations == []


def test_el_agente_sin_evidencia_se_abstiene() -> None:
    ejecucion = run_agent(EchoProvider(), _bundle(False), _veredicto("ABSTAIN"))
    assert ejecucion.valid
    assert isinstance(ejecucion.output, AbstainOutput)
    assert ejecucion.respected_verdict


def test_se_detecta_cuando_el_agente_no_respeta_el_veredicto() -> None:
    """La plantilla explica siempre que hay evidencia, aunque el veredicto diga
    ABSTAIN. Eso debe quedar medido, no oculto."""
    ejecucion = run_agent(EchoProvider(), _bundle(True), _veredicto("ABSTAIN"))
    assert ejecucion.output is not None
    assert ejecucion.respected_verdict is False


def test_el_agente_solo_recibe_evidencia_aplicable() -> None:
    """Un fragmento de otro motor no debe llegar al modelo ni como contexto."""
    bundle = _bundle(True)
    bundle.documents.append(_doc("lf1", "PARTIAL_MATCH"))
    ejecucion = run_agent(EchoProvider(), bundle, _veredicto("EXPLAIN"))
    assert ejecucion.output is not None
    entregados = {
        m for m in ejecucion.raw.text.split('"') if m.startswith("ch") or m.startswith("lf")
    }
    assert "lf1" not in entregados


# ------------------------------------------------------- datos de ajuste


def test_la_salida_esperada_ancla_una_afirmacion_por_observacion() -> None:
    """Lo contrario de lo que hace el modelo sin ajustar, que cuelga todas las
    observaciones de cada afirmación."""
    objetivo = build_target(_bundle(True), _veredicto("EXPLAIN"), random.Random(0))
    assert objetivo["decision"] == "EXPLAIN"
    for claim in objetivo["claims"]:
        assert len(claim["observational_evidence"]) == 1


def test_la_salida_esperada_respeta_el_veredicto_de_abstencion() -> None:
    objetivo = build_target(_bundle(True), _veredicto("ABSTAIN"), random.Random(0))
    assert objetivo["decision"] == "ABSTAIN"
    assert "claims" not in objetivo


def test_el_texto_del_manual_va_en_la_entrada_y_nunca_en_la_salida() -> None:
    """La garantía que sostiene el experimento central, comprobada."""
    ejemplo = build_example(_bundle(True), _veredicto("EXPLAIN"))
    assert ejemplo is not None
    herramienta = next(m for m in ejemplo.messages if m["role"] == "tool")
    assert "Fuel system too lean" in herramienta["content"]
    assert "Fuel system too lean" not in ejemplo.messages[-1]["content"]
    assert verify_no_manual_content_in_targets([ejemplo]) == []


def test_un_explain_sin_afirmaciones_no_genera_ejemplo() -> None:
    """Enseñaría a producir una explicación vacía."""
    bundle = _bundle(True)
    bundle.claims = []
    assert build_example(bundle, _veredicto("EXPLAIN")) is None


def test_la_deteccion_de_fuga_atrapa_una_copia_literal() -> None:
    ejemplo = build_example(_bundle(True), _veredicto("EXPLAIN"))
    assert ejemplo is not None
    # Se copia un trozo largo del manual a la salida, a propósito.
    herramienta = next(m for m in ejemplo.messages if m["role"] == "tool")
    trozo = " ".join(json.loads(herramienta["content"])[0]["text"].split()[:10])
    ejemplo.messages[-1]["content"] += " " + trozo
    assert verify_no_manual_content_in_targets([ejemplo])
