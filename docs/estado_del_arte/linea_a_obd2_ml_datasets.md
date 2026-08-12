# Línea A — Diagnóstico y mantenimiento predictivo con OBD-II/CAN (ML/DL) y datasets

> Fichas de trabajo del primer barrido (Fase 1, 2026-08-12). Referencias verificadas en el venue
> indicado en la fecha del barrido. Antes de citar en la memoria: releer el texto completo y
> normalizar al formato de cita de la plantilla UAX. Los intentos de acceso a IEEE Xplore y
> ScienceDirect fallaron por bloqueo (403); esos trabajos se verificaron por vías alternativas.

## Trabajos verificados

### A1. Michailidis, Panagiotopoulou & Papadakis (2025). *A Review of OBD-II-Based Machine Learning Applications for Sustainable, Efficient, Secure, and Safe Vehicle Driving*
- **Venue:** Sensors (MDPI) 25(13):4057. **DOI:** [10.3390/s25134057](https://www.mdpi.com/1424-8220/25/13/4057)
- Review transversal de aplicaciones ML sobre OBD-II: consumo, emisiones, perfilado de conductor, salud vehicular y detección de anomalías, ciberseguridad, asistencia a la conducción. Referencia panorámica principal (toma OBD-II como eje).
- **Limitaciones que declara:** surveys previos de aplicación única; retos en generalización, escalabilidad, eficiencia computacional, privacidad y regulación.

### A2. Mahale, Kolhar & More (2025). *A comprehensive review on artificial intelligence driven predictive maintenance in vehicles…*
- **Venue:** Discover Applied Sciences (Springer). **DOI:** [10.1007/s42452-025-06681-3](https://link.springer.com/article/10.1007/s42452-025-06681-3)
- Revisión sistemática (94 artículos): RUL, monitorización de salud, XAI (LIME/SHAP/Grad-CAM), LLMs para informes. Repasa datasets usados (Scania APS, C-MAPSS, rodamientos).
- **Limitaciones:** calidad/escasez de datos de fallo; proponen LLMs de dominio y federated learning como futuro → refuerza el hueco del TFM.

### A3. Hossain, Rahman & Ramasamy (2024). *Artificial Intelligence-Driven Vehicle Fault Diagnosis…: A Review*
- **Venue:** CMES 141(2):951–996. **DOI:** [10.32604/cmes.2024.056022](https://www.techscience.com/CMES/v141n2/58171/html)
- Diagnóstico multi-sistema (motor, suspensión, frenos…) con métodos por modelo/señal/conocimiento; compara DT, RF, SVM, KNN, K-Means, MLP, CNN, LSTM, autoencoders. Aboga por híbridos.
- **Limitaciones:** datasets reales etiquetados insuficientes, poca adaptabilidad entre condiciones, fallos concurrentes, y retos de privacidad/seguridad edge-cloud.

### A4. Prytz & Nowaczyk et al. (2015). *Predicting the need for vehicle compressor repairs using maintenance records and logged vehicle data*
- **Venue:** Engineering Applications of AI (Elsevier). **DOI:** [10.1016/j.engappai.2015.02.009](https://dl.acm.org/doi/abs/10.1016/j.engappai.2015.02.009)
- Seminal de PdM con datos reales de flota (camiones Volvo): registros de taller + datos agregados a bordo → predicción supervisada de reparación de compresor, con análisis coste-beneficio.
- **Limitaciones observadas:** datos agregados de baja frecuencia (no series OBD-II crudas), etiquetas ruidosas, datos propietarios. *Pendiente: confirmar lista completa de coautores al citar.*

### A5. Jun et al. (2025). *A Case Study on the DTC Prediction of Commercial Vehicles Using Machine Learning Approach*
- **Venue:** Int. J. of Automotive Technology (Springer). **DOI:** [10.1007/s12239-025-00223-x](https://link.springer.com/article/10.1007/s12239-025-00223-x)
- LightGBM para predecir proactivamente aparición de ciertos DTCs en flota comercial monitorizada.
- **Limitaciones observadas:** datos propietarios; predice DTCs concretos, no salud general.

### A6. Idiri et al. (2025). *Using Deep Learning for Predictive Maintenance: A Study on Exhaust Backpressure and Power Loss*
- **Venue:** Vehicles (MDPI) 7(4):134. **DOI:** [10.3390/vehicles7040134](https://www.mdpi.com/2624-8921/7/4/134)
- LSTM vs GRU (ventana 30) sobre 79.919 obs. / 23 parámetros, mezcla simulación + captura OBD-II con **Raspberry Pi**; gana GRU. Paralelismo directo con nuestro edge.
- **Limitaciones:** dependencia de datos sintéticos; sin validación de despliegue en vehículo real.

### A7. Lu et al. (2025). *Development and Validation of an Explainable Hybrid Deep Learning Model for Multiple-Fault Diagnosis…*
- **Venue:** Electronics (MDPI) 14(22):4488. **DOI:** [10.3390/electronics14224488](https://www.mdpi.com/2079-9292/14/22/4488)
- CNN–LSTM–Transformer con XAI (LIME/SHAP); 36.847 muestras (12 fallos) de simulación + 20 vehículos reales + CAN + DTCs. 96,8 % acc.; campo 91,6 %; latencia 72 ms GPU / 185 ms CPU.
- **Limitaciones:** desbalance en fallos raros, −3 % con fallos no vistos, generalización geográfica; +70 ms del Transformer en embebido → dato útil para nuestra frontera edge/cloud.

### A8. Kumar & Jain (2023). *Driving behavior analysis and classification by vehicle OBD data using machine learning*
- **Venue:** The Journal of Supercomputing. **DOI:** [10.1007/s11227-023-05364-3](https://link.springer.com/article/10.1007/s11227-023-05364-3)
- Clasifica 10 estilos de conducción con 50+ parámetros OBD-II (SVM/AdaBoost/RF, 99–100 %).
- **Limitaciones observadas:** accuracies ~100 % sugieren fuga de datos; sin detalles de dataset ni validación entre conductores. Usar con cautela, solo como referencia de "modelado de conducción".

## Datasets verificados

| Dataset | URL | Contenido | Frec. | Licencia | Veredicto |
|---|---|---|---|---|---|
| HCRL Driving Dataset | [ocslab.hksecurity.net](https://ocslab.hksecurity.net/Datasets/driving-dataset) | 51 señales OBD-II (Kia Soul, 10 conductores, ~23 h) | 1 Hz | Académica (citar Kwak, Woo & Kim, PST 2016) | ★ Mejor candidato para conducción normal real |
| HCRL Car-Hacking | [ocslab.hksecurity.net](https://ocslab.hksecurity.net/Datasets/car-hacking-dataset) | CAN crudo con ataques inyectados (DoS, fuzzy, spoofing) | tramas ms | Académica | Proxy de anomalías (ciberataque ≠ fallo mecánico) |
| X-CANIDS Dataset | [IEEE DataPort](https://ieee-dataport.org/open-access/x-canids-dataset-vehicle-signal-dataset) | CAN crudo + 688 señales decodificadas (Hyundai Sonata) + intrusiones | crudo | Open Access (cuenta IEEE) | ★ Volumen y señales decodificadas; anomalías = ataques |
| UAH-DriveSet | [robesafe.uah.es](http://www.robesafe.uah.es/personal/eduardo.romera/uah-driveset/) | Smartphone (IMU+GPS+vídeo); **sin OBD-II** | — | No comercial | Solo estilos de conducción; NO sirve como OBD |
| AEGIS (Zenodo) | [zenodo.org/records/820576](https://zenodo.org/records/820576) | OBD-II/CAN + GPS + IMU; 35 trayectos, 1 vehículo | — | **CC BY 4.0** | Única licencia abierta clara; volumen limitado |
| ReCAN (Mendeley) | [data.mendeley.com](https://data.mendeley.com/datasets/76knkx3fzv/2) | CAN crudo + decodificado, 3 coches + 4 camiones | crudo | no visible | Complementario multi-vehículo |
| Kaggle (varios: obdii-ds3, obd2data, engine health) | ver barrido | columnas/licencia no verificables sin sesión | — | ? | Auditar con sesión antes de comprometer |

**Hallazgo clave del barrido:** *no existe ningún dataset público verificado con fallos mecánicos reales etiquetados sobre series OBD-II.* Los datasets con anomalías son de ciberataques inyectados. Consecuencias para el TFM: (1) la inyección sintética de fallos no es un atajo sino la práctica del área; (2) nuestro banco de fallos reproducible (contribución C4) cubre una carencia real; (3) la validación externa usará conducción normal real (HCRL Driving / X-CANIDS / AEGIS) para el modelado de normalidad, declarando que los fallos son sintéticos.

## Trabajos LLM + OBD-II (hueco de investigación)

1. **Mahale, Kolhar & More (2025).** *Automated vehicle fault diagnosis and report generation using hybrid machine learning with multi-step RAG approach.* Discover Computing. **DOI:** [10.1007/s10791-025-09823-8](https://link.springer.com/article/10.1007/s10791-025-09823-8). El más cercano al TFM: OBD-II (9.154 registros) + CTGAN + XGBoost para DTCs + RAG multi-paso (FAISS) sobre DTCs y manuales + GPT-4o + LLM-as-judge. Resultado clave: fluidez ~98 % pero **exactitud factual notablemente menor** → la alucinación en dominio técnico es el problema abierto. Sin edge, sin streaming, sin memoria de casos.
2. **Lin & Miao (2025).** *An Automotive Fault Diagnosis Framework Based on Knowledge Graphs and Large Language Models.* Electronics 14(21):4180. **DOI:** [10.3390/electronics14214180](https://www.mdpi.com/2079-9292/14/21/4180). KG de ~130k diálogos de taller + RAG de 3 niveles; 77,3 % en 91 tipos de fallo. **No usa telemetría OBD-II en vivo.**
3. Antecedente NLP pre-LLM: [arXiv 2111.14977](https://arxiv.org/abs/2111.14977) (informes de texto libre, no telemetría).
4. Ecosistema open-source sin evaluación rigurosa (indicador de tendencia, no citable como literatura): open-mechanic, Automotive-Fault-Diagnosis-Agent (LangGraph+RAG).

**Veredicto:** ningún trabajo peer-reviewed integra agente LLM + telemetría OBD-II en streaming + arquitectura edge + memoria de casos con evaluación extremo a extremo. El hueco declarado en `docs/01` §1.2 queda confirmado y es citable.

## Síntesis: limitaciones comunes del área

(1) escasez estructural de datos de fallo etiquetados → simulación/GAN/datos propietarios; (2) irreproducibilidad (nadie publica datos); (3) generalización pobre entre vehículos/condiciones (y métricas infladas con probable fuga de datos); (4) coste/latencia poco evaluados en embebido; (5) en la vertiente LLM, alucinación factual y falta de anclaje en telemetría. El TFM ataca (1)+(2) con el banco reproducible, (4) con la evaluación edge y (5) con RAG + nodo de verificación + memoria.
