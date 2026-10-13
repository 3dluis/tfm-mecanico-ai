# P1 — La condición con distractor, rediseñada y medida

**Fecha de ejecución:** 13 de octubre de 2026 · **Estado:** **ejecutada y cerrada** ·
**Protocolo:** [`protocolo-distractor-v2.md`](../methodology/protocolo-distractor-v2.md), congelado
antes de medir · **Modo:** oracular, política v2.1 · **Partición:** validación ·
**Qué no toca:** el conjunto anotado de E19, cuya huella sigue siendo `7fadc49fc7daaad1`

## 1. El resultado, primero

| Caso | Condición | Esperado | Decidido | Confianza | Docs aplicables | Cobertura | Motivo |
|---|---|---|---|---|---|---|---|
| `P01_vacuum_leak_partial_v2` | PARTIAL | ABSTAIN | **ABSTAIN** ✓ | 0,908 | 4 | 0,00 | cobertura baja |
| `D01_vacuum_leak_distractor_v2` | DISTRACTOR | ABSTAIN | **ABSTAIN** ✓ | 0,908 | 5 | 0,00 | cobertura baja |
| `P02_thermostat_partial_v2` | PARTIAL | ABSTAIN | **ABSTAIN** ✓ | 1,000 | 4 | 0,00 | cobertura baja |
| `D02_thermostat_distractor_v2` | DISTRACTOR | ABSTAIN | **ABSTAIN** ✓ | 1,000 | 7 | 0,00 | cobertura baja |
| `P03_o2_partial_v2` | PARTIAL | ABSTAIN | **ABSTAIN** ✓ | 1,000 | 5 | 0,00 | cobertura baja |
| `D03_o2_distractor_v2` | DISTRACTOR | ABSTAIN | **ABSTAIN** ✓ | 1,000 | 6 | 0,00 | cobertura baja |

**Seis ejecuciones, seis abstenciones. Y son seis ejecuciones de tres casos**, no seis
observaciones: cada caso con distractor se compara con su condición parcial sobre **la misma ventana
de telemetría**, de modo que las dos filas de cada par comparten datos, modelo, atribución y
confianza. **Las unidades son tres**, y el recuento se publica así para que nadie lea 6/6 como una
tasa sobre seis situaciones independientes.

Y lo que importa más que el recuento: **el motivo registrado en los seis es `LOW_CLAIM_COVERAGE`** —la evidencia no sostiene ninguna afirmación— y **no** la baja confianza del
modelo. Las confianzas son 0,908 y 1,000, todas **por encima** del umbral de 0,79.

Eso es exactamente lo que el protocolo declaró de antemano que apoyaría `PI.4`:

> «Qué resultado apoyaría PI.4: que el sistema se abstenga en los tres, y que el motivo registrado
> sea la insuficiencia de la evidencia y no la baja confianza del modelo. Si se abstiene por
> confianza baja, la condición no habrá medido el rechazo de evidencia impertinente: habrá medido
> otra vez la puerta de confianza.»

La puerta de confianza **no intervino**. El rechazo lo hizo la verificación de soporte.

## 2. Que el distractor llegara, comprobado antes de ver ningún veredicto

`scripts/comprobar_distractor_v2.py` ejecuta **solo recuperación**: sin verificador, sin paquete de
evidencia y sin modelo de lenguaje. Se ejecutó primero, y su salida está en el registro de la
ejecución.

| Par | `D-1` ¿llega el distractor? | `D-2` diferencia simétrica | Qué entra solo en la condición con distractor |
|---|---|---|---|
| `D01` ↔ `P01` | **SÍ**, 1 fragmento de `B3E010200102T10` | **2 fragmentos** | el *self-test* KOEO/KOER |
| `D02` ↔ `P02` | **SÍ**, 1 de `B3E010200102T08` y 2 de `node_S07_0000` | **3** | el modo de prueba y el esquema de cableado |
| `D03` ↔ `P03` | **SÍ**, 1 de `node_S07_0000` | **1** | el esquema de cableado |

**Y el distractor no solo llega: se clasifica `EXACT_MATCH`.** Eso es la prueba dura. El filtro de
motor no lo bloquea —es del motor correcto— y el validador de aplicabilidad **no lo degrada**
—lleva el código del fallo—. Llega al verificador como evidencia de primera clase:

| Caso | Documentos aplicables | De ellos, distractores |
|---|---|---|
| `D01` | 5 | **1** |
| `D02` | 7 | **3** |
| `D03` | 6 | **1** |

De modo que la condición **sí mide ahora lo que dice medir**, a diferencia de la versión anterior.

## 3. Qué línea de defensa actuó, y es la respuesta de fondo

Las dos primeras no sirvieron, y eso es información:

| Línea | ¿Actuó? | Por qué |
|---|---|---|
| Filtro de motor en la recuperación | **no** | el distractor es del motor correcto. No tiene nada que objetar |
| Validador de aplicabilidad | **no** | el distractor lleva el DTC del fallo. Lo marca `EXACT_MATCH` |
| **Verificación de soporte** | **sí** | ningún fragmento del distractor **menciona la señal observada con el vocabulario del manual ni es contenido diagnóstico del código**. Cobertura de afirmaciones: 0,00 |

**La conclusión que esto permite, y solo esta:** frente a evidencia del vehículo correcto, con el
código correcto y bien puntuada, lo que impide que el sistema explique es que **el fragmento no
habla de lo que se afirma**. Ni la procedencia ni el código bastan; hace falta que el texto sostenga
la frase. Es la pieza que E15 llamó «citar no es sostener», y aquí se mide contra un adversario
construido para engañar a las otras dos.

**La conclusión que esto NO permite:** nada sobre una tasa. Son tres situaciones construidas por el
autor, con `n = 3`. No se estima ninguna probabilidad de rechazo.

## 4. La redacción: ¿cita el informe el distractor como si lo sostuviera?

El protocolo lo pregunta y la respuesta es **no**, en los tres casos. Con el adaptador congelado
`slm_lora_v2`:

| | Resultado |
|---|---|
| Salidas válidas | 6/6 |
| Respetan el veredicto | 6/6 |
| Citas inventadas | 0 |
| Fallos de esquema | 0 |
| **Menciona algún fragmento del distractor** | **ninguno, en los tres** |

Las seis salidas son abstenciones limpias, sin referencia a los documentos de alcance equivocado.

## 5. Un hallazgo que no se buscaba: el redactor altera cifras

En `D01` la salida del redactor dice:

```
verificador:  "cobertura 0.00 < 0.80"
redactor:     "cobertura 0.908 < 0.80"
```

La frase es **internamente falsa**: 0,908 no es menor que 0,80. El número escrito es la **confianza
calibrada**, no la cobertura. Y **las tres barreras del trabajo la dejan pasar**: esquema válido,
veredicto respetado, cero citas inventadas.

Al auditar los registros ya publicados con `scripts/auditar_cifras_redactadas.py`, **no es un caso
aislado ni es nuevo**:

| Registro | Casos | Con cifra alterada |
|---|---|---|
| E13 · modelo base, sin adaptador | 17 | **0** |
| E13 · adaptador v1 | 17 | **1** (`C01_maf_drift`) |
| **E13 · adaptador v2, el canónico** | 17 | **3** (`C01_maf_drift`, `C07_partial`, `C08_distractor`) |
| P1 · adaptador v2 | 6 | **1** (`D01`) |

Y los tres de la ejecución canónica son los que sostienen el «17/17 válidas · 17/17 respetan el
veredicto · 0 citas inventadas» publicado:

| Caso | Verificador | Redactor | Qué está mal |
|---|---|---|---|
| `C01_maf_drift` | `confianza 0.600 < 0.79` | `confianza 0.60 < 0.80` | **el umbral**: 0,79 escrito como 0,80 |
| `C07_partial` | `cobertura 0.00 < 0.80` | `cobertura 0.908 < 0.80` | **la cifra**, y la frase queda falsa |
| `C08_distractor` | ídem | ídem | ídem |

### Qué significa, con cuidado

**Lo que sostiene:** una salida puede ser **trazable en sus citas y falsa en sus cifras**. Las
barreras comprueban que el identificador citado se entregara; **ninguna comprueba que el número
dicho sea el que el criterio produjo**. Es un hueco en la trazabilidad —`PI.2`— que no estaba
declarado, y afecta a la parte del texto que un lector usaría para juzgar la decisión.

**Lo que no sostiene:** que el adaptador empeore al redactar cifras. La diferencia —0 de 17 en el
modelo base frente a 3 de 17 con el adaptador v2— es sugerente y el número de casos no permite
afirmarla. Con 17 casos, 0 frente a 3 es compatible con el azar del muestreo.

**Lo que no se hace:** añadir una barrera al recorrido. Hacerlo ahora sería cambiar el sistema a la
vista del resultado. Queda como recomendación y como limitación declarada (`L-26`), y la auditoría
queda en un guion para que cualquiera la repita.

## 6. Las ocho comprobaciones previas, una a una

| # | Qué exigía | Resultado |
|---|---|---|
| 1 | Verificar `D-1`…`D-4` | **hecho antes de medir**, con una ejecución de solo recuperación. Los cuatro se cumplen en los tres pares |
| 2 | El candidato cumple las condiciones técnicas del motor Z6/ZJ | **comprobado al medir**: con el filtro de motor **activo**, los distractores llegan al verificador. Si no fueran del motor correcto, no llegarían |
| 3 | `C12` y `C16` no reutilizan configuraciones equivalentes | **no se usan.** Los casos nuevos tienen identificadores propios y exclusiones **medidamente distintas** de su parcial: diferencia simétrica 2, 3 y 1 |
| 4 | El distractor es técnicamente plausible | declarado por escrito en el conjunto anotado, documento a documento, con su sección y su sistema |
| 5 | No se eligió por producir resultados favorables | los tres candidatos están fijados en el protocolo, fechado **antes**; la comprobación previa no observó ningún veredicto |
| 6 | No modifica el conjunto anotado de E19 | **huella `7fadc49fc7daaad1`, sin cambios.** Los casos nuevos van en un fichero nuevo |
| 7 | Identificadores y artefactos nuevos | `P01`…`P03`, `D01`…`D03`; artefactos con etiqueta `distractor_v2` y `distractor_v2_redaccion` |
| 8 | Registrar huellas y configuración | la sección 8 |

## 7. Una ambigüedad del protocolo congelado, declarada en lugar de resuelta en silencio

El protocolo enumera **tres** casos nuevos y, en la misma sección, define una condición `PARTIAL`
**distinta de la canónica**: la del conjunto de E19 no excluye los documentos de alcance equivocado.
Sin esa `PARTIAL` de referencia, el mecanismo del protocolo no se puede ejecutar: `C11` y `C12`
excluían lo mismo, y repetir esa exclusión habría reproducido el defecto que P1 corrige.

Se añadieron por tanto **tres casos `PARTIAL`** con identificadores propios, `P01`…`P03`. **Los tres
casos con distractor, sus distractores y su razón declarada de insuficiencia son los que el
protocolo fijó antes de medir**; lo añadido es su referencia de comparación. La ambigüedad queda
escrita aquí y en el encabezado del conjunto anotado.

## 8. Estado controlado y huellas

| Pieza | Huella SHA-256 (16) |
|---|---|
| `configs/goldset_mazda3_bk_distractor_v2.yaml` | `aff8de27ecda62e1` |
| `configs/goldset_mazda3_bk.yaml` (**sin cambios**) | `7fadc49fc7daaad1` |
| `experiments/E15_suficiencia_distractor_v2.json` | `ae25da2a69356e43` |
| `experiments/E15_suficiencia_distractor_v2_redaccion.json` | `f524d276043e72b5` |
| `experiments/E13_agente_transformers-lora@slm_lora_v2_distractor_v2_redaccion.json` | `e8561000390e5b49` |
| `tables/E15_suficiencia_distractor_v2.csv` | `7074d0ef2376afe8` |
| `models/slm_lora_v2/adapter_model.safetensors` | `e6fccee67dc370bd` |

**Configuración:** commit `3281758`, conjunto `synthetic_v2`, partición validación, modo oracular,
política de suficiencia v2.1, umbrales sin cambios desde el 4 de septiembre
(`min_confidence 0.79`, `min_supporting_chunks 2`, `min_claim_coverage 0.80`,
`accepted_applicability ["EXACT_MATCH"]`), espacio vectorial
`paraphrase-multilingual-MiniLM-L12-v2`, redactor `transformers-lora@slm_lora_v2`.

**Cómo se reproduce:**

```bash
uv run python scripts/comprobar_distractor_v2.py
uv run mecanico-exp sufficiency --goldset goldset_mazda3_bk_distractor_v2.yaml \
  --etiqueta distractor_v2 --mode oracle
uv run mecanico-exp sufficiency --goldset goldset_mazda3_bk_distractor_v2.yaml \
  --etiqueta distractor_v2_redaccion --mode oracle --llm transformers-lora@slm_lora_v2
uv run python scripts/auditar_cifras_redactadas.py
```

## 9. Qué cierra y qué no

**Cierra** el pendiente P1: la condición con distractor vuelve a ser una condición real, con su
requisito de alcanzabilidad comprobado antes de medir y su resultado publicado.

**No cierra, y no debe presentarse como cerrado:**

1. **Los resultados históricos de la condición v1 no se recalculan.** Conservan su etiqueta
   `DISTRACTOR_V1_INVALID_AS_INDEPENDENT_CONDITION` y la corrección del diagnóstico: la causa no era
   el filtro de motor, era que dos condiciones tenían la misma configuración.
2. **E19 no se reabre.** Su conjunto anotado excluye las seis condiciones con distractor, y esa
   exclusión sigue siendo correcta.
3. **`n = 3` no es una estimación, y 6/6 tampoco.** Tres situaciones construidas, recorridas en seis
   ejecuciones. No se publica ninguna tasa, ningún intervalo y ninguna comparación con las cifras de
   E15 o de E19. El resultado **se limita a los casos evaluados**.
4. **La condición sin filtro de motor sigue como estaba.** `C09`, `C13` y `C17` miden la última
   línea de defensa con el filtro desactivado y siguen siendo válidas.
5. **El hueco de las cifras queda abierto.** Declarado, medido y sin corregir, por decisión: se
   corrige después de la entrega o no se corrige, pero no a la vista de este resultado.
