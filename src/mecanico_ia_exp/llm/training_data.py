"""Generación del conjunto de entrenamiento del SLM.

**Se entrena el formato de la tarea, no el contenido del manual.**

La distinción es la que sostiene el experimento central. Si el modelo memorizara
los procedimientos de Mazda, en la condición ABSENT --donde se retira la
evidencia del índice-- los recordaría de sus pesos y explicaría igual, con una
cita de aspecto correcto. El contraste FULL/ABSENT dejaría de medir la evidencia
y pasaría a medir la memoria.

Por eso el texto del manual aparece **solo en la entrada** de cada ejemplo, en la
respuesta de la herramienta, y **nunca en la salida esperada**. Lo que la salida
contiene son identificadores de fragmento, que sin el fragmento delante no dicen
nada.

La salida esperada se construye de la evidencia ya verificada por el pipeline: es
correcta por construcción, no redactada a mano ni generada por otro modelo.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from typing import Any

from mecanico_ia_exp.abstention.sufficiency import SufficiencyVerdict
from mecanico_ia_exp.evidence.model import EvidenceBundle, SupportStatus
from mecanico_ia_exp.llm.agent import (
    SISTEMA,
    _evidencia_para_el_modelo,
    _observaciones_para_el_modelo,
)

#: Formas de enunciar una observación. Varias, para que el modelo aprenda la
#: estructura y no una única frase que repetiría literalmente.
PLANTILLAS_SUBE: tuple[str, ...] = (
    "La señal {senal} presenta un {est} de {valor:.4g}, por encima de lo esperable "
    "en la ventana observada.",
    "El {est} de {senal} alcanza {valor:.4g}, valor superior al habitual en esta "
    "condición de funcionamiento.",
    "Se observa {senal} con {est} de {valor:.4g}, desplazado al alza respecto de lo normal.",
)
PLANTILLAS_BAJA: tuple[str, ...] = (
    "La señal {senal} presenta un {est} de {valor:.4g}, por debajo de lo esperable "
    "en la ventana observada.",
    "El {est} de {senal} se queda en {valor:.4g}, valor inferior al habitual en "
    "esta condición de funcionamiento.",
    "Se observa {senal} con {est} de {valor:.4g}, desplazado a la baja respecto de lo normal.",
)

#: Limitaciones que toda explicación debe declarar. Rotan para que el modelo
#: aprenda a declararlas y no a copiar una.
LIMITACIONES: tuple[str, ...] = (
    "La evidencia sostiene lo observado en las señales; no demuestra la causa.",
    "La atribución indica de qué depende la predicción del modelo, no qué le ocurre al vehículo.",
    "La ventana observada es de 120 s: no se localiza el instante exacto dentro de ella.",
    "El procedimiento citado aplica al motor declarado; no se ha comprobado en "
    "otras motorizaciones.",
)


@dataclass(frozen=True)
class TrainingExample:
    """Un ejemplo en el formato de conversación que espera el ajuste fino."""

    case_id: str
    corpus_variant: str
    decision: str
    messages: list[dict[str, Any]]

    def to_jsonl(self) -> str:
        """Serializa el ejemplo **con su procedencia**.

        Hasta el 4 de septiembre de 2026 solo se escribían los mensajes, y el
        fichero de ajuste no permitía reconstruir de qué ventana ni de qué
        variante de corpus salía cada ejemplo. Sin eso no se puede comparar un
        conjunto regenerado contra el anterior ejemplo a ejemplo, que es
        exactamente lo que exige decidir sobre el adaptador.

        Las claves de procedencia van fuera de `messages`, así que un consumidor
        que solo lea `messages` no cambia de comportamiento.
        """
        return json.dumps(
            {
                "messages": self.messages,
                "example_id": f"{self.case_id}::{self.corpus_variant}",
                "case_id": self.case_id,
                "corpus_variant": self.corpus_variant,
                "decision": self.decision,
            },
            ensure_ascii=False,
        )


def _texto_de_afirmacion(observacion: Any, rng: random.Random) -> str:
    plantillas = PLANTILLAS_SUBE if observacion.direction == "increases" else PLANTILLAS_BAJA
    texto = rng.choice(plantillas).format(
        senal=observacion.signal,
        est=observacion.statistic,
        valor=observacion.value,
    )
    if observacion.window_start_s is not None and observacion.window_end_s is not None:
        texto = texto.rstrip(".") + (
            f", entre los segundos {observacion.window_start_s:.0f} y "
            f"{observacion.window_end_s:.0f} de la sesión."
        )
    return texto


def build_target(
    bundle: EvidenceBundle, verdict: SufficiencyVerdict, rng: random.Random
) -> dict[str, Any]:
    """Construye la salida esperada a partir de la evidencia ya verificada.

    **Una afirmación por observación**, cada una citando *su* observación y los
    fragmentos que la sostienen. Es lo contrario de lo que hace el modelo sin
    ajustar, que cuelga las cinco observaciones de cada afirmación.
    """
    if verdict.decision.value == "ABSTAIN":
        # El motivo es **el primero que emite el verificador, literal**. La
        # primera versión lo traducía a cuatro genéricos ("INSUFFICIENT_EVIDENCE")
        # mientras el prompt mostraba el literal: el modelo ajustado intentaba
        # copiar el prompt y deformaba el identificador ("LOW_CLAIM_COVERDGE").
        # Objetivo y prompt deben decir lo mismo.
        motivo = verdict.reasons[0].value if verdict.reasons else "INSUFFICIENT_EVIDENCE"
        return {
            "decision": "ABSTAIN",
            "reason": motivo,
            "missing_evidence": verdict.missing_evidence[:3],
            "notes": ("No existe evidencia suficiente para sostener una explicación diagnóstica."),
        }

    sostenidas = [c for c in bundle.claims if c.support_status is SupportStatus.SUPPORTED]
    por_id = {o.observation_id: o for o in bundle.observations}
    claims: list[dict[str, Any]] = []
    for i, claim in enumerate(sostenidas, start=1):
        observacion = por_id.get(claim.observation_ids[0]) if claim.observation_ids else None
        if observacion is None:
            continue
        claims.append(
            {
                "claim_id": f"C{i:02d}",
                "text": _texto_de_afirmacion(observacion, rng),
                # Solo SU observación, no todas.
                "observational_evidence": [observacion.observation_id],
                "documentary_evidence": list(claim.chunk_ids[:2]),
            }
        )

    return {
        "decision": "EXPLAIN",
        "diagnosis": f"Condición compatible con {bundle.predicted_class}",
        "confidence": round(bundle.confidence, 2),
        "claims": claims,
        "limitations": rng.sample(LIMITACIONES, k=min(2, len(LIMITACIONES))),
    }


def build_example(
    bundle: EvidenceBundle,
    verdict: SufficiencyVerdict,
    *,
    corpus_variant: str = "FULL",
    seed: int = 0,
) -> TrainingExample | None:
    """Construye un ejemplo completo. Devuelve ``None`` si no es utilizable."""
    rng = random.Random(seed)
    objetivo = build_target(bundle, verdict, rng)

    if objetivo["decision"] == "EXPLAIN" and not objetivo["claims"]:
        # Un EXPLAIN sin afirmaciones enseñaría a producir una explicación vacía.
        return None

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
        {"role": "user", "content": json.dumps(contexto, ensure_ascii=False, indent=1)},
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
        },
        # El texto del manual entra AQUÍ, en la entrada. Nunca en la salida.
        {
            "role": "tool",
            "name": "retrieve_evidence",
            "content": json.dumps(evidencia, ensure_ascii=False),
        },
        {"role": "assistant", "content": json.dumps(objetivo, ensure_ascii=False)},
    ]
    return TrainingExample(
        case_id=bundle.case_id,
        corpus_variant=corpus_variant,
        decision=str(objetivo["decision"]),
        messages=mensajes,
    )


def verify_no_manual_content_in_targets(ejemplos: list[TrainingExample]) -> list[str]:
    """Comprueba que ninguna salida esperada contiene texto del manual.

    Es la garantía que sostiene el experimento central, y se comprueba en lugar
    de confiar en haberlo hecho bien. Se busca solapamiento literal largo entre
    la respuesta de la herramienta y la salida esperada.
    """
    problemas: list[str] = []
    for ejemplo in ejemplos:
        fuente = next((m["content"] for m in ejemplo.messages if m.get("role") == "tool"), "")
        objetivo = ejemplo.messages[-1]["content"]
        # Secuencias de ocho palabras o más compartidas entre entrada y salida.
        palabras_fuente = fuente.split()
        ngramas = {
            " ".join(palabras_fuente[i : i + 8]) for i in range(max(0, len(palabras_fuente) - 7))
        }
        palabras_objetivo = objetivo.split()
        for i in range(max(0, len(palabras_objetivo) - 7)):
            fragmento = " ".join(palabras_objetivo[i : i + 8])
            if fragmento in ngramas:
                problemas.append(f"{ejemplo.case_id}: la salida repite «{fragmento[:60]}…»")
                break
    return problemas
