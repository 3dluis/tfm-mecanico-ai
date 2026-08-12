# 04 — Modelos de embeddings

## 1. Qué representan

Documentación técnica del RAG · CaseMemory (síntomas/casos) · LearnedPatterns ·
síntomas textuales · eventos (futuro) · perfiles de diagnóstico. Hoy el retriever es
léxico (LexicalRetriever, F4); el paso a denso está previsto en R3 con el MISMO contrato
de recuperación — esta estrategia se escribe ANTES para que la evaluación no se improvise.

## 2. Evaluación SEPARADA del LLM (ADR-0024)

Un embedding no se acepta porque "el RAG funciona con el LLM X" ni por benchmarks
generales (MTEB…): se evalúa en NUESTROS tres usos, cada uno con su ground truth:

| Uso | Consulta → objetivo | Ground truth disponible |
|---|---|---|
| **Technical RAG** | query → chunk técnico relevante | corpus v1 anotado por modo de fallo |
| **Case Memory** | caso actual → caso histórico similar | casos sintéticos con fallo conocido (mismo fallo = relevante) |
| **LearnedPatterns** | patrón nuevo → patrones conocidos relacionados | relaciones PatternRelation etiquetadas |

Un único modelo puede servir para los tres inicialmente, **pero debe validarse en los
tres por separado** antes de asumirlo.

## 3. Métricas

Con ground truth suficiente: `Recall@K · Precision@K · MRR · nDCG`. Siempre acompañadas
de evaluación cualitativa documentada de casos relevantes (¿recupera el chunk que un
mecánico usaría?). Métricas operativas: latencia por consulta, RAM del índice, tamaño
del índice, longitud máxima de secuencia efectiva.

## 4. Embedding Model Card (campos adicionales)

`base model · dimensiones · idioma(s) · normalization · chunk strategy (tamaño/solape/
unidad) · vector metric (cosine/dot/L2) · latency · RAM · index size · maximum sequence
length`. La estrategia de chunking se versiona junto al modelo: cambiar el chunking ES
cambiar el sistema de recuperación.

## 5. Candidatos iniciales (sin decisión)

Multilingües y viables en RPi: `paraphrase-multilingual-MiniLM-L12-v2` (384d),
`multilingual-e5-small` (384d), `bge-m3` (denso, más pesado — validar RAM). El corpus y
los síntomas están en español: el rendimiento en ES es criterio eliminatorio. Estados en
el inventario ([14 §3](14_model_selection.md)): PLANNED hasta que exista evaluación.
