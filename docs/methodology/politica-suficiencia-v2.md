# Política de suficiencia v2 — el papel del fragmento

**Fecha:** 4 de septiembre de 2026 · **Motivada por:** hallazgo `LEXICAL-SUPPORT-CONFOUND`
(`docs/experiments/hallazgo-lexical-support-confound.md`) · **Estado:** documentada **antes**
de implementarse y de volver a medir. El commit que introduce este documento precede al que
introduce el código y al que produce el resultado.

**Comparación limpia.** Frente a v1 no cambian el conjunto de datos, los casos, el corpus, el
modelo especializado, la confianza, las condiciones, los umbrales ni el filtro de
aplicabilidad por motor. Cambia **una sola cosa**: qué cuenta como soporte de una afirmación.

## 1. Qué falla en v1

`is_diagnostic_content` decide con dos señales: el **tipo de documento** y la **presencia de
cualquier código de avería**. Todo el corpus es manual de taller, así que la primera no
discrimina; y las tablas llevan decenas de códigos, así que la segunda tampoco. Una tabla que
nombra la señal observada pasa las tres comprobaciones y sostiene una afirmación que no
sostiene.

El diagnóstico del problema es de **granularidad**: la unidad de decisión era el documento y
tiene que ser el fragmento.

## 2. Taxonomía de papeles del fragmento

Tres papeles, definidos por lo que el fragmento **hace**, no por el fichero del que viene.

| Papel | Qué es | ¿Puede sostener una afirmación por sí solo? |
|---|---|---|
| `PROCEDURAL_DIAGNOSTIC_EVIDENCE` | Procedimiento de diagnóstico: pasos de inspección, criterios de decisión, valores esperados, bifurcaciones condicionales | **Sí** |
| `SUPPORTING_DIAGNOSTIC_REFERENCE` | Lógica o condición de detección, especificaciones, descripción del monitor. Habla del código con contenido técnico, pero no dice cómo se comprueba | **No.** Puede acompañar a un procedimiento y aporta contexto |
| `CODE_DEFINITION_OR_TABLE` | Tabla de códigos, autodiagnóstico, listado, definición del código | **No** |

Un cuarto valor, `UNCLASSIFIED`, para lo que no encaja: se trata como si no pudiera sostener,
porque la ausencia de prueba no es prueba.

## 3. Rasgos observables, generales para todo el corpus

La clasificación se decide con rasgos que se pueden leer en cualquier fragmento del manual, sin
mencionar ninguna señal, ningún código ni ninguna condición de fallo concretos.

| Rasgo | Cómo se observa |
|---|---|
| `n_dtc` | Número de códigos distintos que porta el fragmento |
| `inspection_steps` | Marcas de acción de inspección: comprobar, medir, desconectar, inspeccionar, reparar o sustituir |
| `decision_criteria` | Marcas de decisión: pregunta con respuesta sí/no, «ir al paso siguiente», especificación o valor de referencia |
| `detection_logic` | Marcas de lógica de detección: la unidad de control vigila, determina, la condición se cumple |
| `table_layout` | Marcas de listado: el encabezado del fragmento anuncia tabla, autodiagnóstico, listado o índice de códigos |
| `procedure_heading` | El encabezado nombra un único código como asunto del fragmento |

**Por qué `n_dtc` discrimina.** En este manual un procedimiento se titula por el código que
diagnostica y trata **uno**, a veces una familia pequeña. Una tabla enumera los códigos de un
sistema. La distribución del corpus lo confirma: de 6 105 fragmentos, 657 portan un código y
71 portan dos, mientras la cola llega a más de cuarenta. El corte se fija en **tres o más
códigos** como indicio de enumeración, y **nunca decide solo**: siempre se combina con la
presencia o ausencia de marcas procedimentales.

## 4. Reglas de clasificación

En este orden, y aplicables a cualquier fragmento:

1. Si tiene **pasos de inspección** y **criterios de decisión**, y no es un listado
   (`n_dtc < 3` o encabezado de procedimiento) → `PROCEDURAL_DIAGNOSTIC_EVIDENCE`.
2. Si no, y tiene **lógica de detección** o valores de referencia sobre el código →
   `SUPPORTING_DIAGNOSTIC_REFERENCE`.
3. Si no, y es un listado (`n_dtc >= 3`) o su encabezado anuncia tabla o autodiagnóstico →
   `CODE_DEFINITION_OR_TABLE`.
4. En cualquier otro caso → `UNCLASSIFIED`.

Ninguna regla nombra una señal, un código ni un fallo. La misma clasificación se aplica a un
fragmento sobre frenos que a uno sobre la sonda de oxígeno.

## 5. Política de soporte

Una afirmación se marca **sostenida** si, entre los fragmentos aplicables al vehículo:

- existe **al menos uno** con papel `PROCEDURAL_DIAGNOSTIC_EVIDENCE` que además **menciona la
  señal** y **porta el código esperado** de la condición.

Los fragmentos con papel de referencia o de tabla **se conservan como cita acompañante** cuando
hay un procedimiento que sostiene la afirmación, y se registran con su papel; **nunca la
sostienen solos**.

**Orden de examen.** Los candidatos se examinan **por papel antes que por puntuación de
recuperación**: primero los procedimientos, después las referencias, después las tablas. En v1
las dos plazas de cita las podía ocupar una tabla bien puntuada y el procedimiento correcto no
llegaba a examinarse. Ese orden era un artefacto de la implementación, no una decisión.

## 6. Lo que esta política **no** hace

- **No introduce ninguna regla específica de caso.** Nada que diga «si contiene tal expresión,
  rechazar», ni condiciones de termostato, sonda o fuga de vacío. Si apareciera una regla así,
  la política dejaría de ser un criterio y pasaría a ser una racionalización del resultado.
- **No toca el filtro de aplicabilidad por motor**, que el experimento v1 muestra que funciona:
  el procedimiento del motor incorrecto se degrada a coincidencia parcial y no se acepta. El
  problema está aislado en la suficiencia diagnóstica.
- **No cambia ningún umbral**, ni el punto de operación de la confianza, ni el número mínimo de
  fragmentos, ni la cobertura exigida.
- **No cambia el conjunto de casos, el corpus, el modelo ni las condiciones.**

## 7. Riesgo que hay que vigilar, declarado de antemano

Exigir un procedimiento puede llevar al extremo contrario: **abstención excesiva**. Dos casos
con evidencia completa se apoyan hoy en tablas, y uno de ellos ni siquiera examinó el
procedimiento disponible. Si tras la corrección esos casos dejan de explicar, el resultado no
será mejor: será distinto y peor en otra dimensión.

Por eso la comparación entre versiones **no se juzga por la exactitud agregada**. Se reportan,
antes y después:

- explicaciones sostenidas y explicaciones sin soporte suficiente;
- abstenciones correctas y abstenciones falsas;
- cobertura de explicación sobre los casos con evidencia completa.

Una política que abstiene siempre obtiene abstención perfecta y utilidad nula. Ese desenlace
está enumerado desde el principio entre los que refutarían el trabajo, y sigue estándolo.

## 8. Qué se hará con el resultado

Se compara con el resultado congelado de v1, caso a caso y por condición, con el motivo de cada
cambio. **El resultado de v1 no se sobrescribe.** Si la versión revisada empeora en alguna
dimensión, se reporta; si mejora, se reporta con la advertencia de que la corrección es
posterior al hallazgo y por tanto no es una predicción ciega.
