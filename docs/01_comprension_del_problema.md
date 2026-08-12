# 1. Comprensión del problema

## 1.1 Contexto

Los vehículos modernos exponen información de estado a través del estándar OBD-II (On-Board Diagnostics II), obligatorio en turismos de gasolina en EE. UU. desde 1996 y en la Unión Europea (EOBD) desde 2001 (gasolina) y 2004 (diésel). OBD-II define, entre otros, los servicios de diagnóstico (SAE J1979 / ISO 15031-5), los códigos de diagnóstico de fallo o DTC (SAE J2012 / ISO 15031-6) y el conector físico (SAE J1962). Sobre esta interfaz pueden leerse parámetros en tiempo real (PID): régimen del motor, temperatura del refrigerante, ajustes de combustible (fuel trims), carga calculada, tensión de sensores de oxígeno, etc.

El diagnóstico convencional presenta tres carencias que motivan este trabajo:

1. **Reactividad.** Los DTC se generan cuando un umbral de fallo ya se ha superado; el testigo MIL se enciende cuando el problema existe, no cuando se está gestando. La degradación progresiva (p. ej., deriva de un sensor MAF, empobrecimiento gradual de mezcla) no produce códigos hasta fases avanzadas.
2. **Opacidad para el usuario.** Un DTC (p. ej., `P0171 – System Too Lean, Bank 1`) identifica un síntoma, no una causa, y su interpretación exige conocimiento experto: el mismo código puede deberse a una fuga de vacío, un MAF sucio, baja presión de combustible o una sonda lambda degradada.
3. **Conocimiento disperso y no acumulativo.** La relación entre patrones de señales y causas raíz está repartida entre manuales de taller, boletines técnicos de servicio y experiencia de mecánicos, sin que las herramientas de diagnóstico habituales acumulen ni reutilicen los casos ya resueltos.

## 1.2 Problema

**No existe, en el ámbito del diagnóstico accesible al usuario final, un sistema que combine (a) análisis continuo de series temporales OBD-II en el borde (edge), (b) detección de anomalías no supervisada capaz de señalar comportamientos degradados sin DTC asociado, (c) razonamiento explicable apoyado en documentación técnica, y (d) acumulación de experiencia diagnóstica a lo largo del tiempo.**

Los escáneres comerciales leen y borran códigos; las plataformas telemáticas de flota centralizan datos pero dependen de conectividad y reglas predefinidas; los asistentes basados exclusivamente en LLM carecen de anclaje en los datos reales del vehículo y son propensos a alucinación. El hueco que este TFM explora es la integración de estas piezas en un agente híbrido edge-cloud.

## 1.3 Pregunta de investigación

> **PI:** ¿Puede un agente inteligente híbrido, que combine modelos de lenguaje, aprendizaje no supervisado, memoria evolutiva y recuperación aumentada por generación (RAG), descubrir y explicar patrones de fallo vehicular previamente no documentados utilizando datos OBD-II?

Para hacerla operativa y evaluable, se descompone en subpreguntas:

- **PI.1** ¿Con qué precisión pueden detectarse, mediante técnicas no supervisadas sobre series temporales de PIDs OBD-II, desviaciones del comportamiento normal del vehículo *antes* de que se genere un DTC? (métricas: precisión, exhaustividad, F1, tiempo de anticipación sobre fallos inyectados).
- **PI.2** ¿Mejora la incorporación de RAG sobre documentación técnica la calidad y la fiabilidad factual de las explicaciones generadas por un LLM local, frente al mismo LLM sin recuperación? (evaluación comparativa con rúbrica y/o LLM-as-judge, declarando sus limitaciones).
- **PI.3** ¿La acumulación de casos diagnósticos en una memoria persistente mejora el diagnóstico de casos posteriores similares? (evaluación con secuencias de casos repetidos/variantes).
- **PI.4** ¿Es viable ejecutar este pipeline completo con los recursos de una Raspberry Pi (4 GB–8 GB de RAM, CPU ARM)? (medición de latencia, memoria y throughput en entorno emulado con límites de recursos equivalentes).

**Precisión terminológica importante:** "patrones no documentados" se entenderá como *combinaciones de síntomas en los datos que no corresponden a un DTC activo ni a un patrón previamente registrado en la memoria del sistema*, verificables porque el fallo se habrá inyectado sintéticamente de forma controlada. No se afirmará el descubrimiento de fallos desconocidos para la ingeniería automotriz, afirmación que este diseño experimental no puede sustentar.

## 1.4 Hipótesis de trabajo

- **H1:** Un detector no supervisado (p. ej., basado en reconstrucción o en aislamiento) entrenado sobre ventanas de operación normal detecta fallos incipientes inyectados con F1 superior a un umbral fijado a priori y antelación medible respecto al DTC.
- **H2:** El agente con RAG produce explicaciones con menor tasa de afirmaciones no verificables que el LLM sin RAG, medido sobre un conjunto fijo de casos.
- **H3:** La memoria de casos reduce pasos de razonamiento y/o mejora la exactitud del diagnóstico en la segunda aparición de un patrón, frente a la primera.
- **H4:** El pipeline completo se ejecuta dentro de los límites de recursos de una Raspberry Pi 5 (8 GB) emulada, con latencia de diagnóstico aceptable para el caso de uso (orden de decenas de segundos, no interactivo en tiempo real).

Estas hipótesis son falsables y cada una tiene un experimento asociado (véase `07_cronograma_y_entregables.md`, Fase 4, y el protocolo experimental E3, que se publicará a priori en el repositorio).

## 1.5 Usuarios y casos de uso previstos

1. **Conductor particular:** recibe avisos tempranos y explicaciones comprensibles ("el ajuste de combustible a largo plazo lleva 3 semanas subiendo; patrón compatible con fuga de vacío; severidad media; revisar antes de 1000 km").
2. **Taller pequeño:** usa el historial y las hipótesis del agente como apoyo pre-diagnóstico.
3. **Investigación:** el sistema como banco de pruebas de agentes LLM con memoria en dispositivos de recursos limitados.

El caso 1 es el que guía el diseño del prototipo; los otros dos se declaran como contexto.
