# 11 — Optimización para edge

**Regla previa: no optimizar antes de disponer de una baseline funcional.** La
optimización sin baseline medida produce mejoras no atribuibles y consume cronograma.

## 1. Cuantización

- **LLM:** GGUF cuantizado es el punto de partida (no una optimización posterior).
  Escala prevista: Q4_K_M como referencia; Q5/Q8 solo si la calidad diagnóstica del
  benchmark cae de forma medible con Q4. El benchmark interno se ejecuta POR CUANTIZACIÓN
  (una card/entrada por variante: `modelo@version+Q4_K_M` ≠ `modelo@version+Q8`).
- **ML:** los modelos actuales (LOF/OC-SVM ONNX) son minúsculos (<1 MB, <0.01 ms/ventana
  en x86); no requieren cuantización. Si entrara un autoencoder: ONNX FP32→INT8 con
  validación de paridad de decisiones (no solo de scores).
- **Embeddings:** cuantización del índice (PQ/escalar) solo si el tamaño del índice en
  RPi lo exige; medir Recall@K antes/después.

## 2. Otras palancas (aplicar en este orden)

1. **Feature reduction:** eliminar features sin contribución medida (importancias de [02 §5](02_ml_models.md)).
2. **Model size / pruning:** cuando aplique (deep models); no aplica a los baselines actuales.
3. **Threading / runtime:** `onnxruntime` intra-op threads acotados (compartimos 4 CPU
   con el LLM); en llama.cpp, hilos = cores físicos − 1; medir, no asumir.
4. **Compatibilidad ARM64:** toda dependencia de inferencia debe tener wheel/binario
   arm64 (ya verificado para onnxruntime; verificar para el runtime LLM y embeddings).

## 3. Presupuesto de recursos del edge (RPi 5, 8 GB)

| Componente | Presupuesto RAM aprox. |
|---|---|
| LLM 3B Q4 | ~2.0–2.5 GB |
| Embeddings + índice | ~0.5 GB |
| ONNX ML + SQLite + runtime Python | ~0.5 GB |
| Sistema + margen | resto |

Este presupuesto es DISEÑO (L2: medido solo en emulación); las mediciones reales en
ARM64/RPi lo sustituirán y quedarán en la matriz de [10 §3](10_edge_deployment.md).
