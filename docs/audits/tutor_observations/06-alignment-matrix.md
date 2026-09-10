# 06 · Matriz de alineación

**Fecha:** 10 de septiembre de 2026 · **Pregunta vigente:** la de `ADR-003`, sin el adjetivo
«reales».

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis
> sin fundamento?

Estados: `DEFINIDO` · `IMPLEMENTADO` · `MEDIDO` · `VALIDADO` · `PENDIENTE` · `BAJO DIAGNÓSTICO`.

## Cadena completa

| Subpregunta | Objetivo | Fases | Métrica | Artefacto | Estado |
|---|---|---|---|---|---|
| **PI.1** ¿diagnostica a partir de la telemetría? | OE3 | E5–E9 | M1 | `E6_baseline.json`, `E7_modelo_temporal.json` | **MEDIDO**. No validado: dos cifras de F1 en conflicto entre informe y registro, sin resolver |
| **PI.2** ¿la explicación es trazable? | OE4, fases 4.1 a 4.3 | E11–E15 | M2, M4 | `E12_retrieval.json`, `E15_suficiencia.json` (corrida **oracular**) | **IMPLEMENTADO**. M2 medida; **M4 no**: el registro guarda las comprobaciones en crudo y las magnitudes agregadas no se han calculado |
| **PI.3** ¿reconoce la insuficiencia? | OE4 fase 4.4, OE5 | E15, E16, E17 | M5 | `E15_suficiencia.json`, `E15b_barrido_umbral.json` | **MEDIDO**. Es lo más sólido del trabajo y sobrevive a las tres versiones del verificador |
| **PI.4** ¿rechaza evidencia engañosa? | OE4 fases 4.3 y 4.4, OE5 | E15, E17 | M4, M5 | `E15_suficiencia_verifier_v2_1.json` | **BAJO DIAGNÓSTICO**. La condición que debía medirlo recupera los mismos fragmentos que la parcial |

## Objetivos

| Objetivo | Fases | Métricas | Estado |
|---|---|---|---|
| OE1 revisión del conocimiento previo | revisión documental | — | **IMPLEMENTADO**. Flujo PRISMA formal pendiente de acceso institucional |
| OE2 entorno experimental reproducible | E1, E2, E4, E5, E10 | — | **IMPLEMENTADO**. E3, datos reales, `PENDIENTE` como validación externa |
| OE3 modelo de diagnóstico | E5–E9 | M1 | **MEDIDO** sobre datos sintéticos |
| OE4 agente con verificación y abstención | E11, E12, E13, E15; E14 y E16 **pendientes** | M2, M3, M4, M5 | **IMPLEMENTADO**. M2, M3 y M5 medidas; M4 no. Ninguna `VALIDADO` |
| OE5 evaluación bajo cuatro condiciones | E17–E20 | M1–M6 | E17 **MEDIDO**; E18, E19, E20 `PENDIENTE` |

## Métricas: qué responde cada una

| Métrica | Qué mide | Fase | Objetivo | Subpregunta |
|---|---|---|---|---|
| M1 diagnóstico | exactitud, F1 macro, calibración | E5–E9 | OE3 | PI.1 |
| M2 recuperación | acierto en diez primeros, rango recíproco, ganancia descontada | 4.1 | OE4 | PI.2 |
| M3 explicación | adecuación al esquema, salidas válidas | 4.2 | OE4 | **ninguna**, y se declara descriptiva |
| M4 trazabilidad | corrección de citas, completitud, tasa de soporte | 4.3 | OE4 | PI.2, PI.4 · **implementada, sin magnitudes calculadas** |
| M5 abstención | abstención correcta, injustificada, explicación sin fundamento, con cobertura | 4.4 | OE4, OE5 | PI.3, PI.4 |
| M6 rendimiento | latencia, tamaño, coste | transversal | — | **ninguna**, y se declara descriptiva |

Dos métricas no responden a ninguna subpregunta y ambas lo declaran expresamente. Ninguna
subpregunta queda sin métrica. Ninguna fase queda sin objetivo.

## Condiciones experimentales

| Condición | Diseñada | Implementada | Manipulación comprobada | Estado |
|---|---|---|---|---|
| Evidencia completa | sí | sí | sí | **MEDIDO** |
| Evidencia parcial | sí | sí | sí | **MEDIDO** |
| Evidencia ausente | sí | sí | sí | **MEDIDO** |
| Con distractor | sí | sí | **no** | **BAJO DIAGNÓSTICO** |

La cuarta condición está diseñada, implementada y ejecutada, y su manipulación **no está
comprobada**: dos auditorías independientes verificaron que, con el filtro de motor activo,
recupera los mismos fragmentos que la condición parcial en los tres fallos examinados. El
hallazgo se conserva. No se le atribuye ninguna diferencia causal mientras siga así.

## Conclusiones que el estado actual permite

| Se puede afirmar | No se puede afirmar todavía |
|---|---|
| que retirar del índice la evidencia relevante cambia la decisión del agente, con datos, modelo, atribución y confianza constantes | que el sistema distinga presencia de pertinencia de forma general |
| que la abstención es una salida evaluable y no un fallo | ninguna cifra como validada, mientras la recuperación esté bajo reejecución |
| que las tres versiones del verificador y sus resultados intermedios se conservan | que el comportamiento se reproduzca sobre telemetría real |
| que el trabajo describe un vehículo de referencia | que se generalice a otros vehículos, generaciones o motores |
