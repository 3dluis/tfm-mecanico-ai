# Matriz de capacidades: implementada, evaluada y demostrada

**Fecha:** 14 de octubre de 2026 · **Qué es:** qué hace el sistema, qué de eso se ha medido y qué de
lo medido sostiene una afirmación · **Por qué existe:** una capacidad implementada no es una
capacidad demostrada, y una capacidad no evaluada tampoco está necesariamente ausente. Confundir
los tres niveles es el error que un tribunal busca primero

## 1. Los tres niveles

| Nivel | Qué significa | Cómo se comprueba |
|---|---|---|
| **Implementada** | existe código que la ejecuta y produce una salida | se ejecuta y se mira la salida |
| **Evaluada** | se midió con un criterio fijado **antes** de medir, sobre un conjunto declarado | hay un registro de ejecución con su configuración |
| **Demostrada** | lo medido sostiene una afirmación con su alcance declarado, y el alcance se respeta en el texto | la afirmación se puede rastrear hasta su registro, y sus límites están escritos |

Los tres son independientes. Hay capacidades implementadas y no evaluadas; hay capacidades evaluadas
cuyo resultado **no** demuestra lo que el título promete; y hay una, la más incómoda, que está
implementada, evaluada y **demostrada como insuficiente**.

## 2. La matriz

| Capacidad | Implementada | Evaluada | Evidencia | Limitaciones | Estado |
|---|---|---|---|---|---|
| **Diagnóstico vehicular** | **sí**: bosque aleatorio sobre 139 descriptores de ventanas de 120 s | **sí**: E6 y E7 sobre validación, y el diagnóstico entra en E19 sobre prueba | exactitud 0,878 y F1 macro 0,879 frente a 0,286 y 0,074 de la clase mayoritaria; confianza calibrada de ECE 0,144 a 0,085 | un vehículo, datos sintéticos, catálogo cerrado de cinco fallos; dos condiciones por debajo del resto —termostato 9 de 14, encendido 7 de 14—; una ejecución y una semilla, sin intervalos | **demostrada**, con el alcance de un vehículo y datos sintéticos |
| **Identificación de patrones no representados** | **no** | **no** | — | el catálogo es cerrado por construcción. El comportamiento ante una avería ajena a él no se ha examinado ni se ha intentado | **ausente**, y declarada como limitación y línea futura |
| **Generación de hipótesis** | **sí**: el verificador construye tres afirmaciones por caso desde la atribución, y el modelo de lenguaje las redacta | **sí**, pero **de forma indirecta**: se mide si la decisión se respeta y si la cita existe, no la calidad de la hipótesis | 17 de 17 salidas válidas del adaptador canónico; 0 citas inexistentes en las tres configuraciones | **la calidad de la hipótesis no se evalúa**: no hay anotación de qué afirmaciones serían admisibles. Y `L-26`: 3 de 17 salidas contienen una cifra que el verificador no produjo | **implementada y evaluada parcialmente**; no demostrada como generación de hipótesis correctas |
| **Recuperación de evidencia** | **sí**: cinco estrategias sobre el corpus del manual | **sí**: E12, reejecución canónica | guiada por el diagnóstico encuentra el procedimiento en 5 de 5 casos puntuados; la semántica pura, en 0 de 5 | cinco casos. Y la estrategia que gana **usa los códigos de la condición anotada**, que el sistema no tiene antes de diagnosticar: su ventaja es una cota asistida, no una capacidad comparable | **demostrada como cota asistida**, no como recuperación autónoma |
| **Validación de la evidencia** | **sí**: criterio de suficiencia con cuatro comprobaciones deterministas | **sí**: E15 sobre 17 casos, E18 con cuatro ablaciones y E19 sobre prueba | con 5, 6 y 7 fragmentos aplicables delante, la cobertura de afirmaciones es **0,00**; sin criterio de suficiencia, 6 de 9 ejecuciones explican lo que debían callar | las comprobaciones son deterministas: que coincidan con un juicio externo sobre lo que un fragmento sostiene **no se ha medido**. El criterio se revisó dos veces sobre los mismos casos | **demostrada como trazabilidad y como regla de decisión**; **no demostrada** como juicio de soporte |
| **Abstención ante evidencia insuficiente** | **sí**: decisión explícita con el motivo registrado | **sí**: E15, E18, E19 y P1 | sobre prueba, **0 de 14** ejecuciones que debían abstenerse terminaron en explicación, y **2 de 8** que debían explicar terminaron en abstención | el intervalo de Wilson de ese 0 de 14 llega a **0,215**, y depende del nivel de confianza, del modelo estadístico y de una independencia entre ejecuciones que estas no tienen. Siete ventanas | **demostrada en la muestra evaluada**, con el intervalo publicado. **No** es una garantía de riesgo cero |
| **Incorporación de conocimiento reutilizable** | **no** | **no** | — | el sistema recupera y verifica documentación, pero **no aprende de los casos resueltos** ni conserva explicaciones validadas. Está en la prospectiva, con las preguntas que abriría | **ausente**, y declarada |
| **Mantenimiento predictivo** | **no** | **no** | — | el trabajo diagnostica una condición **presente** en una ventana de telemetría. No predice fallos futuros, no estima vida útil ni programa intervenciones. Ninguna métrica del trabajo es de predicción temporal | **ausente**. No estaba en el alcance acotado |

## 3. Qué parte de la pregunta principal queda respondida

La pregunta es:

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis sin
> fundamento?

Tiene tres partes, y no están al mismo nivel.

| Parte de la pregunta | Estado | Qué la sostiene | Qué le falta |
|---|---|---|---|
| **«explicar el diagnóstico a partir de datos OBD-II»** | **respondida** | el diagnóstico se obtiene y se explica; el modelo de lenguaje produce la explicación en un esquema fijo y respeta el veredicto en 17 de 17 | que la explicación sea **correcta** no se mide; `L-26` muestra que puede contener una cifra que nadie le dio |
| **«rastreando cada explicación hasta su evidencia de origen»** | **respondida por construcción, no por medición** | las 51 afirmaciones conservan su observación de origen y sus fragmentos; ninguna cita se asigna fuera de las comprobaciones | que esas comprobaciones coincidan con un juicio independiente **no se ha medido**: el conjunto anotado no incluye las afirmaciones admisibles. Y la trazabilidad cubre identificadores, no cifras |
| **«reconocer cuándo la evidencia no es suficiente»** | **respondida en la muestra evaluada** | 0 de 14 sobre prueba; con documentación aplicable delante la cobertura es cero; sin criterio de suficiencia, 6 de 9 explican lo que debían callar | siete ventanas independientes y un intervalo que llega al 21,5 %. Y el comportamiento ante un **diagnóstico erróneo** solo se ha visto en un escenario de dos ventanas |

**La respuesta global es «parcialmente sostenida»**, y la matriz dice dónde está cada parte: la
tercera es la más sólida, la segunda se cumple por diseño y no por medida, y la primera tiene un
hueco declarado en la fidelidad numérica del texto.

## 4. Lo que esta matriz no permite decir

- Que el sistema **detecte averías nuevas**. No lo hace y no se ha intentado.
- Que **anticipe** fallos. No hay ninguna métrica temporal en el trabajo.
- Que la recuperación guiada sea **mejor** que las demás en condiciones de uso: usa una anotación que
  en uso no existiría.
- Que el cero de falsa confianza sea una **garantía**. Es una observación sobre catorce ejecuciones
  de siete ventanas.
- Que las capacidades ausentes sean **imposibles** con esta arquitectura: están fuera del alcance
  evaluado, que es distinto de estar descartadas.
