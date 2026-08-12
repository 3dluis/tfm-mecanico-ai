# ADR-0012 — Arquitectura de datos: clases, trazabilidad y provenance obligatoria

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 4 · **Docs:** docs/data-architecture/

## Contexto

El agente empezará a generar y almacenar diagnósticos; cambiar la semántica de los datos a
posteriori sería mucho más costoso. La PI exige explicabilidad experimental: reconstruir de
cualquier resultado el camino completo hasta las observaciones crudas.

## Decisión

1. **Cuatro clases de datos** (RAW/NORMALIZED/DERIVED/INFERRED) declaradas por entidad; un
   dato INFERRED jamás se presenta como observación.
2. **Cadena de telemetría trazable por claves foráneas** (sesión→raw→punto→ventana→features→
   inferencia→anomalía), con `TelemetrySession` como entidad central de reproducibilidad
   (source, seed, scenario, versiones). TODA inferencia de modelo se persiste, se dispare o no.
3. **Diagnóstico estructurado**: caso→hipótesis (rank, estado, componente, modo de fallo)→
   evidencias con rol supports/contradicts; la explicación textual es una proyección.
4. **`ProvenanceRecord` explícito y obligatorio** para todo INFERRED de cara al usuario
   (mejor un objeto navegable que enlaces dispersos).
5. **Sin divergencia**: contratos Pydantic como fuente única; JSON Schema, diccionario de
   datos y ejemplos AUTOGENERADOS (`make data-docs`, verificado en CI); esquema SQL espejo
   por convención con mapeo genérico testeado.
6. **Ids globalmente únicos** (UUID) y `schema_version` en todo mensaje/fila (v2 actual).

## Alternativas consideradas

- *Provenance dispersa en cada entidad:* menos tablas, pero la pregunta «¿de dónde salió?»
  requeriría N joins ad hoc y se erosionaría con cada entidad nueva. Descartada.
- *Almacenar solo ventanas agregadas (sin raw):* ahorra espacio pero rompe la trazabilidad
  hasta la observación y la re-derivación; se resuelve con retención corta del raw (docs 09).
- *Diccionario de datos manual:* diverge inevitablemente; descartado por generación automática.

## Consecuencias

- Validado por `tests-integration/test_traceability_e2e.py` (16 pasos + navegación
  LearnedPattern→raw). El coste de escritura extra (inferencias, provenance) es asumible
  (SQLite local, lotes) y esencial para la memoria del TFM.
