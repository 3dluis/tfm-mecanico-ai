# obd-lab

Laboratorio de simulación OBD-II de Mecánico IA (contribución técnica C4 del TFM).

Responsabilidades: emulación ELM327 (pty/TCP), simulación de PIDs, escenarios declarativos
(YAML con semilla), inyección de fallos en caliente, replay de datasets reales al formato común
de sesión (JSONL de `OBDReading`) y grabación reproducible.

Decisiones: ADR-0003 (emulador + escenario propio), ADR-0004 (transporte). Evaluación empírica
del emulador: `docs/fase1/evidencia_emulador.json`.

Estado: scaffolding. Próxima fase: generador de escenarios calibrado con HCRL Driving Dataset.

## Estado (F3/F4)

Funcional: generador parametrizable (perfiles×fallos×escenarios YAML con semilla),
3 categorías (normal / known_fault / held-out multivariable), cuantización J1979,
emulación en vivo (Priority:1 + answer dict), suite_v1 (21 sesiones). El ground truth de
los escenarios alimenta `DiagnosticFeedback` (ver
[data-architecture/05](../docs/data-architecture/05_diagnosticos_evidencias.md)).
