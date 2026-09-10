# 01 · Matriz de trazabilidad de la pregunta

**Fecha:** 10 de septiembre de 2026 · **Estado:** `5a61194`.

> **Sujeta a `SD-01`.** Esta matriz se construye sobre la pregunta vigente en la memoria y en
> `ADR-003`. Su columna de componentes cambiaría si la decisión pendiente adoptara la otra
> versión. El resto de la cadena no.

Vínculos: `DIRECT` · `INDIRECT` · `MISSING` · `CONFLICT`.

## Cadena principal

| Subpregunta | Objetivo | Fases | Métricas | Evidencia | Vínculo | Estado |
|---|---|---|---|---|---|---|
| **PI.1** ¿diagnostica a partir de la telemetría? | OE3 | E5–E9 | M1 | `E6_baseline.json`, `E7_temporal.json` | `DIRECT` | medido; **una fase, E8, pendiente** |
| **PI.2** ¿es trazable la explicación? | OE4, fases 4.1 a 4.3 | E11–E15 | M2, M4 | `E12_retrieval.json`, `E15_suficiencia.json` | `DIRECT` | M2 medida; **M4 sin calcular** |
| **PI.3** ¿reconoce la insuficiencia? | OE4 fase 4.4, OE5 | E15, E16, E17 | M5 | `E15_suficiencia.json`, `E15b_barrido_umbral.json` | `DIRECT` | medido; **E16 pendiente** |
| **PI.4** ¿rechaza evidencia engañosa? | OE4 fases 4.3-4.4, OE5 | E15, E17 | M4, M5 | `E15_suficiencia_verifier_v2_1.json` | `CONFLICT` | **bajo diagnóstico** |

## Objetivos y fases

| Objetivo | Fases declaradas | Ejecutadas | Vínculo |
|---|---|---|---|
| OE1 | revisión documental | sí, sin flujo formal | `INDIRECT`: sin métrica, se verifica por artefacto |
| OE2 | E1, E2, E3, E4, E5, E10 | cuatro; E10 con corpus vacío; E3 pendiente | `DIRECT` |
| OE3 | E5–E9 | cuatro; **E8 pendiente** | `DIRECT` |
| OE4 | E11–E16 | cuatro; **E14 y E16 pendientes** | `DIRECT` |
| OE5 | E17–E20 | E17 sin informe; E18, E19, E20 pendientes | `DIRECT` |

## Huecos de trazabilidad

| Id | Hueco | Consecuencia |
|---|---|---|
| `TG-01` | M4 no tiene magnitud agregada en ningún artefacto | PI.2 se sostiene caso a caso y no como resultado |
| `TG-02` | La condición que debía medir PI.4 no manipula variable independiente | PI.4 sin evidencia propia |
| `TG-03` | E14 y E16 encabezan fases de OE4 y figuran pendientes | dos de las cuatro fases sin artefacto propio |
| `TG-04` | E17 tiene resultados en registro y no informe de fase | estado ambiguo entre tres fuentes |
| `TG-05` | El modelo temporal no alimenta el diagnóstico que el agente explica | la vía longitudinal existe y no llega a la explicación |

## Métricas sin subpregunta, declaradas

M3, explicación, y M6, rendimiento. Ambas se declaran descriptivas en el capítulo 4. **Ninguna
subpregunta queda sin métrica.**

## Lectura

La cadena se recorre entera para PI.1 y PI.3. Para PI.2 se recorre hasta la evidencia y se
detiene en el agregado. Para PI.4 se detiene antes: la condición que debía medirla no manipula
lo que dice manipular.

Ningún vínculo es inventado; los cinco huecos están nombrados.
