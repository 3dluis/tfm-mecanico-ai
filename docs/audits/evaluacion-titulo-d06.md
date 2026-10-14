# Evaluación del título registrado frente al trabajo ejecutado

**Fecha:** 13 de octubre de 2026 · **Qué es:** si el título registrado describe lo que el trabajo
hace · **Qué NO es:** un cambio de título. El título **no se modifica**: la sesión informativa exige
que el definitivo se consensúe con el director, y no consta que esa conversación se haya tenido ·
**Por qué existe:** es la decisión abierta `D-06`

## 1. El título registrado

> **«Sistema inteligente para el diagnóstico y mantenimiento predictivo de vehículos»**

Procede de la propuesta temática aprobada el 14 de julio de 2026. La sesión informativa dice de él:
«El título propuesto tiene carácter **orientativo** y puede ser modificado. El título definitivo
deberá comunicarse tras una primera reunión con el director para consensuarlo».

## 2. Las siete capacidades, una a una

El título contiene o sugiere siete cosas. Esto es lo que el trabajo hace con cada una.

| Capacidad | ¿Está en el trabajo? | Evidencia | Estado |
|---|---|---|---|
| **Diagnóstico de fallos** | **sí, medido** | bosque aleatorio sobre 139 descriptores; exactitud 0,878 frente a 0,286 de la clase mayoritaria, con la confianza calibrada | **ejecutado y publicado** |
| **Identificación de patrones no representados** | **no** | el catálogo de fallos es **cerrado**: cinco condiciones más la normal. El comportamiento ante una avería ajena al catálogo no se ha examinado, y está declarado como limitación y como línea futura | **fuera del alcance** |
| **Generación de hipótesis** | **sí**, con una distinción | el verificador construye tres afirmaciones por caso a partir de la atribución; el modelo de lenguaje **redacta** pero no decide. El capítulo 2 declara que generar una hipótesis y validarla son procesos diferenciados | **ejecutado** |
| **Validación mediante evidencia** | **sí, y es el núcleo** | criterio de suficiencia con cuatro comprobaciones deterministas; 17 casos anotados, cuatro ablaciones y la evaluación final sobre el conjunto de prueba | **ejecutado y publicado** |
| **Abstención** | **sí, y es el núcleo** | 0 de 14 de falsa confianza y 2 de 8 de abstención innecesaria en la evaluación final, con sus intervalos | **ejecutado y publicado** |
| **Incorporación de conocimiento** | **parcial** | se recupera y se verifica documentación técnica del vehículo, pero el sistema **no incorpora** conocimiento nuevo: no aprende de los casos resueltos. Conservar explicaciones validadas para reutilizarlas está en la prospectiva | **parcialmente, como recuperación** |
| **Mantenimiento predictivo** | **no** | el trabajo diagnostica una condición **presente** en una ventana de telemetría. No predice fallos futuros, no estima vida útil ni programa intervenciones. Ninguna métrica del trabajo es de predicción temporal | **no ejecutado, y no estaba en el alcance acotado** |

## 3. El desajuste, en una frase

De las siete capacidades que el título contiene o sugiere, **cuatro se han ejecutado y medido**, una
lo está parcialmente y **dos no forman parte del trabajo**. Las dos que faltan son precisamente las
que el título nombra de forma más llamativa: «**mantenimiento predictivo**» y, por implicación de
«sistema inteligente», la identificación de patrones que el catálogo no representa.

A la vez, el título **no nombra** lo que el trabajo sí hace y es su contribución: la trazabilidad
entre cada afirmación y la evidencia que la sostiene, y la abstención cuando esa evidencia no basta.

## 4. Coherencia con la pregunta, los objetivos y los resultados

| Elemento | Qué dice | ¿Coincide con el título? |
|---|---|---|
| **Pregunta de investigación** | «¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II, rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia disponible no es suficiente…?» | **no del todo**: la pregunta es sobre explicación, trazabilidad y abstención; el título, sobre diagnóstico y predicción |
| **Objetivo general** | «Evaluar experimentalmente un agente de recuperación aumentada por evidencia en su capacidad de explicar diagnósticos vehiculares […] manteniendo una correspondencia verificable entre cada afirmación y la evidencia que la sostiene, y de abstenerse cuando la evidencia disponible resulta insuficiente» | **no**: no menciona predicción, y sí los dos ejes que el título omite |
| **Los cinco objetivos específicos** | revisión, entorno, diagnóstico y confianza, recuperación y verificación, comportamiento integrado | **ninguno** es de mantenimiento predictivo |
| **Los resultados de los capítulos 5 y 6** | PI.1 a PI.4: diagnóstico, trazabilidad, suficiencia y distractores | **ninguno** mide predicción |

La pregunta, los cinco objetivos y los resultados son coherentes **entre sí**. El título es el único
elemento que se desmarca, y se desmarca por exceso: promete dos cosas que el trabajo no entrega.

## 5. Por qué el desajuste no es un defecto del trabajo

La propuesta aprobada en julio tenía **trece objetivos específicos**, incluidos una placa
embarcada, una aplicación móvil, una plataforma en la nube y el mantenimiento predictivo. El alcance
se acotó a cinco objetivos, el recorte está documentado internamente y las piezas retiradas figuran
como líneas futuras. Lo que falta no es trabajo: es la comunicación formal del recorte, que la
sesión informativa exige y de la que no hay constancia. Está registrado como limitación `L-13`.

## 6. Qué se propone, y qué no

**No se cambia el título.** Lo que se propone es llevarlo a la consulta con el director, con dos
opciones concretas en lugar de una duda abierta:

| Opción | Título | A favor | En contra |
|---|---|---|---|
| **A · mantenerlo** | «Sistema inteligente para el diagnóstico y mantenimiento predictivo de vehículos» | es el registrado y el que consta en la propuesta aprobada; cambiarlo a estas alturas puede tener coste administrativo | el tribunal leerá «mantenimiento predictivo» en la portada y no lo encontrará en ningún capítulo. Es la primera pregunta que haría cualquier miembro del tribunal |
| **B · ajustarlo al alcance** | **«Diagnóstico vehicular explicable a partir de datos OBD-II: trazabilidad de la evidencia y abstención ante evidencia insuficiente»** | describe lo que el trabajo hace y nombra su contribución; la sesión informativa **autoriza expresamente** el cambio | exige comunicarlo y consensuarlo, y rehacer la portada |

La recomendación, si se pide: **la opción B**, por una razón que no es de estilo. Un título que
promete mantenimiento predictivo obliga al autor a explicar en la defensa por qué no lo hay, y esa
explicación consume tiempo del tribunal en algo que no es el trabajo. Un título ajustado al alcance
convierte esa pregunta en innecesaria.

Decide el autor con el director. El borrador de la consulta está en
[`consulta-tutor-extension-y-titulo.md`](consulta-tutor-extension-y-titulo.md).
