# Estado del Arte — Segunda Entrega: ampliación del corpus, auditoría de EngineAD y reevaluación adversarial del vacío

**Proyecto:** TFM — Sistema inteligente híbrido Edge–Cloud para diagnóstico y mantenimiento predictivo de vehículos con OBD-II y Raspberry Pi (UAX)
**Fecha:** 2026-08-12 · **Iteración:** 2 de 4 · **Continúa:** `entrega1_revision_sistematica.md` (v1.1)
**Identificadores:** esta entrega añade los bloques M (memoria/validación), P (personalización y CL seguro), X (XAI puente decisión↔causa), D (competidores directos) y R (candidatos E7 recuperados). Se mantienen A/B/C (barrido Fase 1) y N (Entrega 1).

---

## 0. Resumen ejecutivo de la iteración

Se añaden **39 referencias nuevas verificadas** (corpus total ≈ 110). Los cuatro resultados que cambian el estado del análisis:

1. **EngineAD queda auditado** (§2): es utilizable como contraste externo *a nivel de método*, pero publica solo 8 componentes PCA (sin semántica física), con etiqueta binaria de juicio experto y acceso restringido CC BY-NC. La formulación sobre datasets públicos queda actualizada y acotada.
2. **La novedad de V2 se recorta pero sobrevive** (§3): se identificó un preprint de 2026 (HDSO) con un ciclo de validación de hipótesis casi isomorfo al nuestro, aplicado a *habilidades* de agente en benchmark. La reformulación defendible de V2 pasa por dominio (conocimiento diagnóstico declarativo), granularidad (estados pre-hipótesis) y naturaleza de la validación (anclada en el mundo físico).
3. **La personalización por vehículo gana respaldo empírico** (§5): hay evidencia cuantitativa de que la adaptación por unidad supera al modelo global bajo no-IID, y evidencia industrial (Mercedes-Benz) de que la calibración por entidad no transfiere entre vehículos. El patrón maduro es jerárquico: flota como prior/normalizador, individuo como señal.
4. **El vacío sobrevive a la búsqueda adversarial, reformulado** (§7): aparecieron en 2025–2026 trabajos que cubren pares de componentes (LLM+telemetría vehicular temporal; LLM edge-cloud personalizado; TSAD embarcado evaluado por un OEM; RAG documental automotriz industrial). Ninguna afirmación de novedad por componente aislado es defendible; la integración y la memoria con validación siguen libres.

**Nota sobre la consulta formal a bases de datos (transparencia):** desde este entorno no hay acceso institucional a Scopus, Web of Science ni IEEE Xplore, por lo que los recuentos formales por base **no pueden generarse aquí sin fabricarlos** — y no se fabricarán. En su lugar, §9 entrega la **sintaxis exacta lista para ejecutar** con el acceso institucional de la universidad, junto con la plantilla de registro de recuentos por base para construir el flujo PRISMA formal. Los recuentos de esta iteración (§10) siguen siendo, como en la Entrega 1, del barrido web con verificación en editor.

---

## 1. Ajustes aplicados desde la Entrega 1 (v1.1)

Corregida la afiliación institucional (UAX); los recuentos de la E1 quedaron etiquetados como barrido preliminar por web, no como PRISMA definitivo; la fila "TFM (propuesta)" de la matriz distingue ahora entre capacidades implementadas, propuestas y por validar. Desde esta entrega, la matriz incorpora las dos columnas nuevas: **Nivel de validación** (Simulación / Dataset público / Banco-HIL / Vehículo real / Flota real / Despliegue operacional; se anota "propietario" cuando el dato real no es público) y **Tipo de desconocido** (Outlier estadístico / Anomalía no vista / Fallo open-set / Fallo mecánico nuevo / No aplica).

---

## 2. Auditoría de EngineAD (R0)

**Fuentes:** [arXiv:2603.25955](https://arxiv.org/html/2603.25955v1) (asociado al AAAI 2026 Workshop ASTAD), dataset en Borealis/McGill Dataverse DOI [10.5683/SP3/TX13P1](https://borealisdata.ca/dataset.xhtml?persistentId=doi%3A10.5683%2FSP3%2FTX13P1) (metadatos verificados vía DataCite), repositorio [Armanfard-Lab/EngineAD](https://github.com/Armanfard-Lab/EngineAD). Datos aportados por Preteckt, Inc. (tres coautores de la empresa).

| Dimensión | Hallazgo verificado |
|---|---|
| Licencia | **CC BY-NC 4.0 + acceso restringido** (formulario de solicitud + aprobación en Borealis). Uso académico con atribución; sin uso comercial; sin redistribución. |
| Vehículos | 25 camiones comerciales, mismo modelo/fabricante (anonimizados), 6 meses (ago–feb, año no consta). |
| Señales | 13 sensores de motor vía CAN ("presión, temperatura, caudal de combustible, régimen, entre otros"); **los nombres no se enumeran** y **lo publicado son 8 componentes PCA (95 % varianza), no las señales físicas** — deliberado, para proteger información propietaria. |
| Muestreo | Frecuencia CAN original no consta; remuestreo a 1 Hz; ventanas de 300 pasos (5 min); StandardScaler solo-train. |
| Definición de anomalía | "Signos tempranos de defectos potenciales de motor" juzgados por un equipo de técnicos a partir de trazas + informes de mantenimiento. **No es fallo confirmado por reparación; no hay clases/tipos de fallo; etiqueta binaria.** No consta criterio operativo ni acuerdo inter-anotador. |
| Particiones | Protocolo **intra-vehículo** por camión: train = 70 % de segmentos normales; test = 30 % restante + todas las anomalías. Sin validación formal; **sin split cross-vehicle**. |
| Benchmark | 9 métodos one-class; umbral = percentil 95 de scores en train; F1 sobre clase anómala. Medias de flota: empate práctico 0,64–0,65 en los 9 métodos (deep no supera a clásicos). **Variabilidad inter-vehículo: F1 de 0,93 (camión 19) a 0,21 (camión 25) con el mismo método.** |
| Limitaciones declaradas | Anomalías "altamente no uniformes entre la flota"; en ciertos vehículos "excepcionalmente sutiles o contextuales". No declaran: ruido de etiquetas, pérdida de semántica física por PCA, ausencia de protocolo cross-vehicle. |

**Veredicto:** sirve como **dataset externo de contraste a nivel de método** (¿generaliza nuestro detector one-class a otra telemetría vehicular real?), no a nivel de señal (sin semántica de PIDs no se pueden validar reglas físicas ni comparar canal a canal con nuestro banco). Su protocolo one-class encaja con el nuestro; sus 25 experimentos por camión permiten reproducir el análisis de variabilidad como motivación del perfil por vehículo. Reservas a declarar: etiqueta binaria de juicio experto sin confirmación por reparación; acceso restringido (planificar la solicitud con antelación; ~50 ficheros de 103–488 MB).

**Formulación actualizada y defendible sobre datasets públicos (sustituye a H-EA1):**

> "Hasta donde alcanza la literatura pública analizada, no existe ningún dataset abierto de telemetría OBD-II/CAN de vehículos en operación con *clases de fallo mecánico confirmadas y etiquetadas*. Lo más cercano, EngineAD (Hojjati et al., 2026, preprint), aporta *anotaciones binarias de anomalía* —signos tempranos de fallo potencial juzgados por técnicos a partir de trazas e informes de mantenimiento, sin confirmación por reparación ni taxonomía de averías— y publica los datos proyectados a 8 componentes PCA, sin las señales físicas originales. En consecuencia, la validación externa sobre EngineAD debe entenderse como contraste de detección de anomalías reales anotadas, no como evaluación de diagnóstico sobre clases mecánicas de fallo; la inyección sintética de fallos con firma física conocida sigue siendo la práctica del área para evaluar diagnóstico."

**Clasificación matriz:** Nivel de validación = Dataset público (procedencia: flota real) · Tipo de desconocido evaluable = **Anomalía no vista** (no permite fallo open-set por tipo ni fallo mecánico nuevo).

---

## 3. Línea de memoria profundizada (M1–M10) y reevaluación de V2

Objetivo doble: mapear la literatura de memoria con validación de evidencia y **someter V2 a refutación activa**. Todas verificadas el 12-08-2026.

### 3.1 Fichas

**M1. Shang & Yang (2026) [preprint] — HDSO: Hypothesis-Driven Skill Optimization for LLM Agents.** [arXiv:2606.22330](https://arxiv.org/html/2606.22330v1). **El hallazgo más importante de la iteración y la mayor amenaza a V2.** Un "Curator" observa trazas del ejecutor → propone hipótesis estructuradas con condición de aplicabilidad, efecto esperado y **plan de falsación** → validación experimental por etapas (screening → confirmación, ejecuciones pareadas control/tratamiento con puertas métricas y p-valor) → clasificación validated / needs revision / wrong direction / insufficient evidence → **solo lo validado entra al repositorio; lo rechazado queda en un ledger auditable**. ALFWorld; +6,9/+7,8 puntos; robusto a 20 % de corrupción de etiquetas. Diferencias con V2: opera sobre *habilidades procedimentales* del agente (no conocimiento diagnóstico declarativo), valida por A/B intra-benchmark (no contra el mundo físico), y no modela los estados pre-hipótesis (OBSERVACIÓN→ANOMALÍA→PATRÓN CANDIDATO). Veredicto ciclo de evidencia: **Sí completo** (en su dominio). Cercanía conceptual: **Alta**.

**M2. Guo et al. (2024) — DS-Agent (ICML 2024, PMLR v235).** [PMLR](https://proceedings.mlr.press/v235/guo24b.html) · [arXiv:2402.17453](https://arxiv.org/abs/2402.17453). Instancia el ciclo CBR **Retrieve-Reuse-Revise-Retain** con LLM: solo reincorpora al banco de casos soluciones revisadas con rendimiento verificado por ejecución. Veredicto: **Parcial-alto** — el RETAIN condicionado a revisión es el antecedente CBR explícito de "solo retener lo validado"; sin estados de evidencia graduados, validación = métrica inmediata. Cercanía metodológica: **Alta**.

**M3. Wang et al. (2023) [preprint] — Voyager.** [arXiv:2305.16291](https://arxiv.org/abs/2305.16291). Self-verification por ejecución antes de almacenar habilidades. Veredicto: **Parcial** — gate único binario, sin revisión posterior. Cercanía: Media.

**M4. Zhao et al. (2024) — ExpeL (AAAI 2024).** [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/29936) · [arXiv:2308.10144](https://arxiv.org/abs/2308.10144). Insights con ADD/UPVOTE/DOWNVOTE/EDIT juzgados **por el propio LLM, sin validación externa** — el antipatrón exacto que V2 evita; útil como contraste directo. Veredicto: Parcial (débil). Cercanía: Media.

**M5. Huang et al. (2025) — POPPER (ICML 2025, PMLR 267).** [PMLR](https://proceedings.mlr.press/v267/huang25n.html) · [arXiv:2502.09858](https://arxiv.org/pdf/2502.09858). Validación de hipótesis por **falsaciones secuenciales con control estadístico del error Tipo I (e-values)**; rendimiento comparable a científicos humanos con ~10× menos tiempo. **Sin memoria**: es el módulo VALIDACIÓN de nuestro ciclo con rigor formal, no el ciclo completo. Vía de refuerzo (no refutación) para V2. Cercanía: Media-Alta.

**M6. Yan et al. (2026) — Memory-R1 (ACL 2026).** [ACL](https://aclanthology.org/2026.acl-long.583/) · [arXiv:2508.19828](https://arxiv.org/abs/2508.19828). Política RL (ADD/UPDATE/DELETE/NOOP) sobre memoria, recompensada por utilidad aguas abajo — **utilidad ≠ veracidad; sin verificación pre-almacenamiento**. Veredicto: No. Cercanía: Media.

**M7. Chen et al. (2024) — AgentPoison (NeurIPS 2024).** [NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2024/file/eb113910e9c3f6242541c1652e30dfd6-Paper-Conference.pdf). Envenenamiento de memoria/RAG de agentes: ≥80 % de éxito con <0,1 % de memoria comprometida (incluye agente de conducción). **Justificación adversarial de los gates de admisión de V2.** Cercanía: Media (motivación).

**M8. Dong et al. (2025/26) [preprint] — MINJA: Memory Injection Attacks via Query-Only Interaction.** [arXiv:2503.03704](https://arxiv.org/abs/2503.03704). Demuestra que **auto-almacenar salidas no verificadas del LLM es el vector de propagación de errores**, sin necesidad de acceso a la memoria. La defensa publicada (Devarangadi Sunil et al. 2026, [arXiv:2601.05504](https://arxiv.org/abs/2601.05504) [preprint]) filtra en *recuperación* con trust-scoring — **no valida antes de consolidar → hueco que V2 ocupa**. Cercanía: **Alta** (motivación directa).

**M9. Xiong et al. (2025) [preprint] — How Memory Management Impacts LLM Agents.** [arXiv:2505.16067](https://arxiv.org/abs/2505.16067). Evidencia empírica de **experience-following**: propagación de errores y replay de experiencias desalineadas; propone purga *a posteriori* por calidad. V2 se diferencia por validar **antes** de consolidar. Veredicto: Parcial. Cercanía: **Alta** (problema idéntico).

**M10. Lin & Miao (2025) — reanálisis desde la óptica de memoria.** El KG se cura con **validación humana experta offline y estática**; no hay ciclo de vida de evidencia en operación ni actualización continua. Confirma que en dominio vehicular nadie ha publicado el ciclo evolutivo. Veredicto: Parcial (débil).

**Fundamentos y complementarias verificadas (sin ficha completa):** Aamodt & Plaza (1994), *AI Communications* 7(1) — ciclo CBR 4R, el RETAIN clásico ya condiciona la retención a la revisión: **citar como genealogía y reconocerlo**; Alchourrón, Gärdenfors & Makinson (1985) — postulados AGM, fundamento de CONFIRMADA/DESCARTADA; Wilie et al. (2024), *Belief-R* (EMNLP 2024, [ACL](https://aclanthology.org/2024.emnlp-main.586/)) — los LLM revisan mal sus creencias ante evidencia nueva → **argumento para externalizar la revisión en la arquitectura de memoria** en lugar de confiar en el modelo; Xu et al. (2024), *SaySelf* (EMNLP 2024, [ACL](https://aclanthology.org/2024.emnlp-main.343/)) — calibración de confianza con racionales auto-reflexivos, candidato para puntuar el paso ANOMALÍA→HIPÓTESIS.

### 3.2 Veredicto sobre V2 (honesto)

1. La idea genérica "no consolidar sin validar" **ya no es novedosa**: Voyager (gate de ejecución), DS-Agent (RETAIN de CBR) y sobre todo **HDSO (ciclo casi isomorfo con ledger de descartes)**. La afirmación "primer ciclo de estados de evidencia con validación previa" es **indefendible**.
2. Lo que sigue libre: (i) el ciclo aplicado a **conocimiento diagnóstico declarativo** (síntoma→causa), no a habilidades procedimentales; (ii) la **granularidad de 7 estados** con fases pre-hipótesis (ANOMALÍA→PATRÓN CANDIDATO), ausentes en HDSO; (iii) **validación anclada en el mundo físico** (verificación determinista contra features de telemetría, resultado de reparación, humano en el bucle) frente a validación en benchmark; (iv) el **dominio vehicular**, donde lo único publicado es curación humana estática.
3. **Reformulación defendible de V2:** *"Arquitectura de memoria de agente para diagnóstico vehicular que instancia un ciclo de vida de evidencia de grano fino (7 estados), donde la consolidación de conocimiento declarativo exige validación externa anclada en telemetría verificable, unificando el RETAIN de CBR (Aamodt & Plaza, 1994), la revisión de creencias (AGM) y la defensa contra propagación de errores y envenenamiento de memoria demostrada empíricamente (AgentPoison, MINJA, Xiong et al.)"*. HDSO y DS-Agent se citan como trabajos hermanos, diferenciándose por dominio, granularidad y naturaleza de la validación — **no** por la idea del gate en sí.
4. Riesgo residual: HDSO es un preprint industrial de 2026 — **vigilar versiones y derivados antes del depósito** de la memoria.

---

## 4. Separación conceptual: memoria evolutiva ≠ Continual Learning (P6–P9)

La arquitectura separa (a) la **memoria evolutiva**, que almacena experiencias y evidencia con estados, de (b) el **continual learning del detector**, que adapta el modelo ante drift. La literatura aporta cuatro mecanismos convergentes para que una anomalía o hipótesis incorrecta **no** reentrene automáticamente el detector:

**P6. Arazo et al. (2020) — Pseudo-Labeling and Confirmation Bias (IJCNN 2020).** [arXiv:1908.02983](https://arxiv.org/abs/1908.02983). Evidencia canónica del bucle de confirmación: el self-training naíf sobreajusta a sus propias predicciones erróneas y **acumula error**. Justifica que el reentrenamiento se dispare por evidencia *independiente del detector*, nunca por sus predicciones. Cercanía: Media (riesgo transferible).

**P7. Bhatia et al. (2022) — MemStream (WWW 2022).** [ACM](https://dl.acm.org/doi/abs/10.1145/3485447.3512221) · [arXiv:2106.03837](https://arxiv.org/abs/2106.03837). Detección streaming con drift y **memoria explícita de normalidad protegida: una muestra solo entra si su score de anomalía es bajo** (gate de admisión), con robustez probada frente a memory poisoning y tamaño óptimo de memoria demostrado teóricamente. **El mecanismo de referencia para nuestro requisito.** No supervisado, temporal, ligero. Cercanía: **Alta**.

**P8. Deng et al. (2025/26) — HILAD (ACM TiiS).** [ACM](https://dl.acm.org/doi/10.1145/3778167) · [arXiv:2405.03234](https://arxiv.org/html/2405.03234v1). Marco human-in-the-loop donde el experto revisa comportamientos agregados del detector y **solo la corrección validada actualiza el modelo**. Materializa la compuerta humana para cambios mayores. Cercanía: Media.

**P9. Özer, Ebeling & Enzweiler (2025) [preprint, Mercedes-Benz] — STREAM-VAE.** [arXiv:2511.15339](https://arxiv.org/abs/2511.15339). VAE de doble vía que **separa arquitectónicamente drift lento (EMA+atención) de picos transitorios** en telemetría vehicular real (8 señales, 6 tipos de fallo sintético); PA-F1 0,857; **2,45 ms/ventana** (viable embarcado). Limitación declarada por los autores: "la calibración por entidad puede desplazarse entre vehículos" → doble valor para nosotros (patrón drift-vs-anomalía + evidencia de no transferibilidad entre unidades). Cercanía: **Alta**.

**Diseño defendible resultante:** la memoria evolutiva escribe siempre (con etiqueta de confianza y estado de evidencia); el detector **solo** se reentrena si (i) el drift persiste más allá de una ventana de confirmación (distinción drift/transitorio tipo STREAM-VAE), (ii) las muestras candidatas pasan un gate de score tipo MemStream, y (iii) hay confirmación humana para cambios mayores (HILAD); nunca por pseudo-etiquetas del propio sistema (Arazo). Chesterman et al. (P5, §5) añade el mecanismo de *cuarentena* de datos pre-fallo antes de reentrenar.

---

## 5. Personalización por vehículo (P1–P5) y evidencia global-vs-individual

**P1. Hendrickx et al. (2020) [fundacional] — A general anomaly detection framework for fleet-based condition monitoring.** MSSP 139. [DOI 10.1016/j.ymssp.2019.106585](https://www.sciencedirect.com/science/article/abs/pii/S0888327019308064) · [arXiv:1912.12941](https://arxiv.org/abs/1912.12941). Sin histórico propio, la normalidad se define por **consenso de flota** — resuelve el cold start; falla con flotas heterogéneas. Cercanía: **Alta**.

**P2. Michau & Fink (2021) — Unsupervised transfer learning for anomaly detection.** Knowledge-Based Systems 216. [DOI 10.1016/j.knosys.2021.106816](https://www.sciencedirect.com/science/article/pii/S0950705121000794). Transferencia adversarial no supervisada de condiciones operativas *complementarias* desde otras unidades hacia el detector one-class de la unidad objetivo — formaliza el punto medio flota↔individuo (riesgo: transferencia negativa entre unidades disímiles). Cercanía: **Alta**.

**P3. Liu et al. (2021) — Communication-Efficient On-Device Federated Learning (IEEE IoT Journal 8(8)).** [IEEE](https://ieeexplore.ieee.org/document/9146846/). FL en dispositivo con AMCNN-LSTM y compresión Top-k (−50 % comunicación): plantilla per-device en edge. Cercanía: Media.

**P4. Almansour et al. (2025) — Adaptive personalized federated learning… (Scientific Reports 15).** [Nature](https://www.nature.com/articles/s41598-025-17699-3). **La comparación cuantitativa más directa:** fusión personalizada por vehículo (APFed) gana **≈ +3–5 puntos en accuracy/precisión/recall/F1 sobre FedAvg/FedProx** (agregación global uniforme) bajo datos no-IID, con red ligera apta para hardware vehicular. Dominio IDS (supervisado) — transferible como evidencia de personalización, no de diagnóstico mecánico. Cercanía: Media.

**P5. Chesterman et al. (2023) — Normal behavior modeling para turbinas (Wind Energy Science 8(6)).** [Copernicus](https://wes.copernicus.org/articles/8/893/2023/). **Flota real** (5 parques, fallos reales): sustracción de la **mediana de flota** → detección sobre el **residuo idiosincrático por turbina**; elimina efectos macro (estación, meteorología) manteniendo sensibilidad a degradación individual; depura datos contaminados pre-fallo antes de entrenar. Cercanía: Media (patrón directamente transferible).

**Síntesis defendible (RQ13 + variabilidad EngineAD):** (1) bajo no-IID, la personalización supera a la agregación global uniforme (P4, cuantificado; P9/Mercedes: los umbrales por entidad no transfieren); (2) el modelo de flota gana en cold start y escasez de datos por unidad (P1, P2); (3) la síntesis madura es **jerárquica**: prior/normalizador de flota + perfil basal individual que se especializa (P5). Ningún trabajo identificado hace esta comparación sobre OBD-II en edge → experimento diferenciador barato para el TFM: global vs individual vs jerárquico sobre nuestro banco. La variabilidad inter-vehículo de EngineAD (F1 0,21–0,93) es la motivación empírica citable.

---

## 6. RQ5 profundizada: puente decisión↔causa (X1–X8)

**X1. Zhao et al. (2026) — PI-Dual-STGCN + SHAP-LLM (Sensors 26(2):723).** [MDPI](https://www.mdpi.com/1424-8220/26/2/723). **El puente (a)→(b) más explícito del corpus:** STGCN physics-informed (grafo de topología física + grafo de similitud de señal) → SHAP → entradas semánticas estructuradas → **LLM restringido por RAG** que redacta la hipótesis mecánica; el grafo físico ancla features a componentes. 99,22 % acc. (engranajes, dataset SEU). Limitación: la capa (b) es *generada*, no *verificada* (métricas propias, sin expertos ni ground truth de mecanismo); supervisado. Nivel: Dataset público (banco) · Desconocido: No aplica · Cercanía: **Alta**.

**X2. Khan et al. (2024) [preprint] — FaultExplainer.** [arXiv:2412.14492](https://arxiv.org/abs/2412.14492). **El análogo más cercano a nuestro pipeline:** PCA-T² no supervisado (solo datos normales) → variables de mayor contribución → GPT-4o genera hipótesis de causa raíz, **incluso para fallos no vistos sin causa histórica** (Tennessee Eastman, simulación). Alucinaciones ocasionales; sin RAG de verificación — exactamente lo que añadimos. Nivel: Simulación · Desconocido: Anomalía no vista/open-set · Cercanía: **Alta**.

**X3. Zytek et al. (2024) — Explingo (IEEE Big Data 2024).** [IEEE](https://ieeexplore.ieee.org/document/10825114/) · [arXiv:2412.05145](https://arxiv.org/abs/2412.05145). SHAP→narrativa fiel con módulos Narrator+**Grader** (métricas: exactitud, completitud, fluidez, concisión). Deliberadamente solo capa (a). **Aporta el marco de evaluación de calidad de explicaciones adaptable a nuestro agente.** Cercanía: Media.

**X4. Mohammadi, Krysander & Jung (2025) — Consistency-based diagnosis using data-driven residuals (Control Engineering Practice 159).** [DOI 10.1016/j.conengprac.2025.106283](https://doi.org/10.1016/j.conengprac.2025.106283). La capa (b) **estructural por construcción**: residuos grey-box entrenados solo con datos sanos, con sensibilidad conocida a fallos de componentes (firma de fallo) + aislamiento por consistencia + cuantificación de incertidumbre; caso real en postratamiento de camión pesado. **El patrón de "hipótesis validada por consistencia física" que nuestro nodo verify aproxima sin modelo estructural.** Nivel: Vehículo real · Desconocido: Fallo open-set · Cercanía: **Alta**.

**X5. Srinivasan et al. (2024) — Counterfactual Explanation for AE-based TSAD (PHME 2024).** [DOI 10.36001/phme.2024.v8i1.4087](https://papers.phmsociety.org/index.php/phme/article/view/4087). Contrafactuales parsimoniosos sobre autoencoder (SKAB + dataset industrial): "qué señales y en qué dirección deberían cambiar" — input excelente para la hipótesis mecánica del LLM; no mapea a componente físico. Cercanía: **Alta** (combinable).

**X6. Wang et al. (2023) — CORAL: Incremental Causal Graph Learning for Online RCA (KDD 2023).** [ACM](https://dl.acm.org/doi/10.1145/3580305.3599392). Grafo causal incremental sobre series + random walk para causa raíz, auto-disparado ante fallos nuevos; despliegue operacional en TI. Plantilla para un módulo de verificación causal complementario al RAG. Cercanía: Media.

**X7. Wang et al. (2024) — RCAgent (CIKM 2024).** [ACM](https://dl.acm.org/doi/10.1145/3627673.3680016) · [arXiv:2310.16340](https://arxiv.org/abs/2310.16340). Agente ReAct con herramientas + **self-consistency sobre trayectorias** para RCA en Alibaba Cloud (incidentes reales; evaluación por expertos). **Arquitectura de referencia del puente agéntico**: causa + evidencia trazable + solución. Nivel: Despliegue operacional · Cercanía: **Alta**.

**X8. Cortes dos Santos et al. (2025) [preprint] — SHAP + Causal Analysis.** [arXiv:2510.23817](https://arxiv.org/abs/2510.23817). Doble filtro: variables a la vez predictivamente importantes (SHAP) y causalmente influyentes (5 algoritmos de descubrimiento causal) sobre TEP. Valida la idea del doble filtro previo al LLM; ignora dinámica temporal. Cercanía: Media.

**Síntesis RQ5:** el puente existe **por fragmentos, no como cadena cerrada**. Cuatro patrones: atribución→narrativa fiel (X3), atribución→hipótesis LLM (X1, X2 — generada, no verificada), física por construcción (X4 — verificada pero muda, exige modelo del sistema), y causal/agéntico (X6, X7 — con ground truth en TI, no en automoción). **El eslabón vacante es la evaluación de la hipótesis causal:** nadie dispone simultáneamente de (i) detección no supervisada, (ii) atribución, (iii) hipótesis mecánica en lenguaje natural y (iv) verificación contra ground truth físico o juicio experto estructurado — en automoción, con fallos de firma conocida inyectados, sigue vacante. Es exactamente el diseño de nuestro grafo (detector → evidencias → hypothesize → **verify determinista contra features** → report), que puede presentarse como aproximación sin-modelo al patrón de X4.

---

## 7. Búsqueda adversarial: competidores directos (D1–D8) y veredicto sobre el vacío

**D1. Das, Griffith & Rathore (2025) — LLM-Based Fault Detection in Connected Vehicle Time-Series Data (ACM SaT-CPS '25).** [ACM](https://dl.acm.org/doi/10.1145/3716816.3727968) · [NSF PAR](https://par.nsf.gov/servlets/purl/10599400). **El competidor más cercano en "LLM + telemetría vehicular temporal":** mensajes BSM (SAE J2735, piloto de Tampa) + Llama-3.1-8B/Mistral/Gemma (zero-shot, LoRA, embeddings de series inyectados a LLM congelado) para 4 fallos sintéticos de sensor. Resultado clave: **el ML clásico (stacking XGBoost+RF, F1>0,94) supera al LLM (0,09–0,77)** incluso con embeddings. Sin OBD-II, sin streaming continuo, sin RAG/agentes/memoria/edge. **Amenaza: Media-Alta — pero su conclusión (LLM pierde como detector) refuerza nuestra separación detección-ML/razonamiento-LLM (ADR-0009) más que invalidarla.** Nivel: Dataset público (fallos inyectados) · Desconocido: Anomalía no vista (sintética) · Cercanía: **Alta**.

**D2. Quintano, Qiang & Fu (2025) — PA-JJAMA: LLM-based IDS for CAN (IEEE MASS 2025).** [DOI 10.1109/MASS66014.2025.00111](https://par.nsf.gov/biblio/10651645-pa-jjama-llm-based-intrusion-detection-system-can-bus-networks). LLM fine-tuned + explicaciones sobre Car-Hacking (seguridad, supervisado). Erosiona la novedad de "LLM sobre bus vehicular" en general; no toca salud mecánica, no supervisado, RAG, memoria ni edge. Amenaza: Media.

**D3. Huo et al. (2025) — Personalized LLM Service Updating in Collaborative Edge-Enabled Vehicle Autonomous System (IEEE TCE 72(1)).** [DOI 10.1109/TCE.2025.3644688](https://api.openalex.org/works/doi:10.1109%2FTCE.2025.3644688). **Vehículo-edge-cloud con LLM personalizado por vehículo** (PEFT en edge, agregación en nube) para servicios de conducción — el esqueleto arquitectónico del TFM con propósito distinto. Obliga a acotar el vacío al *diagnóstico*. Amenaza: Media.

**D4. Jia, Liang & Yu (2025) [preprint] — Syn-Diag: LLM edge-cloud few-shot fault diagnosis.** [arXiv:2510.05733](https://arxiv.org/abs/2510.05733). LLM nube + destilación a modelo edge 1B con actualización online (rodamientos; 1-shot 98 %; −83 % tamaño, −50 % latencia). "LLM diagnóstico edge-cloud con evolución continua" ya existe en 2025 — en bancos de vibración, no en telemetría vehicular streaming. Amenaza: Media.

**D5. Özer, Ebeling & Enzweiler (2026) [preprint, Mercedes-Benz] — ECoLAD: Deployment-Oriented Evaluation for Automotive TSAD.** [arXiv:2603.10926](https://arxiv.org/abs/2603.10926). Protocolo de evaluación embarcada (telemetría real, límites de CPU): los métodos deep "pierden viabilidad antes que exactitud"; los clásicos ligeros dominan bajo restricciones. Reduce la novedad de "no supervisado + telemetría + edge + evaluación" como conjunto; no toca LLM/RAG/agentes/memoria. **Citar además como respaldo independiente (OEM) de nuestra elección de detectores clásicos ligeros en edge.** Amenaza: Media.

**D6. Loukas et al. (2025) [preprint] — Evaluation of LLMs for Anomaly Detection in AVs.** [arXiv:2509.05315](https://arxiv.org/html/2509.05315). Visión + CoT; dominio perceptual, 12 casos, cualitativo. Amenaza: Baja.

**D7. Sorokin, Vasilev & Pasini (2026) [preprint] — DeepTest 2026: Benchmarking an LLM-Based Automotive Assistant.** [arXiv:2604.12615](https://arxiv.org/html/2604.12615v1). El **RAG documental automotriz ya está en producción industrial (BMW)** con metodología de testing propia. Debilita la novedad aislada del componente RAG; aporta estándar de evaluación citable. Amenaza: Baja-Media.

**D8. [Literatura gris] Automotive-Fault-Diagnosis-Agent (GitHub, 2025-26).** [GitHub](https://github.com/rithi107/Automotive-Fault-Diagnosis-Agent). LangGraph multi-agente + RAG híbrido (denso+BM25+RRF) sobre 5.564 registros OBD-II (DTC + freeze-frame) + Llama-3.3-70B. Sin streaming, sin no-supervisado, sin memoria, sin edge, **sin evaluación formal**. Citable solo como indicador de tendencia. Amenaza: Media (conceptual).

**Contexto que apoya el vacío:** la revisión de Michailidis et al. (Sensors 25(13):4057, jun-2025) sobre ML+OBD-II **no recoge ningún trabajo LLM+OBD-II**; Di Maggio (2025) declara la literatura de agentes LLM para PdM "fragmentada y sin benchmarks". Productos comerciales sin evaluación académica (OBDAI, MECH AI): citables solo como motivación de mercado.

### 7.1 Veredicto agregado y reformulación del vacío

**El vacío sobrevive, reformulado.** Ya existen (2025-26) trabajos que cubren pares o tríos de componentes; **ninguna afirmación de novedad por componente aislado es defendible**. Formulación exacta propuesta para la memoria:

> "En la literatura analizada (hasta agosto de 2026) no se identificó ninguna propuesta que integre *en un único sistema evaluado end-to-end*: (i) ingesta de telemetría OBD-II en streaming, (ii) detección no supervisada de anomalías ejecutada en el dispositivo edge, (iii) razonamiento agéntico con modelos de lenguaje bajo las restricciones del edge, (iv) recuperación aumentada sobre documentación técnica del vehículo y (v) una memoria longitudinal por vehículo con ciclo explícito de validación de hipótesis diagnósticas. Los trabajos existentes cubren a lo sumo dos o tres de estos componentes de forma aislada [D1–D8, A-LLM1/2, N20–N25], y la memoria por vehículo con cierre de bucle hipótesis-verificación no aparece en ningún trabajo identificado del dominio."

El diferenciador más robusto tras el análisis adversarial sigue siendo **V2 reformulada (§3.2)** + la **evaluación end-to-end con banco de fallos reproducible y protocolo held-out** (V5), con V3 (personalización jerárquica flota→vehículo en OBD-II edge) como segundo experimento diferenciador.

---

## 8. Candidatos E7 de la Entrega 1: recuperados (R1–R4)

**R1. Rimpas, Papadakis & Samarakou (2020) — verificado completo** (Crossref + DOAJ, open access): *OBD-II sensor diagnostics for monitoring vehicle operation and consumption.* **Energy Reports 6:55–63.** DOI [10.1016/j.egyr.2019.10.018](https://doi.org/10.1016/j.egyr.2019.10.018). Parámetros OBD-II (temperatura, MAF, RPM) en viaje real de 5 km comparados con estándares del fabricante. Sin ML. **Entra al corpus (L1, cercanía Baja)** como referencia de adquisición/consumo.

**R2. Takara, Cocco Mariani & Coelho (2025) — verificado parcial** (existencia y título en ScienceDirect; autores vía ResearchGate, indicado como último recurso): *Novel engine fault diagnosis framework based on ML and MiniRocket… (ESWA, jun-2025)*. DOI exacto y métricas: no constan (paywall). **Pendiente de lectura con acceso institucional.**

**R3. Min et al. (2024) — verificado en metadatos** (Crossref): *Toward interpretable anomaly detection for autonomous vehicles with denoising variational transformer.* **Engineering Applications of AI 129:107601 (publicación 2024; DOI registrado en 2023 — citar como 2024).** Contenido: no consta (paywall). **Pendiente de lectura con acceso institucional.**

**R4. Onsu, Simsek, Fobert & Kantarci (2025) — verificado en metadatos** (Crossref): *Intelligent multi-sensor fusion and anomaly detection in vehicles via deep learning.* **Internet of Things 31:101561 (2025).** DOI [10.1016/j.iot.2025.101561](https://doi.org/10.1016/j.iot.2025.101561). Contenido: no consta. **Pendiente de lectura con acceso institucional.**

---

## 9. Sintaxis lista para ejecutar en bases de datos con acceso institucional

Estas consultas reproducen las cadenas del protocolo (§2 de la E1) en la sintaxis nativa de cada base. Al ejecutarlas, registrar por consulta y por base: fecha, nº de resultados, filtros aplicados (años 2021–2026, tipo de documento) y exportación (RIS/CSV) — con eso se construye el diagrama PRISMA formal en la Entrega 3/4.

**Scopus (Advanced search):**

- Q1 (OBD-II+IA): `TITLE-ABS-KEY(("OBD-II" OR "OBD2" OR "on-board diagnostics") AND ("machine learning" OR "deep learning" OR "anomaly detection" OR "fault diagnosis")) AND PUBYEAR > 2020`
- Q2 (no supervisado vehicular): `TITLE-ABS-KEY(("vehicle" OR "automotive" OR "CAN bus") AND ("unsupervised" OR "one-class" OR "autoencoder" OR "isolation forest") AND ("anomaly detection" OR "fault detection")) AND PUBYEAR > 2020`
- Q3 (LLM+diagnóstico): `TITLE-ABS-KEY(("large language model" OR "LLM") AND ("fault diagnosis" OR "predictive maintenance" OR "diagnostic trouble code" OR "vehicle diagnostics")) AND PUBYEAR > 2021`
- Q4 (RAG+mantenimiento): `TITLE-ABS-KEY(("retrieval-augmented generation" OR "RAG") AND ("maintenance" OR "technical manual" OR "fault" OR "repair")) AND PUBYEAR > 2021`
- Q5 (agentes+PHM): `TITLE-ABS-KEY(("LLM agent" OR "multi-agent" OR "agentic") AND ("fault diagnosis" OR "prognostics" OR "predictive maintenance")) AND PUBYEAR > 2021`
- Q6 (memoria de agentes): `TITLE-ABS-KEY(("agent memory" OR "episodic memory" OR "memory consolidation" OR "experience replay") AND ("large language model" OR "LLM agent")) AND PUBYEAR > 2021`
- Q7 (CL/drift vehicular): `TITLE-ABS-KEY(("continual learning" OR "concept drift" OR "incremental learning" OR "domain adaptation") AND ("vehicle" OR "predictive maintenance" OR "condition monitoring")) AND PUBYEAR > 2020`
- Q8 (edge vehicular): `TITLE-ABS-KEY(("edge computing" OR "TinyML" OR "Raspberry Pi" OR "embedded") AND ("vehicle" OR "automotive") AND ("anomaly detection" OR "fault diagnosis" OR "predictive maintenance")) AND PUBYEAR > 2020`

**Web of Science (Advanced, campo TS=):** mismas cadenas sustituyendo `TITLE-ABS-KEY(...)` por `TS=(...)` y el filtro de año por `AND PY=(2021-2026)`.

**IEEE Xplore (Command search):** mismas cadenas con `("Abstract":... OR "Document Title":...)` y filtro de años en la interfaz; ejemplo Q1: `("Abstract":"OBD-II" OR "Abstract":"on-board diagnostics") AND ("Abstract":"machine learning" OR "Abstract":"anomaly detection")`.

**Plantilla de registro por base (para el PRISMA formal):** Base | Consulta | Fecha | Resultados brutos | Tras filtro años/tipo | Exportados | Duplicados vs corpus | Nuevos evaluados | Incluidos.

---

## 10. Recuentos del barrido de esta iteración (preliminares, por web)

Cinco bloques de búsqueda (memoria/V2, personalización+CL, XAI puente, adversarial/competidores, auditoría EngineAD): **≈ 480 registros visualizados** en ~60 consultas → ≈ 115 candidatos únicos tras deduplicación → ≈ 60 evaluados en fuente primaria → **39 incluidos** (M: 10 + 4 complementarias; P: 9; X: 8; D: 8, de los cuales 1 literatura gris no citable como evidencia; R: 4 recuperados, 3 pendientes de texto completo). Preprints marcados: 11. Verificación por segunda vez de los registros de mayor riesgo (HDSO, STREAM-VAE, ECoLAD, Memory-R1, Das et al.): confirmados en fuente el 12-08-2026. Estos recuentos siguen siendo del barrido web, no del PRISMA formal (§9).

---

## 11. Matriz comparativa completa (v2)

Valores: Sí / Parcial / No / — (no aplica al tipo de trabajo). **NV** = Nivel de validación (Sim = Simulación; DP = Dataset público; BH = Banco-HIL; VR = Vehículo real; FR = Flota real; DO = Despliegue operacional; "prop." = datos reales propietarios). **TD** = Tipo de desconocido (OE = Outlier estadístico; ANV = Anomalía no vista; FOS = Fallo open-set; FMN = Fallo mecánico nuevo; NA = No aplica). Surveys y frameworks se listan al final sin fila de matriz.

| Referencia | Año | Datos | Técnica | NoSup | Temp | XAI | LLM | RAG | Agentes | Memoria | Edge | Detecta desconocidos | **NV** | **TD** | Cercanía |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Mahale et al. (A-LLM1) | 2025 | OBD-II+DTC+manuales | XGB+CTGAN+RAG+GPT-4o | Parcial | No | Parcial | Sí | Sí | No | No | No | No | DP | NA | Alta |
| Lin & Miao (A-LLM2) | 2025 | Diálogos taller+KG | KG+RAG 3 niveles+LLM | No | No | Sí (causa) | Sí | Parcial | Parcial | Parcial | No | Parcial | prop. (offline) | FOS (parcial) | Alta |
| Giannoulidis et al. (N-EDBT) | 2024 | OBD-II flota | Closest-Pair/LOF/TranAD | Sí | Sí | No | No | No | No | Parcial | No | Sí | FR | ANV | Alta |
| Cherdo et al. (N5) | 2023 | CAN real | LSTM/GRU/CNN+likelihood | Sí | Sí | No | No | No | No | No | Sí | Parcial | VR | ANV | Alta |
| PARAM (N24) [pre] | 2025 | Vibración+manuales | Agentes+RAG+LLM | Parcial | Sí | Parcial | Sí | Sí | Sí | Parcial | No | Parcial | DP (banco) | ANV (parcial) | Alta |
| Park et al. (N23) | 2025 | Códigos error+manuales | Multiagente LLM local | No | No | Parcial | Sí | Sí | Sí | No | Parcial | No | BH | NA | Alta |
| Lee et al. (N22) | 2025 | Sensores simulados | Agentes LLM+herramientas | Parcial | Sí | Sí | Sí | n.c. | Sí | Parcial | No | Parcial | Sim | ANV (parcial) | Alta |
| Nam et al. (N20) | 2025 | Manual taller | RAG multimodal+LoRA 8B | No | No | Parcial | Sí | Sí | No | Parcial | No | No | prop. (QA) | NA | Alta |
| CarExpert (N21) | 2023 | Doc. vehículo BMW | RAG+guardrails | No | No | Parcial | Sí | Sí | Parcial | No | Parcial | No | DO (industrial) | NA | Alta |
| Khemani & Qureshi (N14) | 2026 | OBD-II+IMU+ambiente | LightGBM+SHAP | No | Sí | Sí (decisión) | No | No | No | No | Sí | No | VR+Sim | NA | Alta |
| Giannoulidis & Gounaris (N15) | 2023 | Flota+C-MAPSS | Streaming context-aware | Sí | Sí | No | No | No | No | Parcial | No | Sí | FR+DP | ANV | Alta |
| Abboush et al. (N6) | 2026 | Test real+HiL | DAE+umbral adaptativo | Sí | Sí | Sí | No | No | No | No | No | Parcial | VR+BH | ANV | Alta |
| EngineAD (N8/R0) [pre] | 2026 | CAN flota (8 comp. PCA) | 9 métodos one-class | Sí | Sí | No | No | No | No | No | No | Parcial | DP (orig. FR) | ANV | Alta |
| Lundgren & Jung (C19) | 2022 | Motor real Volvo | Open-set one-class | Sí | Sí | No | No | No | No | No | No | Sí | BH/VR | FOS | Alta |
| Idiri et al. (A6) | 2025 | OBD-II+sim (RPi) | LSTM/GRU | No | Sí | No | No | No | No | No | Sí | No | Sim+VR | NA | Media |
| Lu et al. (A7) | 2025 | CAN+DTC 20 veh. | CNN-LSTM-Transf.+XAI | No | Sí | Sí | No | No | No | No | Parcial | Parcial | VR+Sim | ANV (parcial) | Media |
| Geglio et al. (N7) | 2022 | Telemetría Ford | Conv-AE | Sí | Sí | No | No | No | No | No | No | Parcial | FR | ANV | Media |
| SCANIA X (N11) | 2025 | Telemetría flota | Dataset multi-técnica | Ambos | Sí | No | No | No | No | No | No | Parcial | DP (orig. FR) | ANV (parcial) | Media |
| FD-LLM (N18) [pre] | 2024 | Vibración CWRU | LLM+LoRA clasif. | No | Sí | Parcial | Sí | No | No | No | No | No | DP (banco) | NA | Media |
| LLMAD (N19) | 2025 | Series públicas | LLM ICL+AnoCoT | Parcial | Sí | Sí | Sí | Parcial | No | Parcial | No | Parcial | DP | ANV (parcial) | Media-Alta |
| **HDSO (M1) [pre]** | 2026 | Trazas ALFWorld | Hipótesis falsables+A/B | — | — | No | Sí | No | Sí | **Sí (validada)** | No | Parcial | Sim | NA | **Alta (concept.)** |
| DS-Agent (M2) | 2024 | Casos Kaggle | CBR 4R+ejecución | No | No | No | Sí | Sí | Sí | Sí (Retain validado) | No | No | DP | NA | Alta (metodol.) |
| Voyager (M3) [pre] | 2023 | Entorno Minecraft | Skills+self-verification | — | — | No | Sí | Sí | Sí | Sí (verif. ejecución) | No | No | Sim | NA | Media |
| ExpeL (M4) | 2024 | Trayectorias benchmark | Insights auto-juzgados | — | — | No | Sí | Sí | Sí | Sí (sin validar) | No | No | DP/Sim | NA | Media |
| POPPER (M5) | 2025 | Datasets científicos | Falsación secuencial | — | — | No | Sí | Sí | Sí | No | No | Sí (evidencia insuf.) | DP | NA | Media-Alta |
| Memory-R1 (M6) | 2026 | QA conversacional | RL sobre ops. memoria | — | — | No | Sí | Sí | Sí | Sí (por utilidad) | No | No | DP | NA | Media |
| AgentPoison (M7) | 2024 | Agentes AD/EHR | Backdoor retrieval | — | — | No | Sí | Sí | Sí | Sí (atacada) | No | No | Sim/DP | NA | Media (motiv.) |
| MINJA (M8) [pre] | 2025 | Interacciones agente | Inyección vía queries | — | — | No | Sí | Sí | Sí | Sí (atacada) | No | No | Sim/DP | NA | Alta (motiv.) |
| Xiong et al. (M9) [pre] | 2025 | Trayectorias benchmark | Purga por calidad | — | — | No | Sí | Sí | Sí | Sí (post-hoc) | No | No | DP/Sim | NA | Alta (problema) |
| Hendrickx et al. (P1) | 2020 | Flota máquinas eléctr. | Consenso de flota | Sí | Parcial | Parcial | No | No | No | No | No | Sí | BH | ANV | Alta |
| Michau & Fink (P2) | 2021 | CWRU+turbofán sim. | Transfer adversarial+one-class | Sí | Parcial | No | No | No | No | No | No | Sí | DP+Sim | FOS | Alta |
| Liu et al. (P3) | 2021 | Series IIoT | FL+AMCNN-LSTM | Sí | Sí | Parcial | No | No | No | No | Sí | Sí | DP | ANV | Media |
| Almansour et al. (P4) | 2025 | CAN/red pública | FL personalizado+CNN ligera | No | Parcial | No | No | No | No | No | Sí | No | DP | NA | Media |
| Chesterman et al. (P5) | 2023 | SCADA 5 parques | Mediana flota+residuo indiv. | Sí | Sí | Parcial | No | No | No | No | No | Sí | **FR** | FMN (fallos reales) | Media |
| Arazo et al. (P6) | 2020 | Imagen benchmark | Pseudo-label+mixup | No | No | No | No | No | No | No | No | No | DP | NA | Media (riesgo) |
| MemStream (P7) | 2022 | Streams multivar. | AE+memoria con gate | Sí | Sí | No | No | No | Sí (filtrada) | Parcial | Sí | DP | ANV | Alta |
| HILAD (P8) | 2025/26 | Series públicas | HITL+corrección validada | Parcial | Sí | Sí | No | No | No | Parcial | No | Sí | DP+usuarios | ANV | Media |
| STREAM-VAE (P9) [pre] | 2025 | Telemetría vehicular prop. | VAE dual-path drift/spike | Sí | Sí | Parcial | No | No | No | No | Sí | Sí | VR (prop.)+DP | OE/ANV (sintética) | Alta |
| PI-Dual-STGCN (X1) | 2026 | Vibración SEU | STGCN físico+SHAP+LLM-RAG | No | Sí | **Ambas** | Sí | Sí | No | No | No | No | DP (banco) | NA | Alta |
| FaultExplainer (X2) [pre] | 2024 | TEP simulado | PCA-T²+LLM | Sí | Sí | **Ambas** | Sí | Parcial | No | No | No | Sí | Sim | ANV/FOS | Alta |
| Explingo (X3) | 2024 | Tabulares varios | SHAP→LLM+Grader | No | No | (a) | Sí | No | No | No | No | No | DP | NA | Media |
| Mohammadi et al. (X4) | 2025 | ECU camión real | Residuos grey-box+consistencia | Sí | Sí | (b) estructural | No | No | No | No | n.c. | Parcial | **VR** | FOS | Alta |
| Srinivasan et al. (X5) | 2024 | SKAB+industrial | AE+contrafactual | Sí | Sí | (a) contrafactual | No | No | No | No | No | Sí | DP+prop. | ANV | Alta |
| CORAL (X6) | 2023 | Métricas TI reales | Grafo causal incremental | Sí | Sí | (b) entidad | No | No | No | Parcial | No | Sí | **DO** | FOS | Media |
| RCAgent (X7) | 2024 | Incidentes Alibaba | Agente+herramientas+self-consistency | Parcial | Sí | (b) evidencia | Sí | Parcial | Sí | Parcial | No | Sí | **DO** | FOS | Alta |
| SHAP+Causal (X8) [pre] | 2025 | TEP simulado | SHAP+causal discovery | No | No | **Ambas** | No | No | No | No | No | No | Sim | NA | Media |
| Das et al. (D1) | 2025 | BSM V2X Tampa | LLM+embeddings TS vs XGB/RF | Parcial | Sí | Parcial | Sí | No | No | No | No | Parcial | DP (fallos iny.) | ANV (sintética) | Alta |
| PA-JJAMA (D2) | 2025 | CAN Car-Hacking | LLM fine-tuned+explicación | No | Sí | Sí | Sí | No | No | No | No | No | DP | NA | Media |
| Huo et al. (D3) | 2025 | Telemetría servicio | LLM+PEFT edge-cloud | No | Parcial | No | Sí | No | Sí | Parcial | Sí | No | Sim | NA | Media |
| Syn-Diag (D4) [pre] | 2025 | Vibración bancos | LLM nube+destilación edge | No | Sí | Parcial | Sí | No | No | Parcial | Sí | No | DP (banco) | NA | Media |
| ECoLAD (D5) [pre] | 2026 | Telemetría prop. 1 veh. | TSAD clásicos vs deep embarcado | Sí | Sí | No | No | No | No | No | Sí | Sí | VR (prop., offline) | OE/ANV | Media |
| Loukas et al. (D6) [pre] | 2025 | Dashcam | VLM+LLM CoT | Parcial | No | Sí | Sí | No | No | No | No | Parcial | DP (12 casos) | ANV (semántica) | Baja |
| DeepTest/BMW (D7) [pre] | 2026 | Manuales | RAG+testing metamórfico | No | No | No | Sí | Sí | No | No | No | No | DO (benchmark) | NA | Baja-Media |
| Rimpas et al. (R1) | 2020 | OBD-II viaje real | Comparación con estándares | No | Sí | No | No | No | No | No | No | No | VR | NA | Baja |
| **TFM (propuesta)** | 2026 | OBD-II streaming (emulado) | Detector one-class + agente LLM (LangGraph) | Sí (impl.) | Sí (impl.) | **Objetivo** (causa vía RAG+verify) | Propuesto (SLM edge) | Propuesto | Propuesto | **Por validar** (evolutiva, 7 estados) | Sí (RPi emulada) | **Por validar** (held-out/open-set) | Sim (emulación declarada) + DP (contraste) | FOS (protocolo) | — |

*Surveys/frameworks sin fila: Hurtado (N26), Wang TPAMI (N29), Bala (N30), Di Maggio (N25), Montiel/River (N28), Michailidis (A1), Darban (B1), y fundamentos C1–C17, Aamodt & Plaza, AGM, Belief-R, SaySelf.*

**Lectura vertical (v2):** sigue sin existir fila con Sí/Parcial simultáneo en {NoSup, LLM, RAG, Agentes, Memoria, Edge}. Las novedades de esta iteración pueblan celdas antes vacías — memoria validada (M1, M2), edge+LLM (D3, D4), telemetría+LLM (D1) — pero siempre por pares/tríos. Además, la columna TD muestra que **ningún trabajo del corpus evalúa "fallo mecánico nuevo"** en sentido estricto salvo P5 (fallos reales en turbinas, sin descubrimiento); el máximo alcanzado en automoción es FOS con clases held-out (C19, X4) — lo que confirma que nuestro protocolo held-out/open-set es el techo metodológico defendible.

---

## 12. Datasets, algoritmos y métricas del corpus (síntesis temática)

**Datasets vehiculares utilizables (actualizado):** HCRL Driving (normalidad real, 51 señales 1 Hz) · X-CANIDS (688 señales decodificadas) · AEGIS (CC BY 4.0) · **EngineAD (anomalías reales anotadas, 8 comp. PCA, CC BY-NC restringido — contraste a nivel de método)** · SCANIA Component X (flota, features anonimizadas — pronóstico/supervivencia) · SKAB (electromecánico, para XAI contrafactual). Persisten sin cubrir: fallos mecánicos etiquetados por clase sobre OBD-II → banco propio reproducible (contribución C4) sigue justificado.

**Algoritmos dominantes por función:** detección no supervisada vehicular — one-class clásicos (iForest/LOF/OC-SVM/K-Means) y AE ligeros, con empate clásico-vs-deep confirmado ahora por tres fuentes independientes (Schmidl B2; EngineAD; ECoLAD D5 con criterio de viabilidad embarcada); razonamiento — GPT-4o/Llama-3.x/Qwen con LoRA o ICL; RAG — FAISS/Qdrant, denso+BM25; agentes — ReAct/LangGraph con roles y self-consistency; memoria — gates de admisión (MemStream), retain validado (DS-Agent, HDSO); CL — ventanas adaptativas (OASW/ADWIN) con confirmación de drift.

**Métricas reportadas:** detección — F1/F₀.₅ por eventos (0,21–0,93 según vehículo en EngineAD; 0,66–0,68 en flotas reales con etiquetas parciales), TPR/FPR, PA-F1 (con la cautela de Kim B4); explicación — fluidez vs exactitud factual (divergentes en Mahale), rúbricas Grader (X3), evaluación experta (X7); edge — latencia/ventana (2,45 ms STREAM-VAE; 2 ms nuestro pipeline F3), t/s de SLM, RAM, viabilidad bajo límites de CPU (ECoLAD).

---

## 13. Estado de las RQ tras la iteración 2

RQ9 (memoria longitudinal por vehículo): **respondida** — no existe en el dominio; lo más cercano es memoria de casos recuperables (PARAM) y KG curado offline (Lin & Miao). RQ10 (anomalías repetidas → conocimiento validado): **respondida** — el patrón existe fuera del dominio (HDSO, DS-Agent) pero no en diagnóstico vehicular ni con validación física; V2 reformulada (§3.2). RQ11: ampliada con la distinción memoria/CL y los cuatro mecanismos de seguridad (§4). RQ13: ampliada con evidencia global-vs-individual (§5). RQ5: profundizada (§6) — el puente existe por fragmentos; el eslabón vacante es la verificación de la hipótesis causal. RQ14/RQ15: reformuladas (§7.1). Quedan para la Entrega 3: lectura completa de los 8–10 trabajos de mayor peso, ejecución de §9 con acceso institucional, R2–R4 a texto completo, y la selección definitiva de los 10 antecedentes más cercanos con síntesis de convergencias/contradicciones.

## 14. Acciones que esta iteración impone al TFM

1. **Solicitar acceso a EngineAD ya** (formulario + aprobación Borealis; plazos inciertos) si se decide usarlo como contraste externo.
2. **Actualizar docs/03 y docs/06** con la formulación de datasets de §2 (sustituye a H-EA1).
3. **Reescribir la descripción de V2** en docs/01/05 con la reformulación de §3.2 (citar HDSO, DS-Agent, CBR y AGM como genealogía; diferenciarse por dominio, granularidad y validación física).
4. **Incorporar al diseño del agente:** gate de admisión tipo MemStream entre detector y memoria; confirmación de drift antes de adaptar (patrón STREAM-VAE); cuarentena de datos pre-fallo (Chesterman); juez de confianza tipo SaySelf en el paso hipótesis.
5. **Añadir el experimento global-vs-individual-vs-jerárquico** como candidato de bajo coste y alto valor diferenciador (usa el banco ya construido).
6. **Vigilancia activa:** HDSO (versiones), ECoLAD/STREAM-VAE (línea Mercedes), Das et al. (línea NSF) — re-búsqueda antes del depósito.

