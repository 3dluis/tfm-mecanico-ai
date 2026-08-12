# 10 — Seguridad y límites operacionales

[← Índice](README.md) · ADR: [0016](../adr/0016-tool-registry-y-seguridad.md)

## Categorías de herramientas

- **READ_ONLY**: lectura del vehículo/datos (PIDs, DTC, consultas). Autonomía plena.
- **SAFE_LOCAL**: escritura local (inferencias, evidencia, memoria, eventos). Autonomía
  plena; auditada.
- **VEHICLE_WRITE**: clear_dtc, reset_ecu, tests activos. **NO registradas en v1**: cuando
  se incorporen exigirán (a) confirmación humana explícita por operación, (b) doble
  validación (Supervisor + regla independiente), (c) registro reforzado. Nunca parte de la
  autonomía inicial.
- **EXTERNAL**: red (sync, cloud). Fuera del camino crítico; el runtime opera offline.

## Límites operacionales

Los presupuestos del loop (doc 06) son límites duros del runtime, no sugerencias: superar
cualquiera fuerza transición a Report con el outcome que corresponda (INCONCLUSIVE/
INSUFFICIENT_DATA/FAILED). El disclaimer de prototipo de investigación acompaña todo
informe. El razonamiento de nivel 3 nunca sobrescribe silenciosamente niveles 1-2 (doc 02).
