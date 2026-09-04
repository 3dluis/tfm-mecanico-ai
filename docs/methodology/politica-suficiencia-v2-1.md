# Política de suficiencia v2.1 — la sección como unidad de papel

**Fecha:** 4 de septiembre de 2026 · **Estado:** documentada **antes** de implementarse y de
volver a medir. El commit que introduce este documento precede al del código y al del
resultado.

**Naturaleza:** **segunda revisión, posterior a observar el resultado de v2.** No sustituye ni
anula a v2: v2 y su resultado quedan congelados y se publican. v2.1 es una versión nueva del
criterio, motivada por una regresión concreta que v2 produjo y cuya causa se diagnosticó antes
de proponer nada.

## 1. Procedencia: de dónde viene cada versión

| Versión | Qué decide el soporte | Resultado sobre los 17 casos | Artefacto |
|---|---|---|---|
| v1 | señal + tipo de documento + código | 9/17 | `experiments/E15_suficiencia_verifier_v1.json` |
| v2 | lo anterior + papel del **fragmento** por rasgos léxicos | 14/17, con una abstención falsa nueva | `experiments/E15_suficiencia_verifier_v2.json` |
| **v2.1** | lo anterior, con el papel derivado de la **sección** del manual | por medir | este documento |

## 2. Causa que motiva el cambio

v2 corrigió las seis explicaciones sin pertinencia de v1 y produjo **una regresión**: el caso
de la fuga de vacío con evidencia completa pasó de explicar a abstenerse, y la cobertura de
explicación bajó de 3/5 a 2/5.

Diagnóstico, verificado en el registro de v2: el procedimiento diagnóstico del código `P2187`
está **troceado en varios fragmentos**. Uno contiene los pasos de inspección y las
bifurcaciones, y v2 lo clasifica correctamente como procedimiento, pero **no nombra la señal**.
Otro contiene la condición de detección, **sí nombra la señal**, y v2 lo clasifica como
referencia porque, leído en aislamiento, describe qué vigila la centralita y no cómo se
comprueba.

Los dos pertenecen a la **misma sección del manual**, titulada `DTC P2187 [ZJ, Z6]`, que es el
procedimiento diagnóstico de ese código.

El defecto no está en la política sino en su **granularidad**: el troceado es una decisión del
sistema de recuperación, no una propiedad del documento. Clasificar cada fragmento en
aislamiento hace que una unidad semántica del manual se rompa y que sus partes reciban papeles
distintos. Es un artefacto de la recuperación que se está midiendo como si fuera una
característica de la evidencia.

## 3. Hipótesis de corrección

> Si el papel se deriva de la **sección** a la que el fragmento pertenece, en lugar de del
> fragmento aislado, la unidad de clasificación coincide con la unidad semántica del manual.
> Entonces los fragmentos de un procedimiento se clasifican como procedimiento aunque el
> troceado los separe, y los de una tabla siguen siendo tabla.

**Predicción comprobable, declarada antes de ejecutar:** el caso de la fuga de vacío con
evidencia completa debería volver a explicar, y los seis casos que v2 corrigió deberían seguir
absteniéndose, porque sus fragmentos aceptados pertenecen a secciones tituladas
`KOEO/KOER SELF-TEST` y `DTC DETECTION LOGIC AND CONDITIONS`, que no son procedimientos bajo
ninguna de las dos granularidades.

**Esta predicción no es prueba suficiente.** Que acierte solo dice que la corrección hace lo
que se propone en siete casos conocidos. La generalidad se comprueba aparte, con la regla
aplicada a códigos y señales que no están en el banco experimental.

## 4. Regla exacta, fijada antes de ejecutar

El papel de un fragmento se decide en dos pasos, en este orden:

**Paso 1 · Por la sección, que es la taxonomía del propio manual.**

| Si el encabezado de sección… | Papel |
|---|---|
| nombra **un único código** como asunto, es decir, empieza por `DTC` seguido de un código de la forma letra más cuatro dígitos | `PROCEDURAL_DIAGNOSTIC_EVIDENCE` |
| anuncia un **listado**: tabla, autodiagnóstico, índice o lista | `CODE_DEFINITION_OR_TABLE` |
| anuncia **material de referencia**: lógica o condiciones de detección, modo de prueba, especificaciones, función, descripción, monitorización | `SUPPORTING_DIAGNOSTIC_REFERENCE` |

**Paso 2 · Solo si el encabezado no declara nada de lo anterior**, se aplica la clasificación
por rasgos del fragmento que introdujo v2: pasos de inspección y criterios de decisión →
procedimiento; lógica de detección → referencia; listado o muchos códigos → tabla; en otro
caso, sin clasificar.

**Fundamento en el corpus, no en los casos.** El manual del vehículo tiene **272 secciones
tituladas por un único código, con 921 fragmentos**, y **296 fragmentos en secciones de tabla,
autodiagnóstico o lógica de detección**. La regla lee la organización que el documento ya
declara; no impone una ajena.

**Determinismo.** La regla es una función del encabezado de sección y, subsidiariamente, del
texto del fragmento. No consulta el caso, ni el fallo, ni el resultado esperado, ni ninguna
lista de códigos o señales.

## 5. Política de soporte: sin cambios respecto de v2

Una afirmación se sostiene si existe al menos un fragmento **aplicable al vehículo**, con papel
de **procedimiento**, que **menciona la señal** y **porta el código esperado**. Las referencias
y las tablas acompañan y nunca sostienen solas. Los candidatos se examinan por papel antes que
por puntuación de recuperación.

## 6. Lo único que cambia entre v2 y v2.1

**La granularidad de la clasificación: fragmento → sección.** Nada más.

No cambian, y se declaran para que la comparación sea limpia:

| | Valor, idéntico en v2 y v2.1 |
|---|---|
| Conjunto de datos | `synthetic_v2`, `dataset_type: synthetic` |
| Semilla | `20260901` |
| Casos | los 17 de `configs/goldset_mazda3_bk.yaml` |
| Corpus | versión `0.1.0`, mismo índice |
| Modelo de embeddings | `paraphrase-multilingual-MiniLM-L12-v2` |
| Modelo especializado | bosque aleatorio con calibración isotónica, cv=5 |
| Umbral de confianza | **0,79**, sin tocar |
| Resto de umbrales | mínimo de fragmentos 2, fuentes 1, cobertura 0,8, puntuación desactivada |
| Aplicabilidad admitida | solo coincidencia exacta |
| Filtro de motor | sin tocar; v1 y v2 muestran que funciona |

**Commit de partida:** `9d44037`.

## 7. Qué se hará con el resultado

Se compara con v1 y con v2, caso a caso y por condición, con estas magnitudes: decisiones
correctas, cobertura de explicación, abstenciones correctas, abstenciones falsas y
explicaciones sin soporte suficiente. **No se juzga por la exactitud agregada.**

**Si aparecen regresiones nuevas, no se hace una v2.2.** Se congela el resultado, se diagnostica
el mecanismo y se presenta antes de proponer ningún cambio más.

## 8. Advertencia que acompaña a esta versión allá donde se publique

v2.1 se diseñó **después** de ver el resultado de v2 y con conocimiento de qué caso fallaba.
Su justificación es estructural y comprobable en el corpus, pero la secuencia no es un
pre-registro ciego, y así debe presentarse. La evidencia de que la regla no está escrita para
los casos conocidos no la aporta su resultado sobre ellos: la aportan las pruebas sobre
códigos y señales ajenos al banco experimental.
