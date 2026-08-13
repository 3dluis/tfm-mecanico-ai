# Comparación — Refinamiento del FPR de Event Intelligence (EXP-ANOM-003, F9)

> **CLASIFICACIÓN: PILOT / EXPLORATORY** (decisión del autor, F10). Evidencia
> exploratoria — no confirmatoria. Inventario de decisiones ex-ante/durante/post:
> [../experiments/exploratory/EXP-ANOM-003_clasificacion.md](../../experiments/exploratory/EXP-ANOM-003_clasificacion.md).
> Confirmatorio pre-registrado: [PROTO-CONF-001](../../experiments/preregistered/PROTO-CONF-001.md).


**Fuente:** `ai-models/experiments/e3_summary.json` + `e3_results.csv` +
`e3_per_scenario.csv` + `e3_per_profile.csv` (runner `e3_event_refinement.py`, config
`configs/exp-anom-003.yaml`). Los resultados de EXP-ANOM-002 NO se reetiquetan: los
brazos v1 se recomputaron con el mismo código y reproducen sus valores exactamente.

## 1. Pregunta y diseño

¿Las falsas alarmas del brazo de eventos (FPR 0.149–0.229 en EXP-ANOM-002) se deben a
insuficiencia de datos normales, baselines poco representativos, contabilidad de eventos
largos o contextos inadecuados? Diseño de atribución limpia (cada paso cambia UNA cosa):
datos (AM-E-d), scoring (AM-E-v2), y ventana con los mismos datos nuevos (AM-W-v2, por
equidad). **Dataset v1.1** = v1 + 16 sesiones normales SOLO de train (8 urbano/8
autovía/3 ralentí/3 frío; semillas 111–142; temperatura 4–33 °C; duraciones 1200–1800 s
— justificación en `suite_v1_train_ext.yaml`). Validation/test/held-out **congelados e
idénticos** a EXP-ANOM-001/002; umbrales solo con train (LOF cuantil; eventos LOSO).

## 2. Resultados (test; validación en e3_results.csv)

| Brazo | F1 | FPR | Episodios | Held-out | Retardo | evP | evR | evF1 | FE/sesión normal |
|---|---|---|---|---|---|---|---|---|---|
| AM-W-v1 (referencia) | 0.67 | **0.067** | 4/6 | 2/4 | 15 s | — | — | — | 2.0* |
| AM-W-v2 (train v1.1) | 0.70 | 0.142 | 4/6 | 2/4 | 7.5 s | — | — | — | 1.0* |
| AM-E-v1 (referencia) | 0.58 | 0.149 | 4/6 | 2/4 | 177 s | 0.90 | 0.53 | 0.66 | 5.5 |
| **AM-E-d (datos)** | 0.49 | **0.008** | 3/6 | 1/4 | 111 s | **0.98** | 0.36 | 0.52 | **2.0** |
| AM-E-v2 (robusto) | 0.43 | 0.112 | 2/6 | **0/4** | 79 s | 0.87 | 0.31 | 0.45 | 5.0 |
| AM-WE-v1 (original) | 0.69 | 0.189 | 4/6 | 2/4 | 4.2 s | — | — | — | 3.5* |
| **AM-WE-d (W-v1∨E-d)** | **0.70** | **0.071** | 4/6 | 2/4 | 15 s | — | — | — | 3.5* |
| AM-WE-v2 (W-v2∨E-d) | 0.71 | 0.144 | 4/6 | 2/4 | 7.5 s | — | — | — | 1.5* |
| AM-WE-rob | 0.70 | 0.146 | 4/6 | 2/4 | 7.5 s | — | — | — | 2.0* |

\* Para las vías con ventana, "FE/sesión" = rachas contiguas de ticks marcados en
sesiones normales (pseudo-eventos); para las vías de eventos es la métrica event-level
formal (`evaluation.anomaly_events`). Las métricas tick-level se conservan SIEMPRE.

## 3. Diagnóstico de la causa (pregunta central)

**Confirmado: insuficiencia de normalidad, no defecto conceptual.**

1. **Descomposición de varianza entre/intra sesión** (CONSTANT_SPEED, train v1.1): el
   ÚNICO caso con varianza entre-sesiones dominante es **LTFT en autovía (ratio 1.56)**;
   urbano 0.59 y el resto de señales (MAF, RPM, throttle, load) 0.10–0.30. Es la deriva
   fisiológica del LTFT — exactamente lo hipotetizado en EXP-ANOM-002 §5.2 — que 2
   sesiones/perfil no podían representar.
2. **El umbral LOSO se vuelve honesto con 22 sesiones**: sube de 5.44 a 57.5 porque
   ahora la cola de la distribución normal ENTRE sesiones está representada. Con él,
   AM-E-d alcanza **FPR test 0.008** (por fin dentro del objetivo del 1 %) y **event
   precision 0.98** (FE/sesión normal 5.5→2.0).
3. **Contextos**: 16→32 baselines (mediana 11 muestras/contexto) y la cobertura de
   scoring sube del 87.7 % al **97.6 %** (22/902 sin puntuar). La `context_signature`
   actual (tipo|velocidad|térmico|duración) es SUFICIENTE tras ampliar datos: la
   fragmentación no fue la causa. Trade-off documentado: añadir dimensiones (p. ej.
   banda de carga) duplicaría contextos y devolvería el problema de muestras — no se
   añade sin evidencia (`more context → better comparability → fewer samples per baseline`).

## 4. Trade-off held-out (criterio de éxito conjunto)

La reducción de FPR ATENÚA la ventaja relacional del brazo de eventos solo:
`t-corrbreak-u` pasa de R 0.73/17 s a **R 0.41/38 s (sigue detectada)**; se pierden
`t-corrbreak-h` (que en v1 era marginal: R 0.076, retardo 691 s) y `o2_lag` (v1: R 0.04).
**En la COMBINACIÓN el criterio conjunto se cumple**: AM-WE-d mantiene held-out 2/4 y
recall 0.58 (> 0.54 de la ventana sola) con **FPR 0.071 ≈ ventana sola (0.067)** —
frente al 0.189 de la combinación original. El retardo de la combinación vuelve a 15 s
(el 4.2 s de AM-WE-v1 provenía en parte del umbral laxo que causaba las falsas alarmas).

## 5. Resultados negativos documentados

- **Scoring robusto p50/percentiles (AM-E-v2): RECHAZADO.** σ_robusta=(p95−p05)/3.29
  infraestima la dispersión en features de cola pesada → los z explotan de forma
  desigual entre contextos, el umbral LOSO se dispara (287) y pierde TODO el held-out
  (0/4) con FPR peor que AM-E-d. El detector principal de eventos sigue con media/σ.
- **LOF reentrenado con train v1.1 (AM-W-v2): NO adoptado.** Hallazgo simétrico e
  interesante: la MISMA ampliación que arregla los eventos **perjudica** el umbral de la
  ventana (FPR 0.067→0.142): el train heterogéneo (fríos 4–33 °C) baja el cuantil del
  1 % de LOF. Más datos no son gratis para todos los detectores; la calibración es por
  detector.

## 6. Análisis urbano vs autovía

Desglose completo en `e3_per_profile.csv`. En AM-E-d el FPR de autovía cae de 0.41–0.52
a ~0 y el urbano se mantiene limpio; el coste es sensibilidad (recall de eventos 0.36).
La causa raíz identificada (LTFT entre-sesiones en autovía) sugiere la mejora futura
correcta: **feature de deriva relativa** (LTFT del evento menos LTFT de la propia sesión
en eventos previos) en lugar de más umbral — anotada como candidata para una iteración
posterior, NO ejecutada.

## 7. Limitaciones

Las mismas de EXP-ANOM-002 (sintético, 6 episodios test → lecturas direccionales, un
vehículo) más: la ampliación de train es del MISMO simulador (diversidad real limitada);
el criterio de 50 % de solape para positivos event-level es una elección documentada;
`global vs por-vehículo` sigue pendiente de un segundo perfil de vehículo.

## 8. Decisión

1. **Primario sin cambios: LOF k=10 sobre train v1** (AM-W-v2 no se adopta).
2. **event-baseline-z@0.2.0** (train v1.1, media/σ) sustituye a 0.1.0 (SUPERSEDED) como
   brazo de eventos: CANDIDATE.
3. **Configuración recomendada del sistema: AM-WE-d** = LOF-v1 (primario) ∨ eventos-0.2.0
   (complementario) — registrada como `anom-combined-we@0.2.0`. Se propone su promoción
   EXPERIMENTAL→CANDIDATE (FPR ya ≈ ventana sola): **pendiente de aprobación del autor**.
4. El scoring robusto queda rechazado con evidencia; re-evaluable solo con una
   formulación distinta (p. ej. MAD real almacenado en el contrato).
