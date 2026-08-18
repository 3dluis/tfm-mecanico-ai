# Alineación científica v3 — Núcleo científico canónico

**2026-08-18 · FUENTE ÚNICA de la estructura científica del TFM.** Si otro documento
contradice a éste, gana éste y se corrige el otro (misma regla que REGLAS.md para lo
técnico). Los documentos históricos cerrados no se reescriben: se leen a través de
[`correspondencia_nomenclatura.md`](../correspondencia_nomenclatura.md).

---

## 0. La cadena epistemológica (columna vertebral del TFM)

La investigación estudia una **transición epistemológica**, no una integración de
tecnologías:

```text
1. OBSERVAR        telemetría OBD-II                     ¿Qué ocurrió?
2. CONTEXTUALIZAR  evento operativo + vehículo + historial ¿En qué condiciones ocurrió?
3. DETECTAR        desviación del comportamiento esperado  ¿Hay una anomalía relevante?
4. RECONOCER       cobertura del conocimiento disponible   ¿El sistema ya sabe explicarlo?
   INSUFICIENCIA
5. HIPOTETIZAR     explicaciones diagnósticas candidatas   ¿Qué causas podrían explicarlo?
6. RECUPERAR Y     evidencia a favor, en contra y causas   ¿Qué respalda o contradice
   CONTRASTAR      alternativas                            cada hipótesis?
7. VERIFICAR       criterios establecidos a priori         ¿Qué hipótesis se sostiene?
8. CONSOLIDAR      solo conocimiento suficientemente       ¿Tenemos derecho epistemológico
   O ABSTENERSE    validado entra en memoria               a recordar esta conclusión?
```

Cada componente tecnológico del artefacto se justifica **por el paso de la cadena que
sirve**, nunca por su mera existencia. La tesis, en una frase:

> Estudiar bajo qué condiciones un sistema inteligente híbrido puede transformar un patrón
> anómalo no representado en su conocimiento disponible en una hipótesis diagnóstica
> verificable y, sólo después de contrastarla mediante evidencia, incorporarla como
> conocimiento reutilizable — o abstenerse.

## 1. Pregunta de investigación oficial (PI v3)

> **PI:** ¿Puede un sistema inteligente híbrido identificar patrones de fallo no
> representados en su conocimiento disponible, generar hipótesis diagnósticas a partir del
> análisis contextual y longitudinal de datos OBD-II y validarlas mediante evidencia antes
> de incorporarlas como conocimiento reutilizable?

*Especificación metodológica (fuera del enunciado):* el sistema se implementa mediante
aprendizaje no supervisado, análisis de eventos operativos, arquitectura multiagente,
modelos de lenguaje, RAG y memoria con validación, sobre una arquitectura Edge–Cloud. Los
mecanismos son medios: la refutación de cualquier hipótesis parcial no invalida la PI —
la responde.

La PI no se modifica sin justificación explícita y autorización del autor. Historia:
PI v1 (Fase 0) y PI v2 (Opción B, 12-ago) en `correspondencia_nomenclatura.md` §0.

### Subpreguntas (lectura por pasos de la cadena)

- **PI.a** (pasos 1–3) ¿Mejora la detección cuando la normalidad se condiciona al contexto
  operativo y al vehículo? → H-EVT, H-PERS.
- **PI.b** (paso 4) ¿Puede el sistema reconocer que su conocimiento disponible no cubre el
  patrón observado, en lugar de identificarlo erróneamente con confianza? → H-MAIN (P2/P3).
- **PI.c** (pasos 5–7) ¿La recuperación y el contraste de evidencia producen hipótesis más
  correctas, trazables y calibradas que la generación sin evidencia o sin verificación? → H-EXP.
- **PI.d** (paso 8) ¿La validación previa a la consolidación reduce la contaminación de la
  memoria sin impedir la reutilización de conocimiento verificado? → H-MEM.
- **PI.e** (transversal) ¿Qué configuración arquitectónica mínima sostiene la cadena dentro
  del presupuesto edge? → H-MAS (secundaria) + criterio transversal edge.

## 2. Definición operacional: «patrón de fallo no representado»

Los términos «desconocido», «nuevo», «no documentado» y «nunca visto» **no se usan** como
sinónimos técnicos. La definición canónica:

> Un patrón de fallo está **no representado en el conocimiento disponible** del sistema
> cuando, en el momento de la evaluación, se cumplen simultáneamente las tres exclusiones:
>
> - **E-DET:** ninguna sesión que contenga el patrón (ni su clase de fallo) ha participado
>   en el entrenamiento, la validación, la selección de modelo ni el ajuste de umbrales del
>   detector;
> - **E-RAG:** el corpus recuperable no contiene documentos que describan ese fallo ni su
>   solución de forma directamente recuperable;
> - **E-MEM:** la memoria longitudinal no contiene ningún caso, hipótesis ni conocimiento
>   consolidado derivado de ese patrón.

Consecuencias:

1. «No representado» es **relativo al sistema y a la evaluación**, no a la ingeniería
   automotriz: los fallos held-out son bien conocidos para un mecánico; lo que se estudia
   es la reacción del sistema ante su ausencia de cobertura.
2. La propiedad es **comprobable**: las tres exclusiones se verifican por construcción
   (inyección sintética controlada, manifiestos de corpus, estado inicial de memoria) y se
   auditan antes de cada ejecución (matriz de contaminación, §9).
3. Un patrón puede perder la condición durante el experimento (si el sistema consolida
   conocimiento sobre él tras validarlo): eso no es contaminación, es el fenómeno estudiado.
   La contaminación es la entrada de conocimiento **por vías distintas del protocolo**.
4. Una anomalía estadística aislada **no** es un patrón: se exige recurrencia mínima
   definida en el protocolo del experimento (≥2 episodios del mismo mecanismo) antes de que
   el sistema pueda promover nada más allá de ANOMALOUS (§7).

Clases held-out congeladas (pre-registro): `corr_break_rpm_maf`, `load_coolant_decouple`,
`joint_slow_drift` — precisamente las que la serie exploratoria mantiene en recall 0.000,
lo que convierte el reto en real y no decorativo.

## 3. Vacío científico

### 3.1 Vacío central V\*

> **V\*:** Los trabajos revisados no muestran, de forma integrada y experimentalmente
> validada, cómo transformar un patrón anómalo no representado en el conocimiento
> disponible de un sistema diagnóstico en conocimiento diagnóstico verificable y
> reutilizable, mediante una secuencia que considere el contexto longitudinal, la
> generación de hipótesis, el contraste con evidencia y la consolidación controlada en
> memoria.

**Prudencia obligatoria:** esta formulación afirma *cobertura insuficiente y falta de
evaluación conjunta* en el corpus revisado (≈153 referencias verificadas, barrido hasta
agosto de 2026), no inexistencia absoluta. Sigue condicionada a los pendientes declarados:
PRISMA formal con acceso institucional y lectura a texto completo de Takara (ESWA 2025),
Min (EAAI 2024) y Onsu (IoT 2025). Los antecedentes que más se acercan (Mahale 2025 —
telemetría→ML→RAG→LLM sin verificación ni memoria ni edge; DS-Agent y HDSO — consolidación
validada fuera del dominio y sin telemetría física; CADD — contexto sin diagnóstico) cubren
pasos o pares de pasos de la cadena, no la transición completa con evaluación end-to-end;
la matriz de cobertura (`02_trazabilidad.md` §3) lo documenta trabajo a trabajo, y si el
PRISMA formal aflora un trabajo que cubra la cadena, se analizará explícitamente y V\* se
reformulará — nunca se ocultará.

### 3.2 Dimensiones subordinadas S1–S6 (reclasificación de V1–V7)

| S | Dimensión | Pregunta que aporta a V\* | Absorbe | Estado de evidencia propia |
|---|---|---|---|---|
| **S1** | Detección contextual de anomalías | ¿Cuándo una observación es anomalía, considerando evento, estado del vehículo y comportamiento longitudinal? | V7 (parcial), V3 | 14 experimentos exploratorios; el techo demostrado fue de **cobertura de normalidad**, no de arquitectura (F22) |
| **S2** | Generación de hipótesis diagnósticas | ¿Cómo pasar de «hay algo anómalo» a «estas causas podrían explicarlo»? | V4 | Sin evidencia propia aún; bloqueada por R2 (elección del SLM) |
| **S3** | Verificación mediante evidencia | ¿Cómo contrastar hipótesis con telemetría, relaciones entre variables, evidencia documental y causas alternativas? | V4 (parte), V1 (parte) | Sin evidencia propia aún |
| **S4** | Memoria longitudinal validada | ¿Cuándo una inferencia adquiere derecho a ser recordada como conocimiento? | V2 | Diseño de estados definido (§7); sin evidencia experimental |
| **S5** | Arquitectura híbrida/multiagente Edge–Cloud | Condición habilitante y artefacto experimental; solo contribución si A0–A6 lo demuestra | V6, V1 (parte) | Slice construido; ablaciones no ejecutadas; **no se asume superioridad** |
| **S6** | Patrones no representados como escenario | Operacionalización y resultados del protocolo de exclusión triple | V5 (banco), parte de V7 | Banco v1–v3 congelados por hash; definición §2 |

V1–V7 no desaparecen: su evidencia y referencias se conservan; dejan de presentarse como
siete vacíos independientes de igual rango. Correspondencia completa en
`correspondencia_nomenclatura.md` §5.

## 4. Objetivos (tres niveles)

### Nivel 1 — Objetivo general científico

> Diseñar y evaluar experimentalmente un sistema inteligente híbrido capaz de identificar
> patrones de fallo no representados en su conocimiento disponible, formular hipótesis
> diagnósticas a partir del análisis contextual y longitudinal de datos OBD-II,
> contrastarlas mediante evidencia y consolidar únicamente aquellas que satisfagan
> criterios de validación como conocimiento reutilizable.

### Objetivos científicos específicos

| OE | Enunciado | Pasos de la cadena | Contrasta |
|---|---|---|---|
| **OE-C1** | Delimitar y operacionalizar el concepto de patrón de fallo no representado en el conocimiento disponible, con su protocolo de exclusión triple y su verificación anti-contaminación | 4, transversal | (definicional; habilita H-MAIN) |
| **OE-C2** | Evaluar el efecto del análisis contextual, longitudinal y personalizado sobre la identificación de anomalías | 1–3 | H-EVT, H-PERS |
| **OE-C3** | Evaluar la capacidad de generar hipótesis diagnósticas trazables y verificarlas mediante evidencia, incluida la evidencia contradictoria y las causas alternativas | 5–7 | H-EXP (y H-MAS como variante arquitectónica) |
| **OE-C4** | Evaluar la cadena completa mediante protocolo held-out/open-set con exclusión simultánea del detector, del corpus RAG y de la memoria, incluida la consolidación validada y la abstención | 4–8, end-to-end | H-MAIN, H-MEM |

### Nivel 2 — Objetivos instrumentales

Banco experimental reproducible con ground truth y fallos held-out (incluye benchmarks
v1–v3 congelados por hash y el criterio de **cobertura efectiva** de F22) · generación de
escenarios y control de semillas · implementación del artefacto (detectores, segmentación
de eventos, agentes, RAG, verificador, memoria con estados, Edge–Cloud) · instrumentación
experimental (registro de runs, manifiestos, matriz de contaminación ejecutable, medición
de recursos corregida). Correspondencia con los OE1–OE8 previos:
OE-C1←(nuevo, §2) · OE-C2←OE3 · OE-C3←OE4 · OE-C4←OE6+OE5 · instrumentales←OE1, OE2 ·
ingeniería←OE7 · administración←OE8.

### Nivel 3 — Ingeniería y administración

API, UI, aplicación móvil, contenedores, CI/CD, despliegue, sincronización outbox,
observabilidad, gestión del proyecto, memoria del TFM. **No se presentan como
contribuciones científicas.**

## 5. Hipótesis

### H-MAIN (integradora — contraste directo de la PI)

> **H-MAIN.** Bajo un protocolo held-out/open-set en el que el patrón de fallo evaluado no
> esté representado en el conocimiento utilizado por el detector, en el corpus recuperable
> ni en la memoria previa (§2), el sistema inteligente híbrido podrá: (i) identificar una
> anomalía relevante; (ii) reconocer la insuficiencia de su conocimiento disponible en
> lugar de emitir una identificación errónea con confianza; (iii) generar hipótesis
> diagnósticas trazables; (iv) contrastarlas mediante evidencia favorable y contradictoria;
> y (v) consolidar conocimiento únicamente cuando se satisfagan criterios de validación
> previamente establecidos — absteniéndose en caso contrario.

Operacionalización (conserva las co-primarias ya definidas en el pre-registro §4.6):
P1 recall de señalización en episodios held-out · P2 tasa de «no cubierto» correcta ·
P3 tasa de identificación errónea confiada · P4 calidad de hipótesis contra el mecanismo
GT (rúbrica anclada, juez calibrado ≠ generador, submuestra manual) · **P5 (nueva)**
decisión de consolidación correcta: fracción de casos en que el sistema consolida solo
tras satisfacer los criterios, y se abstiene cuando la evidencia es insuficiente
(controles negativos, §8.3).

**Qué evidencia decide:**

- **Apoya H-MAIN:** P1 y P2 sobre sus umbrales pre-registrados con P3 bajo el máximo
  tolerado, P4 mejor que el control de hipótesis plantilla/aleatoria con IC que excluye el
  empate, y P5 sin consolidaciones indebidas en los controles negativos.
- **Apoyo parcial:** subconjunto de (i)–(v) satisfecho — se reporta por pasos de la
  cadena, identificando el eslabón que falla.
- **Refuta H-MAIN:** identificación confiada errónea por encima del umbral (P3), o
  hipótesis no distinguibles del control (P4), o consolidación de hipótesis no validadas
  en los escenarios de contaminación (P5).
- **Insuficiente para decidir:** potencia por debajo de la planificada (n de episodios
  held-out incompleto), instrumentación inválida (p. ej. juez descalibrado), o violación
  detectada de la matriz de contaminación → se reporta como NO CONCLUYENTE, jamás se
  promociona a apoyo.

H-MAIN **no está diseñada para garantizar éxito**: los umbrales se congelan en el
pre-registro antes de ejecutar, y la serie exploratoria (recall 0.000 en las held-out
lentas con todos los detectores probados) hace plausible la refutación de (i) para parte
del banco — resultado que se publicaría con el mismo detalle.

### Hipótesis subordinadas

| H | Enunciado (resumen) | Paso | Refutación (resumen) |
|---|---|---|---|
| **H-EVT** | La representación contextual por eventos mejora la detección frente a alternativas por ventanas | 2–3 | Sin mejora sobre el mejor brazo por ventanas → el evento queda como unidad semántica del razonador, no como mejora de detección |
| **H-PERS** | La normalidad personalizada por vehículo (jerárquica flota→vehículo) reduce FP o mejora detección | 2–3 | El modelo global iguala → limitación declarada del entorno sintético |
| **H-EXP** | Recuperar y contrastar evidencia mejora exactitud factual, trazabilidad y calibración de las hipótesis frente a generación sin evidencia o sin verificación | 5–7 | Sin reducción medible de errores factuales → C-EXP queda como propuesta con resultado negativo |
| **H-MEM** | La memoria sometida a validación reduce la contaminación y permite reutilizar experiencias verificadas sin propagar hipótesis incorrectas (M0 vs M1 vs M2, §8.5) | 8 | La validación no reduce consolidaciones erróneas o su coste anula el beneficio |
| **H-MAS** (secundaria) | La descomposición multiagente aporta ventaja medible en alguna parte concreta de generación/contraste/verificación frente a alternativas más simples | 5–7 (arquitectura) | El monolítico iguala o supera → **resultado científico válido y publicado**; la arquitectura solo se conservaría por razones de ingeniería |

Ninguna hipótesis subordinada refutada invalida la PI: precisa qué mecanismo aporta y cuál
no. H-MAS no se asume verdadera.

## 6. Tesis · Artefacto · Ingeniería

| Nivel | Qué es | Contenido |
|---|---|---|
| **TESIS** (lo que se investiga) | La transición controlada desde un patrón anómalo no representado hasta conocimiento diagnóstico verificable y reutilizable — o la abstención | Cadena §0 · PI · V\* · H-MAIN y subordinadas |
| **ARTEFACTO EXPERIMENTAL** (lo que se construye para investigarla) | Instrumentos con papel declarado en la cadena | detector (3) · eventos (2) · personalización (2) · generador de hipótesis (5) · RAG (6) · verificador (7) · memoria con estados (8) · reconocedor de cobertura (4) · Edge–Cloud (condición de contorno) · banco sintético + held-out (escenario) |
| **INGENIERÍA DE SOPORTE** (lo que permite ejecutarlo) | Sin pretensión científica | PostgreSQL/pgvector · FastAPI · contratos y migraciones · contenedores · outbox/sync · CI · UI/app · observabilidad |

## 7. Estados epistemológicos

Estados del conocimiento en la memoria del sistema. Regla fundamental: **una hipótesis no
se convierte automáticamente en conocimiento.**

| Estado | Criterio de entrada | Evidencia requerida | Transiciones permitidas | Quién promueve |
|---|---|---|---|---|
| `OBSERVED` | Telemetría persistida con procedencia | — | → ANOMALOUS | pipeline de detección |
| `ANOMALOUS` | Score sobre umbral pre-fijado, con contexto de evento | score + contexto | → HYPOTHESIZED · → descartada (FP contextual) | detector (matemático; nunca el LLM) |
| `HYPOTHESIZED` | Hipótesis generada con ≥1 mecanismo causal explícito y predicciones comprobables | anomalía + contexto + recurrencia mínima (§2.4) | → SUPPORTED · → REFUTED · → INSUFFICIENT_EVIDENCE | agente generador |
| `SUPPORTED` | Evidencia favorable recuperada y contrastada; sin contradicción dominante | evidencia trazable a telemetría/corpus | → EXPERIMENTALLY_VERIFIED · → REFUTED · → INSUFFICIENT_EVIDENCE | verificador |
| `EXPERIMENTALLY_VERIFIED` | Predicciones de la hipótesis contrastadas contra telemetría posterior o contrafactual disponible, según criterios pre-establecidos | contraste explícito + ausencia de causa alternativa igualmente respaldada | → EXTERNALLY_CONFIRMED · → REFUTED | verificador (criterios deterministas) |
| `EXTERNALLY_CONFIRMED` | Confirmación fuera del sistema (mecánico, reparación efectiva, GT del banco en evaluación) | registro externo | (terminal para el caso) | autor/evaluador; nunca el propio sistema |
| `INSUFFICIENT_EVIDENCE` | La evidencia no alcanza los criterios en ningún sentido | — | → HYPOTHESIZED (con evidencia nueva) · caduca | verificador |
| `REFUTED` | Evidencia contradictoria dominante o predicción fallida | contraste registrado | (terminal; se conserva como resultado negativo) | verificador |

Reglas de memoria: solo `EXPERIMENTALLY_VERIFIED` y `EXTERNALLY_CONFIRMED` son
**conocimiento reutilizable** (recuperable como saber consolidado); `SUPPORTED` es
recuperable solo como hipótesis con su estado visible; `HYPOTHESIZED` e
`INSUFFICIENT_EVIDENCE` no se recuperan para razonamiento diagnóstico nuevo (solo para
continuidad del propio caso); `REFUTED` se conserva y bloquea la re-consolidación del mismo
mecanismo sin evidencia nueva. Toda transición queda trazada (quién, cuándo, con qué
evidencia). Distinciones operativas: observación ≠ conocimiento · anomalía ≠ diagnóstico ·
hipótesis ≠ conocimiento · hipótesis plausible ≠ conocimiento validado.

## 8. Diseño experimental de H-MAIN

### 8.1 Protocolo (15 pasos)

1. Selección del patrón held-out (clases congeladas, §2).
2. Exclusión del detector (E-DET) — verificada contra manifiestos de entrenamiento.
3. Exclusión del corpus RAG (E-RAG) — manifiesto de corpus con hash.
4. Exclusión de la memoria (E-MEM) — estado inicial declarado y hasheado.
5. Generación de telemetría (banco congelado; RNG de comportamiento y de inyección
   separados, ADR-0034).
6. Contextualización (eventos operativos + historial del vehículo).
7. Detección (umbral solo con train-normal; sin point adjustment).
8. Evaluación de cobertura del conocimiento (paso 4 de la cadena): el sistema declara
   cubierto / no cubierto con su justificación.
9. Generación de hipótesis (trazables, con mecanismo y predicciones).
10. Recuperación de evidencia favorable.
11. Búsqueda de evidencia contradictoria.
12. Consideración explícita de causas alternativas.
13. Verificación con criterios pre-establecidos (§7).
14. Decisión: estado final del caso.
15. Consolidación o abstención registrada, con trazabilidad completa.

**Se evalúa la cadena completa** — nunca solamente «si el LLM produjo la respuesta
correcta». Cada paso emite artefactos evaluables por separado, de modo que un fallo
end-to-end sea atribuible a su eslabón (misma lógica que `tipos_de_fallo_experimental.md`).

### 8.2 Referencias de comparación

Cota superior: el sistema completo con conocimiento disponible (sin exclusiones). Cota
inferior: clasificador supervisado entrenado solo con fallos conocidos. Control de
hipótesis: generador plantilla/aleatorio. Control de arquitectura: variante monolítica.

### 8.3 Controles negativos (el sistema debe saber no concluir)

| Control | Qué inyecta | Comportamiento correcto |
|---|---|---|
| CN1 | Comportamiento normal poco frecuente (p. ej. nivel LTFT sostenido, crucero largo — la familia exacta del hallazgo F21/F22) | No señalar, o señalar y reconocer normalidad al contextualizar |
| CN2 | Condiciones ambientales extremas pero normales | No diagnosticar avería |
| CN3 | Documentación distractora plausible en el corpus | No anclar la hipótesis en el distractor |
| CN4 | Evidencia contradictoria explícita | Degradar la hipótesis; no consolidar |
| CN5 | Memoria contaminada deliberadamente (hipótesis falsa pre-cargada como SUPPORTED) | No propagarla a casos nuevos; el gate de §7 la mantiene fuera del conocimiento reutilizable |
| CN6 | Hipótesis falsa inyectada en el flujo del verificador | REFUTED o INSUFFICIENT_EVIDENCE |
| CN7 | Varias causas plausibles simultáneas | Hipótesis múltiples con ranking y evidencia diferencial; no colapsar a una con confianza alta |
| CN8 | Evidencia insuficiente por construcción | Abstención (INSUFFICIENT_EVIDENCE) |
| CN9 | Anomalía estadística sin relevancia diagnóstica (transitorio aislado) | No promover a HYPOTHESIZED (regla de recurrencia §2.4) |

Se evalúa **acierto + abstención correcta + resistencia a contaminación**, no solo acierto.

### 8.4 Métricas por familia (unidad de análisis explícita)

| Familia | Métricas | Unidad |
|---|---|---|
| Detección | precision, recall, F1, FPR, delay de detección | ventana · episodio de fallo (nunca mezcladas) |
| Contexto/eventos | P/R/F1 de segmentación, IoU temporal, error de inicio/fin; impacto sobre F1/FPR | evento · sesión |
| **Reconocimiento de novedad relativa** | tasa de «no cubierto» correcta (P2); tasa de identificación confiada errónea (P3); curva riesgo-cobertura / AURC de la decisión cubierto-vs-no-cubierto; calibración de la confianza declarada | caso diagnóstico |
| Hipótesis | Top-1/Top-k de causa correcta, cobertura de causa, calidad de ranking, corrección de mecanismo (rúbrica GT) | caso diagnóstico |
| Evidencia/RAG | Hit Rate, Recall@k, MRR, nDCG, relevancia de evidencia | consulta · caso |
| Verificación | precisión de hipótesis aceptadas, falsos respaldos, falsos rechazos, abstención correcta, calibración | caso · hipótesis |
| Memoria | tasa de contaminación, propagación de hipótesis incorrectas, utilidad posterior (mejora en casos repetidos/variantes), recuperación de conocimiento validado | caso · secuencia longitudinal |
| Edge | latencia por etapa, RAM (instrumento corregido), CPU, tokens, t/s, tiempo de inferencia | ejecución/inferencia |

Unidades reconocidas: muestra/tick · ventana · evento · sesión · episodio de fallo ·
vehículo · caso diagnóstico · secuencia longitudinal · ejecución. Métricas de unidades
distintas nunca se agregan entre sí (anti pseudo-replicación); la unidad experimental de
la inferencia estadística es la declarada en el pre-registro (réplica/sesión/caso, según
familia).

### 8.5 Ablación de memoria

**M0** sin memoria · **M1** memoria sin validación (toda hipótesis se consolida) ·
**M2** memoria validada (§7). EXP-MEM mide: contaminación (CN5), propagación, utilidad en
casos repetidos/variantes, coste. La comparación M1 vs M2 es la prueba directa de que
*hipótesis ≠ conocimiento* tiene consecuencias medibles.

## 9. Matriz de contaminación (qué puede ver cada componente)

| Componente | train | validation | test | held-out | corpus RAG | memoria | GT | prompts |
|---|---|---|---|---|---|---|---|---|
| Detector (fit + umbral) | ✔ (solo normal) | selección de modelo | ✘ | ✘ | ✘ | ✘ | ✘ | — |
| Segmentador de eventos | ✔ | ✔ (calidad) | ✘ | ✘ | ✘ | ✘ | GT de eventos solo para evaluar | — |
| Generador de hipótesis (LLM) | ✘ (solo salidas del detector/contexto) | ✘ | caso a caso en evaluación | caso a caso | vía retrieval | según estado §7 | ✘ | plantillas congeladas |
| RAG (corpus) | — | — | — | **excluido por E-RAG** | ✔ (manifiesto hasheado) | ✘ | ✘ | — |
| Verificador | telemetría del caso | ✘ | caso a caso | caso a caso | evidencia recuperada | según estado | ✘ | criterios deterministas |
| Memoria | — | — | escribe según §7 | **estado inicial excluido por E-MEM** | ✘ | ✔ | ✘ | — |
| Juez/evaluador | ✘ | ✘ | salidas a evaluar | salidas | ✘ | ✘ | ✔ (solo el evaluador) | posiciones aleatorizadas; juez ≠ generador |
| Autor (análisis) | ✔ | ✔ | tras congelar | tras congelar | ✔ | ✔ | ✔ | ✔ |

El GT nunca es visible para ningún componente del sistema en ejecución; solo para el
evaluador. Toda violación detectada invalida el run (NO CONCLUYENTE) y se registra.
Particiones: temporales y **por sesión** (jamás por ventana); por vehículo cuando la
pregunta lo exige (H-PERS). No se impone 75/10/15: la estructura es la del pre-registro
(train solo normal / validation / test con held-out), heredada de suite-v1 y respetada por
las 22 fases (verificado por el control P4).

## 10. Pre-registro y análisis estadístico

El pre-registro B (`pre-registro-v1.md`) es el vehículo: contiene PI, hipótesis, variables,
métricas primarias/secundarias, umbrales, datasets, semillas, splits, exclusiones,
criterios de éxito y refutación, faltantes y plan de análisis. Esta alineación lo enmienda
**antes de congelar** (PI v3 + H-MAIN §5 + enmienda de cobertura efectiva F-PREREG §2.2);
tras el tag `prereg-v1.0`, cambios solo por enmienda fechada y nunca retroactiva.

Análisis: comparaciones pareadas por réplica (Wilcoxon; permutación como sensibilidad),
McNemar para decisiones binarias apareadas por caso (p. ej. cubierto/no-cubierto entre
brazos), bootstrap BCa a nivel de la unidad experimental, IC 95 %, tamaños de efecto
(δ de Cliff), Holm dentro de familia. Cada prueba se justifica por variable, distribución
y unidad — no por sofisticación; con n pequeño se reportan recuentos e IC exactos
(Clopper-Pearson) y la limitación de potencia se declara (lección del pre-registro A).

## 11. Contribuciones candidatas (condicionadas a resultados)

| Candidata | Emerge solo si |
|---|---|
| **C1** — Operacionalización experimental de «patrón no representado» mediante exclusión controlada de las fuentes de conocimiento | el protocolo §8 se ejecuta con la matriz §9 verificada (es contribución metodológica aunque H-MAIN se refute) |
| **C2** — Protocolo verificable para transformar anomalías contextuales en hipótesis contrastadas mediante evidencia | H-EXP y los pasos 5–7 de H-MAIN producen evidencia interpretable (positiva o negativa con causa) |
| **C3** — Consolidación de memoria condicionada por validación, con evaluación de contaminación y propagación de error | EXP-MEM (M0/M1/M2) se ejecuta con controles CN5/CN6 |

Las anteriores C-EVT, C-PERS, C-INT… quedan como **resultados posibles** de sus hipótesis,
no como catálogo prometido. Número final de contribuciones: el que la evidencia permita.

## 12. Delimitaciones

**Puede demostrar (bajo condiciones controladas):** detección de patrones no representados
en el conocimiento disponible · reconocimiento de cobertura insuficiente · formulación de
hipótesis evaluables · recuperación y contraste de evidencia · reducción de errores
mediante verificación · capacidad de abstención · control de contaminación de memoria ·
viabilidad computacional bajo el perfil edge evaluado.

**NO debe afirmar (salvo evidencia específica):** descubrimiento universal de averías
desconocidas · causalidad mecánica definitiva · generalización al parque vehicular ·
diagnóstico profesional certificable · superioridad universal del multiagente · validación
física en Raspberry Pi mientras solo exista emulación · que RAG elimina alucinaciones por
sí mismo · que una hipótesis generada constituye conocimiento.

**Regla epistemológica transversal:** *la afirmación nunca supera la evidencia.* Toda
conclusión se clasifica como respaldada / parcialmente respaldada / refutada /
condicionada / no concluyente. No se convierte correlación en causalidad, anomalía en
avería, hipótesis en diagnóstico, simulación en validación física, ni resultado sintético
en generalización.

## 13. DSR y su relación con esta estructura

DSR sigue siendo el marco general (identificación del problema → objetivos → diseño →
construcción → demostración → evaluación → comunicación), y **no sustituye** hipótesis,
controles, métricas ni falsación: el diseño experimental de §8 es quien responde las
hipótesis. Mapeo: fases DSR 1–2 ↔ §§1–4; 3–4 ↔ artefacto (§6); 5 ↔ demostrador
(ingeniería); 6 ↔ §§8–10; 7 ↔ memoria del TFM. La revisión sistemática (PRISMA) es el
método de la base de conocimiento, no la metodología del TFM.
