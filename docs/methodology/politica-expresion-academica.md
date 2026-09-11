# Política de expresión académica del TFM

**Fecha:** 10 de septiembre de 2026 · **Decide:** Luis Daniel Díaz (autor) · **Estado:** vigente
y **vinculante**.

Regula **cómo se expresa** la memoria, no qué resultados se obtienen. No autoriza a suavizar un
hallazgo, a ocultar una limitación ni a modificar una cifra: la voz sirve a la claridad, no al
revés.

## Por qué existe

Una auditoría puede corregir con acierto un defecto metodológico y proponer, para arreglarlo,
una frase impecable en un informe técnico y mala en una memoria académica. Esta política evita
esa segunda deriva sin renunciar a la primera corrección.

## 1. Principio general

La redacción debe ser clara, académica, precisa, sobria, natural, humana, técnicamente rigurosa,
prudente con las afirmaciones y coherente entre capítulos.

No debe parecer documentación técnica, informe de auditoría, reporte de laboratorio, fichero de
instrucciones del repositorio, especificación funcional, texto promocional ni texto generado de
forma mecánica.

**La voz debe transmitir razonamiento, no decoración.**

## 2. Hechos antes que descripción del documento

| Evitar | Preferir |
|---|---|
| «En esta sección se explica la población utilizada» | «La población de referencia está formada por ventanas de telemetría OBD-II…» |
| «A continuación se muestran las métricas» | «La evaluación utiliza seis familias de métricas» |
| «Como se verá en el capítulo 5…» | el hecho directamente, si se entiende sin anticipar otro capítulo |

## 3. Las decisiones se expresan como decisiones metodológicas

Estructura: **problema → criterio → decisión → consecuencia metodológica.**

| Evitar | Preferir |
|---|---|
| «Se eligió Random Forest» | «Random Forest se adoptó como línea base atendiendo al tamaño del conjunto de datos y a la necesidad de una referencia reproducible frente al modelo temporal» |

## 4. Los resultados, con el alcance exacto de su evidencia

| Evitar | Preferir |
|---|---|
| «El sistema detecta correctamente los fallos» | «En los casos evaluados, el modelo identificó las condiciones representadas con el comportamiento descrito» |
| «El método funciona» | «Bajo las condiciones evaluadas, los resultados apoyan…» |

## 5. La incertidumbre, ni escondida ni dramatizada

**Usar:** «los resultados sugieren», «la evidencia disponible permite sostener», «no se dispone
todavía de evidencia suficiente para», «este resultado debe interpretarse dentro de», «la
evaluación realizada no permite afirmar», «permanece pendiente de validación».

**Evitar:** «parece que funciona», «probablemente está bien», «más o menos demuestra».

## 6. Las limitaciones: qué está limitado → por qué → qué consecuencia tiene

> «Los experimentos se ejecutaron sobre datos sintéticos. Por tanto, los resultados permiten
> evaluar el comportamiento del sistema bajo las condiciones representadas por el generador,
> pero no permiten establecer su validez externa sobre vehículos reales.»

No: «Una limitación importante es que no tenemos datos reales.»

## 7. Los resultados negativos conservan su valor

| Evitar | Preferir |
|---|---|
| «El experimento fracasó» | «El criterio de aceptación no se cumplió» |
| «La condición con distractor no funciona» | «La condición con distractor no permitió todavía demostrar una manipulación independiente respecto de la condición parcial» |

## 8. Hecho e interpretación, separados

Primero qué ocurrió: «Trece de las catorce abstenciones registradas se activaron por cobertura
insuficiente.» Después qué significa: «Esto indica que, en la configuración evaluada, el umbral
de cobertura concentra la mayor parte de las decisiones de abstención.»

## 9. Observación, inferencia, hipótesis, evidencia

| Término | Qué es |
|---|---|
| **Observación** | dato de la telemetría o descriptor derivado de ella |
| **Inferencia** | resultado producido por un modelo |
| **Hipótesis** | explicación diagnóstica provisional |
| **Evidencia** | información observacional o documental usada para contrastar una hipótesis |
| **Validación** | proceso que evalúa si la evidencia disponible sostiene la hipótesis |
| **Conocimiento reutilizable** | hipótesis incorporada tras superar el proceso de validación |

No se intercambian.

## 10. Causalidad, con prudencia

| Evitar | Preferir |
|---|---|
| «SHAP demuestra que la temperatura causa el fallo» | «La atribución mediante SHAP indica que la temperatura contribuye a la predicción del modelo» |

## 11. Sin antropomorfismo innecesario

No «el agente sabe», «entiende», «se da cuenta», «piensa». Sí «clasifica», «genera»,
«comprueba», «determina», «produce una abstención». «El agente decide» se admite cuando la
decisión corresponde formalmente al sistema y queda claro qué mecanismo la produce.

## 12. Tiempos verbales acordes al estado real

| Estado | Forma |
|---|---|
| Realizado | «se ejecutó», «se midió», «se obtuvo» |
| Implementado sin validar | «está implementado», «se encuentra disponible para evaluación» |
| Pendiente | «permanece pendiente», «no se ha ejecutado todavía» |
| Bajo diagnóstico | «su validez experimental permanece bajo evaluación» |

Nunca futuro para lo hecho ni pasado para lo pendiente.

## 13. Sin certeza excesiva

Evitar: «queda demostrado», «se demuestra definitivamente», «garantiza», «sin duda»,
«evidentemente», «claramente», «siempre», «nunca».

## 14. Sin lenguaje promocional

Evitar: innovador, revolucionario, potente, robusto, avanzado, disruptivo. Una novedad se
demuestra con el estado del conocimiento y el diseño experimental, no con adjetivos.

## 15. Muletillas, solo cuando la lógica las pida

«Cabe destacar que», «Es importante señalar que», «En este sentido», «Asimismo», «Por otro
lado», «En definitiva», «En conclusión», «En resumen».

## 16. Sin párrafos defensivos

| Evitar | Preferir |
|---|---|
| «Conviene aclarar que los datos no son reales» | «Los experimentos se ejecutaron sobre datos sintéticos» |
| «Debe quedar claro que el modelo de lenguaje no decide» | «La decisión de suficiencia se realiza mediante un verificador determinista externo al modelo de lenguaje» |

## 17-20. Sintaxis

Impersonal por defecto, con consistencia. Verbos directos en lugar de nominalizaciones: «se
evaluó», no «se procedió a la realización de la evaluación». Una oración no acumula método,
resultado, interpretación, limitación y referencia. Cada párrafo tiene una función reconocible.

## 21-24. Cifras

Toda comparación declara **qué se compara, con qué, bajo qué condición y con qué métrica**. Una
métrica sustituye a un adjetivo. Toda cifra relevante responde qué mide, sobre cuántos casos,
en qué partición, con qué procedencia, con qué unidad experimental y de qué versión del
experimento.

> **La precisión narrativa debe coincidir con la precisión experimental.** Si solo hay cinco
> ventanas independientes, no se redacta como si diecisiete ejecuciones fueran diecisiete
> observaciones.

## 25-27. Datos y validez

Los datos sintéticos se presentan con naturalidad —«la evaluación se realizó sobre datos OBD-II
sintéticos generados bajo condiciones controladas y reproducibles»— y no como consecuencia de
una carencia. La razón práctica de no disponer de datos reales no es la justificación científica.

**Nunca se presenta telemetría sintética como si procediera de un vehículo.** Y no se confunde
validez interna con externa.

## 28-30. Vocabulario

La novedad se acota al proceso de revisión: «entre los trabajos revisados no se identificó…».
No se usa «literatura» como término genérico: se dice trabajos revisados, estudios analizados,
investigaciones revisadas, evidencia encontrada. Se prefiere «la evidencia obtenida respalda» a
«esto prueba que», salvo cuando se hable de una prueba estadística o lógica.

## 31. Criterios previos y enmiendas posteriores

Si un criterio se fijó antes, se dice. Si se modificó después de ver resultados preliminares, se
dice también, y la enmienda se conserva junto al criterio original. **No se llama predefinido a
lo que no lo fue.**

## 32-34. Trazabilidad sin convertirse en documentación técnica

La memoria puede indicar que cada ejecución conserva versión de conjunto, corpus, modelo,
semilla y configuración. Los nombres de fichero aparecen cuando sirven a la trazabilidad, sin
dominar el discurso. Los identificadores internos se explican: no «E15 produjo M5», sino «la
fase E15, dedicada a la evaluación de suficiencia, genera los registros con que se calculan las
métricas de abstención». Toda abreviatura se introduce la primera vez.

## 35-36. Anglicismos

Se prefiere conjunto de datos, flujo, línea base. Se mantiene el término inglés cuando es
estándar técnico o identifica un artefacto: embedding, prompt, fine-tuning, SHAP, RAG, Random
Forest, GRU, pgvector.

## 37-38. Tablas y cierres

Una tabla se introduce y se señala la observación relevante, sin repetirla fila por fila. Un
capítulo cierra con la última idea necesaria, no con un resumen añadido por costumbre.

## 39-40. La voz reflexiva, y su límite

La memoria puede señalar tensiones metodológicas reales:

> «Una referencia puede existir y ser pertinente semánticamente sin sostener la afirmación para
> la que se utiliza. Esa diferencia es uno de los comportamientos que el experimento intenta
> aislar.»

Pero la voz **nunca** dramatiza, exagera hallazgos, esconde limitaciones, cambia resultados ni
sustituye un término científico por una metáfora.

## Plantillas

| Para | Fórmula |
|---|---|
| Presentar una decisión | «Se adoptó X porque Y, lo que permite Z» |
| Presentar un resultado | «Bajo la condición X, se observó Y» |
| Interpretar | «Este resultado indica que…» |
| Limitar | «El resultado se restringe a…» |
| Falta de evidencia | «La evidencia disponible no permite sostener…» |
| Trabajo pendiente | «La evaluación permanece pendiente de…» |
| Resultado negativo | «El criterio establecido no se cumplió» |
| Resultado parcial | «La evidencia respalda parcialmente…» |
| Evitar causalidad | «X contribuye a la predicción…» |
| Generalización | «Estos resultados no permiten inferir todavía…» |
| Datos sintéticos | «Los experimentos se realizaron sobre datos sintéticos generados bajo condiciones controladas y reproducibles» |
| Datos reales pendientes | «La evaluación sobre telemetría real se reserva como validación externa posterior» |

## Control de voz antes de aceptar un párrafo

1. ¿Dice algo científico o solo describe el documento?
2. ¿La afirmación es más fuerte que la evidencia?
3. ¿Puede escribirse con menos palabras sin perder precisión?
4. ¿Usa verbos directos?
5. ¿Hay lenguaje promocional?
6. ¿Hay lenguaje defensivo?
7. ¿Confunde hecho e interpretación?
8. ¿Confunde observación, inferencia, hipótesis o evidencia?
9. ¿El tiempo verbal coincide con el estado real?
10. ¿Alguna cifra aparece sin contexto?
11. ¿Hay términos del repositorio que deberían traducirse?
12. ¿La frase está escrita para un tribunal o para quien desarrolla?
13. ¿La limitación está expresada con precisión?
14. ¿Los datos sintéticos se identifican donde corresponde?
15. ¿La conclusión respeta el alcance de los datos?
16. ¿El texto sigue vinculado a la pregunta de investigación?
17. ¿Conserva una voz humana sin perder rigor?

Si alguna respuesta revela un problema: **reescribir, reevaluar, repetir.**

## Alcance sobre los skills

| Skill | Obligación |
|---|---|
| `tfm-writing-authenticity-auditor` | **vinculante**: evalúa contra esta política |
| `uax-tfm-ai-jury` | **vinculante**: sus preguntas y su veredicto la aplican |
| Los demás auditores | **consulta obligatoria** antes de proponer una redacción |

Ningún auditor puede recomendar una formulación que corrija un defecto metodológico y viole esta
política. Cuando ocurra, la corrección se aplica y su redacción se reescribe conforme a estas
reglas: **el hallazgo manda sobre la forma, y la forma se ajusta después.**

Esta política **no** puede usarse para rebajar un hallazgo, suavizar una limitación ni retirar
una cifra incómoda.

---

# Patrón editorial del TFM · la voz de referencia

Decisión del autor, 11 de septiembre de 2026. El fragmento que abre la justificación del
capítulo 1 —«Un vehículo moderno deja un rastro continuo de su funcionamiento»— **fija la voz de
toda la memoria**. No se imita su tema ni sus frases: se reproducen sus características.

## Qué hace ese fragmento

Abre con un hecho concreto, no con un marco. Encuentra dentro de ese hecho el problema que
contiene: las señales, leídas por separado, dicen poco. Y solo entonces explica por qué importa.
El razonamiento avanza; no se anuncia.

El contraste epistémico aterriza como frase corta, en el punto donde el razonamiento ya lo
sostiene: *«Una etiqueta puede ser correcta y, aun así, decir muy poco sobre aquello que la
produjo.»* No es un eslogan colocado al final del párrafo. Es la consecuencia de lo anterior.

## Perfil medible

| | referencia | umbral aceptable |
|---|---|---|
| longitud media de oración | 14,6 palabras | 14-22 |
| variación σ/µ | 0,63 | **> 0,40** |
| nominalizaciones | 3,4 % | < 7 % en prosa, < 9 % en método |
| oraciones de 12 palabras o menos | 56 % | > 25 % |
| aperturas de párrafo con conector | 0 | **0** |

La variación importa más que la media: un apartado con todas las oraciones de 25 palabras se lee
como una plantilla aunque cada una sea correcta.

## Reglas

Escribir como quien hizo el trabajo, no como quien lo resume. Hecho concreto antes que
formulación abstracta. Verbo antes que sustantivo derivado: *se comprobaron* y no *se llevó a
cabo la verificación*; *la búsqueda se hizo en cuatro iteraciones* y no *se procedió a la
realización de cuatro iteraciones*. Cuando algo puede decirse directamente, se dice.

No todos los párrafos con la misma forma. No cerrar cada uno resumiendo lo dicho. Dejar que una
idea lleve a la siguiente sin anunciarlo.

Los contrastes —detectar no es explicar, recuperar no es demostrar, una referencia no es
evidencia, formular una hipótesis no es validarla— aparecen cuando el razonamiento los alcanza.
Repetidos mecánicamente se convierten en muletilla y pierden el filo.

La tensión epistemológica es de fondo, no de superficie: qué observó el sistema, qué infiere, qué
sostiene la evidencia, qué queda sin saber. Sin metáforas, sin dramatismo, sin ensayo.

## Prohibiciones

`A partir de` como conector de párrafo (su uso preposicional —«a partir de datos OBD-II»— es
correcto y pertenece a la pregunta de investigación) · `En este contexto` · `En este sentido` ·
`Cabe destacar` · `Conviene precisar` · `Resulta fundamental` · `Por este motivo` · `Por esta
razón` · `Estos resultados ponen de manifiesto` · `Esta correspondencia permite` · `Estos frentes
se examinan` · `El proceso dio lugar a` · `Por otro lado` · `Es importante señalar`.

También: enumeraciones perfectamente simétricas, cadenas de sustantivos abstractos, exceso de
pasiva, frases que anuncian lo que el párrafo va a hacer, conclusiones artificiales de cierre,
lenguaje promocional y lenguaje defensivo.

## Límite

**La naturalidad nunca tiene prioridad sobre la precisión.** No se modifican cifras, resultados,
referencias, limitaciones, decisiones metodológicas, estado de los experimentos ni la pregunta de
investigación. No se inventan hechos para que la narración fluya, no se ocultan resultados
negativos, no se convierte una limitación en fortaleza, y no se presenta como validado lo que
solo está diseñado, implementado o medido.

Ninguna reescritura reduce la investigación a RAG, a un modelo de lenguaje, a clasificación, a
explicabilidad o a abstención. Son mecanismos del sistema, no sustitutos de la pregunta.
