# ADR-0007 — Contratos compartidos: Pydantic como fuente única + JSON Schema para Flutter

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 2

## Contexto

Cinco proyectos (cuatro Python, uno Dart) intercambian los mismos objetos (lecturas, anomalías,
diagnósticos…). Duplicar definiciones garantiza deriva; un IDL formal (protobuf) añade toolchain.

## Decisión

1. Paquete `mecanico_contracts` (en `shared/`) con **Pydantic v2 como única fuente de verdad**:
   tipado estricto, validación en runtime en los bordes de cada servicio, serialización JSON.
2. **Exportación automática a JSON Schema** (`shared/schemas/*.schema.json`, script
   `make schemas`) versionada en git. `mobile-app` genera sus modelos Dart desde esos esquemas
   (p. ej. quicktype/json_serializable en su fase); nunca se escriben a mano.
3. **Versionado:** cada mensaje lleva `schema_version` (entero); política del TFM: solo cambios
   aditivos y retro-compatibles; cambio incompatible ⇒ incrementar versión y registrar en el
   CHANGELOG de `shared`.
4. Contratos v1: `OBDReading`, `VehicleTelemetry`, `DetectedAnomaly`, `DTCRecord`,
   `DiagnosticHypothesis`, `DiagnosticResult`, `MaintenanceRecommendation`, `AgentEvent`,
   `CaseRecord`, `ModelManifest`, `ScenarioSpec`, `RecordedSession`, `SyncEnvelope`, más enums
   (`Severity`, `TransportKind`, `DetectorKind`, `AgentNode`).

## Alternativas consideradas

- *protobuf/gRPC:* contratos multi-lenguaje excelentes, pero: toolchain extra, gRPC innecesario
  (REST basta), peor legibilidad para el tribunal. Descartado por simplicidad.
- *JSON Schema escrito a mano como fuente:* válido para Dart pero pierde la validación Pydantic
  idiomática en Python (el 80 % del sistema). Descartado; se genera en la dirección contraria.
- *OpenAPI como fuente:* acopla contratos a las APIs; los contratos también viajan por archivos
  (sesiones JSONL, manifiestos). Descartado.

## Consecuencias

- `pip install -e ../shared` en cada proyecto Python (ruta relativa en el monorepo; en Docker se
  copia `shared/` en la imagen).
- Los JSON Schema exportados son también material de la memoria (apéndice de contratos).
- Riesgo: divergencia Pydantic↔Dart si se olvida regenerar; mitigación: `make schemas` en CI
  con verificación de diff limpio.
