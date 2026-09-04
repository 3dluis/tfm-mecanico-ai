# 07 · Plan de corrección consolidado

**Fecha:** 3 de septiembre de 2026 · **Instantánea:** `mecanico-ia-exp` en `1162d1e`
(las auditorías fijaron su veredicto entre `8d55def` y `a6a5f40`; los avances intermedios
solo añaden ficheros de revisión y no tocan las unidades evaluadas) · **Estado:** STOP
GATE 1, pendiente de aprobación del autor. **No se ha corregido nada.**

## 1. Veredicto agregado

| Auditoría | Veredicto | CRITICAL | MAJOR | MINOR | INFO | Score |
|---|---|---|---|---|---|---|
| Académica (tutor UAX) | `FAIL` | 0 | 13 | 17 | 12 | 55/99 |
| RAG, evidencia y abstención | `FAIL` | 0 | 11 | 10 | 9 | 56/100 |
| Experimentos | `FAIL` | 0 | 12 | 11 | 14 | 60/100 |
| Evidencia (78 claims) | `FAIL` | 0 | 11 | 7 | 13 | 62/100 |
| Estadística | `BLOCKED` | 0 | 5 | 7 | 8 | — |
| Referencias (179 fichas) | `BLOCKED` | 0 | 4 | 13 | 5 | — |
| **Total** | — | **0** | **56** | **65** | **61** | — |

**Ningún BLOCKER.** Los 56 `MAJOR` se reducen a **trece problemas raíz**: la mayoría de los
identificadores son el mismo defecto visto por seis instrumentos distintos.

**Ninguna corrección exige reejecutar E5, E6, E7, E9 ni E15**, salvo dos reejecuciones de
registro que no cambian resultados (escribir la calibración; registrar el barrido de
umbrales).

## 2. Los trece problemas raíz

Ordenados por prioridad de corrección (§35 del encargo: evidencia → diseño → estadística →
referencias → coherencia → estructura UAX). `AD` = decisión del autor requerida.

### P-01 · Cifras publicadas que el artefacto vigente no reproduce · **evidencia**

**Identificadores:** TUTOR-MAJ-001, TUTOR-MAJ-003, TUTOR-MAJ-006 · RAG-MAJ-001, RAG-MAJ-002,
RAG-MAJ-004 · EXP-MAJ-001, EXP-MAJ-012, EXP-MAJ-017, EXP-MAJ-030 · EVID-MAJ-004,
EVID-MAJ-013, EVID-MAJ-014, EVID-MAJ-018, EVID-MAJ-019 · STAT-MAJ-001, STAT-MAJ-006,
STAT-MAJ-008, STAT-MIN-013.

Cinco bloques de cifras vivas en la memoria no proceden de ningún registro vigente:

| Cifra | Dónde se publica | Qué dice el artefacto |
|---|---|---|
| Suelo de ruido 0,369 / 0,399 / 0,438 / 0,512 y el ejemplo de la ventana | `cap4:95-108`, `E5:51-56` | `tables/E5_estudio_ventana.csv`: 0,326 / 0,365 / 0,426 / 0,513; a 30 s el mejor descriptor de F05 es la sonda de oxígeno, **declarada**, no la temperatura |
| Tabla de recuperación (nDCG 0,224 / 0,312 / 0,531 / 0,658) | `cap5:82-89`, `E12:50-56` | `experiments/E12_retrieval.json`: 0,0 / 0,149 / 0,468 / 0,642, sobre 6 casos, no 5; ocho celdas difieren |
| Tabla translingüe (5/5, 1/5, 4/5, 4/5) | `cap5:94-105` | sin registro en `experiments/`, `results/`, `scripts/` ni `notebooks/` |
| ECE calibrado 0,085 · confianza 0,886 · sesgo +0,009 | `cap5:64-71`, citando `E15_suficiencia.json` | el runner lo imprime en consola y **no lo escribe** en el JSON |
| PI.2: 18 afirmaciones / 12 con cita / 0,667 / 51 / 21 | `matriz:67-73` | recuento sobre `E15_suficiencia.json`: **27 / 15 / 0,556 / 63 / 27** |

El último es el más delicado: las cifras publicadas **favorecen a la subpregunta que la
propia matriz llama «la más débil»**. No hay indicio de manipulación (proceden de una
ejecución anterior), pero la corrección debe hacerse con la cifra del artefacto sea cual sea.

**Causa raíz técnica:** EXP-MAJ-013 — ninguno de los quince registros de `experiments/`
contiene `commit`; catorce carecen de `executed_at`; faltan semilla en E12, E13 y E15 y
versión de corpus en E15. Por eso las sobrescrituras fueron indetectables desde el artefacto,
pese a que la regla está escrita en tres documentos del propio proyecto.

**Corrección:** (a) `AD` fijar la ejecución canónica de E5, E6, E7 y E12; (b) regenerar las
tablas de `cap4`, `cap5`, la matriz y los informes de fase desde el registro elegido, citando
el JSON y no el Markdown; (c) registrar la medición translingüe o retirarla del capítulo;
(d) reejecutar E15 escribiendo el bloque de calibración en su registro; (e) añadir `commit`,
`executed_at`, semilla y versiones a la cabecera de todos los registros. **Riesgo:** medio.
Cambian cifras publicadas; la lectura cualitativa se mantiene en los cinco casos.

### P-02 · El código de avería procede de la etiqueta anotada, no del diagnóstico · **diseño**

**Identificadores:** TUTOR-MAJ-002 · RAG-MAJ-003 · EXP-MAJ-014 · EVID-MAJ-003.

`retrieval_runner.py:170` y `sufficiency_runner.py:166` resuelven los códigos con
`caso["fault_id"]`, la etiqueta del conjunto anotado. Con ellos se acota la búsqueda **y** se
decide si un fragmento sostiene una afirmación. `cap4:255` dice «la condición predicha» y
`E12:93-99` niega expresamente que sea un oráculo. En E12 no interviene ningún modelo.

Consecuencia: el salto de Hit@10 de 0,00 a 1,00 es una **cota superior** condicionada a un
diagnóstico correcto, y la cobertura de soporte 1,00 de PI.2 lo es también.

**Matiz que sostiene el diseño:** la verificación de soporte **discrimina sin el oráculo**;
en C07 rechaza las doce comprobaciones por falta de mención de la señal aunque los fragmentos
llevan el código esperado. El oráculo no es lo que separa las condiciones.

**Corrección:** declarar el oráculo en `cap4`, `E12`, `E15` y en el registro de limitaciones,
corrigiendo la frase que lo niega; `AD` decidir si además se mide la recuperación guiada con
las predicciones del modelo en E18 o E19. **Riesgo:** bajo si se declara; alto si se deja como
está y lo encuentra el tribunal.

### P-03 · El experimento central se evalúa sobre un solo caso · **diseño**

**Identificadores:** TUTOR-MAJ-010 · EXP-MAJ-018 · EVID-MAJ-002 · STAT-MIN-010.

C05 a C09 comparten `case_id` (`F01_vacuum_leak__idle__10@120s`): ABSENT, PARTIAL y las dos
variantes de DISTRACTOR existen para **un único fallo**. «Nueve casos» son cinco ventanas
distintas. La matriz declara PI.3 y PI.4 «Sostenidas» y `cap6:17-23` concluye «sí puede» sin
declarar ese tamaño.

El trabajo acota la procedencia sintética en cinco documentos y **no acota el n en ninguno**.

**Corrección:** acotar el alcance en resumen, `cap5`, `cap6` y matriz («en el caso evaluado
bajo las cuatro condiciones»; «en tres de los cinco casos con evidencia»), o `AD` extender
E17 a más fallos por condición. **Riesgo:** bajo. Es la corrección más barata y la de mayor
efecto en defensa.

### P-04 · Una corrección registrada por el proyecto no llega a la memoria · **evidencia**

**Identificadores:** TUTOR-MAJ-004 · EVID-MAJ-015 · STAT-MAJ-005.

`E7_modelo_temporal.md:88-101` registra que con `synthetic_v3` el F1 del fallo de encendido
pasa de 0,518 a 0,911 y la red recurrente deja de ser inferior (0,9446 frente a 0,9321 del
bosque), y declara «corregida» la conclusión anterior. `cap5:52-62`, `cap3:82-84`, `cap6:47-49`
y L-15 conservan la lectura antigua. Clasificado `CONTRADICTION_HIDDEN`.

**Corrección:** reescribir la lectura de E7 como inconcluso con las dos cifras y la
sensibilidad, o `AD` ejecutar el reanálisis apareado por sesión con varias semillas.
**Riesgo:** bajo; mejora la honestidad del capítulo. Ninguna conclusión de la PI depende de
esto: el bosque sigue siendo el modelo del experimento por decisión declarada.

### P-05 · Métricas que no pueden tomar otro valor · **evidencia y diseño**

**Identificadores:** RAG-MAJ-011 · EVID-MAJ-001 · RAG-MAJ-017.

(a) «La distancia entre completitud y soporte es cero» (`cap5:207`) es cero **por
construcción**: `assembly.py:176-185` da cita a una afirmación solo si pasa la verificación,
y la marca sostenida si y solo si tiene cita. La métrica central de PI.2 no puede dar otra
cosa. Además M4 se describe en `cap4` como calculada y no está implementada (E14 pendiente).

(b) La condición ABSENT retira los fragmentos con los mismos códigos con que la búsqueda va
acotada: «0 documentos aplicables» está garantizado por construcción.

**Corrección:** reformular ambas como propiedades del diseño, no como resultados medidos, o
`AD` introducir un brazo con citas generadas por el modelo para que la distancia pueda ser
distinta de cero. **Riesgo:** medio. Afecta a cómo se presenta PI.2, no a que la trazabilidad
funcione.

### P-06 · Tres defectos de instrumento que alteran cifras publicadas · **evidencia**

**Identificadores:** RAG-MAJ-012 · RAG-MAJ-013 · EXP-MAJ-003.

| Defecto | Dónde | Efecto |
|---|---|---|
| La plantilla de afirmación traduce el **signo del valor SHAP** en una aserción sobre el vehículo | `assembly.py:156-160` con `attribution.py:51-52` | Contraejemplo en el registro: C02/`OBS003`, valor −1,496 con `direction: increases`, redactado «se sitúa **por encima** de lo esperable, con valor −1,496», contado como sostenido y sumado a la cobertura 1,00. Contradice `evidence-model.md:42-45`, escrito por el propio proyecto |
| `respected_verdict` se inicializa a `True` y no se actualiza si la salida falla el esquema | `agent.py:110, 231-248` | «9/9 respeta el veredicto» se calcula sobre 7 salidas; en los dos casos sin salida la lectura real es 0/2 |
| La red recurrente elige la mejor época por F1 de **validación** y se reporta sobre esa misma validación; el bosque no selecciona nada | `training.py:150-176` | Comparación asimétrica. El sesgo favorece a la red y aun así pierde en v2: el negativo es conservador |

**Corrección:** corregir la plantilla para que el texto respete el signo; corregir el cálculo
del respeto al veredicto y republicar la cifra; declarar la asimetría de selección de época.
**Riesgo:** bajo en esfuerzo, alto si no se corrige: son tres cifras o frases que un tribunal
puede refutar abriendo un fichero.

### P-07 · El umbral 0,80 no tiene procedencia registrada · **estadística**

**Identificadores:** TUTOR-MAJ-005 · EXP-MAJ-016 · STAT-MAJ-007.

El criterio «precisión ≥ 0,93» no consta en ningún documento anterior al barrido; el barrido
corre sobre la misma partición de la que salen los nueve casos; no existe script ni registro:
la tabla vive en un docstring. Además «los umbrales están calibrados, no elegidos» es cierto
para uno de seis: cuatro no tienen calibración.

**Dato que reduce el riesgo:** las nueve decisiones son **idénticas para cualquier umbral en
(0,5999, 0,9078]**, verificado. El resultado no depende del umbral; lo que no se sostiene es
la frase.

**Corrección:** `AD` registrar el barrido como artefacto con criterio fechado, **o** declarar
0,80 como elección de política y retirar «calibrados, no elegidos». **Riesgo:** bajo.

### P-08 · Solo se evalúan ventanas bien clasificadas · **diseño**

**Identificadores:** RAG-MAJ-010 · EXP-MAJ-015.

`sufficiency_runner.py:112` selecciona, por fallo, la primera ventana que el modelo clasifica
correctamente. El escenario que la PI teme —diagnóstico erróneo, evidencia recuperada para el
diagnóstico erróneo, explicación bien citada y falsa— **nunca se pone a prueba**. `cap4:143-147`
declara la selección; ningún documento declara su consecuencia.

**Corrección:** declarar la consecuencia en `cap4`, `cap5` y limitaciones; `AD` incluir en E19
al menos un caso con diagnóstico incorrecto. **Riesgo:** medio; es una pregunta previsible del
tribunal.

### P-09 · Estado de las fases incoherente entre artefactos · **coherencia**

**Identificadores:** TUTOR-MAJ-007 · TUTOR-MAJ-011 · EXP-MAJ-019.

`cap2:93-96` declara cerradas E8, E14 y E16 y ejecutada E17; ninguna tiene informe ni
registro propio, y cuatro artefactos dan cuatro estados distintos. La matriz de trazabilidad y
la cobertura de objetivos están congeladas el 1 de septiembre: doce fases figuran «pendiente»
teniendo informe, y las columnas de resultados dicen «PENDING por diseño: no hay resultados».

**Corrección:** unificar el estado de fases en un solo sitio y derivar los demás; regenerar
matriz y cobertura; escribir el informe de E17 o declararlo integrado en E15. **Riesgo:** bajo.

### P-10 · Referencias del vacío incompletas y afirmación sin cita · **referencias**

**Identificadores:** TUTOR-MAJ-013 · REF-MAJ-001, REF-MAJ-002, REF-MAJ-011, REF-MAJ-012.

- `cap3:213-218` afirma que existen trabajos sobre robustez de la recuperación a documentos
  irrelevantes —el pasaje que estrecha el vacío de PI.4— **sin citar ninguno**, cuando las
  cuatro obras que lo documentan están verificadas en el registro de búsqueda del proyecto y
  no figuran en la bibliografía.
- REF-049 y REF-106, las dos referencias del vacío, existen y el registro devuelve sus
  metadatos completos, pero las entradas las identifican con título parafraseado o truncado,
  «et al.» en el campo de autor y sin identificador.
- REF-051 es la única de las 144 cuya existencia no se ha podido confirmar (actas no
  consultadas). Queda `UNVERIFIED`, **no** «inventada».
- Siete entradas de la bibliografía de depósito llevan marcadores pendientes.

**Contexto que conviene no perder:** cero referencias inexistentes, cero identificadores
rotos, cero que resuelvan a otra obra y cero discrepancias de título, autor o publicación en
las 137 fichas con registro externo. La norma con sanción de no apto no está incumplida.

**Corrección:** incorporar y citar las cuatro fuentes del vacío; completar REF-049 y REF-106;
consultar las actas de REF-051 o retirarla; resolver los marcadores. `AD` APA 6.ª frente a
7.ª. **Riesgo:** bajo en esfuerzo, alto en consecuencia normativa si no se cierra.

### P-11 · Trazabilidad documental incompleta y canal de procedencia incorrecto · **evidencia**

**Identificadores:** RAG-MAJ-014 · RAG-MAJ-015.

La evidencia serializada no conserva `source_file`, los fragmentos no están exportados y las
ingestas viven solo en la base de datos no versionada: la cadena hasta el fichero de origen no
se puede reconstruir desde los artefactos. Y toda cita lleva un `source_url` que apunta a un
canal que el propio proyecto documenta como **no siendo** el de adquisición.

**Corrección:** añadir `source_file` a la serialización; exportar los fragmentos citados o
versionar el registro de ingesta; corregir el `source_url` del manifiesto; `AD` decidir si se
readquiere el manual por el canal oficial antes del depósito. **Riesgo:** medio.

### P-12 · Estructura UAX incompleta · **estructura**

**Identificadores:** TUTOR-MAJ-008, TUTOR-MAJ-009, TUTOR-MAJ-012.

El capítulo 6 no recorre OE1 → … → OE5 → OG con grado de cumplimiento, como exige la
plantilla; no existe abstract ni palabras clave en inglés y hay siete palabras clave donde se
piden cinco; el capítulo 4 no etiqueta paradigma, tipo ni alcance temporal, que la plantilla
pide con esas palabras, y el ciclo de investigación en ciencias del diseño se usa sin decisión
registrada que lo fije.

**Corrección:** reescribir el capítulo 6 en el orden de la plantilla tras cerrar resultados;
escribir abstract y recortar palabras clave; etiquetar el marco metodológico; registrar la
decisión sobre el método. **Riesgo:** bajo, pero condiciona el gate de cumplimiento.

### P-13 · Afirmación de novedad contradicha por el propio registro · **evidencia**

**Identificador:** EVID-MAJ-016.

`cap1:54-57` mantiene la afirmación de novedad sobre PI.4 que el registro de búsqueda y la
limitación L-10 del propio proyecto declaran refutada. `cap3:214-219` sí lleva la corrección;
`cap1` no.

**Corrección:** propagar a `cap1` la formulación estrecha que `cap3` ya usa. **Riesgo:** bajo.

## 3. Decisiones que corresponden al autor

Ninguna la toma esta revisión. Ordenadas por lo que bloquean.

| # | Decisión | Bloquea | Origen |
|---|---|---|---|
| 1 | **Extensión del TFM**: 12 550 palabras ≈ 31 páginas frente al mínimo de 60 páginas del curso vigente, con «no apto» aparejado; tres cifras oficiales incompatibles | el cronograma completo | tutor, `conflictos-uax.md` |
| 2 | **Ejecución canónica** de E5, E6, E7 y E12; qué se hace con `synthetic_v1` y `synthetic_v3` | P-01, P-04 | los seis |
| 3 | **Oráculo del código de avería**: declararlo como cota superior o sustituirlo y reejecutar E12 | P-02 | RAG, experimentos, tutor, evidencia |
| 4 | **Alcance de PI.3 y PI.4**: acotar el n o extender E17 | P-03 | tutor, experimentos, evidencia |
| 5 | **Umbral 0,80**: registrar el barrido con criterio fechado o declararlo política | P-07 | estadística, experimentos, tutor |
| 6 | **Objetivos y título** con el director; los tres `[CONSENSUAR]` abiertos y el Anexo A | GATE-03, capítulo 2 | tutor |
| 7 | **APA 6.ª frente a 7.ª**; metadatos de REF-049 y REF-106; consultar o retirar REF-051 | P-10, GATE-10 | referencias |
| 8 | **Caso adverso con diagnóstico incorrecto** en E19 | P-08 | RAG, experimentos |
| 9 | **M6**: criterio o descriptiva; **congelación del pre-registro** canónico | GATE-04 | tutor, experimentos |
| 10 | **Convocatoria** y **declaración del uso de herramientas de asistencia** registradas en `research/available-skills.md` | depósito | tutor |
| 11 | **Re-adquisición del manual** por el canal oficial antes del depósito | P-11 | RAG |
| 12 | **Distancia completitud/soporte**: propiedad de diseño o brazo con citas generadas | P-05 | RAG, evidencia |

## 4. Conflictos entre auditorías

| ID | Skill A | Skill B | Discrepancia | Decisión |
|---|---|---|---|---|
| CONFLICT-01 | estadística (`STAT-MAJ-007`, MAJOR) | RAG (mismo hecho, MINOR) | Severidad del umbral sin procedencia. El evaluador RAG lo baja porque `cap5:3-5` declara que todas las cifras son de validación | Se conserva **MAJOR**: la frase «calibrados, no elegidos» es la que no se sostiene, y vive en la memoria. Ambas lecturas quedan registradas |
| CONFLICT-02 | evidencia (`STAT-MIN-013` elevado a MAJOR) | estadística (MINOR) | Gravedad de las cifras obsoletas de la matriz | Se trata dentro de **P-01**, con la severidad más alta |
| CONFLICT-03 | encargo §3 | sistema de ficheros | `Tfm-tutor` no existe; `tfm-defense-coach` sí (instalado durante la revisión) | Orquestación asumida por esta revisión; la fase 5 usará el coach |

Ninguno afecta a la pregunta de investigación, la metodología, las hipótesis, los resultados
ni las conclusiones. Ninguno requiere decisión humana previa a la corrección.

## 5. Lo que se conserva sin tocar (PRESERVE)

Con motivo, según el tutor y las auditorías especializadas:

- `cap4:26-114` población y muestra, `cap4:116-139` corpus, `cap4:174-201` variables e
  instrumentos: coinciden con sus registros y con el diseño ejecutado.
- `cap5:121-162` y `cap5:164-194` (suficiencia y modelo de lenguaje): coinciden con
  `E15_suficiencia.json` y `E13_agente_*.json` campo a campo.
- `cap1:101-111`: la advertencia de procedencia sintética, repetida y correcta.
- `cap5:47-50`: el marcador `[RECONCILIAR]`, que es el proyecto detectando su propio problema.
- `cap6:32-101`: las diecisiete limitaciones, todas con evidencia y ninguna ceremonial.
- `docs/methodology/` completo.
- `configs/goldset_mazda3_bk.yaml` con `tests/test_retrieval_eval.py:195-207`.

## 6. Fortalezas verificadas que la corrección no debe dañar

Sesenta y cinco entre las seis auditorías. Las que un tribunal reconocería:

- **El contraste central funciona y está bien construido.** En `tables/E15_suficiencia.csv`,
  C05 a C09 comparten caso, ventana y confianza calibrada 0,9078, y solo cambia el corpus. En
  PARTIAL y DISTRACTOR hay cuatro documentos aplicables delante y la cobertura es 0,00: el
  sistema responde a la **pertinencia**, no a la presencia.
- **La verificación de soporte discrimina sin el oráculo:** en C07 rechaza las doce
  comprobaciones por falta de mención de la señal aunque los fragmentos llevan el código
  esperado.
- **Cero citas inexistentes** en 63 ejecuciones verificadas contra el contexto entregado, y la
  barrera se comprueba fuera del modelo.
- **El auditor de particiones se prueba provocando la fuga**; el test está cerrado por código
  y ningún ejecutor lo abre.
- **La condición ABSENT se auditó y estaba mal construida** (16 fragmentos frente a 70): se
  rehízo por código y la lectura correcta está escrita.
- **Trece resultados negativos conservados** con su consecuencia; una afirmación falsa tachada
  en cuatro informes en lugar de borrada; una fase cerrada con el corpus vacío y declarada así.
- **Ninguna afirmación de significación estadística en todo el corpus documental**, y ninguna
  prueba ritual: los doce análisis obtienen `NO_TEST_NEEDED` con razón.
- **Cero referencias inexistentes y cero identificadores rotos** en las 137 fichas con registro
  externo.
- **PostgreSQL con pgvector se presenta como instrumento**, no como contribución (`cap4:16`,
  `cap4:249-253`).
- **Ningún resultado sintético se presenta como comportamiento en vehículo real**: declarado
  en `cap5:3-8`, `cap6:25-30` y `matriz:199-206`.
- **De los doce claims críticos, cinco sostenidos y siete parcialmente sostenidos**; ninguno
  sin sostener, contradicho ni inverificable.

## 7. Orden de ejecución propuesto para la segunda pasada

Si el autor aprueba, y respetando `PRESERVE > PATCH > REWRITE`:

1. **Registros y ejecución canónica** (P-01, causa raíz EXP-MAJ-013): cabecera de tracking,
   decisión de ejecución canónica, regeneración de tablas desde los registros.
2. **Defectos de instrumento** (P-06): signo en la plantilla, respeto al veredicto,
   asimetría de selección de época.
3. **Declaraciones de diseño** (P-02, P-05, P-08): oráculo, métricas por construcción,
   selección de ventanas correctas.
4. **Alcance de las afirmaciones** (P-03, P-04, P-13): n de las condiciones, corrección de
   E7, novedad de PI.4.
5. **Estadística** (P-07): umbral.
6. **Referencias** (P-10).
7. **Coherencia de estado** (P-09) y **estructura UAX** (P-12).

Después: STOP GATE 2 con las seis auditorías repetidas, y solo entonces autenticidad, jurado
y defensa.
