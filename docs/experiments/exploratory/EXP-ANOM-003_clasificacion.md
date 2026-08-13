# EXP-ANOM-003 — Clasificación: PILOT / EXPLORATORY (decisión del autor, F10)

**No es un experimento confirmatorio.** Aunque su diseño fue especificado ex ante por el
autor (plan F9: objetivo diagnóstico, brazos con atribución limpia, criterio de éxito
CONJUNTO, prohibición de tocar held-out), el pre-registro formal con umbrales congelados
no existía aún y varias decisiones se tomaron durante el análisis. El hallazgo principal
— *el FPR del brazo de eventos estaba asociado a representación insuficiente de la
variabilidad normal (deriva intersesión del LTFT en autovía), no necesariamente a un
defecto conceptual* — queda como **hallazgo exploratorio hasta replicación confirmatoria**
(PROTO-CONF-001).

## Inventario de decisiones

**Existían ANTES de ejecutar** (plan F9 del autor): objetivo (diagnosticar la causa, no
"hacer ganar" a los eventos), la ampliación de normalidad solo-train con diversidad
controlada, métricas event-level además de tick-level (sin ocultar las tick-level), el
análisis urbano/autovía y de estabilidad de señales, la evaluación de baselines
robustos, el criterio de éxito conjunto (FPR + held-out + retardo + event precision) con
la regla de conservar la versión anterior si se pierde la ventaja relacional, y la
comparación final con el MISMO test/held-out.

**Tomadas DURANTE el análisis:** el tamaño exacto de la ampliación (16 sesiones y su
reparto 6/6/2/2), la formulación del scoring robusto (σ=(p95−p05)/3.29 sobre campos ya
persistidos), el umbral de solape 50 % de las métricas event-level, y la adición de los
combos AM-WE-d / AM-WE-v2 / AM-WE-rob **tras ver** que el brazo robusto fallaba (la
elección del brazo de eventos "ganador" para la combinación fue guiada por resultados).

**Consecuencia de resultados OBSERVADOS:** la recomendación AM-WE-d, la versión
event-baseline-z@0.2.0, el rechazo del scoring robusto, la no-adopción del LOF
reentrenado, y la mejora candidata "deriva LTFT relativa a la sesión" (no ejecutada).

## Estado en el registro

`EXP-ANOM-003.json` → `study_type: "exploratory"`. Informe:
[event_fpr_refinement_v1](../../models/comparisons/event_fpr_refinement_v1.md).
