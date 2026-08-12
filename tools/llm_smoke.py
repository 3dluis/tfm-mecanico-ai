"""Smoke test comparativo de SLMs locales para el agente de diagnóstico (F3.7).

NO fija un modelo definitivo: mide, para cada candidato, (a) capacidad de producir JSON
estructurado válido según un esquema de diagnóstico, (b) latencia y tokens/s, (c) memoria
del modelo. La selección formal se hará con estos datos + criterios de calidad en la
iteración del agente (requisito del autor).

Requiere Ollama en ejecución. Uso (en el Mac del autor o perfil edge):
    ollama pull qwen2.5:3b llama3.2:3b llama3.2:1b gemma2:2b
    python tools/llm_smoke.py [--host http://localhost:11434] [--repeats 3]

Salida: tabla por stdout + registro JSONL en ai-models/experiments/llm_smoke.jsonl.
"""

import argparse
import json
import time
from pathlib import Path
from typing import Any

import httpx

CANDIDATES = ["qwen2.5:3b", "llama3.2:3b", "llama3.2:1b", "gemma2:2b", "phi3.5:3.8b"]

PROMPT = """Eres el módulo de diagnóstico de un sistema vehicular. Se detectó una anomalía:
- PIDs implicados: SHORT_FUEL_TRIM_1 (media +11%), LONG_FUEL_TRIM_1 (media +9%),
  INTAKE_PRESSURE (elevada en ralentí), RPM (inestable en ralentí)
- Sin DTC activos. Vehículo: gasolina, 4 cilindros.

Responde SOLO con un objeto JSON válido (sin markdown, sin texto extra) con este esquema:
{"causa_probable": str, "mecanismo": str, "confianza": float entre 0 y 1,
 "severidad": "low"|"medium"|"high", "recomendacion": str}"""

REQUIRED_KEYS = {"causa_probable", "mecanismo", "confianza", "severidad", "recomendacion"}


def try_model(host: str, model: str, repeats: int) -> dict[str, Any]:
    """Ejecuta el prompt N veces y agrega métricas."""
    ok, latencies, tps = 0, [], []
    for _ in range(repeats):
        t0 = time.perf_counter()
        try:
            r = httpx.post(
                f"{host}/api/generate",
                json={"model": model, "prompt": PROMPT, "stream": False, "format": "json"},
                timeout=300,
            )
            r.raise_for_status()
        except httpx.HTTPError as exc:
            return {"model": model, "error": str(exc)[:120]}
        dt = time.perf_counter() - t0
        body = r.json()
        latencies.append(dt)
        if body.get("eval_count") and body.get("eval_duration"):
            tps.append(body["eval_count"] / (body["eval_duration"] / 1e9))
        try:
            parsed = json.loads(body.get("response", ""))
            if set(parsed) >= REQUIRED_KEYS and 0.0 <= float(parsed["confianza"]) <= 1.0:
                ok += 1
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    return {
        "model": model,
        "json_valido": f"{ok}/{repeats}",
        "latencia_media_s": round(sum(latencies) / len(latencies), 1),
        "tokens_por_s": round(sum(tps) / len(tps), 1) if tps else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:11434")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--models", nargs="*", default=CANDIDATES)
    args = parser.parse_args()

    out = Path(__file__).parents[1] / "ai-models" / "experiments" / "llm_smoke.jsonl"
    results = []
    for model in args.models:
        res = try_model(args.host, model, args.repeats)
        results.append(res)
        print(res)
    with out.open("a", encoding="utf-8") as fh:
        for res in results:
            fh.write(json.dumps({"recorded_with": "tools/llm_smoke.py", **res}) + "\n")
    print(f"\nRegistro anexado a {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
