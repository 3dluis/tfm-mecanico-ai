# CORPUS_MANIFEST — corpus recuperable de Mecánico IA

**Entregable E9.** Registro de procedencia, base legal de uso, versión y suma de
verificación de cada documento del corpus, más los parámetros de troceado y las variantes
de disponibilidad de evidencia. Generado por `tools/build_corpus.py`; **no se edita a mano**.

Versión: `corpus-v2` · construido el 2026-08-27 · **27 documentos · 457 chunks · 55259 palabras**

## 1. Para qué existe este corpus

El corpus es el cuerpo de evidencia contra el que se comprueba si una explicación
diagnóstica está sostenida (PI v4). Su disponibilidad es la **variable independiente**
del experimento central: retirar de él la documentación del mecanismo evaluado es lo que
construye la condición de evidencia insuficiente.

**Regla anti-circularidad.** Los documentos se organizan por subsistema, sensor, PID y
procedimiento, nunca por modo de fallo. Ningún documento lleva `failure_mode` en sus
metadatos y varios mecanismos comparten documento causal, de modo que recuperar el
documento correcto no equivale a acertar el diagnóstico. El conjunto de evidencia de
referencia por mecanismo vive en el manifiesto de congelación, no en el corpus: **el
corpus no contiene la clave de respuestas**.

**Regla E-RAG.** C-A no describe los mecanismos de las clases held-out declaradas en
`ai-models/configs/heldout-exclusions.yaml`. Lo verifica `tools/contamination_audit.py`.

## 2. Parámetros de troceado

| Parámetro | Valor |
|---|---|
| `target_words` | 110 |
| `min_words` | 35 |
| `overlap_sentences` | 1 |

Troceado por agregación de frases hasta el objetivo de palabras, sin partir frases, con
solape de una frase entre chunks contiguos. Determinista: el mismo árbol de fuentes
produce los mismos chunks y los mismos hashes.

## 3. Capa externa — extractos con revisión fijada

Licencia **CC BY-SA 4.0**, que exige atribución y compartir igual. Cada documento conserva
su licencia propia; el corpus no relicencia nada. Fijar el identificador de revisión
(`oldid`) hace el corpus reproducible aunque el artículo cambie después, y el texto
utilizado queda versionado en `external/`.

| Documento | Título | Idioma | Revisión | Fecha | Palabras | Papel |
|---|---|---|---|---|---|---|
| `ext-afr` | Air–fuel ratio | en | `1340937611` | 2026-02-28 | 2572 | C-A |
| `ext-catalytic` | Catalytic converter | en | `1365087910` | 2026-07-20 | 4968 | C-A |
| `ext-cooling` | Internal combustion engine cooling | en | `1336264001` | 2026-02-02 | 3313 | C-A |
| `ext-ecu` | Engine control unit | en | `1358409209` | 2026-06-08 | 478 | C-A |
| `ext-fuel-injection` | Fuel injection | en | `1369000043` | 2026-08-12 | 2675 | C-A |
| `ext-ignition` | Ignition system | en | `1361712538` | 2026-06-29 | 1155 | C-A |
| `ext-maf-sensor-en` | Mass flow sensor | en | `1333957196` | 2026-01-20 | 1775 | C-A |
| `ext-maf-sensor-es` | Caudalímetro | es | `174758446` | 2026-08-08 | 1948 | C-A |
| `ext-manifold-vacuum` | Manifold vacuum | en | `1307643522` | 2025-08-24 | 2077 | C-A |
| `ext-misfire` | Engine knocking | en | `1370218820` | 2026-08-19 | 2121 | C-A |
| `ext-o2-sensor-en` | Oxygen sensor | en | `1364056551` | 2026-07-14 | 3949 | C-A |
| `ext-o2-sensor-es` | Sonda lambda | es | `157369538` | 2024-01-18 | 2336 | C-A |
| `ext-obd2-pids` | OBD-II PIDs | en | `1365659996` | 2026-07-23 | 2473 | C-A |
| `ext-obd2-standard` | On-board diagnostics | en | `1369860855` | 2026-08-17 | 5504 | C-A |
| `ext-rsv-bateria` | Automotive battery | en | `1368475389` | 2026-08-09 | 2621 | reserva (relleno y distractor CN3) |
| `ext-rsv-dpf` | Diesel particulate filter | en | `1366051825` | 2026-07-26 | 3146 | reserva (relleno y distractor CN3) |
| `ext-rsv-frenos` | Disc brake | en | `1366973960` | 2026-07-31 | 7752 | reserva (relleno y distractor CN3) |
| `ext-rsv-neumatico` | Tire | en | `1371065220` | 2026-08-24 | 9111 | reserva (relleno y distractor CN3) |
| `ext-rsv-transmision` | Automatic transmission | en | `1366048532` | 2026-07-26 | 4077 | reserva (relleno y distractor CN3) |
| `ext-rsv-turbo` | Turbocharger | en | `1367362685` | 2026-08-02 | 2565 | reserva (relleno y distractor CN3) |
| `ext-thermostat-en` | Thermostat | en | `1368094202` | 2026-08-07 | 4852 | C-A |
| `ext-thermostat-es` | Termostato | es | `165900503` | 2025-03-06 | 1480 | C-A |

URL completa de cada artículo en `external/provenance.json`.

## 4. Capa propia — procedimientos e interpretación de observables

Obra propia del proyecto, licencia **CC-BY-4.0**. Redactada a partir de las convenciones
J1979 de los PID, del comportamiento del lazo cerrado de combustible y de las firmas que
el emulador del proyecto reproduce efectivamente
(`obd-lab/src/obd_lab/injection/faults.py`). No contiene texto de manuales propietarios.

| Documento | Título | Chunks | sha256 |
|---|---|---|---|
| `own-admision-estanqueidad` | Comprobación de la estanqueidad del circuito de admisión | 2 | `c558eecae94db821…` |
| `own-combustion-irregular` | Detección de combustión irregular por variación instantánea del régimen | 2 | `096a8b732c690785…` |
| `own-dtc-y-sintoma` | Los códigos de diagnóstico identifican síntomas, no causas | 2 | `bff1313647efb2bf…` |
| `own-lambda-dinamica` | Respuesta dinámica de la sonda de oxígeno y efecto de su envejecimiento | 2 | `153036e3e0f6e547…` |
| `own-maf-verificacion` | Contraste del flujo de aire medido frente al esperado por régimen y carga | 2 | `90f0d21ac311e3e8…` |
| `own-mezcla-pobre-diferencial` | Diagnóstico diferencial de una desviación positiva sostenida de los ajustes | 2 | `945d0cdde3818660…` |
| `own-normalidad-y-contexto` | Qué aspecto tiene el funcionamiento normal y por qué el contexto condiciona la lectura | 2 | `62757745cb2ca2e1…` |
| `own-refrigeracion-dinamica` | Dinámica térmica del circuito de refrigeración y su lectura por PID | 2 | `d76fd6cc8131cb26…` |
| `own-trims-fundamentos` | Ajustes de combustible: definición, signo y constantes de tiempo | 3 | `1f7bb62aad0826b2…` |
| `own-trims-por-regimen` | Comparación de los ajustes entre ralentí y régimen sostenido | 2 | `5a9e05d13aebc6dc…` |
| `own-ventanas-y-estadisticos` | Agregación de PID en ventanas: qué significa cada estadístico | 2 | `f2947f50d56ef205…` |

## 5. Variantes de disponibilidad de evidencia

Construidas por exclusión declarada en `mechanisms.yaml`. **Todas tienen exactamente el
mismo número de chunks que C-A**: la diferencia se compensa con documentos de la reserva,
de modo que la exclusión no sea detectable por el tamaño del corpus — mitigación de la
amenaza a la validez nº 5 del diseño experimental.

| Variante | Escenario | Chunks | Docs retirados | Relleno | sha256 |
|---|---|---|---|---|---|
| `corpus-CA` | A (suficiente) | 457 | 0 | 0 | `a1c211d56f410ecf…` |
| `corpus-CB-maf_drift` | B (ausente) | 457 | 5 | 2 | `28c141ce8ddf5bf1…` |
| `corpus-CB-misfire` | B (ausente) | 457 | 3 | 2 | `ce1492e66d351b03…` |
| `corpus-CB-o2_lag` | B (ausente) | 457 | 3 | 3 | `56c44adc2c327e30…` |
| `corpus-CB-thermostat_stuck` | B (ausente) | 457 | 4 | 3 | `35181bbba21e2f01…` |
| `corpus-CB-vacuum_leak` | B (ausente) | 457 | 4 | 2 | `63c81d0f51dfc2a2…` |
| `corpus-CBp-maf_drift` | B duro (parcial) | 457 | 3 | 1 | `0c49350d09355c08…` |
| `corpus-CBp-misfire` | B duro (parcial) | 457 | 1 | 1 | `e6c2a70fa7abe788…` |
| `corpus-CBp-o2_lag` | B duro (parcial) | 457 | 1 | 1 | `39084d882719874a…` |
| `corpus-CBp-thermostat_stuck` | B duro (parcial) | 457 | 1 | 1 | `2e90abcf4b7929dc…` |
| `corpus-CBp-vacuum_leak` | B duro (parcial) | 457 | 3 | 1 | `8645efc243fce417…` |

Verificación: `python tools/build_corpus.py --verify`.

## 6. Evidencia de referencia por mecanismo

Los `chunk_id` considerados pertinentes para cada mecanismo, necesarios para las métricas
de recuperación M3, M4 y M6. Se derivan de la misma declaración que construye las
variantes —es pertinente exactamente aquello cuya retirada produce el Escenario B— y
quedan congelados antes de ejecutar.

| Mecanismo | Chunks pertinentes |
|---|---|
| `maf_drift` | 44 |
| `misfire` | 35 |
| `o2_lag` | 67 |
| `thermostat_stuck` | 97 |
| `vacuum_leak` | 27 |

**Validada por el autor: NO — pendiente.**
El diseño experimental exige que un evaluador humano marque la pertinencia antes de
ejecutar EXP-RET-001. La derivación automática es una propuesta trazable, no esa validación.

## 7. Límites declarados

1. **El corpus es obra propia en su capa de procedimientos.** La capa externa procede de
   una enciclopedia colaborativa, no de documentación técnica de fabricante: es
   verificable y citable, pero no es documentación de taller. No se afirma validez sobre
   corpus técnicos reales.
2. **Mezcla de idiomas.** La capa externa combina español e inglés; la propia es española.
   El efecto del idioma sobre la recuperación no se controla y se declara como limitación.
3. **`corpus_v1.yaml` sigue en el repositorio** como fixture de pruebas. No es el corpus
   recuperable del experimento y mantiene el hallazgo E-RAG de F24; su retirada corresponde
   a la fase que recablee el agente a C-A.
