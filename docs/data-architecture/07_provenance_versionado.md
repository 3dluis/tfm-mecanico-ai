# 07 — Provenance y política de versionado

[← Índice](README.md)

## ProvenanceRecord (obligatorio para todo INFERRED de cara al usuario)

Decisión (ADR-0012): modelo explícito en lugar de dispersar enlaces. Un solo objeto responde:

| Pregunta | Campo |
|---|---|
| ¿Qué vehículo? | `vehicle_id` |
| ¿Qué sesión(es)? | `session_ids` |
| ¿Qué telemetría? | `window_ids` (→ puntos → raw por FK) |
| ¿Qué features? | `fv_ids` |
| ¿Qué modelo ML y versión? | `inference_ids`, `model_refs` ("lof@0.2.0") |
| ¿Qué documentos RAG? | `document_chunk_ids` |
| ¿Qué memoria recuperada? | `case_memory_ids` |
| ¿Qué versión del agente? | `agent_run_id` → AgentRun.graph_version/llm_model |
| ¿Qué prompt? | `prompt_version` |
| ¿Qué hipótesis/evidencia/validación? | vía subject_id → caso → hipótesis/evidencias/feedback |

## Política de versionado

| Artefacto | Mecanismo | Regla |
|---|---|---|
| Contratos | `SCHEMA_VERSION` global + CHANGELOG en shared | Dentro de una versión: SOLO cambios aditivos retro-compatibles; breaking ⇒ +1 y entrada de CHANGELOG (v2 actual) |
| Esquema físico | `PRAGMA user_version` | Sigue a SCHEMA_VERSION; migraciones en `store.migrate()` |
| Features | `feature_set_version` en FeatureVector y ModelManifest | Cambiar features ⇒ nueva versión ⇒ los manifiestos antiguos se rechazan en el edge |
| Modelos ML | semver en ModelManifest + sha256 | ADR-0009 |
| Corpus RAG | `KnowledgeDocument.version` + checksum | reingesta = nueva versión, chunks nuevos |
| Grafo del agente | `AgentRun.graph_version` | cambia con topología o responsabilidades de nodos |
| Prompts | `PROMPT_VERSION` en el generador | todo cambio de prompt es una versión (afecta a resultados) |
| Patrones | `LearnedPattern.version` + estado SUPERSEDED | un patrón nunca se edita: se supersede |

Regla operativa: dos resultados solo son comparables si coinciden schema, feature_set,
modelo, grafo y prompt — el registro de experimentos (`runs.jsonl`) y AgentRun los capturan
todos, así que la comparabilidad es computable.
