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
