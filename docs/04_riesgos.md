# 4. Riesgos

Escala: Probabilidad (P) y Impacto (I) en Bajo / Medio / Alto. Cada riesgo tiene mitigación y plan de contingencia. Los riesgos R1 y RI1 son los dominantes del proyecto.

## 4.1 Riesgos técnicos

| ID | Riesgo | P | I | Mitigación | Contingencia |
|----|--------|---|---|------------|--------------|
| R1 | **El plazo (sept. 2026) no absorbe el alcance completo** | Alta | Alto | Priorización estricta OE vs. OS; cronograma con hitos semanales; lista de recortes preacordada (`07`, §3) | Ejecutar recortes en orden: OS1→OS2→OS3→reducir a 1 técnica de detección→corpus RAG mínimo |
| R2 | Inferencia LLM inviable bajo QEMU ARM64 (lentitud extrema de emulación de instrucciones) | Alta | Medio | Estrategia dual: funcionalidad en ARM64/QEMU, rendimiento en contenedor x86 con límites de recursos; Ollama corre nativo y solo se limita CPU/RAM | Reportar rendimiento como cota con método declarado (L2); opcionalmente alquilar instancia cloud ARM (p. ej. Ampere/Graviton) para una medición más realista |
| R3 | El emulador ELM327 no cubre los PIDs o los escenarios de fallo necesarios | Media | Alto | Evaluar el emulador en la semana 1; diseñar desde el inicio un **generador propio de escenarios** que alimente al emulador o lo sustituya (mismo contrato de interfaz) | Sustituir el emulador por generador propio de tramas/valores; el contrato `TransportLayer` lo permite sin tocar el resto |
| R4 | LLM local de 1–4 B genera salidas estructuradas inválidas o alucina en exceso | Media | Alto | Salida JSON con validación Pydantic y reintentos; descomponer el razonamiento en nodos pequeños del grafo; RAG para anclaje factual; probar ≥3 modelos (familias Qwen, Gemma, Phi) temprano | Plan B de S3: LLM cloud como generador principal y local para tareas simples; se documenta como resultado del estudio de viabilidad edge |
| R5 | Deriva del entorno: dependencias (LangGraph/LangChain cambian API con frecuencia) | Media | Medio | Versiones fijadas (lockfile), Docker como entorno canónico, CI mínima que ejecuta tests | Congelar versiones al inicio de Fase 2 y no actualizar hasta después de la entrega |
| R6 | Rendimiento de ChromaDB + embeddings en recursos limitados | Baja | Medio | Corpus pequeño (< 10⁴ chunks); embeddings compactos (dimensión ≤ 512); medir pronto | Cambiar a FAISS con índice plano (menor overhead) — decisión ya prevista en `05`, §4 |
| R7 | Pérdida de trabajo / entorno local | Baja | Alto | Git desde el día 1 con remoto (GitHub/GitLab); docs y experimentos versionados; datos regenerables por semilla | Restauración desde remoto |
| R8 | La base de datos con series a 1 Hz crece más de lo manejable en el edge | Baja | Bajo | Retención configurable + agregación (downsampling) de sesiones antiguas | Reducir frecuencia de muestreo a 0,5 Hz; irrelevante para la validez experimental |

## 4.2 Riesgos de investigación

| ID | Riesgo | P | I | Mitigación | Contingencia |
|----|--------|---|---|------------|--------------|
| RI1 | **Circularidad experimental**: los fallos se inyectan con reglas definidas por el autor y el detector podría estar implícitamente ajustado a esas mismas reglas, inflando los resultados | Alta | Alto | Separación estricta: quien define los escenarios de fallo (documentados a priori, con parámetros aleatorizados por semilla) no ajusta el detector con ellos; conjunto de escenarios de test *held-out* nunca usados en desarrollo; validación complementaria con dataset público real | Declarar la amenaza a la validez explícitamente y limitar las conclusiones al entorno emulado |
| RI2 | Resultado negativo en H3 (la memoria no mejora los diagnósticos) | Media | Medio | Diseñar el experimento para que el resultado negativo sea igualmente publicable e informativo; medir también métricas intermedias (nº de pasos, tokens, similitud de casos recuperados) | Un TFM puede sostener un resultado negativo bien analizado; se discutirán causas (tamaño del LLM, calidad de recuperación) |
| RI3 | Imposibilidad de sostener la afirmación "descubre patrones no documentados" | Alta | Alto | Redefinición operativa ya hecha en `01`, §1.3: "no documentado" = sin DTC activo y ausente de la memoria del sistema; no se afirmará más de lo que el diseño experimental soporta | Reformular la contribución como "detección y explicación de anomalías pre-DTC" si el tribunal o el tutor lo exige |
| RI4 | Evaluación de explicaciones cuestionada metodológicamente (rúbrica subjetiva, sesgos de LLM-as-judge) | Media | Medio | Rúbrica publicada a priori en el repositorio; doble evaluación (autor + LLM juez) sobre muestra común y reporte del acuerdo entre ambos; citar literatura sobre limitaciones de LLM-as-judge en el estado del arte | Reducir las conclusiones de H2 a la métrica más objetiva disponible (tasa de afirmaciones con soporte en el corpus recuperado) |
| RI5 | Estado del arte insuficiente por falta de tiempo | Media | Alto | La revisión (OE1) arranca en paralelo a la ingeniería en Fase 1 y tiene presupuesto de tiempo protegido en el cronograma | Acotar la revisión a los 4 ejes definidos en OE1 con criterios de inclusión explícitos (revisión estructurada acotada, no exhaustiva, declarándolo) |
| RI6 | Datasets públicos candidatos no disponibles, con licencia incompatible o de calidad insuficiente | Media | Medio | Verificación en semana 1 (tarea IN-6 de `06`); múltiples candidatos identificados | El diseño experimental principal no depende de ellos (se apoya en el emulador); la validación externa quedaría como limitación adicional |

## 4.3 Criterios de disparo

Cada riesgo Alto/Alto se revisa al cierre de cada fase. Disparadores concretos:

- **Fin de semana 1:** si el emulador ELM327 no está operativo con el subconjunto de PIDs → activar contingencia R3.
- **Fin de semana 2:** si ningún LLM local produce JSON válido de forma estable → activar plan B de R4/S3.
- **Fin de semana 3:** si el pipeline de extremo a extremo no funciona en el entorno emulado → ejecutar primer nivel de recortes de R1.
