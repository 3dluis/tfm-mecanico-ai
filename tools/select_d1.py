"""Selección del modelo de lenguaje local (D1) sobre el banco de selección.

Instrumental: **no contrasta ninguna hipótesis** y su resultado no se combina con evidencia
confirmatoria. Se ejecuta sobre `cases_d1.yaml` —disjunto del banco confirmatorio
`cases_v2`— porque elegir el modelo por su rendimiento en el banco de evaluación sería
selección sobre el conjunto de test.

**Context builder `cb:2`.** Cambia una sola cosa respecto de `cb:1`: declara el vocabulario
controlado que el corrector exige. `cb:1` pedía `failure_mode` como cadena libre y comparaba
por igualdad exacta contra identificadores, de modo que medía el formato de la etiqueta y no
el acierto (R2, `docs/experiments/exploratory/R2_smoke_qwen25_3b.md` §2.1). Los resultados de
`cb:1` y `cb:2` **no son comparables entre sí**.

**Brazos.**

* ``sin-evidencia``   contexto diagnóstico + vocabulario. Aísla al modelo.
* ``con-evidencia``   añade los 3 fragmentos que la recuperación léxica devuelve sobre C-A.
* ``control-constante``  responde siempre el mismo mecanismo, sin modelo. Es la referencia
  que un candidato debe superar: si no la supera, su resultado no es informativo.

Uso:
    python tools/select_d1.py --model qwen2.5:3b-instruct-q4_K_M
"""

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import httpx
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = REPO_ROOT / "benchmarks" / "agent-diagnostics" / "cases_d1.yaml"
CORPUS_CA = REPO_ROOT / "diagnostic-agent" / "knowledge" / "corpus_v2" / "build" / "corpus-CA.yaml"
OUT_DIR = REPO_ROOT / "ai-models" / "experiments" / "d1"

CONTEXT_BUILDER_VERSION = "cb:2"
VOCABULARIO = ["vacuum_leak", "maf_drift", "thermostat_stuck", "o2_lag", "misfire", "none"]

SCHEMA_HINT = """{"hipotesis": [{"failure_mode": <uno EXACTO del vocabulario>,
  "confianza": float 0..1, "mecanismo": str}],
 "resultado": "probable"|"inconclusive"|"insufficient_data"|"no_fault",
 "evidencias_citadas": [str]}"""


def _load_ca_chunks() -> list[tuple[str, str]]:
    payload = yaml.safe_load(CORPUS_CA.read_text(encoding="utf-8"))
    return [
        (f"{doc['document_id']}#{chunk['seq']}", chunk["text"])
        for doc in payload["documents"]
        for chunk in doc["chunks"]
    ]


def _retrieve(chunks: list[tuple[str, str]], query: str, k: int = 3) -> list[tuple[str, str]]:
    sys.path.insert(0, str(REPO_ROOT / "diagnostic-agent" / "src"))
    from diagnostic_agent.reasoning.rag.retriever import _tokens

    q = Counter(_tokens(query))
    scored: list[tuple[float, str, str]] = []
    for chunk_id, text in chunks:
        c = Counter(_tokens(text))
        overlap = sum(min(q[t], c[t]) for t in q)
        denom = (sum(q.values()) * max(1, len(c))) ** 0.5
        if denom and overlap:
            scored.append((overlap / denom, chunk_id, text))
    scored.sort(key=lambda x: -x[0])
    return [(cid, text) for _, cid, text in scored[:k]]


def build_prompt(case: dict[str, Any], evidence: list[tuple[str, str]] | None) -> str:
    """Context builder cb:2: contexto medido + vocabulario controlado (+ evidencia opcional)."""
    bloques = [
        "Eres un asistente de diagnóstico de automoción. Responde SOLO con JSON válido.",
        "",
        "vehicle_context: gasolina, 4 cilindros",
        f"current_profile: {case['scenario']['profile']}",
        f"window_features: {case['input_context']}",
        "DTC: ninguno activo",
    ]
    if evidence is not None:
        textos = " | ".join(f"[{cid}] {text[:400]}" for cid, text in evidence)
        bloques.append(f"retrieved_evidence: {textos}")
    bloques += [
        "",
        f"Esquema de respuesta: {SCHEMA_HINT}",
        "",
        "IMPORTANTE: el campo failure_mode debe ser EXACTAMENTE uno de estos identificadores, "
        f"en minúsculas y sin traducir: {', '.join(VOCABULARIO)}. "
        "Usa 'none' si la ventana no muestra evidencia de avería.",
    ]
    return "\n".join(bloques)


def score(case: dict[str, Any], modes: list[str]) -> dict[str, Any]:
    """Acierto top-1 y top-3 contra el mecanismo de referencia; 'none' para los normales."""
    esperado = case["ground_truth"]["failure_mode"] or "none"
    return {
        "esperado": esperado,
        "respondido": modes[0] if modes else None,
        "top1": bool(modes) and modes[0] == esperado,
        "top3": esperado in modes[:3],
    }


def run_arm(
    name: str, cases: list[dict[str, Any]], model: str, host: str, *, with_evidence: bool
) -> dict[str, Any]:
    chunks = _load_ca_chunks() if with_evidence else []
    rows: list[dict[str, Any]] = []
    for case in cases:
        evidence = _retrieve(chunks, case["input_context"]) if with_evidence else None
        t0 = time.perf_counter()
        body = httpx.post(
            f"{host}/api/generate",
            json={
                "model": model,
                "prompt": build_prompt(case, evidence),
                "stream": False,
                "format": "json",
            },
            timeout=600,
        ).json()
        row: dict[str, Any] = {
            "case_id": case["case_id"],
            "latency_s": round(time.perf_counter() - t0, 2),
        }
        try:
            parsed = json.loads(body.get("response", ""))
            modes = [h.get("failure_mode", "") for h in (parsed.get("hipotesis") or [])]
            row["structured_ok"] = True
            row["ranking"] = modes
            row.update(score(case, modes))
        except (json.JSONDecodeError, TypeError, AttributeError):
            row["structured_ok"] = False
            row["top1"] = row["top3"] = False
        rows.append(row)
    n = len(rows)
    return {
        "arm": name,
        "top1": sum(r["top1"] for r in rows) / n,
        "top3": sum(r["top3"] for r in rows) / n,
        "structured_ok": sum(r.get("structured_ok", False) for r in rows) / n,
        "latency_s_median": sorted(r["latency_s"] for r in rows)[n // 2],
        "rows": rows,
    }


def run_constant(cases: list[dict[str, Any]], constant: str) -> dict[str, Any]:
    """Control trivial: sin modelo, responde siempre lo mismo."""
    rows = [{"case_id": c["case_id"], **score(c, [constant])} for c in cases]
    n = len(rows)
    return {
        "arm": f"control-constante:{constant}",
        "top1": sum(r["top1"] for r in rows) / n,
        "top3": sum(r["top3"] for r in rows) / n,
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--host", default="http://localhost:11434")
    args = parser.parse_args()

    cases = yaml.safe_load(CASES_PATH.read_text(encoding="utf-8"))["cases"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    arms = [
        run_arm("sin-evidencia", cases, args.model, args.host, with_evidence=False),
        run_arm("con-evidencia", cases, args.model, args.host, with_evidence=True),
    ]
    arms += [run_constant(cases, m) for m in VOCABULARIO if m != "none"]
    arms.append(run_constant(cases, "none"))

    mejor_control = max(a["top1"] for a in arms if a["arm"].startswith("control-constante"))
    mejor_modelo = max(a["top1"] for a in arms if not a["arm"].startswith("control-constante"))
    report = {
        "model": args.model,
        "bank": "cases_d1 (selección, disjunto de cases_v2)",
        "context_builder_version": CONTEXT_BUILDER_VERSION,
        "n_cases": len(cases),
        "arms": [{k: v for k, v in a.items() if k != "rows"} for a in arms],
        "mejor_modelo_top1": mejor_modelo,
        "mejor_control_top1": mejor_control,
        "supera_al_control": mejor_modelo > mejor_control,
        "detail": arms,
    }
    (OUT_DIR / "d1-selection.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"banco: {report['bank']} · n={len(cases)} · {CONTEXT_BUILDER_VERSION}\n")
    for arm in arms:
        print(f"  {arm['arm']:32s} top1={arm['top1']:.2f}  top3={arm['top3']:.2f}")
    print(
        f"\nmejor modelo {mejor_modelo:.2f} vs mejor control {mejor_control:.2f} → "
        f"{'SUPERA al control' if mejor_modelo > mejor_control else 'NO supera al control'}"
    )
    print(f"informe: {(OUT_DIR / 'd1-selection.json').relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
