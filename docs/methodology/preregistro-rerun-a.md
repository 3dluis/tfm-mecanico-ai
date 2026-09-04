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

**Un segundo cambio de código, con su alcance verificado.** Se corrigió además la propagación
del filtro de motor en la degradación a la estrategia mixta. Verificado en los artefactos: la
degradación **solo ocurre cuando el diagnóstico no tiene códigos asociados**, y en los modos
oracular y no oracular las 17 predicciones aciertan, de modo que **nunca degrada**. La
corrección no altera ninguna celda de `RERUN-A`; su efecto se limita a los artefactos adversos,
que quedan fuera del plan. Se declara aquí en vez de omitirse.

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

---

# Enmienda ENM-S01

**Fecha:** 4 de septiembre de 2026 · **Anterior a toda medición** · **Motivada por:**
`STAT-MAJ-022` y `STAT-MAJ-023`, que encontraron tres grados de libertad que este mismo
pre-registro dejaba abiertos.

## S-1 · La prueba principal, designada

Faltaba, y sin ella el pre-registro no cubría la inferencia.

| | |
|---|---|
| **Prueba principal** | permutación exacta **dentro de bloque** |
| **Bloque** | ventana de origen con varias condiciones |
| **Unidad de permutación** | la asignación de condición dentro de una misma ventana |
| **H₀** | la decisión del sistema es **independiente** de la condición de disponibilidad de evidencia dentro de la ventana |
| **H₁** | la decisión depende de la condición |
| **Lateralidad** | **una cola**: solo cuenta a favor que las explicaciones se concentren en la condición con evidencia completa |
| **Estadístico** | número de bloques cuya única decisión de explicar recae sobre evidencia completa |
| **Nombre** | `T-PRINCIPAL`. Cualquier otra prueba es secundaria y se rotula como tal |

**Ningún otro contraste puede heredar el rótulo de principal después de ver resultados.**

## S-2 · Potencia completa, incluido K = 5

La tabla anterior omitía K = 5, que es precisamente el que devuelve el valor retirado.

| K | p mínimo alcanzable | Nota |
|---|---|---|
| 5 | **0,008** | **`RETRACTED_INVALID_INFERENCE`.** Este K solo existe contando la condición de distractor, que está bajo diagnóstico. **Prohibido** mientras no se resuelva |
| 4 | 0,016 | |
| 3 | 0,037 | |
| 2 | **0,125** | sin resolución para inferencia confirmatoria |

**Fragilidad por margen, declarada:** si **un solo fallo** deja de explicar en la condición de
evidencia completa, el estadístico baja a 2 y **ningún K alcanza 0,05**. El resultado
inferencial pende de una decisión.

**Cláusula que faltaba.** El compromiso anterior decía «no se añadirán condiciones para
conseguir significación», y eso no cerraba la puerta real. Se añade:

> Tampoco se **conservará** una condición cuyo diagnóstico la declare redundante o inválida
> para sostener un K mayor, ni se **redesignará** qué prueba lleva un valor p ya calculado.
> El valor `0,008` queda `RETRACTED_INVALID_INFERENCE` y no puede reaparecer por ninguna vía,
> incluida la de que K vuelva a ser 5.

**No se realizará inferencia confirmatoria si el diseño efectivo no proporciona resolución
suficiente.** Se reportarán resultados descriptivos, comparación por ventana, efecto observado
y limitación de potencia. El trabajo no necesita un valor p por debajo de 0,05.

## S-3 · Líneas base como vector, no como razones

El defecto: expresadas como razones sobre 17 ejecuciones, y 17 depende de K. Si el diagnóstico
retira una condición, las cuatro cambian **por construcción** y la regla de parada salta sin
que nada vaya mal.

Se declaran como **vector ordenado de decisiones por (fallo, condición)** sobre el conjunto
común de ejecuciones presentes antes y después:

```
B = [
  b1 = decisiones de ALWAYS_ABSTAIN,                      por (fallo, condición)
  b2 = decisiones de ALWAYS_EXPLAIN,                      por (fallo, condición)
  b3 = decisiones de ALWAYS_EXPLAIN_WHEN_MODEL_CONFIDENT, por (fallo, condición)
  b4 = decisiones del TECHO alcanzable,                   por (fallo, condición)
]
```

> **Regla de parada.** `B_antes == B_después`, elemento a elemento, sobre el conjunto común.
> Si cualquier elemento cambia: **PARADA**, porque se modificó algo más que la recuperación.
>
> Un cambio de K **no** dispara la parada: reduce el conjunto común, y la comparación se hace
> sobre lo que queda en ambos.

## S-4 · Los dos requisitos del distractor, operacionalizados

Sobre identificadores de fragmento, comprobables **antes** de mirar ninguna decisión:

| | |
|---|---|
| **D-1** | existe al menos un `chunk_id` de los ficheros del distractor en el conjunto recuperado de la condición |
| **D-2** | la diferencia simétrica entre los `chunk_id` de la condición de distractor y los de la condición parcial, para la misma ventana, **no es vacía** |

Ambos se evalúan sobre el campo `retrieved` del artefacto de recuperación y se **congelan antes
de puntuar nada**. La clasificación resultante —válida, redundante o inválida— se registra
antes de calcular ninguna métrica que dependa de ella.
