# Pre-registro de E18 (ablaciones) y de RERUN-B (política v2.2)

**Fecha:** 1 de octubre de 2026 · **Estado:** congelado **antes** de cualquier medición. El
commit que introduce este documento precede al del código de las ablaciones y al de cualquier
artefacto de salida. · **Motivado por:** el objetivo específico OE5, que pide la contribución de
los componentes, y el hallazgo `EMPTY-DTC-GATE-BYPASS`, cuya corrección quedó implementada y sin
medir (`docs/methodology/politica-puerta-dtc.md`).

Dos ejecuciones distintas, con preguntas distintas, que comparten conjunto, modelo y umbral:

| | Pregunta | Variable manipulada |
|---|---|---|
| **E18** | ¿Qué parte del comportamiento observado aporta cada componente del sistema? | el componente que se retira o se degrada |
| **RERUN-B** | ¿Cambia alguna decisión al exigir el requisito explícito de la puerta de códigos? | la versión de la política de suficiencia, v2.1 → v2.2 |

## 1. Lo que no se toca

Ni el conjunto de prueba, que sigue cerrado, ni los umbrales, ni el conjunto anotado de
diecisiete casos, ni el corpus, ni el índice, ni la semilla (20260901), ni el modelo de
diagnóstico, ni su calibración, ni el adaptador del modelo de lenguaje. Las ablaciones **no
redactan**: se ejecutan sin proveedor de lenguaje, porque lo que miden es la decisión y la
evidencia, no la redacción. Los artefactos vigentes de E15 no se sobrescriben: cada ablación
escribe su propio registro.

## 2. Las cuatro ablaciones, definidas antes de ejecutarlas

Cada una cambia **exactamente un** elemento respecto de la configuración canónica (verificador
v2.1, umbral 0,79, recuperación guiada por el diagnóstico, observaciones por atribución).

| Id | Nombre | Qué se cambia, operativamente | Qué aislaría |
|---|---|---|---|
| `A1` | sin atribución | las tres observaciones de cada caso dejan de elegirse por importancia de Shapley y se eligen por la desviación tipificada del descriptor respecto de la media de la clase sin fallo en entrenamiento, tomando las de mayor valor absoluto. El resto del recorrido es idéntico | qué aporta la atribución frente a un criterio estadístico simple, tanto en la decisión como en el soporte documental |
| `A2` | sin recuperación semántica | la consulta no se vectoriza: la recuperación es léxica sobre el texto completo, con los mismos filtros de vehículo, motor y códigos de avería del diagnóstico, y la misma profundidad | cuánto del acierto de la recuperación guiada procede de la similitud semántica y cuánto de los filtros y de la coincidencia léxica |
| `A3` | sin criterio de suficiencia | se retira el criterio compuesto: el sistema explica siempre que exista al menos un fragmento aplicable y se abstiene solo si no hay ninguno | el efecto del criterio completo sobre los dos tipos de error |
| `A4` | umbral único | la decisión se toma solo con la confianza calibrada frente al umbral 0,79, ignorando cobertura, número de fragmentos y de fuentes y contradicciones | cuánto añade el criterio compuesto sobre una puerta de confianza sola |

**Solapamiento declarado de antemano.** `A3` y `A4` coinciden conceptualmente con las dos
políticas de referencia que el capítulo 5 ya publica —explicar cuando hay evidencia y explicar
cuando el modelo confía—. Se ejecutan igual, porque la referencia actual se calculó a mano sobre
el registro y una ablación ejecutada por el mismo camino que el sistema es una comprobación
independiente de esa aritmética. Si no coinciden, manda la ablación y la discrepancia se
investiga antes de publicar.

## 3. Métricas que se registran, fijadas ahora

Las mismas que el sistema, caso a caso y sin agregados nuevos: vector de decisiones; motivos de
cada abstención; falsa confianza y abstención innecesaria con su número de ejecuciones y de
ventanas independientes; cobertura sobre los casos con evidencia completa; número de fragmentos
aplicables; cobertura de afirmaciones. Para `A1` y `A2`, además, el conjunto de fragmentos que
llega al verificador, para poder decir si la diferencia viene de la evidencia o de la decisión.

## 4. Criterio de interpretación

**No hay expectativa direccional para `A1` ni `A2`.** Retirar la atribución puede mejorar o
empeorar la decisión: el criterio exige que el fragmento mencione la señal observada, y una señal
elegida por desviación tipificada puede estar mejor o peor documentada que la que el modelo usa.

| Desenlace | Cómo se interpreta |
|---|---|
| Una ablación **no cambia** ninguna decisión | el componente retirado no es necesario **para estos diecisiete casos**, lo que no equivale a que no aporte. Se reporta así, y nunca como que el componente sea prescindible |
| Una ablación **empeora** la falsa confianza | el componente contribuye a evitar el error de mayor riesgo, y la magnitud se publica con su denominador |
| Una ablación **mejora** alguna tasa | se publica igual y sin reinterpretarla: sería evidencia de que el componente cuesta cobertura, o de que el criterio está más ajustado al conjunto de lo que convendría |
| `A3` o `A4` **no coinciden** con la política de referencia publicada | hay un defecto en una de las dos cuentas; se para, se localiza y se corrige antes de publicar ninguna de las dos |

Ninguna ablación se usa para atribuir causalidad a la arquitectura completa: con diecisiete
casos sobre cinco ventanas, y un criterio ajustado sobre ellos, lo que una ablación sostiene es
qué cambia **en esta muestra** al quitar una pieza.

## 5. RERUN-B: qué se compara y qué sería una parada

La política v2.2 solo cambia una cosa: el requisito de la puerta de códigos se lee de la
declaración del diagnóstico —`DTC_REQUIRED`, `DTC_NOT_APPLICABLE`, `DTC_MAPPING_UNAVAILABLE` o
`DTC_OPTIONAL`— en lugar de exigirse siempre.

| | Predicción registrada antes de medir |
|---|---|
| Modo oracular, diecisiete casos | **ninguna decisión cambia.** Los cinco diagnósticos del conjunto están declarados con códigos, de modo que el requisito es `DTC_REQUIRED` en todos y la puerta se comporta igual |
| Modo adverso, seis ejecuciones | **las decisiones pueden cambiar.** El diagnóstico es «sin fallo», que no está declarado en el mapa de códigos: bajo v2.1 la puerta se abría y bajo v2.2 el requisito pasa a `DTC_MAPPING_UNAVAILABLE` y ninguna afirmación puede sostenerse. Es exactamente el hallazgo `EMPTY-DTC-GATE-BYPASS`, y esta ejecución es la que lo mide |

> **Regla de parada.** Si en el modo oracular cambia alguna decisión, la ejecución se detiene: el
> cambio de política habría tocado algo más que el requisito, y la comparación dejaría de ser de
> una variable.

Si el modo adverso confirma la predicción, el hallazgo pasa de «registrado, no corregido» a
«corregido y medido», y el capítulo 5 lo dirá con esa precisión: la corrección cierra una puerta
que no debía estar abierta, y no mejora ninguna cifra del conjunto principal.

## 6. Qué queda fuera

La evaluación final sobre el conjunto de prueba (E19), que exige una declaración explícita y una
razón escrita para abrirlo. El rediseño de la condición con distractor, que necesita anotar casos
nuevos y tiene su propio pre-registro. El reentrenamiento del adaptador del modelo de lenguaje,
que es una decisión aparte con su coste declarado. Ninguna de las tres se adelanta aquí.

## 7. Enmiendas

Ningún criterio de este documento se modifica tras observar un resultado sin registrar una
enmienda explícita, fechada y con su motivo, en la línea de `ENM-U01` y `ENM-A01`.
