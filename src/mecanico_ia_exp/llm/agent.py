"""El agente: herramientas, recuperación y redacción.

**Reparto de responsabilidades, y no es negociable.**

| Quién | Qué hace |
|---|---|
| Modelo especializado | Diagnostica a partir de OBD-II |
| Atribución | Convierte la predicción en observaciones localizadas |
| Herramienta de recuperación | Trae evidencia documental del vehículo |
| Verificador determinista | Decide EXPLAIN o ABSTAIN |
| **Modelo de lenguaje** | **Redacta la decisión ya tomada** |

El modelo de lenguaje no diagnostica, no decide si hay evidencia suficiente y no
aporta conocimiento propio como fuente. Si decidiera él, la respuesta a la
pregunta de investigación dependería de su disposición a admitir que no sabe algo.

Lo que sí hace, y es medible: **respetar o no el veredicto**. Un modelo al que se
le dice «la evidencia no basta» y aun así explica está fabricando una hipótesis
sin fundamento, que es exactamente lo que el trabajo busca detectar. Se mide.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from mecanico_ia_exp.abstention.sufficiency import SufficiencyVerdict
from mecanico_ia_exp.evidence.model import EvidenceBundle
from mecanico_ia_exp.llm.provider import LLMProvider, LLMResponse
from mecanico_ia_exp.llm.schema import (
    AbstainOutput,
    AgentOutput,
    ExplainOutput,
    verify_citations,
)

#: Herramienta que el modelo puede invocar. Es la única.
HERRAMIENTA_RECUPERAR: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "retrieve_evidence",
        "description": (
            "Recupera fragmentos del manual de taller del vehículo analizado. "
            "Devuelve únicamente documentación aplicable a ese vehículo y motor. "
            "Es la ÚNICA fuente de evidencia documental admisible."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "dtc": {
                    "type": "string",
                    "description": "Código de diagnóstico a buscar, por ejemplo P2187",
                },
                "query": {
                    "type": "string",
                    "description": "Descripción de lo observado en las señales",
                },
            },
            "required": ["query"],
        },
    },
}

SISTEMA = """Eres el módulo de redacción de un sistema de diagnóstico de vehículos.

NO diagnosticas: el diagnóstico ya lo ha emitido un modelo especializado.
NO decides si la evidencia basta: esa decisión ya está tomada y se te comunica.
NO aportas conocimiento propio: tu conocimiento del automóvil no es una fuente.

Tu trabajo es redactar la decisión tomada, anclando cada afirmación en la
evidencia que se te entrega.

REGLAS

1. Cita ÚNICAMENTE los identificadores que aparecen en la evidencia entregada.
   Inventar un identificador con forma correcta es el peor fallo posible.
2. Cada afirmación lleva al menos una observación Y al menos un fragmento.
3. Enuncia lo OBSERVADO, no la causa. «Los ajustes de combustible están
   desplazados» es correcto. «Hay una fuga de vacío» no lo es: la evidencia
   sostiene observaciones, no causas demostradas.
4. Si el veredicto es ABSTAIN, responde con la forma ABSTAIN. No expliques.
   Abstenerse es una respuesta correcta, no un fallo.
5. Responde SOLO con JSON, sin texto alrededor.

FORMATO SI EXPLICAS
{"decision":"EXPLAIN","diagnosis":"<máx. 200 caracteres>","confidence":<0-1>,
 "claims":[{"claim_id":"C01","text":"<máx. 600 caracteres>",
 "observational_evidence":["OBS001"],"documentary_evidence":["<chunk_id>"]}],
 "limitations":["<lo que la evidencia no permite afirmar>"]}

FORMATO SI TE ABSTIENES
{"decision":"ABSTAIN","reason":"INSUFFICIENT_EVIDENCE",
 "missing_evidence":["<qué faltó>"],"notes":""}"""


@dataclass
class AgentRun:
    """Una ejecución completa, con todo lo necesario para auditarla."""

    case_id: str
    verdict: SufficiencyVerdict
    output: AgentOutput | None
    raw: LLMResponse | None
    fake_citations: list[str] = field(default_factory=list)
    schema_error: str = ""
    respected_verdict: bool = True
    """¿La forma de la salida coincide con la decisión del verificador?"""

    @property
    def valid(self) -> bool:
        return self.output is not None and not self.fake_citations

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "verdict": self.verdict.decision.value,
            "output": self.output.model_dump(mode="json") if self.output else None,
            "fake_citations": self.fake_citations,
            "schema_error": self.schema_error,
            "respected_verdict": self.respected_verdict,
            "valid": self.valid,
            "llm": self.raw.identity.as_dict() if self.raw else None,
            "latency_s": round(self.raw.latency_s, 2) if self.raw else None,
        }


def _evidencia_para_el_modelo(bundle: EvidenceBundle) -> list[dict[str, Any]]:
    """Lo que la herramienta devuelve: solo lo aplicable, con su procedencia.

    Se recorta el texto: un fragmento entero por cada uno agotaría la ventana de
    contexto de un modelo pequeño y empujaría fuera las instrucciones, que es
    donde están las reglas que debe respetar.
    """
    return [
        {
            "chunk_id": d.chunk_id,
            "section": d.section,
            "page": d.page_start,
            "publisher": d.publisher,
            "dtc_codes": list(d.dtc_codes),
            "applicability": d.applicability,
            "text": " ".join(d.text.split())[:500],
        }
        for d in bundle.documents
        if d.applicability == "EXACT_MATCH"
    ]


def _observaciones_para_el_modelo(bundle: EvidenceBundle) -> list[dict[str, Any]]:
    return [
        {
            "observation_id": o.observation_id,
            "signal": o.signal,
            "statistic": o.statistic,
            "value": round(o.value, 4),
            "direction": o.direction,
            "window": f"{o.window_start_s:.0f}-{o.window_end_s:.0f} s"
            if o.window_start_s is not None
            else None,
        }
        for o in bundle.observations
    ]


def run_agent(
    provider: LLMProvider,
    bundle: EvidenceBundle,
    verdict: SufficiencyVerdict,
    *,
    use_tools: bool = True,
) -> AgentRun:
    """Ejecuta el agente sobre un caso ya verificado."""
    observaciones = _observaciones_para_el_modelo(bundle)
    evidencia = _evidencia_para_el_modelo(bundle)

    contexto = {
        "vehicle": bundle.vehicle_id,
        "model_diagnosis": bundle.predicted_class,
        "model_confidence": round(bundle.confidence, 3),
        "sufficiency_verdict": verdict.decision.value,
        "verdict_reasons": [r.value for r in verdict.reasons],
        "observations": observaciones,
    }

    mensajes: list[dict[str, Any]] = [
        {"role": "system", "content": SISTEMA},
        {
            "role": "user",
            "content": json.dumps(contexto, ensure_ascii=False, indent=1),
        },
    ]

    if use_tools:
        # La llamada a la herramienta es real: el modelo la pide y se le
        # responde con lo recuperado. Lo que NO se le permite es citar algo que
        # no venga por esa vía.
        mensajes.append(
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "function": {
                            "name": "retrieve_evidence",
                            "arguments": {"query": bundle.predicted_class},
                        }
                    }
                ],
            }
        )
        mensajes.append(
            {
                "role": "tool",
                "name": "retrieve_evidence",
                "content": json.dumps(evidencia, ensure_ascii=False),
            }
        )
    else:
        mensajes[-1]["content"] += "\n\nEVIDENCIA:\n" + json.dumps(evidencia, ensure_ascii=False)

    respuesta = provider.complete(mensajes, tools=[HERRAMIENTA_RECUPERAR] if use_tools else None)

    ejecucion = AgentRun(case_id=bundle.case_id, verdict=verdict, output=None, raw=respuesta)
    try:
        crudo = respuesta.as_json()
    except ValueError as error:
        ejecucion.schema_error = f"sin JSON en la respuesta: {error}"
        return ejecucion

    decision = str(crudo.get("decision", "")).upper()
    try:
        salida: AgentOutput = (
            AbstainOutput.model_validate(crudo)
            if decision == "ABSTAIN"
            else ExplainOutput.model_validate(crudo)
        )
    except Exception as error:  # validación de Pydantic
        ejecucion.schema_error = str(error).split("\n")[0]
        return ejecucion

    ejecucion.output = salida
    ejecucion.respected_verdict = decision == verdict.decision.value
    ejecucion.fake_citations = verify_citations(
        salida,
        available_chunks={d["chunk_id"] for d in evidencia},
        available_observations={o["observation_id"] for o in observaciones},
    )
    return ejecucion
