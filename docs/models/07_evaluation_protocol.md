# 07 — Protocolo de evaluación

## 1. Principio

Toda evaluación se hace bajo un protocolo **pre-registrado** y con linaje completo.
Comparar dos modelos exige mismo dataset, mismo split, mismas features y mismo protocolo
(eso ES un `ModelExperiment`); si algo difiere, la comparación no es válida y no se
publica como tal.

## 2. Por categoría

- **ML anomalías (ventana):** protocolo ADR-0011 — umbral por cuantil de train-normal
  (1% FPR objetivo), sin point-adjustment, métricas point-wise Y por episodio (recall de
  episodios, retardo de detección), held-out solo en test. Mínimos:
  `precision, recall, F1, FPR, episode recall, held-out episode recall, latency`
  (+AUROC/AUPRC cuando aplique, nunca en exclusiva).
- **ML eventos:** P/R/F1 por tipo con emparejamiento por IoU temporal ≥ 0.5, error de
  onset/fin, IoU medio, tolerancia para eventos puntuales; calibración de confianza
  cuando el detector la emita (event-intelligence/11; implementado en
  `ai_models.evaluation.event_metrics`).
- **Anomalía contextual:** FP en held-out normal comparable + recall sobre eventos con
  fallo activo + atribución de features (¿señala los PIDs correctos?); comparación
  ventana-vs-evento con `anomaly_mode` (experimento PI.5/H6).
- **LLM:** benchmark interno de 5 dimensiones (calidad diagnóstica, grounding,
  comportamiento agéntico, seguridad, rendimiento edge — [03 §5](03_llm_models.md)).
- **Embeddings:** Recall@K/Precision@K/MRR/nDCG por uso (RAG/casos/patrones) +
  cualitativa ([04 §3](04_embedding_models.md)).

## 3. Artefactos de cada evaluación relevante

```
metrics.json · predictions.json · run-config.yaml · environment.json
```

y un resumen Markdown cuando proceda. La evaluación se persiste como `ModelEvaluation`
(con `hardware` explícito) y los experimentos comparativos producen informe en
[comparisons/](comparisons/) con: objetivo, protocolo, modelos, datasets, métricas,
resultados, interpretación, limitaciones y decisión.

## 4. Evaluación edge (condición para EDGE_APPROVED)

Además de métricas de calidad: latencia por inferencia, RAM pico, CPU, tamaño en disco,
estabilidad en ejecución sostenida, compatibilidad ARM64 y formato/runtime verificados
([10](10_edge_deployment.md)). Para LLM: tokens/s, time-to-first-token, contexto probado.

## 5. Ablaciones previstas

El sistema queda preparado para medir la contribución real de cada componente:

```
LOF sin contexto de evento  vs  LOF con contexto de evento
LLM  vs  LLM+RAG  vs  LLM+RAG+Memoria         (dimensiones A0–A6 / memory_mode)
Single pass  vs  agent loop                    (A3 vs A6)
rule baseline  vs  detector ML de eventos
```

## 6. Preguntas experimentales que este marco responde

- **ML:** ¿qué modelo no supervisado equilibra mejor detección de anomalías desconocidas
  y falsas alarmas? *(E1 respondida provisionalmente: LOF k=10; ampliable)*
- **Event-aware (H-EVT / PI.2):** ¿mejora la segmentación por eventos la detección
  frente a ventanas arbitrarias? *(evidencia EXPLORATORIA en EXP-ANOM-002/003: como
  sustituto NO; como señal complementaria SÍ; confirmatorio pre-registrado:
  [PROTO-CONF-001](../experiments/preregistered/PROTO-CONF-001.md))*
- **LLM (instrumento de H-EXP):** ¿qué modelo local equilibra mejor calidad diagnóstica
  y recursos edge (criterio transversal)?
- **Memoria (H-MEM / PI.4):** ¿cómo cambia el rendimiento del agente con memoria
  episódica/evolutiva validada?
- **Agéntico (H-MAS, secundaria / PI.5):** ¿qué aporta el proceso iterativo frente a una
  ejecución única? *(A6 vs A3; su refutación no afecta a C-INT)*
- **Central (H-MAIN):** held-out/open-set TRIPLE (datos + corpus + memoria) — el
  held-out de corpus/memoria aún debe formalizarse antes de su confirmatorio (hueco
  identificado en la revisión de coherencia F10)

Nomenclatura: familias H-* de la alineación científica v2
([correspondencia](../correspondencia_nomenclatura.md)).

Ninguna de estas preguntas cambia automáticamente la pregunta principal del TFM.
