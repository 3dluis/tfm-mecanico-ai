# Capítulo 6: Conclusiones

## Conclusiones provisionales sobre la pregunta de investigación

La pregunta de investigación plantea un ciclo diagnóstico completo: identificar un patrón de fallo no representado en el conocimiento disponible, formular una hipótesis a partir del análisis contextual y longitudinal de la telemetría OBD-II, contrastarla mediante evidencia y, únicamente cuando esta resulte suficiente, incorporar la hipótesis validada como conocimiento reutilizable.

En el estado actual del trabajo no es posible ofrecer todavía una respuesta definitiva. La evaluación experimental sigue en curso, y algunos de los componentes necesarios para estudiar el ciclo completo requieren completar su instrumentación. En particular, debe comprobarse experimentalmente la identificación de patrones no representados en el conocimiento disponible y el mecanismo mediante el que una hipótesis validada puede incorporarse y recuperarse posteriormente como conocimiento reutilizable.

El desarrollo realizado permite, sin embargo, establecer la estructura metodológica necesaria para estudiar el tramo correspondiente a la formulación y validación de hipótesis. La arquitectura separa la información obtenida de la telemetría, la inferencia producida por el modelo especializado, la recuperación de información documental, la verificación de su aplicabilidad y soporte, la evaluación de suficiencia y la generación de la explicación. Esta separación permite examinar de forma independiente si una hipótesis dispone realmente de evidencia suficiente y establecer la abstención como una posible decisión cuando dicha evidencia no permite validarla.

La evaluación se desarrolla sobre telemetría OBD-II sintética, generada bajo condiciones controladas y parametrizada a partir de documentación técnica del vehículo de referencia. Esa configuración permite reproducir los experimentos y controlar los mecanismos de fallo representados. No permite, en cambio, establecer por sí sola que el comportamiento observado se generalice a telemetría procedente de vehículos reales. La evaluación con datos reales se considera, por tanto, una etapa posterior de validación externa.

La respuesta definitiva a la pregunta de investigación quedará condicionada a la finalización del diseño experimental previsto, la evaluación sobre el conjunto de prueba reservado y la comprobación de los componentes que permiten cerrar el ciclo completo definido por la pregunta. Los resultados obtenidos hasta ese momento deberán interpretarse exclusivamente dentro de las condiciones experimentales en las que fueron producidos.

## Limitaciones

La interpretación de los resultados está condicionada, en primer lugar, por la procedencia de los datos. La evaluación utiliza telemetría OBD-II sintética, lo que permite controlar las condiciones representadas y reproducir los experimentos, pero no incorpora toda la variabilidad presente en un vehículo en operación. Factores como el desgaste de los componentes, las condiciones ambientales, las diferencias entre conductores, el ruido de los sensores y la interacción entre fallos quedan fuera del entorno experimental actual.

El estudio utiliza un único vehículo de referencia, un Mazda 3 BK de 2007 con motor Z6. Esta decisión permite mantener coherencia entre la configuración mecánica representada, los códigos de avería y la documentación técnica utilizada, pero limita la generalización de los resultados a otros vehículos, generaciones, motores y fabricantes.

La identificación de patrones no representados en el conocimiento disponible requiere una evaluación específica que permita distinguir entre reconocer una clase previamente aprendida y detectar un comportamiento que el sistema no conocía. El modelo de diagnóstico utilizado trabaja sobre clases conocidas. Su rendimiento de clasificación no puede interpretarse, por tanto, como evidencia de esa capacidad.

De forma análoga, el ciclo definido por la pregunta de investigación requiere que una hipótesis que haya superado el proceso de validación pueda incorporarse y recuperarse posteriormente como conocimiento reutilizable, impidiendo al mismo tiempo la incorporación de hipótesis no validadas. La evaluación experimental de este mecanismo debe completarse antes de responder a esta parte de la pregunta.

El número de casos anotados y la utilización de diferentes variantes documentales sobre una misma ventana de telemetría limitan el tamaño efectivo de la muestra. Las ejecuciones realizadas sobre una misma ventana se consideran medidas relacionadas y no observaciones independientes, por lo que el análisis se plantea principalmente de forma comparativa y por casos.

Algunas etapas de la evaluación permanecen abiertas en esta primera entrega. El conjunto de prueba continúa reservado para la evaluación final. Las condiciones experimentales cuya manipulación o recuperación documental sigue en comprobación no se interpretan como resultados definitivos.

## Líneas futuras

La principal línea de continuidad consiste en evaluar el sistema sobre telemetría OBD-II procedente de vehículos reales. Esta validación permitiría estudiar hasta qué punto el comportamiento observado bajo condiciones sintéticas se mantiene frente a la variabilidad introducida por sensores, condiciones ambientales, estilos de conducción, desgaste e interacción entre diferentes mecanismos de fallo.

Una segunda línea consiste en extender la evaluación a otros vehículos y configuraciones mecánicas. Esto permitiría comprobar especialmente la capacidad del sistema para determinar la aplicabilidad de la documentación recuperada cuando existen diferencias entre fabricantes, modelos, generaciones y motores.

También resulta necesario ampliar el número y la diversidad de los casos diagnósticos, incluyendo combinaciones de fallos y situaciones en las que la información disponible sea ambigua, incompleta o aparentemente pertinente pero no aplicable. Esta ampliación permitiría evaluar con mayor precisión tanto la generación de hipótesis como la decisión de abstenerse.

Una vez establecido el comportamiento del ciclo diagnóstico, pueden estudiarse además aspectos de despliegue que no forman parte de la evaluación experimental central de este trabajo, como su ejecución sobre una plataforma embarcada y su integración con aplicaciones destinadas a la interacción con el usuario.

## Consideraciones finales

Una de las cuestiones que atraviesa este trabajo es la diferencia entre formular una explicación plausible y disponer de evidencia suficiente para sostenerla. En un sistema diagnóstico, ambas situaciones pueden producir textos igualmente convincentes, aunque solo una de ellas permite avanzar hacia una hipótesis validada.

Por esta razón, la arquitectura desarrollada mantiene separados los procesos de observación, inferencia, recuperación documental, verificación y decisión. Encontrar un fragmento no equivale a disponer de evidencia, del mismo modo que una referencia puede existir y no sostener aquello que se afirma. La ausencia de evidencia suficiente tampoco se transforma en evidencia por el hecho de que un modelo pueda redactar una respuesta.

La evaluación final deberá determinar hasta qué punto esta separación permite recorrer el ciclo completo planteado por la pregunta de investigación. Hasta entonces, las conclusiones deben permanecer limitadas a aquello que los experimentos efectivamente hayan demostrado.
