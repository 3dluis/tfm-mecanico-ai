# ADR-004 · La pregunta de investigación canónica es la acotada

**Fecha:** 12 de septiembre de 2026 · **Estado:** aceptada · **Decide:** la dirección del TFM,
por escrito, sobre la versión enviada · **Sustituye a:** el registro `SD-01` de la revisión
integral, que quedaba pendiente de decisión.

## Contexto

La memoria circulaba con **dos formulaciones** de la pregunta de investigación. El capítulo 1
mantenía la acotada; el resumen, el objetivo general y las conclusiones habían adoptado una
formulación amplia procedente del material de agosto de 2026.

La revisión integral lo registró como `SD-01` y auditó componente a componente la segunda:
de sus cinco términos, uno tenía evidencia. Dos —la identificación de patrones no representados
y la incorporación de conocimiento reutilizable— no tenían implementación ni fase en el plan de
veinte, y así lo declaraba la propia memoria.

## Decisión

**La pregunta canónica es la acotada**, la que el capítulo 1 enuncia:

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis
> sin fundamento?

La formulación amplia queda descartada. Sus dos términos sin instrumentación pasan a alcance y a
líneas futuras; no son limitaciones de la respuesta, porque no forman parte de la pregunta.

## Consecuencias

El objetivo general vuelve a su enunciado aprobado. OE3 pierde «determinar cuándo estos no se
encuentran representados» y OE5 pierde la incorporación y recuperación de conocimiento
reutilizable, de modo que **los cinco objetivos específicos vuelven a tener fase y métrica**: no
queda ninguna fila sin instrumentar en la tabla de trazabilidad del capítulo 4.

`L-22` se retira del registro de limitaciones y `L-21` se reformula como acotación de alcance,
con severidad media. Los dos experimentos pre-registrados en
`docs/methodology/diseno-gates-pi-pendientes.md` **se conservan**: dejan de ser trabajo pendiente
del TFM y pasan a prospectiva, con su diseño y sus criterios de aceptación intactos por si una
continuación los ejecuta.

El capítulo 6 puede responder a la pregunta en lugar de aplazarla, con el alcance que los
experimentos pendientes acoten.

## Regla derivada

La pregunta de investigación y el objetivo general **se escriben una sola vez**: la pregunta en
el capítulo 1 y el objetivo general en el capítulo 2. El resto de secciones remite a esa
formulación en lugar de reescribirla. La reescritura en varios sitios es lo que produjo esta
divergencia, y la regla existe para que no vuelva a ocurrir.

## Qué no cambia

`ADR-003` sigue vigente: la pregunta dice «datos OBD-II», sin adjetivo. La procedencia de cada
conjunto se declara en cada cifra.
