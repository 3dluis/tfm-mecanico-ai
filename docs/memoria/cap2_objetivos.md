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

**OE3.** Desarrollar y evaluar mecanismos para identificar y caracterizar patrones de
comportamiento en ventanas de telemetría OBD-II, utilizando modelos de referencia, estimaciones
de confianza y técnicas de atribución que permitan localizar las variables y los intervalos
temporales relevantes para la formulación posterior de hipótesis diagnósticas.

**OE4.** Implementar un agente capaz de formular y contrastar hipótesis diagnósticas mediante la
combinación de evidencia observacional procedente de la telemetría y evidencia documental
recuperada de fuentes técnicas, verificando la aplicabilidad y el soporte de la información
utilizada y aplicando un criterio explícito de suficiencia que permita decidir entre validar una
hipótesis o abstenerse cuando la evidencia disponible no resulte suficiente.

La generación de la hipótesis y su validación se mantienen como procesos diferenciados, de manera
que la capacidad del modelo de lenguaje para formular una explicación no determine por sí misma
que exista evidencia suficiente para sostenerla.

**OE5.** Evaluar experimentalmente el comportamiento del sistema bajo condiciones controladas de
evidencia documental completa, parcial, ausente y con distractores, analizando su capacidad
diagnóstica, la recuperación y trazabilidad de la evidencia, la validación de las hipótesis y la
decisión entre explicar y abstenerse, así como la contribución de sus principales componentes.

## Correspondencia entre objetivos, fases y métricas

La Tabla 2.1 recoge esa correspondencia con el estado de cada objetivo.

**Tabla 2.1. Trazabilidad entre objetivos específicos, fases experimentales y métricas.**

| Objetivo | Fases | Métricas | Estado a 10 de septiembre de 2026 |
|---|---|---|---|
| OE1 | revisión documental | — | en curso; flujo PRISMA formal pendiente de acceso institucional |
| OE2 | E1, E2, E3, E4, E5, E10 | — | cuatro cerradas; **E10 con la infraestructura cerrada y el corpus vacío**; E3 pendiente como validación externa |
| OE3 | E5, E6, E7, E8, E9 | M1 | cuatro cerradas sobre datos sintéticos; **E8 pendiente** |
| OE4 | E11, E12, E13, E15; **E14 y E16 pendientes** | M2, M3, M4, M5 | M2, M3 y M5 calculadas **sobre datos sintéticos**; **M4 implementada, sin calcular sus magnitudes agregadas**; resultados no definitivos |
| OE5 | E17, E18, E19, E20 | M1–M6 | **E17 ejecutada sin informe de fase**; E18 pendiente; E19 y E20 pendientes del conjunto de evaluación final |

*Fuente: elaboración propia.*

Ninguna de las veinte fases queda sin objetivo. La correspondencia inversa, en cambio, no es
completa: dos de los términos del objetivo general no tienen objetivo específico que los
desarrolle ni fase que los instrumente. El primero es la identificación de patrones **no
representados** en el conocimiento disponible, que OE3 no aborda porque el modelo empleado
clasifica sobre clases conocidas. El segundo es la incorporación de las hipótesis validadas como
**conocimiento reutilizable**, que ninguna fase del plan contempla. El capítulo 4 desarrolla la
primera de las dos limitaciones y el capítulo 6 recoge ambas.

Los cinco se persiguen sobre un único vehículo de referencia, el Mazda 3 BK de 2007 con motor
Z6, elección justificada en el capítulo 4 que acota cuanto pueda afirmarse. El alcance ejecutado
es más estrecho que el aprobado en julio, y esa distancia está planteada a la dirección (P-03).

Quedan fuera el despliegue sobre placa embarcada, la aplicación móvil y la plataforma en la
nube que contemplaba la propuesta de julio de 2026: no aportan evidencia a la pregunta y su
coste habría desplazado el esfuerzo del experimento central. Pasan a la prospectiva del
capítulo 6.
