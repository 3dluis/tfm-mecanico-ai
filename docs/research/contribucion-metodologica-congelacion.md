# ¿Es una aportación metodológica la congelación verificable, o es ingeniería bien hecha?

**Fecha:** 13 de octubre de 2026 · **Qué es este documento:** una investigación encargada por el
autor tras una observación del tribunal simulado, **no** una reclamación de originalidad ·
**Qué no hace:** no modifica la pregunta de investigación ni los objetivos, y no presenta nada como
contribución principal · **Conclusión, por adelantado:** defendible como **contribución
metodológica complementaria y acotada**, con una evidencia que sostiene la **detección** y no la
prevención, y sin novedad en ninguno de sus mecanismos por separado

---

## 1. Descripción del procedimiento

Lo que este trabajo hace, descrito sin adornos y en el orden en que ocurre.

### 1.1 Las seis piezas

| Pieza | Qué es, concretamente | Dónde está |
|---|---|---|
| **1 · Pre-registro escrito antes de medir** | catorce documentos de política, pre-registro, protocolo o declaración, cada uno con fecha y commit anteriores a la ejecución que gobierna. Declaran el criterio, los umbrales, qué resultado apoyaría la hipótesis y **qué resultado la cuestionaría** | `docs/methodology/` |
| **2 · Cierre del conjunto de prueba en el código** | pedir la partición de prueba exige `allow_test=True` **y** una razón por escrito, que se imprime en la salida de la ejecución. No es una convención: el programa falla sin ella | `src/mecanico_ia_exp/data/dataset.py:77` |
| **3 · Manifiesto del estado controlado** | antes de la evaluación final se congelan las huellas SHA-256 de los ficheros que definen el experimento —conjunto, configuración, umbrales, anotación— y se verifican al arrancar | `configs/manifest_e19.json` |
| **4 · Censo de artefactos publicados** | 151 huellas SHA-256 de tablas, figuras y registros ya publicados. Una ejecución nueva que modifique uno de ellos hace fallar el gate de calidad | `configs/artefactos_historicos.json`, `src/mecanico_ia_exp/experiments/destinos.py` |
| **5 · Afirmación falsable de invariancia del instrumento** | que las reglas no se movieron entre la primera exposición y la medición se comprueba con un comando: `git diff --stat <commit_apertura>..<commit_medicion> -- src/ configs/ tests/` tiene que estar **vacío** | `docs/methodology/registro-aperturas-test.md` |
| **6 · Registro graduado de exposiciones** | cada apertura del conjunto reservado se clasifica en cinco niveles —apertura técnica · lectura de identificadores · exposición de etiquetas · exposición de predicciones · utilización de resultados— y se publica, incluida una que fue accidental | ídem |

### 1.2 Lo que hace que las seis sean un procedimiento y no seis buenas costumbres

Dos propiedades las unen, y son las que merecen examen:

**Primera: cada afirmación de congelación es comprobable por un tercero con un comando.** No se
pide creer que el umbral no se tocó: se señala un diff vacío. No se pide creer que la tabla
publicada es la que produjo la ejecución: se señala una huella. No se pide creer que la selección
del conjunto no se eligió por su resultado: se reejecuta la regla y se compara con la huella
congelada (`tests/test_evaluacion_independiente.py`).

**Segunda: el registro de lo que salió mal es parte del procedimiento, no un apéndice.** Cinco
incidencias publicadas con identificador propio, una de ellas una apertura accidental del conjunto
reservado que nadie habría sabido si no se declarara.

---

## 2. El problema que intenta resolver

### 2.1 El problema general, que no es nuevo

Un analista que ve el resultado de una medición y después ajusta el criterio produce una cifra que
no mide lo que dice medir. Es el problema del análisis adaptativo, y está bien planteado desde hace
una década: la validez se degrada con cada consulta al conjunto reservado, aunque el analista sea
honesto y no lo note (Dwork et al., 2015; Blum y Hardt, 2015).

### 2.2 El problema específico de este trabajo, que es más estrecho y más incómodo

Tres circunstancias concretas, que no son las de un laboratorio con varios investigadores:

1. **Un solo operador.** Quien diseña, mide, interpreta y escribe es la misma persona. No hay
   separación de funciones que obligue a nada: nadie sostiene el conjunto de prueba por el otro
   lado. La única barrera posible es procedimental y autoimpuesta.
2. **Trabajo asistido por agentes.** Parte de la implementación y del análisis se produce en
   sesiones con un asistente de programación. Eso multiplica la velocidad y multiplica la
   oportunidad de que una decisión se tome sin registro: un agente puede abrir una partición, mover
   un umbral o regenerar un artefacto en una línea, sin que nadie lo decida explícitamente. **Esa
   apertura accidental del conjunto de prueba, la quinta, ocurrió exactamente así.**
3. **Recursos para una sola pasada.** El conjunto de prueba se puede abrir pocas veces y el
   presupuesto de cómputo no permite rehacer una evaluación final. No hay margen para el
   «volvemos a medir con el diseño corregido».

**El problema, entonces:** cómo sostener ante un tercero que las decisiones de un experimento no se
movieron después de ver los resultados, **cuando no hay separación de funciones que lo garantice y
cuando parte de las acciones las ejecuta un agente**. Y, cuando se mueven o se rompe algo, cómo
dejarlo registrado de forma que el tercero pueda medir el daño en lugar de confiar.

---

## 3. Trabajos relacionados

Nueve áreas, revisadas con la pregunta «¿qué de esto ya está resuelto, y mejor?».

### 3.1 Pre-registro experimental

El pre-registro separa la predicción de la postdicción: declarar la hipótesis y el análisis antes de
ver los datos convierte una exploración en una prueba (Nosek et al., 2018). En aprendizaje automático
la práctica es reciente y minoritaria: los talleres de pre-registro de NeurIPS 2020 y 2021 publicaron
protocolos revisados **sin resultados**, y sus actas documentan tanto el interés como la dificultad de
adaptar el modelo a un campo donde el incentivo es superar el estado del arte.

**Lo que ya está resuelto:** la idea, la justificación y el formato. **Lo que este trabajo no aporta:**
nada sobre el concepto de pre-registro.

### 3.2 Evaluación reproducible

El programa de reproducibilidad de NeurIPS 2019 —política de envío de código, desafío de
reproducibilidad y lista de control de reproducibilidad— es el referente sobre qué hay que declarar
para que otro pueda repetir una medición (Pineau et al., 2021).

**Lo que ya está resuelto:** qué declarar. **Diferencia de este trabajo:** la lista de control
declara; aquí se **comprueba en el gate de calidad**. No es una idea nueva, es una exigencia más
estricta de la misma idea.

### 3.3 Prevención de contaminación

La contaminación de conjuntos de evaluación por corpus de preentrenamiento es un problema central en
modelos de lenguaje, con propuestas concretas: cifrar los datos de prueba con clave pública,
exigir controles de exclusión de entrenamiento a los proveedores cerrados y publicar el contexto web
del dato (Jacovi et al., 2023).

**Diferencia de alcance, y conviene decirla con cuidado.** La contaminación que allí se discute
—datos de evaluación que acabaron en el preentrenamiento— no es la que este trabajo encontró. Aquí la
contaminación fue **del propio procedimiento**: los ejemplos de ajuste del redactor se generaron desde
la partición donde después se le midió. Es contaminación por diseño del experimento, no por el corpus
del modelo base. El problema es más doméstico y, por eso mismo, más probable en un trabajo de un solo
operador.

### 3.4 Protección de conjuntos de prueba

Aquí está el trabajo más fuerte y más próximo, y hay que reconocerlo con claridad.

- **El *holdout* reutilizable** (Dwork et al., 2015) da un mecanismo con **garantía demostrada**:
  usando ideas de privacidad diferencial, permite validar muchas hipótesis elegidas de forma
  adaptativa sobre el mismo conjunto reservado sin que la validez se degrade.
- **La escalera** (Blum y Hardt, 2015) resuelve el caso del marcador público de una competición, con
  garantías en un modelo completamente adaptativo y sin parámetros que ajustar.

**Lo que esto implica para la pretensión de este trabajo, y es lo más importante de esta sección.**
Esos dos mecanismos son **matemáticamente más fuertes** que cualquier cosa que aquí se haya hecho.
Acotan la pérdida de validez; el procedimiento de este TFM no acota nada: **registra**. Si la
pregunta es «¿cómo se protege un conjunto reservado?», la respuesta de la literatura es mejor que la
de este trabajo y hay que citarla así.

Lo que esos mecanismos **no** cubren es el caso de aquí: no hay un marcador, no hay una secuencia de
consultas numeradas, y lo que se consulta no es una métrica escalar sino una evaluación completa de
un sistema con varios componentes. La escalera protege un número; aquí hay que proteger un conjunto
de **decisiones de diseño**.

### 3.5 Trazabilidad de decisiones

Las fichas de conjunto de datos (Gebru et al., 2021) y las fichas de modelo (Mitchell et al., 2019)
estandarizaron **qué** documentar: procedencia, composición, usos previstos, condiciones de
evaluación, limitaciones.

**Diferencia:** las fichas documentan el artefacto terminado. Lo que este trabajo registra es la
**secuencia temporal de decisiones y exposiciones**, con el orden como información relevante: no solo
qué umbral se usó, sino que se fijó antes de la apertura, y que entre una y otra no cambió.

### 3.6 Verificación criptográfica de artefactos

`in-toto` (Torres-Arias et al., 2019) es el trabajo más cercano en **mecanismo**: metadatos firmados
criptográficamente que documentan cada paso de la cadena de suministro de software, de forma que el
usuario final puede verificar que el artefacto que recibe se produjo por los pasos declarados y por
los actores autorizados. Su eficacia se demostró sobre treinta compromisos reales.

**Prueba de aprendizaje** (Jia et al., 2021) va más lejos en el dominio de aprendizaje automático:
define cómo demostrar que un modelo se obtuvo por el entrenamiento que se declara.

**Diferencia, y es una diferencia de objeto, no de técnica.** `in-toto` verifica que un **artefacto**
se produjo por los pasos declarados. Lo que aquí se verifica es que una **decisión** —un umbral, una
regla de selección, un criterio— no se movió después de una exposición. La técnica es la misma y más
pobre: huellas SHA-256 sin firmar y un diff del control de versiones, donde `in-toto` tiene firmas,
cadena de confianza y un modelo de adversario. **Si el adversario es un tercero malicioso, el
procedimiento de este trabajo no sirve de nada.** Su modelo de adversario es otro: el propio autor,
sin mala fe, con prisa.

### 3.7 Evaluación de sistemas de IA

El giro de la evaluación hacia baterías holísticas y multimétrica —en lugar de una cifra por
conjunto— es el contexto en que esta discusión tiene sentido: cuando lo que se evalúa es un sistema
con varios componentes, «el conjunto de prueba» deja de ser un objeto simple y la protección tiene
que cubrir decisiones, no solo datos.

### 3.8 Gobernanza de experimentos

La gobernanza de sistemas de IA —marcos de gestión de riesgos, requisitos de documentación y
auditoría— opera a escala de organización: define quién responde de qué y qué hay que conservar. No
dice cómo un trabajo de una persona sostiene que no ajustó un umbral después de medir.

### 3.9 Auditoría de decisiones agénticas

Es el área más joven y la más pertinente al tercer rasgo del problema. El trabajo sobre visibilidad
en agentes de IA (Chan et al., 2024) propone tres categorías de medida —identificadores de agente,
supervisión en tiempo real y registro de actividad— y analiza su carácter intrusivo y su utilidad
según el contexto de despliegue.

**Coincidencia conceptual, y es genuina:** el registro de actividad que ese trabajo propone para
agentes desplegados es, en pequeño, lo que aquí se hace con el registro de aperturas y las
incidencias. **Diferencia:** allí el objetivo es la rendición de cuentas de un agente ante la
sociedad; aquí es la validez de una medición científica ante un tribunal. Y aquí el registro no lo
lleva un tercero: lo lleva el mismo que podría querer ocultarlo, lo que debilita la garantía y es
exactamente la limitación que la sección 7 desarrolla.

---

## 4. Comparación con las prácticas existentes

| Dimensión | Práctica establecida | Lo que hace este trabajo | ¿Mejor, igual o peor? |
|---|---|---|---|
| Declarar el criterio antes de medir | pre-registro (Nosek et al.; talleres de NeurIPS) | catorce documentos con fecha y commit anteriores | **igual**, en pequeño |
| Garantizar la validez bajo consulta adaptativa | *holdout* reutilizable; la escalera | nada: no hay garantía, hay registro | **peor**, y por mucho |
| Reproducibilidad declarada | lista de control de NeurIPS | la misma información, **verificada en el gate** | **algo más estricto** |
| Prevenir contaminación del conjunto de evaluación | cifrado, controles de exclusión | comprobación programática de disyunción **antes** de generar ejemplos | **igual en rigor, distinto en objeto** |
| Verificar que un artefacto es el declarado | `in-toto`, prueba de aprendizaje | huellas SHA-256 sin firmar, censo de 151 artefactos en el gate | **peor**: sin firmas ni cadena de confianza |
| Documentar el artefacto final | fichas de conjunto y de modelo | las mismas, más la **secuencia temporal** de decisiones | **comparable, con un eje más** |
| Registrar la actividad de un agente | visibilidad en agentes de IA | registro de aperturas por niveles e incidencias firmadas por fecha y commit | **igual en espíritu, autoadministrado** |
| Afirmar que el instrumento no cambió tras la exposición | **no se encuentra una práctica establecida equivalente** | diff vacío del subárbol congelado entre el commit de apertura y el de medición | **el candidato** |

---

## 5. Elementos potencialmente diferenciadores

Tres, y conviene tratarlos como candidatos a examen, no como hallazgos.

### 5.1 La invariancia del instrumento como afirmación falsable y baratísima

La afirmación «no ajusté nada después de ver los resultados» es, en la práctica habitual, una
declaración de intenciones que un revisor no puede comprobar. Aquí toma la forma:

```
git diff --stat <commit_de_la_primera_apertura>..<commit_de_la_medicion> -- src/ configs/ tests/
```

y su resultado tiene que ser **vacío**. Es falsable —cualquiera puede ejecutarla y refutarla—, cuesta
un segundo y no requiere infraestructura: solo haber definido de antemano **qué subárbol** constituye
el instrumento.

Lo que la hace distinta de la provenance al uso: la provenance demuestra **qué se ejecutó**; esto
demuestra **qué no se movió, y entre qué dos momentos**. Es una afirmación negativa anclada a dos
puntos del historial, y las afirmaciones negativas son justamente las difíciles de sostener.

**Lo que no es:** una garantía. Un operador decidido puede reescribir el historial. Sirve contra el
error y el olvido, no contra el fraude.

### 5.2 La graduación de la exposición en cinco niveles

Separar **apertura técnica · lectura de identificadores · exposición de etiquetas · exposición de
predicciones · utilización de resultados** permite decir algo preciso donde la práctica habitual dice
«el conjunto se usó» o calla. En este trabajo la distinción hace trabajo real: las cinco aperturas
alcanzaron niveles distintos —cuatro llegaron al 4, una se quedó en el 2— y eso cambia lo que se
puede afirmar de cada una.

**Lo que no es:** una escala validada. Son cinco categorías que resultaron útiles en un caso. Nadie
las ha contrastado y no hay razón para pensar que sean las cinco correctas.

### 5.3 El registro de los propios fallos como parte del procedimiento

Cinco incidencias publicadas con identificador, incluida una apertura accidental del conjunto
reservado y una regeneración indebida de cuatro artefactos publicados. No es una sección de
limitaciones escrita al final: son documentos fechados el día del fallo, con lo que se perdió y lo
que no se pudo restaurar.

**Lo que no es:** original. Es lo que un cuaderno de laboratorio honesto siempre ha hecho. Lo que
quizá sea menos común es que el gate de calidad **obligue** a ello: el censo de artefactos hace
fallar la construcción cuando algo publicado cambia, de modo que el fallo no se puede pasar por alto
aunque se quiera.

---

## 6. Evidencia experimental

Aquí es donde la pretensión se decide, y el resultado no es el que favorecería a una reclamación de
originalidad. Hay que leerlo entero.

### 6.1 Lo que el procedimiento detectó, con fecha

| Qué | Cómo se detectó | Qué habría pasado sin el procedimiento |
|---|---|---|
| **Contaminación del adaptador del redactor**: sus ejemplos salían de la partición donde se le medía; 11 de 17 casos afectados | auditoría **previa** al reentrenamiento, exigida por el propio procedimiento antes de tocar nada | la cifra de 17/17 habría llegado al tribunal como medida de redacción ante evidencia nueva, que no es |
| **Cuatro artefactos de E5 sobrescritos** al probar un gate | el censo de 151 huellas hizo fallar la verificación | cuatro ficheros publicados habrían cambiado sin que nadie lo supiera |
| **Una tabla de E15 borrada** sin copia versionada | el mismo censo | se habría descubierto al no encontrarla, sin saber cuándo ni por qué |
| **Quinta apertura, accidental**, del conjunto de prueba | revisión del código que la causaba, con el conjunto ya abierto | no habría constancia. La información expuesta era mínima, y nadie lo sabría |
| **Diagnóstico equivocado de la condición con distractor**: se culpaba al filtro de motor; la causa era que dos condiciones tenían configuración idéntica | obligación pre-registrada de comprobar los requisitos **antes** de mirar ningún veredicto | el rediseño se habría construido sobre una causa falsa |
| **Causa del fallo de ajuste del adaptador** | obligación de medir antes de volver a intentarlo | un tercer intento a ciegas, y probablemente un cuarto |

**Seis casos documentados en seis semanas.** Es evidencia de que el procedimiento **detecta**.

### 6.2 Lo que el procedimiento no evitó, que es la parte que hay que publicar

| Qué falló | Cuánto tiempo pasó sin detectarse |
|---|---|
| La contaminación del adaptador existía desde el 2 de septiembre de 2026 | **seis semanas** |
| La condición con distractor se publicó con un diagnóstico equivocado de su causa | **cinco semanas** |
| El conjunto de prueba se abrió accidentalmente | se detectó el mismo día, **después** de abrirlo |
| Cuatro artefactos publicados se sobrescribieron | se detectó en el acto, pero **ya estaban sobrescritos** |
| Una tabla publicada se borró sin copia | **irreversible**: no se declara restaurada |

**La lectura honesta:** este procedimiento no previene. Detecta, y a veces tarde. En dos de los cinco
casos el daño era ya irreversible cuando la detección ocurrió, y en uno pasó seis semanas en los
documentos publicados.

### 6.3 Lo que no hay, y hace falta decirlo

- **No hay comparación.** No se ha medido este procedimiento contra otro ni contra su ausencia. No se
  sabe cuántos de los seis hallazgos habría encontrado un revisor atento sin ninguna de las seis
  piezas.
- **No hay más de un caso.** Un proyecto, un operador, un dominio. `n = 1`.
- **No hay coste medido.** El procedimiento consume tiempo —catorce documentos, un censo, un gate que
  falla— y nadie ha medido cuánto, ni si ese tiempo habría rendido más en otra cosa.
- **No hay evidencia de que sea transferible.** Que funcione en un repositorio de un autor con control
  de versiones y gate de calidad no dice nada sobre un laboratorio de cinco personas.

---

## 7. Limitaciones

1. **El registro lo lleva el interesado.** Nada obliga a declarar una apertura. La quinta se declaró
   porque el autor decidió declararla; un autor distinto la habría borrado y nadie lo habría sabido.
   Esta es la limitación estructural y no tiene arreglo dentro del procedimiento: haría falta un
   tercero que custodie el conjunto reservado.
2. **Modelo de adversario débil.** Protege contra el error, el olvido y la prisa. No protege contra el
   fraude: las huellas no están firmadas y el historial se puede reescribir.
3. **Ninguna garantía estadística.** Donde el *holdout* reutilizable acota la pérdida de validez con
   una demostración, aquí solo hay un registro de cuántas veces se miró. Un registro no es una cota.
4. **La graduación en cinco niveles no está validada.** Son categorías de un caso.
5. **El procedimiento no cubre lo que no sabe que existe.** La contaminación del adaptador pasó seis
   semanas porque ninguna pieza comprobaba la disyunción entre los ejemplos de ajuste y el conjunto
   de evaluación: se añadió **después** de encontrarla. Un procedimiento así crece por incidentes, y
   eso significa que en cualquier momento le falta la comprobación del próximo fallo.
6. **No hay evaluación independiente del procedimiento mismo.** Quien lo diseñó es quien juzga que
   funciona, con la misma estructura de un solo operador que el procedimiento intenta compensar.

---

## 8. Riesgos de reclamar originalidad

Cinco, ordenados por lo que costarían en una defensa.

| Riesgo | Por qué es real | Cómo se evita |
|---|---|---|
| **Que un miembro del tribunal conozca el *holdout* reutilizable** | existe desde 2015, está en *Science* y es estrictamente más fuerte. Presentar «congelación verificable» como aportación a la protección de conjuntos reservados, sin citarlo, sería una laguna grave | citarlo como mejor solución al problema general y acotar la aportación a lo que esos mecanismos no cubren |
| **Que se lea como provenance reinventada** | `in-toto` y la prueba de aprendizaje hacen lo mismo con firmas y modelo de adversario. Una reclamación de novedad sobre huellas SHA-256 en un manifiesto no aguanta un minuto | declarar que el mecanismo no es nuevo y que la diferencia es de objeto: decisiones en lugar de artefactos |
| **Que la evidencia se lea como propaganda** | los seis hallazgos favorecen al procedimiento. Si se publican sin los cinco fallos que no evitó, el conjunto parece una demostración y es una selección | publicar las dos tablas, 6.1 y 6.2, juntas y con el mismo peso |
| **Que se confunda ingeniería con ciencia** | es la advertencia expresa del encargo. Un gate de calidad bien montado es buena ingeniería. Para ser aportación metodológica hace falta conocimiento generalizable, y de `n = 1` sin comparación no sale | presentarlo como procedimiento documentado y transferible **en hipótesis**, no como resultado validado |
| **Que la aportación desplace a la principal** | la pregunta de investigación es sobre el sistema de diagnóstico, no sobre el método. Un tribunal que vea la metodología en primer plano preguntará por qué | complementaria, en el capítulo de contribuciones, después de las que responden a la pregunta |

---

## 9. Posible relación con la pregunta principal

La pregunta canónica (ADR-004) pregunta si un agente con RAG puede explicar un diagnóstico a partir
de datos OBD-II, rastrear cada explicación hasta su evidencia de origen y **reconocer cuándo la
evidencia disponible no es suficiente** para sostener una explicación.

**La relación directa es instrumental, y es la que se puede defender.** El procedimiento no responde
a la pregunta: produce la evidencia con que se responde. Sin él, las cifras de los capítulos 5 y 6
serían cifras sin cadena de custodia, y la respuesta a la pregunta valdría lo que valga la palabra
del autor.

**Hay una relación conceptual, y conviene nombrarla con cuidado.** Lo que se le exige al sistema
—reconocer que su evidencia no basta y abstenerse, en lugar de producir una explicación sin
fundamento— es lo mismo que el procedimiento exige del trabajo: reconocer que la evidencia de una
afirmación no basta y declararlo, en lugar de publicarla. La simetría es real y es elegante, y
**presentarla como un resultado sería exactamente el error que la pregunta estudia**: una analogía
bien construida no es evidencia de nada. Puede mencionarse como observación en la discusión, y nada
más.

**Lo que no se hace, por decisión del encargo:** no se modifica la pregunta, no se añade un objetivo
y no se reformula ninguna hipótesis.

---

## 10. Recomendación fundamentada

**La pregunta era:** ¿hay aquí un procedimiento con características diferenciadoras y evidencia
suficiente para presentarlo como aportación, o se han aplicado correctamente prácticas conocidas de
reproducibilidad?

**La respuesta: lo segundo, en su mayor parte, con una parte pequeña que sí es defendible.**

### 10.1 Lo que no es aportación, y hay que decirlo primero

El pre-registro no es nuevo. Las huellas criptográficas de artefactos no son nuevas. La comprobación
de disyunción entre particiones no es nueva. El registro de incidencias no es nuevo. La verificación
de reproducibilidad en un gate de calidad es buena ingeniería y está descrita desde 2019. **Cinco de
las seis piezas son aplicación correcta de práctica conocida, y presentarlas de otro modo sería
insostenible.**

### 10.2 Lo que sí se puede defender, enunciado con su alcance

> Un procedimiento para **sostener de forma verificable, y a coste casi nulo, que las decisiones de
> diseño de un experimento no se modificaron entre la primera exposición al conjunto reservado y la
> medición**, junto con un registro graduado de esas exposiciones en cinco niveles. Pensado para el
> caso de **un solo operador con asistencia de agentes**, donde no hay separación de funciones que
> garantice nada. Su valor demostrado es la **detección y el registro honesto** —seis casos
> documentados—, **no la prevención**: cinco fallos lo atravesaron, uno de ellos durante seis
> semanas.

Eso es todo lo que la evidencia aguanta. Es poco, y es verdad.

### 10.3 Cómo incorporarlo

| Dónde | Cómo |
|---|---|
| **Capítulo de contribuciones** | como **contribución metodológica complementaria**, después de las que responden a la pregunta, con el enunciado de 10.2 literal y las dos tablas de evidencia —lo detectado y lo no evitado— juntas |
| **Capítulo de limitaciones** | las seis de la sección 7, y en particular que el registro lo lleva el interesado |
| **Pregunta, objetivos e hipótesis** | **sin cambios.** No se añade objetivo ni se reformula hipótesis |
| **Trabajo futuro** | validar el procedimiento es el trabajo que falta, y se puede enunciar: aplicarlo en un segundo proyecto con otro operador; medir su coste; comparar contra su ausencia; contrastar la graduación de cinco niveles |
| **Defensa oral** | si el tribunal pregunta por la aportación metodológica, la respuesta empieza por «el mecanismo no es nuevo» y sigue por lo que sí lo es. Empezar por lo contrario invita a la pregunta que no se puede responder |

### 10.4 Lo que no se recomienda hacer

- **No** presentarlo como aportación principal.
- **No** reclamar que previene errores: la evidencia dice que detecta, y a veces tarde.
- **No** compararlo favorablemente con el *holdout* reutilizable ni con la escalera: son más fuertes
  en lo que hacen, y ocultarlo sería la clase de omisión que un tribunal encuentra.
- **No** llamarlo marco, metodología ni *framework*. Es un procedimiento de seis piezas, cinco de
  ellas prestadas.

---

## Referencias

Las diez citadas están en `research/references/bibliography.bib` con su identificador resuelto.

| Clave | Trabajo |
|---|---|
| `Nosek2018` | Nosek, B. A., Ebersole, C. R., DeHaven, A. C. y Mellor, D. T. (2018). The preregistration revolution. *PNAS*, 115(11), 2600–2606. `10.1073/pnas.1708274114` |
| `Pineau2021` | Pineau, J. et al. (2021). Improving Reproducibility in Machine Learning Research. *JMLR*, 22(164) |
| `Jacovi2023` | Jacovi, A., Caciularu, A., Goldman, O. y Goldberg, Y. (2023). Stop Uploading Test Data in Plain Text. *EMNLP 2023*, 5075–5084. `10.18653/v1/2023.emnlp-main.308` |
| `Dwork2015` | Dwork, C. et al. (2015). The reusable holdout: Preserving validity in adaptive data analysis. *Science*, 349(6248), 636–638. `10.1126/science.aaa9375` |
| `BlumHardt2015` | Blum, A. y Hardt, M. (2015). The Ladder: A Reliable Leaderboard for Machine Learning Competitions. *ICML 2015*, PMLR 37, 1006–1014 |
| `Gebru2021` | Gebru, T. et al. (2021). Datasheets for datasets. *CACM*, 64(12), 86–92. `10.1145/3458723` |
| `Mitchell2019` | Mitchell, M. et al. (2019). Model Cards for Model Reporting. *FAT\* 2019*, 220–229. `10.1145/3287560.3287596` |
| `TorresArias2019` | Torres-Arias, S., Afzali, H., Kuppusamy, T. K., Curtmola, R. y Cappos, J. (2019). in-toto: Providing farm-to-table guarantees for bits and bytes. *USENIX Security 2019*, 1393–1410 |
| `Jia2021` | Jia, H. et al. (2021). Proof-of-Learning: Definitions and Practice. *IEEE S&P 2021*, 1039–1056. `10.1109/SP40001.2021.00106` |
| `Chan2024` | Chan, A. et al. (2024). Visibility into AI Agents. *ACM FAccT 2024*, 958–973. `10.1145/3630106.3658948` |

**Lo que se ha verificado de cada una:** que el identificador resuelve y que sus metadatos de registro
—autores, año, publicación, páginas— son los que aquí se citan. **Lo que no se ha verificado:** las de
los talleres de pre-registro de NeurIPS, citadas como práctica de la comunidad y no por un resultado
concreto, y las áreas 3.7 y 3.8, descritas como contexto sin atribuir a un trabajo específico. Donde
no hay cita, no se atribuye nada a nadie.
