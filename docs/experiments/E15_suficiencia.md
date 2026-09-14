# E15 — Verificador de suficiencia de evidencia

Fecha: 1 de septiembre de 2026 · Estado: **cerrada**
**Sin modelo de lenguaje.** Ni una llamada.

## Lo que demuestra esta fase

Que la decisión de explicar o abstenerse se puede tomar y **auditar** sin que
intervenga un generador de texto. Si la tomara el modelo de lenguaje, la
respuesta a la pregunta de investigación dependería de su disposición a admitir
que no sabe algo, que es justo lo que no cabe dar por supuesto.

## El experimento central, en dos casos

Mismos datos OBD-II. Mismo modelo. Misma atribución. **Misma confianza.** Lo
único que cambia es que se retira del índice la evidencia documental.

| Caso | Confianza | Docs aplicables | Cobertura | Decisión |
|---|---|---|---|---|
| C05 · evidencia presente | 0,908 | 4 | 1,00 | **EXPLAIN** |
| C06 · evidencia retirada | 0,908 | **0** | 0,00 | **ABSTAIN** |

La decisión cambia porque cambió la evidencia, no porque cambiara el vehículo ni
la certeza del modelo. Es la pregunta de investigación reducida a su mínima
expresión, y funciona.

## Corrección importante de una afirmación anterior

Cuatro informes --E2, E10, E11 y E12-- afirman que la fuga de vacío **no tiene
respaldo documental** porque el código P0171 no aparece en el corpus. **Es
falso**, y el propio sistema lo destapó.

Mazda **no usa los códigos genéricos** de mezcla. Usa la familia
P2177/P2178/P2187/P2188. El corpus contiene 30 fragmentos con P2187:

> **DTC P2187 — «Fuel system too lean at idle»**
> *«PCM monitors short term fuel trim (SHRTFT) and long term fuel trim (LONGFT)
> during closed loop fuel control at idle.»* — `srvc/B3E010202100W09.pdf`

Es literalmente la firma que E2 modeló y E4 midió: ajustes positivos, peores en
ralentí. La evidencia estaba ahí desde el principio.

**La lección importa más que el error.** Busqué un código, no lo encontré y
concluí que no había evidencia. El sistema de recuperación, al que no se le dijo
qué código buscar sino qué diagnóstico sostener, la encontró. **No haber
encontrado algo no es que no exista**, y una afirmación de ausencia exige más
cuidado que una de presencia.

El conjunto anotado se corrigió: C05 pasa a `EXPLAIN` con su evidencia real, y el
caso de abstención pasa a ser **construido** --C06, misma condición con la
evidencia retirada-- en lugar de heredado de un descuido. Es mejor ciencia: la
abstención se provoca, no se encuentra.

## Resultados

| Caso | Variante | Esperado | Decidido | | Confianza | Docs | Cobertura |
|---|---|---|---|---|---|---|---|
| C01 deriva de caudalímetro | FULL | EXPLAIN | ABSTAIN | ✗ | 0,600 | 6 | 1,00 |
| C02 termostato | FULL | EXPLAIN | EXPLAIN | ✓ | 1,000 | 7 | 1,00 |
| C03 sonda lenta | FULL | EXPLAIN | EXPLAIN | ✓ | 1,000 | 6 | 1,00 |
| C04 fallo de encendido | FULL | EXPLAIN | ABSTAIN | ✗ | 0,462 | 4 | 1,00 |
| C05 fuga de vacío | FULL | EXPLAIN | EXPLAIN | ✓ | 0,908 | 5 | 1,00 |
| C06 evidencia retirada | ABSENT | ABSTAIN | ABSTAIN | ✓ | 0,908 | 0 | 0,00 |
| C07 evidencia parcial | PARTIAL | ABSTAIN | ABSTAIN | ✓ | 0,908 | 4 | 0,00 |
| C08 distractor | DISTRACTOR | ABSTAIN | ABSTAIN | ✓ | 0,908 | 4 | 0,00 |
| C09 distractor sin filtro | DISTRACTOR | ABSTAIN | ABSTAIN | ✓ | 0,908 | 1 | 0,00 |

**7 de 9.** Las dos discrepancias son informativas y no se han corregido ajustando
umbrales.

> **Nota del 13-09-2026.** Esta cifra corresponde al verificador v1 sobre los 9 casos de la
> primera pasada (1-09-2026) y se conserva como registro histórico. El conjunto anotado se
> amplió a 17 casos y el verificador pasó por v2 y v2.1; el resultado vigente es **15 de 17**
> (`experiments/E15_suficiencia.json`, reejecutado con recuperación canónica el 13-09-2026).
> Secuencia completa: `docs/experiments/resultado-verificador-v2-1.md` y
> `docs/experiments/resultado-rerun-a.md`.

### Las cuatro condiciones, sobre el mismo caso

Confianza **idéntica** en las cuatro: 0,908. Lo único que cambia es el corpus.

| Condición | Docs aplicables | Cobertura | Decisión | Por qué |
|---|---|---|---|---|
| **FULL** | 5 | 1,00 | **EXPLAIN** | La evidencia está y sostiene |
| **ABSENT** | 0 | 0,00 | ABSTAIN | No queda nada aplicable |
| **PARTIAL** | 4 | 0,00 | ABSTAIN | Hay tablas de códigos, no procedimientos |
| **DISTRACTOR** | 4 | 0,00 | ABSTAIN | El del otro motor no llega ni a ordenarse |

**Un fallo de diseño corregido.** La condición DISTRACTOR inicial no probaba lo
que decía: el filtro de motor bloquea el procedimiento del LF **antes de
ordenarlo**, así que nunca alcanzaba al verificador y DISTRACTOR resultaba
idéntica a PARTIAL.

Se añadió **C09**, con el filtro de motor desactivado a propósito, que es la
única forma de medir la última línea de defensa. Resultado: el distractor **sí
llega** --`DTC P2187 [LF]` aparece entre lo recuperado-- y el validador de
aplicabilidad lo degrada a `PARTIAL_MATCH`, que no cuenta como evidencia fuerte.
Queda un solo documento aplicable, por debajo del mínimo de dos, y el agente se
abstiene.

**Dos líneas de defensa independientes:** el filtro en la recuperación y el
validador de aplicabilidad. La segunda funciona sin la primera.

## Calibración de la confianza

| | ECE | Confianza media | Acierto | Sesgo |
|---|---|---|---|---|
| Sin calibrar | 0,144 | 0,738 | 0,878 | **−0,140** |
| Calibrado (isotónica, cv=5) | **0,085** | 0,886 | 0,878 | **+0,009** |

E6 había medido que el bosque estaba infraconfiado. Sin corregirlo, un umbral
sobre la confianza cruda se abstendría de más y **parecería prudencia cuando
sería mala medición**. La calibración se ajusta sobre entrenamiento con
validación cruzada interna, para no gastar validación dos veces.

## Por qué falla C04, y por qué probablemente no es un fallo

El fallo de encendido tiene confianza calibrada **0,462**. La calibración, que
mejoró la medición global, **bajó** la confianza de esta condición: el modelo
acierta menos de lo que creía en F05.

El conjunto anotado dice `EXPLAIN` porque **existe un documento**. El criterio
dice `ABSTAIN` porque **el modelo no es fiable ahí**. Son dos cosas distintas y
ambas importan: la suficiencia depende de la evidencia documental *y* de la
fiabilidad del diagnóstico.

Se deja la discrepancia registrada en lugar de resolverla bajando el umbral. Es
plausible que la etiqueta esperada de C04 esté mal puesta --se definió por
disponibilidad documental, no por fiabilidad del modelo-- y esa es una discusión
que corresponde al diseño del conjunto, no al ajuste del criterio.

## C01: corregido, y la corrección explica el resultado anterior

Cobertura **0,00** en la primera ejecución; **1,00** tras corregir el mapeo.

La razón es el hallazgo de E4 mordiendo a nivel de verificación de soporte. El
modelo detecta la deriva del caudalímetro **por los ajustes de combustible** --E9
confirmó que `maf` no contribuye nada--, así que las afirmaciones hablan de
`ltft_bank1` y `stft_bank1`. Pero el procedimiento del manual para P0102 habla de
**la tensión del circuito del caudalímetro**, no de ajustes de combustible.

La verificación de soporte lo rechazó, correctamente: ese procedimiento no
sostiene una afirmación sobre ajustes de combustible.

**El sistema no tiene un fallo; tiene una desalineación real.** La observación y
la documentación describen el mismo fallo por vías distintas. La evidencia que sí
sostendría esas afirmaciones es P2177 --«Fuel system too lean off idle»--, que
está en el corpus y no se le pidió.

**Corregido.** Una deriva del caudalímetro deja **dos** rastros documentales y
solo se buscaba uno: los códigos del sensor --P0101, P0102-- documentan la
tensión de su circuito, y los de mezcla --P2177, P2178-- documentan los ajustes
de combustible desviados, que es lo que el modelo observa.

> **P2177 — «System too lean off idle»**
> *«The PCM monitors short term fuel trim (SHRTFT) and long term fuel trim
> (LONGFT) during closed loop fuel control during off-idle.»*

Con el mapeo corregido, la cobertura de C01 pasa de 0,00 a **1,00**, y su único
motivo de abstención pasa a ser la confianza del modelo.

No es ajustar para acertar: es corregir un mapeo que describía mal la condición.
La distinción entre P2177 --«off idle»-- y P2187 --«at idle»-- encaja además con
la física: la fuga de vacío es peor en ralentí, la deriva del caudalímetro afecta
a todos los regímenes.

## Verificación de soporte: citar no es sostener

Es la pieza que faltaba y la que más cambió los resultados.

Una afirmación puede citar un fragmento que existe, resuelve, pertenece al
vehículo correcto y tiene buena puntuación, **y no decir nada sobre lo que se
afirma**. Es el fallo más difícil de ver, porque el texto resultante parece
impecable.

Un fragmento sostiene una afirmación solo si:

1. **menciona la señal** --con el vocabulario del manual: «short term fuel trim»,
   no `stft_bank1`--;
2. es **contenido diagnóstico** y no una descripción de funcionamiento;
3. **porta el código esperado**, cuando la condición tiene uno.

El punto 2 sale directamente de E12: la recuperación devuelve arriba
`HEATED OXYGEN SENSOR (HO2S) FUNCTION`, que explica cómo funciona el sensor y no
sostiene que esté averiado.

Lo que esta verificación **no** hace: juzgar si el contenido implica lógicamente
la afirmación. Eso exigiría una interpretación que no se puede hacer de forma
verificable, y se deja constancia del límite en lugar de fingir que decide más.

## Dos errores encontrados por mirar las cifras

**La fusión devolvía puntuaciones de otra escala.** F01 puntuaba 0,016 y los
demás 0,26–0,52: dos órdenes de magnitud. La fusión por rango recíproco sustituía
la similitud coseno por su propio peso, en torno a 1/60. El criterio comparaba
manzanas con naranjas y F01 se abstenía por un artefacto. Ahora la fusión decide
el orden y cada fragmento conserva su puntuación de origen.

**La condición ABSENT no retiraba toda la evidencia.** Excluir los cuatro
ficheros del procedimiento de P2187 dejaba fuera las tablas de códigos y los
procedimientos vecinos --P2096, P2195, P2196-- que portan el mismo código: la
evidencia seguía disponible y C06 seguía explicando. La exclusión pasa a ser por
código, y retira 70 fragmentos en lugar de 16.

El segundo es especialmente instructivo: **una condición ABSENT mal construida
haría que el experimento central diera un falso positivo**, y el síntoma habría
sido «el agente explica igual sin evidencia», que es exactamente lo que el
experimento quiere detectar.

## El criterio

Conjunción, no promedio ponderado. Un promedio deja que un valor alto compense a
uno inaceptablemente bajo, y aquí ningún factor es compensable: sin cobertura de
afirmaciones no hay explicación que sostener por muy confiado que esté el modelo.
Hay un test que lo comprueba con confianza 0,99 y cero documentación.

Umbrales: confianza ≥ **0,80** · fragmentos ≥ 2 · fuentes distintas ≥ 1 ·
cobertura ≥ 0,80 · sin contradicciones · aplicabilidad `EXACT_MATCH`.

### Los umbrales están calibrados, no elegidos

**Confianza: 0,80.** Criterio declarado: el umbral más bajo con precisión ≥ 0,93
sobre las 98 ventanas de validación.

| umbral | cobertura | precisión |
|---|---|---|
| 0,60 | 0,929 | 0,912 |
| 0,75 | 0,867 | 0,929 |
| **0,80** | **0,827** | **0,938** |
| 0,90 | 0,612 | 0,917 |

**Ningún umbral alcanza 0,95**: la precisión se estanca en 0,93-0,94. Se hace
constar en lugar de subir el umbral hasta que la cobertura se desplome por
alcanzar una cifra redonda.

**Puntuación de recuperación: desactivada.** Se midió si discriminaba el soporte:

| | fragmentos | mediana |
|---|---|---|
| Sostienen la afirmación | 9 | 0,459 |
| No la sostienen | 37 | 0,443 |

El **38 %** de los fragmentos que **no** sostienen puntúan por encima de la
mediana de los que **sí**. Un umbral ahí filtraría por azar y daría apariencia
de rigor. Se retira en lugar de calibrarlo.

Es la **tercera vez** que aparece lo mismo por caminos independientes: en el
orden de los resultados (E11), en la evaluación de la recuperación (E12) y ahora
en el criterio de suficiencia. **La similitud no es evidencia.**

### Que la calibración no cambiara las decisiones es en sí un resultado

Con los umbrales calibrados, las nueve decisiones son las mismas que con los
puestos a ojo. El resultado **no dependía** de haber acertado con unos números
arbitrarios.

## Tests

`tests/test_sufficiency.py` — 26 casos:

- `test_supported_evidence` y `test_insufficient_evidence_sin_documentacion_aplicable`;
- **`test_el_criterio_es_conjuntivo_y_no_compensable`**: confianza 0,99 con cero
  documentación debe abstenerse;
- `test_la_cobertura_exige_soporte_verificado_y_no_solo_una_cita`;
- `test_una_descripcion_de_funcionamiento_no_es_contenido_diagnostico`;
- `test_un_fragmento_sin_el_codigo_esperado_no_sostiene_la_afirmacion`;
- `test_cinco_fragmentos_del_mismo_documento_no_son_cinco_fuentes`;
- `test_se_devuelven_todos_los_motivos_y_no_solo_el_primero`;
- `test_el_veredicto_explica_que_falta_y_no_solo_que_falla`.

## Gates

| Gate | Resultado |
|---|---|
| `ruff check .` | sin incidencias |
| `mypy src` (strict) | sin incidencias, 60 ficheros |
| `pytest` | **242 casos** en verde |

## Siguiente

Calibrar los umbrales sobre validación, corregir el mapeo diagnóstico→DTC de F02
y extender a las cuatro condiciones de corpus (FULL, PARTIAL, ABSENT,
DISTRACTOR), que es E17. El LLM sigue sin hacer falta para nada de eso.
