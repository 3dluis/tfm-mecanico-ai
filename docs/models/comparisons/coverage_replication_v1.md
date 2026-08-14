# Comparación — réplica de cobertura (EXP-ANOM-010, F21)

**Pregunta:** ¿el AE denso fs1 mejora si el train incorpora la normalidad ampliada de F20,
definida a priori desde el mecanismo del generador?

**Respuesta corta:** no. La expansión no cambia nada porque no contiene la región de
normalidad que provoca los falsos positivos. Decisión **D1 = REJECT**.

## Brazos (test histórico intacto, mediana de semillas 42/43/44)

| Brazo | Cambio respecto al anterior | F1 | FPR | FPR autovía | Episodios detectados |
|---|---|---|---|---|---|
| `lof_frozen` | ninguno (arms-freeze-v1) | 0.6448 | 0.0345 | 0.0847 | 4/6 |
| `ae_v11` | AE denso fs1 con train v1.1 | 0.6986 | 0.1379 | 0.4915 | 6/6 |
| `ae_v2` | **solo los datos**: +12 sesiones de F20 | 0.7095 | 0.1336 | 0.4915 | 4/6 |
| `lof_v2` | LOF reentrenado con el banco v2 | 0.6797 | 0.1293 | 0.4915 | — |

Referencia no promovible (F18, normalidad elegida tras diagnosticar test):
**F1 0.7273 · FPR 0.0216 · FPR autovía 0.0847**.

## Por qué no cambia nada

| Conjunto | ventanas con nivel LTFT **+** | distancia mediana a los FP (unid. estandarizadas) |
|---|---|---|
| train v1.1 | 0.0000 | 15.79 |
| expansión v2 (F20) | **0.0000** | 15.74 |
| normales del control F18 | 0.0441 | **3.88** |
| falsos positivos del test | 0.8276 | — |

El 82.8 % de los falsos positivos son ventanas con LTFT sostenido en +0.78125 %; ningún
conjunto de entrenamiento contiene una sola ventana así. La cuantización J1979 del proyecto
trunca hacia cero (`int(v·128/100)`), de modo que el nivel solo cambia al superar un cuanto
**completo**: el criterio de F20 (medio cuanto + contador binario de sesión) declaraba
cerrado un hueco que en el espacio de features seguía abierto.

## Decisiones

- **D1 (detector): REJECT** — 4ª vez que un AE no se adopta. Falla el criterio de FPR
  declarado a priori (0.1336 > 0.03).
- **D2 (embeddings): NEEDS MORE EVIDENCE** — silhouette 0.113 vs referencia 0.202.
- **D3 (XAI): no evaluado** — condicionado a D1 = PROMOTE en la pre-especificación.
- **LOF congelado sigue siendo el detector por defecto** (arms-freeze-v1 reproducido exacto).

## Lectura para la memoria

El valor de este experimento no es la métrica sino el método: la pre-especificación se
commiteó antes de ejecutar (`ac7b353`), incluía una predicción **negativa** (P3) y un
control de integridad (P4), y el criterio numérico no se renegoció al ver los resultados.
El resultado negativo identifica un modo de fallo nuevo y reutilizable — *cobertura
declarada ≠ cobertura efectiva* — y deja una acción concreta y barata para la fase
siguiente (banco v3 con criterio medido en el espacio de features).

Informe completo: [F21](../../fase21/informe_exp_anom_010.md).
