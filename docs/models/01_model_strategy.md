# 01 — Estrategia formal de modelos

## 1. Principios

1. **Baseline-first** (continuidad de F3/ADR-0011): ningún modelo complejo entra sin
   demostrar que supera a las líneas base simples y explicables bajo el mismo protocolo.
2. **Separación ML/LLM** (ADR-0009): el LLM nunca produce una anomalía matemática ni una
   detección de evento; razona SOBRE salidas de modelos deterministas/ML.
3. **Reproducibilidad > cantidad de modelos**: es preferible tener 4 modelos perfectamente
   trazables que 15 sin linaje ([13](13_reproducibility.md)).
4. **Edge-first**: la viabilidad en Raspberry Pi 5 es criterio de selección de primer
   orden, no una comprobación final ([14](14_model_selection.md)).
5. **Estados con condiciones**: un modelo cambia de estado solo si cumple condiciones
   verificables ([08](08_model_registry.md)); EDGE_APPROVED jamás por métricas offline solas.

## 2. Taxonomía

**ML Models** — detección de anomalías, clustering, clasificación cuando aplique,
detección de eventos, change-point detection, modelado temporal, comparación con
baselines y detección contextual de anomalías. Familias iniciales: baselines estadísticos
robustos, LOF, Isolation Forest, One-Class SVM, clustering, change-point detection, HMM
solo si aporta valor, autoencoders **solo si superan a los baselines**, otros modelos
temporales únicamente justificados. Detalle: [02](02_ml_models.md).

**Embedding Models** — representación de documentación RAG, CaseMemory, LearnedPatterns,
síntomas, eventos y perfiles de diagnóstico. Se evalúan por separado del LLM
([04](04_embedding_models.md)).

**LLM** — planificación, triage, generación de hipótesis, selección de herramientas,
interpretación de evidencia, crítica, explicación y generación del reporte
([03](03_llm_models.md)).

## 3. NO se entrena un foundation model desde cero

Decisión explícita (ADR-0023). La escalera de adaptación, de menor a mayor coste:

```
Pretrained model → Quantization → Prompt Engineering → Context Engineering
→ RAG → Tool use → Posible LoRA/QLoRA → Fine-tuning SOLO con evidencia de necesidad
```

Antes de cualquier fine-tuning debe **demostrarse experimentalmente** que prompting,
RAG, contexto, memoria y structured output no bastan (benchmark interno,
[03 §5](03_llm_models.md)). No se entrena un LLM para aumentar la complejidad técnica
del TFM: cada peldaño requiere evidencia del anterior.

## 4. Relación con la metodología (Design Science Research)

Los modelos y pipelines son artefactos evaluables del ciclo DSR:

```
Design → Build → Evaluate → Analyze → Refine
```

Cada decisión de selección deriva de evaluación experimental registrada (ModelExperiment
→ informe de comparación → decisión en el registro), nunca de impresión subjetiva. Las
preguntas experimentales que este marco debe poder responder están en
[07 §6](07_evaluation_protocol.md); ninguna cambia la pregunta principal del TFM.

## 5. Separación literatura ↔ experimentos propios

El Estado del Arte (docs/estado_del_arte/) recoge *lo que dice la literatura* (detección
no supervisada, anomalías automotrices, series event-aware, Edge ML, SLMs, cuantización,
sistemas agénticos, RAG, memoria, embeddings). Esta documentación recoge *lo que muestran
nuestros experimentos*. No se mezclan: las cards citan resultados propios con fuente
interna (informes de fase) y las afirmaciones bibliográficas viven en el EdA.

## 6. Documentación final del TFM

Esta sección alimenta el capítulo *"Diseño y evaluación de modelos de IA"* de la memoria
(estrategia → datasets → preparación → ML → embeddings → LLM → adaptación → optimización
edge → evaluación → selección final → limitaciones). Las cards y comparaciones están
escritas para poder trasladarse casi directamente.
