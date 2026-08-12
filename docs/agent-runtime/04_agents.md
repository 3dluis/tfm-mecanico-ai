# 04 — Agentes especializados

[← Índice](README.md) · Interacción con tools: [agents-tools.mmd](diagrams/agents-tools.mmd)

**Telemetry Agent** (determinista, sin LLM). Solicita PIDs, consulta telemetría/sesiones
históricas, inicia adquisiciones dirigidas ("observar 60 s más", "medir a 2500 rpm" cuando
exista control del escenario), valida calidad (pérdidas, rangos). Fuente única de datos
nuevos del vehículo.

**Anomaly Agent** (determinista/ML). Ejecuta los modelos del paquete activo (LOF ONNX; z-score
de respaldo; futuros temporales), produce scores y métricas afectadas, compara ventanas.
El LLM jamás produce una anomalía matemática (ADR-0009).

**Diagnostic Agent** (LLM). Analiza el contexto ensamblado (doc 07), formula/ordena hipótesis
ESTRUCTURADAS (contrato DiagnosticHypothesis), identifica evidencia necesaria y propone
próximos pasos (`pending_questions`). Salida validada con Pydantic + reintento acotado.

**Knowledge Agent** (recuperación). Consulta RAG local (DTC, síntomas, procedimientos,
componentes); registra SIEMPRE documentos y chunks usados (RetrievalEvent).

**Recall Agent** (recuperación). Memoria episódica + LearnedPatterns por similitud
(vehículo, síntomas, DTC, features, firma temporal, diagnóstico); devuelve evidencia
histórica SIEMPRE etiquetada con su nivel epistemológico (simulado/sintético/dataset/real
no validado/humano validado — pesos de ADR-0013).

**Verification Agent** (CRÍTICO; principalmente determinista). Para cada hipótesis:
evidencia esperada (de las reglas por failure_mode y, en el futuro, derivada de las fichas
del corpus) vs observada (telemetría/features/DTC/relaciones entre variables/pruebas) →
SUPPORTED/CONTRADICTED/INCONCLUSIVE con DiagnosticEvidence ±. El LLM puede ayudar a ELEGIR
qué prueba realizar; la evidencia solo puede provenir de datos reales o fuentes explícitas.

**Critic Agent** (LLM con criterios estructurados; NO "opinión"). Checklist auditable sobre
el estado: ¿la hipótesis top está SUPPORTED? ¿hay evidencia contradictoria sin tratar?
¿afirmaciones sin evidencia (statement sin reference)? ¿cobertura de evidencia mínima?
¿las hipótesis rivales fueron consideradas? → veredicto {aceptable | necesita_iteración |
irresoluble} + preguntas concretas que alimentan `pending_questions`.

**Memory Agent** (determinista). Persiste episodio (CaseMemory con nivel epistemológico),
actualiza evidencia de patrones existentes (touch/supporting/contradicting), genera
candidatos (solo CANDIDATE, ADR-0013), mantiene provenance.

**Report Agent** (LLM/plantilla). Explicación final desde evidencia con etiquetado
explícito: **observado** (telemetría/DTC) · **inferido** (anomalías/scores) · **probable**
(hipótesis SUPPORTED) · **confirmado** (solo con feedback externo) · **desconocido**
(vacíos declarados). Incluye limitaciones y recomendaciones.
