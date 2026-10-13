# Impacto de L-26 sobre E13 y sobre el «17/17 válidas»

**Fecha:** 13 de octubre de 2026 · **Qué es:** el análisis de impacto que el encargo pide, con las
cifras medidas · **Qué NO es:** una modificación de ningún resultado. **Los registros de E13 y de P1
no se tocan** · **Reproducible con:** `uv run python scripts/auditar_cifras_redactadas.py`

## 1. El hallazgo, delimitado

El redactor escribe números en dos sitios, y falla en los dos de maneras distintas:

```
en una ABSTENCIÓN:
   verificador:  "cobertura 0.00 < 0.80"
   redactor:     "cobertura 0.908 < 0.80"      ← 0,908 es la CONFIANZA, no la cobertura
                                                 y la frase es internamente falsa

en una AFIRMACIÓN de una explicación:
   observación OBS001:  oxygen_sensor · delta_max = 0.083801
   redactor:            "...presenta un delta_max de 0.08381..."   ← dígitos corrompidos
```

El segundo caso es el grave y no se había visto hasta ahora. **La afirmación cita el identificador
correcto** —`OBS001`— y **corrompe el valor que cita**. No es un redondeo: 0,083801 redondeado a
cinco decimales es 0,08380, no 0,08381.

## 2. Lo medido, configuración por configuración

| Configuración | Abstenciones con cifra ajena | Afirmaciones con cifra ajena | Salidas con defecto |
|---|---|---|---|
| Modelo base, sin adaptador | **0 de 14** | **0 de 2** | **0** |
| Adaptador v1 | 1 de 8 | 0 de 9 | 1 |
| **Adaptador v2, el canónico** | **3 de 14** | **2 de 9** | **5** |
| Adaptador v2 sobre los casos de P1 | 1 de 6 | — (ninguna explicación) | 1 |

**Detalle del canónico, que es el que sostiene las cifras publicadas:**

| Caso | Dónde | Lo que escribió | Lo que debía decir |
|---|---|---|---|
| `C01_maf_drift` | abstención | `confianza 0.60 < 0.80` | `confianza 0.600 < 0.79` — **el umbral está mal** |
| `C03_o2_slow_response` | afirmación `C01` | `delta_max de 0.08381` | 0,083801 — **dígitos corrompidos** |
| `C03_o2_slow_response` | afirmación `C02` | `std ... 0.02871` | 0,028741 — ídem |
| `C07_partial` | abstención | `cobertura 0.908 < 0.80` | `cobertura 0.00 < 0.80` — **cifra sustituida; frase falsa** |
| `C08_distractor` | abstención | ídem | ídem |

## 3. Qué le hace esto al «17/17 válidas»

La cifra publicada es: **17 de 17 salidas válidas · 17 de 17 respetan el veredicto · 0 citas
inventadas · 0 fallos de esquema**.

### Lo que sigue siendo cierto, sin matices

| Afirmación | Sigue en pie | Por qué |
|---|---|---|
| **17 de 17 salidas válidas** | **sí** | «válida» significa que cumple el esquema de salida. Las diecisiete lo cumplen |
| **17 de 17 respetan el veredicto** | **sí** | la decisión escrita coincide con la que el modelo recibió en la entrada, en las diecisiete |
| **0 citas inventadas** | **sí** | ninguna salida cita un identificador documental que no se le hubiera entregado. Lo garantiza una barrera externa, no el ajuste |
| **0 fallos de esquema** | **sí** | — |

**Ninguna de las cuatro cifras se retira ni se recalcula.** Miden lo que miden, y lo miden bien.

### Lo que ya no se puede afirmar con ellas

| Lectura que había que corregir | Por qué |
|---|---|
| «La salida del redactor es fiable» | **5 de 23 salidas** del adaptador canónico contienen al menos una cifra que no sale de los datos que recibió |
| «El esquema válido garantiza una explicación correcta» | una salida con esquema válido puede contener una comparación numérica **falsa** —«0.908 < 0.80»— y pasar las tres barreras |
| «La trazabilidad de las afirmaciones está verificada» | está verificada **en los identificadores**: la cita existe y se entregó. **No** en los valores: dos afirmaciones citan la observación correcta y escriben mal su número |
| «Las barreras cubren la calidad de la explicación» | cubren la existencia de la cita y la coherencia de la decisión. **Ninguna mira los números** |

### La redacción que esto exige

> **17 de 17 salidas válidas, 17 de 17 respetando el veredicto y cero citas inventadas**, medido con
> el adaptador canónico sobre los diecisiete casos anotados. «Válida» significa que la salida cumple
> el esquema y que su decisión coincide con la del verificador; **no** significa que su contenido
> numérico sea correcto: cinco de las veintitrés salidas de esa configuración contienen al menos una
> cifra que no procede de los datos que el modelo recibió, y las tres barreras no lo detectan
> (`L-26`).

## 4. Qué parte de la respuesta a la pregunta de investigación queda afectada

| Subpregunta | Afectada | Cómo |
|---|---|---|
| **PI.1** diagnóstico, calibración, atribución | **no** | el redactor no diagnostica |
| **PI.2** trazabilidad | **sí, y es el daño principal** | la cadena «afirmación → observación → fragmento» está verificada en sus **enlaces** y no en sus **valores**. Un lector que compruebe el identificador lo encontrará; si comprueba el número, en dos casos de nueve no coincidirá |
| **PI.3** reconocimiento de insuficiencia | **no la decisión; sí su explicación** | la decisión la toma un criterio determinista sin modelo de lenguaje y no está afectada. El **motivo escrito** sí: tres de catorce abstenciones lo justifican con una cifra que el verificador no produjo |
| **PI.4** rechazo de evidencia impertinente | **no** | P1 se decide con el verificador; su única salida afectada es la justificación escrita de `D01` |

**Lo que NO cambia, y conviene decirlo con la misma claridad:** ninguna decisión del sistema es
distinta por este defecto. Las 17 de E15, las 68 de E19 y las 6 de P1 las toma un criterio
determinista que no usa el modelo de lenguaje. **El defecto está en el texto, no en la decisión.**

Y eso es exactamente lo que el hallazgo demuestra, en una forma que vale como resultado:
**una decisión correcta no garantiza una explicación correcta.** Es la separación entre decidir y
redactar vista por su lado incómodo: al aislar la decisión del modelo de lenguaje, el trabajo
protegió la parte que importaba y dejó sin proteger la que el usuario lee.

## 5. Qué se corrige en lo publicado, y qué no

| Documento | Qué se hace |
|---|---|
| `docs/experiments/E13_agente_slm.md` | ya lleva la nota del 13-10-2026; se **amplía** con las dos afirmaciones de `C03` y con el recuento de 5 de 23 |
| `docs/limitations.md` · `L-26` | se **amplía**: no es solo el campo de motivos, también el valor de las afirmaciones |
| `docs/experiment-index.md` | la fila de E13 remite a este análisis |
| `docs/memoria/cap5_resultados.md` · Tabla 5.7 | entrada `A-2` de la matriz de impacto; la cifra no cambia, cambia lo que se afirma con ella |
| `docs/memoria/cap6_conclusiones.md` · OE4 | entrada `A-5`: «no cita nada que no se le haya entregado» es cierto e **incompleto** |
| **Los registros `experiments/E13_*.json` y los de P1** | **no se tocan.** Son la evidencia de lo que ocurrió |
| **Las cifras de validez de salida** | **no se recalculan.** Recalcularlas exigiría otro adaptador, y entonces serían otras cifras |

## 6. Lo que este análisis no permite afirmar

1. **Que el ajuste empeore la fidelidad numérica.** El contraste es sugerente —0 de 16 salidas del
   modelo base frente a 5 de 23 del adaptador canónico— y **el número de casos no lo sostiene**. Con
   estos tamaños, la diferencia es compatible con el azar del muestreo. Para afirmarlo haría falta
   una medición diseñada para eso, sobre el conjunto de evaluación independiente que está congelado.
2. **Que el defecto afecte al 22 % de las salidas** en ningún sentido poblacional. Cinco de
   veintitrés describe veintitrés salidas sobre cinco ventanas de telemetría.
3. **Que el mecanismo del fallo esté establecido.** Los dos patrones observados —sustituir una
   magnitud por otra y corromper dígitos— son los típicos de un modelo de lenguaje copiando números,
   y aquí solo están **descritos**, no explicados.
4. **Que un validador numérico lo resolvería.** La propuesta está en
   [`propuesta-validador-numerico.md`](../methodology/propuesta-validador-numerico.md) y **no se ha
   evaluado**: es una propuesta con su protocolo, no un resultado.
