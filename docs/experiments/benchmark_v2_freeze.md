# Synthetic Benchmark v2 — congelación (F21)

**Fecha:** 2026-08-14 · **Estado: CONGELADO** ·
**Manifiesto:** [`ai-models/configs/benchmark-v2-freeze.json`](../../ai-models/configs/benchmark-v2-freeze.json) ·
**Hash del banco:** `e2cdb79f96239b26f67d39d8d1a4ad2fa3b93ab773474400fac922e75503d275`

## Qué significa congelar

A partir de aquí, la composición del banco **no cambia** dentro de la línea experimental
que lo usa. Añadir o retirar sesiones exige **una versión nueva** del banco, nunca una
edición silenciosa de esta — misma regla que `arms-freeze-v1` para los brazos.

Los datos **no** se versionan en Git (`/data/` está en `.gitignore`: son regenerables de
forma determinista por semilla). Lo que se versiona es el **hash SHA-256 de cada sesión**,
que es la prueba de que una regeneración futura produce exactamente el mismo banco. La
verificación es una orden:

```bash
python tools/freeze_benchmark.py --verify ai-models/configs/benchmark-v2-freeze.json
```

## Composición

| Partición | Sesiones | Duración | Perfiles | Hash agregado |
|---|---|---|---|---|
| `train_v11` | 22 | 9.75 h | cold_start, highway, idle, urban | `596a1fa4d3db…` |
| `expansion_v2` | 12 | 12.00 h | cold_start, highway, urban | `8bd188777756…` |
| `test_historico` | 8 | 4.00 h | highway, urban | `4118f4b853f6…` |

- **train v2 = `train_v11` + `expansion_v2` = 34 sesiones normales (21.75 h).** Sin fallos.
- **`test_historico` NO se toca**: mismas 8 sesiones de la serie EXP-ANOM-001…009, con 5
  tipos de fallo (`vacuum_leak`, `maf_drift`, `corr_break_rpm_maf`, `load_coolant_decouple`,
  `joint_slow_drift`). El *distribution shift* que documentó AUDIT-DATA-001 **se conserva
  a propósito**: corregirlo ahora invalidaría la comparación con toda la serie anterior.

## Procedencia y trazabilidad

- `provenance: SIMULATED` (obd-lab, generación determinista por semilla).
- Semillas de comportamiento: 101-106 y 111-142 (v1.1), **530-541** (expansión v2), 301-314 (test).
- Política de RNG: `vehicle_behavior_seed` = `ScenarioSpec.seed`; `anomaly_injection_seed` =
  `ScenarioSpec.anomaly_seed` (ADR-0034). Las 34 sesiones de train son normales: no inyectan.
- Diseño de la expansión: derivado del **mecanismo** del generador (paseo aleatorio del LTFT
  σ = 0.01 %/tick frente al cuanto J1979 de 0.78125 % ⇒ el cruce depende de la DURACIÓN),
  no de mirar el conjunto de test. Detalle en [informe F20](../fase20/informe_f20.md).

## Límite declarado

El cruce de cuantización queda en **FEW** (6 de 34 sesiones, 18 %), no en `REPRESENTED`.
Si aparece FPR residual en autovía, la palanca prevista es **más sesiones largas** (banco
v3), no cambiar de modelo ni retocar el test.
