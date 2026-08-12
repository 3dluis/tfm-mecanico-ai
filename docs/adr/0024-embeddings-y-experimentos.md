# ADR-0024 — Evaluación separada de embeddings, configs declarativas y selección multicriterio

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 7

## Decisión

1. **Los embeddings se evalúan POR SEPARADO del LLM** y en NUESTROS tres usos (RAG
   técnico, CaseMemory, LearnedPatterns), cada uno con su ground truth propio;
   Recall@K/Precision@K/MRR/nDCG + evaluación cualitativa documentada. Nunca se
   selecciona un embedding solo por benchmarks generales (MTEB). Un único modelo puede
   servir para los tres usos, pero debe validarse en los tres.
2. **Configuración declarativa de experimentos** (YAML en `ai-models/configs/`): los
   parámetros críticos nunca viven solo en notebooks o hardcodeados. Regla
   `notebook ≠ pipeline`: ningún resultado de la memoria proviene únicamente de un
   notebook.
3. **Experiment tracking mínimo suficiente**: archivos estructurados versionados
   (runs.jsonl + registro JSON + configs YAML). MLflow solo si el volumen lo justifica
   (re-evaluable). La reproducibilidad prima sobre la plataforma.
4. **Selección multicriterio formal** (docs/models/14): accuracy + generalización
   held-out + FPR + latencia + RAM + interpretabilidad + viabilidad edge, con trade-offs
   documentados por escrito. Precedente aplicado: LOF sobre OC-SVM pese a menor F1.
5. **Versionado en 4 ejes independientes** (algoritmo / artefacto / features / dataset)
   sin mezclar identificadores.

## Alternativas descartadas

- Evaluar embeddings "de rebote" midiendo solo la calidad final del RAG con LLM:
  confunde la contribución del retriever con la del generador (no atribuible).
- Selección por leaderboard público: nuestros textos son español técnico automotriz;
  el dominio manda.
