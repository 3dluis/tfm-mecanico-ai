# Mecánico IA — Edge Agent Runtime

**Punto de entrada a la arquitectura del sistema agéntico multiagente del edge.**
Evolución aprobada en F5: el `diagnostic-agent` deja de concebirse como agente monolítico y
pasa a ser el **Mecánico IA Edge Agent Runtime** — varios agentes especializados (roles
lógicos) orquestados por un Supervisor LangGraph con ciclos iterativos de investigación,
ejecutándose local-first en la Raspberry Pi. El directorio físico `diagnostic-agent/` se
conserva (ADR-0015 §consecuencias).

Analogía rectora: como un coding agent sobre un repositorio, pero sobre un vehículo:
`objetivo → observar telemetría → detectar → investigar → consultar memoria/documentación →
hipotetizar → obtener evidencia adicional → verificar → criticar → repetir → concluir`.

| Documento | Contenido |
|---|---|
| [01 Overview](01_overview.md) | Qué es el runtime, principios, qué reutiliza de F3/F4 |
| [02 Arquitectura multiagente](02_multi_agent_architecture.md) | Agentes lógicos vs modelos físicos; mapa completo |
| [03 Supervisor](03_supervisor.md) | Responsabilidades, DiagnosticState, política de decisión |
| [04 Agentes](04_agents.md) | Los 9 agentes: responsabilidades, herramientas, LLM sí/no |
| [05 Tool Registry](05_tool_registry.md) | Registro formal: esquemas, permisos, riesgo, idempotencia |
| [06 Loop Engineering](06_loop_engineering.md) | Ciclo OBSERVE→…→CRITIQUE, re-planificación, stop conditions |
| [07 Context Engineering](07_context_engineering.md) | Ensamblado dinámico de contexto con presupuestos |
| [08 Arquitectura de memoria](08_memory_architecture.md) | Working/episódica/evolutiva en el runtime (integra ADR-0013) |
| [09 Model Router](09_model_router.md) | Roles→modelos; registro por AgentRun |
| [10 Seguridad y límites](10_safety_and_limits.md) | Categorías READ_ONLY…VEHICLE_WRITE; read-only por defecto |
| [11 Observabilidad](11_observability.md) | Métricas del runtime para la evaluación científica |
| [12 Diseño experimental](12_experimental_design.md) | Arquitecturas A0–A6 por feature flags; métricas; hipótesis H5 |
| [Modelos de IA](../models/README.md) | (F7) Qué agente consume qué modelo (ML/embeddings/LLM), registro, ciclo de vida — mapa en [agent-model-use](../models/diagrams/agent-model-use.mmd) |
| [Detección dual](../diagrams/deteccion-dual.mmd) | (F10) Entrada del runtime: LOF primario + Event Intelligence complementario + Evidence Fusion (OR auditable, `RuntimeConfig.anomaly_mode`); contexto estructurado, nunca score a secas (07 §decisión F8/F9) |

Diagramas: [multi-agent](diagrams/multi-agent.mmd) · [flujo de diagnóstico](diagrams/diagnostic-flow.mmd) ·
[loop de investigación](diagrams/investigation-loop.mmd) · [agentes↔tools](diagrams/agents-tools.mmd) ·
[memoria](diagrams/memory.mmd) · [model router](diagrams/model-router.mmd) ·
[secuencia de un caso](diagrams/case-sequence.mmd)

ADRs: [0015 runtime multiagente](../adr/0015-edge-agent-runtime-multiagente.md) ·
[0016 tool registry y seguridad](../adr/0016-tool-registry-y-seguridad.md) ·
[0017 loop y context engineering](../adr/0017-loop-y-context-engineering.md) ·
[0018 diseño experimental A0–A6](../adr/0018-diseno-experimental-arquitecturas.md)

Relación con el resto de la documentación: la base de datos y contratos son los de
[data-architecture](../data-architecture/README.md) (sin cambios de esquema: el runtime los
CONSUME); la separación ML/LLM sigue siendo ADR-0009; la memoria sigue ADR-0013.
