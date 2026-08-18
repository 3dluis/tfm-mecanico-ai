# Estado del Arte y Metodología de Investigación

> **NOTA DE VIGENCIA (alineación v3, 2026-08-18).** Este documento (12-ago) usa la PI v2 y
> la estructura V1–V7. La versión consolidada v2.0 para el tutor se reestructura alrededor
> de la **PI v3**, el vacío central **V\*** con dimensiones S1–S6 y la cadena
> epistemológica de ocho pasos — fuente canónica:
> [`docs/alineacion_v3/01_nucleo_cientifico.md`](../alineacion_v3/01_nucleo_cientifico.md).
> Se conserva sin reescribir como documento fechado; las citas de PI/vacíos se leen a
> través de `docs/correspondencia_nomenclatura.md` §0 y §5.


**Trabajo Fin de Máster — Máster Universitario en Inteligencia Artificial**
**Universidad Alfonso X el Sabio (UAX)**

**Título de trabajo:** Diseño e implementación de un sistema inteligente híbrido Edge–Cloud para diagnóstico y mantenimiento predictivo de vehículos con OBD-II y Raspberry Pi
**Autor:** Luis Daniel Díaz
**Documento:** consolidado para revisión del tutor · versión 1.0 · 12 de agosto de 2026
**Base documental:** capítulo 2 del Estado del Arte (Entrega 4), entregas 1–3 de la revisión sistemática, auditoría de alineación científica, clasificación de afirmaciones de novedad y documentación experimental del prototipo (fases F0–F8).

---

## Resumen ejecutivo

**Qué investigamos.** Este trabajo estudia una pregunta que es fácil de enunciar y difícil de responder con honestidad: ¿puede un sistema inteligente híbrido descubrir y explicar patrones de fallo vehicular previamente no documentados mediante el análisis contextual y longitudinal de datos OBD-II? La dificultad no está en detectar desviaciones — cualquier detector estadístico las produce en abundancia — sino en la distancia que separa una desviación observada de un conocimiento diagnóstico: no toda anomalía es una avería, y una máquina puede señalar algo que nunca había visto sin saber todavía qué significa. La cadena que operacionaliza la pregunta (telemetría → evento operativo → anomalía contextual → patrón candidato → hipótesis diagnóstica → verificación → conocimiento) convierte esa distancia en objeto experimental.

**Qué ha encontrado la literatura.** La revisión sistemática realizada (≈153 referencias verificadas en fuente primaria, con búsqueda adversarial dirigida a refutar cada afirmación de novedad) muestra un área con piezas maduras y conjunciones ausentes: la detección no supervisada vehicular es viable pero modesta y muy sensible al vehículo y al régimen de conducción; el condicionamiento contextual multiplica la detectabilidad de anomalías contextuales; el RAG sobre documentación automotriz es práctica industrial, pero la recuperación no garantiza exactitud factual; los sistemas multiagente con LLM presentan evidencia contradictoria — ablaciones muy favorables y taxonomías de fallo igualmente sólidas —; y la memoria de agentes consolida experiencia sin validar su veracidad, con vulnerabilidades de envenenamiento documentadas.

**Cuál es el vacío.** En la literatura analizada no se identificó ninguna propuesta que integre, en un único sistema evaluado end-to-end: telemetría OBD-II en streaming; segmentación en eventos operativos con normalidad por tipo de evento y baseline por vehículo; detección no supervisada contextual en el dispositivo edge; razonamiento multiagente con LLM, RAG, hipótesis y verificación bajo restricciones edge; y memoria longitudinal con ciclo de estados de evidencia en la que solo se consolida conocimiento validado (vacíos V1–V7, con V7 como vacío central).

**Qué proponemos.** Un artefacto: el sistema híbrido Edge–Cloud que instancia la cadena completa, con cinco contribuciones diferenciadas por naturaleza y nivel de riesgo (C-MEM, candidata a científica; C-EVT, metodológica y experimental; C-INT, arquitectónica; C-EXP, metodológica; C-PERS, experimental).

**Con qué metodología.** Design Science Research (DSR) como metodología general — el conocimiento se genera construyendo y evaluando el artefacto —, con la revisión sistemática inspirada en PRISMA como método de la fase de conocimiento y un diseño experimental predominantemente cuantitativo como método de validación.

**Cómo lo demostraremos o refutaremos.** Mediante seis familias de hipótesis falsables: H-MAIN (contraste directo de la pregunta, mediante protocolo held-out/open-set con retirada simultánea del conocimiento del detector, del corpus RAG y de la memoria) y cinco parciales (H-EVT, H-MEM, H-MAS, H-PERS, H-EXP) cuya eventual refutación individual no invalida la pregunta, sino que precisa qué mecanismo aporta y cuál no. Los umbrales confirmatorios se congelan por pre-registro antes de ejecutar los experimentos confirmatorios; el piloto exploratorio ya ejecutado (EXP-ANOM-002) se declara como tal y no se convertirá retrospectivamente en evidencia confirmatoria. La viabilidad edge (antigua H4) actúa como criterio transversal de aceptación, no como hipótesis.

---

## Índice

**Parte I — Estado del Arte**
1. Introducción y propósito · 2. Metodología de revisión bibliográfica · 3. Diagnóstico vehicular y OBD-II · 4. Inteligencia artificial y mantenimiento predictivo · 5. Eventos y contexto operacional · 6. Personalización longitudinal · 7. Explicabilidad y diagnóstico causal · 8. Modelos de lenguaje y RAG · 9. Sistemas agénticos y multiagente · 10. Memoria de agentes y consolidación validada · 11. Edge AI y arquitecturas Edge–Cloud · 12. Antecedentes más próximos · 13. Contradicciones de la literatura · 14. Vacíos de investigación V1–V7 · 15. Posicionamiento del TFM · 16. Síntesis

**Parte II — Metodología de Investigación**
1. Enfoque metodológico · 2. Justificación de Design Science Research · 3. Aplicación de DSR al TFM · 4. Pregunta y objetivos · 5. Hipótesis · 6. Diseño experimental · 7. Variables e instrumentos · 8. Datos y unidades experimentales · 9. Modelo de análisis · 10. Validez y reproducibilidad · 11. Ética, seguridad y límites · 12. Relación con el pre-registro

**Referencias**

---

# PARTE I — ESTADO DEL ARTE

## 1. Introducción y propósito del Estado del Arte

El diagnóstico vehicular convencional es reactivo, opaco y no acumulativo: los códigos DTC se generan cuando el umbral de fallo ya se ha superado, identifican síntomas y no causas, y las herramientas habituales no reutilizan los casos resueltos. Frente a esa carencia, este trabajo plantea la siguiente pregunta de investigación:

> **PI:** ¿Puede un sistema inteligente híbrido descubrir y explicar patrones de fallo vehicular previamente no documentados mediante el análisis contextual y longitudinal de datos OBD-II?
>
> *Especificación metodológica:* el sistema se implementará mediante aprendizaje no supervisado, análisis de eventos operativos, arquitectura multiagente, modelos de lenguaje, RAG y memoria evolutiva con validación de hipótesis.

La separación entre pregunta y especificación es deliberada. La pregunta estudia un fenómeno — la posibilidad de convertir telemetría en conocimiento diagnóstico nuevo —; las tecnologías enumeradas son los mecanismos experimentales con los que se contrasta, y cada mecanismo puede ser aceptado o refutado individualmente sin invalidar automáticamente la pregunta. Esta distinción gobierna tanto el Estado del Arte como el diseño experimental de la Parte II.

El hilo conductor de ambas partes es una cadena epistemológica que conviene enunciar antes de revisar la literatura, porque delimita qué debe encontrarse en ella y qué no puede darse por resuelto:

```text
TELEMETRÍA → EVENTO OPERATIVO → ANOMALÍA CONTEXTUAL → PATRÓN CANDIDATO
           → HIPÓTESIS DIAGNÓSTICA → VERIFICACIÓN → CONOCIMIENTO
```

Cada eslabón nombra una cosa distinta, y la revisión demuestra que la literatura tiende a confundirlas. Un *outlier* es una rareza estadística; una *anomalía contextual* es una desviación respecto de lo esperado en un contexto operativo concreto; un *patrón candidato* exige recurrencia en eventos comparables; una *hipótesis diagnóstica* es una conjetura causal formulada sobre ese patrón; y solo la verificación — contra la telemetría, contra el resultado de una reparación, contra juicio experto — convierte la conjetura en conocimiento. Una anomalía estadística aislada no constituye un fallo nuevo. El propósito de este capítulo es examinar, eslabón por eslabón, qué resuelve ya la investigación existente, con qué limitaciones, y qué eslabones o combinaciones permanecen sin cubrir; el capítulo termina donde empieza la metodología: en la formulación del vacío que justifica el artefacto y en las hipótesis que lo someterán a prueba.

Dos reglas de redacción se aplican en todo el capítulo. Primera: ninguna afirmación de ausencia se formula como inexistencia absoluta; siempre se escribe "en la literatura analizada no se identificó…", porque eso es exactamente lo que el método permite afirmar. Segunda: se distingue de forma sistemática entre lo que la literatura demuestra (evidencia externa), lo que la documentación del proyecto ya ha medido (evidencia interna, hoy exclusivamente exploratoria), lo que este trabajo infiere razonadamente y lo que constituye hipótesis pendiente de validación.

## 2. Metodología de revisión bibliográfica

### 2.1 Protocolo

La revisión siguió un procedimiento inspirado en PRISMA (Page et al., 2021), ejecutado en cuatro iteraciones documentadas (entregas 1–4). El protocolo definió una taxonomía temática de quince líneas (las trece iniciales, ampliadas con la sublínea de sistemas multiagente y la línea de eventos vehiculares); diecisiete preguntas de revisión (RQ1–RQ17); cadenas de búsqueda por línea; criterios de inclusión (publicaciones 2021–2026, o anteriores si son fundacionales y se marcan como tales; estudios de diagnóstico, anomalías, pronóstico o mantenimiento; telemetría vehicular o técnicas directamente transferibles; metodología verificable) y criterios de exclusión (material comercial, ausencia de metodología, conducción autónoma no pertinente, ciberseguridad CAN pura salvo técnicas de anomalías reutilizables, duplicados, imposibilidad de verificación en fuente primaria).

### 2.2 Verificación y salvaguarda adversarial

Cada registro incluido fue verificado en su fuente primaria (página del editor, DOI resuelto o arXiv); los campos no verificables se marcaron "no consta" y los candidatos inaccesibles se descartaron y anotaron para recuperación posterior, en lugar de citarse sin verificar. Los preprints se identifican siempre como tales y se emplean como indicadores de tendencia, no como evidencia consolidada.

Como salvaguarda frente al sesgo de confirmación, cada vacío candidato fue sometido a una búsqueda adversarial cuyo objetivo declarado era refutarlo. Este procedimiento — buscar deliberadamente los trabajos que desmentirían la novedad propia — produjo los tres hallazgos que más han moldeado el capítulo: el ciclo de validación de hipótesis HDSO (Shang & Yang, 2026, preprint), que recortó la novedad del mecanismo de memoria propuesto; el sistema multiagente vehicular DDAS de 2003 (Murphey et al., 2003), que refutó la formulación literal del vacío multiagente; y el detector contextual CADD (Chen, Shin & Dadras, 2024), que cubre parcialmente el vacío de diagnóstico por eventos. Los tres se incorporan como antecedentes en lugar de omitirse: un vacío que sobrevive a su propia refutación intentada vale más que uno que nunca fue puesto a prueba.

### 2.3 Alcance y limitaciones del proceso

La búsqueda se ejecutó mediante buscador web general con verificación en editor. Los recuentos agregados — aproximadamente 1.350 registros visualizados en unas 170 consultas, unos 250 candidatos evaluados en fuente primaria y 153 referencias incluidas, de ellas 27 preprints — **describen el barrido sistemático preliminar y no constituyen el flujo PRISMA definitivo**. La consulta formal a Scopus, Web of Science e IEEE Xplore, con registro de números exactos por base y cadena (sintaxis ya preparada en las entregas 2 y 3), queda pendiente del acceso institucional; el diagrama PRISMA definitivo se construirá con esos números, y esta limitación se declarará en la memoria mientras persista. Quedan igualmente pendientes la lectura a texto completo de tres candidatos relevantes recuperados solo a nivel de metadatos (Takara et al., ESWA 2025; Min et al., EAAI 2024; Onsu et al., IoT 2025) — los vacíos V1–V7 no se consideran definitivos hasta entonces — y una búsqueda adversarial de vigilancia inmediatamente anterior al depósito, justificada por la proporción de literatura de 2025–2026 en el corpus.

## 3. Diagnóstico vehicular y OBD-II

### 3.1 Estándares y acceso a señales

El diagnóstico a bordo está normalizado por ISO 15031 y SAE J1979, que definen los PID de acceso estándar sobre el bus CAN (ISO 15765); el diagnóstico avanzado emplea UDS (ISO 14229), y la transición normativa hacia SAE J1979-2 ("OBDonUDS", obligatoria en EE. UU. desde el año-modelo 2027 según CARB) confirma que la frontera entre OBD clásico y UDS se está desplazando. Este trabajo distingue por ello, de forma sistemática, entre PID estándar, PID propietarios, datos UDS, tramas CAN crudas y sensores externos. La práctica documenta límites concretos del acceso de bajo coste: con adaptadores de clase ELM327 la frecuencia efectiva ronda 1 Hz y la calidad depende del adaptador (Rykała et al., 2023); los parámetros no cubiertos por el estándar exigen PID propietarios obtenidos por ingeniería inversa y no transferibles entre fabricantes; y una Raspberry Pi es suficiente como nodo de adquisición (Ramai et al., 2022; Rimpas et al., 2020). Estas restricciones definen el punto de partida realista del prototipo: PID estándar a ~1 Hz con capa de transporte abstraída.

El paradigma diagnóstico previo al aprendizaje automático descansa en los códigos DTC y en sistemas expertos de reglas sobre síntomas, cuyo exponente clásico (EXEDS; Gelgele & Wang, 1998) exhibe las limitaciones canónicas del enfoque: conocimiento estático extraído de manuales de mantenimiento, sin aprendizaje ni adaptación. La insuficiencia del DTC como señal diagnóstica está además documentada empíricamente: en flotas reales los códigos frecuentes dejan de ser informativos y requieren ponderación (Ferreira et al., 2020), y el estudio de mantenimiento predictivo de Giannoulidis et al. (2024) sobre 40 vehículos registró fallos reales que no generaron ningún DTC. El eje del diagnóstico se desplaza así del código de avería a la telemetría continua contextualizada — el desplazamiento del que parte este TFM.

### 3.2 Datasets públicos: la limitación estructural del área

Los datasets públicos verificados cubren conducción normal real (HCRL Driving; X-CANIDS; AEGIS), ataques inyectados (HCRL Car-Hacking), telemetría de flota anonimizada orientada a pronóstico (SCANIA Component X; Kharazian et al., 2025) y, desde 2026, anomalías reales de motor anotadas por expertos (EngineAD; Hojjati et al., 2026, preprint). La auditoría de EngineAD obliga a una formulación precisa que este trabajo adopta: hasta donde alcanza la literatura pública analizada, no existe ningún dataset abierto de telemetría OBD-II/CAN de vehículos en operación con clases de fallo mecánico confirmadas y etiquetadas. EngineAD aporta únicamente anotaciones binarias de anomalía — signos tempranos juzgados por técnicos, sin confirmación por reparación — y publica los datos proyectados a componentes PCA, sin las señales físicas originales. La consecuencia metodológica es doble: la inyección sintética de fallos con firma física conocida no es un atajo de este trabajo sino la práctica del área, y el banco de fallos reproducible con ground truth que el prototipo construye cubre una carencia real de la literatura, no solo una necesidad interna.

## 4. Inteligencia artificial y mantenimiento predictivo

### 4.1 Aprendizaje supervisado: rendimiento alto, alcance limitado

La vertiente supervisada domina la literatura de diagnóstico automotriz con ML: ensembles y gradient boosting sobre registros OBD-II tabulares (Mahale et al., 2025; Jun et al., 2025), redes recurrentes sobre series con captura en Raspberry Pi (Idiri et al., 2025), híbridos profundos con validación de campo en 20 vehículos (Lu et al., 2025) y diagnóstico acústico (Tuleski et al., 2024). Sus métricas son altas, pero tres patrones sistemáticos limitan su alcance para nuestra pregunta: dependen de fallos conocidos y etiquetados; las exactitudes cercanas al 100 % sugieren con frecuencia fuga de datos y validaciones poco exigentes (Kumar & Jain, 2023); y la generalización entre vehículos y condiciones es pobre. Para descubrir patrones no documentados, el aprendizaje supervisado es por construcción insuficiente: no puede etiquetar lo que nadie ha etiquetado. Su papel en este trabajo queda relegado a línea base de contraste y a componentes auxiliares.

### 4.2 Detección no supervisada de anomalías

La detección no supervisada — modelar solo el comportamiento normal y señalar desviaciones — es el fundamento técnico de la capacidad de detectar lo no etiquetado. Tres resultados metodológicos fijan el marco de evaluación que este trabajo hereda: la evaluación masiva de Schmidl et al. (2022; 71 algoritmos, 976 series) muestra que los métodos clásicos son competitivos con el aprendizaje profundo a mucho menor coste y que no existe ganador universal; Wu & Keogh (2023) demuestran que los benchmarks públicos habituales están viciados; y Kim et al. (2022) prueban que el protocolo de *point adjustment* infla el F1 hasta hacer parecer competitivas puntuaciones aleatorias. La conclusión operativa — protocolo de evaluación propio, sin point adjustment, con fallos held-out declarados a priori — es una de las decisiones metodológicas más importantes heredadas de la revisión.

En el dominio vehicular, los detectores no supervisados sobre telemetría real confirman viabilidad y modestia a la vez: modelos recurrentes pequeños sobre CAN real alcanzan TPR del 86 % con FPR del 0,06 % en fallos de presión de aceite (Cherdo et al., 2023); autoencoders con umbral adaptativo llegan a F1 ≈ 94 % en registros de prueba (Abboush et al., 2026); pero sobre flotas en operación los F-scores caen a 0,68 (Giannoulidis et al., 2024) o exhiben una variabilidad inter-vehículo extrema — de 0,21 a 0,93 según el camión, con empate práctico entre los nueve métodos one-class evaluados (EngineAD). El empate clásico-profundo bajo restricciones reales lo corrobora la evaluación orientada a despliegue embarcado de un OEM (ECoLAD; Özer et al., 2026, preprint), donde varios métodos profundos "pierden viabilidad antes que exactitud". La lectura conjunta es reveladora: el factor limitante dominante del área no es la capacidad del modelo, sino la variabilidad inter-vehículo e inter-régimen — lo que convierte el condicionamiento contextual (sección 5) y la personalización (sección 6) en las palancas de mejora con mejor respaldo, y a los detectores clásicos ligeros en los candidatos naturales para edge.

Sobre el problema específico de lo "nuevo", la práctica del área reduce siempre el descubrimiento a protocolos held-out, open-set o novelty detection (Feng & Zhao, 2021; Lundgren & Jung, 2022; Pang et al., 2021): se retira del entrenamiento un fallo conocido por el experimentador y se mide si el sistema lo señala sin identificarlo erróneamente. Este trabajo adopta esa operacionalización y la extiende con dos condiciones adicionales — recurrencia y ausencia de correspondencia documental — que la práctica actual no integra.

## 5. Eventos y contexto operacional

### 5.1 Definiciones de trabajo

La revisión permite anclar en la literatura cuatro definiciones que el resto de la memoria emplea de forma estricta, porque su confusión es precisamente uno de los defectos que este trabajo trata de evitar:

- **Evento:** intervalo temporal delimitado que representa una condición o transición operacional reconocible del vehículo (arranque, ralentí, aceleración, frenado, régimen estable…). Corresponde a la maniobra o estado operativo de la literatura de conducción (Aboah et al., 2023; Molina-Campoverde et al., 2025) y al régimen o estado latente de la de series temporales (Hallac et al., 2017; Wang et al., 2023 — Time2State).
- **Anomalía contextual:** desviación respecto al comportamiento esperado *para un determinado evento o contexto operativo* — una presión de combustible normal en términos absolutos pero anormalmente baja durante una aceleración a alta carga. Es la anomalía contextual de la taxonomía clásica de Chandola et al. (2009), instanciada con el evento como atributo contextual.
- **Patrón candidato:** estructura multivariable y temporal que se repite en eventos comparables y presenta una desviación consistente respecto al baseline histórico.
- **Patrón de fallo no documentado:** patrón candidato recurrente que no encuentra correspondencia suficiente en DTC, corpus RAG, memoria validada ni conocimiento técnico disponible, y que es posteriormente sometido a validación.

La gradación importa porque es la que impide inflar los resultados: un detector que dispara una alarma no ha descubierto nada todavía; ha observado una diferencia. El problema científico empieza en la distancia entre detectar esa diferencia y convertirla en conocimiento diagnóstico, y las definiciones anteriores son los peldaños medibles de esa distancia. No se afirmará el descubrimiento de fallos desconocidos para la ingeniería automotriz — afirmación que este diseño experimental no puede sustentar —; "no documentado" se operacionaliza siempre respecto del conocimiento disponible del sistema.

### 5.2 Segmentación y detección de eventos

La literatura de eventos de conducción muestra un patrón nítido: clasificar eventos ya segmentados alcanza rendimientos muy altos — CNN unidimensionales logran el 93–99 % sobre maniobras (Escottá et al., 2022; Aboah et al., 2023) y la marcha engranada se infiere con 99,7 % de exactitud usando solo PID estándar a 1 Hz (Molina-Campoverde et al., 2025) —, mientras que los cuellos de botella reales son otros dos. El primero es la segmentación: en el pipeline naturalista de Aboah et al. la calidad del sistema la limita el segmentador, no el clasificador. El segundo es el descubrimiento no supervisado de regímenes, que sobre CAN alcanza solo F1-macro 0,469 (Kreutz et al., 2023, preprint), lo que desaconseja confiar la taxonomía de eventos a métodos puramente no supervisados. El espectro de métodos disponibles va de heurísticas y máquinas de estados (triviales a 1 Hz y aptas para edge) a detección de puntos de cambio — con la advertencia del benchmark TCPD de que ningún algoritmo domina (van den Burg & Williams, 2020) —, segmentación semántica (ClaSP/ClaSS; Ermshaus et al., 2023, 2024), clustering de regímenes interpretable — TICC, validado sobre sensores de un automóvil real (Hallac et al., 2017) — y detección de estados por aprendizaje contrastivo ligero, cuyo exponente E2USD corre en un microcontrolador con 73 KB de RAM (Lai et al., 2024). Ningún trabajo define una taxonomía estándar de eventos vehiculares: todas son ad hoc, lo que legitima definir la nuestra por diseño — en tres capas (viaje, evento/estado, muestra), que son los tres niveles recurrentes de la literatura — con evaluación propia de la segmentación contra ground truth antes de usarla aguas abajo. El evento cumple, además, una segunda función que la literatura de detección no suele contemplar y que anticipa la sección 10: es la clave natural de indexación de la experiencia del vehículo (la memoria de eventos), de modo que la misma unidad que contextualiza la detección organiza después la comparación longitudinal contra el propio historial.

### 5.3 Anomalía contextual: la evidencia central de la revisión

La evidencia de que condicionar la normalidad al contexto mejora la detección es cuantitativa y proviene de tres fuentes independientes. En datasets tabulares con anomalías contextuales, el mismo detector base pasa de AUC-PR inferior a 0,6 en su versión global a 0,85–1,0 condicionado al contexto (WisCon; Calikus et al., 2022), y los detectores globales fallan sistemáticamente en anomalías contextuales aunque rindan bien en las puntuales — lo que aconseja mantener también un detector global de extremos (QCAD; Li & van Leeuwen, 2023). En el dominio vehicular, CADD (Chen, Shin & Dadras, 2024) aporta la evidencia más directa: modelos de normalidad condicionados al régimen físico sobre OBD-II/CAN real, ejecutables en una ECU en tiempo real, mantienen TPR superior al 90 % con FPR bajo, mientras que el baseline global queda por debajo del 31 % de TPR y su tasa de falsos positivos se degrada por encima del 90 % cuando el entrenamiento mezcla condiciones distintas. Esa degradación del modelo global al mezclar regímenes es exactamente el fenómeno que la arquitectura de este trabajo pretende evitar mediante baselines por evento.

Queda, sin embargo, un hueco preciso: ningún trabajo identificado compara la detección de anomalías de *salud* vehicular condicionada a eventos operativos discretos frente al análisis continuo. CADD emplea contexto físico continuo sin diagnóstico posterior; Molina-Campoverde condiciona el consumo, no la salud; RAAD-LLM (Russell-Gilbert et al., 2025, preprint) condiciona la normalidad industrial con LLM y RAG pero sin eventos ni vehículos. Esa comparación ausente se convierte en uno de los experimentos formales de este trabajo (E0–E4; Parte II, §6).

## 6. Personalización longitudinal

La segunda forma de contexto es el propio vehículo: la pregunta de investigación es longitudinal porque la normalidad relevante no es la de la flota sino la de *esta* unidad física con *su* historia. La evidencia disponible converge: bajo datos no-IID, la agregación personalizada por vehículo supera a la global en 3–5 puntos (Almansour et al., 2025); la calibración por entidad no transfiere entre vehículos, según la propia industria (STREAM-VAE, Mercedes-Benz; Özer et al., 2025, preprint); la variabilidad inter-vehículo de EngineAD (F1 de 0,21 a 0,93) hace inviable un umbral común; y los modelos entrenados en una sola unidad arrastran sesgo condición-específico (Alonso-Fernandez et al., 2026).

El patrón maduro que emerge de la literatura no es, sin embargo, "global o individual", sino jerárquico: la flota como prior y normalizador — resolviendo el arranque en frío (Hendrickx et al., 2020) y la transferencia a condiciones no vistas (Michau & Fink, 2021) — y el residuo idiosincrático individual como señal, patrón demostrado en flotas eólicas reales (Chesterman et al., 2023). A ello se añade la cuestión del drift: la deriva lenta de un sensor y la degradación incipiente de un componente pueden ser estadísticamente indistinguibles, y un baseline que se adapta sin control puede aprender el fallo como normalidad. La literatura de aprendizaje continuo aporta el marco (Wang et al., 2024, TPAMI; Hurtado et al., 2023) y las herramientas operativas (ADWIN/DDM y frameworks ligeros aptos para Raspberry Pi como River; Montiel et al., 2021; OASW; Yang & Shami, 2021), pero ningún trabajo identificado realiza la comparación global-vs-individual-vs-jerárquico sobre OBD-II en edge. Esa comparación es el experimento C-PERS de este trabajo.

## 7. Explicabilidad y diagnóstico causal

La revisión mantiene una distinción estricta entre explicar la *decisión matemática del modelo* (capa a) y explicar la *posible causa mecánica de la anomalía* (capa b). La literatura XAI automotriz habita mayoritariamente la capa (a): SHAP y LIME sobre clasificadores de fallos (Brusa et al., 2023; Haque et al., 2025; Khemani & Qureshi, 2026; Lu et al., 2025). Saber qué variables movieron la puntuación del detector no es todavía saber qué le ocurre al vehículo.

El puente hacia la capa (b) existe por fragmentos, con cuatro patrones identificables: la traducción fiel de atribuciones a narrativa, deliberadamente sin añadir física (Explingo; Zytek et al., 2024, que además aporta un marco reutilizable de evaluación de explicaciones); la generación de hipótesis causales por LLM a partir de atribuciones — el análogo más cercano a nuestro pipeline es FaultExplainer, que parte de detección no supervisada y genera hipótesis incluso para fallos no vistos, aunque con alucinaciones y sin verificación (Khan et al., 2024, preprint), y su versión más completa integra grafo físico, SHAP, RAG y LLM (Zhao et al., 2026) —; la explicación estructural por construcción, donde cada residuo tiene sensibilidad física conocida y la hipótesis se valida por consistencia, demostrada en un camión real pero muda en lenguaje natural (Mohammadi, Krysander & Jung, 2025); y la vía causal/agéntica con ground truth de incidentes en sistemas TI (CORAL, Wang et al., 2023; RCAgent, Wang et al., 2024). El eslabón vacante, común a todos, es la *verificación de la hipótesis causal*: ningún trabajo identificado reúne detección no supervisada, atribución, hipótesis mecánica en lenguaje natural y validación contra ground truth físico o juicio experto estructurado. En automoción, con fallos de firma conocida, ese hueco define la contribución C-EXP, cuyo patrón de referencia es aproximar sin modelo estructural la validación por consistencia de Mohammadi et al.

## 8. Modelos de lenguaje y RAG

### 8.1 El LLM como detector: evidencia en contra

Los LLM pueden consumir series de sensores serializadas, pero la evidencia disponible los descarta como detectores: con fine-tuning alcanzan exactitudes altas solo en clases conocidas y generalizan mal (FD-LLM; Qaid et al., 2024, preprint); sin entrenamiento logran resultados comparables al estado del arte en benchmarks genéricos (LLMAD; Liu et al., 2025), pero en telemetría vehicular conectada el ML clásico los supera con claridad — F1 superior a 0,94 frente a 0,09–0,77 (Das et al., 2025). Este resultado convergente respalda una decisión arquitectónica central del prototipo: la detección corresponde a modelos de ML especializados; el modelo de lenguaje actúa como razonador sobre evidencia estructurada, nunca como detector.

### 8.2 RAG técnico: necesario, no suficiente

El RAG sobre manuales de fabricante es ya práctica industrial: asistentes embarcados con guardrails en BMW (CarExpert; Rony et al., 2023), pregunta-respuesta multimodal sobre un manual de taller con un modelo de 8B ajustado y 89,7 % de precisión procedimental (Nam et al., 2025), y benchmarking sistemático (Sorokin et al., 2026, preprint). La cadena de evidencia general — la recuperación reduce la alucinación (Shuster et al., 2021), especialmente con modelos pequeños (Béchard & Marquez Ayala, 2024) — convive con el resultado del antecedente más completo de OBD-II con RAG y LLM: la evaluación de Mahale et al. (2025) reporta alta fluidez pero exactitud factual notablemente menor. La recuperación es condición necesaria, no suficiente; la verificación posterior resulta imprescindible, y ese es el fundamento del agente crítico/verificador del sistema propuesto.

En cuanto al descubrimiento, la literatura es clara: el RAG recupera conocimiento existente; solo PARAM (Harbola & Purwar, 2025, preprint) lo aproxima al descubrimiento fusionando evidencia numérica nueva con conocimiento documental, y añadir RAG a la detección adaptativa aporta mejoras sustanciales (+18 puntos de exactitud en RAAD-LLM). En nuestro sistema el RAG cumple por ello dos funciones, y la segunda es la menos convencional: fundamentar hipótesis, y detectar la *ausencia* de correspondencia documental — condición necesaria de la definición de patrón no documentado. El mismo índice que normalmente responde "esto se parece a X" debe poder responder, con garantías medibles, "esto no se parece suficientemente a nada de lo que conozco".

## 9. Sistemas agénticos y multiagente

### 9.1 Tres cuerpos de literatura que conviene no confundir

El término "multiagente" nombra hoy al menos tres tradiciones distintas, y confundirlas invalida cualquier afirmación de novedad. La primera son los sistemas multiagente clásicos, anteriores a los LLM: la genealogía automotriz existe y debe citarse — DDAS combinaba en 2003 un agente de diagnóstico de vehículo con nueve agentes especializados por señal, lógica difusa entrenada únicamente con datos correctos (un modelo de normalidad) y razonamiento basado en casos como memoria de fallos previos, sobre señales reales de ECU (Murphey et al., 2003), y la escuela holónica desplegó agentes distribuidos de diagnóstico sobre redes de ECUs (Pavlíček et al., 2007). Que un sistema de 2003 anticipe la combinación normalidad-más-memoria-de-casos es un recordatorio útil de que las ideas arquitectónicas envejecen mejor que sus implementaciones. La segunda tradición son los sistemas multiagente con LLM, donde los agentes son roles conversacionales orquestados: aplicados a mantenimiento (Park et al., 2025, con LLM local; Lee et al., 2025), a análisis de causa raíz con recuperación y validación (MA-RCA; Fu et al., 2025), a detección de anomalías en series temporales (SAGE; Kang et al., 2026, preprint) y a telemetría operativa en producción (LEMAD; Ji et al., 2025). La tercera es la que este TFM propone y ninguna de las dos anteriores instancia: agentes LLM ligeros en edge que orquestan, además de herramientas, modelos de ML especializados, RAG, memoria y bases locales sobre telemetría en streaming.

Una precisión técnica evita malentendidos sobre viabilidad: la arquitectura multiagente describe roles lógicos, no procesos con modelos independientes. Varios agentes pueden compartir un mismo SLM físico, especializándose mediante prompts, herramientas, estado y permisos; la literatura formaliza la distinción entre rol e instancia del modelo (Wang et al., 2024) y los sistemas de referencia la practican. "Multiagente en Raspberry Pi" significa un grafo de roles sobre uno o dos modelos físicos, con enrutado selectivo hacia la nube.

### 9.2 Evidencia a favor y en contra de la descomposición

La honestidad del capítulo exige presentar ambos platos de la balanza, porque ambos pesan. A favor: la especialización multiagente tiene ablaciones contundentes cuando la tarea es heterogénea — SAGE pierde 48,4 % de F1 al eliminar los analizadores especializados; MA-RCA cae de F1 0,952 a 0,716 sin descomposición, y de forma más informativa aún, a 0,295 sin el agente de recuperación de casos y a 0,650 sin el validador, lo que indica que la memoria y la verificación son los componentes de mayor valor, no la multiplicidad en sí; LEMAD gana unos 9 puntos de F1 con su jerarquía. En contra: la coordinación es la primera fuente de fallo de los sistemas multiagente LLM (36,9 % de los fallos por desalineamiento inter-agente y 21,3 % por verificación deficiente en la taxonomía empírica MAST; Cemri et al., 2025); las ventajas se disipan al mejorar el modelo base y el enrutado en cascada de agente único a multiagente ahorra hasta un 20 % de coste (Gao et al., 2025, preprint); el agente único gana en el caso medio (Idowu & Almasoud, 2026, preprint); el debate por votación aporta márgenes pequeños con patologías propias (Tian et al., 2025, preprint); y un agente único bien equipado alcanza resultados sobresalientes en diagnóstico de baterías (BatteryAgent; Zhou et al., 2025, preprint).

La síntesis operativa que este trabajo extrae — y que se presenta como lectura original de evidencia ajena, no como hallazgo propio — es un conjunto de condiciones de aplicabilidad: la descomposición está justificada cuando concurren señales heterogéneas, salida diagnóstica estructurada y explicable, memoria de casos explotable y modelo base pequeño, condiciones que se dan en el caso edge de este TFM, donde la descomposición suple capacidad del SLM. Pero debe demostrarse por ablación, incorporar un verificador dedicado, ofrecer vía rápida mono-agente y presupuestar la latencia desde el diseño (los 3,2 s por muestra de LEMAD en cloud dimensionan el riesgo en una Raspberry Pi). El compromiso metodológico es explícito y va en ambas direcciones: la ablación A0–A6 somete la descomposición a prueba y, si el agente monolítico obtuviera resultados equivalentes con menor coste, así se reportará como resultado principal.

## 10. Memoria de agentes y consolidación validada

### 10.1 El punto ciego de la memoria de agentes

La literatura de memoria de agentes LLM ofrece la genealogía de la "memoria evolutiva" propuesta: memoria episódica de reflexiones (Reflexion; Shinn et al., 2023), recuperación ponderada por recencia, relevancia e importancia (Park et al., 2023), jerarquías paginadas para contextos pequeños (MemGPT; Packer et al., 2023), notas que evolucionan (A-MEM; Xu et al., 2025) y marcos taxonómicos generales (Zhang et al., 2024). Su punto ciego, sin embargo, es la validación: los insights se consolidan por juicio del propio LLM (ExpeL; Zhao et al., 2024) o por utilidad aprendida con refuerzo, sin verificación de veracidad (Memory-R1; Yan et al., 2026). Hay algo epistemológicamente inquietante en un sistema que convierte su propia inferencia en memoria y su memoria en premisa de la siguiente inferencia: si ningún filtro separa lo comprobado de lo plausible, el agente acaba recordando sus conjeturas como si fueran hechos. Las consecuencias están documentadas empíricamente: la memoria de agentes es envenenable con fracciones ínfimas de contenido malicioso (AgentPoison; Chen et al., 2024), el auto-almacenamiento de salidas no verificadas es un vector de inyección que no requiere acceso al banco de memoria (MINJA; Dong et al., 2025, preprint), y el "experience-following" propaga errores a largo plazo (Xiong et al., 2025, preprint). Las defensas publicadas filtran en la recuperación, no en la consolidación — el hueco exacto que el mecanismo de este TFM ocupa.

### 10.2 Consolidación validada: genealogía y estado

La idea de no consolidar sin validar tiene antecedentes que este trabajo reconoce expresamente. El ciclo Retrieve-Reuse-Revise-Retain del razonamiento basado en casos ya condiciona la retención a la revisión del caso (Aamodt & Plaza, 1994), instanciado con LLM y verificación por ejecución en DS-Agent (Guo et al., 2024); Voyager verifica habilidades por ejecución antes de almacenarlas (Wang et al., 2023, preprint); POPPER valida hipótesis con control estadístico del error mediante falsaciones secuenciales, sin memoria (Huang et al., 2025); y — el hallazgo adversarial que más recorta la novedad de nuestra propuesta — HDSO (Shang & Yang, 2026, preprint) implementa un ciclo casi isomorfo al nuestro (hipótesis falsables con plan de falsación, validación por etapas, consolidación selectiva, registro auditable de descartes), aplicado a habilidades procedimentales de agentes en benchmark. A ello se suman la teoría clásica de revisión de creencias (Alchourrón, Gärdenfors & Makinson, 1985) y la evidencia de que los LLM revisan mal sus creencias ante evidencia nueva (Belief-R; Wilie et al., 2024) — argumento decisivo para externalizar la revisión en la arquitectura de memoria en lugar de confiarla al modelo.

Lo que permanece sin cubrir es la conjunción que define C-MEM: un ciclo de estados de evidencia de grano fino (observación → anomalía → patrón candidato → hipótesis → validación → confirmada/descartada → conocimiento) sobre conocimiento diagnóstico *declarativo*, con validación anclada en el mundo físico (verificación determinista contra telemetría, resultado de reparación o juicio humano) y en dominio vehicular, donde lo único publicado es curación humana estática de grafos de conocimiento (Lin & Miao, 2025). Es también la contribución con mayor riesgo de erosión: HDSO demuestra que la idea está en el aire, y la vigilancia adversarial pre-depósito existe precisamente para detectar a tiempo si alguien la instancia antes en nuestro dominio.

### 10.3 Memoria indexada por eventos

La estructura de memoria propuesta — submemorias de viajes, de eventos por tipo, de anomalías, de hipótesis y de conocimiento validado, capaz de responder consultas como "comparar esta aceleración con las últimas quinientas aceleraciones similares del mismo vehículo" — tiene piezas en la literatura pero no instancia completa. La robótica aporta memorias episódicas jerárquicas consultables de la experiencia de una unidad física (Bärmann et al., 2025; ArmarX, Peller-Konrad et al., 2023) y el patrón de recuperar experiencias similares del propio historial (Du et al., 2023); el razonamiento basado en casos temporal ofrece el marco formal para casos-episodio con recuperación por embeddings (Weich et al., 2025); el mantenimiento predictivo practica el baseline por similitud de episodios a nivel de flota (Xue et al., 2022; Wang et al., 2008); y la infraestructura de similitud a escala está resuelta (Matrix Profile, Yeh et al., 2016/2018; índices iSAX, Wang et al., 2023). Ningún trabajo identificado combina los tres elementos: indexación por tipo de evento operativo como clave primaria, baseline histórico por unidad física individual y ejecución edge con capa de conocimiento destilado. La Event Memory se posiciona así como extensión natural y citada de cuatro tradiciones, no como invención ex nihilo.

### 10.4 Tres mecanismos adaptativos, tres regímenes de actualización

El sistema mantiene deliberadamente separados tres mecanismos adaptativos que la literatura tiende a confundir: la memoria de eventos, que aprende experiencias (escribe siempre, con etiqueta de confianza y estado de evidencia); el baseline del vehículo, que aprende normalidad individual (se actualiza solo con muestras que superan un filtro de admisión por score, siguiendo el patrón robusto a envenenamiento de MemStream; Bhatia et al., 2022); y el aprendizaje continuo, que modifica modelos (se dispara únicamente ante drift confirmado y persistente, con cuarentena de datos pre-fallo, Chesterman et al., 2023, y compuerta humana para cambios mayores, HILAD; Deng et al., 2025). Ninguno actualiza automáticamente a otro sin validación: la evidencia del sesgo de confirmación del self-training — el modelo que se reentrena con sus propias predicciones acumula error (Arazo et al., 2020) — convierte este aislamiento en requisito de seguridad, no en preferencia de diseño.

## 11. Edge AI y arquitecturas Edge–Cloud

La partición edge-cloud que el sistema adopta — preprocesado, segmentación, detección y alertas locales; razonamiento costoso, RAG amplio y entrenamiento en la nube — es el patrón dominante que la revisión del área confirma, con inferencia local en Raspberry Pi/Jetson, ganancias de latencia de hasta 37× frente al cloud centralizado y una carencia declarada de sistemas end-to-end reales (Bala et al., 2024). La viabilidad cuantitativa de cada pieza está establecida: detectores de anomalías corren en microcontroladores (MLPerf Tiny; Banbury et al., 2021), la cuantización INT8 reduce latencia un 27–40 % con pérdidas mínimas (DeepEdgeBench; Baller et al., 2021), la detección de estados contrastiva cabe en 73 KB de RAM (E2USD) y los SLM de 1,5–3B generan 2–15 tokens/s en Raspberry Pi 5 (Nguyen, 2025, preprint), suficiente para diagnóstico no interactivo. Existen antecedentes de LLM distribuido vehículo-edge-cloud con otros propósitos (Huo et al., 2025; Syn-Diag; Jia et al., 2025, preprint). El criterio que este trabajo deriva de esta línea no es una hipótesis sino una restricción: todo experimento reporta latencia, RAM y throughput en el perfil de recursos emulado equivalente a Raspberry Pi 5, y un resultado que viole el presupuesto edge se reporta como no viable aunque gane en calidad (Parte II, §5).

## 12. Antecedentes más próximos

La tabla siguiente resume los quince trabajos más próximos identificados en las cuatro iteraciones de la revisión, evaluados componente a componente frente a la propuesta (✔ presente, ◐ parcial, · ausente). Ninguno cubre más de cinco de las nueve dimensiones; las de menor cobertura simultánea son eventos, memoria validada, edge, verificación y telemetría OBD viva.

| # | Antecedente | OBD/CAN vivo | No sup. | Evento | Multiag. | LLM | RAG | Verif. | Memoria | Edge |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Mahale et al. 2025 (Discover Computing) | ◐ | ◐ | · | · | ✔ | ✔ | ◐ | · | · |
| 2 | Lin & Miao 2025 (Electronics) | · | · | · | ◐ | ✔ | ◐ | ◐ | ◐ | · |
| 3 | CADD — Chen et al. 2024 (RAID) | ✔ | ✔ | ◐ | · | · | · | ✔ | · | ✔ |
| 4 | DDAS — Murphey et al. 2003 (IEEE TVT) | ◐ | ✔ | ◐ | ✔ | · | · | · | ✔ | · |
| 5 | SAGE — Kang et al. 2026 [preprint] | · | ◐ | · | ✔ | ✔ | · | ◐ | · | · |
| 6 | MA-RCA — Fu et al. 2025 (CIS) | · | ◐ | · | ✔ | ✔ | ✔ | ✔ | ✔ | · |
| 7 | Giannoulidis et al. 2024 (EDBT) | ✔ | ✔ | · | · | · | · | · | ◐ | · |
| 8 | Cherdo et al. 2023 (Sensors) | ✔ | ✔ | · | · | · | · | · | · | ✔ |
| 9 | PARAM — Harbola & Purwar 2025 [preprint] | · | ◐ | · | ✔ | ✔ | ✔ | ◐ | ◐ | · |
| 10 | Park et al. 2025 (PHMAP) | · | · | · | ✔ | ✔ | ✔ | ◐ | · | ◐ |
| 11 | HDSO — Shang & Yang 2026 [preprint] | · | · | · | ◐ | ✔ | · | ✔ | ✔ | · |
| 12 | FaultExplainer — Khan et al. 2024 [preprint] | · | ✔ | · | · | ✔ | ◐ | · | · | · |
| 13 | RAAD-LLM — Russell-Gilbert et al. 2025 [preprint] | · | ✔ | ◐ | · | ✔ | ✔ | · | · | · |
| 14 | Das et al. 2025 (ACM SaT-CPS) | ◐ | ◐ | · | · | ✔ | · | · | · | · |
| 15 | DriveAgent — Hou et al. 2025 [preprint/IEEE] | · | ◐ | ◐ | ✔ | ✔ | · | ◐ | · | · |

La lectura por columnas es más informativa que la lectura por filas. Los antecedentes con telemetría vehicular viva (CADD, Giannoulidis, Cherdo) carecen de razonamiento agéntico, RAG y memoria; los antecedentes agénticos con LLM (SAGE, MA-RCA, PARAM, Park) operan fuera del dominio vehicular o sin telemetría en streaming, y ninguno en edge; el único con verificación y memoria validada simultáneas (HDSO) trabaja sobre habilidades procedimentales en benchmark, no sobre conocimiento diagnóstico anclado en telemetría; y la columna "Evento" no contiene ningún ✔ pleno — el diagnóstico condicionado a eventos operativos discretos no aparece instanciado en ningún antecedente. Cinco resultados replicados de forma independiente funcionan además como principios de diseño heredados: los métodos clásicos ligeros igualan o superan al aprendizaje profundo en detección embarcada; el LLM no debe ser el detector sino el razonador; la memoria de casos y la verificación son los componentes de mayor valor añadido en sistemas agénticos de diagnóstico; el condicionamiento contextual multiplica la detectabilidad; y la personalización por unidad supera al modelo global bajo heterogeneidad.

## 13. Contradicciones de la literatura

Una revisión que no encuentra contradicciones probablemente no ha buscado bien. Este corpus contiene al menos cuatro, y el diseño experimental del TFM está construido, en buena parte, para posicionarse ante ellas con datos propios en lugar de con preferencias.

**Profundo frente a clásico.** Los métodos de aprendizaje profundo dominan los benchmarks académicos de detección de anomalías, pero las evaluaciones masivas (Schmidl et al., 2022), los datasets vehiculares reales (EngineAD) y las evaluaciones industriales embarcadas (ECoLAD) muestran empate práctico con los clásicos a mucho menor coste. Interpretación adoptada: bajo restricciones edge y con datos vehiculares heterogéneos, la carga de la prueba recae sobre el método profundo; el prototipo parte de detectores clásicos ligeros y solo escala si la mejora medida lo justifica.

**Global frente a contextual.** Los detectores globales rinden bien en benchmarks con anomalías puntuales y se degradan drásticamente en anomalías contextuales (WisCon; QCAD; CADD). No es una contradicción real sino un artefacto de evaluación: los benchmarks viciados (Wu & Keogh, 2023) sobre-representan anomalías puntuales. Interpretación adoptada: mantener ambos — baseline por evento para lo contextual, guardián global para extremos —, y medir la diferencia en el experimento E0–E4.

**Monoagente frente a multiagente.** Tratada en §9.2: ablaciones favorables (SAGE, MA-RCA, LEMAD) frente a taxonomías de fallo y costes (MAST, Gao, Idowu). Se resuelve por condiciones de aplicabilidad y, en este trabajo, por ablación propia A0–A6 con compromiso de reportar el resultado en cualquier dirección.

**Fluidez frente a exactitud factual.** Las evaluaciones de explicaciones divergen: fluidez alta con exactitud factual baja (Mahale et al., 2025) frente a valoración humana alta (SAGE). La divergencia refleja instrumentos de medida distintos, no fenómenos distintos: una explicación puede sonar competente y estar equivocada — y un evaluador que solo mide fluidez no distinguirá ambas cosas. Interpretación adoptada: evaluación en dos capas, con métricas objetivas de recuperación, juez LLM calibrado no coincidente con el generador, aleatorización de posiciones y submuestra validada manualmente (Zheng et al., 2023; Wang et al., 2024), y la exactitud factual como métrica primaria de H-EXP.

## 14. Vacíos de investigación V1–V7

Los vacíos se formulan tras las búsquedas adversariales y se ordenan por su papel en este trabajo. Su consolidación definitiva queda condicionada al PRISMA formal y a los tres textos completos pendientes (§2.3); ninguno se modifica aquí respecto de la versión auditada del capítulo 2.

**V7 (central) — Diagnóstico basado en eventos.** En la literatura analizada no se identificó ningún sistema que integre segmentación explícita de la telemetría OBD-II en eventos operativos discretos, modelos de normalidad por tipo de evento con baseline histórico por vehículo, y razonamiento agéntico de diagnóstico alimentado por esas anomalías contextuales. Los sistemas contextuales existentes emplean contexto continuo sin diagnóstico agéntico (CADD) o razonamiento LLM sin eventos ni vehículos (RAAD-LLM); nadie compara detección de salud por evento frente a continua.

**V2 — Memoria con validación de hipótesis.** No se identificó una memoria de agente para conocimiento diagnóstico declarativo con ciclo de estados de evidencia de grano fino y validación externa anclada en el mundo físico previa a la consolidación; los ciclos validados existentes operan sobre habilidades procedimentales en benchmark (HDSO) o artefactos ejecutables (DS-Agent), y las defensas de memoria filtran en recuperación, no en consolidación.

**V6 (reformulado tras la búsqueda adversarial) — Multiagente vehicular híbrido.** No consta una arquitectura multiagente LLM desplegada en el edge que opere sobre telemetría OBD-II viva y encadene detección de anomalías contextuales, RAG, hipótesis, verificación y memoria longitudinal por vehículo. La genealogía MAS de los años 2000 (DDAS, HoloMAS) se reconoce expresamente como antecedente; la formulación del vacío es la conjunción, no la multiplicidad de agentes.

**V1 — Integración global; V3 — personalización jerárquica por vehículo en OBD-II edge; V4 — eslabón anomalía-no-supervisada → explicación causal verificada; V5 — evaluación end-to-end con banco reproducible.** Mantienen las formulaciones de las entregas 2 y 3, reforzadas por la revisión final: la unidad "evento" da a V3 su mecanismo y a V4 su anclaje semántico, y las revisiones del área siguen declarando la ausencia de sistemas end-to-end evaluados (Bala et al., 2024; ECoLAD).

**Formulación integradora.** En la literatura analizada (≈153 referencias verificadas, hasta agosto de 2026) no se identificó ninguna propuesta que integre, en un único sistema evaluado end-to-end: (i) telemetría OBD-II en streaming; (ii) segmentación explícita en eventos operativos discretos con modelos de normalidad por tipo de evento y baseline histórico por vehículo; (iii) detección no supervisada de anomalías contextuales en el dispositivo edge; (iv) un sistema multiagente con modelos de lenguaje bajo restricciones edge, con roles de recuperación documental, historial, hipótesis y verificación; y (v) una memoria longitudinal por vehículo con ciclo explícito de estados de evidencia en la que solo el conocimiento validado se consolida. Los antecedentes cubren a lo sumo tres de los cinco ejes.

## 15. Posicionamiento del TFM

La dirección de la justificación es del estado del arte hacia el sistema, y no a la inversa: cada componente del prototipo existe porque una pregunta de revisión y un vacío identificado lo exigen — la capa de eventos responde a RQ17 y V7; el mecanismo de memoria a RQ9/RQ10 y V2; la descomposición agéntica a RQ16 y V6; el perfil por vehículo a RQ13 y V3. Ningún elemento arquitectónico se incorpora por interés tecnológico propio.

Las cinco contribuciones candidatas se clasifican por su naturaleza, y ninguna se presenta automáticamente como novedad científica:

- **C-MEM — Memoria diagnóstica evolutiva** (contribución **candidata a científica**): ciclo de evidencia de siete estados con validación previa a la consolidación, aplicado a conocimiento diagnóstico declarativo y anclado en verificación física, incluida la memoria indexada por eventos. Es la contribución más distintiva y, a la vez, la de mayor riesgo de erosión (vigilancia de HDSO y derivados hasta el depósito).
- **C-EVT — Diagnóstico event-aware** (contribución **metodológica y experimental**): la formalización del patrón candidato como unidad de representación y la comparación experimental E0–E4 entre representaciones de detección, que la literatura no contiene.
- **C-INT — Integración** (contribución **arquitectónica**, con validación experimental): la instancia medida de la cadena completa. Se declara como novedad de integración y de instancia: el esquema funcional en abstracto ya está propuesto conceptualmente (Jiang & Hu, 2025), sin validación.
- **C-EXP — Explicación verificada** (contribución **metodológica**): el pipeline anomalía → evidencias → hipótesis mecánica → verificación → explicación, que cubre el eslabón vacante de §7; su implementación concreta es en parte decisión de ingeniería.
- **C-PERS — Personalización** (contribución **experimental**, secundaria): la comparación global vs individual vs jerárquico por evento y por vehículo sobre el banco reproducible.

Separadamente, el trabajo produce ingeniería habilitadora que se documenta como tal y nunca como contribución científica: la API y la interfaz del demostrador, los contratos de datos, la infraestructura de contenedores, el registro de herramientas con escrituras al vehículo bloqueadas, el ciclo de vida y la gobernanza de modelos. La distinción no es cosmética: protege al tribunal de evaluar como ciencia lo que es producto, y protege al trabajo de que una crítica a la ingeniería se lea como refutación de la investigación.

## 16. Síntesis

El recorrido completo puede condensarse en una sola línea argumental. La pregunta de investigación exige convertir telemetría en conocimiento diagnóstico nuevo; la literatura muestra que cada eslabón de esa conversión existe por separado — detección no supervisada viable pero limitada por la variabilidad inter-vehículo e inter-régimen; evidencia fuerte de que el contexto multiplica la detección; generación de hipótesis por LLM sin verificación; memoria de agentes sin validación previa a la consolidación; viabilidad edge pieza a pieza — y que ninguna propuesta integra la cadena completa (V1–V7).

La conexión entre la pregunta, la evidencia revisada, el vacío, las hipótesis y los experimentos puede recorrerse familia a familia:

```text
PI ──► evidencia ─────────────► vacío ──► hipótesis ──► experimento
      contextual ≫ global          V7       H-EVT       E0–E4
      (WisCon, QCAD, CADD)                  H-PERS      global/individual/jerárquico
      consolidación sin validar    V2       H-MEM       ablación de memoria +
      (ExpeL, MINJA, HDSO)                              escenarios de propagación
      MAS: evidencia dividida      V6       H-MAS       A0–A6
      (SAGE/MA-RCA vs MAST/Gao)
      hipótesis sin verificación   V4       H-EXP       LLM / +RAG / +RAG+verif.
      (FaultExplainer, Mahale)
      sin sistema end-to-end       V1, V5   H-MAIN      held-out/open-set triple
      (Bala, ECoLAD)
```

De ese vacío se derivan, en suma, las seis familias de hipótesis que estructuran la validación: H-MAIN contrasta directamente la pregunta mediante el protocolo held-out/open-set con retirada simultánea de conocimiento; H-EVT, H-MEM, H-MAS, H-PERS y H-EXP contrastan cada mecanismo por separado, con condiciones de refutación explícitas que no arrastran a la pregunta principal. La Parte II desarrolla la metodología que gobierna ese contraste.

---

# PARTE II — METODOLOGÍA DE INVESTIGACIÓN

## 1. Enfoque metodológico

Este TFM es investigación aplicada de carácter constructivo: su objeto no es únicamente describir o explicar un fenómeno existente, sino diseñar, construir y evaluar un artefacto — el sistema inteligente híbrido Edge–Cloud — cuya evaluación experimental produce, a su vez, conocimiento científico sobre el fenómeno que motiva la pregunta de investigación. Esta doble condición (el artefacto como medio, el conocimiento como fin) sitúa el trabajo de forma natural en el paradigma de Design Science Research (DSR), cuya justificación se desarrolla en §2.

Dentro de ese marco general, el enfoque de validación es predominantemente cuantitativo y experimental: experimentos controlados con baselines, ablaciones, escenarios held-out y open-set, semillas y particiones fijadas, métricas pre-registradas y análisis estadístico. Se complementa, cuando el objeto lo exige, con evaluación cualitativa estructurada: rúbricas de calidad de explicación definidas a priori, revisión humana de submuestras y LLM-as-judge calibrado como instrumento auxiliar — nunca como única evidencia, dada la divergencia documentada entre fluidez y exactitud factual (Parte I, §13). Tres niveles metodológicos coexisten y no deben confundirse: la revisión sistemática inspirada en PRISMA es el *método de la fase de conocimiento*; DSR es la *metodología general* que organiza todo el trabajo; y el diseño experimental es el *mecanismo de validación empírica* de las hipótesis. El §3 y el diagrama que lo acompaña hacen explícita esta relación.

## 2. Justificación de Design Science Research

DSR es el paradigma que formaliza la producción de conocimiento científico mediante la construcción y evaluación de artefactos. Su fundamento moderno distingue entre la ciencia natural, que explica cómo son las cosas, y la ciencia del diseño, que estudia cómo deberían ser los artefactos para cumplir propósitos — distinción articulada por March & Smith (1995), que tipifican los productos del diseño (constructos, modelos, métodos e instanciaciones) y sus actividades (construir y evaluar). Hevner, March, Park & Ram (2004) establecieron las directrices canónicas del paradigma: un artefacto viable para un problema relevante, evaluación rigurosa, contribución verificable, rigor metodológico en construcción y evaluación, búsqueda iterativa de la solución y comunicación a audiencias técnicas y de gestión. Peffers, Tuunanen, Rothenberger & Chatterjee (2007) operacionalizaron el paradigma en un proceso de seis actividades (identificación del problema, objetivos de la solución, diseño y desarrollo, demostración, evaluación, comunicación) que es el que este TFM adopta como esqueleto. Gregor & Hevner (2013) aportan el marco para clasificar el tipo de contribución de conocimiento — relevante aquí porque permite posicionar las contribuciones del TFM como *improvement* (soluciones nuevas para problemas conocidos) y evitar reclamaciones de invención absoluta —, y Venable, Pries-Heje & Baskerville (2016) formalizan las estrategias de evaluación de artefactos (formativa/sumativa, artificial/naturalista), que fundamentan la elección de evaluación artificial controlada en este trabajo.

La adecuación de DSR a este TFM no se declara: se argumenta por contraste con las alternativas razonables. Un *diseño puramente experimental* (hipótesis sobre un fenómeno natural, sin artefacto) no captura la mitad constructiva del trabajo: aquí las hipótesis solo son contrastables porque el artefacto existe, y el artefacto es en sí una parte del resultado. La *investigación-acción* exige intervención iterativa en un contexto organizacional real con usuarios; este trabajo se desarrolla sobre un entorno emulado sin organización cliente, por lo que sus ciclos de intervención-reflexión no aplican. El *estudio de caso* y los métodos observacionales presuponen un objeto preexistente que estudiar; el sistema que aquí se estudia no existe hasta que se construye. Y el *desarrollo de ingeniería sin marco de investigación* produciría el prototipo pero no conocimiento evaluable: sin hipótesis falsables, baselines ni criterios de refutación, el resultado sería un producto, no una investigación. DSR es precisamente el marco que obliga a que la construcción rinda cuentas ante criterios científicos: cada componente debe justificarse desde el conocimiento previo (rigor), responder a un problema real (relevancia) y someterse a evaluación con posibilidad de refutación.

Conviene explicitar, además, qué coexiste dentro de DSR en este trabajo: la revisión sistemática (método de la base de conocimiento), el diseño experimental cuantitativo (método de evaluación), la evaluación cualitativa estructurada (método complementario de evaluación para explicaciones) y las decisiones de ingeniería documentadas (que DSR reconoce como parte de la construcción, pero que este TFM separa expresamente de las contribuciones). La relación entre los tres niveles se representa así:

```text
                    DSR (metodología general)
                            │
            ┌───────────────┴────────────────┐
            │                                │
   Estado del Arte                    Construcción del artefacto
   (revisión sistemática              (sistema híbrido Edge–Cloud:
    inspirada en PRISMA)               eventos, detección, multiagente,
            │                          RAG, memoria validada)
            │                                │
            └────────► Vacíos V1–V7          ▼
                       Hipótesis H-*   Evaluación experimental
                                       (E0–E4, A0–A6, memoria,
                                        held-out/open-set, edge)
                                             │
                                             ▼
                                        Conocimiento
                                 (aceptación o refutación de H-*;
                                  comunicación en la memoria del TFM)
```

PRISMA no es la metodología del TFM: es el procedimiento de una de sus fases. El diseño experimental tampoco lo es: es el instrumento de otra. DSR es el marco que exige que ambas existan y que las conecta.

## 3. Aplicación de DSR al TFM

La tabla siguiente mapea las actividades del proceso DSR (Peffers et al., 2007) sobre las fases reales del proyecto y sus entregables verificables. El proyecto se ha desarrollado en fases iterativas (F0–F8 completadas a fecha de este documento), lo que refleja la naturaleza iterativa del ciclo diseño-evaluación de DSR: los resultados de cada fase han refinado el diseño de la siguiente.

| Etapa DSR (Peffers et al., 2007) | Aplicación al TFM | Evidencia / entregable |
|---|---|---|
| 1. Identificación y motivación del problema | Carencias del diagnóstico convencional (reactividad, opacidad, no acumulación); formulación del problema y de la PI | docs/01 (comprensión del problema); Parte I §1 |
| 2. Definición de los objetivos de la solución | OG y OE1–OE8 con clase declarada ([C]/[M]/[X]/[A]/[I]), trazados a vacíos e hipótesis | docs/02 (objetivos); auditoría de alineación |
| 3. Diseño y desarrollo del artefacto | Arquitectura Edge–Cloud: banco de fallos y emulación OBD-II, segmentación de eventos, detectores no supervisados, runtime multiagente con RAG, memoria evolutiva con validación, gobernanza de modelos | ADRs 0001–0024; docs de arquitectura (agent-runtime, event-intelligence, data-architecture, models); fases F0–F7 |
| 4. Demostración | Prototipo funcional en entorno emulado; piloto exploratorio EXP-ANOM-002 (ventana vs evento) como demostración instrumental | Informes de fase F1–F8; registro de experimentos y modelos |
| 5. Evaluación | Protocolo experimental pre-registrado: EXP-ANOM-003 y sucesivos (confirmatorios), E0–E4, A0–A6, ablaciones de memoria, held-out/open-set triple, criterios edge | Protocolo de pre-registro (próximo hito); harness de evaluación; §6–§9 de esta Parte |
| 6. Comunicación | Memoria del TFM conforme a la plantilla UAX; este documento como comunicación intermedia al tutor | OE8; el presente documento |

Dos matices honestos sobre este mapeo. Primero, las etapas no fueron estrictamente secuenciales: parte de la construcción (F5–F6) avanzó en paralelo a la consolidación del Estado del Arte, y la auditoría de alineación científica de agosto de 2026 existe precisamente para verificar que la dirección de justificación quedara restaurada (del conocimiento hacia el sistema, y no al revés). DSR admite esta iteración; lo que exige es que la trazabilidad final sea verificable, y la matriz de trazabilidad del capítulo 2 la documenta componente a componente. Segundo, la etapa de evaluación está deliberadamente partida en dos regímenes — exploratorio y confirmatorio — separados por el pre-registro, distinción que §12 desarrolla.

## 4. Pregunta y objetivos

**Pregunta principal (vigente, con su especificación metodológica):**

> **PI:** ¿Puede un sistema inteligente híbrido descubrir y explicar patrones de fallo vehicular previamente no documentados mediante el análisis contextual y longitudinal de datos OBD-II?
>
> *Especificación metodológica:* el sistema se implementará mediante aprendizaje no supervisado, análisis de eventos operativos, arquitectura multiagente, modelos de lenguaje, RAG y memoria evolutiva con validación de hipótesis.

La PI se descompone en siete subpreguntas operativas, cada una ligada a una familia de hipótesis: PI.1 (detección no supervisada pre-DTC; precondición de H-EVT), PI.2 (eventos frente a análisis continuo → H-EVT), PI.3 (RAG y verificación → H-EXP), PI.4 (memoria validada → H-MEM), PI.5 (multiagente frente a monolítico → H-MAS, secundaria), PI.6 (personalización → H-PERS) y PI.7 (viabilidad edge → criterio transversal, no hipótesis).

**Objetivo general:** diseñar, implementar y evaluar un sistema inteligente híbrido Edge–Cloud para el diagnóstico vehicular a partir de telemetría OBD-II, capaz de detectar anomalías contextuales mediante aprendizaje no supervisado y de formular y explicar hipótesis diagnósticas mediante análisis de eventos, razonamiento multiagente, RAG y memoria evolutiva por vehículo con validación de hipótesis, evaluando experimentalmente su capacidad para identificar patrones no cubiertos por el conocimiento disponible y su viabilidad en dispositivos de recursos limitados.

**Objetivos específicos.** Cada objetivo declara su clase — [C] científico, [M] metodológico, [X] experimental, [A] arquitectónico, [I] ingeniería — precisamente para que el tribunal pueda distinguir qué se somete a juicio científico y qué se presenta como soporte:

- **OE1 [M]** Estado del arte y posicionamiento (RQ1–RQ17, V1–V7, con pendientes declarados).
- **OE2 [M+I]** Banco experimental reproducible: entorno emulado con límites de recursos, banco de fallos parametrizable con fallos conocidos y held-out, ground truth de eventos. La parte metodológica (banco con ground truth, carencia real del área) es instrumento de C-EXP; la infraestructura se declara ingeniería habilitadora.
- **OE3 [X/C]** Detección contextual basada en eventos: segmentación con evaluación propia y comparación E0–E4, incluido el brazo de personalización. Contrasta H-EVT y H-PERS.
- **OE4 [A+X]** Razonamiento diagnóstico multiagente con recuperación y verificación: ablación A0–A6 y comparación LLM / +RAG / +RAG+verificación. Contrasta H-MAS (secundaria) y H-EXP.
- **OE5 [C]** Memoria evolutiva con validación: ciclo de estados de evidencia, Event Memory, gates de admisión; ablación frente a sin-memoria y memoria sin validación, con escenarios de propagación de errores. Contrasta H-MEM.
- **OE6 [X]** Evaluación integradora end-to-end frente a H-MAIN, con protocolo pre-registrado y análisis de amenazas a la validez.
- **OE7 [I]** Sistema demostrador (API REST e interfaz mínima): ingeniería y producto, sin pregunta de investigación asociada; no se presentará como contribución.
- **OE8 [adm.]** Memoria del TFM conforme a la plantilla UAX.

Los objetivos secundarios OS1–OS3 (aplicación móvil, sincronización cloud, Raspberry Pi física) no condicionan la aprobación; OS3, si el cronograma lo permite, cerraría la diferencia metodológica declarada entre emulación y hardware real.

## 5. Hipótesis

La estructura es jerárquica por diseño: una hipótesis integradora que contrasta directamente la PI, y cinco parciales que explican *por qué* el sistema integrado funciona o no. Cada parcial aísla un mecanismo de la especificación metodológica, y su eventual refutación no invalida la pregunta: la precisa. Esta arquitectura de hipótesis es la traducción metodológica de la separación pregunta/mecanismos declarada en §4 — cualquier resultado de una parcial, positivo o negativo, responde la pregunta en lugar de amenazarla.

**H-MAIN (integradora — contraste directo de la PI).** El sistema integrado, ante patrones held-out/open-set retirados simultáneamente del detector, del corpus RAG y de la memoria, (i) los detecta como anómalos; (ii) los señala correctamente como *no cubiertos* por el conocimiento disponible; (iii) genera hipótesis diagnósticas evaluables — operacionalizadas como hipótesis correcta o parcialmente correcta según el ground truth del fallo inyectado, con evidencia recuperada suficiente y trazable —; y (iv) no incurre en identificación errónea con alta confianza. *Refutación:* identificación confiada errónea de los held-out, o hipótesis no mejores que el azar según el ground truth → la respuesta a la parte fuerte de la PI es negativa y se reporta con su análisis. La retirada simultánea del conocimiento en los tres planos (datos de entrenamiento, corpus documental, memoria) es la condición que hace al protocolo exigente: impide que el sistema "reconozca" por una vía lo que se le ocultó por otra.

**H-EVT (parcial — mecanismo de contexto).** El baseline por evento operativo (y por evento+vehículo) reduce los falsos positivos y mejora la detección de anomalías contextuales frente a la detección por puntos o por ventanas (comparación E0–E4). *Refutación:* sin mejora sobre la detección por ventanas → el evento queda como representación semántica para el razonamiento, no como mejora de detección.

**H-MEM (parcial — mecanismo de memoria).** La memoria con ciclo de validación (solo se consolida conocimiento validado) mejora el diagnóstico en casos repetidos y variantes, y consolida menos errores que una memoria sin validación, sin degradar los casos nuevos. Se evalúan tres brazos — sin memoria, memoria sin validación, memoria con validación — incluyendo escenarios de propagación de errores (inyección controlada de conclusiones incorrectas). *Refutación:* la validación no reduce consolidaciones erróneas o su coste anula la mejora → C-MEM queda como mecanismo de seguridad con resultado negativo documentado.

**H-MAS (parcial y explícitamente secundaria — mecanismo arquitectónico).** La descomposición multiagente aporta valor frente al agente monolítico en los casos complejos, a coste acotado de latencia y tokens (ablación A0–A6). No se presupone la superioridad multiagente: si el monolítico iguala en todos los estratos, se reporta como resultado principal — alineado con la evidencia contraria de la literatura — y la arquitectura se justifica solo por mantenibilidad y seguridad. Su refutación no afecta a la contribución C-INT ni a la PI.

**H-PERS (parcial — mecanismo de personalización).** El baseline jerárquico (flota→vehículo, por evento) iguala o supera al individual y supera al global en tasa de falsos positivos, con arranque en frío acotado. *Refutación:* el global no es peor → se declara la limitación del entorno sintético para esta pregunta.

**H-EXP (parcial — mecanismo de explicación).** La verificación determinista de hipótesis contra las features de telemetría reduce las afirmaciones factualmente incorrectas frente a LLM solo y frente a LLM+RAG sin verificación, manteniendo la utilidad. La métrica primaria es la exactitud factual, precisamente porque el antecedente más completo del área documenta el fallo en ese punto. *Refutación:* sin reducción de errores factuales → C-EXP queda como propuesta de diseño con resultado negativo.

**Criterio transversal de viabilidad edge (no es una hipótesis).** La antigua H4 ("el sistema es viable en Raspberry Pi") se reclasificó como criterio transversal de aceptación, porque no compite con alternativas: es una restricción medible. Todo experimento reporta latencia por etapa, memoria RAM y, cuando aplica, throughput del modelo de lenguaje, en el perfil de recursos emulado equivalente a Raspberry Pi 5 (8 GB); un resultado que viole el presupuesto edge se reporta como no viable aunque gane en calidad. PI.7 se responde con el agregado de estas mediciones, declarando la diferencia metodológica emulación-vs-hardware.

*Nota de trazabilidad:* los informes históricos del proyecto (fases F0–F8) emplean la nomenclatura anterior (H1–H6, H2b, PI.5/H6); la tabla de correspondencia (docs/correspondencia_nomenclatura.md) los mapea a las familias vigentes, y los documentos históricos no se reescriben.

## 6. Diseño experimental

**Banco de fallos y escenarios.** La unidad de generación es el escenario: una sesión de conducción sintética con perfil de vehículo, secuencia de eventos operativos con ground truth exacto (el emulador conoce cada transición) y, opcionalmente, un fallo inyectado con firma física parametrizada y momento de inicio conocido. El banco incluye fallos conocidos (usados en diseño y ajuste) y fallos held-out (≥3, declarados a priori, jamás usados en entrenamiento ni ajuste), además de sesiones de normalidad para medir tasa de falsos positivos. La inyección sintética con firma conocida es la práctica del área ante la ausencia de datasets etiquetados con fallo mecánico confirmado (Parte I, §3.2), y es lo que proporciona el ground truth que hace evaluables las hipótesis.

**Protocolo held-out y open-set.** Para H-MAIN, los fallos held-out se retiran simultáneamente del entrenamiento del detector, del corpus RAG y de la memoria. El sistema se evalúa en su capacidad de señalarlos como anómalos, declararlos no cubiertos, y formular hipótesis evaluables contra el ground truth — con un clasificador supervisado de fallos conocidos como cota de contraste y el mismo sistema con conocimiento completo como cota superior.

**Comparaciones planificadas.** Cuatro ejes experimentales, cada uno ligado a una familia: E0–E4 (representaciones de detección: punto, ventana, régimen, evento, evento+vehículo → H-EVT, con el brazo de personalización global/individual/jerárquico → H-PERS); A0–A6 (arquitecturas de agente, de monolítico a runtime completo con crítico y memoria, por feature flags sobre una única base de código → H-MAS); brazos de memoria (sin / sin-validación / con-validación → H-MEM); y cadena de explicación (LLM / +RAG / +RAG+verificación → H-EXP). Los brazos con LLM se ejecutan además con un hipotetizador heurístico como control, para aislar la contribución del modelo de lenguaje de la de la arquitectura.

**Replicación y control.** Mismos datos, sesiones, splits, semillas y reglas para todos los brazos de una misma comparación; semillas múltiples fijadas y declaradas; particiones train/validación/test sin contaminación (los held-out solo existen en test); umbrales de detección fijados por cuantil sobre train-normal, nunca sobre test; sin point adjustment; métricas point-wise y por episodio. La evaluación de la segmentación de eventos es previa e independiente (precision/recall/F1 por tipo con emparejamiento por IoU temporal, error de inicio y fin): ninguna comparación aguas abajo se apoya en una segmentación no evaluada.

**Evidencia exploratoria previa: el piloto EXP-ANOM-002.** Antes del pre-registro se ejecutó un experimento comparativo ventana-vs-evento-vs-unión (EXP-ANOM-002, fase F8) que este trabajo declara estrictamente como **piloto exploratorio** y que no se convertirá retrospectivamente en experimento confirmatorio. Sus resultados no confirman ni refutan H-EVT; su valor metodológico es otro, y es considerable: generó las lecturas direccionales que dan forma al experimento confirmatorio (la representación por eventos no sustituyó a la ventana como detector — F1 0,58 frente a 0,67, con FPR concentrado en un perfil con train escaso —, pero aportó señal complementaria medible exactamente en el tipo de anomalía relacional que motiva la PI, y la unión de ambos redujo el retardo de detección), permitió estimar magnitudes de efecto y costes computacionales reales (la capa de eventos resultó más barata que las ventanas), identificó correcciones de diseño concretas (más sesiones normales de entrenamiento por perfil; métrica complementaria por-evento) y motivó la selección de comparaciones de EXP-ANOM-003. Esta separación entre exploración que informa el diseño y confirmación que somete a prueba — con el pre-registro como frontera — es un mecanismo deliberado de integridad metodológica: impide que el mismo dato cuente dos veces, una para sugerir la hipótesis y otra para confirmarla.

## 7. Variables e instrumentos

| Hipótesis | Variable independiente | Variables dependientes | Instrumentos | Métricas |
|---|---|---|---|---|
| H-EVT | Representación de la detección (E0 punto / E1 ventana / E2 régimen / E3 evento / E4 evento+vehículo) | Detección y falsas alarmas | Banco de fallos con ground truth; harness de evaluación; detectores one-class; segmentador evaluado | P, R, F1, FPR, retardo de detección, F1 por tipo de evento, recursos edge |
| H-MEM | Configuración de memoria (sin / sin validación / con ciclo de validación) | Calidad diagnóstica en casos repetidos/variantes; consolidación de errores | Secuencias de casos con repeticiones; escenarios de propagación (inyección de conclusiones incorrectas) | Δexactitud 1.ª vs n-ésima aparición; consolidaciones erróneas; contaminación posterior; coste (tokens, latencia) |
| H-MAS | Arquitectura del agente (A0–A6, por feature flags) | Calidad y coste del diagnóstico | Suite estratificada por dificultad; mismo SLM compartido; control heurístico | Exactitud top-1/top-k, cobertura de evidencias, contradicciones, alucinaciones, latencia, tokens, RAM, tasa de finalización correcta |
| H-PERS | Alcance del baseline (global / individual / jerárquico flota→vehículo, por evento) | Detección contextual por vehículo; arranque en frío | ≥2 perfiles de vehículo del generador con firmas de normalidad distintas | ΔF1/ΔFPR por vehículo; curva de aprendizaje del baseline individual |
| H-EXP | Cadena de explicación (LLM / +RAG / +RAG+verificación determinista) | Exactitud factual y utilidad de las explicaciones | Casos con ground truth de causa; rúbrica a priori; juez LLM calibrado (≠ generador, posiciones aleatorizadas); submuestra con validación manual | Afirmaciones factualmente incorrectas; afirmaciones no verificables; utilidad; métricas IR del RAG (hit rate, MRR, nDCG) |
| H-MAIN | Disponibilidad del conocimiento (completo vs held-out triple: datos+corpus+memoria) | Comportamiento ante lo no cubierto | Protocolo held-out/open-set; cotas superior (conocimiento completo) y de contraste (clasificador supervisado) | Recall de señalización en held-out; tasa de "no cubierto" correcta; calidad de hipótesis según ground truth; calibración de confianza |

Los umbrales numéricos de éxito de cada familia están propuestos en la auditoría de alineación (docs/auditoria_alineacion_investigacion.md, §4) y se congelan en el pre-registro antes de ejecutar los experimentos confirmatorios (§12); por esa razón este documento los referencia sin reproducirlos como definitivos.

## 8. Datos y unidades experimentales

La plantilla académica habitual pide "población y muestra", categorías pensadas para investigación con sujetos humanos. Forzarlas literalmente sobre una investigación computacional produciría afirmaciones sin sentido; lo que sigue las traduce con rigor al objeto real de estudio, que es la práctica correcta cuando la unidad experimental no es una persona.

La **población** de este estudio es, en rigor, el espacio de comportamiento vehicular observable mediante telemetría OBD-II estándar: el conjunto de trayectorias de señales (RPM, carga, temperaturas, fuel trims, caudal de aire…) que un vehículo de gasolina puede exhibir en operación, en condiciones normales y bajo fallos incipientes. Ese espacio se muestrea mediante el generador de escenarios del banco experimental, que produce sesiones de conducción sintéticas a partir de perfiles de vehículo parametrizados y modelos de fallo con firma física definida a partir de literatura y documentación técnica. La **muestra** es, por tanto, el conjunto de sesiones generadas bajo el diseño experimental — no una muestra aleatoria de vehículos reales, y así se declara: la representatividad respecto del parque real es una limitación estructural asumida (L1), mitigada parcialmente mediante validación de la capa de detección sobre un dataset público con anomalías reales anotadas (EngineAD), entendida como contraste a nivel de método.

Las **unidades experimentales** se organizan jerárquicamente: el *perfil de vehículo* (parametrización de normalidad; la unidad de H-PERS); la *sesión* de conducción (la unidad de generación y de split); el *evento operativo* dentro de la sesión (la unidad de contexto; con ground truth del emulador); la *ventana* y el *tick* (las unidades de detección de los brazos E1 y E0); el *episodio de fallo* (intervalo con fallo activo; la unidad de recall de episodios y retardo); y el *caso diagnóstico* (la unidad de razonamiento del agente y de las comparaciones A0–A6 y H-EXP). Cada métrica de §9 se define sobre la unidad que le corresponde, y las particiones train/validación/test se realizan a nivel de sesión para evitar fuga entre unidades correlacionadas de una misma sesión.

## 9. Modelo de análisis

**Descriptivos y métricas por familia.** Detección: precision, recall, F1, FPR, retardo de detección y recall por episodio, con F1 desglosado por tipo de evento; segmentación: P/R/F1 por tipo con emparejamiento por IoU temporal (umbral 0,5), error de inicio y fin; recuperación documental: hit rate, MRR, nDCG; explicación: exactitud factual, afirmaciones no verificables, utilidad según rúbrica; sistema: latencia por etapa, RAM pico, throughput del SLM (tokens/s, time-to-first-token); H-MAIN: recall de señalización en held-out, tasa de rechazo open-set correcto, calidad de hipótesis contra ground truth y calibración de confianza.

**Inferencia estadística.** Se propone el siguiente plan de análisis, cuya versión definitiva quedará fijada en el pre-registro: comparaciones entre brazos con las mismas sesiones y semillas se tratan como datos apareados; dada la escala esperable de los experimentos (decenas de sesiones y episodios, no miles), se priorizan pruebas no paramétricas y de remuestreo — tests de permutación y Wilcoxon de rangos con signo para métricas continuas apareadas; McNemar para aciertos/fallos apareados por caso; intervalos de confianza por bootstrap (percentil, con remuestreo a nivel de sesión para respetar la estructura de dependencia) — junto con tamaños de efecto (diferencias absolutas y relativas de F1/FPR con sus intervalos; delta de Cliff para comparaciones ordinales), corrección por comparaciones múltiples dentro de cada familia (Holm) y análisis de errores cualitativo de los casos discordantes. La justificación es directa: los tamaños muestrales no garantizan normalidad ni la potencia necesaria para tests paramétricos; el apareamiento por sesión y semilla elimina una fuente mayor de varianza; y el énfasis en tamaños de efecto con intervalos — más que en umbrales de significación aislados — es lo que corresponde cuando el número de unidades es limitado y el interés es la magnitud práctica de la mejora. Cuando una diferencia no alcance evidencia suficiente, se reportará como no concluyente, no como ausencia de efecto; y los resultados negativos se reportan con el mismo detalle que los positivos, porque varias familias (H-MAS de forma explícita) tienen el resultado negativo como desenlace plenamente informativo.

**Evaluación cualitativa estructurada.** Las explicaciones se evalúan en dos capas: rúbrica definida a priori aplicada por juez LLM calibrado — distinto del modelo generador, con posiciones aleatorizadas para neutralizar sesgos posicionales documentados — y submuestra validada manualmente por el autor, que actúa como control de calidad del juez. El LLM-as-judge es instrumento auxiliar; ninguna conclusión de H-EXP o H-MAIN descansa exclusivamente en él.

## 10. Validez y reproducibilidad

**Validez interna.** Amenaza principal: que las diferencias entre brazos reflejen artefactos del banco y no del mecanismo evaluado. Controles: marco común por comparación (mismos datos, splits, semillas, reglas de decisión), umbral fijado sobre train-normal, held-out intocable, ablaciones que aíslan un factor por vez, control heurístico en los brazos con LLM y benchmark de casos congelado antes de conocer resultados (las ampliaciones generan versión nueva del benchmark, nunca modificación de la vigente).

**Validez externa.** Limitación estructural declarada: datos sintéticos de un entorno emulado, con modelos de fallo definidos por el autor (L1) y rendimiento medido en emulación, no en hardware real (L2). Mitigaciones: validación de la capa de detección sobre datos reales anotados a nivel de método; declaración explícita de la diferencia emulación-vs-hardware, que OS3 cerraría si el cronograma lo permite; y renuncia expresa a extrapolar los resultados al parque vehicular real — las conclusiones se formulan sobre el entorno experimental y como evidencia de concepto.

**Validez de constructo.** Las definiciones formales de evento, anomalía contextual, patrón candidato y patrón no documentado (Parte I, §5.1) operacionalizan los constructos de la PI; el protocolo de evaluación evita las prácticas que inflan resultados (point adjustment, benchmarks triviales); y "descubrir" se mide con el protocolo held-out/open-set estándar del área, extendido con recurrencia y contraste documental — nunca como afirmación de descubrimiento para la ingeniería automotriz.

**Validez estadística.** Tratada en §9: apareamiento, remuestreo, tamaños de efecto, corrección por multiplicidad y lectura direccional cuando el número de unidades no sustente más.

**Reproducibilidad.** El proyecto adopta reproducibilidad byte a byte como requisito operativo: semillas fijadas y registradas; manifiestos de datos y modelos con linaje completo; configuración declarativa por experimento; registro de ejecuciones con hash de código y entorno; reconstrucción determinista del registro de modelos verificada por test; y persistencia de artefactos de evaluación (métricas, predicciones, configuración, entorno) por cada corrida. El piloto EXP-ANOM-002 ya se ejecutó bajo este régimen, lo que da evidencia interna de que el marco es operativo y no aspiracional.

## 11. Ética, seguridad y límites

Cuatro riesgos concentran la reflexión ética de este trabajo, y los cuatro tienen contramedidas de diseño verificables. Primero, el riesgo de diagnóstico erróneo presentado con autoridad: el sistema es un prototipo de investigación y así se declara ante cualquier usuario ("no sustituye el diagnóstico profesional"); ninguna hipótesis diagnóstica se presenta como definitiva sin validación, la confianza se comunica calibrada y el ciclo de memoria está diseñado precisamente para que las conjeturas no se consoliden como hechos. Segundo, los errores del modelo de lenguaje: la evidencia de alucinación en el dominio es la razón de ser del verificador determinista y de la evaluación de exactitud factual; el LLM nunca decide solo. Tercero, la contaminación de la memoria: la propagación de errores y el envenenamiento documentados en la literatura se tratan como amenaza de seguridad de primer orden — gates de admisión, estados de evidencia, validación previa a la consolidación y escenarios experimentales de propagación que miden el fallo en lugar de suponerlo imposible. Cuarto, la seguridad del vehículo y de los datos: el registro de herramientas del agente tiene bloqueadas las escrituras al vehículo por construcción (el sistema observa, no actúa); y aunque el trabajo opera con telemetría sintética, el diseño trata la telemetría vehicular como dato personal potencialmente sensible — la localización y los hábitos de conducción son inferibles de ella —, con procesamiento local en el edge como decisión de minimización. En todos los flujos donde el sistema aprende de su propia experiencia se mantiene el principio de human-in-the-loop para cambios mayores: la automatización de la consolidación de conocimiento tiene compuertas, no piloto automático.

## 12. Relación con el pre-registro

La frontera entre exploración y confirmación de este trabajo es un acto administrativo con fecha: el pre-registro del protocolo experimental. Antes de ejecutar EXP-ANOM-003 y los restantes experimentos confirmatorios, se congelan por escrito: los umbrales numéricos de éxito y refutación de cada familia de hipótesis (hoy propuestos, no definitivos), los escenarios y fallos held-out, las semillas y particiones, y el plan de análisis estadístico. Lo ejecutado antes de esa fecha — señaladamente el piloto EXP-ANOM-002 — queda clasificado como exploratorio: puede generar hipótesis, seleccionar comparaciones, estimar tamaños de efecto y proponer umbrales, pero no puede confirmar nada, porque un umbral elegido mirando los datos que luego lo superan no es un contraste sino una descripción. Los experimentos confirmatorios se ejecutan después del pre-registro, contra los umbrales congelados, y sus resultados se reportan sean cuales sean — incluida la refutación de cualquiera de las familias, que el diseño jerárquico de §5 convierte en resultado informativo y no en fracaso del trabajo.

---

## Referencias

*Formato: APA abreviado con DOI/arXiv cuando consta; los preprints se marcan [preprint]. Las fichas bibliográficas completas de todo el corpus (≈153 referencias) están en las entregas 1–3 de la revisión sistemática (docs/estado_del_arte/). Se listan aquí únicamente las obras citadas en este documento.*

**Metodología de investigación (DSR, PRISMA):**

- Gregor, S., & Hevner, A. R. (2013). Positioning and presenting design science research for maximum impact. *MIS Quarterly, 37*(2), 337–355. https://doi.org/10.25300/MISQ/2013/37.2.01
- Hevner, A. R., March, S. T., Park, J., & Ram, S. (2004). Design science in information systems research. *MIS Quarterly, 28*(1), 75–105.
- March, S. T., & Smith, G. F. (1995). Design and natural science research on information technology. *Decision Support Systems, 15*(4), 251–266. https://doi.org/10.1016/0167-9236(94)00041-2
- Page, M. J., McKenzie, J. E., Bossuyt, P. M., et al. (2021). The PRISMA 2020 statement: An updated guideline for reporting systematic reviews. *BMJ, 372*, n71. https://doi.org/10.1136/bmj.n71
- Peffers, K., Tuunanen, T., Rothenberger, M. A., & Chatterjee, S. (2007). A design science research methodology for information systems research. *Journal of Management Information Systems, 24*(3), 45–77. https://doi.org/10.2753/MIS0742-1222240302
- Venable, J., Pries-Heje, J., & Baskerville, R. (2016). FEDS: A framework for evaluation in design science research. *European Journal of Information Systems, 25*(1), 77–89. https://doi.org/10.1057/ejis.2014.36

**Corpus del Estado del Arte (obras citadas en la Parte I):**

- Aamodt, A., & Plaza, E. (1994). Case-based reasoning: Foundational issues, methodological variations, and system approaches. *AI Communications, 7*(1), 39–59.
- Abboush, M., et al. (2026). Robust and interpretable anomaly detection. *Electronics, 15*(12), 2723. https://doi.org/10.3390/electronics15122723
- Aboah, A., et al. (2023). Driver maneuver detection. *Journal of Transportation Engineering, Part A, 149*(3). https://doi.org/10.1061/JTEPBS.TEENG-7312
- Alchourrón, C. E., Gärdenfors, P., & Makinson, D. (1985). On the logic of theory change. *Journal of Symbolic Logic, 50*(2), 510–530.
- Almansour, A., et al. (2025). Adaptive personalized federated learning. *Scientific Reports, 15*. https://doi.org/10.1038/s41598-025-17699-3
- Alonso-Fernandez, F., et al. (2026). Overtake detection in trucks using CAN. *Expert Systems with Applications* (en prensa; PII S0957417425029549).
- Arazo, E., et al. (2020). Pseudo-labeling and confirmation bias in deep semi-supervised learning. *IJCNN 2020*. https://doi.org/10.1109/IJCNN48605.2020.9207304
- Bala, B., et al. (2024). AI and edge computing for machine maintenance. *Artificial Intelligence Review*. https://doi.org/10.1007/s10462-024-10748-9
- Baller, S. P., et al. (2021). DeepEdgeBench: Benchmarking deep neural networks on edge devices. *IEEE IC2E 2021*. arXiv:2108.09457
- Banbury, C., et al. (2021). MLPerf Tiny benchmark. *NeurIPS Datasets & Benchmarks*. arXiv:2106.07597
- Bärmann, L., et al. (2025). Episodic memory verbalization. *IEEE Humanoids 2025*. arXiv:2409.17702
- Béchard, P., & Marquez Ayala, O. (2024). Reducing hallucination in structured outputs via retrieval-augmented generation. *NAACL 2024 Industry Track*. arXiv:2404.08189
- Bhatia, S., et al. (2022). MemStream: Memory-based streaming anomaly detection. *WWW 2022*. https://doi.org/10.1145/3485447.3512221
- Brusa, E., et al. (2023). Explainable AI for machine fault diagnosis. *Applied Sciences, 13*(4), 2038. https://doi.org/10.3390/app13042038
- Calikus, E., et al. (2022). Wisdom of the contexts (WisCon). *Data Mining and Knowledge Discovery, 36*. https://doi.org/10.1007/s10618-022-00868-7
- Cemri, M., et al. (2025). Why do multi-agent LLM systems fail? (MAST). *NeurIPS 2025*. arXiv:2503.13657
- Chandola, V., Banerjee, A., & Kumar, V. (2009). Anomaly detection: A survey. *ACM Computing Surveys, 41*(3). https://doi.org/10.1145/1541880.1541882
- Chen, K., Shin, S., & Dadras, S. (2024). CADD: Context-aware anomaly detection using vehicle dynamics. *RAID 2024*. https://doi.org/10.1145/3678890.3678895
- Chen, Z., et al. (2024). AgentPoison: Red-teaming LLM agents via poisoning memory. *NeurIPS 2024*.
- Cherdo, Y., et al. (2023). Unsupervised anomaly detection for cars CAN sensors. *Sensors, 23*(11), 5013. https://doi.org/10.3390/s23115013
- Chesterman, X., et al. (2023). Overview of normal behavior modeling approaches for SCADA-based wind turbine condition monitoring. *Wind Energy Science, 8*(6), 893–924. https://doi.org/10.5194/wes-8-893-2023
- Das, S., Griffith, D., & Rathore, H. (2025). LLM-based fault detection in connected vehicle time-series data. *ACM SaT-CPS 2025*. https://doi.org/10.1145/3716816.3727968
- Deng, H., et al. (2025). HILAD: Human-in-the-loop anomaly detection. *ACM Transactions on Interactive Intelligent Systems*. https://doi.org/10.1145/3778167
- Dong, Y., et al. (2025). MINJA: Memory injection attacks on LLM agents. arXiv:2503.03704 [preprint]
- Du, M., et al. (2023). Behavior Retrieval. *RSS 2023*. arXiv:2304.08742
- Ermshaus, A., Schäfer, P., & Leser, U. (2023). ClaSP: Parameter-free time series segmentation. *Data Mining and Knowledge Discovery, 37*. https://doi.org/10.1007/s10618-023-00923-x — variante streaming ClaSS: *PVLDB, 17*, 1953 (2024).
- Escottá, Á. T., et al. (2022). Evaluation of 1D and 2D CNNs for driving event recognition. *Sensors, 22*(11), 4226. https://doi.org/10.3390/s22114226
- Feng, L., & Zhao, C. (2021). Fault description based attribute transfer for zero-sample industrial fault diagnosis. *IEEE Transactions on Industrial Informatics, 17*(3).
- Ferreira, R., Scholz, T., & Prytz, R. (2020). Fault detection using DTC statistics. *LOD 2020*. https://doi.org/10.1007/978-3-030-64583-0_37
- Fu, Y., et al. (2025). MA-RCA: Multi-agent root cause analysis. *Complex & Intelligent Systems, 12*(4). https://doi.org/10.1007/s40747-025-02096-0
- Gao, S., et al. (2025). Single-agent or multi-agent systems? Why not both? arXiv:2505.18286 [preprint]
- Gelgele, H. L., & Wang, K. (1998). An expert system for engine fault diagnosis (EXEDS). *Journal of Intelligent Manufacturing, 9*(6). https://doi.org/10.1023/A:1008888219539
- Giannoulidis, A., & Gounaris, A. (2023). A context-aware unsupervised predictive maintenance solution. *Journal of Intelligent Information Systems, 60*(2). https://doi.org/10.1007/s10844-022-00744-2
- Giannoulidis, A., et al. (2024). Exploring unsupervised anomaly detection for vehicle predictive maintenance. *EDBT 2024*. https://doi.org/10.48786/edbt.2024.65
- Guo, S., et al. (2024). DS-Agent: Automated data science by empowering LLMs with case-based reasoning. *ICML 2024*, PMLR 235.
- Hallac, D., et al. (2017). TICC: Toeplitz inverse covariance-based clustering. *KDD 2017*. https://doi.org/10.1145/3097983.3098060
- Haque, E., Zabin, H., & Uddin, J. (2025). EnsembleXAI-Motor. *Machines, 13*(4), 314. https://doi.org/10.3390/machines13040314
- Harbola, A., & Purwar, S. (2025). PARAM. arXiv:2508.04714 [preprint]
- Hendrickx, K., et al. (2020). A general anomaly detection framework for fleet-based condition monitoring. *Mechanical Systems and Signal Processing, 139*. https://doi.org/10.1016/j.ymssp.2019.106585
- Hojjati, H., et al. (2026). EngineAD. arXiv:2603.25955 [preprint]; dataset: https://doi.org/10.5683/SP3/TX13P1
- Hou, K., et al. (2025). DriveAgent. arXiv:2505.02123 [preprint]
- Huang, K., et al. (2025). POPPER: Automated hypothesis validation with agentic sequential falsifications. *ICML 2025*, PMLR 267.
- Huo, J., et al. (2025). Personalized LLM service updating in vehicle-edge-cloud systems. *IEEE Transactions on Consumer Electronics, 72*(1). https://doi.org/10.1109/TCE.2025.3644688
- Hurtado, J., et al. (2023). Continual learning for predictive maintenance. *Intelligent Systems with Applications, 19*, 200251.
- Idiri, B., et al. (2025). Using deep learning for predictive maintenance. *Vehicles, 7*(4), 134. https://doi.org/10.3390/vehicles7040134
- Idowu, S., & Almasoud, A. (2026). Specialists or generalists? arXiv:2601.22386 [preprint]
- Ji, T., et al. (2025). LEMAD: LLM-empowered multi-agent anomaly detection. *Electronics, 14*(15), 3008. https://doi.org/10.3390/electronics14153008
- Jia, N., Liang, P., & Yu, H. (2025). Syn-Diag. arXiv:2510.05733 [preprint]
- Jiang, Y., & Hu, J. (2025). AI agent-enabled predictive maintenance. *Computers, 14*(8), 329. https://doi.org/10.3390/computers14080329
- Jun, S., et al. (2025). DTC prediction of commercial vehicles. *International Journal of Automotive Technology*. https://doi.org/10.1007/s12239-025-00223-x
- Kang, H., et al. (2026). SAGE. arXiv:2605.05725 [preprint]
- Khan, A., et al. (2024). FaultExplainer. arXiv:2412.14492 [preprint]
- Kharazian, Z., et al. (2025). SCANIA Component X dataset. *Scientific Data, 12*, 493. https://doi.org/10.1038/s41597-025-04802-6
- Khemani, B., & Qureshi, R. (2026). AI-driven predictive maintenance for connected vehicles. *Discover Vehicles*. https://doi.org/10.1007/s44465-026-00023-2
- Kim, S., et al. (2022). Towards a rigorous evaluation of time-series anomaly detection. *AAAI, 36*(7). https://doi.org/10.1609/aaai.v36i7.20680
- Kreutz, F., et al. (2023). Unsupervised driving event discovery. arXiv:2301.04988 [preprint]
- Kumar, A., & Jain, S. (2023). Driving behavior analysis. *Journal of Supercomputing*. https://doi.org/10.1007/s11227-023-05364-3
- Lai, Z., et al. (2024). E2USD: Efficient unsupervised state detection. *WWW 2024*. https://doi.org/10.1145/3589334.3645593
- Lee, J., et al. (2025). Exploring LLM-based agentic frameworks for fault diagnosis. *Annual Conference of the PHM Society, 17*(1). https://doi.org/10.36001/phmconf.2025.v17i1.4350
- Li, Z., & van Leeuwen, M. (2023). QCAD: Quantile-based contextual anomaly detection. *Data Mining and Knowledge Discovery, 37*(6). https://doi.org/10.1007/s10618-023-00967-z
- Lin, Y., & Miao, Q. (2025). An automotive fault diagnosis framework based on knowledge graphs and LLMs. *Electronics, 14*(21), 4180. https://doi.org/10.3390/electronics14214180
- Liu, J., et al. (2025). LLMAD. *KDD 2025*. https://doi.org/10.1145/3711896.3737239
- Lu, W., et al. (2025). Explainable hybrid deep learning model. *Electronics, 14*(22), 4488. https://doi.org/10.3390/electronics14224488
- Lundgren, A., & Jung, D. (2022). Open-set classification of time-series data. *Control Engineering Practice, 121*.
- Mahale, Y., Kolhar, S., & More, A. S. (2025). Automated vehicle fault diagnosis. *Discover Computing, 28*, 283. https://doi.org/10.1007/s10791-025-09823-8
- Michau, G., & Fink, O. (2021). Unsupervised transfer learning for anomaly detection. *Knowledge-Based Systems, 216*. https://doi.org/10.1016/j.knosys.2021.106816
- Mohammadi, F., Krysander, M., & Jung, D. (2025). Consistency-based diagnosis. *Control Engineering Practice, 159*, 106283. https://doi.org/10.1016/j.conengprac.2025.106283
- Molina-Campoverde, P., et al. (2025). Driving pattern analysis and gear shift classification. *Sensors, 25*(13), 4043. https://doi.org/10.3390/s25134043
- Montiel, J., et al. (2021). River: Machine learning for streaming data in Python. *JMLR, 22*(110).
- Murphey, Y. L., et al. (2003). DDAS: Distributed diagnostics agent system. *IEEE Transactions on Vehicular Technology, 52*(4). https://doi.org/10.1109/TVT.2003.814236
- Nam, S., et al. (2025). LoRA-tuned multimodal RAG. *Applied Sciences, 15*(15), 8387. https://doi.org/10.3390/app15158387
- Nguyen, T. (2025). LLM inference on single-board computers. arXiv:2511.07425 [preprint]
- Özer, E., et al. (2025). STREAM-VAE. arXiv:2511.15339 [preprint]
- Özer, E., et al. (2026). ECoLAD. arXiv:2603.10926 [preprint]
- Packer, C., et al. (2023). MemGPT. arXiv:2310.08560 [preprint]
- Pang, G., et al. (2021). Deep learning for anomaly detection: A review. *ACM Computing Surveys, 54*(2).
- Park, J. S., et al. (2023). Generative agents: Interactive simulacra of human behavior. *UIST 2023*.
- Park, S., et al. (2025). LLM-based multi-agent system for machine tools. *PHMAP, 5*(1). https://doi.org/10.36001/phmap.2025.v5i1.4480
- Pavlíček, P., et al. (2007). Multi-agent-based diagnostics of automotive electronic systems. *HoloMAS 2007*. https://doi.org/10.1007/978-3-540-74481-8_35
- Peller-Konrad, F., et al. (2023). A memory system of a robot cognitive architecture (ArmarX). *Robotics and Autonomous Systems, 164*, 104415. https://doi.org/10.1016/j.robot.2023.104415
- Qaid, H., et al. (2024). FD-LLM. arXiv:2412.01218 [preprint]
- Ramai, C., et al. (2022). Low-cost OBD-II data logging for battery electric vehicles. *Vehicles, 4*(4). https://doi.org/10.3390/vehicles4040064
- Rimpas, D., et al. (2020). OBD-II sensor diagnostics. *Energy Reports, 6*, 55–63. https://doi.org/10.1016/j.egyr.2019.10.018
- Rony, M. R. A. H., et al. (2023). CarExpert. *EMNLP 2023 Industry Track*. https://doi.org/10.18653/v1/2023.emnlp-industry.56
- Russell-Gilbert, A., et al. (2025). RAAD-LLM. arXiv:2503.02800 [preprint]
- Rykała, P., et al. (2023). *Energies, 16*(21), 7266. https://doi.org/10.3390/en16217266
- Schmidl, S., Wenig, P., & Papenbrock, T. (2022). Anomaly detection in time series: A comprehensive evaluation. *PVLDB, 15*(9).
- Shang, W., & Yang, T. (2026). HDSO. arXiv:2606.22330 [preprint]
- Shinn, N., et al. (2023). Reflexion: Language agents with verbal reinforcement learning. *NeurIPS 2023*.
- Shuster, K., et al. (2021). Retrieval augmentation reduces hallucination in conversation. *Findings of EMNLP 2021*.
- Sorokin, N., et al. (2026). DeepTest 2026. arXiv:2604.12615 [preprint]
- Tian, Y., et al. (2025). Beyond the strongest LLM. arXiv:2509.23537 [preprint]
- Tuleski, B. L., et al. (2024). Audio-based engine fault diagnosis. *Sensors, 24*(22), 7316. https://doi.org/10.3390/s24227316
- van den Burg, G. J. J., & Williams, C. K. I. (2020). An evaluation of change point detection algorithms (TCPD). arXiv:2003.06222 [preprint]
- Wang, C., et al. (2024). RCAgent. *CIKM 2024*. https://doi.org/10.1145/3627673.3680016
- Wang, D., et al. (2023). CORAL: Incident root cause analysis. *KDD 2023*. https://doi.org/10.1145/3580305.3599392
- Wang, L., Zhang, X., Su, H., & Zhu, J. (2024). A comprehensive survey of continual learning. *IEEE TPAMI, 46*(8). https://doi.org/10.1109/TPAMI.2024.3367329
- Wang, P., et al. (2024). Large language models are not fair evaluators. *ACL 2024*.
- Wang, T., et al. (2008). Similarity-based prognostics. *PHM 2008*.
- Wang, X., et al. (2024). A survey on LLM-based autonomous agents. *Frontiers of Computer Science, 18*(6).
- Wang, Y., et al. (2023). Time2State. *SIGMOD/PACMMOD, 1*(1). https://doi.org/10.1145/3588697
- Wang, Z., et al. (2023). Dumpy: A compact and adaptive index for large data series collections. *SIGMOD/PACMMOD, 1*(1). https://doi.org/10.1145/3588965
- Wang, G., et al. (2023). Voyager: An open-ended embodied agent with LLMs. arXiv:2305.16291 [preprint]
- Weich, R., et al. (2025). Time series embedding for CBR retrieval. *ICCBR 2025*. https://doi.org/10.1007/978-3-031-96559-3_22
- Wilie, B., et al. (2024). Belief-R: The belief revision capability of LLMs. *EMNLP 2024*.
- Wu, R., & Keogh, E. (2023). Current time series anomaly detection benchmarks are flawed. *IEEE TKDE, 35*(3).
- Xiong, Z., et al. (2025). How memory management impacts LLM agents. arXiv:2505.16067 [preprint]
- Xu, T., et al. (2024). SaySelf. *EMNLP 2024*.
- Xu, W., et al. (2025). A-MEM: Agentic memory for LLM agents. *NeurIPS 2025*. arXiv:2502.12110
- Xue, B., et al. (2022). Similarity-based prediction for remaining useful life: A review. *International Journal of Advanced Manufacturing Technology*. https://doi.org/10.1007/s00170-022-09280-3
- Yan, X., et al. (2026). Memory-R1. *ACL 2026*.
- Yang, L., & Shami, A. (2021). Lightweight concept drift detection (OASW). *IEEE IoT Magazine, 4*(2).
- Yeh, C.-C. M., et al. (2016/2018). Matrix Profile I; a unifying view. *ICDM 2016*; *DMKD, 32*(1). https://doi.org/10.1007/s10618-017-0519-9
- Zhang, Z., et al. (2024). A survey on the memory mechanism of LLM agents. arXiv:2404.13501 [preprint]
- Zhao, A., et al. (2024). ExpeL: LLM agents are experiential learners. *AAAI 2024*.
- Zhao, L., et al. (2026). PI-Dual-STGCN. *Sensors, 26*(2), 723. https://doi.org/10.3390/s26020723
- Zheng, L., et al. (2023). Judging LLM-as-a-judge. *NeurIPS 2023 Datasets & Benchmarks*.
- Zhou, Y., et al. (2025). BatteryAgent. arXiv:2512.24686 [preprint]
- Zytek, A., et al. (2024). Explingo. *IEEE Big Data 2024*.
- Normas: SAE J1979 / J1979-2 (OBDonUDS; CARB, MY2027); ISO 15031; ISO 14229 (UDS); ISO 15765.
