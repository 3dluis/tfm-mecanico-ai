# Acciones A2/A3 — Validación ARM64 en el Mac (instrucciones concretas)

**Objetivo:** cerrar el hueco `x86 development → ARM64 container → Raspberry Pi target`
de la matriz de compatibilidad ([10 §3](10_edge_deployment.md)). Estados honestos:
`NOT_TESTED → PASSED/FAILED` según lo medido; **Raspberry Pi NO se marca validada hasta
ejecutar en hardware real**, y `EDGE_APPROVED` siempre lo decide una revisión humana.

## Requisitos previos (una vez)

1. Docker Desktop (o colima) corriendo en el Mac.
2. Repo actualizado: descomprimir `TFM/mecanico-ia-repo.zip` o `git pull` de tu copia.
3. Si iCloud mantiene evictados los docs: `git checkout -- docs/08_roadmap_tecnico.md`.

## A2 — Build multiarquitectura (≈10–20 min la primera vez)

```bash
cd ~/Documents/MasterAI/TFM/mecanico-ia
make arm64-build          # construye las imágenes linux/arm64 (QEMU/nativo Apple Silicon)
```

Resultado esperado: imágenes edge construidas sin error. Si falla, guarda la salida
completa — el fallo mismo es un dato (estado FAILED con motivo).

## A3 — Validación funcional + benchmark en contenedor ARM64

```bash
# 1) Tests del proyecto dentro del contenedor arm64 (valida dependencias/wheels ARM64)
docker run --rm --platform linux/arm64 -v "$PWD":/app -w /app \
  python:3.11-slim bash -c "
    pip install 'setuptools<81' wheel -q &&
    pip install -q ./shared ./obd-lab ./ai-models ./diagnostic-agent &&
    python -m pytest tests-integration -q"

# 2) Benchmark ONNX real en ARM64 (latencia, RAM, tamaño del artefacto)
docker run --rm --platform linux/arm64 -v "$PWD":/app -w /app \
  python:3.11-slim bash -c "
    pip install 'setuptools<81' wheel -q &&
    pip install -q ./shared ./obd-lab ./ai-models ./diagnostic-agent &&
    python tools/edge_validate.py --target arm64-container --out arm64-validation.json"
```

**Entregable:** `arm64-validation.json` (+ salida de los tests). Pásamelo en la sesión y
actualizo `HardwareValidation` de `anom-lof@0.2.0` en el registro con los valores REALES
(y, si todo pasa y lo apruebas, la transición VALIDATED→EDGE_APPROVED con su
justificación). El script sugiere PASSED/FAILED pero **nunca** marca approved solo.

## Después (cuando exista hardware)

En la Raspberry Pi 5 real: mismo `tools/edge_validate.py --target rpi5` + medición de
temperatura/ejecución sostenida (docs/models/10 §3). Hasta entonces la celda rpi5
permanece **NOT_TESTED** — sin excepciones.

## R2 en el mismo viaje (opcional, recomendado)

Con Ollama instalado en el Mac:

```bash
ollama pull qwen2.5:3b-instruct-q4_K_M
make llm-smoke            # valida carga, JSON estructurado, tokens/s, TTFT, RAM
```

El candidato único propuesto para el primer smoke es **Qwen2.5-3B-Instruct Q4_K_M**
(justificación en el informe F8 §propuesta LLM). Guarda la salida completa del smoke.
