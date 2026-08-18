# Pre-registro del protocolo experimental — v1.0-rc1

> **NOTA DE ADOPCIÓN (M0, 2026-08-16) — no modifica el contenido de este documento.**
> Incorporado a `main` desde la rama `backup-alineacion-cientifica`, donde permanecía sin
> fusionar. **Sigue sin ser canónico:** su reconciliación con
> [`PROTO-CONF-001.md`](preregistered/PROTO-CONF-001.md) se resuelve en
> [F-PREREG](preregistered/F-PREREG_tarea.md), y el tag `prereg-v1.0` no se ha creado.
>
> **Advertencia de vigencia:** este documento está fechado el 2026-08-12 y por tanto es
> anterior a las fases F13–F22. En particular, su §11 («evidencia exploratoria previa») solo
> recoge EXP-ANOM-001/002/003; desde entonces se han ejecutado y publicado
> EXP-ANOM-005…010-R2 y AUDIT-DATA-001, todos ellos **también exploratorios**. Esa lista debe
> completarse durante F-PREREG antes de cualquier congelación. No se actualiza aquí para no
> reescribir retrospectivamente un documento fechado.

> **NOTA DE ALINEACIÓN v3 (2026-08-18) — no modifica el cuerpo de este documento fechado.**
> La alineación científica v3 (`docs/alineacion_v3/01_nucleo_cientifico.md`) fija la **PI v3**
> («identificar patrones no representados en su conocimiento disponible, generar hipótesis
> diagnósticas y validarlas mediante evidencia antes de incorporarlas como conocimiento
> reutilizable») y reformula **H-MAIN** añadiendo explícitamente el contraste con evidencia
> contradictoria y la consolidación/abstención (co-primaria P5), manteniendo P1–P4 tal como
> aquí se operacionalizan. La versión que se congele (rc2 → `prereg-v1.0`) deberá incorporar:
> (1) PI v3 en §1; (2) H-MAIN v3 en §4.6 con P5 y los controles negativos CN1–CN9;
> (3) la enmienda de cobertura efectiva del dataset confirmatorio (F-PREREG §2.2);
> (4) el §11 completado con EXP-ANOM-005…010-R2 y AUDIT-DATA-001;
> (5) la corrección del instrumento de RAM previa a cualquier criterio edge (F-PREREG §2.5).
> Nada de esto es retroactivo: ningún experimento confirmatorio se ha ejecutado.

**TFM Mecánico IA · UAX · 2026-08-12.**
**Estado: PROPUESTO (rc1) — pendiente de aprobación del autor. La congelación se produce con la aprobación + commit + tag `prereg-v1.0` (§13). Hasta entonces este documento no vincula.**

Este documento fija, **antes de ejecutar cualquier experimento confirmatorio**, las hipótesis, comparaciones, baselines, escenarios, unidades experimentales, semillas, splits, métricas, umbrales numéricos, pruebas estadísticas y criterios de aceptación/refutación del TFM. Es la frontera formal entre el diseño de la investigación y la fase de validación científica. Usa exclusivamente la nomenclatura vigente (docs/correspondencia_nomenclatura.md); las especificaciones de hipótesis derivan de docs/auditoria_alineacion_investigacion.md §4 y de docs/propuesta_alineacion_final.md §4 (PI Opción B adoptada), convirtiendo los umbrales provisionales ◊ en valores definitivos.

**Distinción central de este pre-registro:** los experimentos ya ejecutados (EXP-ANOM-001, EXP-ANOM-002, EXP-ANOM-003) son **evidencia exploratoria previa** (§11): motivan decisiones de diseño y umbrales, pero **no cuentan como evidencia confirmatoria de ninguna hipótesis** ni se combinan estadísticamente con los experimentos confirmatorios. La confirmación o refutación de cada familia recae únicamente en los experimentos pre-registrados aquí (EXP-SEG-001, EXP-ANOM-004, EXP-PERS-001, EXP-MAS-001, EXP-MEM-001, EXP-EXP-001, EXP-MAIN-001).

> **Nota de identificadores:** el identificador EXP-ANOM-003 ya está asignado a un experimento exploratorio ejecutado en F9 (refinamiento del FPR de eventos; docs/models/comparisons/event_fpr_refinement_v1.md). Los identificadores de experimentos ejecutados son inmutables; por ello el experimento confirmatorio de H-EVT se pre-registra como **EXP-ANOM-004**.

---

## 1. Pregunta de investigación e hipótesis cubiertas

**PI (Opción B, adoptada):** ¿Puede un sistema inteligente híbrido descubrir y explicar patrones de fallo vehicular previamente no documentados mediante el análisis contextual y longitudinal de datos OBD-II?
*Especificación metodológica:* el sistema se implementa mediante aprendizaje no supervisado, análisis de eventos operativos, arquitectura multiagente, modelos de lenguaje, RAG y memoria evolutiva con validación de hipótesis. Los mecanismos no forman parte del enunciado: la refutación de cualquier hipótesis parcial (en particular H-MAS, secundaria) no invalida la PI.

**Precisión terminológica vigente:** "patrones no documentados" = combinaciones de síntomas que no corresponden a un DTC activo, ni a conocimiento presente en el corpus RAG, ni a un patrón registrado en la memoria del sistema, verificables porque el fallo se inyecta sintéticamente de forma controlada (protocolo held-out/open-set triple, §7). No se afirma descubrimiento de fallos desconocidos para la ingeniería automotriz.

Familias de hipótesis contrastadas: **H-MAIN** (integradora), **H-EVT**, **H-MEM**, **H-MAS** (explícitamente secundaria), **H-PERS**, **H-EXP**, más el **criterio transversal edge** (antes H4; restricción de aceptación, no hipótesis). Correspondencia con la nomenclatura histórica: docs/correspondencia_nomenclatura.md.

## 2. Principios vinculantes

1. **Congelación previa:** ningún umbral, métrica primaria, split ni criterio de aceptación se modifica tras iniciar la ejecución del experimento correspondiente. Cambios posteriores solo mediante enmienda (§13), fechada, justificada y nunca retroactiva.
2. **Held-out intocable (RI1):** las clases held-out y los splits validation/test están congelados desde suite-v1-split-1 y jamás se usan para ajustar modelos, umbrales, prompts, corpus ni memoria.
3. **Umbrales de detección solo con train:** LOF por cuantil de train-normal; eventos por cuantil leave-one-session-out sobre train-normal. Nunca con validation ni test.
4. **Resultados negativos = resultados** (§12): se reportan con el mismo detalle que los positivos y resuelven la hipótesis igualmente.
5. **Sin exclusiones silenciosas:** todo run, fallo de ejecución o sustitución de semilla queda registrado en runs.jsonl (§9).
6. **Equidad entre brazos:** dentro de cada experimento, mismos datos, splits, semillas, reglas de evaluación y mismo SLM físico para todos los brazos; la diferencia entre brazos es exactamente la variable independiente.
7. **Evidencia exploratoria separada:** los resultados de §11 no se promedian, no se meta-analizan y no se citan como confirmación en la memoria del TFM; se citan como piloto que motivó el diseño.
8. **Benchmark inmutable:** `benchmarks/agent-diagnostics/cases_v1.yaml` (6 casos) quedó congelado antes de ver salidas de ningún modelo; su ampliación a `cases_v2` (§6.2) se congela con este pre-registro y no se modifica tras ver resultados.

## 3. Marco experimental común

### 3.1 Entorno y plataforma

Entorno 100 % emulado y reproducible: emulador OBD-II/ELM327 de obd-lab (generador de escenarios con semilla; mismo YAML + misma semilla ⇒ mismos bytes) y perfil de recursos equivalente a Raspberry Pi 5 (8 GB): contenedor con límites 4 CPU / 8 GB (x86 como proxy documentado y ARM64 vía `make arm64-build` cuando el experimento lo requiera). El hardware de cada medición se declara en su `ModelEvaluation`. RPi física permanece NOT_TESTED salvo que OS3 se ejecute; la diferencia metodológica emulación-vs-hardware se declara en la memoria.

### 3.2 Banco de datos y splits

- **Estructura de splits (anti-circularidad, idéntica a suite v1):** train = solo conducción normal; validation = normales + fallos conocidos (selección de modelo/umbral); test = normales de control FP + fallos conocidos con semillas nuevas + anomalías held-out (evaluación final, jamás para ajustar).
- **Clases de fallo conocidas (5):** `vacuum_leak`, `maf_drift`, `thermostat_stuck`, `o2_lag`, `misfire`.
- **Clases held-out (3):** `corr_break_rpm_maf` (episodios urbano y autovía), `load_coolant_decouple`, `joint_slow_drift`. Congeladas; no se añaden ni retiran clases held-out por enmienda una vez ejecutado el primer experimento confirmatorio.
- **Dataset confirmatorio `obd-lab-suite-v2` (a generar antes de EXP-SEG-001):** R = 10 réplicas de la estructura de suite v1 **con la normalidad de train ampliada** (por réplica: 22 sesiones de train — 8 urbano, 8 autovía, 3 ralentí, 3 frío — replicando la composición del train total v1.1, es decir, train v1 + el patrón de `suite_v1_train_ext.yaml`; 7 de validation; 8 de test). Decisión de diseño motivada por el piloto EXP-ANOM-003 (2 sesiones/perfil son insuficientes para representar la deriva LTFT entre sesiones), tomada aquí, antes de ejecutar los confirmatorios.
- **Semillas de suite-v2 (asignación determinista por bloques, sin colisiones):** la réplica r (1–10) usa el bloque `[10000 + 1000·r, 10000 + 1000·r + 999]`, asignando semillas consecutivas desde el inicio del bloque en el orden de escenarios listado (22 train, 7 validation, 8 test): réplica 1 → 11000–11036, …, réplica 10 → 20000–20036. Los bloques no intersecan entre sí ni con ninguna semilla existente (suite v1: 101–322; train_ext: 111–142; benchmark: 31–9001; `cases_v2`: 30000–30039). La lista materializada se commitea en `obd-lab/scenarios/suite_v2/` antes de ejecutar.
- **Semilla de runner:** 42 en todos los experimentos (idéntica a los pilotos).
- **Justificación de R = 10:** la suite v1 tiene 6 episodios de fallo en test (lecturas direccionales, no concluyentes — limitación reconocida en los pilotos). Con 10 réplicas: 40 episodios held-out, 20 episodios de fallo conocido en test y 20 sesiones normales de control por brazo, manteniendo el coste computacional dentro del presupuesto del sandbox (los pilotos completos costaron RSS pico 213 MB y minutos de CPU).

### 3.3 Unidades experimentales

| Familia | Unidad experimental | n confirmatorio |
|---|---|---|
| H-EVT, H-PERS | réplica de suite (métricas agregadas por réplica; episodio para desgloses) | 10 réplicas (40 episodios held-out) |
| H-MAS, H-EXP | caso diagnóstico (pareado entre brazos) | 40 casos (`cases_v2`) |
| H-MEM | secuencia de casos (pareada entre brazos) | 20 secuencias |
| H-MAIN | episodio held-out (detección/rechazo) y caso held-out end-to-end (calidad de hipótesis) | 40 episodios / 40 casos |

### 3.4 Criterio transversal edge (antes H4) — presupuesto fijado

Todo experimento reporta latencia por etapa, RAM pico y, cuando aplique, tokens/s y TTFT, en el perfil de §3.1. Un resultado que viole el presupuesto se reporta como **no viable aunque gane en calidad**. PI.7 se responde con el agregado de estas mediciones. Valores fijados a priori:

| Componente | Métrica | Presupuesto |
|---|---|---|
| Detección (ventana+eventos) | latencia por sesión de 30 min | ≤ 5 s |
| Detección | RSS incremental | ≤ 512 MB |
| SLM local | tamaño en disco (GGUF) | ≤ 3.5 GB |
| SLM local | RSS en inferencia | ≤ 4 GB |
| SLM local | velocidad de generación | ≥ 3 tokens/s |
| SLM local | time-to-first-token | ≤ 15 s |
| Agente end-to-end | diagnóstico completo (p95) y timeouts | p95 ≤ 120 s (= `max_execution_time`) **y** tasa de FAILED por tiempo ≤ 10 % de casos¹ |
| Sistema completo | RAM pico simultánea | ≤ 6 GB (margen ≥ 2 GB para SO) |

¹ Como el runtime aborta a los 120 s, el límite de latencia no puede excederse por construcción; la viabilidad se mide entonces por la tasa de abortos por tiempo, que sí puede fallar. Justificación del conjunto: límites del loop ya definidos en agent-runtime/06 (v1 del slice), tamaño Q4_K_M del candidato SLM (~1.9–2.3 GB) y la caracterización de coste de los pilotos. Estos valores son criterios de aceptación de viabilidad: si el smoke R2 muestra que el SLM no los cumple, el resultado es un hallazgo negativo de viabilidad, no un motivo para relajar el presupuesto.

### 3.5 Modelos e instrumentación

- **Detector primario de ventana:** `anom-lof@0.1.0` (LOF k=10, features fs1: 42, ventana 60/30), entrenado por réplica sobre su train; umbral por cuantil 1 % FPR de train-normal.
- **Brazo de eventos:** `event-baseline-z@0.2.0` (media/σ; agrupación event_type + context_signature; umbral LOSO sobre train-normal). El scoring robusto p50/percentiles queda **rechazado con evidencia** (piloto EXP-ANOM-003) y no participa.
- **Combinación:** OR por tick (sin umbral nuevo), configuración AM-WE-d (`anom-combined-we@0.2.0`).
- **SLM:** un único modelo físico compartido por todos los brazos agénticos. Candidato: Qwen2.5-3B-Instruct GGUF Q4_K_M. **Parámetro diferido D1** (§13): el SLM definitivo se fija tras el smoke R2 (instrumental, no confirmatorio) y **antes** de ejecutar EXP-MAS-001/EXP-EXP-001/EXP-MEM-001/EXP-MAIN-001; jamás se cambia tras ver resultados confirmatorios.
- **Decodificación:** temperatura 0 (greedy) en todos los brazos; una ejecución por caso y brazo; el determinismo efectivo se verifica con 3 repeticiones del 10 % de los casos (si hubiera varianza, se reporta y se pasa a 3 ejecuciones/caso con mediana, decisión tomada antes de ver métricas de calidad).
- **Contexto del agente:** entrada estructurada `cb:1` (score estructurado + contexto de evento; nunca telemetría cruda ni `anomaly_score=X` a secas), conforme a la decisión formal de agent-runtime/07.

## 4. Hipótesis confirmatorias: especificación congelada

Formato por familia: enunciado · H0/H1 · VI/VD · baselines · escenario · métricas primarias/secundarias · umbrales · análisis · criterio de aceptación/refutación. Convención de decisión (común): **aceptación** exige (i) significación estadística de la comparación primaria tras la corrección de la familia (§8) y (ii) tamaño de efecto puntual que alcance el umbral pre-registrado; **refutación** cuando el IC 95 % del efecto excluya el umbral mínimo en la dirección hipotetizada; el resto es **no concluyente** y se reporta como tal (nunca se re-ejecuta hasta obtener significación).

### 4.1 H-EVT — el contexto por eventos mejora la detección (EXP-ANOM-004)

- **Enunciado:** el baseline por evento, como señal complementaria del detector de ventana (configuración W∨E) o como representación E3, reduce falsos positivos y/o mejora la detección de anomalías contextuales frente a la detección por ventanas (E1).
- **H0:** la representación con eventos no reduce el FPR a recall igual o superior, ni mejora la detección held-out, respecto a E1. **H1:** direccional, según umbrales.
- **VI:** representación de la detección — brazos **E0** (z-score por punto, referencia inferior), **E1** (ventana 60/30 + LOF k=10; baseline), **E3** (eventos `ed:1` + baseline-z 0.2.0), **E4** (evento+vehículo; solo si obd-lab v2 con ≥2 perfiles está disponible; si no, se declara no evaluable), **W∨E** (combinación AM-WE-d). **E2 (régimen) se excluye** por decisión pre-registrada: no existe implementación validada y su contraste no es necesario para resolver H-EVT (el evento subsume al régimen como contexto).
- **VD (primarias, co-primarias declaradas):** (P1) FPR por tick en sesiones normales de test, condicionado a recall de episodios ≥ E1; (P2) recall de episodios held-out.
- **Secundarias:** F1 por tick, retardo de detección, precisión/recall/F1 por evento (`evaluation.anomaly_events`), falsos eventos por sesión normal, cobertura de scoring, coste (latencia, RSS, tamaño de modelo).
- **Escenario:** suite-v2 (10 réplicas), segmentación previamente validada por EXP-SEG-001.
- **Umbrales fijados (antes ◊):** éxito si, respecto a E1, **E3 o W∨E reduce el FPR ≥ 30 % relativo con recall de episodios igual o superior**, **o** mejora el recall medio de episodios held-out sobre las 10 réplicas en **≥ 0.15 absoluto** (granularidad de la media: 1/40 = 0.025), sin violar el presupuesto edge (§3.4). Desviaciones declaradas respecto al ◊ de la auditoría: el "+0.05 de F1 held-out" se re-expresa en la métrica por episodio del protocolo ADR-0011; y el brazo elegible "E3 o E4" pasa a "E3 o W∨E" (E4 queda condicionado a D2; W∨E es la configuración de sistema motivada por los pilotos).
- **Análisis:** diferencias pareadas por réplica (n=10); prueba de rangos con signo de Wilcoxon unilateral, α=0.05, corrección de Holm sobre los **4 contrastes primarios efectivos** (2 brazos {E3, W∨E} × 2 endpoints co-primarios {P1, P2}); tamaño de efecto: mediana de la diferencia pareada + IC 95 % bootstrap BCa (10 000 remuestras) y δ de Cliff.
- **Aceptación/refutación:** según convención común. Refutación adicional explícita: si ninguna configuración con eventos supera a E1 (o solo lo hace violando el presupuesto edge), H-EVT se refuta y el evento queda como representación semántica para el razonador, no como mejora de detección — resultado que se reporta como principal.

### 4.2 H-MEM — la memoria validada mejora el razonamiento y reduce la propagación de errores (EXP-MEM-001)

- **Enunciado:** la memoria con ciclo de validación mejora el diagnóstico en casos repetidos/variantes y consolida menos errores que la memoria sin validación, sin degradar casos nuevos.
- **H0:** sin diferencia en exactitud de reaparición vs sin-memoria; sin reducción de consolidaciones erróneas vs memoria-sin-validación. **H1:** direccional, conforme a los umbrales fijados abajo.
- **VI:** configuración de memoria — M0 (sin memoria), M1 (memoria sin validación, estilo ExpeL: consolida todo caso cerrado), M2 (memoria con ciclo de validación de 7 estados y gates de admisión, §6.3).
- **VD (primarias):** (P1) Δ exactitud diagnóstica entre 1.ª y n-ésima aparición del mismo patrón (M2 vs M0); (P2) tasa de consolidaciones erróneas (M2 vs M1) bajo inyección de conclusiones incorrectas (escenario de propagación tipo MINJA sintético, §6.3).
- **Secundarias:** contaminación del diagnóstico posterior a la inyección, exactitud en casos nuevos (no-inferioridad), precisión de recuperación de episodios, coste (tokens/latencia).
- **Escenario:** 20 secuencias de casos (composición por secuencia: 1 caso semilla de `cases_v2` + 1 repetición exacta + 1 variante + 1 caso nuevo de control; en las 10 secuencias de índice par se inyecta además una conclusión errónea controlada). **Congelación de las secuencias:** la asignación de casos a secuencias se materializa en `sequences_v1.yaml` por muestreo determinista con semilla 55000; la "variante" de un caso = mismo fallo y contexto con semilla de escenario +1 (bloque 30040–30079); el fichero se commitea junto a este pre-registro y es inmutable. Cada brazo ejecuta las mismas secuencias partiendo del mismo snapshot inicial de memoria (hash registrado); la memoria evoluciona dentro de la secuencia y se resetea entre secuencias.
- **Umbrales fijados:** éxito si M2 mejora la exactitud en reapariciones frente a M0 (mejora significativa con Δ ≥ +0.10 absoluto) **y** consolida ≥ 50 % menos errores (relativo) que M1, **sin** degradar los casos nuevos (margen de no-inferioridad: caída ≤ 0.05 absoluto).
- **Análisis:** exactitud por secuencia pareada — Wilcoxon unilateral α=0.05, Holm sobre las 2 primarias; consolidaciones erróneas: cociente de tasas con IC 95 % bootstrap por secuencia; no-inferioridad en casos nuevos con IC 90 %.
- **Aceptación/refutación:** convención común; refutación explícita si la validación no reduce consolidaciones erróneas o su coste anula la mejora → C-MEM queda como mecanismo de seguridad con resultado negativo documentado.

### 4.3 H-MAS — la descomposición multiagente aporta valor en casos complejos, considerando coste (EXP-MAS-001) — SECUNDARIA

Su refutación no afecta a C-INT ni a la PI (propuesta_alineacion_final.md §4, aprobada; docs/02 v2).

- **Enunciado:** alguna configuración multiagente (A3–A6) supera al agente monolítico en el estrato de casos complejos con sobrecoste acotado; existe un punto identificable de la curva calidad-coste donde la descomposición deja de pagar.
- **H0:** A1 iguala a A3–A6 en exactitud y alucinaciones en todos los estratos. **H1:** direccional, conforme a los umbrales fijados abajo.
- **VI:** arquitectura A0–A6 según la definición registrada en agent-runtime/12 (ADR-0018), que es la operativa: A0 ML baseline sin LLM · A1 LLM+RAG una pasada · A2 single agent+RAG (grafo lineal) · A3 multiagente+RAG (recall/critic OFF) · A4 = A3+memoria episódica · A5 = A4+memoria evolutiva · A6 = full runtime con critic y loop. *Desviación declarada:* la glosa abreviada de la auditoría §4 ("monolítico → +tools → … → +eventos") no coincide con esta escalera; prevalece ADR-0018. El baseline monolítico con LLM es A1 (A0 no contiene LLM y sirve de referencia inferior).
- **VD (co-primarias, 4 contrastes):** exactitud diagnóstica top-1 y alucinaciones (afirmaciones no soportadas) en el estrato complejo, para A3 vs A1 y A6 vs A1.
- **Secundarias:** cobertura de evidencias, contradicciones, tasa de finalización correcta, exactitud en estrato simple, curvas calidad-coste (latencia, tokens, RAM), iteraciones y tool calls, resultados de A2/A4/A5 (descriptivos).
- **Escenario:** `cases_v2` (40 casos: 20 simples / 20 complejos, §6.2), mismos casos para todos los brazos, mismo SLM físico, temperatura 0.
- **Umbrales fijados:** éxito si A3 o A6 supera a A1 en el estrato complejo en exactitud top-1 **≥ +0.15 absoluto**, o reduce alucinaciones **≥ 50 % relativo** con exactitud no inferior (margen 0.05) — en ambos casos con sobrecoste de latencia **≤ 2×** respecto a A1.
- **Análisis:** exactitud — McNemar exacto pareado por caso (estrato complejo, n=20); alucinaciones — Wilcoxon pareado sobre conteos por caso; unilateral α=0.05 con Holm sobre los **4 contrastes co-primarios** (2 brazos × 2 endpoints). Efectos: diferencia de proporciones pareada / cociente de medias, con IC 95 % bootstrap. La curva calidad-coste se reporta descriptivamente con IC.
- **Aceptación/refutación:** convención común; si A1 iguala en todos los estratos, se reporta como resultado principal (alineado con la literatura crítica) y la arquitectura se justifica solo por mantenibilidad/seguridad.

### 4.4 H-PERS — la personalización por vehículo/evento mejora frente al modelo global (EXP-PERS-001)

**Condicionado** a la ampliación de obd-lab a ≥ 3 perfiles de vehículo con firmas de normalidad distintas (parámetro diferido D2, §13: los perfiles se definen y congelan antes de generar los datos). Si la ampliación no llega a tiempo, H-PERS se declara **no evaluable en este TFM** (limitación, no refutación).

- **Enunciado:** el baseline jerárquico (flota→vehículo, por evento) iguala o supera al individual y supera al global en FPR, con arranque en frío acotado.
- **H0:** el baseline global no es peor que el jerárquico en FPR por vehículo. **H1:** direccional, conforme a los umbrales fijados abajo.
- **VI:** alcance del baseline — global de flota / individual por vehículo / jerárquico (flota→vehículo).
- **VD (primaria):** FPR por tick por vehículo (jerárquico vs global). **Secundarias:** F1 por vehículo (jerárquico vs individual, no-inferioridad), curva de arranque en frío (sesiones hasta el 90 % del F1 estable), cobertura por contexto.
- **Escenario:** suite-v2-multi = estructura de suite-v2 instanciada por perfil (3 perfiles × 10 réplicas), semillas por el esquema de bloques de §3.2 con offset por perfil `+100000·p`, p ∈ {1, 2, 3} (bloques 111000+, 211000+, 311000+; sin intersección con ningún bloque existente).
- **Umbrales fijados:** éxito si el jerárquico reduce el FPR **≥ 20 % relativo** frente al global (mediana de diferencias pareadas por vehículo-réplica), iguala o supera al individual en F1 (no-inferioridad, margen 0.03) y su arranque en frío es **≤ 4 sesiones**.
- **Análisis:** Wilcoxon pareado por vehículo-réplica (n=30), unilateral α=0.05 (una comparación primaria; sin corrección adicional); efecto: mediana + IC BCa.
- **Aceptación/refutación:** convención común; si el global no es peor, se reporta y se declara la limitación del entorno sintético (perfiles emulados quizá insuficientemente distintos) — sin forzar conclusiones.

### 4.5 H-EXP — la verificación de hipótesis mejora la exactitud factual de las explicaciones (EXP-EXP-001)

- **Enunciado:** la verificación determinista de hipótesis contra las features reduce las afirmaciones factualmente incorrectas frente a LLM solo y LLM+RAG sin verificación, manteniendo utilidad.
- **H0:** sin reducción de afirmaciones incorrectas de X2 vs X1. **H1:** direccional, conforme a los umbrales fijados abajo.
- **VI:** cadena de explicación — X0 (LLM solo), X1 (LLM+RAG), X2 (LLM+RAG+verificación determinista contra features).
- **VD (primaria):** nº de afirmaciones factualmente incorrectas por explicación (verificables contra features/GT del fallo inyectado), X2 vs X1. **Secundarias:** tasa de afirmaciones no verificables, X1 vs X0 (réplica de la antigua H2), utilidad (rúbrica 1–5), longitud/latencia.
- **Escenario:** `cases_v2` (40 casos con GT de causa), mismos casos y SLM en los tres brazos.
- **Evaluación en dos capas (§6.4):** juez LLM calibrado (juez ≠ generador, posiciones aleatorizadas) + validación manual del autor sobre una submuestra aleatoria pre-extraída del 25 % (κ de Cohen reportado; si κ < 0.6, la métrica primaria pasa a computarse solo sobre anotación manual ampliada — regla fijada aquí).
- **Umbrales fijados:** éxito si X2 reduce las afirmaciones incorrectas **≥ 50 % relativo** frente a X1, manteniendo utilidad (no-inferioridad: caída media ≤ 0.5 puntos sobre 5).
- **Análisis:** Wilcoxon pareado sobre conteos por caso (n=40), unilateral α=0.05 (una primaria); efecto: cociente de medias con IC bootstrap; utilidad con IC 90 % de no-inferioridad.
- **Aceptación/refutación:** convención común; refutación explícita si no hay reducción o la utilidad se degrada → C-EXP queda como propuesta de diseño con resultado negativo.

### 4.6 H-MAIN — el sistema integrado señala, hipotetiza y explica patrones held-out/open-set (EXP-MAIN-001)

El contraste directo de la PI. Se ejecuta en último lugar, con los mecanismos ya resueltos por las parciales.

- **Enunciado:** ante patrones retirados simultáneamente del detector, del corpus RAG y de la memoria, el sistema integrado los detecta como anómalos, los señala como no cubiertos, formula hipótesis correctas o parcialmente correctas respecto al mecanismo inyectado, con evidencia suficiente, y los explica — en lugar de identificarlos erróneamente con confianza.
- **H0:** el sistema identifica los held-out como fallos conocidos con confianza alta, o sus hipótesis no superan al control aleatorio. **H1:** el sistema cumple conjuntamente P1–P4 (abajo).
- **VI:** disponibilidad del conocimiento — condición held-out (triple retirada, §7) vs condición de conocimiento completo (cota superior).
- **Baselines:** (B1) el mismo sistema con conocimiento completo de las clases held-out (cota superior de detección/identificación); (B2) clasificador supervisado entrenado solo con fallos conocidos (cota de contraste: mide la identificación errónea confiada de un sistema cerrado).
- **VD (co-primarias, las cuatro):** (P1) recall de señalización de anomalía en episodios held-out; (P2) tasa de "no cubierto" correcta entre los held-out señalados; (P3) tasa de identificación errónea confiada (el sistema afirma un fallo conocido con confianza alta ante un held-out); (P4) calidad de las hipótesis generadas, operacionalizada **sin recurrir a "plausibilidad" subjetiva** (conforme a la operacionalización de H-MAIN aprobada en la alineación científica v2, 2026-08-12; docs/01 v2): rúbrica anclada 1–5 de **corrección respecto al mecanismo GT del fallo inyectado** (correcta / parcialmente correcta / incorrecta) más suficiencia del anclaje en la evidencia; juez calibrado + validación manual §6.4; comparada frente a control de hipótesis plantilla/aleatoria.
- **Secundarias:** calibración de confianza (ECE), retardo, desglose por clase held-out, comparación con B1/B2, tasa de outcomes honestos (INCONCLUSIVE/INSUFFICIENT_DATA donde procede).
- **Escenario:** episodios held-out de suite-v2 (40) para P1–P3; casos held-out end-to-end (40, uno por episodio) para P4. Sistema en configuración final aprobada (detección AM-WE-d + runtime según resultados de las parciales, fijado antes de ejecutar).
- **Umbrales fijados (antes "fracción pre-registrada"):** aceptación si **P1 ≥ 0.60**, **P2 ≥ 0.70**, **P3 ≤ 0.10** y **P4**: mediana de rúbrica ≥ 3/5 **y** superioridad sobre el control (test de permutación pareado, unilateral, α=0.05). Justificación de P1: el piloto alcanzó 2/4 (0.5) solo con detección y sin razonador; 0.60 exige que la integración aporte sin ser inalcanzable. P3 ≤ 0.10 operacionaliza "no identificar erróneamente con confianza" (con B2 se espera ≫ 0.10).
- **Análisis:** P1–P3 como proporciones con IC 95 % exacto de Clopper-Pearson (n=40; clúster por clase reportado como desglose); P4 con permutación pareada por caso. Sin corrección entre P1–P4: son co-primarias conjuntivas (todas deben cumplirse), lo que ya es conservador. *Desviación declarada de la convención común (§4 intro):* P1–P3 se contrastan contra umbrales absolutos, no contra un brazo comparador, por lo que la exigencia de significación se sustituye por estimación puntual + IC exacto reportado; P4 conserva el contraste inferencial.
- **Aceptación/refutación:** aceptación si las cuatro co-primarias se cumplen (P1–P3 en estimación puntual con IC reportado; P4 con significación). **Refutación** si P3 > 0.25 (límite inferior del IC 95 % > 0.10), o P1 < 0.40, o P4 no distinguible del control. Zona intermedia: no concluyente, reportada como respuesta matizada a la PI con análisis de por qué.

### 4.7 Precondición pre-registrada: calidad de la segmentación (EXP-SEG-001)

No es una hipótesis: es la condición de validez instrumental de E3/E4 y de H-MAIN (OE3). Se evalúa el segmentador `ed:1` contra el ground truth del emulador en los splits **train y validation** de las réplicas de suite-v2 (test no se toca), **antes** de EXP-ANOM-004.

- **Métricas:** P/R/F1 por tipo de evento con emparejamiento por IoU temporal ≥ 0.5, error de onset/fin, IoU medio, error de duración (protocolo docs/models/07 §2).
- **Umbral fijado (antes ◊ "p. ej."):** F1 ≥ 0.80 en los eventos mayores (IDLE, ACCELERATION, DECELERATION, CONSTANT_SPEED, ENGINE_START/STOP, VEHICLE_START_MOVING/STOPPED) promediado sobre réplicas, y error medio de onset ≤ 10 ticks. Incertidumbre: media ± IC 95 % bootstrap por réplica; el umbral se exige sobre la estimación puntual (criterio instrumental, sin prueba de hipótesis).
- **Consecuencia si falla:** E3/E4 y la parte de eventos de H-MAIN no se ejecutan hasta corregir el segmentador (la corrección no toca validation/test/held-out); el pre-registro no se altera.

## 5. Correspondencia de brazos exploratorios y confirmatorios

Para trazabilidad con la evidencia exploratoria (los informes F8/F9 usan la dimensión `anomaly_mode`): AM-W ≡ E1 · AM-E ≡ E3 · AM-WE ≡ W∨E · AM-E-d/AM-WE-d = variantes con train ampliado (adoptadas como configuración de partida aquí). Las etiquetas A0–A6 designan exclusivamente arquitecturas de agente (ADR-0018), nunca brazos de detección.

## 6. Definiciones operativas congeladas

### 6.1 Criterios exactos de segmentación de eventos

Taxonomía v1 (event-intelligence/02, `taxonomy_version=1`) con clases de conocimiento OBSERVED/INFERRED/ESTIMATED; solo los eventos OBSERVED participan en baselines de detección. Reglas v1 del detector `ed:1` (event-intelligence/04), congeladas para todos los confirmatorios:

- ACCELERATION/DECELERATION: dv/dt suavizado (media móvil 3 s), umbral ±0.8 km/h/s con histéresis (entrada 0.8 / salida 0.4), duración mínima 3 s, fusión de eventos separados < 2 s.
- IDLE: RPM > 400 ∧ v < 2 km/h ∧ duración ≥ 10 s.
- ENGINE_START/STOP: flanco RPM 0→>400 / >400→0; COLD_START si coolant en arranque < ambiente + 15 °C.
- VEHICLE_START_MOVING/STOPPED: cruce de 3 km/h con histéresis y 3 s mínimos.
- Postprocesado: filtro de mediana 3, fusión y resolución de solapes.
- `context_signature` v1 = tipo | banda de velocidad | estado térmico | banda de duración (bins log). **No se añaden dimensiones de contexto** en los confirmatorios (el piloto EXP-ANOM-003 mostró cobertura 97.6 % suficiente; el trade-off contexto/muestras queda documentado).

Cualquier cambio de estas reglas invalida la comparabilidad y exige enmienda + re-ejecución completa del experimento afectado.

### 6.2 Banco de casos `cases_v2` (H-MAS, H-EXP y secuencias de H-MEM)

Extiende `cases_v1` (6 casos, inmutable) a **40 casos** definidos por (scenario_id, seed, fault, contexto de entrada, expected_evidence, expected_outcome) **antes de ver salidas de ningún modelo**. Composición fijada: 20 simples y 20 complejos; distribución: las 5 clases conocidas (≥ 3 casos/clase, incluyendo variantes ambiguas), 8 casos sin fallo (control de sobre-diagnóstico y distractores, p. ej. arranque frío normal), 6 casos con datos deliberadamente insuficientes. **`cases_v2` no contiene clases held-out** (decisión pre-registrada: minimiza superficies de contaminación; H-MAIN usa exclusivamente los episodios held-out de suite-v2). Semillas de casos: bloque 30000–30039. El fichero `cases_v2.yaml` se materializa y commitea junto a este pre-registro; tras el commit es inmutable (ampliaciones = v3, nunca retroactivas).

**Definición operativa de caso simple/complejo (H-MAS), fijada por caso antes de ejecutar:** un caso es **complejo** si cumple al menos una: (i) más de una hipótesis de causa compatible con la evidencia inicial (definido por la matriz fallo→firmas del generador), (ii) datos incompletos o contexto distractor (p. ej. arranque frío normal), (iii) `expected_outcome` ∈ {inconclusive, insufficient_data}. **Simple** en caso contrario (firma clara de un único fallo conocido con datos completos). La etiqueta queda escrita en `cases_v2.yaml` y no se reasigna tras ver resultados.

### 6.3 Condiciones de actualización de memoria (H-MEM y todo experimento con memoria)

- **Ciclo de estados (7):** observación → anomalía → patrón candidato → hipótesis → validación → confirmada/descartada → conocimiento. Consolidación de patrones aprendidos: CANDIDATE → EMERGING → VALIDATED.
- **Gate de admisión (brazo M2):** solo se consolida un caso cuyo hipótesis-top haya superado la verificación determinista contra features **y** con ≥ 2 piezas de evidencia de soporte (`minimum_evidence` del runtime) **y** outcome ∈ {probable, confirmed}; INCONCLUSIVE/INSUFFICIENT_DATA/FAILED no consolidan (se registran como episodios, no como conocimiento).
- **Brazo M1 (sin validación):** consolida todo caso cerrado con su hipótesis-top, sin gate — es el contraste tipo ExpeL.
- **Aislamiento entre brazos:** cada brazo parte del mismo snapshot inicial (hash registrado); la memoria evoluciona solo dentro de la secuencia; reseteo entre secuencias; prohibido compartir memoria entre brazos o experimentos.
- **Escenario de propagación (tipo MINJA sintético):** en 10 de las 20 secuencias se inserta, mediante la interfaz normal de cierre de casos, una conclusión errónea controlada (diagnóstico incorrecto con evidencia aparentemente coherente, generada por plantilla desde el GT). VD: cuántas veces cada brazo la consolida y cuánto contamina los diagnósticos posteriores de la secuencia.

### 6.4 Evaluación de explicaciones e hipótesis (H-EXP, H-MAIN, H-MAS)

- **Afirmación factual:** unidad = afirmación atómica verificable contra features/GT (extracción por reglas + revisión); incorrecta si contradice el GT o las features de la sesión.
- **Juez LLM calibrado:** modelo ≠ generador (parámetro diferido D1b, fijado junto a D1 antes de los confirmatorios agénticos), prompts de juez congelados en el harness, posiciones/orden aleatorizados con semilla 42, temperatura 0.
- **Validación humana:** submuestra aleatoria pre-extraída del 25 % de los ítems juzgados, anotada por el autor a ciegas del brazo; se reporta κ de Cohen juez-humano. Regla fijada: κ ≥ 0.6 habilita el juez para el resto; κ < 0.6 → la métrica primaria se computa solo sobre anotación manual ampliada al 50 %.
- **Rúbrica de hipótesis (H-MAIN P4):** escala anclada 1–5 referida al mecanismo GT del fallo inyectado (1 = mecanismo incorrecto o sin anclaje en la evidencia; 3 = mecanismo parcialmente correcto, anclado en parte de la evidencia; 5 = mecanismo correcto, anclado, con discriminadores propuestos). **Control:** hipótesis plantilla/aleatoria extraída del pool de causas conocidas, mismo formato. La rúbrica exacta se congela en el harness junto a este documento.
- **Outcomes honestos:** INCONCLUSIVE e INSUFFICIENT_DATA son resultados correctos cuando proceden (obligatorios en los casos diseñados para ello) y puntúan como acierto en esos casos; `unsupported_certainty` es error explícito.

## 7. Protocolo anti-contaminación de H-MAIN (retirada triple)

H-MAIN es especialmente sensible a fuga de conocimiento: un patrón "no documentado" que aparezca en el entrenamiento, el corpus recuperable, la memoria o los prompts invalida el experimento. Qué se retira, exactamente:

1. **Datos (detector):** el train es solo normalidad por construcción; validation contiene únicamente fallos conocidos. Ninguna sesión con clase held-out existe fuera del split test.
2. **Corpus RAG:** se excluye todo documento que describa las firmas held-out o sus mecanismos (desacoplo RPM↔MAF, dinámica térmica muerta carga↔coolant, deriva lenta conjunta MAF/avance), incluidas descripciones de DTC directamente asociables. La lista de documentos excluidos y el hash del corpus congelado se registran antes de ejecutar.
3. **Memoria:** el snapshot inicial contiene solo casos de fallos conocidos; se verifica por hash + auditoría (abajo).
4. **Prompts, configs y few-shots:** ningún prompt del sistema, descripción de herramienta, ejemplo o config menciona las clases held-out ni sus firmas. Los nombres `corr_break_rpm_maf`, `load_coolant_decouple`, `joint_slow_drift` existen solo en el harness de evaluación, nunca en la entrada del sistema.

**Tabla de contaminación (se verifica y firma antes de EXP-MAIN-001; "No" = verificado ausente):**

| Elemento (clase de fallo) | Train detector | Validation (ajuste) | Corpus RAG | Memoria inicial | Prompts/config | Test |
|---|---|---|---|---|---|---|
| vacuum_leak (conocido) | No¹ | Sí | Sí | Sí | Sí² | Sí |
| maf_drift (conocido) | No¹ | Sí | Sí | Sí | Sí² | Sí |
| thermostat_stuck (conocido) | No¹ | Sí | Sí | Sí | Sí² | No³ |
| o2_lag (conocido) | No¹ | Sí | Sí | Sí | Sí² | No³ |
| misfire (conocido) | No¹ | Sí | Sí | Sí | Sí² | No³ |
| **corr_break_rpm_maf (held-out)** | **No** | **No** | **No** | **No** | **No** | **Sí** |
| **load_coolant_decouple (held-out)** | **No** | **No** | **No** | **No** | **No** | **Sí** |
| **joint_slow_drift (held-out)** | **No** | **No** | **No** | **No** | **No** | **Sí** |

¹ El train de los detectores es exclusivamente conducción normal (anti-circularidad §3.2). ² Como conocimiento legítimo del dominio (descripciones de DTC/fallos conocidos), no como pistas de casos concretos. ³ En suite v1/v2 el test incluye con semillas nuevas solo vacuum_leak y maf_drift; el resto de conocidos se evalúa en validation.

**Procedimiento de auditoría (ejecutable y registrado):** (a) búsqueda léxica automatizada de los identificadores y descriptores de las clases held-out (lista de términos congelada con el corpus) sobre corpus RAG, snapshot de memoria, prompts y configs; (b) búsqueda por similitud de embeddings (top-20 por firma held-out) con revisión manual de los recuperados; (c) hashes del corpus, del snapshot de memoria y de los prompts registrados en runs.jsonl; (d) resultado de la auditoría archivado como artefacto del experimento. Cualquier positivo → se retira el elemento, se re-audita y se documenta; si la retirada altera un experimento ya ejecutado, ese run queda invalidado y se repite.

## 8. Plan estadístico global

- **Nivel de significación:** α = 0.05; pruebas unilaterales donde la dirección está pre-especificada (todas las primarias lo están); exactas/no paramétricas por defecto (n pequeños): Wilcoxon de rangos con signo pareado, McNemar exacto, permutación pareada, IC binomiales de Clopper-Pearson.
- **Tamaño de efecto siempre junto al p-valor:** mediana de diferencias pareadas, δ de Cliff o diferencia/cociente de proporciones, con IC 95 % bootstrap BCa (10 000 remuestras) o exacto según el caso.
- **Múltiples comparaciones:** corrección de Holm-Bonferroni **dentro de cada familia de hipótesis** sobre sus contrastes primarios efectivos (H-EVT: 4 — 2 brazos × 2 endpoints; H-MAS: 4 — 2 brazos × 2 endpoints; H-MEM: 2; H-PERS: 1; H-EXP: 1; H-MAIN: co-primarias conjuntivas sin corrección, ya conservador). No se corrige entre familias: cada familia se acepta/refuta por separado y así se reporta (decisión declarada, estándar en pre-registros con hipótesis independientes). Las métricas secundarias son descriptivas: se reportan con IC y **sin** pruebas de hipótesis ni afirmaciones de significación.
- **Potencia (declaración honesta):** con n = 10 réplicas (Wilcoxon pareado) solo son detectables efectos grandes y consistentes; con n = 20 por estrato (McNemar) el efecto mínimo detectable ronda diferencias de proporción ≥ 0.3 con discordancias favorables. Consecuencia asumida: los umbrales pre-registrados exigen efectos grandes; un efecto pequeño real quedará "no concluyente" y se reportará como tal — preferible a inflar n con pseudo-réplicas del mismo simulador y fingir potencia.
- **Sin paradas opcionales ni repesca:** no se añade n, no se repiten runs "para confirmar", no se cambia de métrica tras ver datos. Un experimento se ejecuta una vez por su config congelada (re-ejecuciones solo por fallo técnico documentado, §9).

## 9. Manejo de fallos de ejecución

- **Generación de datos:** si un escenario no genera (error del emulador), semilla sustituta = semilla + 50 000, documentada en runs.jsonl con el error original; nunca se elige a mano.
- **Runtime agéntico:** reintentos internos según config congelada (`max_tool_retries` 2); outcome FAILED cuenta como diagnóstico incorrecto en exactitud y se reporta aparte como tasa de finalización; los casos FAILED **no se excluyen** del denominador.
- **Crash del runner:** relanzamiento completo de la réplica desde la config determinista (por construcción reproduce los mismos resultados); registrado.
- **Presupuesto edge excedido:** el run se completa y se reporta como no viable (§3.4); no se descarta.
- **Registro:** todo run con `git_sha`, config, entorno, hardware y semillas en runs.jsonl + registro formal (Experiment/TrainingRun/ModelEvaluation), como en los pilotos.

## 10. Tabla maestra de experimentos

| ID | Hipótesis | Pregunta/RQ | Comparación | Baseline | Escenario | Métrica primaria | Umbral | Seeds | Split | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| EXP-SEG-001 | precondición H-EVT/H-MAIN (OE3) | PI.2 | segmentador `ed:1` vs GT emulador | GT | suite-v2 (10 réplicas) | F1 eventos mayores (IoU ≥ 0.5) | ≥ 0.80; onset ≤ 10 ticks | fórmula §3.2; runner 42 | train+validation | pre-registrado |
| EXP-ANOM-004 | H-EVT | PI.2 | E0/E1/E3(/E4)/W∨E | E1 (LOF ventana) | suite-v2 (10 réplicas) | FPR rel. a recall ≥ E1; recall episodios held-out | −30 % rel.; +0.15 abs. | fórmula §3.2; runner 42 | train/val/test congelados | pre-registrado |
| EXP-PERS-001 | H-PERS | PI.6 | global / individual / jerárquico | global | suite-v2-multi (3 perfiles × 10) | FPR por vehículo | −20 % rel.; F1 no inferior (0.03); arranque ≤ 4 sesiones | bloques §3.2 + 100000·p | ídem | pre-registrado, condicionado a obd-lab v2 (D2) |
| EXP-MAS-001 | H-MAS (secundaria) | PI.5 | A0–A6 | A1 | cases_v2 (20 complejos / 20 simples) | exactitud top-1 y alucinaciones, estrato complejo | +0.15 abs. o −50 % rel. alucinaciones; coste ≤ 2× | casos 30000–30039; temp 0 | casos congelados | pre-registrado, requiere D1 (SLM) |
| EXP-MEM-001 | H-MEM | PI.4 | M0 / M1 / M2 | M0 y M1 | 20 secuencias (10 con inyección) | Δexactitud reaparición; consolidaciones erróneas | ≥ +0.10 abs.; −50 % rel.; casos nuevos no inferiores (0.05) | sequences_v1 (semilla 55000; variantes 30040–30079) | secuencias congeladas; snapshots hasheados | pre-registrado, requiere D1 |
| EXP-EXP-001 | H-EXP | PI.3 | X0 / X1 / X2 | X1 (LLM+RAG) | cases_v2 (40) | afirmaciones incorrectas / explicación | −50 % rel.; utilidad no inferior (−0.5) | ídem EXP-MAS-001 | casos congelados | pre-registrado, requiere D1 + corpus R3 |
| EXP-MAIN-001 | H-MAIN | PI (núcleo) | held-out triple vs conocimiento completo | B1 cota superior; B2 clasificador supervisado | suite-v2 held-out (40 episodios / 40 casos) | P1 señalización; P2 no-cubierto; P3 misid. confiada; P4 rúbrica | ≥ 0.60; ≥ 0.70; ≤ 0.10; ≥ 3/5 y > control | §3.2; runner 42 | held-out congelado + auditoría §7 | pre-registrado, se ejecuta el último |

Instrumentales (no contrastan hipótesis; sin criterio de aceptación científico): R2 (smoke + benchmark `cases_v1` del SLM; fija D1), R3 (corpus e índice RAG con métricas IR descriptivas: hit rate, MRR, nDCG), A2/A3 (validación ARM64), generación de suite-v2.

**Dependencias y orden:** suite-v2 → EXP-SEG-001 → EXP-ANOM-004 → (si D2) EXP-PERS-001; en paralelo R2 (fija D1) → R3 → EXP-EXP-001, EXP-MAS-001, EXP-MEM-001 → configuración final → EXP-MAIN-001 (último). El criterio transversal edge aplica a todos.

## 11. Evidencia exploratoria previa (NO confirmatoria)

Los tres experimentos siguientes se ejecutaron **antes** de este pre-registro. Se registran aquí como pilotos exploratorios: informan el diseño y los umbrales anteriores; **no** se usan como evidencia de aceptación/refutación de ninguna familia, **no** se combinan estadísticamente con los confirmatorios y sus resultados se conservan tal como fueron obtenidos, sin reinterpretación posterior a la fijación de hipótesis.

### 11.1 EXP-ANOM-001 (F3; piloto de selección de detector)

Comparación de baselines no supervisados sobre suite v1. Resultado: LOF k=10 mejor compromiso; OC-SVM segundo; z-score/IForest rechazados. Decisión motivada: LOF como detector primario (precondición operativa de H-EVT, antigua H1). Informe: docs/models/comparisons/anomaly_detectors_v1.md.

### 11.2 EXP-ANOM-002 (F8, 2026-08-12; piloto window vs event vs both)

- **Configuración:** `ai-models/configs/exp-anom-002.yaml` + runner `e2_window_vs_event.py`; suite v1 (21 sesiones), split suite-v1-split-1, semilla 42; brazos AM-W / AM-E / AM-E-NOCTX / AM-WE; marco común por tick; umbral LOF cuantil train (0.1632); umbral de eventos LOSO train-normal; held-out intocable; sin LLM.
- **Resultados observados (test):** AM-W F1 0.67 / FPR 0.067 / held-out 2/4 / retardo 15 s (mejor detector individual); AM-E F1 0.58 / FPR 0.149 (concentrado en normales de autovía); AM-WE recall 0.54→0.63 y retardo 15→4.2 s con FPR 0.189. En el held-out relacional urbano `t-corrbreak-u`: AM-E R = 0.73 / 17 s vs LOF R = 0.25 / 30 s. Ablación: `context_signature` aporta (F1 0.58 vs 0.52; held-out 2/4 vs 1/4). `t-coolfreeze` y `t-jointdrift` indetectados por todos los brazos. Eventos computacionalmente más baratos (38 KB vs 142 KB; 9 vs 28 ms/sesión).
- **Decisiones metodológicas que motivó:** entrada del sistema agéntico = ventana+LOF primario con eventos como evidencia contextual complementaria; necesidad de más normalidad de train y de métrica por-evento (→ EXP-ANOM-003); benchmark agent-diagnostics declarado inmutable tras ver resultados; el resultado direccional en `t-corrbreak-u` motiva — no decide — la comparación confirmatoria EXP-ANOM-004.

### 11.3 EXP-ANOM-003 (F9, informe 2026-08-13; piloto de diagnóstico del FPR)

- **Configuración:** `configs/exp-anom-003.yaml` + runner `e3_event_refinement.py`; dataset v1.1 = v1 + 16 sesiones normales solo de train (semillas 111–142); validation/test/held-out congelados e idénticos; brazos de atribución limpia (AM-W-v1/v2, AM-E-v1/d/v2, combinaciones).
- **Resultados observados (test):** causa del FPR = insuficiencia de normalidad (descomposición de varianza: LTFT en autovía, ratio entre/intra 1.56); AM-E-d FPR 0.149→0.008 con event precision 0.98 y cobertura 97.6 %; trade-off: `t-corrbreak-u` R 0.73→0.41 (sigue detectada); AM-WE-d F1 0.70 / FPR 0.071 / held-out 2/4. Negativos conservados: scoring robusto rechazado (held-out 0/4); LOF reentrenado con v1.1 empeora (FPR 0.067→0.142) — la calibración es por detector.
- **Decisiones metodológicas que motivó:** ampliar la normalidad de train en el diseño confirmatorio (§3.2); fijar `event-baseline-z@0.2.0` y AM-WE-d como configuración de partida (§3.5); no fragmentar `context_signature` (§6.1); añadir métricas por-evento como secundarias (§4.1).

### 11.4 Límite de uso

Ningún número de §11 entra en los análisis de §4; ninguna tabla de la memoria del TFM presentará resultados exploratorios y confirmatorios agregados. En la memoria, los pilotos aparecen en la sección de metodología/diseño (como justificación) y los confirmatorios en resultados.

## 12. Análisis de errores, amenazas a la validez y política de resultados negativos

### 12.1 Análisis de errores (obligatorio en cada experimento)

Detección: matriz por clase de fallo, FP por perfil de conducción (urbano/autovía/ralentí/frío), distribución de retardos, desglose por tipo de evento, casos indetectados con inspección de firmas. Agénticos: taxonomía de error fijada — percepción (evidencia no leída), evidencia (mal atribuida), razonamiento (hipótesis incorrecta con evidencia correcta), verificación (afirmación no soportada que pasa), formato (salida inválida) — anotada por caso fallido; trazas completas archivadas. H-MAIN: análisis específico de cada identificación errónea confiada y de cada held-out no señalado.

### 12.2 Amenazas a la validez (declaradas a priori)

- **Interna:** fuga de conocimiento (mitigación: §7); ajuste inadvertido sobre test (mitigación: umbrales train-only, splits congelados, runs registrados); contaminación entre brazos de memoria (snapshots hasheados); deriva del harness entre brazos (mismo código, misma versión, tests en verde antes de cada experimento).
- **De constructo:** juez LLM sesgado (juez ≠ generador, aleatorización, calibración humana con κ y regla de fallback §6.4); la calidad de hipótesis se operacionaliza por corrección respecto al GT (rúbrica anclada + control), no por "plausibilidad" subjetiva; métricas por tick penalizan estructuralmente eventos largos (se reportan tick-level y event-level siempre, ambas pre-registradas).
- **Externa:** datos 100 % sintéticos de un único simulador (las réplicas de suite-v2 comparten generador: son réplicas de muestreo, no de entorno); 1–3 perfiles de vehículo; emulación de recursos ≠ RPi física (declarado; OS3 lo cerraría). Las conclusiones se enunciarán como válidas para el entorno emulado, con la generalización como trabajo futuro.
- **De conclusión estadística:** n pequeños y efectos exigidos grandes (§8); co-primarias conjuntivas en H-MAIN; riesgo de leer secundarias como confirmatorias (prohibido por §8).

### 12.3 Política de resultados negativos

Toda familia refutada o no concluyente se reporta en la memoria con el mismo nivel de detalle que una aceptada, incluyendo tamaño de efecto, IC y análisis de errores. Precedente ya sentado en los pilotos (evento-como-sustituto negativo; scoring robusto rechazado; LOF-v2 no adoptado). La refutación de H-MAS está explícitamente prevista como resultado publicable de primera clase (hipótesis secundaria); la refutación de H-MAIN es una respuesta negativa válida a la parte fuerte de la PI y se reportará con el análisis de por qué. Ningún resultado negativo motiva re-ejecutar con umbrales relajados.

## 13. Congelación, enmiendas y parámetros diferidos

- **Congelación:** este documento entra en vigor con la aprobación del autor + commit + tag `prereg-v1.0`. El hash del commit se cita en la memoria del TFM como referencia del pre-registro.
- **Enmiendas:** numeradas (ENM-001, …), fechadas y justificadas en una sección al final de este fichero; solo pueden afectar a experimentos **aún no iniciados**; nunca modifican retroactivamente umbrales, métricas ni criterios de un experimento ejecutado o en curso.
- **Parámetros diferidos (los únicos):**
  - **D1 — SLM definitivo** (y **D1b** — modelo juez): se fijan tras el smoke instrumental R2 y antes del primer experimento confirmatorio agéntico, mediante enmienda que registra la elección y su justificación.
  - **D2 — perfiles de vehículo de obd-lab v2** (para EXP-PERS-001 y el brazo E4): ≥ 3 perfiles con firmas de normalidad distintas, definidos y congelados antes de generar suite-v2-multi.
  - Ningún otro parámetro queda abierto. Si la ejecución revela un parámetro no previsto, se fija por enmienda **antes** de ejecutar el experimento afectado y se declara en la memoria.
- **Publicación:** el pre-registro y sus enmiendas viven en `docs/experiments/` del monorepo (histórico completo vía git), citados desde el capítulo de metodología.

---

*Documentos fuente: docs/propuesta_alineacion_final.md (aprobada) · docs/auditoria_alineacion_investigacion.md §4 (umbrales ◊ origen) · docs/correspondencia_nomenclatura.md · obd-lab/scenarios/suite_v1.yaml y suite_v1_train_ext.yaml · ADR-0011/0018 · agent-runtime/06, 07, 08 y 12 · event-intelligence/02, 04, 07 y 11 · docs/models/07 · benchmarks/agent-diagnostics · informes F3/F8/F9 y comparaciones asociadas.*
