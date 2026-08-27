# Alineación científica v4 — Núcleo científico canónico

**2026-08-27 · FUENTE ÚNICA de la estructura científica del TFM.** Sustituye a
`docs/alineacion_v3/01_nucleo_cientifico.md`, que permanece en el repositorio como
registro histórico y se lee a través del §11 de este documento. Si otro documento vivo
contradice a éste, gana éste y se corrige el otro.

---

## 0. La cadena que se investiga

El trabajo estudia **cómo se sostiene una explicación diagnóstica**, no cómo se descubre
un fallo. La cadena tiene seis pasos:

```text
1. OBSERVAR         telemetría OBD-II real                ¿Qué registró el vehículo?
2. CONTEXTUALIZAR   evento operativo, ventana, historial  ¿En qué condiciones?
3. DIAGNOSTICAR     anomalía y/o DTC → contexto           ¿Qué se afirma que ocurre?
   O RECIBIR EL     diagnóstico
   DIAGNÓSTICO
4. RECUPERAR        evidencia documental mediante RAG     ¿Qué respalda esa afirmación?
   EVIDENCIA
5. VERIFICAR EL     cada afirmación contra la evidencia   ¿Está sostenida y es rastreable?
   SOPORTE          recuperada y contra la telemetría
6. DECIDIR          explicación trazable  |  abstención   ¿Tenemos derecho a explicar?
```

La tesis, en una frase:

> Una explicación diagnóstica solo es defendible si cada una de sus afirmaciones puede
> rastrearse hasta una evidencia concreta —documental o telemétrica— y si el sistema
> reconoce y declara los casos en que esa evidencia no existe, en lugar de completarlos.

Cada componente del artefacto se justifica **por el paso que sirve**. Los pasos 1–3 están
resueltos instrumentalmente por la serie experimental F3–F22 y no son la contribución; la
contribución está en los pasos 4–6.

## 1. Pregunta de investigación oficial (PI v4)

> **PI:** ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos
> OBD-II reales, rastreando cada explicación hasta su evidencia de origen, y reconocer
> cuándo la evidencia disponible no es suficiente para sostener una explicación en lugar de
> generar una hipótesis sin fundamento?

*Especificación metodológica (fuera del enunciado):* el sistema se implementa mediante un
agente sobre un grafo explícito, recuperación documental sobre un corpus con manifiesto,
un modelo de lenguaje pequeño ejecutado localmente, un verificador determinista y una
política de abstención, sobre la arquitectura Edge–Cloud ya construida. Los mecanismos son
medios: la refutación de una hipótesis parcial no invalida la PI, la responde.

Historia completa de la PI (v1 → v4) y motivo de cada cambio: `04_historial_pi.md`.

### Subpreguntas

- **PI.a** (pasos 3–4) ¿La evidencia recuperada mediante RAG sobre un corpus técnico es
  relevante para el diagnóstico producido a partir de telemetría OBD-II real? → H-GRD.
- **PI.b** (paso 5) ¿Puede establecerse y verificarse una correspondencia explícita entre
  cada afirmación de la explicación y la evidencia que la sostiene? → H-TRC.
- **PI.c** (paso 5) ¿Reduce la verificación del soporte las afirmaciones no sustentadas
  frente a generar la explicación sin evidencia o sin verificarla? → H-GRD.
- **PI.d** (paso 6) ¿Distingue el sistema los casos en que la evidencia disponible no
  sostiene ninguna explicación, y se abstiene en ellos? → H-ABS.
- **PI.e** (paso 6) ¿Mejora la abstención la calidad de lo que el sistema sí afirma, sin
  reducir la cobertura hasta hacerlo inútil? → H-SEL.
- **PI.f** (transversal) ¿Se sostiene todo lo anterior dentro del presupuesto de cómputo
  del perfil edge evaluado? → criterio transversal edge (no es hipótesis).

## 2. Definiciones operativas

El vocabulario se usa con un único significado en todo el trabajo.

| Término | Definición operativa |
|---|---|
| **Dato** | Valor de un PID OBD-II en un instante, o un agregado determinista de esos valores (feature de ventana o de evento). No interpreta nada. |
| **Evidencia** | Unidad identificable y citable que puede sostener o contradecir una afirmación. Dos tipos: **evidencia documental** (un `chunk_id` del corpus, con su `document_id` y su checksum) y **evidencia telemétrica** (una comprobación determinista sobre un `feature_vector` identificado, con su valor y su umbral). |
| **Diagnóstico** | Afirmación sobre el estado del vehículo: modo de fallo candidato, alcance y severidad. En este trabajo se produce a partir de la detección de anomalías y del contexto, o se recibe como entrada del banco. |
| **Explicación** | Texto estructurado que justifica un diagnóstico, descompuesto en **afirmaciones** atómicas y verificables por separado. |
| **Afirmación** | Proposición unitaria de la explicación que puede ser verdadera o falsa por sí sola («el LTFT medio es +7,2 %», «un LTFT sostenidamente positivo es compatible con una fuga de vacío»). |
| **Trazabilidad** | Propiedad de una afirmación: existe al menos una referencia de evidencia asociada, esa referencia resuelve a una unidad existente y su contenido sostiene la afirmación. Se verifica, no se declara. |
| **Soporte (groundedness)** | Fracción de afirmaciones de una explicación que son trazables en el sentido anterior. |
| **Fidelidad (faithfulness)** | Grado en que la explicación emitida refleja la evidencia efectivamente recuperada y no conocimiento paramétrico del modelo de lenguaje. |
| **Evidencia insuficiente** | Estado del caso en que, tras la recuperación, ninguna combinación de evidencia disponible alcanza el criterio de soporte pre-registrado para ninguna explicación candidata. Es una propiedad **relativa al corpus y verificable por construcción**. |
| **Abstención** | Salida del sistema en la que declara explícitamente que la evidencia disponible no sostiene una explicación, indica qué falta y no emite un diagnóstico explicado. No es un fallo: es una salida correcta. |
| **Hipótesis (sentido operativo)** | Explicación candidata antes de verificar su soporte. En este TFM la hipótesis es un **objeto interno del proceso**, no un resultado ni un objeto que se consolide como conocimiento. |

**Distinciones que el trabajo no puede confundir:** dato ≠ evidencia · anomalía ≠
diagnóstico · diagnóstico ≠ explicación · explicación fluida ≠ explicación sostenida ·
afirmación sostenida ≠ afirmación verdadera · abstención ≠ fallo del sistema.

### 2.1 Control experimental de la disponibilidad de evidencia

La condición «evidencia insuficiente» no se simula: se **construye** retirando del corpus
recuperable los documentos que describen el mecanismo del fallo evaluado, con manifiesto y
checksum, y verificándolo con el auditor ejecutable ya implementado
(`tools/contamination_audit.py`, exclusión E-RAG). El mismo instrumento que en la
alineación v3 servía para garantizar que el sistema *no había visto* un patrón sirve ahora
para manipular deliberadamente **qué evidencia está disponible**. Las tres clases held-out
congeladas (`corr_break_rpm_maf`, `load_coolant_decouple`, `joint_slow_drift`) siguen
siendo el material del escenario, con una lectura distinta (§6.3 y `03_diseno_experimental.md`).

## 3. Vacío de investigación

### 3.1 Vacío central V4\*

> **V4\*:** En los trabajos revisados no fue identificada una evaluación conjunta de:
> (a) diagnóstico obtenido a partir de datos OBD-II reales, (b) explicación de ese
> diagnóstico mediante evidencia recuperada con RAG, (c) trazabilidad explícita y
> verificable entre cada afirmación de la explicación y la evidencia que la sostiene, y
> (d) comportamiento seguro —abstención declarada— cuando la evidencia recuperada resulta
> insuficiente. Los estudios analizados abordan estos elementos por separado o en pares,
> y evalúan mayoritariamente la calidad percibida de la explicación antes que su soporte
> verificable y su comportamiento ante la ausencia de evidencia.

**Prudencia obligatoria.** La formulación afirma *cobertura insuficiente y ausencia de
evaluación conjunta en el corpus revisado* (≈153 referencias verificadas, barrido hasta
agosto de 2026), **no** inexistencia. No se afirma —y sería falso— que no existan sistemas
RAG aplicados al diagnóstico vehicular: existen y se citan (Mahale 2025 entre ellos). Lo
que no fue identificado es la combinación experimental completa, y en particular la
evaluación explícita del comportamiento ante evidencia insuficiente. Si la revisión
sistemática pendiente a texto completo aflora un trabajo que cubra la combinación, se
analizará explícitamente y V4\* se reformulará; nunca se ocultará.

### 3.2 Dimensiones subordinadas SD1–SD4

| SD | Dimensión | Pregunta que aporta a V4\* | Procede de (v3) | Evidencia propia |
|---|---|---|---|---|
| **SD1** | Contexto diagnóstico a partir de OBD-II | ¿Qué contexto verificable puede construirse desde telemetría real, y con qué calidad? | S1 (+ parte de S6) | 14 experimentos ejecutados (F3–F22); techo demostrado = cobertura efectiva de la normalidad |
| **SD2** | Recuperación de evidencia para diagnóstico | ¿Qué se recupera, con qué relevancia, y cuándo la recuperación es vacía o no concluyente? | S2 + S3 (parte) | Sin evidencia propia; retriever léxico implementado y auditado |
| **SD3** | Trazabilidad y verificación del soporte | ¿Cómo se establece y comprueba la correspondencia afirmación→evidencia→dato? | S3 | Verificador determinista implementado; sin evaluación |
| **SD4** | Suficiencia de evidencia y abstención | ¿Cuándo el sistema no debe explicar, y sabe reconocerlo? | S6 (reinterpretada) + parte de S4 | Sin evidencia propia; escenario y controles ya materializados (`cases_v2`, CN8) |

S4 (memoria validada) y S5 (arquitectura multiagente) de la alineación v3 **salen del
núcleo científico** y pasan a `05_fuera_de_alcance.md`. Su evidencia y su diseño no se
borran.

## 4. Objetivos

### 4.1 Objetivo general

> Diseñar y evaluar experimentalmente un agente basado en recuperación aumentada por
> evidencia (RAG) que explique diagnósticos vehiculares obtenidos a partir de datos OBD-II
> reales, manteniendo una correspondencia verificable entre cada afirmación de la
> explicación y la evidencia que la sostiene, y que se abstenga de explicar cuando la
> evidencia disponible resulte insuficiente, bajo las restricciones de cómputo de una
> plataforma embarcada.

### 4.2 Objetivos científicos específicos

| OE | Enunciado | Pasos | Contrasta |
|---|---|---|---|
| **OE-C1** | Construir el contexto diagnóstico verificable a partir de telemetría OBD-II real —ventanas, eventos operativos y detección de anomalías ya validada— y definir el objeto de entrada del razonamiento con su procedencia registrada. | 1–3 | (instrumental; habilita todas) |
| **OE-C2** | Diseñar y evaluar la recuperación de evidencia documental pertinente para un diagnóstico dado, sobre un corpus con manifiesto y disponibilidad controlada. | 4 | H-GRD |
| **OE-C3** | Definir una representación de la explicación en afirmaciones atómicas con referencia de evidencia, y un procedimiento que verifique que la correspondencia afirmación→evidencia→dato es efectiva y no meramente declarada. | 5 | H-TRC, H-GRD |
| **OE-C4** | Operacionalizar el criterio de suficiencia de la evidencia e implementar una política de abstención que distinga la explicación sostenida de la declaración de evidencia insuficiente. | 5–6 | H-ABS |
| **OE-C5** | Evaluar experimentalmente el agente bajo disponibilidad de evidencia controlada, midiendo exactitud diagnóstica, soporte y fidelidad de la explicación, corrección y completitud de la trazabilidad, y calidad de la abstención, dentro del presupuesto edge. | 3–6 | H-MAIN, H-SEL |

**Correspondencia con la alineación v3:** OE-C1(v4) ← OE-C2(v3) *degradado a instrumental,
conserva su evidencia* · OE-C2(v4) ← parte de OE-C3(v3) · OE-C3(v4) ← parte de OE-C3(v3),
ampliado con trazabilidad · OE-C4(v4) ← OE-C1(v3) *reorientado: la exclusión ya no define
novedad, define insuficiencia* · OE-C5(v4) ← OE-C4(v3) *sin la parte de consolidación*.

### 4.3 Objetivos instrumentales y de ingeniería

Sin pretensión de contribución científica: banco reproducible con semillas y freeze por
hash (`suite_v2`, `cases_v2`) · generación de escenarios · corpus documental con manifiesto
y variantes de disponibilidad · persistencia PostgreSQL+pgvector con procedencia ·
instrumentación de runs y medición de recursos · API, interfaz y contenedores · memoria del
TFM.

## 5. Hipótesis

Todas son falsables, con umbrales congelados antes de ejecutar
(`03_diseno_experimental.md` §5) y con resultados negativos publicables con el mismo
detalle que los positivos.

### H-MAIN v4 (integradora — contraste directo de la PI)

> **H-MAIN.** Dado un diagnóstico obtenido de datos OBD-II reales y un corpus documental
> cuya cobertura del mecanismo evaluado se controla experimentalmente, el agente con RAG,
> verificación de soporte y política de abstención podrá: (i) producir una explicación
> diagnóstica correcta respecto al mecanismo de referencia cuando la evidencia esté
> disponible; (ii) mantener cada afirmación relevante de esa explicación rastreable hasta
> una unidad de evidencia concreta; (iii) no introducir afirmaciones sin soporte; y
> (iv) declarar evidencia insuficiente, en lugar de emitir una explicación, cuando el
> corpus no contenga la evidencia necesaria.

Operacionalización (co-primarias conjuntivas; definición completa de cada métrica en
`03_diseno_experimental.md` §4):

- **Q1** exactitud diagnóstica del brazo completo en el escenario de evidencia suficiente;
- **Q2** proporción de afirmaciones sustentadas (*groundedness*) por explicación;
- **Q3** corrección de la citación (la referencia existe y sostiene la afirmación);
- **Q4** tasa de abstención correcta en el escenario de evidencia insuficiente;
- **Q5** tasa de falsa aceptación: explicación emitida como sostenida cuando la evidencia
  necesaria fue retirada del corpus.

**Qué evidencia decide.** *Apoyo:* Q1–Q4 sobre sus umbrales con Q5 bajo el máximo
tolerado. *Apoyo parcial:* subconjunto satisfecho, reportado por paso de la cadena e
identificando el eslabón que falla. *Refutación:* Q5 por encima del máximo tolerado (el
sistema completa huecos), o Q2/Q3 no distinguibles del brazo sin verificación, o Q4 por
debajo del mínimo (el sistema no reconoce la insuficiencia). *No concluyente:* potencia
insuficiente, instrumento inválido (juez descalibrado) o violación detectada del control
de disponibilidad del corpus — se reporta como tal, nunca se promociona a apoyo.

H-MAIN no está diseñada para garantizar éxito. Un modelo de lenguaje pequeño con un corpus
reducido puede razonablemente fallar en Q3 (citación correcta) o en Q5 (completar huecos);
ambos resultados se publicarían con el mismo detalle.

### Hipótesis subordinadas

| H | Enunciado | Paso | Contraste | Refutación |
|---|---|---|---|---|
| **H-GRD** *(soporte)* | Recuperar evidencia y verificar el soporte de cada afirmación reduce las afirmaciones no sustentadas frente a generar la explicación sin evidencia (B1) o con evidencia pero sin verificación (B2). | 4–5 | B1 vs B2 vs B3 | Sin reducción medible de afirmaciones no sustentadas de B3 sobre B2 → la verificación queda como propuesta de diseño con resultado negativo. |
| **H-TRC** *(trazabilidad)* | La correspondencia afirmación→evidencia→dato producida por el sistema es **efectiva**: las referencias resuelven a unidades existentes y su contenido sostiene la afirmación, por encima de lo que produciría una atribución posicional o aleatoria. | 5 | B3 vs control de atribución trivial | Citación correcta no distinguible del control → la trazabilidad es decorativa y así se reporta. |
| **H-ABS** *(abstención)* | Ante evidencia deliberadamente retirada del corpus, el sistema declara insuficiencia en lugar de emitir una explicación, y lo hace con una tasa de falsa abstención acotada en el escenario donde la evidencia sí está. | 6 | Escenario A vs Escenario B, B2 vs B3 | El sistema explica igual con y sin evidencia disponible → refuta el núcleo de la PI. |
| **H-SEL** *(exactitud selectiva)* | La política de abstención mejora la exactitud sobre los casos no abstenidos (*selective accuracy*) sin reducir la cobertura por debajo del mínimo pre-registrado. | 6 | curva riesgo-cobertura, B3 vs B2 | Toda la ganancia de exactitud se paga con cobertura por debajo del mínimo → la abstención es un mecanismo de seguridad sin utilidad diagnóstica y así se reporta. |

**Hipótesis retiradas del contraste principal** (con su diseño íntegro y sin ejecutar, en
`05_fuera_de_alcance.md`): H-MEM (memoria validada), H-MAS (descomposición multiagente),
H-EVT (eventos vs ventanas) y H-PERS (normalidad personalizada). Las dos últimas conservan
valor instrumental sobre SD1 y podrán ejecutarse si el calendario lo permite, sin que su
resultado condicione la respuesta a la PI.

## 6. Tesis · Artefacto · Ingeniería

| Nivel | Qué es | Contenido |
|---|---|---|
| **TESIS** | Cómo se sostiene y cómo se limita una explicación diagnóstica | Cadena §0 · PI v4 · V4\* · H-MAIN y subordinadas |
| **ARTEFACTO EXPERIMENTAL** | Instrumentos con papel declarado en la cadena | contexto diagnóstico OBD-II (1–3) · retriever con manifiesto de corpus (4) · generador de explicación en afirmaciones (5) · verificador de soporte documental y telemétrico (5) · política de suficiencia y abstención (6) · banco con disponibilidad de evidencia controlada (escenario) |
| **INGENIERÍA DE SOPORTE** | Sin pretensión científica | PostgreSQL/pgvector · FastAPI · contratos y migraciones · contenedores · outbox/sync · CI · UI/app · observabilidad |

### 6.1 Estados de una explicación

Sustituyen, en el alcance del TFM, a los ocho estados epistemológicos de la alineación v3.
Son los estados que el sistema **emite y que se evalúan**:

| Estado | Criterio | Salida al usuario |
|---|---|---|
| `SUPPORTED` | Todas las afirmaciones relevantes tienen evidencia que las sostiene y ninguna contradicción domina | Explicación trazable con sus referencias |
| `CONTRADICTED` | Existe evidencia que contradice la explicación candidata de forma dominante | Explicación descartada, con la evidencia contradictoria |
| `INSUFFICIENT_EVIDENCE` | Ninguna explicación candidata alcanza el criterio de soporte | **Abstención declarada**, indicando qué evidencia faltó |
| `INCONCLUSIVE` | Varias explicaciones candidatas con soporte comparable y sin evidencia diferencial | Explicaciones alternativas con su evidencia, sin colapsar a una |

Los estados de la alineación v3 orientados a **promover una hipótesis a conocimiento
reutilizable** (`EXPERIMENTALLY_VERIFIED`, `EXTERNALLY_CONFIRMED`) y los estados de patrón
(`PatternStatus`) permanecen en los contratos por compatibilidad, **no se evalúan** y se
declaran fuera del alcance (`05_fuera_de_alcance.md` §2).

## 7. Contribución central

> Evaluar si un agente basado en RAG puede generar explicaciones diagnósticas de vehículos
> a partir de datos OBD-II reales, manteniendo trazabilidad entre afirmaciones y evidencia
> recuperada, y absteniéndose cuando dicha evidencia no sea suficiente.

Contribuciones candidatas, condicionadas a resultados:

| Candidata | Emerge solo si |
|---|---|
| **C1 — Protocolo de disponibilidad de evidencia controlada** para evaluar el comportamiento de un sistema RAG diagnóstico ante ausencia de evidencia, con exclusión verificable y auditada del corpus | el protocolo de `03_diseno_experimental.md` se ejecuta con la exclusión E-RAG verificada; es contribución metodológica aunque H-MAIN se refute |
| **C2 — Representación y verificación de la trazabilidad afirmación→evidencia→dato** en explicaciones diagnósticas sobre telemetría | H-TRC y H-GRD producen evidencia interpretable, positiva o negativa con causa |
| **C3 — Caracterización empírica de la abstención** de un agente diagnóstico con modelo de lenguaje pequeño en el borde, con su curva riesgo-cobertura | H-ABS y H-SEL se ejecutan con ambos escenarios y sus controles |

El número final de contribuciones es el que la evidencia permita.

## 8. Delimitaciones

**Puede demostrar, bajo condiciones controladas:** que un diagnóstico obtenido de
telemetría OBD-II puede explicarse con evidencia recuperada · que la correspondencia
afirmación→evidencia puede establecerse y verificarse · que la verificación del soporte
modifica (o no) la tasa de afirmaciones sin sustento · que el sistema distingue (o no) la
disponibilidad de evidencia · el coste de todo ello bajo el perfil edge evaluado.

**No debe afirmar, salvo evidencia específica:** descubrimiento de averías desconocidas ·
generación de conocimiento diagnóstico nuevo · aprendizaje autónomo · causalidad mecánica
definitiva · generalización al parque vehicular · diagnóstico profesional certificable ·
validación física en Raspberry Pi mientras solo exista emulación · que RAG elimina las
alucinaciones por sí mismo · que una explicación sostenida es una explicación verdadera.

**Regla epistemológica transversal:** *la afirmación nunca supera la evidencia.* Toda
conclusión se clasifica como respaldada / parcialmente respaldada / refutada / condicionada
/ no concluyente.

## 9. Metodología: Design Science Research

DSR sigue siendo el marco general y **no sustituye** hipótesis, controles, métricas ni
falsación: el diseño experimental de `03_diseno_experimental.md` es quien responde a las
hipótesis. El artefacto investigado se redefine.

| Actividad DSR | Contenido bajo la PI v4 |
|---|---|
| **1. Identificación del problema** | Una explicación diagnóstica fluida no es una explicación sostenida; sin trazabilidad no puede distinguirse una de otra, y sin política de abstención el sistema completa los huecos de evidencia. §0, §3. |
| **2. Objetivos de la solución** | Explicación trazable hasta la evidencia y abstención verificable ante evidencia insuficiente, dentro del presupuesto edge. §4. |
| **3. Diseño y desarrollo** | Artefacto = contexto diagnóstico OBD-II + retriever con manifiesto + generador de explicación en afirmaciones + verificador de soporte + política de suficiencia/abstención. §6. |
| **4. Demostración** | Ejecución sobre `cases_v2` y los episodios held-out de `suite_v2`, en los dos escenarios de disponibilidad de evidencia. |
| **5. Evaluación** | Contraste de H-MAIN, H-GRD, H-TRC, H-ABS y H-SEL con las métricas y umbrales congelados; controles negativos CN1–CN4, CN7–CN9. |
| **6. Comunicación** | Memoria del TFM, informes de fase y pre-registro con sus enmiendas. |

Se retiran del ciclo DSR los componentes metodológicos añadidos únicamente para demostrar
descubrimiento y aprendizaje autónomo: el gate de promoción a conocimiento, las ablaciones
de memoria M0/M1/M2 y la matriz de contaminación de la memoria (E-MEM), que deja de ser
condición del experimento principal. La revisión sistemática (PRISMA) sigue siendo el
método de construcción de la base de conocimiento, no la metodología del TFM.

## 10. Control de contaminación (reducido)

| Componente | train | validation | test | corpus RAG | GT | prompts |
|---|---|---|---|---|---|---|
| Detector (fit + umbral) | ✔ (solo normal) | selección de modelo | ✘ | ✘ | ✘ | — |
| Generador de explicación (LLM) | ✘ | ✘ | caso a caso | vía recuperación | ✘ | plantillas congeladas |
| Retriever / corpus | — | — | — | ✔ (manifiesto hasheado, **variante A o B declarada por caso**) | ✘ | — |
| Verificador | telemetría del caso | ✘ | caso a caso | evidencia recuperada | ✘ | criterios deterministas |
| Juez / evaluador | ✘ | ✘ | salidas a evaluar | ✘ | ✔ (solo el evaluador) | posiciones aleatorizadas; juez ≠ generador |

E-DET se conserva íntegro (protege el contexto diagnóstico). **E-RAG deja de ser una
restricción y pasa a ser la variable independiente principal.** E-MEM desaparece del
protocolo: la memoria no participa en la evaluación. El ground truth nunca es visible para
ningún componente en ejecución.

## 11. Correspondencia con la alineación v3

| Elemento v3 | Elemento v4 | Nota |
|---|---|---|
| Cadena de 8 pasos | Cadena de 6 pasos (§0) | Se retiran *hipotetizar como resultado* y *consolidar*; se reformula *reconocer insuficiencia* como verificación de suficiencia de la evidencia recuperada |
| PI v3 | PI v4 | `04_historial_pi.md` |
| V\* | V4\* | Reformulado sobre explicación, trazabilidad y abstención |
| S1 · S2 · S3 · S6 | SD1 · SD2 · SD3 · SD4 | Reasignación, no eliminación |
| S4 · S5 | — | `05_fuera_de_alcance.md` |
| OE-C1…C4 (v3) | OE-C1…C5 (v4) | Tabla §4.2 |
| H-MAIN v3 (P1–P5) | H-MAIN v4 (Q1–Q5) | P2→Q4, P3→Q5, P4→Q1/Q2; P1 pasa a precondición; P5 sale del alcance |
| H-EXP | H-GRD (ampliada con Q2/Q3) | Los brazos X0/X1/X2 se conservan como B1/B2/B3 |
| H-EVT · H-PERS | instrumentales sobre SD1 | No condicionan la PI |
| H-MEM · H-MAS | — | `05_fuera_de_alcance.md` |
| 8 estados epistemológicos | 4 estados de explicación (§6.1) | Los de promoción a conocimiento no se evalúan |
| CN1–CN9 | CN1–CN4, CN7–CN9 | CN5/CN6 dependen de memoria |
| C1–C3 (v3) | C1–C3 (v4) | Redefinidas §7 |

Los documentos históricos cerrados (informes de fase, ADRs aceptados, la propia alineación
v3) **no se reescriben**: se leen a través de esta tabla y de
`docs/correspondencia_nomenclatura.md`.
