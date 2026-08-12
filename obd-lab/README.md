# obd-lab

Laboratorio de simulación OBD-II de Mecánico IA (contribución técnica C4 del TFM).

Responsabilidades: emulación ELM327 (pty/TCP), simulación de PIDs, escenarios declarativos
(YAML con semilla), inyección de fallos en caliente, replay de datasets reales al formato común
de sesión (JSONL de `OBDReading`) y grabación reproducible.

Decisiones: ADR-0003 (emulador + escenario propio), ADR-0004 (transporte). Evaluación empírica
del emulador: `docs/fase1/evidencia_emulador.json`.

Estado: scaffolding. Próxima fase: generador de escenarios calibrado con HCRL Driving Dataset.
