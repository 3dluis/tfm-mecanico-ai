"""Runner del benchmark agent-diagnostics (R2) — harness CONTROLADO, sin runtime multiagente.

Ejecuta los 6 casos pre-registrados de ``benchmarks/agent-diagnostics/cases_v1.yaml``
contra UN LLM local (tras superar el smoke profundo). Deliberadamente NO usa el
Supervisor ni múltiples llamadas por caso (decisión R2 §11): una llamada por caso con
contexto ESTRUCTURADO (context builder cb:1 — nunca telemetría cruda) para entender el
comportamiento base del modelo.

REGLA: cases_v1.yaml es INMUTABLE tras observar resultados; ampliaciones = cases_v2.

Puntuación automática (lo subjetivo queda marcado para revisión humana):
- diagnóstico: top-1 / top-3 contra acceptable_hypotheses; ranking registrado
- resultado: match con expected_outcome (INCONCLUSIVE obligatorio donde toca)
- seguridad: ``unsupported_certainty`` = ERROR explícito si confianza>0.6 cuando el
  caso esperaba inconclusive/insufficient_data (un modelo que siempre da causa
  convincente se penaliza)
- grounding: cobertura de expected_evidence por solape de términos (heurística
  DOCUMENTADA y aproximada; la revisión fina es humana)
- structured output: cumplimiento del esquema JSON
- edge: latencia, tokens/s, tokens de prompt

Uso (en el Mac, con Ollama):
    python tools/bench_agent_diagnostics.py --model qwen2.5:3b-instruct-q4_K_M
"""

import argparse
import json
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import yaml

REPO_ROOT = Path(__file__).parents[1]
CASES = REPO_ROOT / "benchmarks" / "agent-diagnostics" / "cases_v1.yaml"
OUT = REPO_ROOT / "ai-models" / "experiments" / "bench_agent_diagnostics.jsonl"

CONTEXT_BUILDER_VERSION = "cb:1"
#: El harness v1 no expone herramientas: BENCH-002 (que pediría medición dirigida)
#: admite también 'inconclusive' como resultado correcto. Documentado, no se edita el YAML.
OUTCOME_ALTERNATIVES = {"BENCH-002": {"probable", "inconclusive"}}

CORPUS_SNIPPET = (
    "corpus_v1: 'una fuga de vacío produce mezcla pobre: trims positivos sostenidos, MAP "
    "elevado y ralentí inestable; la deriva de MAF produce trims positivos SIN MAP elevado "
    "en ralentí; el termostato abierto impide alcanzar temperatura de régimen'"
)

SCHEMA_HINT = """{"hipotesis": [{"failure_mode": str, "confianza": float 0..1,
  "mecanismo": str}],
 "resultado": "probable"|"inconclusive"|"insufficient_data",
 "evidencias_citadas": [str],
 "informacion_faltante": str|null}"""


def build_context(case: dict[str, Any]) -> str:
    """Context builder cb:1: contexto diagnóstico estructurado, nunca telemetría cruda."""
    sc = case["scenario"]
    return (
        f"vehicle_context: gasolina, 4 cilindros\n"
        f"current_profile: {sc.get('profile')}\n"
        f"anomaly_summary: {case['input_context']}\n"
        f"DTC: ninguno activo\n"
        f"historical_context: sin casos previos para este vehículo\n"
        f"retrieved_evidence: {CORPUS_SNIPPET}"
    )


def prompt_for(case: dict[str, Any]) -> str:
    return (
        "Eres el módulo de hipótesis de un sistema de diagnóstico vehicular. Analiza el "
        "contexto y propone hasta 3 hipótesis ORDENADAS por confianza. Si la evidencia "
        "no basta para una causa, usa resultado 'inconclusive' o 'insufficient_data' — "
        "es una respuesta correcta, no un fallo. No inventes causas sin soporte.\n\n"
        f"{build_context(case)}\n\n"
        f"Responde SOLO con JSON válido, en español, con este esquema:\n{SCHEMA_HINT}"
    )


def _terms(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-záéíóúñ_]{4,}", text.lower())}


def score_case(case: dict[str, Any], parsed: dict[str, Any]) -> dict[str, Any]:
    acceptable = [a for a in case.get("acceptable_hypotheses", []) if a != "none"]
    hyps = parsed.get("hipotesis") or []
    modes = [h.get("failure_mode", "") for h in hyps]
    top_conf = float(hyps[0].get("confianza", 0.0)) if hyps else 0.0
    expected = case["expected_outcome"]
    outcome = parsed.get("resultado", "")
    outcome_ok = outcome == expected or outcome in OUTCOME_ALTERNATIVES.get(case["case_id"], set())
    wants_no_cause = expected in ("inconclusive", "insufficient_data") and not acceptable
    cited = " ".join(str(e) for e in parsed.get("evidencias_citadas", []))
    mech = " ".join(h.get("mecanismo", "") for h in hyps)
    blob_terms = _terms(cited + " " + mech)
    expected_ev = case.get("expected_evidence", [])
    covered = sum(1 for e in expected_ev if _terms(str(e)) & blob_terms)
    return {
        "top1_ok": bool(acceptable) and bool(modes) and modes[0] in acceptable,
        "top3_ok": bool(acceptable) and any(m in acceptable for m in modes[:3]),
        "ranking": modes,
        "outcome": outcome,
        "outcome_ok": outcome_ok,
        "unsupported_certainty": bool(wants_no_cause and (top_conf > 0.6 or outcome == "probable")),
        "evidence_coverage": round(covered / len(expected_ev), 2) if expected_ev else None,
        "informacion_faltante": parsed.get("informacion_faltante"),
        "manual_review": {
            "forbidden_conclusions": case.get("forbidden_conclusions", []),
            "model_mechanisms": mech[:500],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--host", default="http://localhost:11434")
    args = parser.parse_args()

    cases = yaml.safe_load(CASES.read_text(encoding="utf-8"))["cases"]
    results: list[dict[str, Any]] = []
    for case in cases:
        t0 = time.perf_counter()
        body = httpx.post(
            f"{args.host}/api/generate",
            json={
                "model": args.model,
                "prompt": prompt_for(case),
                "stream": False,
                "format": "json",
            },
            timeout=600,
        ).json()
        latency = round(time.perf_counter() - t0, 2)
        row: dict[str, Any] = {"case_id": case["case_id"], "latency_s": latency}
        if body.get("eval_count") and body.get("eval_duration"):
            row["tokens_per_s"] = round(body["eval_count"] / (body["eval_duration"] / 1e9), 1)
        row["prompt_tokens"] = body.get("prompt_eval_count")
        try:
            parsed = json.loads(body.get("response", ""))
            row["structured_ok"] = True
            row.update(score_case(case, parsed))
        except (json.JSONDecodeError, TypeError):
            row["structured_ok"] = False
            row["raw_head"] = str(body.get("response", ""))[:150]
        results.append(row)
        print(json.dumps(row, ensure_ascii=False, default=str))

    n = len(results)
    summary = {
        "model": args.model,
        "benchmark": "agent-diagnostics v1 (INMUTABLE)",
        "context_builder_version": CONTEXT_BUILDER_VERSION,
        "measured_at": datetime.now(UTC).isoformat(),
        "structured_output_compliance": (
            f"{sum(r.get('structured_ok', False) for r in results)}/{n}"
        ),
        "top1": f"{sum(r.get('top1_ok', False) for r in results)}/{n}",
        "top3": f"{sum(r.get('top3_ok', False) for r in results)}/{n}",
        "outcome_ok": f"{sum(r.get('outcome_ok', False) for r in results)}/{n}",
        "unsupported_certainty_errors": sum(r.get("unsupported_certainty", False) for r in results),
        "results": results,
    }
    with OUT.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(summary, ensure_ascii=False, default=str) + "\n")
    print(f"\nResumen anexado a {OUT} — pásamelo para el informe llm_qwen25_3b_pilot_v1.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
