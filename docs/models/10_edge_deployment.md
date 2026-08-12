# 10 — Despliegue en edge

## 1. Pipeline (manual durante el TFM)

```
ai-models → modelo VALIDATED → export (ONNX/GGUF) → manifest → checksum
→ validación ARM64 → EDGE_APPROVED → diagnostic-agent (instalación manual)
```

La actualización automática Cloud→Edge NO se implementa todavía; el diseño del registro
y el manifest la dejan preparada (ADR-0022, docs/data-architecture/09 para el transporte).

## 2. Formatos por categoría

| Categoría | Formato | Runtime | Nota |
|---|---|---|---|
| ML | **ONNX** (skl2onnx; paridad exacta verificada) | onnxruntime | joblib/pickle solo justificado y nunca como formato de distribución |
| LLM | **GGUF** (cuantizado) | Ollama / llama.cpp | formato final depende del runtime elegido en R2 |
| Embeddings | según runtime (ONNX u nativo sentence-transformers) | a decidir en R3 | mismo criterio: formato+runtime+versión+limitaciones SIEMPRE documentados |

## 3. Matriz de compatibilidad hardware

Objetivos: `mac-dev · arm64-container · rpi5`. Estados por celda:
`COMPATIBLE | NOT_TESTED | FAILED | APPROVED` (contrato `HardwareValidation`, embebido en
la entrada del registro). Estado actual real:

| Modelo | mac-dev | arm64-container | rpi5 |
|---|---|---|---|
| anom-lof@0.2.0 (ONNX) | not_tested | not_tested (pendiente A2/A3) | not_tested (sin hardware, L2) |
| anom-lof@0.2.0 en sandbox-x86 | — | — | APPROVED como proxy x86 con límites 4CPU/8GB (0.007 ms/ventana) |
| event-detector ed:1 | compatible (python puro) | compatible | compatible (sin runtime de inferencia) |

En RPi física, cuando exista, se medirá: RAM, CPU, latencia, temperatura, almacenamiento
y ejecución sostenida. **Ningún modelo se marca EDGE_APPROVED sin celda ARM64 aprobada.**

## 4. Rollback (diseñado; manual)

Cada dispositivo conoce `active_model` y `previous_model` (contrato `ModelDeployment`:
`active_model_id/version + previous_model_id/version + rollback_of`). Si la versión
nueva falla en el edge, se vuelve a la anterior y el rollback queda registrado como un
despliegue más (auditable). El loader del edge ya rechaza artefactos con checksum
inválido (F4), lo que hace el rollback seguro.
