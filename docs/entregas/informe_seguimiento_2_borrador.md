# Informe de seguimiento 2 — borrador de contenido

**TFM · Máster Universitario en Inteligencia Artificial · Universidad Alfonso X el Sabio**
**Autor:** Luis Daniel Díaz Díaz · **Fecha del borrador:** 1 de octubre de 2026

> ⚠ **Este borrador no tiene formato oficial.** Los formatos de los informes de seguimiento
> están en el mosaico *Documentación* del campus; aquí está el contenido, el continente es del
> campus. El informe se entrega por el campus y se comunica al director su disponibilidad.
>
> **Fechas del informe 2:** 15/10/2026 para la convocatoria de noviembre, 06/11/2026 para la de
> diciembre. Depósito: 13/11/2026 o 04/12/2026.
>
> `[AUTHOR_DECISION_REQUIRED]` — a qué convocatoria se opta. De esa decisión depende el plan de
> la sección 6: con noviembre quedan dos semanas hasta el informe y seis hasta el depósito.

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

**E18, ablaciones.** `[PENDIENTE: resultado de la ejecución de esta entrega]`

**RERUN-B, política v2.2 de la puerta de códigos.** `[PENDIENTE: resultado de la ejecución de
esta entrega]`

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
| **Global** | **≈ 80 %** | |

`[AUTHOR_DECISION_REQUIRED]` — la estimación es del autor; el director la valida y la califica.

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
   integrada sobre esa partición.
5. Volcar la memoria en la plantilla oficial, regenerar el índice y resolver las dos decisiones
   abiertas con el director: el título definitivo y la edición de las normas APA.
