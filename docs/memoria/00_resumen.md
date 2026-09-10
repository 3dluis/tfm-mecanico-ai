# Resumen

Los sistemas de diagnóstico asistidos por modelos de lenguaje pueden producir explicaciones
plausibles incluso cuando la evidencia disponible no basta para sostenerlas. En el diagnóstico
vehicular esto importa, porque una explicación puede orientar una decisión de mantenimiento. Este trabajo estudia si un sistema inteligente híbrido
puede identificar patrones de fallo no representados en su conocimiento disponible, generar
hipótesis diagnósticas mediante el análisis contextual y longitudinal de datos OBD-II y
contrastarlas con evidencia antes de incorporarlas como conocimiento reutilizable.

Se desarrolla un agente que combina un modelo especializado de diagnóstico, atribución sobre
la telemetría, recuperación sobre documentación técnica y un proceso determinista de
verificación. La arquitectura separa la generación de hipótesis de su validación: la evidencia
recuperada debe ser aplicable al vehículo, sostener las afirmaciones formuladas y superar un
criterio explícito de suficiencia. Si no se cumplen, el
sistema se abstiene en lugar de presentar la hipótesis como validada. La evaluación emplea datos
OBD-II sintéticos generados bajo condiciones controladas y parametrizados a partir de
especificaciones documentadas del vehículo de referencia, un Mazda 3 BK de 2007, bajo cuatro
condiciones de disponibilidad y pertinencia de la evidencia documental
—completa, parcial, ausente y con distractor—, con los restantes elementos del caso
controlados en lo que la manipulación permite.

El diseño permite estudiar por separado la recuperación, el soporte de las afirmaciones y la
decisión entre explicar y abstenerse, e identifica situaciones en las que tener documentación no
es tener evidencia suficiente. Lo ejecutado se concentra en ese
contraste y en esa decisión; la identificación de patrones no representados y la incorporación
de conocimiento reutilizable quedan como continuación, y las condiciones cuya validación
experimental permanece abierta se conservan como tales. La telemetría sintética permite
reproducir los casos estudiados, pero limita la generalización a condiciones reales de
conducción, por lo que la evaluación con datos reales queda como validación externa posterior.

**Palabras clave:** diagnóstico vehicular, OBD-II, recuperación aumentada por generación,
verificación de evidencia, abstención.

# Abstract

Language-model-assisted diagnostic systems can produce plausible explanations even when the
available evidence is not sufficient to support them. In vehicle diagnosis this limitation matters, because an
explanation may inform a maintenance decision. This work
studies whether a hybrid intelligent system can identify fault patterns not represented in its
available knowledge, generate diagnostic hypotheses through contextual and longitudinal analysis
of OBD-II data, and test them against evidence before incorporating them as reusable knowledge.

An agent is developed that combines a specialised diagnostic model, attribution mechanisms over
the telemetry, information retrieval over technical documentation, and a deterministic
verification process. The architecture separates hypothesis generation from hypothesis
validation: retrieved evidence must be applicable to the vehicle, support the claims made, and
meet an explicit sufficiency criterion. When these conditions are not met, the system abstains
rather than presenting the hypothesis as validated. The evaluation uses synthetic OBD-II data
generated under controlled conditions and parameterised from documented specifications, with a
2007 Mazda 3 BK as reference vehicle, under four conditions of documentary evidence availability
and relevance —full, partial, absent and distractor—, holding the remaining elements of the case
constant wherever the experimental manipulation allows it.

The design makes it possible to study retrieval, claim support and the decision between
explaining and abstaining separately, and identifies situations in which having retrieved
documentation is not equivalent to having sufficient evidence. The executed work concentrates on
testing the hypothesis against documentary evidence and on that decision; identifying
unrepresented fault patterns and incorporating reusable knowledge are stated as future work.
Conditions whose experimental validation remains open are reported as such. Synthetic telemetry
allows the studied cases to be reproduced, but limits generalisation to real driving conditions,
so evaluation with data from real vehicles is proposed as subsequent external validation.

**Keywords:** vehicle diagnosis, OBD-II, retrieval-augmented generation, evidence verification,
abstention.
