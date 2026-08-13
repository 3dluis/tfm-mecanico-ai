"""Smoke profundo de UN candidato LLM local (R2, F9) — checklist completa del plan.

Complementa a tools/llm_smoke.py (comparativo ligero, F3). Este script valida UN modelo
en profundidad ANTES del benchmark: descarga/carga, arranque del runtime, generación
básica, español, JSON estructurado + cumplimiento de esquema, seguimiento de
instrucciones, estabilidad multi-run, tiempo de carga, TTFT, tokens/s, RAM, CPU, tamaño
del artefacto y contexto mínimo útil. NO evalúa calidad diagnóstica en profundidad (eso
es el benchmark de 6 casos, posterior e inmutable).

Candidato R2 aprobado: qwen2.5:3b-instruct-q4_K_M (tag verificado en ollama.com:
1.9 GB, contexto 32K, instruct, Q4_K_M). Requiere Ollama en ejecución:

    ollama pull qwen2.5:3b-instruct-q4_K_M
    python tools/llm_smoke_deep.py                       # o --model <tag> --host <url>

Salida: JSON por stdout + ai-models/experiments/llm_smoke_deep.jsonl (traza para la
Model Card — que SOLO se creará con estos resultados reales, nunca antes).
"""

import argparse
import json
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

DEFAULT_MODEL = "qwen2.5:3b-instruct-q4_K_M"
SCHEMA_KEYS = {"causa_probable", "mecanismo", "confianza", "severidad", "recomendacion"}

#: Contexto estructurado de prueba (context engineering: NUNCA telemetría cruda).
CONTEXT_BUILDER_VERSION = "cb:1"
STRUCTURED_CONTEXT = """vehicle_context: gasolina, 4 cilindros, 89000 km
current_event: IDLE (45 s, motor caliente)
anomaly_summary: detectada por LOF (ventana) score 8.0 (umbral 0.16), scope=window
relevant_features: SHORT_FUEL_TRIM_1 +11% · LONG_FUEL_TRIM_1 +9% · INTAKE_PRESSURE
  elevada en ralentí · RPM inestable en ralentí (std 48)
DTC: ninguno activo
historical_context: sin casos previos similares para este vehículo
retrieved_evidence: 'una fuga de vacío produce mezcla pobre: trims positivos sostenidos,
  MAP elevado y ralentí inestable; la deriva de MAF produce trims positivos SIN MAP
  elevado en ralentí' (corpus_v1)"""

PROMPT = f"""Eres el módulo de hipótesis de un sistema de diagnóstico vehicular. Contexto:

{STRUCTURED_CONTEXT}

Responde SOLO con un objeto JSON válido (sin markdown, sin texto adicional), en español,
con este esquema exacto:
{{"causa_probable": str, "mecanismo": str, "confianza": float 0..1,
 "severidad": "low"|"medium"|"high", "recomendacion": str}}"""


def _ollama(
    host: str, path: str, payload: dict[str, Any] | None = None, timeout: float = 600.0
) -> dict[str, Any]:
    if payload is None:
        r = httpx.get(f"{host}{path}", timeout=timeout)
    else:
        r = httpx.post(f"{host}{path}", json=payload, timeout=timeout)
    r.raise_for_status()
    return dict(r.json())


def measure_ttft(host: str, model: str) -> float:
    """Time-to-first-token vía streaming."""
    t0 = time.perf_counter()
    with httpx.stream(
        "POST",
        f"{host}/api/generate",
        json={"model": model, "prompt": "Di 'hola'.", "stream": True},
        timeout=600,
    ) as r:
        r.raise_for_status()
        for _line in r.iter_lines():
            return time.perf_counter() - t0
    return -1.0


def run_generation(host: str, model: str, prompt: str, ctx: int | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": model, "prompt": prompt, "stream": False, "format": "json"}
    if ctx:
        payload["options"] = {"num_ctx": ctx}
    t0 = time.perf_counter()
    body = _ollama(host, "/api/generate", payload)
    out: dict[str, Any] = {"latency_s": round(time.perf_counter() - t0, 2)}
    if body.get("eval_count") and body.get("eval_duration"):
        out["tokens_per_s"] = round(body["eval_count"] / (body["eval_duration"] / 1e9), 1)
    if body.get("prompt_eval_count"):
        out["prompt_tokens"] = body["prompt_eval_count"]
    text = body.get("response", "")
    out["schema_ok"] = False
    out["unsupported_certainty"] = None
    try:
        parsed = json.loads(text)
        out["schema_ok"] = (
            set(parsed) >= SCHEMA_KEYS
            and 0.0 <= float(parsed["confianza"]) <= 1.0
            and parsed["severidad"] in ("low", "medium", "high")
        )
        # Español: heurística mínima documentada (caracteres/término esperables).
        blob = f"{parsed.get('causa_probable', '')} {parsed.get('mecanismo', '')}".lower()
        out["spanish_ok"] = any(
            w in blob
            for w in ("fuga", "vacío", "mezcla", "admisión", "sensor", "presión", "combustible")
        )
        out["confianza"] = parsed.get("confianza")
    except (json.JSONDecodeError, TypeError, ValueError, KeyError):
        out["raw_head"] = text[:120]
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--host", default="http://localhost:11434")
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()

    report: dict[str, Any] = {
        "model": args.model,
        "context_builder_version": CONTEXT_BUILDER_VERSION,
        "measured_at": datetime.now(UTC).isoformat(),
        "host": args.host,
    }
    # 1) Artefacto y carga
    tags = _ollama(args.host, "/api/tags")
    info = next((m for m in tags.get("models", []) if m.get("name") == args.model), None)
    if info is None:
        print(
            json.dumps(
                {"error": f"modelo {args.model} no descargado; ejecuta 'ollama pull {args.model}'"},
                indent=2,
            )
        )
        return 1
    report["artifact_size_bytes"] = info.get("size")
    t0 = time.perf_counter()
    _ollama(args.host, "/api/generate", {"model": args.model, "prompt": "ok", "stream": False})
    report["load_plus_first_gen_s"] = round(time.perf_counter() - t0, 1)
    ps = _ollama(args.host, "/api/ps")
    running = next((m for m in ps.get("models", []) if m.get("name") == args.model), {})
    report["ram_bytes"] = running.get("size_vram") or running.get("size")

    # 2) TTFT
    report["ttft_s"] = round(measure_ttft(args.host, args.model), 2)

    # 3) Estabilidad: N repeticiones del prompt estructurado
    runs = [run_generation(args.host, args.model, PROMPT) for _ in range(args.repeats)]
    report["runs"] = runs
    report["schema_compliance"] = f"{sum(r['schema_ok'] for r in runs)}/{args.repeats}"
    report["spanish_compliance"] = f"{sum(bool(r.get('spanish_ok')) for r in runs)}/{args.repeats}"
    tps = [r["tokens_per_s"] for r in runs if "tokens_per_s" in r]
    report["tokens_per_s_median"] = round(statistics.median(tps), 1) if tps else None
    lat = [r["latency_s"] for r in runs]
    report["latency_s_median"] = round(statistics.median(lat), 2)

    # 4) Contexto mínimo útil: mismo prompt con num_ctx creciente
    report["context_probe"] = {
        str(ctx): run_generation(args.host, args.model, PROMPT, ctx=ctx)
        for ctx in (2048, 4096, 8192)
    }

    payload = json.dumps(report, indent=2, ensure_ascii=False, default=str)
    print(payload)
    # Artefactos formales R2 (esquemas en docs/experiments/preregistered/r2_artefactos.md)
    r2_dir = Path(__file__).parents[1] / "ai-models" / "experiments" / "r2"
    r2_dir.mkdir(parents=True, exist_ok=True)
    (r2_dir / "llm-smoke.json").write_text(payload + "\n", encoding="utf-8")
    import platform as _pf

    env = {
        "platform": _pf.platform(),
        "machine": _pf.machine(),
        "python": _pf.python_version(),
        "measured_at": report["measured_at"],
    }
    try:
        env["ollama_version"] = _ollama(args.host, "/api/version").get("version")
    except httpx.HTTPError:
        env["ollama_version"] = None
    (r2_dir / "environment.json").write_text(
        json.dumps(env, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    try:
        show = _ollama(args.host, "/api/show", {"model": args.model})
        runtime = {
            "model": args.model,
            "details": show.get("details", {}),
            "parameters_head": str(show.get("parameters", ""))[:500],
            "license_head": str(show.get("license", ""))[:200],
        }
    except httpx.HTTPError as exc:
        runtime = {"model": args.model, "error": str(exc)[:200]}
    (r2_dir / "model-runtime.json").write_text(
        json.dumps(runtime, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    out = Path(__file__).parents[1] / "ai-models" / "experiments" / "llm_smoke_deep.jsonl"
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(report, ensure_ascii=False, default=str) + "\n")
    print(f"\nArtefactos R2 en {r2_dir} (llm-smoke.json, environment.json, model-runtime.json)")
    print("Pásamelos junto con llm-benchmark.json para importarlos SIN recalcular.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
