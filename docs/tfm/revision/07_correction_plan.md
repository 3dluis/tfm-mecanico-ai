# 07 · Plan de corrección consolidado

**Fecha:** 3 de septiembre de 2026 · **Instantánea:** `mecanico-ia-exp` en `af008f9` ·
**Estado:** `CORRECTIONS READY FOR REVIEW`. **No se ha corregido nada.**
**Documentos asociados:** `07a_human_decisions.md` (doce decisiones),
`07b_reexecution_plan.md` (qué se reejecuta y con qué), `07c_claim_impact_matrix.md`
(afirmaciones afectadas y fortalezas en riesgo).

**Pregunta de investigación, bloqueada y sin modificar:**

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una
> hipótesis sin fundamento?

Cada corrección de este plan sirve a uno de sus tres ejes: **explicación**, **trazabilidad**,
**abstención**. Ninguna la reformula.

---

## 1. Reclasificación de severidad

La formulación anterior, «ningún hallazgo bloqueante», era correcta para una sola pregunta
—¿puede el proyecto seguir adelante?— y engañosa para otra. Se sustituye por tres niveles.

| Nivel | Definición | Cómo se levanta |
|---|---|---|
| `BLOQUEA_DESARROLLO` | Impide seguir construyendo el artefacto o ejecutar las fases siguientes | corrigiendo el defecto |
| `BLOQUEA_AFIRMACIÓN` | Una afirmación concreta del documento **no puede sostenerse tal como está escrita** con la evidencia disponible | acotando la afirmación **o** aportando la evidencia que falta |
| `BLOQUEA_DEPÓSITO` | Impide depositar aunque las afirmaciones se acoten, por normativa de la titulación | cumpliendo el requisito |

**Resultado de la reclasificación:**

- `BLOQUEA_DESARROLLO`: **ninguno**. El artefacto funciona, los experimentos se ejecutan y
  las fases siguientes no dependen de ninguna corrección.
- `BLOQUEA_AFIRMACIÓN`: **nueve problemas** (P-01, P-02, P-03, P-04, P-05, P-06, P-08, P-10,
  P-13). Entre ellos están los tres que el autor señaló.
- `BLOQUEA_DEPÓSITO`: **dos** (P-12 por estructura y extensión; P-10 por la norma de fuentes).
- `MAJOR` sin bloqueo de afirmación: **dos** (P-07, P-09) y P-11.

### 1.1 Los tres problemas señalados por el autor

**P-03 · experimento central sobre un solo caso → `BLOQUEA_AFIRMACIÓN`.** Verificado en
`experiments/E15_suficiencia.json`: C05, C06, C07, C08 y C09 comparten `bundle.case_id`
`F01_vacuum_leak__idle__10@120s`. Las condiciones ABSENT, PARTIAL y las dos DISTRACTOR
existen **para un solo fallo**. Impide sostener, tal como están escritas: «PI.3 sostenida»,
«PI.4 sostenida» (`matriz:37-40, 187-196`), «el agente se abstiene cuando se retira la
evidencia y también cuando lo que queda es parecido» (`cap6:17-23`) y la frase equivalente del
resumen. **No impide** sostener el contraste como demostración de mecanismo sobre el caso
evaluado, que es lo que la evidencia sí permite.

**P-06 · defectos de instrumento que alteran cifras → `BLOQUEA_AFIRMACIÓN`.** Tres cifras
publicadas se calculan con código defectuoso. La cobertura de soporte 1,00 incluye al menos
una afirmación cuyo texto contradice el dato que cita; el «9 de 9 respeta el veredicto» se
computa sobre siete salidas. Ambas sostienen conclusiones de PI.2 y de la sección del modelo
de lenguaje. **No impide** el desarrollo: los defectos son locales y con corrección conocida.

**P-08 · solo ventanas correctamente clasificadas → `BLOQUEA_AFIRMACIÓN`.** Verificado en
`sufficiency_runner.py:112`: `np.flatnonzero((validacion.y == fault_id) & aciertos)`. Impide
sostener cualquier afirmación sobre el comportamiento del sistema **cuando el diagnóstico de
entrada es incorrecto**, que es exactamente el escenario que la pregunta teme. La memoria no
hace hoy esa afirmación de forma explícita, pero `cap6:17-23` y el resumen se leen como si el
resultado fuera incondicional. **No impide** el desarrollo.

Ninguna severidad se ha reducido. Dos han subido respecto del informe anterior: P-01 y P-05,
que estaban descritos como problemas de trazabilidad y son también bloqueos de afirmación.

---

## 2. Matriz de problemas por tipo de acción

Tipos: **A** documental · **B** instrumento · **C** experimental · **D** estadístico ·
**E** evidencia y procedencia · **F** estructura UAX · **G** claim e interpretación ·
**H** decisión humana.

| ID | Problema | Severidad | Tipo | ¿Cambia cifras? | ¿Requiere reejecución? | ¿Cambia claims? | Acción propuesta |
|---|---|---|---|---|---|---|---|
| **P-01** | Cinco bloques de cifras sin registro vigente | `BLOQUEA_AFIRMACIÓN` + `BLOQUEA_DEPÓSITO` | A · D · E · H | **Sí**, las cinco | Parcial: `RX-01`, `RX-03`; el resto no | Sí: los que citan esas cifras | Fijar ejecución canónica, regenerar tablas desde el registro, registrar lo no registrado |
| **P-02** | Código de avería tomado de la etiqueta anotada | `BLOQUEA_AFIRMACIÓN` | B · C · G · H | No | No para declarar; `NEW_EXPERIMENT` para la versión no oracular | Sí: el claim de recuperación y el de cobertura de soporte | Etiquetar como cota superior asistida por oráculo; corregir la frase que lo niega |
| **P-03** | Cuatro condiciones sobre un solo fallo | `BLOQUEA_AFIRMACIÓN` | C · G · H | No | No (opción B) / `NEW_EXPERIMENT` (opción A) | Sí: PI.3, PI.4, conclusión y resumen | Acotar el alcance **o** ampliar E17. Ambas opciones en §5 |
| **P-04** | Corrección de E7 no propagada a la memoria | `BLOQUEA_AFIRMACIÓN` | A · G | **Sí** | No: los dos registros existen | Sí: el claim sobre el modelo temporal y sobre F05 | Publicar el resultado canónico vigente y retirar el anterior |
| **P-05** | Métricas verdaderas por construcción | `BLOQUEA_AFIRMACIÓN` | B · G | No | No para reclasificar; `NEW_EXPERIMENT` para el brazo con citas generadas | Sí: la distancia cero como resultado de PI.2 | Reclasificar como invariante o comprobación de implementación |
| **P-06** | Tres defectos de instrumento | `BLOQUEA_AFIRMACIÓN` | B · G | **Sí**, tres cifras | Sí: `RX-01` (A), `RX-02` (B); C no | Sí: cobertura de soporte, respeto al veredicto, comparación de modelos | Corregir código, reejecutar, republicar; declarar la asimetría de selección |
| **P-07** | Umbral sin procedencia registrada | MAJOR | B · D · H | No (verificado: decisiones invariantes en (0,5999, 0,9078]) | No para declarar; `RX-04` opcional | Sí: solo la frase «calibrados, no elegidos» | Declarar heurístico **o** registrar el barrido |
| **P-08** | Solo ventanas bien clasificadas | `BLOQUEA_AFIRMACIÓN` | C · G · H | No | No (opción A) / `NEW_EXPERIMENT` (opción B) | Sí: el alcance de toda conclusión sobre el agente | Declarar la condición **o** experimento adverso. Ambas en §10 |
| **P-09** | Cuatro fuentes de verdad del estado de fases | MAJOR | A · F | No | No | No | Fuente única derivada de artefactos; los demás pasan a vistas generadas |
| **P-10** | Vacío afirmado sin cita; referencias del vacío incompletas | `BLOQUEA_AFIRMACIÓN` + `BLOQUEA_DEPÓSITO` | A · E · G · H | No | No | Sí: la afirmación del vacío de PI.4 | Incorporar y citar las cuatro fuentes; completar metadatos |
| **P-11** | Cadena de procedencia incompleta y canal incorrecto | MAJOR | B · E | No | Sí: `RX-01` (reserializa) | No directamente | Añadir `source_file`, exportar fragmentos, separar editor de canal |
| **P-12** | Estructura y extensión UAX | `BLOQUEA_DEPÓSITO` | F · H | No | No | No | Completar contenido académico faltante; proyección honesta en §16 |
| **P-13** | Novedad del capítulo 1 contradicha por el registro propio | `BLOQUEA_AFIRMACIÓN` | A · G | No | No | Sí: la afirmación de novedad | Propagar a `cap1` la formulación estrecha que `cap3` ya usa |

---

## 3. Corrección frente a reejecución

Clasificación exigida, por problema. El detalle de cada reejecución (script, entrada, semilla,
dataset, modelo, configuración, resultado esperado y artefactos) está en
`07b_reexecution_plan.md`.

| ID | Clasificación | Justificación |
|---|---|---|
| P-01 | `HUMAN_DECISION_REQUIRED` + `RX-01` + `RX-03` | La ejecución canónica es decisión del autor. Dos bloques exigen reejecución: la calibración, que hoy no se escribe en ningún registro, y la medición translingüe, que no tiene artefacto. Los otros tres se corrigen regenerando tablas desde registros existentes: `NO_REEXECUTION` |
| P-02 | `NO_REEXECUTION` (declarar) · `NEW_EXPERIMENT` (versión no oracular) | Declarar el oráculo es documental. Medir sin él exige un experimento nuevo, descrito en §6 |
| P-03 | `NO_REEXECUTION` (opción B) · `NEW_EXPERIMENT` (opción A) | Acotar es documental. Ampliar exige anotar y ejecutar casos nuevos |
| P-04 | `NO_REEXECUTION` | Los dos registros existen y están verificados: `E7_temporal_synthetic_v{2,3}.json` |
| P-05 | `NO_REEXECUTION` (reclasificar) · `NEW_EXPERIMENT` (brazo con citas generadas) | |
| P-06 | `RX-01` (defecto A) · `RX-02` (defecto B) · `NO_REEXECUTION` (defecto C) | A y B cambian la salida del pipeline; C se declara |
| P-07 | `NO_REEXECUTION` (declarar heurístico) · `RX-04` (registrar el barrido) | |
| P-08 | `NO_REEXECUTION` (opción A) · `NEW_EXPERIMENT` (opción B) | |
| P-09 | `NO_REEXECUTION` | Cambio de herramienta, no de resultado |
| P-10 | `NO_REEXECUTION` | Documental y bibliográfico |
| P-11 | `RX-01` | Añadir `source_file` obliga a reserializar los paquetes de evidencia |
| P-12 | `NO_REEXECUTION` | Redacción |
| P-13 | `NO_REEXECUTION` | Documental |

**Cuatro reejecuciones identificadas**, ninguna de ellas un experimento nuevo:
`RX-01` (E15 con instrumento corregido y calibración registrada), `RX-02` (E13 con el respeto
al veredicto corregido), `RX-03` (medición translingüe con registro), `RX-04` (barrido de
umbrales como artefacto, opcional). **Ninguna presupone que el resultado será igual**: cada
una declara qué se espera y qué haría si no coincide.

---

## 4. P-01 · Las cinco cifras, una por una

| # | Documento y línea | Valor publicado | Supuesto origen | Registro canónico disponible | Estado |
|---|---|---|---|---|---|
| 1 | `cap4:95-108`, `E5:51-56` | Suelo de ruido 0,369 / 0,399 / 0,438 / 0,512; a 30 s el mejor descriptor de F05 es la temperatura, **no declarada** | Ejecución de E5 anterior a la recalibración del generador | `tables/E5_estudio_ventana.csv`: 0,326 / 0,365 / 0,426 / 0,513; a 30 s el mejor descriptor es la sonda de oxígeno, **declarada** | **STALE** — el dataset que produjo la cifra fue regenerado y no se conserva bajo ese identificador |
| 2 | `cap5:82-89`, `E12:50-56` | nDCG 0,224 / 0,312 / 0,531 / 0,658; «cinco casos»; Hit 0,25 | Ejecución de E12 sobre 5 casos, sustituida | `experiments/E12_retrieval.json` (`executed_at` 2026-09-01T21:32:01Z, 6 casos): nDCG 0,000 / 0,149 / 0,468 / 0,468 / 0,642; Hit 0,000 / 0,200 / 0,400 / 0,400 / 1,000 | **STALE** — existe registro vigente con otras cifras y otro número de casos |
| 3 | `cap5:94-105` | Translingüe 5/5, 1/5, 4/5, 4/5; medianas 47, 376, 58, 54 | Medición adyacente a E12 | **Ninguno** en `experiments/`, `results/`, `scripts/` ni `notebooks/` | **UNTRACEABLE** |
| 4 | `cap5:64-71` | ECE calibrado 0,085 · confianza 0,886 · acierto 0,878 · sesgo +0,009 | Salida de consola de `sufficiency_runner.py` | El registro citado, `experiments/E15_suficiencia.json`, **no contiene** el bloque | **UNTRACEABLE** |
| 5 | `matriz:67-73` | PI.2: 18 afirmaciones / 12 con cita / 0,667 / 51 comprobaciones / 21 aceptadas | Ejecución anterior de E15 | Recuento sobre `experiments/E15_suficiencia.json`: **27 / 15 / 0,556 / 63 / 27** | **INCORRECT** — el registro vigente da cifras peores para la subpregunta que la propia matriz llama «la más débil» |

**Regla aplicada:** ninguna cifra se sustituye por una parecida. Las `STALE` se regeneran desde
el registro que el autor declare canónico. Las `UNTRACEABLE` se registran (`RX-01`, `RX-03`) o
se retiran del documento hasta tenerlo. La `INCORRECT` se corrige con la cifra del artefacto,
sea cual sea, y se declara el cambio.

**Causa raíz:** ninguno de los quince registros de `experiments/` contiene `commit`; catorce
carecen de `executed_at`; faltan semilla en E12, E13 y E15 y versión de corpus en E15. La
regla está escrita en tres documentos del proyecto y no se cumple. Sin cabecera de
identificación, una sobrescritura es indetectable desde el artefacto. **La corrección de la
causa raíz precede a la de los síntomas.**

---

## 5. P-02 · El oráculo, con precisión

### 5.1 Tres cosas que hay que distinguir

| Concepto | Qué es | Dónde vive en este proyecto |
|---|---|---|
| `GROUND_TRUTH_LABEL` | La condición de fallo con que se generó la sesión y con que se anotó el caso | `fault_id` en `configs/goldset_mazda3_bk.yaml` y en la partición de validación |
| `MODEL_OUTPUT` | La clase que el modelo de diagnóstico predice para la ventana | `modelo.predict(...)` en `sufficiency_runner.py`; **no interviene en E12** |
| `RETRIEVAL_QUERY_INPUT` | Lo que se introduce en la consulta de recuperación | Texto de la consulta **más** los códigos de avería de `DIAGNOSTICO_A_DTC[...]` |

### 5.2 Qué ocurre hoy

`retrieval_runner.py:170` resuelve los códigos con `DIAGNOSTICO_A_DTC.get(str(caso["fault_id"]))`.
El `fault_id` es `GROUND_TRUTH_LABEL`. Por tanto **el `RETRIEVAL_QUERY_INPUT` contiene
información derivada del ground truth**, y en E12 no interviene ningún `MODEL_OUTPUT`.

Lo mismo ocurre aguas abajo: `sufficiency_runner.py:166` pasa `expected_dtc` derivado del
mismo `fault_id` a la verificación de soporte, de modo que la comprobación de si un fragmento
sostiene una afirmación también consume la etiqueta.

`cap4:255` dice «la condición predicha». `E12:93-99` niega expresamente que sea un oráculo.
**Ambas afirmaciones son incorrectas y deben corregirse.**

### 5.3 Qué conclusión permite realmente el experimento

Permitido: *«condicionada a un diagnóstico correcto, la recuperación guiada por los códigos
que el manual asocia a ese diagnóstico encuentra el procedimiento relevante en el 100 % de los
casos anotados, frente al 0 % de la recuperación semántica pura»*. Es un resultado real y
fuerte sobre el **mecanismo de recuperación**: dice que en documentación técnica lo que une
consulta y procedimiento es un identificador exacto, no la similitud semántica.

No permitido: cualquier lectura como rendimiento del sistema extremo a extremo, porque la
cadena diagnóstico → consulta no está cerrada.

**Etiqueta propuesta:** `ORACLE-ASSISTED UPPER BOUND`, declarada en `cap4`, `cap5`, `E12`,
`E15` y en el registro de limitaciones. Con esa etiqueta el experimento **se conserva**: mide
lo que dice medir.

**Matiz verificado que conviene conservar:** la verificación de soporte **discrimina sin el
oráculo**. En C07, con los códigos esperados presentes en los fragmentos, rechaza las doce
comprobaciones por falta de mención de la señal. El oráculo no es lo que separa las
condiciones del experimento central.

### 5.4 Versión no oracular metodológicamente correcta (propuesta, no ejecutada)

```
Para cada ventana de validación:
  1. dtc_predicho = DIAGNOSTICO_A_DTC[ modelo.predict(ventana) ]      # MODEL_OUTPUT
  2. consulta = texto_del_caso + dtc_predicho
  3. recuperar; medir contra los documentos relevantes del fault_id REAL
Reportar por separado:
  - subconjunto con diagnóstico correcto  → debe reproducir la cota superior
  - subconjunto con diagnóstico incorrecto → mide el coste del error aguas arriba
  - agregado                               → rendimiento del sistema extremo a extremo
```

Condición necesaria: el `GROUND_TRUTH_LABEL` solo puede usarse para **evaluar**, nunca para
construir la consulta. Coste estimado: bajo, reutiliza el pipeline. Se enlaza con la opción B
de P-08, con la que comparte casi toda la implementación.

---

## 6. P-03 · Cobertura de la pregunta con la evidencia actual

| Dimensión de la PI | Evidencia actual | Cobertura |
|---|---|---|
| **Explicación** | E13: tres configuraciones sobre 9 casos; la ajustada produce 9/9 salidas válidas, 3 explicaciones con una observación y dos fragmentos por afirmación | 5 ventanas distintas, 4 fallos con condición completa; **suficiente para el mecanismo**, escasa para variabilidad |
| **Trazabilidad** | E15: 27 afirmaciones, 63 comprobaciones, cobertura de soporte 1,00 en las cinco condiciones con evidencia; doble rama reconstruible a nivel de afirmación | Condicionada a diagnóstico correcto (P-08) y a códigos del ground truth (P-02); métrica de distancia invariante (P-05) |
| **Abstención** | E15: 7 de 9 decisiones correctas; cobertura de explicación 3 de 5; contraste completo → ausente con confianza idéntica 0,9078 | **Un solo fallo** con las cuatro condiciones |
| **Variabilidad entre fallos** | 4 fallos en condición completa (C01–C04) y 1 en las cuatro condiciones (C05–C09) | **Insuficiente** para afirmar propiedad general |
| **Variabilidad entre ventanas** | 1 ventana por fallo, elegida como la primera bien clasificada | **Nula**: no hay réplica intra-fallo |

### Opción A · Ampliar los experimentos

Extender E17 a **tres fallos más** con las cuatro condiciones, y a **dos ventanas por fallo**.

- Coste de implementación: anotar entre 12 y 24 casos nuevos en el conjunto anotado
  (`relevant_files`, `exclude_dtc`, `distractor_files`, `expected_action`); el pipeline no
  cambia. Estimación: media jornada de anotación más una ejecución.
- Coste científico: ninguno negativo. Convierte «demostración de mecanismo» en «resultado con
  variabilidad», que es lo que PI.3 y PI.4 necesitan para sostenerse como están escritas.
- Riesgo: los casos nuevos pueden no reproducir el contraste. **Eso sería un resultado**, y
  habría que publicarlo.

### Opción B · Acotar las conclusiones

Reescribir cuatro pasajes (resumen, `cap5:203-212`, `cap6:17-23`, `matriz:187-196`) para decir
lo que la evidencia sostiene: *«en el caso evaluado bajo las cuatro condiciones, la decisión
cambia con la evidencia disponible; en tres de los cinco casos con evidencia completa el
agente explica»*.

- Coste de implementación: bajo, cuatro pasajes.
- Coste científico: la contribución pasa de «propiedad del sistema» a «demostración de
  mecanismo sobre un caso». Sigue respondiendo a la PI, con alcance menor y honesto.
- Riesgo: el tribunal puede preguntar por qué no se amplió, teniendo el pipeline hecho.

**No se decide aquí.** Recomendación en `07a_human_decisions.md`, decisión D-04.

---

## 7. P-04 · El resultado canónico vigente

| | Resultado antiguo (publicado) | Resultado corregido (registrado) |
|---|---|---|
| Experimento | E7, modelo temporal | E7, sensibilidad del propio informe |
| Dataset | `synthetic_v2` | `synthetic_v3` |
| Muestras de validación | 98 ventanas (12 sesiones, 2 por clase) | 343 ventanas (36 sesiones) |
| Métrica | F1 macro | F1 macro |
| Red recurrente | **0,823** | **0,9446** |
| Bosque aleatorio | 0,8788 | 0,9321 |
| Diferencia | −0,056 a favor del bosque | **+0,0125 a favor de la red** |
| F1 del fallo de encendido, red | 0,500 | **0,9111** |
| F1 del fallo de encendido, bosque | 0,6667 | 0,8602 |
| Registro | `experiments/E7_temporal_synthetic_v2.json` | `experiments/E7_temporal_synthetic_v3.json` |

`E7_modelo_temporal.md:88-101` declara «corregida» la conclusión anterior. `cap5:52-62`,
`cap3:82-84`, `cap6:47-49` y la limitación L-15 conservan la lectura antigua.

**Acción:** el documento final usa **únicamente el resultado canónico vigente**, que el autor
debe declarar (decisión D-02). La afirmación anterior no se conserva por razones narrativas;
si se conserva la comparación entre volúmenes de datos, se presenta como lo que es: el orden
entre los dos modelos depende del número de sesiones, y con la evidencia disponible ninguna de
las dos diferencias se ha establecido con réplicas. Estado estadístico: `INCONCLUSIVE`.

---

## 8. P-05 · Métricas verdaderas por construcción

| Métrica | Por qué es invariante | Clasificación propuesta | Destino |
|---|---|---|---|
| «Distancia entre completitud de citación y tasa de soporte = 0» (`cap5:207`) | `assembly.py:176-185`: una afirmación recibe cita solo si pasa la verificación, y se marca sostenida si y solo si tiene cita. La diferencia no puede ser distinta de cero | `INVARIANT` | **Sale de resultados principales.** Pasa a `cap4` como propiedad del diseño del verificador |
| «0 documentos aplicables» en la condición sin evidencia (`cap5:144-145`) | La condición retira los fragmentos con los mismos códigos con que la búsqueda va acotada | `SANITY_CHECK` | **Permanece como control**, declarado como tal: prueba que la exclusión funciona, no que el sistema reaccione |
| Cobertura de soporte 1,00 en las condiciones con evidencia | **No** es invariante: en C07, C08 y C09 la cobertura es 0,00 con documentos aplicables delante | resultado real | **Permanece en resultados** |
| M4 descrita en `cap4:222-225` como calculada de forma determinista | No está implementada; E14 no se ha ejecutado | `PENDING` | **Validación de implementación**: o se implementa y se ejecuta, o `cap4` deja de describirla como calculada |

La lectura que sí sobrevive, y que conviene conservar: el sistema **responde a la pertinencia
y no a la presencia**, porque en PARTIAL y DISTRACTOR hay cuatro documentos aplicables delante
y la cobertura es 0,00. Eso no es invariante: es el resultado.

---

## 9. P-06 · Radio de impacto de los tres defectos

### Defecto A · El signo de la atribución se convierte en aserción sobre el vehículo

| Campo | Contenido |
|---|---|
| **Bug** | `assembly.py:155-160` construye el texto con `sentido = "por encima" if obs.direction == "increases" else "por debajo"`, y `obs.direction` procede del **signo del valor SHAP** (`attribution.py`: «Su signo es la dirección»). El texto resultante afirma que la señal está por encima o por debajo de lo esperable, e imprime a continuación `obs.value`, que es el valor del descriptor y puede tener el signo contrario |
| **Impacto** | Confunde «contribuye positivamente a la predicción» con «la señal es alta». Contradice `docs/methodology/evidence-model.md:42-45`, escrito por el propio proyecto |
| **Artefactos afectados** | `experiments/E15_suficiencia.json` (textos de afirmación), `experiments/E13_agente_*.json` (los textos entran en el prompt y en la salida), `tables/E15_suficiencia.csv` |
| **Métricas afectadas** | Cobertura de soporte y tasa de aceptación de citas: una afirmación con texto incorrecto se contabiliza como sostenida |
| **Resultados publicados afectados** | `cap5:109-113` y `cap5:206-207` (cobertura 1,00 y la lectura de PI.2); los ejemplos de texto de `cap5:164-194` |
| **Ejemplo verificado** | C02, `OBS003`: `value: -1.496284`, `direction: "increases"` → «se sitúa **por encima** de lo esperable, con valor **−1,496**» |
| **Corrección** | Separar las dos nociones: el texto debe decir que el descriptor **contribuye** al diagnóstico en una dirección, y reservar «por encima/por debajo» para cuando se compare con un valor de referencia que el sistema tenga. Alternativa mínima: usar el signo de `obs.value` para el sentido y el signo SHAP para la contribución, en dos frases distintas |
| **Tests de regresión** | Uno que construya una observación con `value` negativo y `direction: increases` y compruebe que el texto no afirma «por encima»; uno que compruebe que el texto de la afirmación no contradice el signo del valor que cita |
| **Experimentos a reejecutar** | `RX-01` (E15) y, en cascada, `RX-02` (E13, porque los textos entran en el prompt) |

### Defecto B · El respeto al veredicto se computa sobre salidas que no existen

| Campo | Contenido |
|---|---|
| **Bug** | `agent.py:110` inicializa `respected_verdict: bool = True`; `agent.py:251` lo actualiza **solo** cuando la salida se ha podido interpretar. Si el esquema falla, el campo conserva `True` |
| **Impacto** | El recuento publicado «respeta el veredicto 9/9» se calcula sobre 7 salidas reales en dos de las tres configuraciones; en los dos casos sin salida no hay veredicto que respetar y se cuentan como respetados |
| **Artefactos afectados** | `experiments/E13_agente_transformers.json`, `..._transformers-lora.json`, `..._transformers-lora@slm_lora_v2.json` y los dos `*_esquema_v1.json` |
| **Métricas afectadas** | «Respeta el veredicto» en las tres configuraciones |
| **Resultados publicados afectados** | `cap5:172-176` (tabla de las tres configuraciones), `E13_agente_slm.md:199-209` y `:246-249` |
| **Corrección** | El campo pasa a tres estados —respetado, no respetado, sin salida— o se inicializa a `False` y se reporta el denominador real. La tabla publica «respeta el veredicto: n de m salidas válidas» |
| **Tests de regresión** | Uno que fuerce un fallo de esquema y compruebe que el campo no queda en `True`; uno que compruebe que el denominador publicado coincide con el número de salidas válidas |
| **Experimentos a reejecutar** | `RX-02` (E13). No exige reentrenar: los adaptadores no cambian |

### Defecto C · Selección de época sobre la partición que se reporta

| Campo | Contenido |
|---|---|
| **Bug** | No es un error de código: `training.py:156-166` restaura la época con mejor F1 macro **de validación**, y la cifra reportada es la F1 macro sobre esa misma validación. El bosque no selecciona nada. La comparación es asimétrica y no está declarada |
| **Impacto** | La cifra de la red recurrente es el máximo de entre 60 a 74 evaluaciones sobre el conjunto que se reporta |
| **Artefactos afectados** | `experiments/E7_temporal_synthetic_v{2,3}.json` (`best_epoch` 19 y 33) |
| **Métricas afectadas** | F1 macro de la red recurrente en validación |
| **Resultados publicados afectados** | `cap5:52-62`; se cruza con P-04 |
| **Dirección del sesgo** | Favorece a la red recurrente. En `synthetic_v2` pierde **a pesar** del sesgo: el resultado negativo es conservador. En `synthetic_v3` gana por 0,0125, margen inferior al sesgo plausible: `INCONCLUSIVE` |
| **Corrección** | Declarar el mecanismo y su dirección en `cap4` y en `E7`. Para sostener cualquier orden entre modelos: selección de época sobre partición interna de entrenamiento y evaluación final sobre test |
| **Tests de regresión** | Ninguno necesario: no es un defecto de implementación |
| **Experimentos a reejecutar** | Ninguno para declarar. Si el autor quiere sostener un orden: reanálisis descrito en `07b`, `RX-05` (opcional) |

---

## 10. P-07 · El umbral, con precisión

| Pregunta | Respuesta verificada |
|---|---|
| ¿Qué umbral existe? | `min_confidence = 0.80` en `src/mecanico_ia_exp/abstention/sufficiency.py:62`. Los otros cinco umbrales del criterio no tienen calibración |
| ¿Dónde se definió? | En el propio valor por defecto de la clase, con un docstring que contiene la tabla del barrido |
| ¿Con qué datos? | 98 ventanas de la partición de **validación** de `synthetic_v2` |
| ¿En qué partición? | Validación. **El test no se usó**: `load_partition("test")` lanza excepción y ningún ejecutor la abre. Verificado |
| ¿Con qué criterio? | «El umbral más bajo con precisión ≥ 0,93». El criterio **no consta en ningún documento anterior al barrido** |
| ¿Registro del barrido? | **No existe.** La tabla vive en el docstring y en el informe de fase; no hay script ni artefacto |
| ¿Acoplamiento? | El barrido corre sobre la misma partición de la que `sufficiency_runner.py:110-116` extrae los nueve casos evaluados |

**Conclusión honesta:** con la evidencia disponible, el umbral está **definido
heurísticamente**, no calibrado. La frase «los umbrales están calibrados, no elegidos»
(`cap5:123-125`, `E15:213-227`) no puede mantenerse tal como está.

**Dato que acota el riesgo, verificado:** las nueve decisiones de E15 son idénticas para
cualquier umbral en el intervalo (0,5999, 0,9078]. El resultado del experimento **no depende
del umbral**. Lo que no se sostiene es la palabra «calibrado».

**Procedimiento correcto si se quiere calibrar (propuesto, no ejecutado):** `RX-04` en `07b`.
Condiciones innegociables: criterio escrito y fechado **antes** de leer la tabla; barrido
registrado como artefacto con precisión y cobertura por ventana **y por sesión**; **nunca usar
el conjunto de test** para seleccionar el umbral.

---

## 11. P-08 · El escenario adverso

`sufficiency_runner.py:110-119` selecciona, por fallo, la primera ventana de validación que el
modelo clasifica correctamente. Lo mismo hacen `xai_runner.py:50-56` y `training_runner.py:71-78`.

La pregunta que la evidencia actual responde es: *¿puede explicar y abstenerse **cuando el
diagnóstico de entrada es correcto**?* La que no responde: *¿qué ocurre cuando el modelo se
equivoca y el sistema recupera evidencia coherente con el diagnóstico equivocado?* Ese es el
caso que produce una explicación bien citada y falsa, que es el fallo que el trabajo estudia.

### Opción A · Alcance acotado

Declarar que el trabajo estudia **explicación y abstención condicionadas a un diagnóstico
especializado correcto**, en `cap4`, `cap5`, `cap6` y en el registro de limitaciones.

- Esfuerzo: bajo. Cuatro declaraciones.
- Valor científico: conserva lo demostrado y delimita honestamente. La contribución sigue
  siendo válida: la trazabilidad y la abstención se miden sobre la evidencia documental, que
  es donde se manipula la variable.
- Efecto sobre la PI: la respuesta queda condicionada; PI.2, PI.3 y PI.4 se responden dentro
  de esa condición.

### Opción B · Experimento adverso

Seleccionar ventanas **mal clasificadas** por el modelo y comprobar si la recuperación y el
verificador impiden construir una explicación aparentemente respaldada alrededor del
diagnóstico equivocado.

- Esfuerzo: medio. La selección se invierte en una línea; hay que anotar qué se espera para
  cada caso adverso (probablemente abstención por baja confianza o por cobertura) y decidir el
  criterio de éxito **antes** de ejecutar.
- Valor científico: **alto**. Es el experimento que convierte la pregunta en falsable en su
  parte más difícil, y el que un tribunal pedirá.
- Efecto sobre la PI: responde a la pregunta en su formulación completa, sin condición.
- Riesgo declarado: es plausible que el sistema **falle** en ese escenario. Sería un resultado
  publicable y coherente con el trabajo.
- Sinergia: comparte casi toda la implementación con la versión no oracular de P-02 (§5.4).

**No se decide aquí.** Decisión D-08.

---

## 12. P-09 · Fuente única de verdad del estado de fases

Hoy conviven cuatro: `docs/experiments/README.md`, `docs/plan_experimental_macbook.md`,
`research/traceability-matrix.md` y `research/objective-coverage.md`, más lo que declara
`cap2:93-96`. Dan hasta cuatro estados distintos para la misma fase.

**Propuesta:** el estado se **deriva de los artefactos**, no se mantiene a mano.

```
estado(fase) = f(informe en docs/experiments/, registro en experiments/, tests que la cubren)
  cerrada    : informe + registro + tests en verde
  ejecutada  : registro sin informe propio         → se declara dónde se documenta
  pendiente  : ni informe ni registro
  bloqueada  : declarada así en un ADR o en una decisión abierta
```

Un script en `scripts/` genera una tabla y la escribe en un fichero marcado como **vista
generada, no editable a mano**. `README.md`, el plan, la matriz y la cobertura pasan a
incluir esa vista en lugar de mantener su propia copia. El gate de calidad comprueba que la
vista está al día.

Coste: bajo. Evita que las cuatro fuentes vuelvan a divergir mañana, que es la objeción
correcta del autor a una corrección manual.

---

## 13. P-10 y P-13 · Vacío y novedad, tratados juntos

**Regla que se adopta:** ninguna afirmación de novedad absoluta. La forma admitida es
*«en los trabajos analizados no se identificó…»*, y **cada afirmación del vacío debe llevar la
evidencia de la revisión que la sostiene**. La integración tecnológica no cuenta como novedad
científica: que el sistema combine recuperación, verificación y abstención no es, por sí
mismo, una contribución.

| Dónde | Qué dice hoy | Qué dice el registro propio | Acción |
|---|---|---|---|
| `cap1:54-57` | Afirmación de novedad sobre PI.4 | L-10 y el registro de búsqueda declaran la hipótesis de vacío **refutada**: la capacidad está estudiada, con banco público y vocabulario establecido | Propagar a `cap1` la formulación estrecha que `cap3:214-219` ya usa |
| `cap3:213-218` | «Existen trabajos sobre robustez de la recuperación a documentos irrelevantes en dominios generales» | Cuatro obras verificadas en el registro de búsqueda, **ninguna citada ni en la bibliografía** | Incorporarlas a la lista maestra y a la bibliografía, y citarlas en ese pasaje |
| Bibliografía | REF-049 y REF-106, las dos referencias del vacío, con título parafraseado o truncado, «et al.» por autores y sin identificador | Los registros externos devuelven los metadatos completos | Completar; decisión D-07 |
| Lista maestra | REF-051 sin título de obra ni identificador; no localizada en los registros consultados | Actas no consultadas | Consultar la fuente o retirarla. **No se declara inventada** |

La formulación del vacío que sí se sostiene, y que conviene conservar, es la estrecha: en los
trabajos analizados no se identificó una evaluación del rechazo de evidencia no pertinente en
diagnóstico vehicular a partir de telemetría, con verificación a nivel de afirmación
individual, doble rama de evidencia y la abstención tratada como salida medida.

---

## 14. P-11 · Cadena de procedencia

**Cadena esperada:**

```
claim → chunk → document → document_version → source file → hash → acquisition source
```

**Dónde termina hoy:** la serialización de la evidencia documental
(`evidence/model.py:127-140`) conserva `chunk_id`, `document_id`, `vehicle_id`, `score`,
`applicability`, `authority_level`, `document_type`, `publisher`, `section`, `page_start` y
`page_end`. **No conserva `source_file`.** Los fragmentos no están exportados
(`corpus/vehicles/mazda-3-bk-2007/chunks/` está vacío) y los registros de ingesta viven en la
base de datos, que no está versionada. La cadena se corta en `document`.

**Modificación propuesta:** añadir `source_file` y `document_version_id` a la serialización;
exportar los fragmentos citados por los casos anotados, o versionar el registro de ingesta con
su hash; declarar en `cap4` dónde termina la cadena y por qué (el binario del manual no se
redistribuye).

**Editor frente a canal de adquisición.** El manifiesto ya los distingue:
`publisher: Mazda Motor Corporation`, `acquisition_source: copia local del autor, origen web
de terceros`, `acquisition_channel: SECONDARY_REPOSITORY`. Pero el mismo bloque declara
`source_url: https://www.mazdatechinfo.com/`, el portal oficial del fabricante, que **no es**
el canal por el que se adquirió. Toda cita hereda esa URL.

**Corrección:** `source_url` debe describir el canal real de adquisición o quedar vacío con la
razón; el portal oficial puede figurar como `publisher_url`, claramente separado. No se
atribuye al fabricante una URL que no es la de origen del ejemplar utilizado.

---

## 15. P-12 · Estructura y extensión, sin relleno

**Regla:** no se escribe texto para alcanzar una cifra. Primero se identifica qué contenido
académico falta, y la extensión es su consecuencia.

### Contenido académico que falta de verdad

| Elemento | Estado | Por qué falta |
|---|---|---|
| Abstract y palabras clave en inglés | **ausente** | La plantilla lo exige |
| Palabras clave en español | 7 donde se piden 5 | |
| Justificación **personal** (cap. 1) | ausente | La plantilla la pide expresamente |
| Recorrido OE1 → … → OE5 → OG en conclusiones | ausente | La plantilla fija ese orden y el grado de cumplimiento por objetivo |
| Etiquetado de paradigma, tipo y alcance temporal (cap. 4) | ausente | La plantilla lo pide con esas palabras |
| Decisión registrada sobre el método de investigación | ausente | Se usa el ciclo de ciencias del diseño sin ADR que lo fije |
| Detalle experimental por fase en la memoria | disperso en `docs/experiments/` | El capítulo 4 resume; el detalle reproducible debería estar en anexo |
| Discusión frente a los trabajos revisados | mínima | El capítulo 5 discute resultados propios, no los compara con los trabajos del capítulo 3 |
| Anexo A: objetivos aprobados ↔ reformulados | ausente | Comprometido por el propio proyecto |
| Anexo de reproducibilidad | ausente | Permitido y útil |

### Proyección honesta de extensión

| Capítulo | Palabras hoy | Falta por incorporar | Proyección | Recomendado por la plantilla |
|---|---|---|---|---|
| Resumen y abstract | 331 | abstract, keywords, recorte a 300 | ≈ 700 | — |
| 1 Introducción | 1 278 | justificación personal, contexto | 2 000–2 500 | 5–10 pág. |
| 2 Objetivos | 924 | correspondencia con lo aprobado | 1 000–1 200 | 1–3 pág. |
| 3 Marco teórico | 2 365 | dos apartados marcados, cuatro fuentes del vacío, síntesis comparativa | 5 000–6 500 | 10–20 pág. |
| 4 Marco metodológico | 2 984 | etiquetado, procedencia, declaraciones de condición, análisis | 4 500–5 500 | 5–15 pág. |
| 5 Resultados y discusión | 1 948 | cifras corregidas, discusión frente a los trabajos revisados | 4 000–5 000 | 5–15 pág. |
| 6 Conclusiones | 1 284 | recorrido por objetivos, consideraciones finales | 2 500–3 000 | 5–10 pág. |
| Bibliografía | 1 076 | referencias nuevas | 1 400 | — |
| Anexos | 0 | A objetivos, B reproducibilidad, C fichas de experimento | 3 000–5 000 | ≤ 20 % |
| **Total** | **12 550** | | **24 000–31 000** | ≈ 60–78 páginas |

Con contenido real, el documento llega a unas 60–78 páginas sin relleno. **Queda por debajo de
las 50 000 palabras** que la nota al pie de la plantilla menciona, y esa contradicción entre
documentos oficiales es la decisión D-01. La proyección no incluye ninguna página escrita para
cubrir expediente.

---

## 16. Prioridad del plan

Se adopta el orden propuesto por el autor, con una precisión dentro del grupo 1.

| Grupo | Contenido | Justificación |
|---|---|---|
| **1 · Integridad del instrumento** | **P-06**, P-05, P-07 | Ninguna cifra debe regenerarse antes de que el instrumento que la produce sea correcto: si se regeneran las tablas y luego se corrige la plantilla de afirmaciones, hay que regenerarlas dos veces. **Precisión:** dentro del grupo 1, la causa raíz de P-01 —la cabecera de identificación de los registros— se implementa **aquí**, no en el grupo 3, porque `RX-01` y `RX-02` deben escribir ya registros identificables |
| **2 · Validez experimental** | P-02, P-03, P-08 | Declarar condiciones y decidir alcance antes de tocar la redacción de resultados |
| **3 · Integridad de resultados** | P-01, P-04, P-09 | Ya con el instrumento corregido y las condiciones declaradas, se regeneran las cifras desde los registros canónicos |
| **4 · Evidencia científica** | P-10, P-11, P-13 | |
| **5 · Documento UAX** | P-12 | Al final, cuando el contenido está fijado |

Justificación del único cambio: mover la cabecera de identificación de registros del grupo 3 al
grupo 1 evita reejecutar dos veces y hace auditable cada reejecución desde la primera.

---

## 17. Protección de las fortalezas

Las 65 fortalezas verificadas quedan protegidas. Se aplica `PRESERVE > PATCH > REWRITE`. La
lista de qué fortaleza podría verse afectada por cada corrección está en
`07c_claim_impact_matrix.md` §3. Resumen de las que exigen cuidado:

| Corrección | Fortaleza en riesgo | Cómo se protege |
|---|---|---|
| P-06A, plantilla de afirmaciones | «Las afirmaciones no atribuyen causa» y el rechazo de frases causales | El cambio afecta al sentido de la magnitud, no a la prohibición de causalidad. El test de frases causales se conserva intacto |
| P-01, regeneración de tablas | «Trece resultados negativos conservados» | Se regeneran también los negativos; ninguno se retira |
| P-03 opción B, acotar | «Refutadores enumerados de antemano» | Acotar el alcance no toca la lista de desenlaces que refutarían la pregunta |
| P-05, sacar la distancia de resultados | «Doble trazabilidad verificada a nivel de afirmación» | La doble trazabilidad se sostiene con la cobertura, que no es invariante |
| P-12, ampliar capítulos | «Ninguna afirmación de significación estadística» y «cero adjetivación vacía» | El texto nuevo pasa por las mismas reglas; la autenticidad se audita después |

Ninguna corrección exige reescritura general. Las secciones marcadas `PRESERVE` en
`01_tutor_findings.md` no se tocan.

---

## 18. Lo que no se hace en esta fase

No se modifica la memoria, no se cambian resultados ni umbrales, no se reentrena, no se
reescriben capítulos, no se ejecutan experimentos, no se humaniza, no se ejecuta el jurado
final ni el entrenamiento de defensa. Nada de lo anterior está en marcha.

---

`CORRECTIONS READY FOR REVIEW`
