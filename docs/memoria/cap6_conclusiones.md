# Capítulo 6: Conclusiones

## Conclusiones provisionales sobre la pregunta de investigación

La pregunta de investigación, enunciada en el capítulo 1, interroga dos capacidades del agente: que cada afirmación de su explicación pueda rastrearse hasta la evidencia que la sostiene, y que sepa reconocer cuándo esa evidencia no basta. Sobre ambas, la evaluación realizada hasta esta versión permite adelantar una respuesta parcial que las ejecuciones pendientes deberán confirmar.

El desarrollo realizado establece la estructura metodológica que la pregunta requiere. La arquitectura separa la información obtenida de la telemetría, la inferencia producida por el modelo especializado, la recuperación de información documental, la verificación de su aplicabilidad y soporte, la evaluación de suficiencia y la generación de la explicación. Esta separación permite examinar de forma independiente si una hipótesis dispone realmente de evidencia suficiente y establecer la abstención como una posible decisión cuando dicha evidencia no permite validarla.

La evaluación se desarrolla sobre telemetría OBD-II sintética, generada bajo condiciones controladas y parametrizada a partir de documentación técnica del vehículo de referencia. Esa configuración permite reproducir los experimentos y controlar los mecanismos de fallo representados. No permite, en cambio, establecer por sí sola que el comportamiento observado se generalice a telemetría procedente de vehículos reales. La evaluación con datos reales se considera, por tanto, una etapa posterior de validación externa.

La respuesta definitiva quedará condicionada a la finalización del diseño experimental previsto y a la evaluación sobre el conjunto de prueba reservado. Los resultados obtenidos hasta ese momento deberán interpretarse exclusivamente dentro de las condiciones experimentales en las que fueron producidos.

## Limitaciones

La interpretación de los resultados está condicionada, en primer lugar, por la procedencia de los datos. La evaluación utiliza telemetría OBD-II sintética, lo que permite controlar las condiciones representadas y reproducir los experimentos, pero no incorpora toda la variabilidad presente en un vehículo en operación. Factores como el desgaste de los componentes, las condiciones ambientales, las diferencias entre conductores, el ruido de los sensores y la interacción entre fallos quedan fuera del entorno experimental actual.

El estudio utiliza un único vehículo de referencia, un Mazda 3 BK de 2007 con motor Z6. Esta decisión permite mantener coherencia entre la configuración mecánica representada, los códigos de avería y la documentación técnica utilizada, pero limita la generalización de los resultados a otros vehículos, generaciones, motores y fabricantes.

El modelo de diagnóstico trabaja sobre un catálogo cerrado de clases de fallo, de modo que el trabajo no examina el comportamiento del sistema ante averías ajenas a ese catálogo; esa extensión queda fuera del alcance y se recoge entre las líneas futuras.

El número de casos anotados y la utilización de diferentes variantes documentales sobre una misma ventana de telemetría limitan el tamaño efectivo de la muestra. Las ejecuciones realizadas sobre una misma ventana se consideran medidas relacionadas y no observaciones independientes, por lo que el análisis se plantea principalmente de forma comparativa y por casos.

Algunas etapas de la evaluación permanecen abiertas en esta primera entrega. El conjunto de prueba continúa reservado para la evaluación final. Las condiciones experimentales cuya manipulación o recuperación documental sigue en comprobación no se interpretan como resultados definitivos.

## Prospectiva

La continuación más clara es evaluar el sistema con telemetría OBD-II tomada de vehículos reales. Solo así puede verse si el comportamiento observado sobre datos sintéticos aguanta la variabilidad de la operación: conductores distintos, condiciones ambientales cambiantes, componentes desgastados, ruido de sensores y fallos que aparecen a la vez.

Conviene hacerlo sobre el vehículo de referencia, o sobre otro cuya documentación técnica tenga suficiente detalle para que telemetría, configuración mecánica y evidencia documental sigan correspondiéndose. El entorno experimental admite cambiar la fuente de telemetría sin tocar la lógica de recuperación, verificación y decisión. Cada fuente nueva, eso sí, obliga a revisar la parametrización, la segmentación temporal y la aplicabilidad de la documentación.

Vendrían después otros vehículos, otros motores, otros fabricantes. El trabajo se apoya hoy en una sola configuración mecánica, y ampliarla mostraría si la recuperación y la validación siguen funcionando cuando la documentación cambia de estructura, de nomenclatura, de códigos de avería y de procedimientos.

Hace falta también ampliar los casos anotados y hacerlos más difíciles: fallos simultáneos, evidencia que se contradice en parte, documentación que parece pertinente pero corresponde a otra configuración, y situaciones en las que más de una hipótesis encaja con la misma telemetría. Ese último caso es el que menos se ha explorado y el que más dice sobre cuándo el sistema debería abstenerse en lugar de elegir.

El despliegue sobre una plataforma embarcada abre otra línea. Permitiría medir latencia, consumo de recursos, funcionamiento sin conexión y operación continua sobre telemetría tomada directamente del vehículo. Llega después, porque lo que ahora está en juego es el ciclo diagnóstico y no sus condiciones de ejecución.

Queda abierta, por último, la posibilidad de conservar las explicaciones que superaron la validación para reutilizarlas en casos posteriores. Eso plantea preguntas propias: cómo se recupera una explicación validada cuando reaparece un caso equivalente, qué hacer cuando surge evidencia que la contradice, y qué impide que algo aceptado para un vehículo y unas condiciones concretas acabe aplicándose donde no corresponde. También exigiría una salvaguarda contra la circularidad, para que una explicación conservada no se convierta en evidencia de sí misma.

## Consideraciones finales

Una explicación plausible y una explicación sostenida por evidencia se parecen mucho sobre el papel. En diagnóstico, las dos pueden producir un texto convincente. Solo una permite dar una hipótesis por validada.

De ahí que la arquitectura mantenga separados lo que se observa, lo que el modelo infiere, lo que se recupera, lo que se verifica y lo que se decide. Encontrar un fragmento no es tener evidencia. Una referencia puede existir, estar bien citada y no sostener aquello para lo que se usa. Y cuando la evidencia falta, que un modelo sepa redactar una respuesta no la suple.

Queda por determinar hasta dónde llega esa separación al recorrer el ciclo completo que plantea la pregunta. Mientras tanto, las conclusiones no pueden ir más allá de lo que los experimentos hayan mostrado.
