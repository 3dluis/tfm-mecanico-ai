# Informe de seguimiento 2 — borrador de contenido

**TFM · Máster Universitario en Inteligencia Artificial · Universidad Alfonso X el Sabio**
**Autor:** Luis Daniel Díaz Díaz · **Fecha del borrador:** 1 de octubre de 2026

> ⚠ **Este borrador no tiene formato oficial.** Los formatos de los informes de seguimiento
> están en el mosaico *Documentación* del campus; aquí está el contenido, el continente es del
> campus. El informe se entrega por el campus y se comunica al director su disponibilidad.
>
> **Convocatoria objetivo: diciembre de 2026.** El informe 2 se entrega el **06/11/2026** y el
> depósito es el **04/12/2026**. La decisión, tomada el 1 de octubre, busca margen para cerrar la
> evaluación final sin abrir el conjunto de prueba con prisa y para revisar la memoria completa
> después; la alternativa de noviembre dejaba dos semanas hasta el informe y seis hasta el
> depósito.

---

## 1. Título del trabajo

**Título registrado en la propuesta (14/07/2026):** «Sistema inteligente para el diagnóstico y
mantenimiento predictivo de vehículos».

El alcance efectivo no es el mantenimiento predictivo, sino el soporte verificable de las
explicaciones diagnósticas y la abstención ante evidencia insuficiente. El título definitivo se
consensúa con el director; la propuesta sigue siendo:

> *Explicación diagnóstica trazable y abstención ante evidencia insuficiente: evaluación de un
> agente con recuperación aumentada sobre telemetría OBD-II*

`[AUTHOR_DECISION_REQUIRED]` — confirmación del título definitivo.

## 2. Pregunta de investigación y objetivos

La pregunta no ha cambiado desde el informe 1 y es la acotada, fijada como canónica el 12 de
septiembre de 2026 por decisión de la dirección (ADR-004):

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis
> sin fundamento?

Lo que sí cambió, tras el feedback escrito del director de septiembre, es que la formulación
amplia anterior quedó descartada y la memoria se revisó entera para que una sola investigación
la atraviese. Dos objetivos específicos se reescribieron para no exigir lo que la evaluación no
cubre: OE3 pasó de «identificar y caracterizar patrones» a evaluar el diagnóstico del modelo y
caracterizar su confianza y sus señales, y OE5 dejó de exigir la contribución de los componentes
—que son las ablaciones, ejecutadas ahora— para pedir la distinción entre explicaciones
sostenidas, explicaciones sin soporte y abstenciones innecesarias.

## 3. Estado de avance

### 3.1 Memoria

Los seis capítulos están redactados sobre el diseño ejecutado: unas 23 400 palabras de texto
fuente, con 15 tablas numeradas en el capítulo 4 y 7 en el capítulo 5. Bibliografía con 40
entradas citadas, todas verificadas en fuente primaria, sobre una lista maestra de 144
referencias de dominio y 19 de método.

La memoria declara en la introducción que la evaluación experimental sigue en desarrollo y que
los resultados son parciales, como pidió el director.

### 3.2 Trabajo experimental

De las veinte fases del plan están ejecutadas y registradas las de entorno y datos, las del
modelo de diagnóstico salvo su evaluación sobre el conjunto de prueba, las de corpus y
recuperación y las del agente y la suficiencia. Hay 22 registros de ejecución en el repositorio,
cada uno con su semilla, versiones y parámetros, y 347 funciones de prueba en verde.

| Fase | Estado a 1 de octubre de 2026 |
|---|---|
| E1 entorno · E2 datos sintéticos · E4 análisis exploratorio · E5 preprocesamiento | cerradas |
| E6 línea base · E7 modelo temporal · E9 atribución | cerradas sobre validación |
| E10 corpus del vehículo · E11 ingesta en pgvector · E12 evaluación de recuperación | cerradas |
| E13 agente con modelo de lenguaje · E13b conjunto de ajuste · E15 suficiencia · E15b umbral | cerradas sobre validación |
| E17 condiciones de evidencia | parcial: completa, parcial y ausente evaluadas; la condición con distractor, diagnosticada y pendiente de rediseño |
| **E18 ablaciones** | **ejecutada en esta entrega** (§3.4) |
| **RERUN-B, política v2.2** | **ejecutada en esta entrega** (§3.4) |
| E3 datos reales · E8 y E19 evaluación final sobre test · E20 demostración | pendientes |

### 3.3 Lo que se corrigió desde el informe 1

El trabajo de este periodo ha sido, en buena parte, de corrección y verificación, y conviene
declararlo como avance porque es lo que hace defendible lo demás.

- **Un defecto del índice documental.** El 4 de septiembre se detectó que el índice contenía dos
  representaciones vectoriales por fragmento y que ninguna búsqueda declaraba en cuál buscaba.
  Se corrigió, se pre-registró la comparación y se reejecutaron la recuperación, la suficiencia
  en sus dos modos, la generación del conjunto de ajuste y la redacción con el modelo de
  lenguaje. Ninguna de las diecisiete decisiones cambió; los conjuntos recuperados cambiaron en
  diez de los diecisiete casos, siempre por adición.
- **Siete auditorías independientes** sobre la memoria (experimental, de evidencia, de RAG,
  estadística, de referencias, de autenticidad de la redacción y un tribunal simulado), con sus
  informes conservados. De 39 hallazgos mayores, 30 quedaron corregidos y 8 parcialmente; no
  queda ninguno crítico abierto.
- **Cifras que el texto publicaba y los registros no sostenían.** Cinco discrepancias
  localizadas y resueltas citando el registro vigente, entre ellas un «9 de 9» de respeto al
  veredicto que en realidad era «7 de 7 evaluables».
- **Trazabilidad del repositorio.** El historial se normalizó, se publicó el mapa de
  identificadores de commit, se versionaron las figuras y tablas que la memoria usa con su
  procedencia, y se añadieron una guía de revisión para el tribunal y dos scripts de
  reproducción.

### 3.4 Resultados

Todas las cifras son de **validación**; el conjunto de prueba sigue cerrado por construcción y
no se ha abierto.

| Subpregunta | Qué se midió | Resultado |
|---|---|---|
| PI.1 diagnóstico | bosque aleatorio frente a la clase mayoritaria, y calibración | exactitud 0,878 frente a 0,286; error de calibración de 0,144 a 0,085 |
| PI.1 modelo temporal | GRU frente al bosque | 0,823 frente a 0,879 de F1 macro: **resultado negativo**, conservado |
| PI.2 recuperación | cinco estrategias sobre el corpus del vehículo | similitud sin filtros 0,00 de acierto; guiada por el diagnóstico 1,00 |
| PI.2 trazabilidad | afirmaciones con observación y con cita que las sostiene | 51 afirmaciones, todas con su observación; 12 con soporte documental, y esa igualdad es una propiedad del verificador, no una medición independiente |
| PI.3 abstención | decisiones sobre 17 casos anotados | falsa confianza 0 de 9 ejecuciones (3 ventanas); abstención innecesaria 2 de 5; cobertura 3 de 5 |
| PI.4 distractores | condición con evidencia parecida pero no aplicable | **no sostenida con el diseño actual**: con el filtro de motor la condición no añade ningún distractor que la condición parcial no tuviera |
| Modelo de lenguaje | tres configuraciones, 17 casos | con adaptador: 17 de 17 salidas válidas, 0 citas inexistentes; cita, eso sí, fragmentos que el verificador no aceptó en 6 de 9 afirmaciones |

**E18, ablaciones.** Cuatro ablaciones pre-registradas sobre los mismos diecisiete casos, cada
una cambiando una pieza. La falsa confianza se cuenta sobre nueve ejecuciones de tres ventanas de
telemetría y la abstención innecesaria sobre cinco de cinco ventanas:

| Configuración | Falsa confianza | Abstención innecesaria | Cobertura |
|---|---|---|---|
| Canónica | 0 de 9 | 2 de 5 | 3 de 5 |
| Sin atribución | 0 de 9 | 2 de 5 | 3 de 5 |
| Sin recuperación semántica | 0 de 9 | 5 de 5 | 0 de 5 |
| Sin criterio de suficiencia | **6 de 9** | 0 de 5 | 5 de 5 |
| Solo umbral de confianza | **9 de 9** | 2 de 5 | 3 de 5 |

La lección es que **una confianza diagnóstica alta no basta si la evidencia documental no sostiene
la explicación**: con una puerta de confianza sola el sistema explica las doce ejecuciones que
debían terminar en abstención, incluidas las tres en que la recuperación no devuelve nada, y
exigiendo solo que exista algún fragmento aplicable aparecen seis explicaciones sin soporte de
nueve. La atribución resultó sustituible por un criterio estadístico simple sin que cambiara
ninguna decisión ni ninguna evidencia: no interviene en la política de abstención, y su
contribución está en la trazabilidad y en la explicación de la predicción, que es una dimensión no
evaluada aquí. La ablación de la recuperación semántica quedó **inconclusa**, porque la ruta léxica
no recupera nada con una consulta en prosa; se conserva como tal, y la variante que lo mediría
queda declarada en una enmienda fechada como medición nueva, no como corrección de esta.

**Segunda versión de la política de suficiencia.** La corrección del defecto de la puerta de
códigos de avería, implementada en septiembre y hasta ahora sin medir, se midió en los tres modos.
Sobre los diecisiete casos no cambia ninguna decisión ni ningún motivo. Lo que mejora es el
**control de aplicabilidad ante un diagnóstico incorrecto**: en el escenario adverso el diagnóstico
del modelo es «sin fallo», que el mapa de códigos no declara, y con la regla anterior el sistema
aceptaba como soporte dos de las tres afirmaciones construidas para ese diagnóstico equivocado, con
una cobertura de 0,67; con la regla nueva ninguna obtiene soporte y la cobertura pasa a 0,00. Las
seis ejecuciones se abstenían antes y se abstienen después, pero antes lo hacían por un margen
sobre evidencia que no debía haberse aceptado. El defecto queda corregido y medido, con dos pruebas
de regresión que reproducen la conducta anterior y su cierre. La nueva política pasará a ser la
canónica **con la evaluación final**, de modo que los resultados ya publicados quedan bajo la
política previa y la evaluación final bajo la nueva, cada uno con su registro.

Aplicada la regla de decisión fijada antes de evaluar, la respuesta a la pregunta queda
**parcialmente sostenida**, con carácter provisional: las cifras del agente son de desarrollo,
porque el criterio, su umbral y las anotaciones se ajustaron sobre los mismos diecisiete casos
con que se evalúan, y la evaluación final sobre el conjunto de prueba es la que puede confirmar
si se mantienen.

## 4. Porcentaje de avance estimado

| Bloque | Avance | Base de la estimación |
|---|---|---|
| Marco teórico | 90 % | capítulo cerrado y referencias verificadas; el flujo PRISMA formal sigue pendiente de acceso institucional |
| Marco metodológico | 95 % | redactado sobre el diseño ejecutado, con sus unidades de análisis y sus enmiendas declaradas |
| Trabajo experimental | 80 % | ejecutadas y registradas las fases de datos, modelo, corpus, recuperación, agente, suficiencia y ablaciones; faltan la evaluación final sobre test y el rediseño de la condición con distractor |
| Resultados y discusión | 75 % | capítulo 5 completo sobre validación; faltan las cifras de test y la comparación final con los trabajos revisados |
| Conclusiones | 70 % | conclusiones provisionales por objetivo; la respuesta definitiva depende de la evaluación final |
| **Global** | **≈ 80 %, provisional** | estimación sujeta a revisión según las fases que falten realmente antes de la evaluación final |

`[AUTHOR_DECISION_REQUIRED]` — la estimación es provisional y del autor; el director la valida y la
califica. Lo que queda antes de la evaluación final, y que condiciona el porcentaje: construir y
cerrar la anotación de los casos sobre la partición de prueba, abrir el conjunto con su declaración,
medir, llevar las cifras a la memoria y reevaluar con los auditores. El rediseño de la condición con
distractor y el reentrenamiento del adaptador no condicionan la evaluación final y se declaran como
trabajo posterior.

## 5. Dificultades encontradas

1. **Fuente de datos reales.** Sigue sin resolverse y, desde ADR-003, no bloquea la pregunta:
   cada conjunto declara su procedencia y la validación externa es una etapa posterior. Lo que
   sí limita es el alcance de lo que puede afirmarse, y así se declara.
2. **Un defecto metodológico propio, detectado por auditoría interna.** La mezcla de espacios de
   embeddings obligó a congelar cifras ya escritas, pre-registrar una reejecución y repetir
   cuatro fases. El coste fue alto; la alternativa era publicar cifras cuya procedencia no podía
   determinarse.
3. **Una condición experimental que no manipula lo que decía manipular.** Con el filtro de motor
   activo, la condición con distractor recupera los mismos fragmentos que la condición parcial.
   El diseño necesita casos nuevos, anotados de modo que la condición parcial no contenga ya el
   distractor. Está declarado como limitación y como trabajo inmediato.
4. **Criterios reescritos después de ver resultados.** Tres: las subpreguntas el 1 de
   septiembre, el umbral de confianza y el criterio de suficiencia. Los tres quedan declarados
   con su fecha y su motivo junto al criterio original, en lugar de presentarse como fijados de
   antemano.

## 6. Trabajo previsto hasta el depósito

1. Rediseñar y anotar la condición con distractor, con su pre-registro, para que PI.4 pueda
   interpretarse.
2. Reentrenar el adaptador del modelo de lenguaje sobre el conjunto regenerado y volver a medir,
   para que su resultado no dependa de ejemplos anteriores a la corrección del índice.
3. Anotar las afirmaciones admisibles y la evidencia mínima de cada caso, que es lo que
   convertiría la trazabilidad en una medición independiente del verificador.
4. Cerrar el diseño y **abrir el conjunto de prueba** para la evaluación final, con la
   declaración explícita y la razón escrita que el propio código exige, y la demostración
   integrada sobre esa partición. El plan, el orden de ejecución y el gate de ocho
   comprobaciones están escritos, y las ocho en PASS: la última era congelar por escrito las reglas
   de selección y anotación de los casos, que quedan fijadas con su huella y comprobadas por pruebas.
   El conjunto **sigue cerrado**: lo que falta no es una comprobación más, sino la declaración formal
   de apertura con su razón escrita, que es el punto de no retorno.
5. Volcar la memoria en la plantilla oficial, regenerar el índice y resolver las dos decisiones
   abiertas con el director: el título definitivo y la edición de las normas APA.
