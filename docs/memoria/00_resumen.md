# Resumen

Los sistemas de diagnóstico asistidos por modelos de lenguaje pueden producir explicaciones
plausibles incluso cuando la evidencia disponible no basta para sostenerlas. En diagnóstico vehicular
esto importa, porque una explicación puede orientar una decisión de mantenimiento. Este trabajo estudia si un sistema inteligente híbrido puede
identificar patrones de fallo no representados en su conocimiento disponible, generar hipótesis
diagnósticas mediante el análisis contextual y longitudinal de datos OBD-II, contrastarlas con
evidencia y determinar si pueden incorporarse como conocimiento reutilizable.

Se desarrolla un agente que combina un modelo especializado de diagnóstico, atribución sobre la
telemetría, recuperación sobre documentación técnica y verificación determinista. La arquitectura
separa la generación de hipótesis de su validación: la evidencia recuperada debe ser aplicable al
vehículo, sostener las afirmaciones y superar un criterio explícito de suficiencia. Si no, el
sistema se abstiene en lugar de presentar la hipótesis como validada.

La evaluación utiliza datos OBD-II sintéticos generados bajo condiciones controladas,
parametrizados a partir de especificaciones documentadas del vehículo de referencia, un Mazda 3
BK de 2007. El diseño contempla cuatro condiciones de disponibilidad y pertinencia de la
evidencia documental —completa, parcial, ausente y con distractor— y mantiene constantes los
restantes elementos del caso en lo que la manipulación permite. Permite así estudiar por separado
la recuperación, el soporte de las afirmaciones y la decisión entre explicar y abstenerse.

Los experimentos registrados muestran que la disponibilidad de documentación no implica, por sí
sola, disponer de evidencia suficiente: bajo evidencia parcial el sistema recupera documentación
aplicable sin que ninguna afirmación quede sostenida. La identificación de patrones no
representados y la incorporación de conocimiento reutilizable forman parte del ciclo que define
la pregunta, y su evaluación permanece abierta: el diseño ejecutado no las instrumenta todavía.
Las condiciones cuya validación sigue abierta se conservan como tales. La telemetría sintética
permite reproducir los casos estudiados, pero limita la generalización a condiciones reales de
conducción, y la evaluación con datos de vehículos reales queda como validación externa
posterior.

**Palabras clave:** diagnóstico vehicular, OBD-II, recuperación aumentada por generación,
verificación de evidencia, abstención.

# Abstract

Language-model-assisted diagnostic systems can produce plausible explanations even when the
available evidence is not sufficient to support them. In vehicle diagnosis this matters, because
an explanation may inform a maintenance decision. This work studies whether a hybrid intelligent
system can identify fault patterns not represented in its available knowledge, generate
diagnostic hypotheses through contextual and longitudinal analysis of OBD-II data, test them
against evidence, and determine whether they can be incorporated as reusable knowledge.

An agent is developed that combines a specialised diagnostic model, attribution over the
telemetry, retrieval over technical documentation, and deterministic verification. The
architecture separates hypothesis generation from hypothesis validation: retrieved evidence must
be applicable to the vehicle, support the claims made, and meet an explicit sufficiency
criterion. Otherwise the system abstains rather than presenting the hypothesis as validated.

The evaluation uses synthetic OBD-II data generated under controlled conditions, parameterised
from documented specifications of the reference vehicle, a 2007 Mazda 3 BK. The design covers
four conditions of documentary evidence availability and relevance —full, partial, absent and
distractor—, with the remaining elements of the case held constant as far as the experimental
manipulation allows. This makes it possible to study retrieval, claim support and the decision
between explaining and abstaining separately.

The recorded experiments show that the availability of documentation does not, by itself, imply
having sufficient evidence: under partial evidence the system retrieves applicable documentation
without any claim being supported. Identifying unrepresented fault patterns and incorporating
reusable knowledge are part of the cycle defined by the research question, and their evaluation
remains open: the executed design does not yet instrument them. Conditions whose validation
remains open are reported as such. Synthetic telemetry allows the studied cases to be reproduced
but limits generalisation to real driving conditions, so evaluation with data from real vehicles
remains a subsequent external validation stage.

**Keywords:** vehicle diagnosis, OBD-II, retrieval-augmented generation, evidence verification,
abstention.
