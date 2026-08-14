# 14 — Selección de modelos e inventario

## 1. Función multicriterio (nunca "el mayor F1")

```
Accuracy + Generalization (held-out) + FPR + Latency + RAM + Interpretability + Edge feasibility
```

> **Extensión F15 (ADR-0033, [Adenda XAI v1](../experiments/protocolo_ml_v1_adenda_xai.md)):**
> la dimensión Interpretability se desagrega y se hace EVALUABLE:
>
> ```
> Detection Performance + Explainability + Explanation Stability
> + Representation Quality + Edge Feasibility
> ```
>
> **Decision gate** (todo modelo candidato responde las 7 antes de promoverse):
> 1. ¿Detecta adecuadamente? · 2. ¿Mantiene el FPR permitido? · 3. ¿Las variables
> atribuidas son coherentes con el ground truth cuando existe (AR@K vs baseline
> aleatorio)? · 4. ¿Las explicaciones son estables (perturbación y seeds)? · 5. ¿Hay
> señales de leakage? · 6. ¿Hay señales de synthetic-domain bias? · 7. ¿Mantiene
> viabilidad edge?
>
> La evidencia negativa de explicación (atribuciones inestables o incoherentes con lo
> inyectado) es motivo legítimo de no-promoción aunque el F1 sea superior. Cada
> experimento separa además las decisiones D1 (detector) / D2 (representación) /
> D3 (mecanismo explicativo).

No hay fórmula cerrada con pesos: cada selección documenta sus trade-offs en el informe
de comparación y en la card. Ejemplo real (E1): OC-SVM tuvo MEJOR F1 (0.68 vs 0.64) y
6/6 episodios, pero se seleccionó **LOF k=10** por FPR 2.5× menor (0.035 vs 0.086) con
recall de conocidos equivalente — en un sistema que alerta al conductor, las falsas
alarmas destruyen la confianza. OC-SVM queda como segundo paquete (CANDIDATE), no se
descarta. Para LLM el equivalente es: calidad + RAM + latencia + tool use + structured
output + contexto + viabilidad edge — nunca el nº de parámetros.

Todo modelo descartado queda documentado con motivo (status REJECTED + card): los
resultados negativos de z-score e IForest son hallazgos citables, no fracasos a ocultar.

## 2. Estados del inventario

`PLANNED` (identificado, sin evaluar) → `EXPERIMENTING` (en evaluación) → `SELECTED` /
`REJECTED`. (El ciclo de vida fino del registro — EXPERIMENTAL…DEPLOYED — aplica a
modelos ya materializados; este inventario cubre también lo no construido.)

## 3. Inventario (12-ago-2026 — sin resultados inventados)

| Modelo/familia | Categoría | Estado | Evidencia |
|---|---|---|---|
| z-score robusto (max-\|z\|) | ML ventana | **REJECTED** | F1 0.44, FPR 0.10, held-out 0.0 (E1) |
| Isolation Forest | ML ventana | **REJECTED** | F1 test 0.0 (E1; normalidad multimodal) |
| **LOF k=10** | ML ventana | **SELECTED** | F1 0.64, FPR 0.035, 4/6 episodios held-out (E1) |
| OC-SVM (ν=0.01, γ=0.005) | ML ventana | SELECTED (2º paquete) | F1 0.68, 6/6 episodios, FPR 0.086 (E1) |
| Máquina de estados `ed:1` | ML eventos | **SELECTED** (baseline) | F1 0.77–1.00 por tipo (F6) |
| `event-baseline-z` contextual | ML contextual | **SELECTED (complementario)** v0.2.0 | EXP-ANOM-003: FPR 0.008 con train v1.1 (causa del FPR: insuficiencia de normalidad); conserva relacional urbana (R 0.41); scoring robusto RECHAZADO |
| `anom-combined-we` (OR window+event) | ML combinación | EXPERIMENTING → propuesta CANDIDATE | EXP-ANOM-003 (AM-WE-d): F1 0.70, FPR 0.071 ≈ ventana sola, held-out 2/4, recall 0.58>0.54 |
| Clustering (perfiles de conducción) | ML | PLANNED | — |
| Change-point detection (segmentación) | ML eventos | PLANNED | candidato a retar a `ed:1` |
| HMM (estados vehiculares) | ML eventos | PLANNED | solo si supera a `ed:1`/CPD |
| Autoencoder (denso 4.1k/10.2k params) | ML ventana | **EXPERIMENTING** (F14-F16) | EXP-ANOM-006/007: D1 REJECT ×2 — ni train v1.1 ni capacidad ni weight decay corrigen el FPR (0.129-0.168 vs 0.035 LOF); causa raíz identificada (features absolutas de fuel trim; diagnóstico + SHAP convergentes); candidato EXP-ANOM-008 = ablation fs2-lite |
| SHAP (Permutation) como capa XAI | XAI | **ADOPT** (D3, F16) | EXP-ANOM-007: AR@K ≫ azar en fallos detectados (vacuum 1.0 vs 0.38), agreement parcial con per-feature error (J5 0.42), estabilidad moderada (0.60/0.68), diagnóstico de FP demostrado; uso como evidencia/diagnóstico, NO decisión automática |
| Modelos temporales profundos (LSTM/GRU-AE) | ML | PLANNED (pospuestos, F16) | la patología identificada en EXP-ANOM-007 (offsets absolutos de trim) NO es de orden temporal → primero la ablation de features (EXP-ANOM-008); línea secuencial después, como experimento independiente |
| HDBSCAN sobre embeddings (descubrimiento) | ML patrones | PLANNED (F13) | EXP-PAT-001/002; los clusters son `candidate_pattern`, nunca «fallos» (Protocolo ML v1 §10) |
| Qwen 2.5/3 (1.5B–7B) | LLM | PLANNED | pendiente llm-smoke + benchmark |
| Llama 3.2 (1B–3B) | LLM | PLANNED | ídem |
| Gemma 2/3 (2B–4B) | LLM | PLANNED | ídem (licencia a revisar) |
| Phi 3.5/4-mini | LLM | PLANNED | ídem (validar ES) |
| paraphrase-multilingual-MiniLM | Embedding | PLANNED | pendiente evaluación 3 usos |
| multilingual-e5-small | Embedding | PLANNED | ídem |
| bge-m3 | Embedding | PLANNED | ídem (validar RAM en RPi) |

## 4. Alcance controlado (F7)

**MUST:** ML Model Cards · documentación LOF · Registry básico · ModelManifest ·
experiment tracking · reproducibilidad · benchmark LLM · mediciones edge · evaluación
básica de embeddings.
**SHOULD:** comparación de varios LLM · comparación de embeddings · benchmark de
cuantización · comparación event-aware · ModelRouter básico.
**COULD (no comprometen la entrega):** LoRA/QLoRA · fine-tuning LLM · autoencoder
avanzado · deep learning temporal · MLOps cloud completo · online learning.
