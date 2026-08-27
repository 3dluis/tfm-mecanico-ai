# Estado del Arte — Tercera Entrega: multiagente (L10B), eventos vehiculares (L14), antecedentes definitivos y vacío V1–V7

**Proyecto:** TFM — Sistema inteligente híbrido Edge–Cloud para diagnóstico y mantenimiento predictivo de vehículos con OBD-II y Raspberry Pi (UAX)
**Fecha:** 2026-08-12 · **Iteración:** 3 de 4 · **Continúa:** entregas 1 (v1.1) y 2
**Identificadores nuevos:** G (L10B multiagente), E (L14A eventos de conducción), S (L14B segmentación/anomalía contextual), ADV (hallazgos adversariales V6/V7). Corpus total ≈ 145 referencias verificadas.

---

## 0-bis. Reorientación de la revisión (2026-08-27, alineación v4)

> **Esta entrega se conserva íntegra como evidencia histórica del proceso de revisión.** Sus
> búsquedas, cadenas, criterios y fichas siguen siendo válidas y no se descartan. Lo que
> cambia es la pregunta a la que la revisión sirve.
>
> **Pregunta de revisión anterior:** ¿qué se ha hecho para descubrir patrones de fallo no
> documentados a partir de telemetría vehicular, generar hipótesis diagnósticas, validarlas
> e incorporarlas como conocimiento reutilizable?
>
> **Pregunta de revisión vigente:** ¿qué se ha hecho para **explicar diagnósticos
> vehiculares con evidencia recuperada**, **verificar que cada afirmación se sostiene en esa
> evidencia** y **decidir no explicar cuando la evidencia es insuficiente**?
>
> **Criterios de relevancia actualizados.** Un trabajo es central para la revisión vigente si
> aborda al menos una de estas cuatro capacidades: diagnóstico sobre telemetría vehicular ·
> explicación mediante evidencia recuperada · atribución verificable de la evidencia
> (corrección y completitud de la cita, procedencia hasta el dato) · comportamiento ante
> evidencia insuficiente (incertidumbre, predicción selectiva, abstención). Los trabajos
> sobre memoria de agentes, consolidación validada, aprendizaje continuo y descomposición
> multiagente pasan de **centrales** a **antecedente y trabajo futuro**: se conservan
> citados, dejan de sostener el vacío.
>
> **Lo que esta revisión no cubrió** y debe cubrirse antes del depósito: fidelidad
> (*groundedness*, *faithfulness*), atribución de evidencia y citación verificable,
> incertidumbre y predicción selectiva, abstención y mitigación de alucinación en dominios
> técnicos. Protocolo de la línea nueva, con sus cadenas de búsqueda, criterios y búsqueda
> adversarial: [`linea_d_trazabilidad_fidelidad_abstencion.md`](linea_d_trazabilidad_fidelidad_abstencion.md).
>
> **Matriz de evidencias y síntesis.** La matriz de los quince antecedentes se recodifica por
> las capacidades de la PI v4 en [`docs/alineacion_v4/02_trazabilidad.md`](../alineacion_v4/02_trazabilidad.md) §3;
> la síntesis y la formulación del vacío, en `capitulo2_estado_del_arte.md` §§2.15–2.16.
> Los vacíos V1–V7 de esta entrega se leen a través de `docs/correspondencia_nomenclatura.md`.

## 0. Resumen ejecutivo

1. **RQ16 respondida con evidencia en ambos sentidos** (§2): la especialización multiagente tiene ablaciones favorables contundentes en tareas heterogéneas (SAGE −48 % de F1 sin especialistas; MA-RCA de 0,952 a 0,716 sin descomposición), pero la literatura crítica (MAST, Gao et al.) documenta que la coordinación es la primera fuente de fallo y que el margen se estrecha con modelos potentes. La configuración con mejor evidencia coincide con nuestra propuesta: **orquestador + especialistas + recuperación/memoria + verificador, con vía rápida mono-agente** — y en edge con SLM pequeños el argumento pro-descomposición se refuerza.
2. **RQ17 respondida** (§3): la detección de eventos vehiculares es madura en supervisado (93–99,7 % con eventos ya segmentados, incluso a 1 Hz con PIDs estándar), el cuello de botella es la segmentación y el régimen no supervisado; y la evidencia contextual-vs-global es sólida y cuantitativa (WisCon, QCAD, y CADD en vehículo real: el baseline global colapsa a FPR>90 % al mezclar regímenes). **Ningún trabajo compara detección de anomalías condicionada a evento vs continua PID-a-PID en diagnóstico vehicular** — hueco explícito.
3. **V6 NO sobrevive en su formulación literal** (§4): DDAS (Murphey et al., IEEE TVT **2003**) ya combinaba agentes especializados + normalidad "solo datos buenos" + memoria CBR sobre señales vehiculares; DriveAgent (2025) es multiagente LLM sobre sensores vehiculares reales; SAGE/LEMAD aplican el patrón a series temporales. V6 queda reformulado sobre la conjunción {LLM, edge, OBD-II/powertrain vivo, RAG, verificación, memoria por vehículo}, citando expresamente la tradición MAS automotriz de los 2000s como antecedente.
4. **V7 sobrevive como vacío de integración** (§4): CADD demuestra normalidad contextual sobre OBD-II en edge (sin agentes ni eventos discretos); RAAD-LLM demuestra normalidad contextual + LLM + RAG (industrial, sin eventos ni vehículo). La conjunción {segmentación en eventos operativos discretos + normalidad por evento con baseline por vehículo + razonamiento agéntico} no aparece en ningún trabajo identificado.
5. **Antecedentes definitivos:** §6 presenta los 15 más cercanos con comparación componente a componente. La contribución reformulada del TFM queda en §8.

---

## 1. Taxonomía y preguntas actualizadas

- **L10A** — Sistemas agénticos (agente único con herramientas): cubierta en E1/E2 (C1–C9, N22–N25, RCAgent, BatteryAgent).
- **L10B** — Sistemas multiagente cooperativos/orquestados para diagnóstico y mantenimiento: esta entrega (G1–G9 + ADV).
- **L14** — Detección, segmentación y representación de eventos vehiculares en series temporales: esta entrega (E1–E9, S1–S9).
- **RQ16** — arquitecturas multiagente para diagnóstico/PdM/series temporales: distribución de responsabilidades y evidencia de que la especialización mejora (o no) frente a un agente monolítico.
- **RQ17** — métodos para transformar telemetría continua en eventos/estados operativos semánticamente significativos, y en qué medida el análisis basado en eventos mejora detección y diagnóstico frente al análisis PID-a-PID.

Taxonomía de arquitecturas agénticas usada en toda la entrega: **(1)** agente único multi-herramienta · **(2)** especialistas en paralelo · **(3)** jerárquica supervisor–workers · **(4)** cooperativa/debate entre pares · **(5)** con verificador/crítico dedicado · **(6)** distribución edge/cloud de agentes.

---

## 2. L10B — Sistemas multiagente para diagnóstico (G1–G9) y respuesta a RQ16

### 2.1 Fichas nuevas (verificadas 12-08-2026)

**G1. SAGE — Kang, Kim, Park & Kang (2026) [preprint].** *Detecting Time Series Anomalies Like an Expert: A Multi-Agent LLM Framework with Specialized Analyzers.* [arXiv:2605.05725](https://arxiv.org/abs/2605.05725). Tipo **2+3**: cuatro analizadores especializados por familia de anomalía (Point/Struct/Season/Pattern) con herramientas numéricas → Detector agregador con confianza → Supervisor que redacta el informe. Yahoo/KPI/WSD: Point-F1 0,663 (+44 % vs LLMAD); **ablación: sin multi-analyzer el F1 cae de 0,797 a 0,411 (−48,4 %)**; evaluación humana 4,18/5. Limitaciones: univariante, coste de múltiples llamadas LLM por ventana. **La evidencia pro-especialización más fuerte en series temporales; no vehicular, no edge.** Cercanía: **Alta**.

**G2. MA-RCA — Fu, Ding, Qin, Yu & Xu (2025).** *Leveraging multi-agent framework for root cause analysis.* Complex & Intelligent Systems 12(4), DOI [10.1007/s40747-025-02096-0](https://link.springer.com/article/10.1007/s40747-025-02096-0). Tipo **3+5** con RAG: orquestador + Retrieval Agent (casos históricos, índice causa→síntoma) + **Validation Agent** (verificación dinámica de hipótesis) + Report Agent. Nezha: F1 0,952 vs 0,725 del agente único (RCAgent) y 0,412 de CoT. **Ablación: sin multiagente 0,716; sin Retrieval 0,295; sin Validation 0,650 → la memoria de casos y la verificación son los componentes más valiosos, no la multiplicidad per se.** Cercanía: **Alta** (valida casi exactamente nuestro esquema).

**G3. LEMAD — Ji et al. (2025).** *LLM-Empowered Multi-Agent System for Anomaly Detection in Power Grid Services.* Electronics 14(15):3008, DOI [10.3390/electronics14153008](https://www.mdpi.com/2079-9292/14/15/3008). Tipo **3**: recolección → logs (parsing LLM) → análisis streaming → detección (IF/Z-score/LSTM) + RCA en lenguaje natural; Kafka; 28,9 M invocaciones reales (State Grid). F1 84,6–88,8 % (+10,3 % vs baselines); ablación: sin agentes/LLM 75,3 %. **Coste: 3.156 ms/muestra (≈4× LogBERT, 19× PCA) — cifra crítica para dimensionar un orquestador en RPi; los propios autores posponen la versión edge.** Cercanía: Media.

**G4. BatteryAgent — Zhou et al. (2025) [preprint].** [arXiv:2512.24686](https://arxiv.org/abs/2512.24686). **Contraejemplo vehicular**: agente único (tipo 1) con capas-herramienta (percepción física + GBDT+SHAP + LLM con KB de mecanismos) logra AUROC 0,986 en fallos de batería **sin descomposición multiagente**. Cercanía: Media.

**G5. AD-AGENT — Yang et al. (2025) [preprint].** [arXiv:2505.12594](https://arxiv.org/abs/2505.12594). Tipo 3 con memoria compartida (workspace + caché): convierte instrucciones NL en pipelines de detección (PyOD/TSLib). Patrón de orquestación reutilizable. Cercanía: Media.

**G6. MAST — Cemri et al. (2025).** *Why Do Multi-Agent LLM Systems Fail?* NeurIPS 2025 · [arXiv:2503.13657](https://arxiv.org/abs/2503.13657). **Evidencia crítica:** taxonomía empírica de 14 modos de fallo sobre >1.600 trazas (κ=0,88): especificación 41,8 %, **desalineamiento inter-agente 36,9 %, verificación deficiente 21,3 %**; los arreglos simples recuperan solo +9,4/+15,6 pts. Checklist de riesgos para nuestro orquestador; justifica el agente verificador y contratos de interfaz estrictos. Cercanía: Media (metodológica).

**G7. Gao et al. (2025) [preprint].** *Single-agent or Multi-agent Systems? Why Not Both?* [arXiv:2505.18286](https://arxiv.org/abs/2505.18286). **Evidencia crítica:** las ventajas de MAS **se disipan al mejorar el LLM base**; el *request cascading* SAS→MAS por complejidad logra +1,1–12 % de precisión con hasta −20 % de coste. Implicación para nosotros (inversa): con SLM pequeños en edge la descomposición suple capacidad, pero conviene una vía rápida mono-agente para casos simples (DTC único claro). Cercanía: Media.

**G8. Idowu & Almasoud (2026) [preprint].** [arXiv:2601.22386](https://arxiv.org/abs/2601.22386). Ablación directa 3 especialistas+chairman vs mono con el mismo LLM: **ningún ganador global** — multi mejor en cribado de casos difíciles/anómalos; mono gana en el caso medio con menos coste. El perfil "multi para screening de anomalías" coincide con nuestro caso de uso. Cercanía: Baja (dominio), relevante (método).

**G9. Tian et al. (2025) [preprint].** [arXiv:2509.23537](https://arxiv.org/abs/2509.23537). Orquestación por votación multi-turno (tipo 4) iguala/supera al mejor modelo, pero con patologías cuantificadas (auto-voto, herding). **Refuerza elegir jerarquía con verificador (3+5) en lugar de debate entre pares (4).** Cercanía: Baja.

### 2.2 Respuesta a RQ16

**Patrón dominante y reparto de responsabilidades:** jerárquico (3), frecuentemente con verificador (5) y RAG; especialistas por modalidad o familia de anomalía; un agente de recuperación de casos y un validador de hipótesis. El debate entre pares (4) apenas aparece en dominios industriales y aporta margen pequeño con riesgos propios.

**A favor de la especialización (con cifras):** SAGE −48,4 % sin especialistas; MA-RCA 0,952→0,716 sin descomposición (y →0,295 sin memoria de casos, →0,650 sin validador); LEMAD +9 pts con la jerarquía; especialización mejora explicabilidad medida con humanos (4,18/5) y tipado de anomalías.

**En contra:** (i) coste/latencia (LEMAD 3,2 s/muestra; SAGE reconoce las llamadas múltiples como cuello de botella); (ii) la coordinación es la primera fuente de fallo (MAST: 36,9 % desalineamiento + 21,3 % verificación deficiente); (iii) el margen se estrecha con LLM potentes (Gao) y el mono gana el caso medio (Idowu); (iv) BatteryAgent logra SOTA vehicular con un solo agente bien equipado.

**Condiciones en las que la descomposición está justificada** (las cuatro se dan en nuestro sistema): señales heterogéneas/multimodales; salida diagnóstica estructurada y explicable; memoria de casos que explotar; **modelo base pequeño** (en edge, la descomposición suple capacidad — el argumento de Gao et al. se invierte). Decisiones de diseño que la literatura impone: agente verificador dedicado y contratos de interfaz estrictos (MAST, MA-RCA); vía rápida mono-agente para casos simples (Gao, Idowu); evitar votación entre pares (Tian); presupuestar latencia por llamada desde el diseño (LEMAD). **No se reclamará novedad por "usar múltiples agentes": la novedad, si existe, está en la conjunción con edge, OBD-II vivo y memoria validada (V6 reformulado, §4).**

---

## 3. L14 — Eventos vehiculares (E1–E9, S1–S9) y respuesta a RQ17

### 3.1 L14A — Detección de eventos/estados de conducción (E1–E9)

**E1. Escottá, Beccaro & Arjona Ramírez (2022).** Sensors 22(11):4226, DOI [10.3390/s22114226](https://www.mdpi.com/1424-8220/22/11/4226). CNN 1D vs 2D sobre IMU; 7 eventos (giros, cambios de carril, frenada/aceleración agresivas); 1D: 93,6 % acc., 2 min de entrenamiento vs 1,6 h la 2D. Referencia de coste para eventos en edge. Cercanía: Media.

**E2. Aboah et al. (2023).** *Driver Maneuver Detection Using Time Series Segmentation and Classification.* J. Transp. Eng. A 149(3), DOI [10.1061/JTEPBS.TEENG-7312](https://pmc.ncbi.nlm.nih.gov/articles/PMC10686548/). Segmentación no supervisada (Energy-Maximization) + clasificación (1D-CNN 98,99 %); 8 maniobras; datos naturalistas (77 participantes, ~290.000 km). **Hallazgo clave: la calidad del sistema la limita la segmentación (duration score 0,59–0,86), no el clasificador** — respalda nuestra fase de segmentación explícita. Cercanía: Media.

**E3. Kreutz et al. (2023) [preprint].** *Unsupervised Driving Event Discovery Based on Vehicle CAN-data.* [arXiv:2301.04988](https://arxiv.org/abs/2301.04988). SSL (VAME) + k-means sobre 9 señales CAN (Tesla Model 3); 13 eventos de evaluación; **F1-macro 0,469** — cuantifica el gap no-supervisado vs supervisado y justifica taxonomías híbridas regla+clustering. El más cercano en espíritu (descubrimiento no supervisado de eventos desde el bus). Cercanía: **Alta**.

**E4. Molina-Campoverde, Zurita-Jara & Molina-Campoverde (2025).** *Driving Pattern Analysis, Gear Shift Classification, and Fuel Efficiency Using GPS and OBD II PID Signals.* Sensors 25(13):4043, DOI [10.3390/s25134043](https://doi.org/10.3390/s25134043). **El más cercano metodológicamente: OBD-II estándar a 1 Hz**, estado latente (marcha) inferido sin sensor dedicado (K-means→KNN, acc. 99,7 %), y **análisis posterior condicionado al estado** (consumo por marcha/patrón de tráfico, R²=0,897; ralentí en neutro = máxima variabilidad). Plantilla directa para nuestros modelos de normalidad por evento. Cercanía: **Alta**.

**E5. Keskin, Yıldız & Arslannur (2025).** Transportation Research Record, DOI [10.1177/03611981241260700](https://doi.org/10.1177/03611981241260700). Representación estado-espacio velocidad-aceleración con cadena de Markov + Monte Carlo + DTW desde OBD-II real. Base formal para máquina de estados y para señalar **transiciones improbables como anomalías**. Cercanía: Media.

**E6. Zhang et al. (2026).** Sensors 26(9):2744, DOI [10.3390/s26092744](https://www.mdpi.com/1424-8220/26/9/2744). H-BMASS (segmentación bayesiana jerárquica que desacopla dinámica longitudinal/lateral) + LDA; 5 primitivas interpretables; simulador. La idea de desacoplar la dinámica longitudinal (la única visible en OBD-II sin IMU) es directamente aplicable a 1 Hz. Cercanía: Media.

**E7. Alonso-Fernandez, Butt & Tiwari (2025/26).** *Overtake Detection in Trucks Using CAN Bus Signals.* ESWA ([PII S0957417425029549](https://www.sciencedirect.com/science/article/pii/S0957417425029549)) · [arXiv:2507.00593](https://arxiv.org/html/2507.00593v1). 5 camiones Volvo en servicio; fusión RF+SVM: TPR 86,5 %/TNR 93 %. **Hallazgo transferible: los modelos por vehículo sufren sesgo condición-específico → normalizar por evento.** Cercanía: Media.

**E8. Molina-Campoverde et al. (2024).** Sensors 24(12):3884, DOI [10.3390/s24123884](https://doi.org/10.3390/s24123884). Capa viaje: segmentación de jornadas en viajes/paradas a 1 Hz con GPS (94,9 % acc.). La capa superior de nuestra jerarquía viaje→evento→muestra. Cercanía: Media.

**E9. Molina Campoverde (2020) [fundacional].** ICAT 2019, Springer CCIS, DOI [10.1007/978-3-030-42520-3_7](https://link.springer.com/chapter/10.1007/978-3-030-42520-3_7). Modos de conducción por nivel de carga desde PIDs estándar (RF, acc. 0,989). Base para el estado "alta carga". Cercanía: Media.

### 3.2 L14B — Segmentación de series y anomalía contextual (S1–S9)

**Fundamentos citables:** Chandola, Banerjee & Kumar (2009), ACM CSUR 41(3), DOI [10.1145/1541880.1541882](https://doi.org/10.1145/1541880.1541882) — taxonomía punto/contextual/colectiva, base conceptual de RQ17; Adams & MacKay (2007) [preprint] — BOCPD (CPD online); Gharghabi et al. — FLUSS/FLOSS (segmentación semántica streaming); van den Burg & Williams (2020) [preprint] + TCPD — ningún CPD domina universalmente: elegir por criterios operativos.

**S1. Truong, Oudre & Vayatis (2020) [fundacional].** *Selective review of offline change point detection.* Signal Processing 167:107299, DOI [10.1016/j.sigpro.2019.107299](https://www.sciencedirect.com/science/article/abs/pii/S0165168419303494) · librería `ruptures`. Marco coste+búsqueda+restricción; PELT ~lineal. Base algorítmica de la etapa de segmentación (trivial en RPi a 1 Hz por trayecto). Cercanía: Media.

**S2. Ermshaus, Schäfer & Leser (2023).** *ClaSP: parameter-free time series segmentation.* DMKD 37:1262–1300, DOI [10.1007/s10618-023-00923-x](https://link.springer.com/article/10.1007/s10618-023-00923-x); versión streaming **ClaSS** (PVLDB 17:1953, 2024). Mejor en 70/107 series del benchmark TSSB frente a FLOSS/BinSeg/PELT/BOCD/ESPRESSO. Candidato principal para fronteras de evento sobre canal derivado. Cercanía: Media.

**S3. Hallac, Vare, Boyd & Leskovec (2017) [fundacional].** *TICC.* KDD 2017, DOI [10.1145/3097983.3098060](https://web.stanford.edu/~boyd/papers/ticc.html). Clustering de regímenes por covarianza inversa Toeplitz con penalización de cambio; **descubre estados interpretables (girar, acelerar, frenar, crucero) en sensores de automóvil real**. El precedente más directo de "regímenes de conducción" no supervisados. Cercanía: **Alta**.

**S4. Yue et al. (2022).** *TS2Vec.* AAAI 36(8), DOI [10.1609/aaai.v36i8.20881](https://ojs.aaai.org/index.php/AAAI/article/view/20881). Representación contrastiva jerárquica, embeddings agregables a cualquier granularidad (→ embedding por evento). Cercanía: Media.

**S5. Wang, Wu, Zhou & Cai (2023).** *Time2State.* SIGMOD/PACMMOD 1(1), DOI [10.1145/3588697](https://dl.acm.org/doi/10.1145/3588697). Encoder contrastivo + DPGMM: infiere número y fronteras de estados sin etiquetas; supera a TICC/AutoPlait/HDP-HSMM en ARI/NMI. Unifica segmentación+representación+estado — la mitad izquierda de nuestro pipeline. Cercanía: Media.

**S6. Lai et al. (2024).** *E2USD.* WWW 2024, DOI [10.1145/3589334.3645593](https://dl.acm.org/doi/10.1145/3589334.3645593). Detección de estados no supervisada eficiente: 0,52–0,63 s/40k puntos; 228,8× menos memoria pico que Time2State; **desplegado en MCU STM32H747 (73 KB RAM, 45 ms/muestra)** → una RPi a 1 Hz tiene ~2 órdenes de magnitud de margen. Patrón de diseño idóneo para nuestra etapa online. Cercanía: **Alta**.

**S7. Calikus et al. (2022).** *WisCon: active ensemble learning for contextual anomaly detection.* DMKD 36:2410–2458, DOI [10.1007/s10618-022-00868-7](https://link.springer.com/article/10.1007/s10618-022-00868-7). **Evidencia contextual-vs-global:** el mismo iForest pasa de AUC-PR <0,6 (global) a 0,85–1,0 (contextual) sobre anomalías contextuales; superioridad estadística en ≥12/18 datasets (Friedman p=3,3×10⁻¹⁶). Cercanía: Media.

**S8. Li & van Leeuwen (2023).** *QCAD: explainable contextual anomaly detection using quantile regression forests.* DMKD 37(6):2517–2563, DOI [10.1007/s10618-023-00967-z](https://link.springer.com/article/10.1007/s10618-023-00967-z). Grupos de referencia k-NN contextual + QRF (densidad condicional); los detectores globales **fallan sistemáticamente en anomalías contextuales** aunque rindan en puntuales → mantener también un detector global de extremos (arquitectura híbrida). Plantilla metodológica del "modelo de normalidad por evento" con explicabilidad. Cercanía: Media.

**S9. Chen, Shin & Dadras (2024).** *CADD: Context-Aware Anomaly Detection Using Vehicle Dynamics.* RAID 2024, DOI [10.1145/3678890.3678895](https://dl.acm.org/doi/fullHtml/3678890.3678895). **El ejemplo vehicular más próximo:** normalidad condicionada al régimen físico (fases aceleración/frenada, bins de velocidad, inclinación/masa estimadas) sobre OBD-II/CAN real, con validación cruzada entre estimaciones independientes y **viabilidad en ECU en tiempo real**. TPR >96 % con FPR <0,5 % (sim.); >80 %/6 % (real). **Contextual-vs-global: el baseline global (PID-Piper, LSTM) queda en <30,7 % TPR y su FPR se degrada a >90 % al mezclar 10 condiciones de inclinación.** Sin agentes, sin eventos discretos, sin memoria, orientado a ataques/fallos de sensor. Cercanía: **Alta**.

### 3.3 Respuesta a RQ17

**Métodos disponibles:** heurísticas/umbrales (baratas, edge, 1 Hz) → segmentación explícita (EMA, H-BMASS; CPD: PELT/BOCPD/ClaSP-ClaSS) → estados markovianos (rejilla S-A) → clustering/SSL no supervisado (TICC, Time2State, E2USD, VAME+k-means) → DL supervisado (CNN 1D dominante en coste/precisión). Taxonomías típicas en tres niveles: maniobra (7–13 clases), estado operativo (ralentí/aceleración/crucero/carga/marcha), viaje. Ninguna taxonomía estándar consensuada: todas ad hoc — nuestra taxonomía puede definirse por diseño citando estas tres capas.

**Precisión:** clasificar eventos ya segmentados está casi resuelto (93–99,7 %, incluso a 1 Hz con PIDs estándar — E4); los cuellos de botella son la **segmentación** (0,59–0,86, E2) y el **régimen no supervisado** (F1 0,469, E3) — exactamente el régimen del TFM, lo que aconseja arquitectura híbrida reglas+CPD+clustering con validación propia.

**¿Mejora el análisis basado en eventos frente a PID-a-PID?** Tres piezas de evidencia cuantitativa independiente en anomalía contextual (S7, S8, S9 — la última en vehículo real con OBD-II), más evidencia indirecta vehicular (E4: estructura invisible en el análisis agregado; E7: sesgo condición-específico). **Pero ningún trabajo identificado compara detección de anomalías de salud vehicular condicionada a eventos discretos vs análisis continuo** — hueco explícito que convierte nuestra comparación (punto vs ventana vs evento) en una contribución experimental citable por sí misma.

**Viabilidad edge:** E2USD corre en un microcontrolador (73 KB RAM); a 1 Hz en RPi 5 el presupuesto sobra. La segmentación por trayecto puede ser offline-por-lotes al cerrar el viaje, con reglas + CPD online (BOCPD/ClaSS) para el streaming.

---

## 4. Revisión adversarial de V6/V7 (ADV1–ADV5) y estado V1–V7

### 4.1 Hallazgos adversariales nuevos

**ADV1. DDAS — Murphey, Crossman, Chen & Cardillo (2003) [fundacional, crítico].** *Automotive Fault Diagnosis—Part II: A Distributed Agent Diagnostic System.* IEEE Trans. Vehicular Technology 52(4), DOI [10.1109/TVT.2003.814236](https://ieeexplore.ieee.org/abstract/document/1224562). **El antecedente pre-LLM más importante encontrado en toda la revisión:** 1 Vehicle Diagnostic Agent + 9 Signal Diagnostic Agents (ECT, IAC, MAF, RPM, TP), segmentación de señal + selección de características, **fuzzy entrenada solo con datos "buenos"** (normalidad), y **CBR como memoria de fallos previos** — sobre señales vehiculares reales, en 2003. ECT 94,2 % de detección por segmento; ~20 % falsas alarmas; biblioteca de 15 casos. Sin LLM, sin RAG, sin verificación, análisis offline, sin eventos operativos ni baseline por vehículo. **Refuta la literalidad de V6; obliga a citar la tradición MAS automotriz y a formular la novedad sobre la conjunción moderna.** Cercanía: **Alta** (como antecedente).

**ADV2. Pavlíček, Pěchouček, Mařík & Flek (2007) [fundacional].** *Multi-agent-Based Diagnostics of Automotive Electronic Systems.* HoloMAS 2007, Springer LNAI, DOI [10.1007/978-3-540-74481-8_35](https://link.springer.com/chapter/10.1007/978-3-540-74481-8_35). MAS distribuido on-board/off-board sobre redes ECU (PoC simulado). Segundo pilar de la tradición; sin métricas. Cercanía: Media.

**ADV3. RAAD-LLM — Russell-Gilbert et al. (2025) [preprint].** [arXiv:2503.02800](https://arxiv.org/html/2503.02800v3) (extiende AAD-LLM, IEEE Big Data 2024). Normalidad estadística adaptativa (SPC) + LLM sin fine-tuning + **RAG** con conocimiento de planta; accuracy 70,7 %→88,6 % al añadir RAG (planta real de plásticos + SKAB). "Normalidad contextual + LLM + RAG" ya existe en industria — sin multiagente, sin eventos, sin vehículo, sin edge. Amenaza V7: Media. Cercanía: Media-Alta.

**ADV4. DriveAgent — Hou et al. (2025) [preprint; versión IEEE].** [arXiv:2505.02123](https://arxiv.org/abs/2505.02123) · [IEEE](https://ieeexplore.ieee.org/document/11197905). Multiagente LLM sobre sensores vehiculares reales (cámara/LiDAR/GPS/IMU): identifica timestamps de eventos críticos, "diagnostica anomalías potenciales del vehículo" con verificación cruzada entre modalidades. **Es percepción para conducción, no salud de powertrain**: sin OBD-II, sin normalidad por evento, sin RAG/memoria/edge. Obliga a acotar V6 a telemetría de diagnóstico/powertrain. Amenaza V6: Media-Alta. Cercanía: **Alta** (para V6).

**ADV5. Jiang & Hu (2025).** *AI Agent-Enabled Predictive Maintenance: Conceptual Proposal and Basic Framework.* Computers 14(8):329, DOI [10.3390/computers14080329](https://www.mdpi.com/2073-431X/14/8/329). Propuesta conceptual con casi todo el vocabulario de V6 (4 agentes + RAG + KG/memoria + verificación por gemelo digital + edge-fog-cloud declarado) — **sin validación cuantitativa, no vehicular**. Impide reclamar novedad del esquema funcional *en abstracto*; la novedad debe ser la instancia validada. Amenaza V6: Media. Cercanía: Media.

*Literatura gris (indicador):* asistente Bosch en-vehículo con arquitectura híbrida edge-cloud LLM (asistencia conversacional, no diagnóstico sobre telemetría).

### 4.2 Estado de los vacíos V1–V7

- **V1 (integración global)** — se mantiene con la formulación de E2 §7.1, ahora ampliada con los componentes de eventos y multiagente (ver §8).
- **V2 (memoria con validación)** — se mantiene reformulada (E2 §3.2); sin cambios en esta iteración; sigue siendo el diferenciador más robusto junto a V7.
- **V3 (adaptación por vehículo)** — se mantiene; refuerzo nuevo: E7 (sesgo condición-específico) y el concepto de *event memory* (baseline histórico por evento y por vehículo) que ningún trabajo implementa.
- **V4 (explicación decisión→causa)** — se mantiene (E2 §6); refuerzo: la unidad "evento" da a la explicación un anclaje semántico que el punto anómalo no tiene.
- **V5 (evaluación end-to-end)** — se mantiene; refuerzo: ECoLAD (D5) confirma que ni la industria tiene aún un protocolo end-to-end con capa cognitiva.
- **V6 (multiagente vehicular)** — **NO sobrevive en su formulación literal** (DDAS 2003, DriveAgent 2025, SAGE/LEMAD 2025-26, Jiang & Hu 2025). **Formulación defendible:** *"No consta una arquitectura multiagente LLM desplegada en el edge que opere sobre telemetría OBD-II/powertrain en vivo y encadene detección de anomalías contextuales, recuperación RAG, generación de hipótesis de avería, verificación y memoria longitudinal por vehículo; los multiagentes vehiculares existentes son de percepción (DriveAgent) o pre-LLM sin razonamiento generativo ni RAG (DDAS, HoloMAS), y los multiagentes LLM de series temporales (SAGE, LEMAD) no son vehiculares ni edge."* La tradición MAS automotriz de los 2000s se cita expresamente como antecedente.
- **V7 (diagnóstico basado en eventos)** — **Sobrevive como vacío de integración, no de componentes.** CADD cubre "normalidad contextual sobre OBD-II en edge" (contexto continuo, sin agentes); RAAD-LLM cubre "normalidad contextual + LLM + RAG" (sin eventos ni vehículo); E4 cubre "análisis condicionado al estado" (consumo, no anomalías). **Formulación defendible:** *"No consta un sistema que integre segmentación explícita de la telemetría OBD-II en eventos operativos discretos, modelos de normalidad por tipo de evento con baseline histórico por vehículo, y razonamiento agéntico (LLM) de diagnóstico alimentado por esas anomalías contextuales."*

---

## 5. El evento como unidad de representación de "patrones no documentados"

### 5.1 Comparación de unidades de análisis

| Unidad | Qué detecta bien | Qué pierde | Soporte en la literatura | Coste edge |
|---|---|---|---|---|
| **Punto/PID** (muestra a muestra) | Extremos absolutos (sobretemperatura, corte de señal) | Todo lo contextual: un valor normal-en-ralentí/anómalo-en-carga es invisible | z-score robusto; QCAD muestra que los globales "sobresalen en puntuales" pero fallan en contextuales (S8) | Mínimo |
| **Ventana temporal fija** (estado actual del prototipo) | Dinámica local multivariante; degradación en la ventana | Mezcla regímenes dentro de la ventana → FPR alto al variar condiciones (CADD: FPR>90 % del baseline global al mezclar regímenes, S9) | Práctica dominante (B2, N5–N8); crítica implícita en S9 | Bajo (validado: ~2 ms/ventana en F3) |
| **Evento operativo** (aceleración, ralentí…) | Anomalías contextuales; comparación de eventos equivalentes entre sí y a lo largo del tiempo | Anomalías que cruzan fronteras de evento; depende de la calidad de la segmentación (E2: el cuello de botella) | S7/S8/S9 (contextual>global, cuantificado); E4 (estructura invisible en el agregado); **nadie lo aplica a salud vehicular** | Bajo-medio (E2USD en MCU; reglas+CPD a 1 Hz triviales) |
| **Patrón/evento recurrente** (P = {evento, contexto, variables, secuencia, desviación, recurrencia, vehículo, evidencia}) | Exactamente el objetivo de la RQ principal: combinaciones recurrentes no documentadas ligadas a transiciones operativas | Requiere las tres capas anteriores + memoria longitudinal; riesgo de sobre-ajuste a hábitos del conductor | Motif discovery/Matrix Profile (S-fundamentos); recurrencia como evidencia = nuestro estado PATRÓN CANDIDATO; **sin antecedente integrado** | Medio (minería por lotes al cerrar viaje) |

### 5.2 Veredicto: ¿es el evento la unidad adecuada?

**Sí, con arquitectura en capas, y la literatura lo respalda pieza a pieza:** (i) la evidencia contextual-vs-global es contundente y llega hasta vehículo real (S9); (ii) el evento da al agente una unidad *semánticamente interpretable* — "presión de riel baja durante aceleración a alta carga, 7/9 veces, contra 1.243 aceleraciones normales históricas" es una entrada de razonamiento incomparablemente mejor que N puntos anómalos dispersos, y conecta directamente con la explicación causal (V4) y con la memoria (V2); (iii) el baseline histórico por evento y por vehículo operacionaliza la personalización (V3) con la estructura jerárquica que la literatura recomienda (P5: flota como normalizador, individuo como señal — aquí: catálogo de eventos como esquema común, distribución por vehículo como baseline).

**La distinción de tres niveles queda anclada en la literatura:** *evento conocido* (aceleración — detección madura, E1–E9); *anomalía durante un evento* (anomalía contextual — S7/S8/S9, evaluable con nuestro banco de fallos); *patrón nuevo* (combinación recurrente no documentada ligada a transiciones — sin antecedente; se operacionaliza como recurrencia de anomalías contextuales del mismo tipo de evento + protocolo held-out/open-set de C18–C19). Esta cadena da, por fin, una definición operativa completa de "patrón de fallo no documentado" defendible ante el tribunal.

**Advertencias de diseño que la literatura impone:** mantener también el detector global de extremos (S8) y el detector por ventana ya validado (híbrido de tres capas, no sustitución); la segmentación es el eslabón débil (E2) → empezar con reglas+umbral sobre PIDs (estados groseros: ralentí/aceleración/crucero/frenada/alta carga), validarla con el emulador (ground truth de eventos gratis en nuestros escenarios), y dejar TICC/E2USD como refinamiento; el F1 0,469 de E3 advierte contra el descubrimiento de eventos puramente no supervisado.

---

## 6. Los 15 antecedentes más cercanos (selección definitiva)

Criterio: máximo solapamiento componente a componente con la propuesta. ✔ = lo tiene; ◐ = parcial; · = no.

| # | Antecedente | OBD/CAN vivo | No sup. | Evento | Multiag. | LLM | RAG | Verif. | Memoria | Edge | Por qué está aquí |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Mahale et al. 2025** (Discover Computing) | ◐ (tabular) | ◐ | · | · | ✔ | ✔ | ◐ (juez) | · | · | La cadena OBD-II→ML→RAG→LLM peer-reviewed más completa |
| 2 | **Lin & Miao 2025** (Electronics) | · | · | · | ◐ | ✔ | ◐ | ◐ | ◐ (KG) | · | La capa cognitiva más sofisticada; explicación de causa mecánica |
| 3 | **CADD 2024** (RAID) | ✔ | ✔ | ◐ (contexto continuo) | · | · | · | ✔ (consistencia cruzada) | · | ✔ | Normalidad contextual sobre OBD-II real en edge — la mitad de V7 |
| 4 | **DDAS 2003** (IEEE TVT) | ◐ (grabaciones) | ✔ (solo-bueno) | ◐ (segm. señal) | ✔ | · | · | · | ✔ (CBR) | · | El antecedente multiagente vehicular con memoria; genealogía obligada |
| 5 | **SAGE 2026** [pre] | · | ◐ | · | ✔ | ✔ | · | ◐ (agregador) | · | · | El patrón multiagente de detección+explicación en series; ablación −48 % |
| 6 | **MA-RCA 2025** (CIS) | · | ◐ | · | ✔ | ✔ | ✔ | ✔ | ✔ (casos) | · | Orquestador+RAG+validador+memoria: nuestro esquema, en TI |
| 7 | **Giannoulidis 2024** (EDBT) | ✔ | ✔ | · | · | · | · | · | ◐ | · | El suelo empírico de detección no supervisada OBD-II real |
| 8 | **Cherdo 2023** (Sensors) | ✔ (CAN) | ✔ | · | · | · | · | · | · | ✔ | Detector no supervisado vehicular dimensionado para embebido |
| 9 | **PARAM 2025** [pre] | · | ◐ | · | ✔ | ✔ | ✔ | ◐ | ◐ | · | Pipeline señal→detección→RAG→prescripción completo (rodamientos) |
| 10 | **Park et al. 2025** (PHMAP) | · | · | · | ✔ | ✔ (local) | ✔ | ◐ (supervisor) | · | ◐ | Multiagente con LLM local sobre códigos de error + manuales |
| 11 | **HDSO 2026** [pre] | · | · | · | ◐ | ✔ | · | ✔ (falsación) | ✔ (validada) | · | El ciclo de memoria validada casi isomorfo a V2 (en skills/benchmark) |
| 12 | **FaultExplainer 2024** [pre] | · | ✔ (PCA) | · | · | ✔ | ◐ | · | · | · | No supervisado→hipótesis LLM incluso en fallos no vistos (TEP) |
| 13 | **RAAD-LLM 2025** [pre] | · | ✔ (SPC) | ◐ (contexto sem.) | · | ✔ | ✔ | · | · | · | Normalidad contextual+LLM+RAG en planta real (+18 pts por RAG) |
| 14 | **Das et al. 2025** (SaT-CPS) | ◐ (BSM) | ◐ | · | · | ✔ | · | · | · | · | LLM sobre telemetría vehicular temporal; el ML clásico gana → ADR-0009 |
| 15 | **DriveAgent 2025** [pre/IEEE] | · (percepción) | ◐ | ◐ (timestamps) | ✔ | ✔ | · | ◐ (cruzada) | · | · | El multiagente LLM vehicular existente; delimita V6 |
| — | **TFM** | ✔ (streaming emulado, declarado) | ✔ (impl.) | **Propuesto** | **Propuesto** | Propuesto (SLM) | Propuesto | Propuesto (verify determinista) | **Por validar** (7 estados) | ✔ (RPi emulada) | — |

**Lectura:** ninguna fila reúne más de 5 de las 9 columnas; los cinco componentes con menos cobertura simultánea son {Evento, Memoria validada, Edge, Verificación, OBD vivo}. Las combinaciones ya existentes por pares se citan como antecedentes directos de cada módulo; la contribución se defiende sobre la conjunción y sobre los mecanismos concretos (§8).

**Convergencias del corpus:** (1) clásico ligero ≥ deep en detección embarcada (B2, EngineAD, ECoLAD, LEMAD-latencia); (2) el LLM no debe ser el detector (Das, FD-LLM, BatteryAgent como excepción instrumentada) sino el razonador sobre evidencia estructurada; (3) memoria/recuperación de casos y verificación son los componentes de mayor valor en sistemas agénticos (MA-RCA ablación); (4) el contexto/régimen multiplica la detectabilidad (S7/S8/S9); (5) la personalización por unidad supera al global bajo no-IID (P4, P9, EngineAD).
**Contradicciones a discutir en el capítulo:** multiagente mejora (G1–G3) vs se disipa/estorba (G6–G8) — resuelta por condiciones de aplicabilidad (§2.2); RAG reduce alucinación (C12, RAAD-LLM +18 pts) vs exactitud factual baja pese a RAG (Mahale) — resuelta por la necesidad de verificación posterior; fluidez ≠ exactitud (Mahale) vs evaluación humana alta (SAGE) — resuelta por diseño de evaluación (juez calibrado + métricas objetivas, C16/C17).

---

## 7. Matriz v3 — filas nuevas con columnas ampliadas

Columnas nuevas: **MA** = Multiagente (Sí/No) · **Arq** = tipo arquitectura (1–6, §1) · **EA** = Event-aware (Sí/Parcial/No) · **Seg** = método de segmentación · **BpE** = baseline por evento/régimen (Sí/Parcial/No). (NV y TD como en E2.)

| Ref | Año | Datos | Técnica | NoSup | LLM | RAG | MA | Arq | EA | Seg | BpE | Memoria | Edge | NV | TD | Cercanía |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G1 SAGE [pre] | 2026 | Series benchmark | 4 analizadores+LLM | ◐ | Sí | No | **Sí** | 2+3 | No | — | No | No | No | DP | ANV | Alta |
| G2 MA-RCA | 2025 | Microservicios+eléctrico | Orquestador+RAG+validador | ◐ | Sí | Sí | **Sí** | 3+5 | No | — | No | Sí (casos) | No | DP+DO | FOS | Alta |
| G3 LEMAD | 2025 | Telemetría real State Grid | IF/LSTM+LLM+Kafka | ◐ | Sí | No | **Sí** | 3 | ◐ | — | No | No | No | DO (offline) | ANV | Media |
| G4 BatteryAgent [pre] | 2025 | Baterías | Física+GBDT+SHAP+LLM | No | Sí | KB | No | 1 | No | — | No | No | No | n.c. | NA | Media |
| G5 AD-AGENT [pre] | 2025 | Benchmarks AD | Generación de pipelines | ◐ | Sí | doc | **Sí** | 3 | No | — | No | Sí (workspace) | No | DP | NA | Media |
| G6 MAST | 2025 | 1.600+ trazas MAS | Taxonomía de fallos | — | Sí | No | Sí (meta) | 2–5 | — | — | — | — | No | Sim/DP | NA | Media |
| G7 Gao et al. [pre] | 2025 | Benchmarks | SAS vs MAS + cascading | — | Sí | No | Ambos | 1 vs 2–4 | — | — | — | No | No | DP | NA | Media |
| E2 Aboah | 2023 | IMU+GPS+OBD 30 Hz | EMA+1D-CNN | ◐ (segm.) | No | No | No | — | **Sí** | EMA | No | No | No | FR | NA | Media |
| E3 Kreutz [pre] | 2023 | CAN Tesla | SSL(VAME)+k-means | **Sí** | No | No | No | — | **Sí** | Clustering latente | No | No | No | VR | NA | Alta |
| E4 Molina-C. 2025 | 2025 | **OBD-II 1 Hz**+GPS | K-means+KNN | ◐ | No | No | No | — | **Sí** | Clustering estados | **◐ (consumo/marcha)** | No | No | VR | NA | Alta |
| E5 Keskin | 2025 | OBD-II 50 Hz | Markov S-A+DTW | Sí | No | No | No | — | ◐ | Rejilla S-A | No | No | No | VR | NA | Media |
| E7 Alonso-F. | 2025/26 | CAN 5 camiones | RF/SVM fusión | No | No | No | No | — | **Sí** | Trigger+ventanas | No | No | No | FR | NA | Media |
| S3 TICC | 2017 | Sensores auto real | Clustering Toeplitz | **Sí** | No | No | No | — | **Sí** | Clustering regímenes | No | No | ◐ | VR | NA | Alta |
| S6 E2USD | 2024 | HAR+sintético | Estados contrastivos ligeros | **Sí** | No | No | No | — | **Sí** | Embedding+clustering adapt. | No | No | **Sí (MCU)** | DP+BH | NA | Alta |
| S7 WisCon | 2022 | Tabulares | Ensemble de contextos | ◐ | No | No | No | — | ◐ | Partición atributos | **Sí** | No | No | DP | ANV | Media |
| S8 QCAD | 2023 | Tabulares | k-NN contextual+QRF | **Sí** | No | No | No | — | ◐ | k-NN contextual | **Sí** | No | ◐ | DP | ANV | Media |
| S9 CADD | 2024 | **OBD-II/CAN vivo** | Física condicionada+verif. cruzada | **Sí** | No | No | No | — | **Sí** | Fases físicas+bins | **Sí** | No | **Sí (ECU)** | VR+Sim | ANV | **Alta** |
| ADV1 DDAS | 2003 | Señales ECU grabadas | Fuzzy+wavelets+CBR | **Sí** (solo-bueno) | No | No | **Sí** | 3 | ◐ | Segm. de señal | No | **Sí (CBR)** | No | BH (datos reales) | ANV | **Alta** |
| ADV3 RAAD-LLM [pre] | 2025 | Planta real+SKAB | SPC adaptativo+LLM+RAG | **Sí** | Sí | **Sí** | No | 1 | ◐ | — | No | No | No | DO+DP | ANV | Media-Alta |
| ADV4 DriveAgent [pre/IEEE] | 2025 | Cámara/LiDAR/GPS/IMU | LLM multimodal | ◐ | Sí | No | **Sí** | 2+4 | ◐ | Relevancia LLM | No | No | No | VR | ANV | Alta |
| ADV5 Jiang & Hu | 2025 | Prototipo conceptual | LLM+KG+gemelo digital | — | Sí | Sí | **Sí** | 4/6 | No | — | No | Sí | ◐ (declarado) | Sim (concepto) | NA | Media |
| **TFM (propuesta)** | 2026 | OBD-II streaming emulado | Segm. eventos + one-class por evento + multiagente SLM | Sí (impl.) | Propuesto | Propuesto | **Propuesto** | **3+5+6** | **Propuesto** | **Reglas+CPD (→TICC/E2USD)** | **Por validar** | **Por validar (7 estados)** | Sí (RPi emulada) | Sim (declarada)+DP | FOS (protocolo) | — |

*Para las filas de E1/E2 la ampliación de columnas (MA/Arq/EA/Seg/BpE) queda: todos MA=No salvo Park (Sí, 3), Lee (Sí, 2/3), PARAM (Sí, 3), Lin & Miao (◐); EA=No en todo el corpus previo salvo Khemani (◐ contexto ambiental) y STREAM-VAE (◐ dual-path); BpE=No en todo el corpus previo. Se consolidará la matriz única completa en la Entrega 4.*

---

## 8. Reformulación de la contribución científica (post-búsqueda)

**Formulación del vacío integrador (sustituye y amplía la de E2 §7.1):**

> "En la literatura analizada (≈145 referencias verificadas, hasta agosto de 2026) no se identificó ninguna propuesta que integre, en un único sistema evaluado end-to-end: (i) telemetría OBD-II en streaming; (ii) segmentación explícita en eventos operativos discretos con modelos de normalidad por tipo de evento y baseline histórico por vehículo; (iii) detección no supervisada de anomalías contextuales ejecutada en el dispositivo edge; (iv) un sistema multiagente con modelos de lenguaje bajo restricciones edge, con agentes de recuperación documental (RAG), historial, hipótesis y verificación; y (v) una memoria longitudinal por vehículo con ciclo explícito de estados de evidencia donde solo el conocimiento validado se consolida. Los antecedentes cubren a lo sumo tres de estos cinco ejes (DDAS: multiagente+normalidad+memoria, 2003, pre-LLM; CADD: contexto+OBD-II+edge, sin agentes; MA-RCA: agentes+RAG+verificación+memoria, en TI; RAAD-LLM: contexto+LLM+RAG, industrial), y ninguno los conjuga sobre telemetría vehicular de diagnóstico."

**Contribuciones defendibles, en orden de solidez:**

1. **C-INT (integración, V1+V6+V7):** primera instancia *validada experimentalmente* de la cadena eventos→normalidad-por-evento→anomalía contextual→multiagente-SLM-edge→hipótesis→verificación→memoria sobre OBD-II. Se declara como novedad de integración y de instancia (Jiang & Hu demuestran que el esquema en abstracto ya está propuesto; nuestra diferencia es la instancia vehicular medida).
2. **C-MEM (mecanismo, V2):** la memoria de 7 estados con validación previa a consolidación, aplicada a conocimiento diagnóstico declarativo y anclada en verificación determinista contra telemetría — con la genealogía completa (CBR/AGM/HDSO/DS-Agent) y motivación adversarial (AgentPoison/MINJA).
3. **C-EVT (metodológica, V7):** la formalización del patrón P = {evento, contexto, variables, secuencia, desviación, recurrencia, vehículo, evidencia} como unidad de representación de "patrones no documentados", y la comparación experimental punto-vs-ventana-vs-evento en detección de salud vehicular — comparación que la literatura no contiene.
4. **C-EXP (experimental, V5):** banco de fallos reproducible + protocolo held-out/open-set en datos, corpus RAG y memoria + evaluación end-to-end con presupuesto edge (llenando el hueco declarado por Bala, Di Maggio y ECoLAD).
5. **C-PERS (secundaria, V3):** experimento global-vs-individual-vs-jerárquico por evento sobre el banco (evidencia previa: P4/P5/P9/EngineAD).

**Impacto en el diseño del sistema (para validar con el tutor antes de implementar el agente):** la arquitectura multiagente adopta jerarquía con verificador (3+5) y distribución edge-cloud (6), con vía rápida mono-agente para casos triviales (G7/G8) y contratos de interfaz estrictos (G6); el pipeline edge añade la capa de eventos (reglas+CPD primero; TICC/E2USD como refinamiento) manteniendo el detector por ventana ya validado y un guardián global de extremos (S8) — tres capas de detección, no una. El número de agentes NO se fija por diseño previo: se parte del mínimo funcional (orquestador, detección/eventos, recuperación, hipótesis, verificación, memoria, explicación) y la descomposición adicional se justifica solo si la ablación propia lo respalda (lección de G6–G8 y RQ16).

---

## 9. Recuentos del barrido de esta iteración (preliminares, por web)

Cuatro bloques (L10B, L14A, L14B, adversarial V6/V7): ≈ 380 registros visualizados en ~48 consultas → ≈ 250 tras deduplicación → ≈ 72 evaluados en fuente primaria → **32 fichas nuevas** (G: 9; E: 9; S: 9 + 4 fundamentos; ADV: 5 únicas — CADD/SAGE/LEMAD deduplicadas entre bloques) + 1 indicador de literatura gris. Preprints marcados: 12. Corpus total ≈ 145. Los recuentos siguen siendo del barrido web con verificación en editor; el flujo PRISMA formal por bases sigue pendiente de la ejecución de las consultas de E2 §9 con acceso institucional (añadir a esa lista: `TITLE-ABS-KEY(("multi-agent") AND ("fault diagnosis" OR "predictive maintenance" OR "anomaly detection")) AND PUBYEAR > 2020` y `TITLE-ABS-KEY(("driving event" OR "maneuver recognition" OR "operating state" OR "trip segmentation") AND ("OBD" OR "CAN" OR "vehicle telemetry")) AND PUBYEAR > 2020`).

## 10. Plan para la Entrega 4 (capítulo completo)

1. Ejecutar consultas formales (E2 §9 + las dos nuevas) con acceso institucional; construir el diagrama PRISMA definitivo; leer a texto completo R2–R4 y los 8–10 trabajos de mayor peso.
2. Consolidar la matriz única (≈150 filas, todas las columnas) como anexo; el capítulo usará tablas temáticas compactas.
3. Redactar el capítulo 2 completo (estructura de la E4 del plan original + secciones nuevas: multiagente y eventos), con la sección final "Vacío de investigación y oportunidad científica" respondiendo: qué sabemos / qué pueden hacer las soluciones existentes / qué no resuelven / qué propone este TFM / cómo mediremos el aporte.
4. Vigilancia pre-depósito: HDSO, SAGE, DriveAgent, línea Mercedes (ECoLAD/STREAM-VAE), RAAD-LLM (versión journal), EngineAD (versión revisada).

