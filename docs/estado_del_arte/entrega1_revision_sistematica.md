# Estado del Arte — Primera Entrega: Protocolo de revisión sistemática y primer corpus verificado

**Proyecto:** TFM — Sistema inteligente híbrido Edge–Cloud para diagnóstico y mantenimiento predictivo de vehículos con OBD-II y Raspberry Pi
**Fecha de la entrega:** 2026-08-12 · **Iteración:** 1 de 4
**Relación con trabajo previo:** este documento formaliza y amplía el primer barrido de Fase 1 (`docs/estado_del_arte/00_sintesis.md`, `linea_a…`, `linea_b…`, `linea_c….md`, 35+ referencias verificadas el 2026-08-12). Las referencias de ese barrido se citan aquí con sus identificadores originales (A1–A8, B1–B7, C1–C20) y NO se re-listan en detalle; las fichas nuevas de esta entrega usan identificadores N1–N32.

---

## 1. Protocolo de revisión

### 1.1 Objetivo de la revisión

Construir una revisión de literatura, inspirada en el procedimiento PRISMA, que permita: (i) identificar las soluciones existentes para diagnóstico y mantenimiento predictivo vehicular basadas en telemetría; (ii) compararlas por técnica, datos, arquitectura y resultados; (iii) detectar sus limitaciones; (iv) establecer qué componentes de la propuesta ya han sido investigados por separado; (v) comprobar si existen trabajos que integren varios de ellos; (vi) justificar con evidencia el vacío de investigación; y (vii) delimitar el aporte novedoso defendible del TFM.

### 1.2 Pregunta de investigación del TFM y preguntas de revisión

Pregunta principal: *¿Puede un agente inteligente híbrido, que combine modelos de lenguaje, aprendizaje no supervisado, memoria evolutiva y RAG, descubrir y explicar patrones de fallo vehicular previamente no documentados utilizando datos OBD-II?*

Las quince preguntas de revisión (RQ1–RQ15) se mapean sobre la taxonomía de la sección 4. En esta primera entrega se responden de forma preliminar RQ1–RQ3, RQ6–RQ8, RQ11, RQ12, RQ14 y RQ15 (sección 8); las restantes se completarán en las entregas 2 y 3.

### 1.3 Fuentes y periodo

- **Ventana temporal:** enero 2021 – agosto 2026, admitiendo trabajos anteriores únicamente como fundacionales (se marcan como tales: p.ej. Gelgele & Wang 1998; Prytz 2015; USAD 2020; Lewis 2020; Ferreira 2020).
- **Fuentes objetivo del protocolo:** IEEE Xplore, ACM DL, ScienceDirect, Springer, Scopus, Web of Science, MDPI, SAE International; Google Scholar / búsqueda web para descubrimiento; arXiv solo para trabajos relevantes y recientes, siempre marcados **[preprint]**.
- **Limitación operativa declarada (transparencia metodológica):** en esta iteración la búsqueda se ejecutó mediante buscador web general con verificación posterior de cada registro en la página del editor (MDPI, Springer/Nature, ACM DL, ACL Anthology, PHM Society, OpenProceedings, JMLR, arXiv). El acceso automatizado a IEEE Xplore y ScienceDirect estuvo parcialmente bloqueado (robots/403): los candidatos de esas plataformas que no pudieron verificarse en fuente primaria **se descartaron en lugar de citarse sin verificar**, y quedan anotados en §5.4 para recuperación manual con acceso institucional de la universidad. Por el mismo motivo, los recuentos de §3 corresponden únicamente al barrido preliminar por web (resultados visualizados por consulta), no a totales de bases de datos indexadas ni al flujo PRISMA definitivo; la consulta formal a Scopus/WoS/IEEE con las cadenas de §2, con registro de números exactos por base, queda planificada para la Entrega 2.

### 1.4 Procedimiento

1. Definición de taxonomía (13 líneas) y mapeo a RQs.
2. Ejecución de cadenas de búsqueda por línea (5 bloques de búsqueda paralelos).
3. Cribado por título/resumen contra criterios de inclusión/exclusión.
4. Verificación de cada candidato en fuente primaria (página del editor o DOI resuelto); doble verificación independiente de los registros de mayor riesgo (publicaciones 2026 y preprints).
5. Extracción estructurada (ficha por publicación con los campos de §5).
6. Construcción incremental de la matriz comparativa (§6) y clasificación de cercanía (Alta/Media/Baja).
7. Síntesis de vacíos (§8).

**Regla estricta aplicada:** ningún artículo, autor, DOI, dataset, métrica o conclusión se registra sin haber sido verificado en una fuente real. Los campos no verificables se marcan "no consta".

---

## 2. Cadenas de búsqueda definitivas

Cadenas ejecutadas en esta iteración (buscador web general, 12-08-2026), reutilizables tal cual en Scopus/WoS/IEEE con sintaxis adaptada (TITLE-ABS-KEY, comillas y operadores AND/OR):

**L1 — OBD-II y adquisición:**
- `OBD-II data acquisition survey vehicle diagnostics SAE J1979 review 2022 2023 2024`
- `ELM327 OBD-II PID sampling rate data quality study`

**L2 — Diagnóstico tradicional:**
- `expert system rule-based automotive fault diagnosis DTC diagnostic trouble codes limitations root cause`
- `diagnostic trouble code DTC prediction vehicle unsupervised anomaly detection OBD`

**L3–L5 — ML, anomalías, series temporales/PdM:**
- `unsupervised anomaly detection vehicle OBD-II telemetry autoencoder fault detection 2023 2024`
- `LSTM autoencoder anomaly detection CAN bus vehicle sensor fault mechanical`
- `OBD-II data machine learning vehicle fault diagnosis random forest XGBoost engine classification`
- `remaining useful life prediction battery electric vehicle LSTM transformer journal`

**L6–L7 — Fusión multisensor y XAI:**
- `multi-sensor fusion OBD-II GPS IMU vehicle fault anomaly detection driving context`
- `context-aware anomaly detection vehicle CAN GPS environmental data reduce false positives predictive maintenance`
- `SHAP LIME explainable AI vehicle fault diagnosis machine learning`

**L8–L10 — LLM, RAG, agentes:**
- `LLM diagnostic trouble codes DTC automotive large language model diagnosis`
- `retrieval augmented generation automotive service manuals technical service bulletins vehicle diagnostics`
- `LLM multi-agent framework industrial fault diagnosis maintenance agents tool calling`
- `large language models time series anomaly detection explanation`

**L11–L12 — Memoria de agentes y continual learning:**
- `continual learning predictive maintenance concept drift telemetry incremental`
- `concept drift detection anomaly detection vehicle telemetry OBD online learning`
- `LLM agent memory episodic semantic long-term survey` *(cubierta en el primer barrido: C6–C9)*

**L13 — Edge AI / Edge–Cloud:**
- `edge cloud collaborative architecture predictive maintenance connected vehicles inference offloading`
- `TinyML predictive maintenance edge devices TensorFlow Lite ONNX quantization Raspberry Pi`

El registro completo de cadenas ejecutadas (con variantes de verificación por título exacto) figura en los anexos de proceso de cada bloque de búsqueda; se conserva para reproducibilidad.

---

## 3. Criterios PRISMA y flujo de esta iteración

### 3.1 Criterios de inclusión

(I1) publicado 2021–2026, o anterior si es fundacional (marcado); (I2) estudia diagnóstico, anomalías, pronóstico o mantenimiento; (I3) usa telemetría vehicular (OBD-II/CAN/UDS/sensores) o, para las líneas 8–13, técnicas directamente transferibles (LLM/RAG/agentes/memoria/CL/edge) en dominios de mantenimiento o monitorización; (I4) emplea técnicas de IA o define estándares/datos que las habilitan; (I5) metodología o experimentos verificables; (I6) relevante para algún componente del sistema propuesto.

### 3.2 Criterios de exclusión

(E1) material comercial y blogs como evidencia principal; (E2) sin metodología; (E3) conducción autónoma irrelevante; (E4) ciberseguridad CAN pura, salvo técnicas de anomalías reutilizables (se marca); (E5) duplicados; (E6) información insuficiente para evaluar resultados; (E7) **no verificable en fuente primaria** (bloqueo de acceso): descartado y anotado para recuperación manual.

### 3.3 Recuentos del barrido preliminar por web (esta iteración)

**Nota de alcance:** los recuentos siguientes documentan únicamente el barrido preliminar realizado mediante buscador web con verificación en editor. **No constituyen el flujo PRISMA definitivo.** El diagrama PRISMA formal se construirá cuando se ejecuten las cadenas de §2 en Scopus, Web of Science, IEEE Xplore y demás bases con acceso institucional de la universidad, registrando números exactos por base de datos (planificado desde la Entrega 2).

| Etapa | Recuento |
|---|---|
| Consultas ejecutadas (5 bloques temáticos) | 49 cadenas/variantes |
| Registros visualizados en resultados de búsqueda | ≈ 386 |
| Tras eliminar duplicados entre consultas y espejos (ResearchGate, DOAJ, agregadores) | ≈ 230 |
| Candidatos evaluados en página de editor / texto accesible | ≈ 55 |
| Excluidos en evaluación (E1–E7; detalle en §5.4) | ≈ 23 |
| **Incluidos nuevos en esta entrega (N1–N32)** | **32** |
| Corpus previo verificado (barrido Fase 1: A1–A8, B1–B7 + tabla SLM, C1–C20, datasets) | 39 |
| **Corpus total verificado a la fecha** | **≈ 71** |

De los 32 nuevos: 28 peer-reviewed y 4 **[preprint]** arXiv marcados. Los registros con año 2026 y los preprints se sometieron a una segunda verificación independiente (Abboush 2026, Khemani & Qureshi 2026, Di Maggio 2025, Lee et al. 2025, EngineAD 2026: confirmados en editor/arXiv el 12-08-2026).

---

## 4. Taxonomía del estado del arte (13 líneas ↔ RQs)

| # | Línea | RQs | Cobertura actual |
|---|---|---|---|
| L1 | OBD-II y adquisición de datos (ISO 15031, SAE J1979/J1979-2, PIDs, ELM327, CAN, UDS, datasets) | RQ1 | A1, datasets A, N1–N2, normas §5.1 |
| L2 | Diagnóstico tradicional (DTC, sistemas expertos, reglas) | RQ1, RQ2 | N3–N4 |
| L3 | ML supervisado para diagnóstico automotriz | RQ2, RQ13 | A3–A8, N9–N10 |
| L4 | No supervisado y detección de anomalías | RQ3, RQ14 | B1–B7, C18–C20, N5–N8 |
| L5 | Series temporales y PdM (RUL, degradación) | RQ4 | A2, A4–A6, N11–N12 |
| L6 | Fusión multisensor y contexto | RQ4, RQ13 | N13–N15 |
| L7 | XAI en diagnóstico | RQ5 | A7, N16–N17 |
| L8 | LLMs en mantenimiento/diagnóstico | RQ6 | A-LLM1/2, N18–N19 |
| L9 | RAG en mantenimiento/diagnóstico | RQ7 | C10–C15, N20–N21 |
| L10 | Sistemas agénticos aplicados | RQ8 | C1–C5, N22–N25 |
| L11 | Memoria para agentes | RQ9, RQ10 | C6–C9 |
| L12 | Continual / online learning | RQ11 | N26–N29 |
| L13 | Edge AI y Edge–Cloud | RQ12 | B-SLM, B-TinyML, N30–N32 |

Distinción transversal aplicada en todas las fichas: PID OBD-II estándar / PID propietario / UDS / CAN crudo / sensores externos (columna "Datos" de la matriz).

---

## 5. Publicaciones verificadas nuevas (N1–N32)

Cada ficha se verificó en la fuente indicada el 12-08-2026. Formato compacto; los campos ausentes en la fuente accesible se marcan "no consta". Las fichas completas del corpus previo están en `linea_a/b/c_*.md`.

### 5.1 L1 — OBD-II y adquisición (N1–N2 + normas)

**N1. Rykała, Grzelak, Rykała, Voicu & Stoica (2023).** *Modelling Vehicle Fuel Consumption Using OBD-II data.* Energies 16(21):7266. DOI [10.3390/en16217266](https://www.mdpi.com/1996-1073/16/21/7266). PIDs estándar vía adaptador clase ELM327 (Vgate iCar Pro) + GPS; 1 vehículo, ruta real ~320 km, 1 Hz. Regresión multivariante (R²=0,85) supera a MLP (+73 % MSE) y árboles (+163 %). **Aporte a L1:** techo real de muestreo ~1 Hz con hardware low-cost y calidad de datos alcanzable — directamente aplicable a nuestro pipeline ELM327→RPi. Limitaciones: 1 vehículo/conductor. Cercanía: **Baja**.

**N2. Ramai, Ramnarine, Ramharack, Bahadoorsingh & Sharma (2022).** *Framework for Building Low-Cost OBD-II Data-Logging Systems for Battery Electric Vehicles.* Vehicles 4(4):1209–1222. DOI [10.3390/vehicles4040064](https://www.mdpi.com/2624-8921/4/4/64). **PIDs propietarios** (Hyundai Ioniq, 2101–2105 por ingeniería inversa) sobre CAN leídos con **Raspberry Pi Zero W** cada 5 s. Documenta la ausencia de estándar OBD-II para baterías BEV y la no transferibilidad de PIDs entre fabricantes. Cercanía: **Media** (valida RPi como nodo de adquisición y fundamenta la distinción estándar/propietario).

**Normas citables (referencias normativas, no fichas):** SAE J1979 / [J1979-DA](https://www.sae.org/standards/content/j1979da_202104/) (PIDs); SAE J1979-2 "OBDonUDS" — transición hacia UDS obligatoria en EE. UU. desde MY2027 según [CARB](https://ww2.arb.ca.gov/node/42081); ISO 15031; ISO 14229 (UDS); ISO 15765 (CAN de diagnóstico).

### 5.2 L2 — Diagnóstico tradicional (N3–N4)

**N3. Gelgele & Wang (1998) [fundacional].** *An expert system for engine fault diagnosis (EXEDS).* J. Intelligent Manufacturing 9(6):539–545. DOI [10.1023/A:1008888219539](https://link.springer.com/article/10.1023/A:1008888219539). Sistema experto de reglas sobre síntomas. Limitaciones canónicas: conocimiento estático, mantenimiento manual, sin aprendizaje. **Motiva el salto reglas→agente con RAG y memoria.** Cercanía: Baja (contexto).

**N4. Ferreira, Scholz & Prytz (2020) [fundacional].** *On the relevance of DTCs for obtaining insights into fleet-wide anomalies.* LOD 2020, Springer LNCS. DOI [10.1007/978-3-030-64583-0_37](https://link.springer.com/chapter/10.1007/978-3-030-64583-0_37). Ponderación entrópica de DTCs en flota de camiones (no supervisado, temporal); demuestra que los DTC frecuentes "dejan de informar" y que los DTC solos no bastan para causa raíz. Cercanía: **Media** (munición empírica contra el diagnóstico DTC puro — L2/RQ1).

### 5.3 L4 — Detección no supervisada sobre telemetría vehicular real (N5–N8)

**N5. Cherdo, Miramond, Pegatoquet & Vallauri (2023).** *Unsupervised Anomaly Detection for Cars CAN Sensors Time Series Using Small Recurrent and Convolutional Neural Networks.* Sensors 23(11):5013. DOI [10.3390/s23115013](https://doi.org/10.3390/s23115013). CAN real (Alpine/Renault, 4 meses, 17 GB, 486→85 señales a 1 Hz); predictores LSTM/GRU/CNN pequeños + anomaly likelihood; solo datos normales en entrenamiento. TPR 86 % con FPR 0,061 % (fallos de presión de aceite); −23 % parámetros y −60 % cómputo vs baseline. **El análogo más cercano a nuestro detector edge: no supervisado, temporal, vehicular, dimensionado para embebido — sin capa LLM/RAG/memoria.** Cercanía: **Alta**.

**N6. Abboush, Dzoupet Yimtchi, Tan, Ouarrad & Rausch (2026).** *Robust and Interpretable Anomaly Detection in Automotive Test Recordings Using Denoising Autoencoders with Adaptive Thresholding.* Electronics 15(12):2723. DOI [10.3390/electronics15122723](https://www.mdpi.com/2079-9292/15/12/2723). Registros reales de pruebas (IAV) + HiL; 531 mediciones (~29,5 GB), 12 señales; 4 DAE + umbral gaussiano adaptativo + XAI (ARCANA, permutación). F1 93,9 % (real). Valida el pipeline "AE no supervisado + umbral adaptativo + explicación localizada" que nuestro agente consumiría como evidencia. Cercanía: **Alta**.

**N7. Geglio, Hedayati, Tascillo, Anderson, Barker & Havens (2022).** *Deep Convolutional Autoencoder for Assessment of Drive-Cycle Anomalies in Connected Vehicle Sensor Data.* IEEE SSCI 2022:743–749. DOI [10.1109/SSCI51031.2022.10022233](https://ieeexplore.ieee.org/document/10022233/) · [arXiv:2202.07592](https://arxiv.org/abs/2202.07592). AE convolucional sobre 57–58 señales de powertrain a 10 Hz (híbridos Ford; 271 ciclos sanos + 150 con fallo de batería envejecida); supera detectores PyOD. Un solo tipo de fallo evaluado. Cercanía: Media.

**N8. Hojjati, Roth, Woods, Sills & Armanfard (2026) [preprint].** *EngineAD: A Real-World Vehicle Engine Anomaly Detection Dataset.* [arXiv:2603.25955](https://arxiv.org/abs/2603.25955); dataset en [McGill Dataverse](https://borealisdata.ca/dataset.xhtml?persistentId=doi%3A10.5683%2FSP3%2FTX13P1). 25 vehículos comerciales, 6 meses, 13 sensores de motor vía CAN; benchmark de 9 métodos one-class (HBOS, COPOD, LOF, iForest, OC-SVM, K-Means, AE, Deep SVDD…). F1 0,21–0,93 **según vehículo**; métodos simples igualan o superan a los profundos. **Hallazgo doble para el TFM:** (a) primer dataset público con signos tempranos de fallo real de motor — matiza el hallazgo H-EA1 del barrido previo (sigue sin haber dataset con *fallos mecánicos etiquetados por clase*, pero ya existe uno con anomalías de motor anotadas por expertos; auditar licencia y contenido en Entrega 2); (b) la fuerte variabilidad inter-vehículo justifica empíricamente el perfil/memoria por vehículo de nuestra propuesta. Cercanía: **Alta**.

### 5.4 L3/L5 — ML supervisado, PdM y RUL (N9–N12)

**N9. Tuleski, Yamaguchi, Stefenon, Coelho & Mariani (2024).** *Audio-Based Engine Fault Diagnosis with Wavelet, Markov Blanket, ROCKET…* Sensors 24(22):7316. DOI [10.3390/s24227316](https://doi.org/10.3390/s24227316). Diagnóstico acústico de motor diésel (3 clases conocidas), supervisado. Relevante como posible sensor externo adicional; sin capacidad ante fallos no vistos. Cercanía: Baja–Media.

**N10. (Cruce con L6) Khemani & Qureshi (2026)** — ver N14.

**N11. Kharazian, Lindgren, Magnússon, Steinert & Andersson Reyna (2025).** *SCANIA Component X: a real-world multivariate time series dataset for predictive maintenance.* Scientific Data 12:493. DOI [10.1038/s41597-025-04802-6](https://www.nature.com/articles/s41597-025-04802-6). >33.000 camiones, 1,12 M observaciones de entrenamiento, 14 features operacionales anonimizadas; habilita clasificación, supervivencia, anomalías y RUL. Desbalanceo fuerte (21.278 sanos / 2.272 fallos). Recurso de referencia a escala de flota (variables anonimizadas → no sustituye a nuestro banco OBD-II). Cercanía: Media.

**N12. Han, Li, Zheng, Lei & Li (2023).** *RUL Prediction of Lithium-Ion Batteries by Using a Denoising Transformer-Based Neural Network.* Energies 16(17):6328. DOI [10.3390/en16176328](https://www.mdpi.com/1996-1073/16/17/6328). DTNN sobre dataset NASA (4 celdas): R² 0,991, error RUL 3,2 ciclos; supera RF/LSTM/GRU. Pilar RUL; laboratorio, sin flota ni edge. Cercanía: Media.

### 5.5 L6 — Fusión multisensor y contexto (N13–N15)

**N13. Campos-Ferreira et al. (2023).** *Vehicle and Driver Monitoring System Using On-Board and Remote Sensors.* Sensors 23(2):814. DOI [10.3390/s23020814](https://www.mdpi.com/1424-8220/23/2/814). Fusión OBD-II (ELM327) + smartphone (IMU/GPS) + biométrica; 44 viajes, 38→26 variables (PCA); modelos físicos + reglas; 84–89 % exactitud (consumo/emisiones/estilo). Viabilidad de fusión low-cost análoga a RPi. Cercanía: Media.

**N14. Khemani & Qureshi (2026).** *AI-driven predictive maintenance for connected vehicles using environmental context integration…* Discover Vehicles. DOI [10.1007/s44465-026-00023-2](https://link.springer.com/article/10.1007/s44465-026-00023-2). OBD-II + IMU/CAN 50 Hz + APIs ambientales (clima, IRI, tráfico); LightGBM+SHAP; sintético físico-informado (2.000 obs.) + AI4I + piloto real (5 vehículos, 3 países, 992 viajes). Macro-F1 0,855; **ablación: sin rasgos ambientales el macro-F1 cae 2,6 puntos → evidencia cuantitativa de que el contexto reduce falsas anomalías** (RQ4). Edge real: TFLite INT8, inferencia <1 s vs ~3,5 s nube. Supervisado, sin LLM/memoria. Cercanía: **Alta**.

**N15. Giannoulidis & Gounaris (2023).** *A context-aware unsupervised predictive maintenance solution for fleet management.* J. Intelligent Information Systems 60(2). DOI [10.1007/s10844-022-00744-2](https://link.springer.com/article/10.1007/s10844-022-00744-2). Anomalías en streaming **no supervisadas** conscientes de contexto vía "peer groups" de vehículos; evaluación por coste. El contexto resulta "crucial" en entornos volátiles. En despliegue mono-vehículo no hay pares → **motiva nuestra memoria evolutiva como sustituto del contexto de flota**. Cercanía: **Alta**.

*Anotado no verificable (E7):* "Intelligent multi-sensor fusion and anomaly detection in vehicles via deep learning" (Internet of Things, Elsevier, PII S2542660525000745) — recuperar manualmente.

### 5.6 L7 — XAI en diagnóstico (N16–N17)

**N16. Brusa, Cibrario, Delprete & Di Maggio (2023).** *Explainable AI for Machine Fault Diagnosis…* Applied Sciences 13(4):2038. DOI [10.3390/app13042038](https://www.mdpi.com/2076-3417/13/4/2038). SHAP para selección de rasgos en fallos de rodamientos (SVM/kNN, >98,5 %). Tipo de explicación: **(a) decisión del modelo**. Cercanía: Baja.

**N17. Haque, Zabin & Uddin (2025).** *EnsembleXAI-Motor: A Lightweight Framework for Fault Classification in EV Drive Motors…* Machines 13(4):314. DOI [10.3390/machines13040314](https://www.mdpi.com/2075-1702/13/4/314). Ensembles + LIME, 94,5 % acc., framework "ligero" (apoya viabilidad XAI en edge). Tipo **(a)**. Cercanía: Media.

**Patrón de L7 (respuesta preliminar a RQ5):** la literatura XAI automotriz explica mayoritariamente la *decisión del modelo* (SHAP/LIME: N14, N16, N17, A7); la explicación de la *causa mecánica* solo aparece cuando interviene conocimiento estructurado + LLM (Lin & Miao — A-LLM2), y nunca acoplada a detección no supervisada sobre telemetría en vivo. Este es exactamente el eslabón que nuestro agente pretende cubrir.

### 5.7 L8 — LLMs en mantenimiento y diagnóstico (N18–N19)

**N18. Qaid, Zhang, Li, Ng & Li (2024) [preprint].** *FD-LLM: Large Language Model for Fault Diagnosis of Machines.* [arXiv:2412.01218](https://arxiv.org/abs/2412.01218). Serializa señales de vibración (FFT cuantizada o 15 rasgos estadísticos) como texto; Llama3-8B/Qwen1.5-7B/Mistral-7B con LoRA; CWRU (9.200 muestras). Llama3-Instruct 99,8 % acc.; transferencia entre cargas 96,5 %; mala generalización entre componentes. **Demuestra que un LLM puede consumir telemetría serializada, pero con fine-tuning y solo clases conocidas → justifica nuestra separación detección-no-supervisada / razonamiento-LLM (ADR-0009).** Cercanía: Media.

**N19. Liu et al. (2025).** *LLMAD: Large Language Models can Deliver Accurate and Interpretable Time Series Anomaly Detection.* KDD '25. DOI [10.1145/3711896.3737239](https://dl.acm.org/doi/10.1145/3711896.3737239) · [arXiv:2405.15370](https://arxiv.org/abs/2405.15370). TSAD con LLM sin entrenamiento: recuperación de segmentos similares como few-shot dinámico + cadena de razonamiento "AnoCoT"; rendimiento comparable a DL con explicación interpretable. **Avala el patrón detección→explicación LLM con ejemplos recuperados (≈ memoria de casos).** Cercanía: Media–Alta.

### 5.8 L9 — RAG en mantenimiento/diagnóstico técnico (N20–N21)

**N20. Nam, Choi, Choi & Kwon (2025).** *LoRA-Tuned Multimodal RAG System for Technical Manual QA: A Case Study on Hyundai Staria.* Applied Sciences 15(15):8387. DOI [10.3390/app15158387](https://www.mdpi.com/2076-3417/15/15/8387). RAG multimodal sobre manual de taller real (522 págs.); LLM 8B + LoRA + bge-m3; 5.065 pares QA; precisión procedimental 89,7 %. **El caso más próximo a "RAG + manual de fabricante"; modelo 8B compatible con filosofía edge, aunque no despliega en edge. RAG solo recupera, no descubre.** Cercanía: **Alta**.

**N21. Rony et al. (2023).** *CarExpert: Leveraging LLMs for In-Car Conversational Question Answering.* EMNLP 2023 Industry (BMW/Fraunhofer). DOI [10.18653/v1/2023.emnlp-industry.56](https://aclanthology.org/2023.emnlp-industry.56/). RAG embarcado sobre documentación del vehículo con control de entrada y moderación de salida (guardrails). Patrón industrial reutilizable como nodo de verificación de nuestro agente. Cercanía: **Alta**.

### 5.9 L10 — Sistemas agénticos aplicados (N22–N25)

**N22. Lee, Vidyaratne, Farahat & Gupta (2025).** *Exploring LLM-based Agentic Frameworks for Fault Diagnosis.* PHM Society Conf. 17(1). DOI [10.36001/phmconf.2025.v17i1.4350](https://papers.phmsociety.org/index.php/phmconf/article/view/4350). Compara configuraciones de agentes centralizadas vs distribuidas para monitorización de salud con herramientas computacionales, aprendizaje continuo y calibración de confianza (simulación). **Plantea exactamente nuestra pregunta de diseño arquitectónico; exploratorio, sin telemetría vehicular real.** Cercanía: **Alta**.

**N23. Park, Cho, Chae, Durgunlu & Um (2025).** *LLM-based multi-agent system for autonomous maintenance process of machine tools.* PHM Asia-Pacific 5(1). DOI [10.36001/phmap.2025.v5i1.4480](https://papers.phmsociety.org/index.php/phmap/article/view/4480). 4 agentes con roles (Chatbot / Solution_finder / Actor / Supervisor) sobre alarmas CNC y manuales, con **LLM local**. Paralelo estructural casi exacto de nuestro grafo (código de error → recuperación → acción → supervisión); sin detección no supervisada ni memoria persistente. Cercanía: **Alta**.

**N24. Harbola & Purwar (2025) [preprint].** *PARAM: Prescriptive Agents based on RAG for Automated Maintenance.* [arXiv:2508.04714](https://arxiv.org/abs/2508.04714). Pipeline completo señal→detección→RAG documental→prescripción en rodamientos; Gemini/Llama-3.1 (4B–253B); híbrido "modelo pequeño local + modelo capaz" (Flash 4,5/5 en 2,4 s vs 253B 5/5 en 83 s). **El pipeline íntegro del TFM en otro dominio; su hallazgo del híbrido small/large informa nuestra frontera edge–cloud.** Cercanía: **Alta**.

**N25. Di Maggio (2025).** *Toward Autonomous LLM-Based AI Agents for Predictive Maintenance: State of the Art, Challenges, and Future Perspectives.* Applied Sciences 15(21):11515. DOI [10.3390/app152111515](https://www.mdpi.com/2076-3417/15/21/11515). Revisión que unifica agentes LLM para PdM (taxonomía soft/hard agents, memoria, guardrails, MCP); constata literatura fragmentada, poca evidencia operacional y ausencia de benchmarks. **Marco para posicionar nuestro agente y citar el hueco desde una revisión de 2025.** Cercanía: Media–Alta.

### 5.10 L12 — Continual / online learning (N26–N29)

**N26. Hurtado, Salvati, Semola, Bosio & Lomonaco (2023).** *Continual learning for predictive maintenance: Overview and challenges.* Intelligent Systems with Applications 19:200251. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2667305323000765) · [arXiv:2301.12467](https://arxiv.org/abs/2301.12467). Survey CL↔PdM: regímenes de datos, tipos de drift, taxonomía (regularización/arquitectura/replay); señala la adaptación en edge como reto abierto. **Fundamento directo de la actualización incremental por vehículo de nuestra memoria evolutiva.** Cercanía: **Alta**.

**N27. Yang & Shami (2021).** *A Lightweight Concept Drift Detection and Adaptation Framework for IoT Data Streams.* IEEE IoT Magazine 4(2). DOI [10.1109/IOTM.0001.2100012](https://ieeexplore.ieee.org/document/9427288) · [arXiv:2104.10529](https://arxiv.org/abs/2104.10529). OASW (ventana adaptativa tipo ADWIN) + LightGBM; reentrenamiento selectivo solo ante drift. Patrón arquitectónico directo para actualizar el detector en RPi sin coste continuo. Cercanía: **Alta**.

**N28. Montiel et al. (2021).** *River: machine learning for streaming data in Python.* JMLR 22(110):1–8. [JMLR](https://www.jmlr.org/papers/v22/20-1380.html). Librería de referencia de ML incremental: ADWIN/DDM/KSWIN, Half-Space Trees (anomalía online no supervisada), métricas prequential. Herramienta de implementación candidata para el edge. Cercanía: **Alta** (instrumental).

**N29. Wang, Zhang, Su & Zhu (2024).** *A Comprehensive Survey of Continual Learning: Theory, Method and Application.* IEEE TPAMI 46(8). DOI [10.1109/TPAMI.2024.3367329](https://dl.acm.org/doi/10.1109/TPAMI.2024.3367329) · [arXiv:2302.00487](https://arxiv.org/abs/2302.00487). Survey canónico (estabilidad–plasticidad, task/domain/class-incremental, online CL). Vocabulario formal: la adaptación por vehículo ≈ escenario *domain-incremental*. Cercanía: Media (fundamento).

### 5.11 L13 — Edge AI y Edge–Cloud (N30–N32)

**N30. Bala et al. (2024).** *Artificial intelligence and edge computing for machine maintenance — review.* Artificial Intelligence Review. DOI [10.1007/s10462-024-10748-9](https://link.springer.com/article/10.1007/s10462-024-10748-9). Revisión sistemática AI+edge en PHM: patrón dominante = preprocesado e inferencia en edge (RPi/Jetson), entrenamiento en cloud; latencia ↓ hasta 37× y ancho de banda ↓ 43× vs cloud centralizado; carencias: sistemas end-to-end reales y análisis coste-beneficio. **Valida nuestra partición edge/cloud y nombra el hueco "end-to-end" que ocupamos.** Cercanía: **Alta**.

**N31. Jain, Mondal, Das & Khandelwal (2025).** *Intelligent predictive maintenance: multivariate ML model optimization in an Edge-Fog-Cloud environment (FogBayes).* Computing (Springer). DOI [10.1007/s00607-025-01585-x](https://link.springer.com/article/10.1007/s00607-025-01585-x). Arquitectura edge-fog-cloud para PdM vehicular (IoV); ensembles supervisados; acc. 98,9 %. Sin detección de desconocidos ni capa cognitiva. Cercanía: Media.

**N32. Baller, Jindal, Chadha & Gerndt (2021).** *DeepEdgeBench: Benchmarking DNNs on Edge Devices.* IEEE IC2E 2021. [arXiv:2108.09457](https://arxiv.org/abs/2108.09457). Benchmark RPi 4 / Coral / Jetson Nano / Tinker / Arduino: cuantización INT8 → −27–40 % latencia con ~0,6 % de pérdida Top-1. Base cuantitativa para justificar RPi + cuantización (solo visión; nuestras series requieren medición propia — ya prevista en Fase 2). Cercanía: Media.

### 5.12 Candidatos anotados no verificables en esta iteración (E7 — recuperar con acceso institucional)

1. Rimpas et al. (2020), *OBD-II sensor diagnostics…*, Energy Reports, DOI 10.1016/j.egyr.2019.10.018 (L1).
2. *Novel engine fault diagnosis framework… MiniRocket*, Expert Systems with Applications 2025, PII S0957417425022808 (L3).
3. *Toward interpretable anomaly detection for autonomous vehicles with denoising variational transformer*, Eng. Appl. of AI, DOI 10.1016/j.engappai.2023.107601 (L4/L7).
4. *Intelligent multi-sensor fusion and anomaly detection in vehicles via deep learning*, Internet of Things, PII S2542660525000745 (L6).

---

## 6. Matriz comparativa inicial

Valores: **Sí / Parcial / No**. "Detecta desconocidos" evaluado con el criterio estricto acordado: detectar outliers ≠ descubrir un fallo nuevo; se puntúa "Sí" solo si el protocolo evalúa explícitamente anomalías/clases no vistas en entrenamiento, y "Parcial" si el marco lo permite pero la validación usa fallos conocidos o etiquetas a posteriori. Se incluyen las filas nuevas (N) y las referencias previas imprescindibles para la comparación (A/B/C).

| Referencia | Año | Datos | Subsistema | Técnica | No sup. | Temporal | XAI | LLM | RAG | Agentes | Memoria | Edge | Detecta desconocidos | Cercanía |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Mahale et al. (A-LLM1) | 2025 | OBD-II + DTC + manuales | Motor | CTGAN+XGBoost+RAG+GPT-4o | Parcial | No | Parcial | Sí | Sí | No | No | No | No | **Alta** |
| Lin & Miao (A-LLM2) | 2025 | Diálogos taller + KG | Multisistema | KG+RAG 3 niveles+LLM | No | No | Sí (causa mecánica) | Sí | Parcial | Parcial | Parcial | No | Parcial | **Alta** |
| Giannoulidis et al. EDBT (N-EDBT)¹ | 2024 | OBD-II flota (40 veh., 1,5 M reg.) | Motor/multi | Closest-Pair/LOF/TranAD | Sí | Sí | No | No | No | No | Parcial | No | Sí | **Alta** |
| Cherdo et al. (N5) | 2023 | CAN real | Motor (aceite) | LSTM/GRU/CNN + likelihood | Sí | Sí | No | No | No | No | No | Sí | Parcial | **Alta** |
| PARAM (N24) [preprint] | 2025 | Vibración + manuales | Rodamientos | Agentes+RAG+LLM | Parcial | Sí | Parcial | Sí | Sí | Sí | Parcial | No | Parcial | **Alta** |
| Park et al. (N23) | 2025 | Códigos error + manuales | CNC | Multiagente LLM local | No | No | Parcial | Sí | Sí | Sí | No | Parcial | No | **Alta** |
| Lee et al. (N22) | 2025 | Sensores simulados | Industrial | Agentes LLM + herramientas | Parcial | Sí | Sí | Sí | no consta | Sí | Parcial | No | Parcial | **Alta** |
| Nam et al. (N20) | 2025 | Manual taller (texto+imagen) | Vehículo completo | RAG multimodal + LoRA 8B | No | No | Parcial | Sí | Sí | No | Parcial | No | No | **Alta** |
| CarExpert (N21) | 2023 | Doc. vehículo BMW | Vehículo completo | RAG + guardrails | No | No | Parcial | Sí | Sí | Parcial | No | Parcial | No | **Alta** |
| Khemani & Qureshi (N14) | 2026 | OBD-II+IMU+APIs ambiente | Frenos/aceite/motor | LightGBM+SHAP | No | Sí | Sí (decisión) | No | No | No | No | Sí | No | **Alta** |
| Giannoulidis & Gounaris (N15) | 2023 | Flota + C-MAPSS | Neumática/motor | Streaming context-aware | Sí | Sí | No | No | No | No | Parcial | No | Sí | **Alta** |
| Abboush et al. (N6) | 2026 | Test real + HiL | Eléctrico/ECU | DAE + umbral adaptativo | Sí | Sí | Sí | No | No | No | No | No | Parcial | **Alta** |
| EngineAD (N8) [preprint] | 2026 | CAN flota real | Motor | 9 métodos one-class | Sí | Sí | No | No | No | No | No | No | Parcial | **Alta** |
| Hurtado et al. (N26) | 2023 | Telemetría condición | Genérico | Survey CL+PdM | Parcial | Sí | No | No | No | No | Sí | Parcial | Parcial | **Alta** |
| Yang & Shami (N27) | 2021 | Streams IoT | IoT | OASW+LightGBM | No | Sí | No | No | No | No | Parcial | Parcial | Parcial | **Alta** |
| Bala et al. (N30) | 2024 | Condición máquinas | Genérico | Review edge-AI PHM | Parcial | Sí | No | No | No | No | No | Sí | Parcial | **Alta** |
| FD-LLM (N18) [preprint] | 2024 | Vibración (CWRU) | Rodamientos | LLM+LoRA clasif. | No | Sí | Parcial | Sí | No | No | No | No | No | Media |
| LLMAD (N19) | 2025 | Series públicas | Genérico | LLM ICL + AnoCoT | Parcial | Sí | Sí | Sí | Parcial | No | Parcial | No | Parcial | Media–Alta |
| Di Maggio (N25) | 2025 | — (revisión) | PdM industrial | Review agentes LLM | — | — | Parcial | Sí | Sí | Sí | Sí | Parcial | No | Media–Alta |
| Idiri et al. (A6) | 2025 | OBD-II + simulación (RPi) | Escape/motor | LSTM/GRU | No | Sí | No | No | No | No | No | Sí | No | Media |
| Lu et al. (A7) | 2025 | CAN + DTC (20 veh.) | Multisistema | CNN-LSTM-Transformer+XAI | No | Sí | Sí | No | No | No | No | Parcial | Parcial | Media |
| Lundgren & Jung (C19) | 2022 | Motor real (Volvo) | Admisión/sensores | Open-set one-class | Sí | Sí | No | No | No | No | No | No | Sí | **Alta** |
| Geglio et al. (N7) | 2022 | Telemetría Ford | Powertrain HEV | Conv-AE | Sí | Sí | No | No | No | No | No | No | Parcial | Media |
| SCANIA X (N11) | 2025 | Telemetría flota | Comp. motor | Dataset multi-técnica | Ambos | Sí | No | No | No | No | No | No | Parcial | Media |
| Jain et al. (N31) | 2025 | Sensores vehículo | Fallos genéricos | Ensembles edge-fog-cloud | No | Parcial | No | No | No | No | No | Sí | No | Media |
| Campos-Ferreira (N13) | 2023 | OBD-II+IMU+bio | Vehículo/conductor | Físico+reglas+PCA | Parcial | Sí | Parcial | No | No | No | No | Parcial | No | Media |
| Haque et al. (N17) | 2025 | Simulación+real | Motor eléctrico | Ensembles+LIME | No | No | Sí (decisión) | No | No | No | No | Parcial | No | Media |
| Ferreira et al. (N4) | 2020 | DTC flota | Multisistema | Ponderación entrópica | Sí | Sí | Parcial | No | No | No | No | No | Parcial | Media |
| Ramai et al. (N2) | 2022 | PID propietario/CAN | Batería BEV | Logging RPi | No | Sí | No | No | No | No | No | Sí | No | Media |
| **TFM (propuesta)** | 2026 | OBD-II streaming (emulado, ELM327) | Multisistema | Detector one-class + agente LLM (LangGraph) | Sí (implementado) | Sí (implementado) | **Objetivo** (causa, vía RAG+verificación) | Propuesto (SLM edge) | Propuesto | Propuesto | **Por validar** (evolutiva, estados de evidencia) | Sí (RPi emulada; HW real por validar) | **Por validar** (protocolo held-out/open-set) | — |

*Nota sobre la fila TFM: se distingue entre capacidades ya implementadas y validadas en el prototipo a la fecha (detección no supervisada temporal sobre streaming emulado, pipeline edge), capacidades propuestas (agente, RAG, SLM edge) y capacidades objetivo cuya demostración constituye precisamente las hipótesis experimentales del TFM (explicación causal, memoria evolutiva, detección de desconocidos). Ninguna capacidad no demostrada experimentalmente se registra como "Sí".*

¹ Giannoulidis, Gounaris et al. (2024), *Exploring unsupervised anomaly detection for vehicle predictive maintenance with partial information*, EDBT 2024, DOI [10.48786/edbt.2024.65](https://openproceedings.org/2024/conf/edbt/paper-200.pdf): 40 vehículos, 1 año, 1,5 M registros OBD-II a 1/min; F₀.₅ 0,68; hallazgo colateral valioso: hubo fallos reales **sin DTC** — evidencia directa de la insuficiencia del DTC (RQ1). Se incorpora al corpus con ficha completa en Entrega 2.

**Lectura vertical de la matriz (núcleo del argumento de vacío):** ninguna fila tiene "Sí/Parcial" simultáneamente en las columnas {No supervisado, LLM, RAG, Agentes, Memoria, Edge}. Los trabajos con capa cognitiva (LLM/RAG/agentes) carecen de detección no supervisada sobre telemetría en vivo y de edge; los trabajos no supervisados con telemetría real carecen de capa cognitiva y de memoria; los trabajos edge carecen de ambas.

---

## 7. Los cinco trabajos más cercanos

**1. Mahale, Kolhar & More (2025) — Discover Computing** ([10.1007/s10791-025-09823-8](https://link.springer.com/article/10.1007/s10791-025-09823-8)). Único trabajo peer-reviewed con la cadena OBD-II→ML→RAG→LLM completa. Diferencias medibles frente a nuestro TFM: clasificación **supervisada** de DTCs (no anomalías no vistas); datos tabulares estáticos (no streaming); GPT-4o en nube (no SLM edge); sin memoria; su propia evaluación reporta exactitud factual baja pese a alta fluidez — el problema que nuestro nodo de verificación + memoria de casos ataca.

**2. Lin & Miao (2025) — Electronics** ([10.3390/electronics14214180](https://www.mdpi.com/2079-9292/14/21/4180)). La capa cognitiva más sofisticada del área (KG + RAG 3 niveles + consulta proactiva de información faltante; 77,3 % en 91 fallos; explicación de causa mecánica). Carece por completo de telemetría en vivo: parte de síntomas/diálogos. Complementario exacto de nuestro flujo ascendente señal→anomalía→hipótesis.

**3. PARAM — Harbola & Purwar (2025) [preprint]** ([arXiv:2508.04714](https://arxiv.org/abs/2508.04714)). Estructuralmente el más parecido al pipeline completo (detección→conocimiento→prescripción con agentes y RAG), en rodamientos industriales. Diferencias: dominio no vehicular; sin edge (Gemini en nube); detección basada en clasificación LLM (no one-class); memoria solo como casos históricos recuperables, sin ciclo de validación de hipótesis. Al ser preprint, se cita como indicador de tendencia, no como evidencia consolidada.

**4. Giannoulidis et al. (2024) — EDBT** ([10.48786/edbt.2024.65](https://openproceedings.org/2024/conf/edbt/paper-200.pdf)). La detección no supervisada sobre OBD-II real más sólida y honesta del corpus (flota real, etiquetas parciales, F₀.₅ 0,68, DTCs poco fiables). Sin explicación, sin capa cognitiva, sin edge, procesamiento centralizado. Es nuestro "suelo empírico": lo que un detector realista consigue solo.

**5. Cherdo et al. (2023) — Sensors** ([10.3390/s23115013](https://doi.org/10.3390/s23115013)). El detector no supervisado vehicular más próximo a nuestras restricciones edge (modelos pequeños, CAN real, colaboración Renault). Sin LLM, sin RAG, sin memoria; un solo tipo de fallo validado.

**Síntesis:** los cinco cubren, por pares disjuntos, todos los componentes de nuestra propuesta; ninguno cubre la integración ni el mecanismo de memoria con estados de evidencia (OBSERVACIÓN→…→CONOCIMIENTO). Los candidatos 6–10 para la Entrega 3: Park et al. (N23), Lee et al. (N22), Nam et al. (N20), Khemani & Qureshi (N14), Lundgren & Jung (C19).

---

## 8. Vacíos preliminares y respuesta preliminar a RQ14/RQ15

**Formulación defendible (no absoluta):** *en la literatura analizada hasta la fecha (≈71 referencias verificadas, ventana 2021–2026 con fundacionales) no se identificó ninguna propuesta que integre simultáneamente telemetría OBD-II en streaming, detección no supervisada en el dispositivo edge, razonamiento con SLM/LLM asistido por RAG sobre documentación técnica, arquitectura agéntica con verificación, y una memoria longitudinal por vehículo con ciclo explícito de confirmación/descarte de hipótesis.*

Vacíos concretos, cada uno anclado en evidencia:

- **V1 (integración):** los sistemas con capa cognitiva (Mahale; Lin & Miao; PARAM; Park; CarExpert; Nam) no consumen telemetría en vivo o no la procesan de forma no supervisada; los detectores no supervisados vehiculares (Giannoulidis ×2; Cherdo; Abboush; Geglio; EngineAD; Lundgren & Jung) no explican causa mecánica ni aprenden de casos. Confirma y amplía H-EA2.
- **V2 (memoria evolutiva con control de errores):** la literatura de memoria de agentes (C6–C9) no incluye mecanismos de validación de hipótesis antes de consolidar conocimiento; en el dominio PdM, la memoria aparece solo como casos recuperables (PARAM) o caché (Nam). Ningún trabajo modela estados de evidencia (anomalía→patrón candidato→hipótesis→validación→conocimiento/descartada). La prevención de propagación de errores del LLM a la memoria (nuestro requisito) no está resuelta: Mahale documenta precisamente la baja exactitud factual que la haría peligrosa.
- **V3 (adaptación por vehículo):** EngineAD demuestra variabilidad inter-vehículo severa (F1 0,21–0,93); la línea CL (Hurtado; Yang & Shami; Wang) ofrece las herramientas (domain-incremental, drift detection) pero nadie las acopla a un perfil evolutivo por vehículo en edge. Responde RQ11/RQ13 preliminarmente.
- **V4 (explicación de causa vs decisión):** L7 explica decisiones de modelo (SHAP/LIME); solo KG+LLM explica causas, y sin señal en vivo. El eslabón anomalía-no-supervisada→explicación-causal-verificada está vacío (RQ5).
- **V5 (evaluación end-to-end en edge):** Bala et al. (2024) y Di Maggio (2025) — ambas revisiones recientes — señalan expresamente la ausencia de sistemas end-to-end evaluados y de benchmarks; nuestra evaluación extremo a extremo con banco de fallos reproducible ataca ese hueco.

**Tipos de novedad defendibles (respuesta preliminar a RQ15):** (a) novedad **en integración** (V1) — la más sólida; (b) novedad **en el mecanismo de aprendizaje/memoria** (V2) — la más distintiva, por el ciclo de estados de evidencia; (c) novedad **experimental** (V5 + banco de fallos reproducible + protocolo held-out/open-set sobre corpus RAG y memoria, alineado con C18–C20). No se reclamará novedad tecnológica de componentes individuales: cada componente por separado tiene antecedentes (secciones 5.3–5.11), y así se declarará.

**Matiz nuevo sobre H-EA1:** la aparición de EngineAD (2026, preprint + dataset público en McGill Dataverse) obliga a suavizar la afirmación "no existe dataset público con fallos mecánicos reales": sigue sin existir uno con *clases de fallo mecánico etiquetadas* sobre OBD-II, pero existe ya uno con *anomalías de motor reales anotadas por expertos* sobre CAN. Acción: auditar EngineAD en la Entrega 2 y actualizar docs/03 y docs/06 en consecuencia.

---

## 9. Estado respecto a las preguntas de revisión

| RQ | Estado | Respuesta preliminar |
|---|---|---|
| RQ1 | Parcial | PIDs estándar a ~1 Hz con ELM327 (N1); PIDs propietarios no transferibles (N2); DTCs insuficientes y a veces ausentes en fallos reales (N4, N-EDBT); transición normativa a OBDonUDS (J1979-2) |
| RQ2 | Parcial | Supervisado domina (XGBoost/ensembles/híbridos CNN-LSTM); métricas altas pero con sospecha de fuga y mala generalización (A8, A7) |
| RQ3 | Parcial | One-class/AE/streaming sobre telemetría real funcionan pero con F1 modestos y alta variabilidad (N-EDBT 0,68 F₀.₅; EngineAD 0,21–0,93) |
| RQ4 | Parcial | El contexto reduce falsas anomalías con evidencia cuantitativa (N14: −2,6 pts sin ambiente; N15: peer groups "cruciales") |
| RQ5 | Parcial | SHAP/LIME = decisión del modelo; causa mecánica solo vía KG+LLM sin señal (V4) |
| RQ6 | Parcial | LLMs consumen series serializadas con fine-tuning (N18) o ICL (N19); nadie sobre OBD-II streaming |
| RQ7 | Parcial | RAG sobre manuales automotrices funciona (N20, N21, A-LLM1); solo recupera, no descubre (única excepción parcial: N24) |
| RQ8 | Parcial | Agentes con roles en mantenimiento existen (N22–N24); ninguno vehicular con telemetría |
| RQ9–RQ10 | Pendiente E2 | Base: C6–C9 + V2 |
| RQ11 | Parcial | CL/drift maduro como herramienta (N26–N29); sin acople a vehículo individual |
| RQ12 | Parcial | Detección ligera viable en edge (N5, B-TinyML); SLM 1.5–3B viables en RPi 5 (B-SLM); agentes LLM locales incipientes (N23) |
| RQ13 | Parcial | Variabilidad inter-vehículo severa (N8); generalización pobre documentada (A7, síntesis A) |
| RQ14 | **Respondida provisionalmente: No** | Ver §8, formulación defendible |
| RQ15 | Preliminar | Integración + mecanismo de memoria + evaluación (§8) |

---

## 10. Plan para la Segunda Entrega

1. Ejecutar las cadenas de §2 en Scopus/WoS/IEEE con acceso institucional; registrar recuentos formales PRISMA por base de datos.
2. Recuperar y evaluar los 4 candidatos anotados (§5.12).
3. Auditar EngineAD (licencia, señales, protocolo) y decidir si entra como dataset de validación.
4. Completar fichas: Giannoulidis EDBT 2024, y profundizar L11 (memoria) y L2 (sistemas expertos 2021+ si existen).
5. Ampliar a 30–40 nuevas publicaciones con matriz completa, comparación temática, datasets y métricas agregadas (RQ9, RQ10).
6. Lectura completa de los 6–8 trabajos de mayor peso (ya previsto en el barrido de Fase 1).
