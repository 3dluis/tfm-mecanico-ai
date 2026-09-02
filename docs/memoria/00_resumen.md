# Resumen

> Estado: redactado sobre resultados de datos sintéticos. Cuando E19 se ejecute, se
> reescriben las cifras y la última frase. Extensión orientativa: 250–300 palabras.

Los modelos de lenguaje producen explicaciones fluidas incluso cuando no disponen de
evidencia que las sostenga. En el diagnóstico de vehículos, donde una explicación se traduce
en una intervención mecánica, ese comportamiento no es una molestia sino un riesgo. Este
trabajo estudia si un agente con recuperación aumentada por evidencia puede explicar el
diagnóstico de un vehículo a partir de telemetría OBD-II rastreando cada afirmación hasta su
evidencia de origen, y si puede reconocer cuándo la evidencia disponible no basta y
abstenerse en lugar de generar una hipótesis sin fundamento.

El agente separa tres responsabilidades que habitualmente se confunden. Un modelo de
diagnóstico especializado, con confianza calibrada, clasifica ventanas de telemetría; la
atribución de sus descriptores produce evidencia observacional localizada en señal y tiempo.
Un sistema de recuperación sobre el manual de taller del vehículo, filtrado por
aplicabilidad al motor y modelo concretos, produce evidencia documental con procedencia
completa. Un verificador determinista, independiente del modelo de lenguaje, construye
afirmaciones ancladas en ambas clases de evidencia, comprueba que cada cita sostiene lo
afirmado y decide entre explicar y abstenerse. El modelo de lenguaje, un modelo pequeño
ejecutado localmente y ajustado solo en el formato de la tarea, redacta la decisión ya
tomada.

El experimento central manipula una sola variable, la evidencia documental disponible, bajo
cuatro condiciones: completa, parcial, ausente y con distractor. Sobre datos OBD-II
sintéticos calibrados contra el manual del vehículo, el agente explica cuando la evidencia
está y se abstiene cuando se retira, con datos, modelo, atribución y confianza idénticos; el
modelo de lenguaje respeta esa decisión y no produce citas inexistentes. El trabajo declara
que sus datos no son reales y presenta sus resultados como condicionales a esa limitación,
que es la primera de las que enumera.

**Palabras clave:** diagnóstico vehicular, OBD-II, recuperación aumentada, explicabilidad,
trazabilidad de evidencia, abstención, modelos de lenguaje.
