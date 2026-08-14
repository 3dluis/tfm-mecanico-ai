# ADR-0034 — Separación del generador aleatorio del comportamiento normal y de la inyección

**Estado:** Aceptada (decisión del autor, F20 · 2026-08-14)
**Relacionada con:** ADR-0010 (catálogo de inyección), ADR-0011 (protocolo de
evaluación), AUDIT-DATA-001 (F19, hallazgo que la motiva), Protocolo ML v1

## Contexto

La auditoría F19 midió una limitación estructural del laboratorio: el fallo compartía el
generador aleatorio del motor de señales (`FaultRuntime(rng=engine.rng)` en
`generate.iter_ticks_labeled`). Como todas las inyecciones del catálogo extraen números
aleatorios en cada tick de su ventana, **a partir de `fault_start` la secuencia del motor
se desincroniza**: la sesión anómala y su gemela normal dejan de compartir la trayectoria
base aunque usen la misma semilla.

Consecuencia experimental: los contrafactuales `normal_original` vs `synthetic_anomalous_copy`
—el instrumento con el que se mide el efecto real de una anomalía— mezclaban dos cosas
distintas: el efecto de la inyección y la divergencia del flujo aleatorio. F19 tuvo que
introducir un brazo SHAM (que consume el mismo RNG sin alterar valores) solo para poder
separarlas. Además, señales que la anomalía ni siquiera toca (SPEED, RPM en fallos
térmicos) aparecían modificadas.

## Decisión

1. **Dos fuentes de aleatoriedad independientes y declaradas:**
   - `seed` → **vehicle_behavior_seed**: trayectoria normal del vehículo (motor de señales).
   - `anomaly_seed` → **anomaly_injection_seed**: aleatoriedad propia de la inyección.
2. **Cambio ADITIVO del contrato** (`ScenarioSpec.anomaly_seed: int | None`, REGLAS.md
   regla 5). Con `anomaly_seed = None` se conserva **exactamente** el comportamiento
   heredado (RNG compartido); con valor, la inyección usa `random.Random(anomaly_seed)` y
   **no consume extracciones del motor**.
3. **Propiedad garantizada y verificada por tests:** con el mismo `vehicle_behavior_seed`
   y distinto `anomaly_injection_seed`, la trayectoria normal es **idéntica fuera de la
   región intervenida**, y las señales que la anomalía no modifica son idénticas en toda
   la sesión.
4. **Los datasets v1 no se regeneran ni se invalidan.** Sus escenarios no llevan
   `anomaly_seed`, por lo que siguen produciendo **los mismos ticks byte a byte**
   (verificado sobre las 8 sesiones de test). El encabezado de sesión gana un campo
   nullable, que es el efecto esperado de un cambio aditivo de contrato.
5. **A partir de Synthetic Benchmark v2, todo escenario con fallo declara ambas semillas.**

## Consecuencias

**A favor**
- Los contrafactuales pasan a ser exactos por construcción: el brazo SHAM deja de ser
  necesario para nuevos datasets (se conserva para auditar los v1).
- Permite el diseño que pedía el autor: fijar la trayectoria base y variar solo la
  anomalía (`normal + drift` vs `normal + correlation break` sobre la misma base).
- Elimina una fuente de ruido que contaminaba las medidas de efecto de F16 y F18.

**En contra / riesgos**
- Coexisten dos modos de generación. Mitigación: el modo se deduce del propio escenario
  (presencia de `anomaly_seed`), queda registrado en la cabecera de cada sesión y está
  cubierto por tests que comprueban ambas ramas.
- Las cifras de los experimentos v1 no son directamente comparables con las de v2 en el
  detalle de las regiones anómalas. Mitigación: v2 se declara como benchmark nuevo con
  referencia explícita a v1; **no se reescribe ninguna métrica histórica**.

## Alternativas descartadas

- **Cambiar el RNG compartido sin modo heredado:** habría invalidado la reproducibilidad
  byte a byte de todos los datasets y de la cadena de anclaje del freeze (LOF 0.163197).
- **Mantener el brazo SHAM como única solución:** corrige la medición pero no el dato; el
  gemelo sigue divergiendo y las señales no tocadas siguen contaminadas.
- **Semilla derivada (`anomaly_seed = f(seed)`):** reproducible, pero impide variar la
  anomalía manteniendo la base, que es justamente el requisito.
