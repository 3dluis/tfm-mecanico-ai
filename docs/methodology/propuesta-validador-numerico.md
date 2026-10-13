# Propuesta: un validador determinista de las afirmaciones numéricas

**Fecha:** 13 de octubre de 2026 · **Qué es:** una **propuesta de corrección del sistema**, separada
de los experimentos históricos y **no implementada** · **Qué la motiva:** `L-26`, y su análisis de
impacto en [`impacto-l26-e13.md`](../audits/impacto-l26-e13.md) · **Cuándo se aplica:** de forma
**prospectiva**. Ninguna cifra publicada se recalcula con ella · **Estado: diseño. No se ha escrito
una línea de código**

## 1. El problema que tiene que resolver

Medido sobre registros ya publicados: **cinco de las veintitrés salidas** del adaptador canónico
contienen al menos una cifra que no procede de los datos que el modelo recibió. Dos patrones
distintos:

| Patrón | Ejemplo medido | Qué falla |
|---|---|---|
| **Magnitud sustituida** | el verificador dice «cobertura 0.00 < 0.80»; el redactor escribe «cobertura 0.908 < 0.80» | el número es la **confianza calibrada**, puesto donde iba la cobertura. La comparación resulta **internamente falsa**: 0,908 no es menor que 0,80 |
| **Umbral cambiado** | «confianza 0.600 < 0.79» → «confianza 0.60 < 0.80» | el valor se redondea legítimamente y **el umbral se altera**: 0,79 se convierte en 0,80 |
| **Dígitos corrompidos** | la observación `OBS001` vale 0,083801; la afirmación escribe «delta_max de 0.08381» | cita el identificador correcto y **corrompe el valor que cita**. No es redondeo: 0,083801 a cinco decimales es 0,08380 |

Y las tres barreras actuales los dejan pasar, porque ninguna mira números:

| Barrera | Qué comprueba | Qué no |
|---|---|---|
| Esquema de salida | que los campos existan y tengan el tipo declarado | que su contenido sea cierto |
| Respeto al veredicto | que la decisión escrita sea la recibida | nada del cuerpo del texto |
| Citas entregadas | que todo identificador documental citado se hubiera entregado | que lo que se dice del fragmento sea cierto |

**El enunciado de la regla que falta**, en una frase: *si una explicación contiene una comparación
numérica incorrecta, no debe presentarse como válida*.

## 2. Las siete comprobaciones

El encargo las enumera. Para cada una: qué comprueba, contra qué, y **si hoy es posible**.

| # | Comprobación | Contra qué se contrasta | Posible hoy |
|---|---|---|---|
| 1 | **Nombre de la métrica** | el `signal` y el `statistic` de la observación citada, o la señal del veredicto —`claim_coverage`, `confidence`— | **sí** |
| 2 | **Valor** | el `value` de la observación citada, admitiendo cualquier redondeo de 0 a 6 decimales | **sí** |
| 3 | **Umbral** | el umbral vigente del criterio: `min_confidence` 0,79, `min_claim_coverage` 0,80, `min_supporting_chunks` 2 | **sí** |
| 4 | **Operador de comparación** | que la relación escrita sea **cierta** con los dos números: si dice `a < b`, que `a < b` | **sí**, y es la que habría detectado los tres casos de `C07`, `C08` y `D01` |
| 5 | **Unidad** | la unidad de la señal, declarada en `obd/signals.py` | **NO todavía**: ver §3 |
| 6 | **Procedencia** | que cada cifra del texto se pueda atribuir a una observación citada o a una señal del veredicto | **sí** |
| 7 | **Coherencia entre texto y datos estructurados** | que no haya ninguna cifra en el texto sin origen, ni ninguna magnitud del veredicto contradicha | **sí** |

### Qué habría detectado cada una, sobre lo ya medido

| Caso | Qué lo habría detenido |
|---|---|
| `C07_partial`, `C08_distractor`, `D01` | la **4**: «0.908 < 0.80» es falsa, y eso se comprueba sin saber nada del dominio |
| `C01_maf_drift` | la **3**: 0,80 no es ningún umbral del criterio; el de confianza es 0,79 |
| `C03_o2_slow_response`, afirmaciones `C01` y `C02` | la **2** y la **6**: 0,08381 no es ningún redondeo de 0,083801 y no sale de ninguna observación citada |

**Las cuatro primeras bastarían para los cinco casos conocidos.** Conviene decirlo porque fija una
versión mínima defendible, sin pedir cambios en el resto del recorrido.

## 3. La comprobación 5 no es implementable todavía, y la razón importa

Las observaciones que el redactor recibe **no llevan la unidad**. Sus campos son
`observation_id`, `kind`, `signal`, `statistic`, `value`, `direction`, `importance`, `session_id`,
`window_start_s`, `window_end_s`. La unidad existe en el catálogo de señales —`rpm`, `km/h`, `%`,
`°C`, `g/s`, `kPa`, `V`, `° antes del PMS`— y **no viaja en el paquete de evidencia**.

Consecuencia: **las afirmaciones actuales no mencionan ninguna unidad**, y no por descuido del
modelo: nadie se la dio. «`ltft_bank1` con `max` de 2.716» no dice que sean puntos porcentuales.

De modo que la comprobación 5 exige dos pasos, en este orden:

1. **Añadir la unidad a la observación** en el paquete de evidencia, tomándola del catálogo. Es un
   cambio en la entrada del redactor y **altera el experimento**: la plantilla de afirmación
   cambiaría y las salidas no serían comparables con las publicadas.
2. **Después**, comprobar que la unidad escrita es la de la señal.

**Por eso la propuesta separa dos versiones** y no las mezcla:

| Versión | Qué comprueba | Qué cambia del recorrido |
|---|---|---|
| **V1 · mínima** | las comprobaciones 1, 2, 3, 4, 6 y 7 | **nada de la entrada.** Solo se añade una barrera a la salida, como la de las citas |
| **V2 · con unidades** | las siete | añade la unidad a la observación, lo que cambia qué recibe el redactor |

**Se recomienda V1.** Cubre los cinco casos conocidos, no toca la entrada del modelo y por tanto no
invalida la comparación con las salidas publicadas. V2 queda como trabajo posterior y como la
respuesta a una pregunta que este trabajo no se ha hecho: si una explicación sin unidades es una
explicación suficiente para un mecánico.

## 4. Dónde se coloca, y qué hace cuando falla

**Dónde.** Junto a la barrera que ya rechaza identificadores no entregados: en el mismo punto, sobre
la salida ya parseada, **después** del verificador y **antes** de dar la salida por válida. No toca
el verificador, no toca la recuperación y no toca el modelo.

**Qué hace cuando encuentra una cifra sin origen o una comparación falsa.** Tres conductas posibles,
y la propuesta elige una:

| Conducta | Qué implica | ¿Se propone? |
|---|---|---|
| **Rechazar la salida y marcarla inválida** | el recuento de «salidas válidas» pasa a incluir la fidelidad numérica, que es lo que el encargo pide: *si contiene una comparación numérica incorrecta, no debe presentarse como válida* | **sí** |
| Corregir el número en el texto | el sistema reescribiría lo que el modelo dijo, y la salida dejaría de ser la del modelo | no |
| Avisar y publicar igual | deja la decisión al lector, que es quien no puede comprobarlo | no |

**Y una consecuencia que hay que aceptar de antemano:** con el validador puesto, **el «17/17» del
adaptador canónico habría sido 13/17** —fallarían `C01`, `C03`, `C07` y `C08`—, y el 6/6 de P1,
5/6. No es un empeoramiento del sistema: es que la métrica pasa a medir algo más estricto.
Declararlo antes de medir evita que parezca una regresión.

## 5. El protocolo de evaluación, fijado antes de implementar

### 5.1 Sobre qué se evalúa, y sobre qué no

| | |
|---|---|
| **Conjunto** | el **conjunto de evaluación independiente del redactor**, quince ventanas de validación de `synthetic_v3`, congelado el 13-10-2026 en `configs/evaluacion-independiente-redactor.json` |
| **Por qué ese** | ninguno de los dos adaptadores lo ha visto, y la selección se fijó antes de que existiera el adaptador que se iba a medir |
| **Lo que NO se usa** | **el conjunto de prueba.** Se abrió cinco veces y no es plenamente independiente; usarlo para ajustar un mecanismo nuevo sería gastar lo único que no se repone, y además está prohibido por el encargo |
| **Lo que tampoco se usa** | los diecisiete casos de E15, porque el validador se diseñó **mirando** cinco de sus salidas. Evaluarlo ahí mediría la búsqueda |

### 5.2 Las dos métricas, y por qué hacen falta las dos

Un validador que rechazara todo tendría cero falsos negativos y sería inútil. Se miden los dos
errores por separado, como en el criterio de suficiencia:

| Métrica | Qué cuenta | Qué la empeora |
|---|---|---|
| **Defectos no detectados** | salidas con una cifra ajena que el validador acepta | una expresión numérica que la gramática no cubre |
| **Rechazos indebidos** | salidas correctas que el validador rechaza | un redondeo legítimo tomado por error, una cifra del dominio que no es una métrica |

**Criterio, escrito antes de medir:** el validador se adopta si **detecta los cinco defectos
conocidos** —reinyectados como casos de prueba sintéticos, no sobre el conjunto de evaluación— y
produce **cero rechazos indebidos** sobre las salidas del conjunto independiente. Un solo rechazo
indebido obliga a revisar la gramática antes de adoptarlo: una barrera que rechaza explicaciones
correctas es peor que no tener barrera, porque el sistema se abstendría por un defecto del validador
y lo registraría como insuficiencia de la evidencia.

### 5.3 Qué lo cuestionaría

- Que la mayoría de los rechazos sean indebidos: significaría que la gramática no distingue una
  cifra métrica de una cifra cualquiera.
- Que los cinco defectos conocidos se detecten y aparezcan otros patrones nuevos en el conjunto
  independiente: significaría que cinco casos no bastaban para diseñarlo.
- Que el validador exija del modelo una precisión que la plantilla no permite —por ejemplo, un
  número de decimales que el prompt no fija—. En ese caso lo que hay que cambiar es la plantilla, no
  la barrera.

### 5.4 Lo que el protocolo no permitirá afirmar

1. **Nada sobre el modelo.** El validador mide y rechaza; no mejora cómo redacta.
2. **Ninguna tasa.** Quince ventanas y dos condiciones describen treinta situaciones.
3. **Que el problema esté resuelto.** Un validador detecta lo que su gramática cubre. Una afirmación
   numéricamente correcta puede seguir siendo engañosa por otras vías —un valor cierto atribuido a
   la señal equivocada en prosa, por ejemplo—, y eso esta propuesta no lo aborda.

## 6. Orden de trabajo, si se aprueba

1. Escribir la gramática de las expresiones numéricas que el recorrido produce hoy: las de
   `missing_evidence` y las de las plantillas de afirmación. **Enumerarlas, no inferirlas.**
2. Implementar V1 con sus seis comprobaciones, con pruebas que incluyan los cinco defectos conocidos
   como casos sintéticos.
3. Medir los dos errores sobre el conjunto independiente, con el criterio de §5.2 ya fijado.
4. Publicar el resultado, sea el que sea, y declarar que el recuento de «salidas válidas» pasa a ser
   más estricto que el de las cifras históricas.
5. **No** reevaluar las salidas publicadas con el validador para dar otra cifra: serían otras
   condiciones. Lo que sí vale es decir cuántas de las históricas no pasarían, que es el 13 de 17 de
   §4, y eso ya está dicho.

## 7. Lo que esta propuesta no hace

- **No modifica ningún resultado histórico.** Los registros de E13, E15, E18, E19 y P1 quedan como
  están.
- **No se aplica retroactivamente.** La corrección es prospectiva, por instrucción.
- **No está implementada.** Este documento es el diseño, y su valor es que fija el criterio **antes**
  de que exista el código, cuando todavía no se puede elegir en función del resultado.
