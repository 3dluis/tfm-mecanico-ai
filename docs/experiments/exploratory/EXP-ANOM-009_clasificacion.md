# EXP-ANOM-009 — Clasificación: EXPLORATORY (F18)

**Decisión del autor (aprobación de F18):** exploratorio bajo el Protocolo ML v1 +
Adenda XAI v1 + adenda temporal. Sin seeds confirmatorias (se usan exploratorias
437–509 para el brazo control, dentro del bloque 426–599); arms-freeze-v1 intacto; LOF y
AE estático participan sin reoptimizar. **Validez declarada: entorno emulado/sintético**
— HCRL y ARM64/RPi5 siguen como dependencias externas registradas aparte.

## Inventario de decisiones

**Existían ANTES de ejecutar (congeladas y committeadas en un commit previo al run):**

- **HX-ML-3** enunciada de forma falsable, con su criterio de refutación explícito, en
  `configs/exp-anom-009.yaml`. No se reformula después de ver resultados.
- Entrada principal aprobada: **secuencias crudas `[60 × 12 PIDs]`**; fs1-sequence como
  ablation SECUNDARIA. Longitudes a evaluar 30/60/120 pasos, con duración real en
  segundos siempre registrada.
- Espacio de modelos acotado: LSTM-AE y GRU-AE, <150k parámetros, sin
  Transformer/TCN/VAE/attention; búsqueda de hiperparámetros mínima.
- Normalización declarada (train-only, global por feature — NO por secuencia) y contrato
  de ausencias (máscara, relleno declarado, idéntico en train e inferencia).
- **Adenda XAI temporal**: matriz `A[t,f]` canónica, agregados derivados, GT temporal y
  métricas FAR@K / TAR@K / FTH@K con azar hipergeométrico — todo definido antes de medir.
- Brazo control diagnóstico aprobado por el autor, declarado explícitamente como **no
  candidato a adopción**.
- **Regla de parada** escrita antes de ejecutar: si no hay mejora defendible, informe de
  causa en lugar de más profundidad o de saltar a TCN/Transformer.

**Tomadas DURANTE la ejecución (ninguna afecta al ajuste):**

- Elección del explainer: la config exigía NO fijarlo a priori. Se comprobó
  compatibilidad real (DeepExplainer incompatible con LSTM/GRU; Permutation viable pero
  ~21–27 s/secuencia) y se eligió GradientExplainer, **validándolo contra Permutation**
  en una submuestra en lugar de justificarlo por coste. El desacuerdo resultante
  (0.14–0.26) se reporta como evidencia negativa, no se oculta.
- Selección de las 10 sesiones del brazo control por barrido según el criterio declarado
  («el LTFT cruza ≥1 frontera de cuantización»), nunca por su efecto en las métricas.
- Umbrales intactos tras ver test; ningún re-entreno posterior a los resultados; ningún
  dato regenerado para mejorar cifras.

**Consecuencia de resultados OBSERVADOS:**

- **HX-ML-3 REFUTADA**; D1 = REJECT · D2 = NEEDS MORE EVIDENCE (EXP-PAT-001 NO se abre) ·
  D3 (nivel celda) = NEEDS MORE EVIDENCE · LSTM vs GRU = NO WINNER.
- El **brazo control confirma** la causa refinada de EXP-ANOM-008: el techo de la serie
  era cobertura de normalidad, no arquitectura ni representación.
- **Caveat epistémico registrado**: la cobertura del control se derivó de un diagnóstico
  hecho sobre test, por lo que NO se convierte en decisión de detector sin réplica
  independiente. Esta limitación se declara en el informe y en el registro.
- Regla de parada activada → informe de causa (dataset insuficiente = dominante;
  emulador/GT = causa secundaria abierta por el recall 0.000 universal en anomalías
  lentas).

## Estado en el registro

- `ai-models/registry/experiments/EXP-ANOM-009.json` (`study_type: exploratory`)
- Artefactos: `e8_results.json` (brazos, barrido, seeds, control, ablation, embeddings,
  análisis de cuantización, XAI), `runs.jsonl`, figuras en `docs/fase18/figs/`.
- Informe: [`temporal_autoencoders_v1`](../../models/comparisons/temporal_autoencoders_v1.md).
