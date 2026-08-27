# Afirmaciones de novedad — clasificación para la redacción final

**TFM Mecánico IA · UAX · 2026-08-12, revisado el 2026-08-27 (alineación v4).** Cada afirmación que la memoria pueda hacer sobre novedad o vacío, clasificada por su estado de defensa. Regla transversal: toda afirmación de ausencia se formula como "en la literatura analizada no se identificó…", nunca como inexistencia absoluta.

> **⚠ Revisión del 27-ago-2026.** Con la acotación de la pregunta de investigación a
> explicación diagnóstica trazable y abstención (PI v4, ADR-0036), varias afirmaciones de
> este documento dejan de pertenecer al TFM. Se marcan **[FUERA DE ALCANCE]** y se conservan
> por trazabilidad y para el trabajo futuro; **no se eliminan**, porque documentan un
> análisis del estado del conocimiento que sigue siendo correcto. Las afirmaciones nuevas
> que la PI v4 exige están en las secciones A′, C′ y D′. Regla transversal inalterada: toda
> afirmación de ausencia se formula como «en los trabajos analizados no se identificó…»,
> nunca como inexistencia absoluta, y se evita la palabra «literatura».

## A. Defendible actualmente (con el corpus verificado de ≈153 referencias)

A1. **[REFORMULADA → A′1]** La formulación del vacío integrador de cinco ejes se sustituye por V4\* (§2.15.3): la evaluación conjunta de diagnóstico OBD-II, explicación con RAG, trazabilidad verificable y abstención. La matriz de 15 antecedentes se recodifica en `docs/alineacion_v4/02_trazabilidad.md` §3.

A2. **No se identificó ninguna comparación** entre detección de anomalías de salud vehicular condicionada a eventos operativos discretos y detección continua PID-a-PID (fundamento de C-EVT). CADD usa contexto continuo sin diagnóstico; Molina-Campoverde condiciona consumo, no salud; RAAD-LLM no es vehicular.

A3. **[FUERA DE ALCANCE]** No se identificó ninguna memoria que combine indexación por tipo de evento operativo, baseline histórico por unidad física y ejecución edge con capa de conocimiento validado (fundamento de la Event Memory dentro de C-MEM); las piezas existen por separado en robótica, TCBR, similarity-based prognostics e indexación de series, y así se citan.

A4. **[FUERA DE ALCANCE]** No se identificó un ciclo de estados de evidencia con validación previa a la consolidación aplicado a conocimiento diagnóstico declarativo y anclado en validación física (fundamento de C-MEM); los ciclos validados existentes operan sobre habilidades en benchmark (HDSO) o artefactos ejecutables (DS-Agent), y se citan como trabajos hermanos.

A5. **[FUERA DE ALCANCE]** La reformulación de V6: no consta arquitectura multiagente LLM en edge sobre telemetría OBD-II/powertrain viva con la cadena detección-RAG-hipótesis-verificación-memoria; siempre acompañada de la genealogía MAS (DDAS 2003, HoloMAS 2007) y de los multiagentes LLM no vehiculares (SAGE, LEMAD) y vehiculares de percepción (DriveAgent).

A6. La **formulación sobre datasets**: no existe dataset público identificado de telemetría OBD-II/CAN con clases de fallo mecánico confirmadas y etiquetadas; EngineAD aporta solo anomalías binarias anotadas por expertos sobre componentes PCA. (Defendible; conviene re-verificar la versión de EngineAD antes del depósito.)

A7. Las **condiciones de aplicabilidad de la descomposición multiagente** (síntesis de RQ16) como lectura original de evidencia ajena — es síntesis, no hallazgo empírico propio, y así debe presentarse.

## B. Condicionada al PRISMA formal (Scopus/WoS/IEEE con acceso institucional)

B1. La elevación de las afirmaciones A1–A5 de "en la literatura analizada (barrido web verificado)" a "en la literatura indexada consultada sistemáticamente". Hasta el PRISMA formal, mantener siempre la primera formulación.

B2. Cualquier cifra de cobertura ("X registros identificados en N bases") — actualmente solo existen los recuentos del barrido preliminar y así deben declararse.

B3. La consolidación definitiva de V1–V7 — condicionada además a la lectura a texto completo de Takara (ESWA 2025), Min (EAAI 2024) y Onsu (IoT 2025); si alguno cubre más componentes de los que muestran sus metadatos, se reajusta el vacío correspondiente.

## C. Condicionada a validación experimental (no afirmar como logro hasta tener resultados)

C1. Que la representación por eventos **reduce falsos positivos y mejora** la identificación de anomalías contextuales frente a punto/ventana en salud vehicular (hipótesis de E0–E4; la evidencia externa — CADD, WisCon, QCAD — la motiva pero no la demuestra en nuestro dominio y configuración).

C2. **[FUERA DE ALCANCE]** Que la memoria evolutiva con validación mejora el diagnóstico** y evita la propagación de errores (hipótesis de la ablación de memoria y de los escenarios de propagación).

C3. **[FUERA DE ALCANCE]** Que la descomposición multiagente aporta valor** frente al agente monolítico en nuestro contexto edge (hipótesis de A0–A6; compromiso explícito de reportar el resultado aunque favorezca al monolítico).

C4. **[FUERA DE ALCANCE]** Que el perfil jerárquico por vehículo y evento supera** al modelo global y al individual puro (hipótesis de C-PERS).

C5. Que el pipeline completo **funciona end-to-end dentro del presupuesto edge** (latencia, RAM, t/s del SLM) — las mediciones parciales existentes son preliminares y en emulación.

C6. Que las **explicaciones verificadas alcanzan exactitud factual** superior a la generación no verificada (hipótesis de C-EXP; el antecedente de Mahale demuestra el riesgo, no nuestra solución).

C7. **[RETIRADA]** La capacidad de descubrir y explicar patrones no documentados deja de ser afirmación del TFM (ADR-0036). No se reclamará descubrimiento en ninguna forma. El protocolo held-out/open-set se conserva con otra finalidad: controlar la disponibilidad de evidencia.

## D. No reclamar (la literatura ya lo cubre o la afirmación es indefendible)

D1. Novedad por **usar múltiples agentes** en diagnóstico/mantenimiento (Park, Lee, PARAM, MA-RCA, SAGE, LEMAD; genealogía DDAS/HoloMAS).

D2. Novedad del **esquema funcional multiagente+RAG+memoria+verificación en abstracto** (Jiang & Hu 2025 lo propone conceptualmente; nuestra diferencia es la instancia vehicular validada).

D3. Novedad de la **detección no supervisada de anomalías vehiculares** (Cherdo, Giannoulidis, Abboush, Geglio, EngineAD) ni de los algoritmos one-class empleados.

D4. Novedad del **concepto de anomalía contextual** (Chandola 2009) ni de la **normalidad condicionada al régimen en vehículos** (CADD 2024).

D5. Novedad del principio **"no consolidar sin validar"** (RETAIN de CBR, Voyager, DS-Agent, HDSO); lo defendible es la instancia de A4, no el principio.

D6. Novedad de la **detección de eventos/maniobras de conducción** (línea madura, E1–E9) ni de los métodos de segmentación (CPD, ClaSP, TICC, E2USD).

D7. Novedad del **RAG sobre documentación automotriz** (CarExpert/BMW, Nam, DeepTest) ni del uso de **LLM en diagnóstico** (Mahale, Lin & Miao, FD-LLM, LLMAD).

D8. Novedad de la **arquitectura edge-cloud** para mantenimiento (Bala, Jain, Huo, Syn-Diag) ni de la viabilidad de SLM/detectores en edge (Nguyen, E2USD, MLPerf Tiny).

D9. Cualquier variante de **"no existe ningún sistema similar"** en términos absolutos.

D10. Equiparar **anomalía estadística con fallo nuevo**: la definición de patrón no documentado exige recurrencia, ausencia de correspondencia documental y validación (§2.6.1); un outlier aislado nunca se reporta como descubrimiento.

D11. Presentar los resultados de la literatura sobre ventajas del multiagente como si aplicaran automáticamente a nuestro caso (las ablaciones de SAGE/MA-RCA son de otros dominios; nuestro caso se decide con A0–A6).

---

## Adenda v3 (2026-08-18) — remapeo al vacío central V\*

La alineación científica v3 sustituye V1–V7 por **V\*** con dimensiones S1–S6
(`docs/alineacion_v3/01_nucleo_cientifico.md` §3; correspondencia en
`docs/correspondencia_nomenclatura.md` §5). Efectos sobre esta clasificación:

- **A1 (vacío integrador de cinco ejes):** deja de usarse como argumento científico
  principal. Se conserva como observación de cobertura de la matriz de antecedentes
  (`docs/alineacion_v3/02_trazabilidad.md` §3): ningún trabajo revisado recorre la cadena
  detección→…→consolidación con open-set y evaluación conjunta. La novedad defendible es
  la **transición epistemológica evaluada**, no la integración tecnológica.
- **A2** sostiene S1 (contraste de H-EVT) · **A3–A4** sostienen S4 (memoria validada) ·
  **A5** sostiene S5 (condición habilitante; contribución solo si A0–A6 lo demuestra) ·
  **A6** sostiene S6 (banco held-out) · **A7** se mantiene como síntesis.
- **C7** pasa a enunciarse sobre la PI v3: la capacidad de *identificar un patrón no
  representado, reconocer la insuficiencia, hipotetizar, verificar y consolidar o
  abstenerse* solo será defendible tras EXP-MAIN-001 con la exclusión triple verificada.
- Regla de estilo v3: en documentos vivos se sustituye «literatura (analizada)» por
  «trabajos revisados/analizados» o «estado del conocimiento»; este fichero conserva su
  redacción original de 12-ago por ser documento fechado, y esta adenda fija el uso nuevo.

---

## A′. Defendible actualmente bajo la PI v4

**A′1.** La formulación de **V4\*** (§2.15.3): en los trabajos revisados no fue identificada
una evaluación conjunta de diagnóstico OBD-II real, explicación mediante RAG, trazabilidad
verificable hasta la evidencia y comportamiento seguro ante evidencia insuficiente. La
matriz de antecedentes lo documenta trabajo a trabajo, y la formulación cita dentro de sí
los antecedentes que obligan a la prudencia (Mahale et al. 2025, RAAD-LLM).

**A′2.** En los estudios analizados **no fue identificada la aplicación de atribución de
evidencia verificable** —corrección y completitud de la cita medidas por separado— a
explicaciones diagnósticas ancladas simultáneamente en documentación técnica y en
telemetría física. La atribución verificable se estudia en dominio abierto; la
explicabilidad vehicular, sobre la decisión del modelo.

**A′3.** En los trabajos analizados **no fue identificado un estudio de diagnóstico
vehicular con recuperación que manipule deliberadamente la disponibilidad de evidencia** y
evalúe si el sistema declara la insuficiencia o completa el hueco. La predicción selectiva y
las curvas riesgo-cobertura son marco maduro fuera del dominio.

**A′4.** La observación de que **la fluidez de una explicación diagnóstica no implica su
exactitud factual** es un hallazgo ajeno, no propio: procede de Mahale et al. (2025) y se
cita siempre como tal. Este trabajo lo toma como motivación, no como aportación.

*Condición de A′1–A′3, igual que B1:* hasta completar la consulta formal a las bases
indexadas, la formulación se mantiene como «en el barrido verificado no se identificó…».
La línea D (`linea_d_trazabilidad_fidelidad_abstencion.md`) debe ejecutarse antes de
consolidarlas: son afirmaciones sobre un área que la revisión anterior no barrió.

## C′. Condicionada a validación experimental bajo la PI v4

**C′1.** Que el sistema **mantiene la trazabilidad afirmación→evidencia→dato** por encima de
una atribución posicional trivial (hipótesis H-TRC).

**C′2.** Que **verificar el soporte reduce las afirmaciones no sustentadas** frente a
recuperar sin verificar (hipótesis H-GRD; hereda el umbral pre-registrado de H-EXP).

**C′3.** Que el sistema **declara evidencia insuficiente** cuando la evidencia se retira del
corpus, en lugar de completar el hueco (hipótesis H-ABS). Es el núcleo de la PI: no puede
afirmarse en ninguna forma antes de EXP-EVID-001.

**C′4.** Que la **abstención mejora la exactitud selectiva** sin colapsar la cobertura
(hipótesis H-SEL).

**C′5.** Que todo lo anterior **cabe en el presupuesto edge** (criterio transversal; las
mediciones existentes son de infraestructura, no del razonador).

## D′. No reclamar bajo la PI v4

**D′1.** Novedad por **usar RAG para explicar diagnósticos vehiculares**: existe
(Mahale et al. 2025). Lo defendible es la verificación de la trazabilidad y la abstención,
no el uso de RAG.

**D′2.** Novedad de las **métricas de fidelidad o de atribución de citas**: son marcos
existentes que este trabajo aplica y adapta, no inventa.

**D′3.** Novedad del **concepto de abstención o predicción selectiva**: tiene genealogía
anterior a los modelos de lenguaje y así se cita.

**D′4.** **Descubrimiento** de fallos, generación de conocimiento diagnóstico nuevo o
aprendizaje autónomo, en ninguna forma ni con ningún sinónimo.

**D′5.** Que una **explicación sostenida sea una explicación verdadera**: el trabajo mide
soporte y trazabilidad, no verdad mecánica. La distinción debe aparecer explícitamente en
las conclusiones.
