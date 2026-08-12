# 11 — Diseño experimental de eventos

[← Índice](README.md) · ADR: [0021](../adr/0021-deteccion-anomalias-contextual.md)

## Métricas de detección de eventos (contra ground truth de obd-lab)

Por tipo de evento: precision, recall, F1, FP/FN (emparejamiento por solape). **Precisión
temporal**: onset error (s), end error, duration error y **IoU temporal** (intersección/unión
de intervalos; umbral de match v1: IoU ≥ 0,5). Para inferidos (gear shift): detection
accuracy + calibración de confidence (reliability diagram / ECE).

## Experimento central: ventana vs evento (requisito 31)

> ¿Mejora la detección de anomalías al comparar comportamientos dentro de eventos
> equivalentes frente a ventanas temporales arbitrarias?

Mismos escenarios y splits de la suite (ampliada con fallos activos SOLO durante tipos de
evento concretos, p. ej. deriva MAF que solo se manifiesta en aceleraciones): brazo A =
pipeline F3 (ventana+LOF); brazo B = evento+baseline contextual; brazo A+B combinado.
Métricas: F1/FPR por ventana y por episodio, retardo, y cobertura de los held-out
relacionales. Se integra como dimensión adicional del diseño A0–A6 (una columna más de la
RuntimeConfig: `anomaly_mode ∈ {window, event, both}`).

> **Resultado v1 (EXP-ANOM-002, F8):** ejecutado sobre la suite v1 SIN ampliar (fallos
> estándar) y sin LLM. Como sustituto, el brazo de eventos NO supera a LOF-ventana
> (F1 test 0.58 vs 0.67; FPR 0.15 vs 0.07 — concentrado en normales de autovía con solo
> 2 sesiones de train por perfil); como señal COMPLEMENTARIA sí aporta: localiza el
> held-out relacional urbano (R 0.73 vs 0.25, retardo 17 s) y la unión sube recall
> 0.54→0.63 con retardo 15→4.2 s a costa de FPR. La ablación con/sin context_signature
> confirma la aportación del contexto. Informe completo:
> [docs/models/comparisons/anomaly_window_vs_event_v1.md](../models/comparisons/anomaly_window_vs_event_v1.md).

> **Resultado v2 (EXP-ANOM-003, F9):** el FPR del brazo de eventos era INSUFICIENCIA DE
> NORMALIDAD, no defecto conceptual: con 22 sesiones de train (dataset v1.1; val/test
> congelados) el umbral LOSO se vuelve honesto y el FPR cae a 0.008 (event precision
> 0.98), conservando la detección relacional urbana atenuada (R 0.41). La causa raíz es
> la deriva entre-sesiones del LTFT en autovía (ratio varianza entre/intra = 1.56). La
> combinación recomendada AM-WE-d logra FPR 0.071 ≈ ventana sola con recall superior.
> Scoring robusto p50/percentiles rechazado. Informe:
> [event_fpr_refinement_v1.md](../models/comparisons/event_fpr_refinement_v1.md).

## Subpregunta académica (análisis del requisito 42)

Cabe como **subpregunta PI.5 / hipótesis H6** sin cambiar la pregunta principal — la
REFUERZA: los eventos son exactamente el mecanismo por el que el sistema puede explicar
patrones ("en qué contexto ocurre") y comparar contra la normalidad propia del vehículo:

> **PI.5/H6:** La segmentación contextual de la telemetría mediante eventos vehiculares
> mejora la detección de anomalías y la identificación de patrones de fallo frente al
> análisis basado únicamente en ventanas temporales (medida: F1/FPR/retardo sobre los mismos
> escenarios, brazos window vs event vs both).

Alcance TFM: SÍ cabe si se limita al MUST del roadmap (eventos OBD-only + baseline por
contexto + experimento window-vs-event); IMU/giros/secuencias quedan SHOULD/COULD.

## Posible contribución (hipótesis a validar con Estado del Arte — requisito 43)

La combinación telemetría event-aware + baselines por vehículo/contexto + detección no
supervisada + memoria episódica/evolutiva + razonamiento multiagente NO se afirma novedosa:
queda registrada como hipótesis de contribución C6 pendiente de barrido bibliográfico
específico (event segmentation en driving analytics, per-vehicle baselines en PdM,
contextual anomaly detection) antes de reclamarla en la memoria.
