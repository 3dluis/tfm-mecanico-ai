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

## Prospectiva

La principal línea de continuidad del trabajo consiste en realizar una validación externa con telemetría OBD-II obtenida de vehículos reales. Esta evaluación permitiría comprobar hasta qué punto el comportamiento observado sobre datos sintéticos se mantiene frente a la variabilidad propia de la operación real, incluyendo diferencias entre conductores, condiciones ambientales, desgaste de los componentes, ruido de los sensores e interacción entre mecanismos de fallo.

Esta validación debería realizarse preferentemente sobre el vehículo de referencia o sobre otro vehículo para el que exista documentación técnica con un nivel de detalle suficiente para mantener la correspondencia entre telemetría, configuración mecánica y evidencia documental. El entorno experimental ha sido diseñado de forma que la fuente de telemetría pueda sustituirse sin modificar la lógica general de recuperación, verificación y decisión, aunque cada nueva fuente de datos requeriría comprobar nuevamente la parametrización, la segmentación temporal y la aplicabilidad de la documentación utilizada.

Una segunda línea consiste en extender la evaluación a otros vehículos, motores y fabricantes. El trabajo actual utiliza una única configuración mecánica de referencia, por lo que ampliar el corpus y los casos permitiría estudiar si los mecanismos de recuperación y validación continúan siendo efectivos cuando la documentación presenta diferencias de estructura, nomenclatura, códigos de avería y procedimientos de diagnóstico.

También resulta relevante ampliar el conjunto de casos anotados y la diversidad de las condiciones experimentales. En particular, sería de interés incluir fallos simultáneos, evidencia parcialmente contradictoria, documentación aparentemente pertinente pero correspondiente a otra configuración mecánica y casos en los que más de una hipótesis diagnóstica resulte compatible con la telemetría observada. Esta ampliación permitiría estudiar con mayor profundidad la capacidad del sistema para discriminar entre hipótesis y determinar cuándo la evidencia disponible no permite sostener una única explicación.

Una línea adicional consiste en evaluar el sistema sobre una plataforma embarcada. El despliegue en hardware de borde permitiría medir latencia, consumo de recursos, comportamiento sin conexión y capacidad de operar de forma continua sobre telemetría adquirida directamente del vehículo. Esta evaluación pertenece a una etapa posterior, ya que el trabajo actual prioriza la validación del ciclo diagnóstico sobre las características de despliegue.

La evolución del mecanismo de conocimiento reutilizable, una vez implantado y evaluado, abre la posibilidad de estudiar cómo las hipótesis previamente validadas pueden recuperarse en situaciones posteriores, cómo deben actualizarse cuando aparece nueva evidencia y qué controles son necesarios para evitar que una conclusión aceptada en un contexto concreto se generalice indebidamente a otros vehículos o condiciones.

## Consideraciones finales

Una de las cuestiones que atraviesa este trabajo es la diferencia entre formular una explicación plausible y disponer de evidencia suficiente para sostenerla. En un sistema diagnóstico, ambas situaciones pueden producir textos igualmente convincentes, aunque solo una de ellas permite avanzar hacia una hipótesis validada.

Por esta razón, la arquitectura desarrollada mantiene separados los procesos de observación, inferencia, recuperación documental, verificación y decisión. Encontrar un fragmento no equivale a disponer de evidencia, del mismo modo que una referencia puede existir y no sostener aquello que se afirma. La ausencia de evidencia suficiente tampoco se transforma en evidencia por el hecho de que un modelo pueda redactar una respuesta.

La evaluación final deberá determinar hasta qué punto esta separación permite recorrer el ciclo completo planteado por la pregunta de investigación. Hasta entonces, las conclusiones deben permanecer limitadas a aquello que los experimentos efectivamente hayan demostrado.
