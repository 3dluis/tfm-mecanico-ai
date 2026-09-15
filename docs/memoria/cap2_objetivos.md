# Capítulo 2: Objetivos del TFM

Los objetivos del TFM concretan la pregunta de investigación en aspectos que pueden abordarse y evaluarse a lo largo del trabajo. Cada objetivo específico se vincula con las fases necesarias para su desarrollo y, cuando su naturaleza lo requiere, con las métricas empleadas para evaluar los resultados obtenidos. Esta correspondencia mantiene una relación explícita entre la pregunta de investigación, las decisiones metodológicas y la evidencia obtenida.

No todos los objetivos requieren una medida cuantitativa. En aquellos relacionados con la revisión del conocimiento previo y la construcción del entorno experimental, su cumplimiento se verifica mediante los artefactos y evidencias generados durante su desarrollo. Los objetivos asociados al comportamiento del sistema, en cambio, se someten a evaluación experimental mediante las métricas y los criterios definidos para cada caso.

## Objetivo general

Evaluar experimentalmente un agente de recuperación aumentada por evidencia en su capacidad de explicar diagnósticos vehiculares obtenidos a partir de datos OBD-II, manteniendo una correspondencia verificable entre cada afirmación y la evidencia que la sostiene, y de abstenerse cuando la evidencia disponible resulta insuficiente o no pertinente.

## Objetivos específicos

Los objetivos específicos recorren las etapas necesarias para responder a la pregunta de investigación: delimitan el problema a partir del conocimiento previo, establecen el entorno experimental, evalúan el modelo de diagnóstico y la confianza que aporta, implementan la recuperación y la verificación de la evidencia y, finalmente, evalúan el comportamiento integrado del agente bajo las condiciones experimentales definidas.

**OE1.** Revisar críticamente el estado del conocimiento sobre diagnóstico vehicular mediante datos OBD-II, explicabilidad de modelos, recuperación de información sobre documentación técnica y mecanismos de abstención ante evidencia insuficiente, con el propósito de delimitar el vacío abordado por la pregunta de investigación y fundamentar las decisiones metodológicas y de diseño del sistema frente a los trabajos previos.

**OE2.** Construir un entorno experimental reproducible que integre telemetría OBD-II, un corpus documental asociado al vehículo de referencia y condiciones controladas de disponibilidad y pertinencia de la información documental, preservando la separación temporal de los datos y la trazabilidad necesaria para reproducir los experimentos.

**OE3.** Evaluar la capacidad del modelo especializado para obtener diagnósticos a partir de ventanas de telemetría OBD-II y caracterizar, mediante calibración y técnicas de atribución, la confianza de cada decisión y las señales e intervalos temporales que contribuyen a ella, de modo que sirvan como evidencia observacional para las etapas posteriores.

**OE4.** Implementar un agente capaz de formular y contrastar hipótesis diagnósticas mediante la combinación de evidencia observacional procedente de la telemetría y evidencia documental recuperada de fuentes técnicas, verificando la aplicabilidad y el soporte de la información utilizada y aplicando un criterio explícito de suficiencia que permita decidir entre validar una hipótesis o abstenerse cuando la evidencia disponible no resulte suficiente.

La generación de una hipótesis y su validación se consideran procesos diferenciados. La capacidad del modelo de lenguaje para producir una explicación diagnóstica no determina por sí misma que exista evidencia suficiente para sostenerla.

**OE5.** Evaluar experimentalmente el comportamiento integrado del agente bajo condiciones controladas de evidencia documental completa, parcial, ausente y con distractores, analizando la recuperación y trazabilidad de la evidencia, la validación de las hipótesis y la decisión entre explicar y abstenerse, y distinguiendo entre explicaciones sostenidas por evidencia suficiente, explicaciones sin soporte suficiente y abstenciones innecesarias.

## Correspondencia entre los objetivos y su evaluación

**Tabla 2.1. Correspondencia entre los objetivos específicos y su estrategia de evaluación.**

| Objetivo | Propósito | Estrategia de evaluación |
|---|---|---|
| OE1 | Delimitar el estado del conocimiento y el vacío investigado | Revisión estructurada y verificación de fuentes primarias |
| OE2 | Establecer el entorno experimental | Verificación de reproducibilidad, procedencia de los datos y coherencia entre telemetría y corpus |
| OE3 | Evaluar el diagnóstico obtenido de la telemetría y caracterizar su confianza y sus señales | Evaluación experimental sobre telemetría OBD-II frente a una referencia mínima, calibración de la confianza y análisis de atribuciones |
| OE4 | Formular y validar hipótesis mediante evidencia | Evaluación de recuperación, aplicabilidad, soporte, suficiencia y abstención |
| OE5 | Evaluar el comportamiento integrado bajo las cuatro condiciones de evidencia | Comparación entre condiciones experimentales sobre el mismo caso, con los dos tipos de error de la decisión contados por separado |

*Fuente: elaboración propia.*

El capítulo 4 desarrolla esta correspondencia hasta las fases experimentales, las métricas y los criterios de evaluación de cada objetivo, y declara el estado de ejecución de cada una.
