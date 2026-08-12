"""Generación de hipótesis: interfaz plugable con dos implementaciones (ADR-0014).

- ``OllamaHypothesizer``: LLM local real (salida JSON validada con reintento acotado).
- ``HeuristicHypothesizer``: determinista, construye hipótesis desde los fragmentos
  recuperados (metadata ``failure_mode``); permite CI y experimentos reproducibles sin
  LLM, y sirve de baseline "sin LLM" para el estudio comparativo.

El nodo ``hypothesize`` no decide nada más: propone. La verificación es de ``verify``.
"""

import json
import uuid
from typing import Any, Protocol

import httpx

from mecanico_contracts import DiagnosticHypothesis

PROMPT_VERSION = "p1"

_PROMPT_TEMPLATE = """Eres el módulo generador de hipótesis de un sistema de diagnóstico vehicular.
Anomalía detectada por un modelo matemático (no por ti):
- PIDs implicados: {pids}
- Features de la ventana (nombre=valor): {features}
- DTCs activos: {dtcs}
Documentación técnica recuperada:
{context}

Genera hasta {max_h} hipótesis de causa raíz DISTINTAS. Responde SOLO JSON válido:
{{"hypotheses": [{{"suspected_component": str, "failure_mode": str, "cause": str,
"mechanism": str, "confidence": float 0..1}}]}}
Si la documentación no cubre los síntomas, incluye una única hipótesis con
failure_mode="unknown_relational" y dilo explícitamente en "cause"."""


class Hypothesizer(Protocol):
    """Interfaz del generador de hipótesis."""

    name: str

    def generate(
        self,
        pids: list[str],
        features: dict[str, float],
        dtcs: list[str],
        context_chunks: list[tuple[str, str, dict[str, str]]],
        max_hypotheses: int = 3,
    ) -> tuple[list[DiagnosticHypothesis], dict[str, Any]]:
        """Devuelve (hipótesis, métricas: tokens/latencia si aplican)."""
        ...


def _mk(component: str, mode: str, cause: str, mechanism: str, conf: float) -> DiagnosticHypothesis:
    return DiagnosticHypothesis(
        hypothesis_id=str(uuid.uuid4()),
        suspected_component=component,
        failure_mode=mode,
        cause=cause,
        mechanism=mechanism,
        confidence=max(0.0, min(1.0, conf)),
    )


class HeuristicHypothesizer:
    """Determinista: una hipótesis por failure_mode recuperado, ponderada por el score RAG."""

    name = "heuristic"

    def generate(
        self,
        pids: list[str],
        features: dict[str, float],
        dtcs: list[str],
        context_chunks: list[tuple[str, str, dict[str, str]]],
        max_hypotheses: int = 3,
    ) -> tuple[list[DiagnosticHypothesis], dict[str, Any]]:
        out: list[DiagnosticHypothesis] = []
        seen: set[str] = set()
        for chunk_id, text, meta in context_chunks:
            mode = meta.get("failure_mode", "")
            if not mode or mode in seen or mode == "reference":
                continue
            seen.add(mode)
            first_sentence = text.strip().split(".")[0][:220]
            out.append(
                _mk(
                    meta.get("component", "indeterminado"),
                    mode,
                    f"Compatible con: {first_sentence}",
                    f"Según ficha {chunk_id}: los síntomas en {', '.join(pids[:3])} "
                    "coinciden con la firma documentada de este modo de fallo.",
                    0.5,
                )
            )
            if len(out) >= max_hypotheses:
                break
        if not out:
            out.append(
                _mk(
                    "indeterminado",
                    "unknown_relational",
                    "Patrón no cubierto por la documentación disponible",
                    "La anomalía es multivariable y ningún modo de fallo documentado "
                    "coincide con su firma; se registra para consolidación futura.",
                    0.3,
                )
            )
        return out, {"generator": self.name}


class OllamaHypothesizer:
    """LLM local vía Ollama con salida JSON validada y reintento acotado."""

    def __init__(self, host: str, model: str, max_retries: int = 2) -> None:
        self.host = host
        self.model = model
        self.max_retries = max_retries
        self.name = f"ollama:{model}"

    def generate(
        self,
        pids: list[str],
        features: dict[str, float],
        dtcs: list[str],
        context_chunks: list[tuple[str, str, dict[str, str]]],
        max_hypotheses: int = 3,
    ) -> tuple[list[DiagnosticHypothesis], dict[str, Any]]:
        context = "\n---\n".join(f"[{cid}] {text[:600]}" for cid, text, _ in context_chunks)
        compact = {k: round(v, 2) for k, v in features.items() if abs(v) > 1e-9}
        prompt = _PROMPT_TEMPLATE.format(
            pids=", ".join(pids),
            features=json.dumps(compact, ensure_ascii=False)[:1200],
            dtcs=", ".join(dtcs) or "ninguno",
            context=context,
            max_h=max_hypotheses,
        )
        metrics: dict[str, Any] = {"generator": self.name}
        for _attempt in range(1 + self.max_retries):
            r = httpx.post(
                f"{self.host}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "format": "json"},
                timeout=300,
            )
            r.raise_for_status()
            body = r.json()
            metrics["tokens_in"] = body.get("prompt_eval_count")
            metrics["tokens_out"] = body.get("eval_count")
            try:
                parsed = json.loads(body.get("response", ""))
                hyps = [
                    _mk(
                        str(h["suspected_component"]),
                        str(h["failure_mode"]),
                        str(h["cause"]),
                        str(h["mechanism"]),
                        float(h["confidence"]),
                    )
                    for h in parsed["hypotheses"][:max_hypotheses]
                ]
                if hyps:
                    return hyps, metrics
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue
        # Degradación honesta: sin salida válida del LLM no se inventa nada.
        return (
            [
                _mk(
                    "indeterminado",
                    "unknown_relational",
                    "El generador LLM no produjo hipótesis válidas",
                    "Tras reintentos, la salida no cumplió el esquema; el caso queda "
                    "inconcluso y registrado.",
                    0.1,
                )
            ],
            metrics,
        )
