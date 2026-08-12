# ADR-0016 — Tool Registry formal y operación read-only sobre el vehículo

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 5 · **Docs:** agent-runtime/05 y 10

## Decisión

1. Registro único de herramientas con especificación obligatoria: nombre, descripción,
   input/output schema, timeout, permisos por rol, side effects, idempotencia y
   `risk_level ∈ {READ_ONLY, SAFE_LOCAL, VEHICLE_WRITE, EXTERNAL}`.
2. Ningún agente ejecuta capacidades no registradas; todo acceso a datos pasa por
   repositorios expuestos como herramientas; toda ejecución se registra y cuenta contra
   presupuestos.
3. **El sistema opera READ_ONLY sobre el vehículo por defecto.** `clear_dtc`, `reset_ecu` y
   tests activos NO se registran en v1; su futura incorporación exigirá confirmación humana
   explícita por operación + doble validación + registro reforzado. Nunca autonomía inicial.

## Consecuencias

La superficie de acción del runtime es enumerable y auditable (necesario para la memoria
del TFM y para seguridad). Coste: burocracia al añadir herramientas — deliberado.
