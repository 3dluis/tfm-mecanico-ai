# Capítulo 6: Conclusiones

## Conclusiones provisionales sobre los objetivos y la pregunta de investigación

Esta es una entrega intermedia. Las conclusiones recorren los objetivos específicos en su orden y terminan en el general, y en cada uno separan lo que los resultados parciales ya permiten observar de lo que requiere la evaluación final sobre el conjunto de prueba, que sigue cerrado. Ninguna cifra de este capítulo procede de ese conjunto.

**OE1, revisar el estado del conocimiento.** Cumplido en el alcance declarado. La revisión, inspirada en PRISMA pero sin su flujo formal, delimitó el vacío en cuatro frentes y fundamentó las tres decisiones de diseño del capítulo 1; sus límites, tres trabajos sin leer a texto completo y un cribado sin duplicación entre revisores, están declarados en el capítulo 3.

**OE2, establecer un entorno experimental reproducible.** Cumplido sobre telemetría sintética. El generador es determinista, los conjuntos se reparten por sesión, el conjunto de prueba está cerrado por construcción, el corpus conserva su huella y cada ejecución deja un registro con versión, semilla y parámetros; el registro del modelo de diagnóstico se reprodujo bit a bit. La validación externa con telemetría de vehículos reales no forma parte de este objetivo y queda como limitación y prospectiva.

**OE3, evaluar el diagnóstico a partir de la telemetría y caracterizar su confianza.** Cumplido parcialmente. El bosque aleatorio diagnostica muy por encima de la referencia mínima sobre validación y su confianza, mal calibrada en origen, significa lo que aparenta tras la calibración; la atribución produce para cada caso la evidencia observacional que las etapas posteriores consumen. Falta la evaluación sobre el conjunto de prueba. El modelo temporal no aportó ventaja sobre el tabular, y se conserva como resultado negativo.

**OE4, implementar y evaluar la recuperación y la verificación de evidencia.** Cumplido parcialmente sobre los diecisiete casos anotados. Toda afirmación admitida se rastrea hasta una observación y un fragmento aplicable que la sostienen, y ninguna cita apunta a algo que no la respalde; la recuperación solo encuentra el procedimiento correcto cuando la guía el código de avería asociado al diagnóstico, y ese resultado no cambió al corregir el índice documental y reejecutar. Queda pendiente la evaluación final, y el adaptador del modelo de lenguaje sigue entrenado sobre ejemplos anteriores a esa corrección.

**OE5, evaluar el comportamiento integrado bajo las cuatro condiciones de evidencia.** Cumplido parcialmente, y es donde los resultados parciales dicen más. La decisión cambia con la evidencia en la dirección correcta: en los doce casos que debían terminar en abstención el sistema se abstuvo, con una falsa confianza de 0 sobre 12, y en los cinco con evidencia completa explicó tres, con dos abstenciones innecesarias que proceden de la confianza del modelo y no del criterio de evidencia. La condición con distractor resultó redundante con la condición parcial en dos de los tres fallos cuando el filtro de motor está activo; el procedimiento del otro motor no sostuvo ninguna afirmación, pero la condición necesita un rediseño antes de sostener sobre ella una inferencia. Las ablaciones, que atribuirían el resultado a cada componente, no se han ejecutado.

**Objetivo general.** La evaluación experimental del agente está hecha en parte. Sobre datos sintéticos de un vehículo y sobre la partición de validación, los resultados indican que el agente mantiene una correspondencia verificable entre cada afirmación y la evidencia que la sostiene, y que se abstiene cuando la evidencia falta o no basta, sin haber explicado ningún caso en el que no debía hacerlo. Lo que la pregunta de investigación interroga se observa, por tanto, en las condiciones evaluadas. Lo que la evaluación final debe añadir es la medición sobre el conjunto de prueba, las ablaciones y el rediseño de la condición con distractor; hasta entonces la respuesta es parcial y se sostiene solo dentro de las condiciones en que se obtuvo.

## Limitaciones

La interpretación de los resultados está condicionada, en primer lugar, por la procedencia de los datos. La evaluación utiliza telemetría OBD-II sintética, lo que permite controlar las condiciones representadas y reproducir los experimentos, pero no incorpora toda la variabilidad presente en un vehículo en operación. Factores como el desgaste de los componentes, las condiciones ambientales, las diferencias entre conductores, el ruido de los sensores y la interacción entre fallos quedan fuera del entorno experimental actual.

El estudio utiliza un único vehículo de referencia, un Mazda 3 BK de 2007 con motor Z6. Esta decisión permite mantener coherencia entre la configuración mecánica representada, los códigos de avería y la documentación técnica utilizada, pero limita la generalización de los resultados a otros vehículos, generaciones, motores y fabricantes.

El modelo de diagnóstico trabaja sobre un catálogo cerrado de clases de fallo, de modo que el trabajo no examina el comportamiento del sistema ante averías ajenas a ese catálogo; esa extensión queda fuera del alcance y se recoge entre las líneas futuras.

El número de casos anotados y la utilización de diferentes variantes documentales sobre una misma ventana de telemetría limitan el tamaño efectivo de la muestra. Las ejecuciones realizadas sobre una misma ventana se consideran medidas relacionadas y no observaciones independientes, por lo que el análisis se plantea principalmente de forma comparativa y por casos.

Algunas etapas de la evaluación permanecen abiertas en esta primera entrega. El conjunto de prueba continúa reservado para la evaluación final. Las condiciones experimentales cuya manipulación o recuperación documental sigue en comprobación no se interpretan como resultados definitivos.

## Prospectiva

La continuación más clara es evaluar el sistema con telemetría OBD-II tomada de vehículos reales, porque solo así puede verse si el comportamiento observado sobre datos sintéticos aguanta la variabilidad de la operación: conductores distintos, condiciones ambientales cambiantes, componentes desgastados, ruido de sensores y fallos que aparecen a la vez.

Conviene hacerlo sobre el vehículo de referencia, o sobre otro cuya documentación técnica tenga suficiente detalle para que telemetría, configuración mecánica y evidencia documental sigan correspondiéndose. El entorno experimental admite cambiar la fuente de telemetría sin tocar la lógica de recuperación, verificación y decisión, aunque cada fuente nueva obliga a revisar la parametrización, la segmentación temporal y la aplicabilidad de la documentación.

Vendrían después otros vehículos, otros motores y otros fabricantes: el trabajo se apoya hoy en una sola configuración mecánica, y ampliarla mostraría si la recuperación y la validación siguen funcionando cuando la documentación cambia de estructura, de nomenclatura, de códigos de avería y de procedimientos.

Hace falta también ampliar los casos anotados y hacerlos más difíciles: fallos simultáneos, evidencia que se contradice en parte, documentación que parece pertinente pero corresponde a otra configuración, y situaciones en las que más de una hipótesis encaja con la misma telemetría. Ese último caso es el que menos se ha explorado y el que más dice sobre cuándo el sistema debería abstenerse en lugar de elegir.

El despliegue sobre una plataforma embarcada abre otra línea, que permitiría medir latencia, consumo de recursos, funcionamiento sin conexión y operación continua sobre telemetría tomada directamente del vehículo. Llega después, porque lo que ahora está en juego es el proceso diagnóstico y no sus condiciones de ejecución.

Queda abierta, por último, la posibilidad de conservar las explicaciones que superaron la validación para reutilizarlas en casos posteriores. Eso plantea preguntas propias: cómo se recupera una explicación validada cuando reaparece un caso equivalente, qué hacer cuando surge evidencia que la contradice, y qué impide que algo aceptado para un vehículo y unas condiciones concretas acabe aplicándose donde no corresponde. También exigiría una salvaguarda contra la circularidad, para que una explicación conservada no se convierta en evidencia de sí misma.

## Consideraciones finales

Una explicación plausible y una explicación sostenida por evidencia se parecen mucho sobre el papel, y en diagnóstico las dos pueden producir un texto igualmente convincente. Solo una permite dar una hipótesis por validada.

De ahí que la arquitectura mantenga separados lo que se observa, lo que el modelo infiere, lo que se recupera, lo que se verifica y lo que se decide, porque encontrar un fragmento no es tener evidencia y una referencia puede existir, estar bien citada y no sostener aquello para lo que se usa. Cuando la evidencia falta, que un modelo sepa redactar una respuesta no la suple.

Queda por determinar hasta dónde llega esa separación cuando se recorre el proceso completo que plantea la pregunta; mientras tanto, las conclusiones no pueden ir más allá de lo que los experimentos hayan mostrado.
