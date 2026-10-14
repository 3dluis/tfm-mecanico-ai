# Viabilidad de completar o acotar el alcance de la pregunta principal

**Fecha:** 14 de octubre de 2026 · **Qué es:** qué costaría cada una de las dos alternativas y qué
riesgo lleva cada una · **Qué NO hace:** no ejecuta ningún experimento, no modifica la pregunta, no
toca los objetivos y no cambia el título

---

## 0. Antes del análisis: la pregunta citada no es la vigente

Conviene decirlo primero, porque cambia el marco de todo lo demás y porque llevarlo al tutor sin
comprobarlo sería peor que no consultarlo.

La pregunta que el encargo enuncia —«¿Puede un **sistema inteligente híbrido identificar patrones de
fallo no representados** en su conocimiento disponible, generar hipótesis diagnósticas […] y
validarlas mediante evidencia antes de **incorporarlas como conocimiento reutilizable**?»— es la
**formulación amplia**, y está **descartada desde el 12 de septiembre de 2026**.

La descartó **`ADR-004`**, cuyo estado es «aceptada» y cuyo campo de decisión dice: «la dirección del
TFM, por escrito, sobre la versión enviada». Su texto es explícito:

> «La pregunta canónica es la acotada, la que el capítulo 1 enuncia […]. La formulación amplia queda
> descartada. Sus dos términos sin instrumentación pasan a alcance y a líneas futuras; **no son
> limitaciones de la respuesta, porque no forman parte de la pregunta**.»

Y el motivo por el que se descartó es **exactamente** el que el encargo señala ahora: de los cinco
términos de la formulación amplia, «dos —la identificación de patrones no representados y la
incorporación de conocimiento reutilizable— **no tenían implementación ni fase en el plan de
veinte**, y así lo declaraba la propia memoria».

La pregunta vigente, la única que la memoria escribe y en un solo sitio, es:

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis sin
> fundamento?

**Comprobado hoy sobre los nueve ficheros de la memoria:** ninguno contiene «patrones no
representados», «conocimiento reutilizable» ni «sistema inteligente híbrido». `ADR-004` se aplicó
entero, y la memoria no arrastra la formulación amplia en ningún sitio.

### Qué significa esto para la decisión

| Si se parte de… | Entonces… |
|---|---|
| **la pregunta vigente** (`ADR-004`) | **no hay desajuste**. Las tres ausencias de la matriz de capacidades no son partes de la pregunta: son alcance declarado y líneas futuras. La alternativa **B ya está ejecutada desde septiembre**, por decisión de la dirección |
| **la formulación amplia** | hay desajuste, y es el que `ADR-004` resolvió hace cinco semanas. Reabrirlo es legítimo, pero es **revocar una decisión de la dirección**, no corregir un descuido |

El análisis que sigue se hace de todos modos, porque la decisión de revisar `ADR-004` es del autor y
del director, y conviene que la tomen con el coste delante.

---

## 1. Alternativa A · Completar experimentalmente las dos capacidades

Los dos experimentos **ya están diseñados**: `ADR-004` los conservó a propósito, con sus brazos y
sus criterios de aceptación intactos, en `docs/methodology/diseno-gates-pi-pendientes.md`. No hay
que diseñarlos; hay que implementarlos y ejecutarlos.

### A.1 · Gate `UNREPRESENTED_PATTERN_VALIDATION`

| | |
|---|---|
| **Trabajo necesario** | una partición `leave_one_class_out` con la clase excluida en el registro; un mecanismo de detección fuera de distribución —umbralizar la confianza calibrada máxima, con el umbral fijado sobre validación y **sin ver la clase excluida**—; un motivo de abstención nuevo, `PATTERN_NOT_REPRESENTED`, distinto del de confianza baja; y un control del conocimiento paramétrico del modelo de lenguaje |
| **Experimentos** | **cuatro brazos**: representado; no representado pero documentado; no representado ni documentado; y un control de observabilidad con ventanas de 10 s |
| **Dependencias** | reentrenar el modelo de diagnóstico **una vez por clase excluida**; reconstruir el conjunto; un conjunto anotado nuevo para los cuatro brazos; y el corpus documental, que no se redistribuye |
| **Recursos** | el reentrenamiento del bosque es de minutos. El conjunto anotado es trabajo manual |
| **Riesgos metodológicos** | el criterio declara que **queda no concluyente** si el modelo de lenguaje nombra la clase excluida sin evidencia: el riesgo de terminar sin resultado está escrito en el propio diseño. Y el umbral de detección fuera de distribución se fija sobre una muestra pequeña |
| **Tiempo estimado** | **5 a 8 días** de trabajo efectivo: 2 a 3 de implementación, 1 de anotación, 1 de ejecución y 1 a 3 de redacción |
| **Impacto sobre los objetivos** | OE3 recuperaría «determinar cuándo estos no se encuentran representados», que `ADR-004` le quitó |

### A.2 · Gate `REUSABLE_KNOWLEDGE_VALIDATION`

| | |
|---|---|
| **Trabajo necesario** | un almacén de hipótesis validadas con caso, diagnóstico, afirmaciones, citas, veredicto, versión del corpus e identificador de ejecución; la vía negativa —que una abstención **no** deje registro—; la recuperación de antecedentes sin que cuenten para la suficiencia; y la invalidación cuando el corpus cambia y una cita deja de ser aplicable |
| **Experimentos** | cuatro medidas, dos de las cuales **deben dar cero exacto**: ninguna hipótesis abstenida incorporada, y ningún caso en que un antecedente satisfaga por sí solo la suficiencia |
| **Dependencias** | un conjunto de casos **equivalentes** que todavía no existe: hacen falta pares de casos lo bastante parecidos para que el antecedente se recupere, y lo bastante distintos para que no sea el mismo caso |
| **Recursos** | implementación de almacén y recuperación, más la construcción del conjunto de pares |
| **Riesgos metodológicos** | el más serio, y el diseño lo nombra: **la circularidad**. Un antecedente que satisface la suficiencia por sí solo convierte una explicación conservada en evidencia de sí misma. El criterio exige cero, y un solo caso lo refuta |
| **Tiempo estimado** | **8 a 12 días**: 4 a 6 de implementación, 2 de construcción del conjunto, 1 de ejecución y 1 a 3 de redacción |
| **Impacto sobre los objetivos** | OE5 recuperaría la incorporación de conocimiento reutilizable |

### A.3 · Lo que la alternativa A supone en conjunto

| Dimensión | Valoración |
|---|---|
| **Tiempo total** | **13 a 20 días** de trabajo efectivo, los dos gates juntos, sin contar la revisión |
| **Dependencia bloqueante** | ninguna de las dos depende de `P2`, que sigue bloqueado por memoria |
| **Impacto sobre el título** | lo acercaría a lo registrado: «sistema inteligente» tendría al menos una capacidad de detección de lo no representado detrás |
| **Impacto sobre los capítulos** | capítulo 2 —OE3 y OE5 ampliados—, capítulo 4 —dos fases nuevas con su instrumentación—, capítulo 5 —dos apartados—, capítulo 6 —dos objetivos reescritos y la pregunta respondida en más partes—. Entre 4 000 y 6 000 palabras |
| **Defensa ante el jurado** | **mejor si salen bien, peor si salen a medias**. Un gate no concluyente es un apartado que el tribunal preguntará y que no se puede responder. El de conocimiento reutilizable tiene además un criterio de cero exacto: un solo caso de circularidad lo refuta, y habría que publicarlo |
| **Riesgo principal** | que el calendario no llegue. El depósito es el **13 de noviembre** o el **4 de diciembre de 2026**: 13 a 20 días de trabajo efectivo caben, pero sin margen para que un resultado salga no concluyente y haya que explicarlo |

---

## 2. Alternativa B · Ajustar el alcance a lo demostrado

| Dimensión | Valoración |
|---|---|
| **Trabajo necesario** | **ninguno sobre el alcance**: `ADR-004` ya lo hizo el 12 de septiembre y la memoria está alineada. Lo que queda es de presentación: que el **título** deje de prometer lo que la pregunta ya no pide |
| **Experimentos** | ninguno |
| **Dependencias** | ninguna |
| **Recursos** | el tiempo de una conversación con el director y el de rehacer la portada |
| **Riesgos metodológicos** | **ninguno nuevo.** El riesgo que existe es el contrario y ya está declarado: el título registrado promete dos capacidades que el trabajo no entrega, y es `D-06` |
| **Tiempo estimado** | **1 día**, y es de redacción |
| **Impacto sobre los objetivos** | ninguno: los cinco tienen fase y métrica desde `ADR-004` |
| **Impacto sobre el título** | aquí está todo el impacto. Es la decisión `D-06`, con tres alternativas preparadas |
| **Impacto sobre los capítulos** | ninguno en el contenido. Las menciones del título en portada, encabezado y pie se regeneran con un campo |
| **Defensa ante el jurado** | **sólida**, y por una razón concreta: el recorte **no es una renuncia ante la dificultad** sino una decisión documentada, fechada, tomada por la dirección y motivada por una auditoría que encontró dos términos sin instrumentación. Eso se defiende mejor que cualquier resultado |

---

## 3. Comparación

| | **A · completar** | **B · ajustar** |
|---|---|---|
| Tiempo | 13-20 días | 1 día |
| Experimentos nuevos | 2 gates, 8 brazos y medidas | ninguno |
| Riesgo de resultado no concluyente | **alto**: está escrito en los dos criterios | ninguno |
| Riesgo de calendario | **real** frente al depósito de noviembre | ninguno |
| Qué gana el trabajo | dos capacidades evaluadas y un título más justo | claridad entre lo que promete y lo que demuestra |
| Qué arriesga | terminar con dos apartados a medias que el tribunal preguntará | que el título registrado cambie, con el trámite que eso exige |
| Estado hoy | **no iniciada** | **ejecutada desde el 12-09-2026** |

## 4. Recomendación, con su límite

**La alternativa B, y además ya está hecha.** Tres razones:

1. **No hay desajuste que reparar.** La pregunta vigente no contiene las dos capacidades ausentes, y
   no las contiene porque la dirección decidió quitarlas tras auditar que no tenían instrumentación.
   Lo que queda por alinear es el **título**, no el alcance.
2. **El coste de A es real y su resultado no está garantizado.** Los dos criterios de aceptación
   contemplan explícitamente terminar sin conclusión, y uno exige un cero exacto que un solo caso
   refuta. Dos apartados a medias en el capítulo 5 son peores que dos líneas futuras bien
   enunciadas.
3. **B se defiende mejor.** Un tribunal pregunta por qué el alcance se recortó, y la respuesta es
   una decisión fechada con su auditoría detrás. Un tribunal que pregunta por un gate no concluyente
   obtiene una respuesta peor.

**El límite de esta recomendación:** si la dirección quiere revisar `ADR-004`, la decisión es suya y
este documento no la sustituye. Lo que sí puede decir es que revisarla significa **revocar una
decisión propia tomada hace cinco semanas**, no corregir un descuido del trabajo. Esa diferencia
conviene que esté clara antes de preguntarlo.

## 5. Una tercera vía, por si el tiempo lo permite

Si el director prefiere no cerrar la puerta y el calendario lo admite, hay una opción intermedia que
el diseño ya contempla: ejecutar **solo el primer gate**, el de patrones no representados, que es el
más barato —5 a 8 días—, el que menos dependencias nuevas tiene y el único de los dos que no exige
construir un conjunto de casos equivalentes. El segundo quedaría como línea futura, que es donde
`ADR-004` lo puso.

No se recomienda iniciarla sin que el director lo indique, y no se ha iniciado.
