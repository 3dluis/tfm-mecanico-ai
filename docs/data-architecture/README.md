# Arquitectura de datos — Mecánico IA

**Punto de entrada al modelo de información completo del sistema.** Versión del esquema:
`SCHEMA_VERSION = 2` (contratos `mecanico_contracts` 0.2.0; ver [CHANGELOG](../../shared/CHANGELOG.md)).

## Principio rector: sin divergencia

```
Documentación  ↔  Contratos Pydantic  ↔  JSON Schema  ↔  SQLite/PostgreSQL
```

La **fuente de verdad son los contratos** (`shared/src/mecanico_contracts/`). De ellos se
generan automáticamente: los JSON Schemas (`make schemas`), el
[diccionario de datos](02_diccionario_datos.md) y los [ejemplos](examples/) (`make data-docs`);
el esquema relacional ([03](03_modelo_relacional.md)) es un espejo por convención de nombres
verificado por los tests de integridad (`tests-integration/`). CI regenera y compara: si algo
diverge, el build falla.

## Mapa de documentos

| Documento | Qué responde |
|---|---|
| [01 Modelo conceptual](01_modelo_conceptual.md) | Qué entidades existen, por qué, y cómo sirven a la pregunta de investigación |
| [02 Diccionario de datos](02_diccionario_datos.md) | **(autogenerado)** Cada atributo: tipo, requerido, descripción, restricciones; clasificación RAW/NORMALIZED/DERIVED/INFERRED y productor/consumidor/residencia por entidad |
| [03 Modelo relacional](03_modelo_relacional.md) | Tablas SQLite, migraciones, equivalencia PostgreSQL |
| [04 Telemetría](04_telemetria_series_temporales.md) | La cadena trazable sesión→raw→normalizado→ventana→features→inferencia→anomalía |
| [05 Diagnósticos y evidencias](05_diagnosticos_evidencias.md) | Caso→hipótesis(estados)→evidencia; el diagnóstico nunca es solo texto |
| [06 Memoria evolutiva](06_memoria_evolutiva.md) | Working/episódica/semántica; LearnedPattern; proceso de consolidación; experimento H3 |
| [07 Provenance y versionado](07_provenance_versionado.md) | ProvenanceRecord; política de versionado de esquemas, modelos, prompts y grafo |
| [08 Ownership Edge/Cloud](08_edge_cloud_ownership.md) | Matriz formal de qué vive dónde; funcionamiento offline |
| [09 Retención y sincronización](09_retencion_sincronizacion.md) | Política de retención por clase de dato; outbox priorizado idempotente |
| [10 Modelo vectorial y RAG](10_modelo_vectorial_rag.md) | KnowledgeDocument/Chunk/RetrievalEvent; grounding medible; plan de embeddings |

Diagramas: [ER](diagrams/er-model.mmd) · [flujo de telemetría](diagrams/telemetry-flow.mmd) ·
[diagnóstico y memoria](diagrams/diagnostic-memory-flow.mmd) ·
[datos edge↔cloud](diagrams/edge-cloud-data-flow.mmd) · Ejemplos JSON: [examples/](examples/)

## Las cuatro clases de datos (regla de oro)

**RAW** (observado directamente) → **NORMALIZED** (esquema canónico) → **DERIVED**
(features/ventanas calculadas) → **INFERRED** (producido por modelos o agente).
*Un dato INFERRED jamás se presenta como observación real*: cada entidad declara su clase
en el diccionario, y API/UI deben etiquetarla.

## Relación con el Agent Runtime

El [Edge Agent Runtime](../agent-runtime/README.md) (F5) CONSUME este modelo sin cambios de
esquema: DiagnosticState es working memory efímera; su traza y toda la observabilidad del
runtime se persisten en las entidades ya definidas (AgentRun/AgentStep/RetrievalEvent).

## Decisiones (ADRs)

[ADR-0012](../adr/0012-arquitectura-de-datos.md) (modelo de datos, trazabilidad, provenance) ·
[ADR-0013](../adr/0013-memoria-tres-niveles.md) (memoria en 3 niveles, pesos epistemológicos,
consolidación no automática) · [ADR-0014](../adr/0014-agente-v1.md) (agente v1 y
responsabilidades de nodos). Índice completo: [../adr/README.md](../adr/README.md).
