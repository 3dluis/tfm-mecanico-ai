# 2. Objetivos

## 2.1 Objetivo general

Diseñar, implementar y evaluar un sistema inteligente híbrido edge-cloud que, a partir de datos OBD-II, detecte anomalías de funcionamiento vehicular mediante aprendizaje no supervisado y genere diagnósticos explicables y recomendaciones de mantenimiento mediante un agente basado en LLM con recuperación aumentada por generación (RAG) y memoria evolutiva de casos, ejecutable en una plataforma de recursos limitados equivalente a una Raspberry Pi.

## 2.2 Objetivos específicos

Cada objetivo específico (OE) tiene criterio de verificación (CV) para que su cumplimiento sea comprobable en la memoria del TFM.

**OE1 — Estado del arte.** Elaborar una revisión estructurada de la literatura sobre (i) diagnóstico y mantenimiento predictivo vehicular con datos OBD-II/CAN, (ii) detección de anomalías en series temporales multivariantes, (iii) agentes LLM con herramientas y memoria, y (iv) RAG en dominios técnicos.
*CV: capítulo de estado del arte con tabla comparativa de trabajos, limitaciones identificadas y hueco de investigación justificado; todas las referencias verificadas.*

**OE2 — Entorno de datos emulado.** Construir un entorno de desarrollo reproducible que emule la plataforma edge (contenedor Docker con imagen ARM64 y límites de recursos) y el vehículo (emulador de ELM327 por software con transporte serie-virtual/TCP), capaz de reproducir escenarios de conducción normal y escenarios con fallos inyectados parametrizables.
*CV: `docker compose up` levanta el entorno completo; al menos 5 escenarios de fallo inyectable documentados y reproducibles con semilla fija.*

**OE3 — Adquisición y almacenamiento.** Implementar el módulo de captura de PIDs OBD-II (frecuencia configurable), validación, y persistencia local en base de datos con esquema documentado.
*CV: sesiones de conducción emuladas almacenadas e inspeccionables; pérdida de muestras < 1 % en condiciones nominales.*

**OE4 — Detección de anomalías.** Implementar y comparar al menos dos técnicas de detección de anomalías no supervisada sobre las series temporales capturadas, seleccionando la de mejor compromiso rendimiento/coste computacional para el edge.
*CV: comparación cuantitativa (F1, AUC-ROC, latencia, memoria) sobre los escenarios de fallo inyectado; justificación escrita de la técnica elegida.*

**OE5 — Sistema RAG.** Construir un índice vectorial sobre un corpus de documentación técnica de licencia compatible (descripciones de DTC, procedimientos genéricos de diagnóstico, manuales libres) y el pipeline de recuperación asociado.
*CV: conjunto de consultas de prueba con métricas de recuperación (hit rate, MRR) y análisis cualitativo de fragmentos recuperados.*

**OE6 — Agente de diagnóstico.** Implementar un agente en LangGraph que orqueste: interpretación de la anomalía detectada, consulta de DTC activos, recuperación RAG, consulta de la memoria de casos, generación de hipótesis, y producción de un diagnóstico estructurado y explicable con recomendación y severidad.
*CV: grafo del agente documentado; salida JSON estructurada válida en ≥ 95 % de ejecuciones de prueba; trazas de razonamiento almacenadas.*

**OE7 — Memoria evolutiva.** Implementar una memoria persistente de casos diagnósticos (episódica) con recuperación por similitud, que el agente consulte y actualice, y evaluar su efecto en diagnósticos repetidos.
*CV: experimento antes/después descrito en el plan experimental; métricas reportadas aunque el resultado sea negativo.*

**OE8 — Evaluación integral.** Evaluar el sistema completo frente a las hipótesis H1–H4: calidad de detección, calidad de explicación (con y sin RAG), efecto de la memoria, y viabilidad de recursos en la plataforma emulada.
*CV: capítulo de resultados con tablas, análisis de errores y discusión de amenazas a la validez.*

**OE9 — Interfaz de consulta.** Exponer el sistema mediante una API REST documentada (OpenAPI) y una interfaz mínima de usuario para visualizar estado, alertas y diagnósticos.
*CV: API desplegada en el entorno emulado; interfaz capaz de mostrar un caso de diagnóstico de extremo a extremo.*

**OE10 — Memoria del TFM.** Redactar la memoria conforme a la plantilla UAX, con estilo científico, decisiones justificadas y limitaciones declaradas.
*CV: documento completo entregado en plazo.*

## 2.3 Objetivos explícitamente secundarios (solo si el cronograma lo permite)

- **OS1:** Aplicación móvil Flutter consumiendo la API (en su defecto, la interfaz del OE9 será web mínima).
- **OS2:** Sincronización cloud bidireccional con resolución de conflictos (en su defecto, exportación/carga manual de la memoria de casos).
- **OS3:** Despliegue y medición en Raspberry Pi física (en su defecto, medición en contenedor ARM64 con límites de recursos, declarando la diferencia metodológica).

La distinción OE/OS es deliberada: los OE caben en el plazo de septiembre de 2026; los OS no condicionan la aprobación del TFM y se abordarán solo tras completar OE1–OE10.
