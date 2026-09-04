# Pre-registro de RERUN-A

**Fecha:** 4 de septiembre de 2026 · **Estado:** congelado **antes** de cualquier medición.
El commit que introduce este documento precede a todo artefacto de la reejecución.
**Exigido por:** `tfm-statistical-reviewer` (C-1 a C-8), `tfm-experiment-auditor` y
`tfm-rag-evaluator`, los tres en `FAIL` sobre el plan anterior por no ser un pre-registro.

Sin pre-registro, cualquier resultado de una reejecución es racionalizable después. Esto lo
impide, y por eso se escribe entero antes de medir.

## 1. Pregunta experimental

> ¿Modifica la corrección del espacio de embeddings la evidencia que llega al agente y las
> decisiones que toma, sobre exactamente el mismo conjunto, modelo, umbral y política de
> suficiencia?

No es una pregunta sobre si el sistema es bueno. Es sobre si el defecto era inocuo.

## 2. Variable manipulada: **una sola**

| | Antes | Después |
|---|---|---|
| Recuperación | espacio de embeddings **sin control**: dos modelos mezclados | espacio **derivado del proveedor** que vectoriza la consulta |

**Todo lo demás idéntico**, y se declara para que la comparación sea limpia: política de
suficiencia **v2.1** (v2.2 queda implementada, probada y **sin medir**, para RERUN-B) · umbral
0,79 · conjunto `synthetic_v2` · semilla 20260901 · corpus 0.1.0 · bosque aleatorio con
calibración isotónica cv=5 · filtro de motor · conjunto anotado.

## 3. Unidad de análisis, N y K

**Vocabulario fijado. Estos términos no se intercambian en ningún documento.**

| Término | Qué es | Valor |
|---|---|---|
| **N** | ventanas o sesiones de origen **independientes** | **5** |
| **K** | condiciones experimentales aplicadas por ventana | por determinar tras el diagnóstico del distractor |
| **ejecuciones** | combinaciones efectivamente evaluadas | 17 históricas |

| Contraste | Unidad | N |
|---|---|---|
| Inferencia sobre el sistema | ventana de origen | 5 |
| Entre condiciones, permutación dentro de bloque | ventana con varias condiciones | 3 bloques |
| Sistema frente a línea base en condiciones adversas | ventana | 3 |
| Escenario adverso | ventana mal clasificada | 2 |
| Recuperación | consulta anidada en ventana | 6 consultas de 5 ventanas |
| Umbral, calibración, matriz de confusión | sesión de validación | 12 |

**Eliminar una condición cambia K, no N.** Confundirlos sería la variante fina del error de
pseudorreplicación ya registrado.

## 4. Métricas que se registran, todas antes de mirar

| # | Métrica | Unidad |
|---|---|---|
| M1 | vector de decisiones, caso a caso | ejecución |
| M2 | **vector de motivos** de cada abstención | ejecución |
| M3 | señales continuas: confianza, cobertura, documentos aplicables, fuentes distintas | ejecución |
| M4 | conjunto de fragmentos recuperados, con identificador | ejecución |
| M5 | duplicados por mezcla de espacios, con la unidad de §7 | ejecución |
| M6 | las seis líneas base | conjunto |
| M7 | métricas de recuperación de las **cinco** estrategias | consulta |

M2 es la que impide confundir «abstiene por lo mismo» con «abstiene igual».

## 5. Líneas base, y cuáles son control de integridad

**Invariantes por construcción.** No dependen de la recuperación: se recalculan **solo como
control** y **deben salir idénticas**.

| Línea base | Valor que debe reproducirse |
|---|---|
| `ALWAYS_ABSTAIN` | 12/17 · 12/12 en condiciones sin evidencia completa |
| `ALWAYS_EXPLAIN` | 5/17 |
| `ALWAYS_EXPLAIN_WHEN_MODEL_CONFIDENT` | 3/17 · 0/12 |
| **Techo alcanzable** | 15/17 |

> **Regla de parada.** Si **cualquiera** de las cuatro cambia, la reejecución se detiene: sería
> prueba de que cambió algo más que el espacio vectorial. Es un control negativo gratuito.

**Se recalculan** porque sí dependen de la recuperación: `ABSTAIN_IF_NO_EVIDENCE_RETRIEVED`
(6/17 antes) y el sistema.

## 6. Criterio de interpretación, fijado ahora

**No hay expectativa direccional.** Eliminar la mitad de los candidatos puede subir o bajar
cualquier cifra.

| Desenlace | Cómo se interpreta |
|---|---|
| Las decisiones **no cambian** | **No** significa que el defecto fuera inocuo. Con cobertura binaria, techo saturado y N = 5, el instrumento puede no tener resolución. Se reporta como «sin efecto detectable con este instrumento», nunca como validación de v2.1 |
| Las decisiones **cambian** | El resultado nuevo es el canónico. **No** significa que la implementación nueva sea mejor: es la primera interpretable bajo el contrato correcto |
| Cambia una **línea base invariante** | **Parada.** Se cambió más de una variable |
| Cambian los conjuntos y no las decisiones | Se reporta así, y es informativo: el defecto tocaba candidatos redundantes |

**Compromiso de publicación incondicional:** el resultado se publica sea cual sea su signo,
junto al anterior, que no se sobrescribe.

**Bandera roja declarada:** si el resultado nuevo fuera *mejor* en toda dimensión, se
sospechará de un segundo cambio no declarado antes de celebrarlo.

## 7. Duplicados: unidad definida antes de contar

El recuento anterior es `EMBEDDING_DUPLICATION_PREVALENCE: UNIT_UNDEFINED_IN_LEGACY_RESULT`.
Tres reconstrucciones dieron tres cifras —24/150, 27/140 y 8/50— porque **la unidad no estaba
declarada**. Ninguna se adopta por coincidencia entre auditores.

**Unidad canónica, fijada aquí:**

| | |
|---|---|
| **Numerador** | posiciones del conjunto recuperado ocupadas por un `chunk_id` ya presente en una posición anterior del **mismo** conjunto |
| **Denominador** | posiciones totales del conjunto recuperado, sumadas sobre las ejecuciones con conjunto no vacío |
| **Unidad** | posición dentro de un conjunto recuperado, por ejecución |
| **«Duplicado»** | segunda y sucesivas apariciones del mismo `chunk_id`; la primera no cuenta |

Las cifras antiguas se conservan como reconstrucciones históricas, etiquetadas.

## 8. Comparación antes/después: **descriptiva, nunca inferencial**

Se publica caso a caso: consulta, conjunto anterior, conjunto canónico, duplicados eliminados,
fragmentos nuevos, cambio de orden, evidencia aceptada, decisión.

> **No se calcula ningún valor p ni intervalo sobre diferencias entre ejecuciones que comparten
> la misma ventana de origen.** Es trazabilidad, no contraste.

## 9. Valores p: qué se puede y qué no

El `p = 0,008` está retirado. El `p = 0,037` **no entra en la memoria** y debe recalcularse tras
la reejecución.

**Potencia declarada de antemano, por número de condiciones comparables:**

| K | p mínimo alcanzable |
|---|---|
| 4 | 0,016 |
| 3 | 0,037 |
| **2** | **0,125** |

> Si el diseño canónico deja **dos** condiciones comparables, el p mínimo es 0,125 y **ninguna
> inferencia confirmatoria es posible**. Se acepta el hecho y se reportan resultados
> descriptivos, comparación por ventana, efecto observado y limitación de potencia.
>
> **No se añadirán condiciones para conseguir significación.** El trabajo no necesita un valor
> p por debajo de 0,05 para ser defendible.

## 10. Qué se hace si una condición resulta inválida

La condición de distractor está en `PENDING_CANONICAL_RETRIEVAL_DIAGNOSIS`. Se reejecuta como
**diagnóstico no puntuado** y, con recuperación limpia, se le aplica el criterio: ¿recupera
evidencia distinta de la condición parcial? ¿entra el distractor? ¿cambia el orden? ¿manipula
una variable independiente?

Solo entonces se clasifica como `VALID_CONDITION`, `REDUNDANT_WITH_PARTIAL` o
`INVALID_CONDITION`. **No se fuerza su conservación**, y **no se decide con la recuperación
declarada no canónica**, que es lo que el plan anterior hacía.

## 11. Enmiendas

Ninguno de estos criterios se modifica tras observar resultados sin registrar una **enmienda
explícita, fechada y con commit**, en la línea de `ENM-U01`, `ENM-A01` y `ENM-E01`.
