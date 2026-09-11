# Capítulo 2: Objetivos del TFM

Los objetivos del TFM concretan la pregunta de investigación en aspectos que pueden abordarse y
evaluarse a lo largo del trabajo. Cada objetivo específico se vincula con las fases necesarias
para su desarrollo y, cuando su naturaleza lo requiere, con las métricas empleadas para evaluar
los resultados obtenidos. Esta correspondencia mantiene una relación explícita entre la pregunta
de investigación, las decisiones metodológicas y la evidencia obtenida.

No todos los objetivos requieren una medida cuantitativa. En aquellos relacionados con la
revisión del conocimiento previo y la construcción del entorno experimental, su cumplimiento se
verifica mediante los artefactos y evidencias generados durante su desarrollo. Los objetivos
asociados al comportamiento del sistema, en cambio, se someten a evaluación experimental mediante
las métricas y los criterios definidos para cada caso.

## Objetivo general

Evaluar experimentalmente la capacidad de un sistema inteligente híbrido para identificar
patrones de fallo no representados en su conocimiento disponible, generar hipótesis diagnósticas
mediante el análisis contextual y longitudinal de datos OBD-II, contrastarlas con evidencia
suficiente y pertinente, abstenerse cuando dicha evidencia no permita validarlas e incorporar
como conocimiento reutilizable únicamente aquellas hipótesis que superen el proceso de validación
establecido.

## Objetivos específicos

Los objetivos específicos recorren las etapas necesarias para responder a la pregunta de
investigación: delimitan el problema a partir del conocimiento previo, establecen el entorno
experimental, desarrollan los mecanismos de identificación y caracterización de patrones,
implementan el proceso de generación y validación de hipótesis y, finalmente, evalúan el
comportamiento del sistema bajo las condiciones experimentales definidas.

**OE1.** Revisar críticamente el estado del conocimiento sobre diagnóstico vehicular mediante
datos OBD-II, explicabilidad de modelos, recuperación de información sobre documentación técnica
y mecanismos de abstención ante evidencia insuficiente, con el propósito de delimitar el vacío
abordado por la pregunta de investigación y fundamentar las decisiones metodológicas y de diseño
del sistema frente a los trabajos previos.

**OE2.** Construir un entorno experimental reproducible que integre telemetría OBD-II, un corpus
documental asociado al vehículo de referencia y condiciones controladas de disponibilidad y
pertinencia de la información documental, preservando la separación temporal de los datos y la
trazabilidad necesaria para reproducir los experimentos.

**OE3.** Desarrollar y evaluar mecanismos para identificar y caracterizar patrones de fallo en
ventanas de telemetría OBD-II y determinar cuándo estos no se encuentran representados en el
conocimiento disponible para el proceso diagnóstico, utilizando el comportamiento contextual y
longitudinal de las señales, estimaciones de confianza y técnicas de atribución como soporte
para la formulación posterior de hipótesis diagnósticas.

**OE4.** Implementar un agente capaz de formular y contrastar hipótesis diagnósticas mediante la
combinación de evidencia observacional procedente de la telemetría y evidencia documental
recuperada de fuentes técnicas, verificando la aplicabilidad y el soporte de la información
utilizada y aplicando un criterio explícito de suficiencia que permita decidir entre validar una
hipótesis o abstenerse cuando la evidencia disponible no resulte suficiente.

La generación de una hipótesis y su validación se consideran procesos diferenciados. La
capacidad del modelo de lenguaje para producir una explicación diagnóstica no determina por sí
misma que exista evidencia suficiente para sostenerla.

**OE5.** Evaluar experimentalmente el ciclo de diagnóstico y validación bajo condiciones
controladas de evidencia documental completa, parcial, ausente y con distractores, analizando la
identificación y caracterización del patrón, la formulación de la hipótesis, la recuperación y
trazabilidad de la evidencia y la decisión entre validarla o abstenerse; así como comprobar que
las hipótesis que superen el proceso de validación puedan incorporarse y recuperarse
posteriormente como conocimiento reutilizable sin admitir aquellas que no satisfagan los
criterios establecidos.

## Correspondencia entre los objetivos y su evaluación

**Tabla 2.1. Correspondencia entre los objetivos específicos y su estrategia de evaluación.**

| Objetivo | Propósito | Estrategia de evaluación |
|---|---|---|
| OE1 | Delimitar el estado del conocimiento y el vacío investigado | Revisión estructurada y verificación de fuentes primarias |
| OE2 | Establecer el entorno experimental | Verificación de reproducibilidad, procedencia de los datos y coherencia entre telemetría y corpus |
| OE3 | Identificar y caracterizar patrones de fallo, y determinar cuándo no están representados | Evaluación experimental sobre telemetría OBD-II y análisis de atribuciones y confianza |
| OE4 | Formular y validar hipótesis mediante evidencia | Evaluación de recuperación, aplicabilidad, soporte, suficiencia y abstención |
| OE5 | Evaluar el ciclo integrado y la reutilización del conocimiento validado | Comparación entre condiciones experimentales y comprobación de incorporación y recuperación posterior |

*Fuente: elaboración propia.*

El capítulo 4 desarrolla esta correspondencia hasta las fases experimentales, las métricas y los
criterios de evaluación de cada objetivo, y declara el estado de ejecución de cada una.
