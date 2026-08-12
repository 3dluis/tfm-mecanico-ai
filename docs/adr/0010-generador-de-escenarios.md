# ADR-0010 — Generador de escenarios: diseño, categorías y cuantización

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 3

## Contexto

No existe dataset público OBD-II con fallos mecánicos reales etiquetados (verificado en el
barrido de Fase 1 y en `docs/fase3/dataset_hcrl_verificacion.md`); la inyección sintética es la
práctica del área. El generador debe ser parametrizable (no casos codificados ad hoc), producir
las tres categorías exigidas por el plan de investigación, y ser él mismo un instrumento
experimental defendible (candidato a contribución C4).

## Decisión

1. **Arquitectura en capas:** `SignalEngine` (dinámica base por tick: perfil de conducción →
   velocidad → rpm/carga/MAF/térmica/mezcla, con correlaciones físicas aproximadas y ruido) ×
   `FaultDef` (transformaciones parametrizadas aplicadas en su ventana de actividad) ×
   `ScenarioSpec` (contrato declarativo con semilla obligatoria). Los escenarios viven en YAML
   (`obd-lab/scenarios/suite_v1.yaml`), no en código.
2. **Tres categorías con semántica experimental** (campo `category` del contrato):
   `normal`; `known_fault` (5 fallos con firma documentada: fuga de vacío, deriva MAF,
   termostato, sonda O2 lenta, misfire — utilizables en ajuste/validación); y `held_out`
   (3 anomalías **multivariables/temporales donde cada PID permanece individualmente en rango**:
   desacoplo MAF↔RPM, dinámica térmica muerta, deriva conjunta MAF↓+avance↑). El cargador de
   suites **rechaza** cualquier suite que use held-out fuera del split `test` (RI1).
3. **La detección no depende de DTCs:** las anomalías se definen sobre la dinámica de señales;
   los DTCs se añadirán como información complementaria del agente, no como etiqueta.
4. **Cuantización J1979 en el camino offline:** toda sesión generada pasa por la ida-y-vuelta
   de codificación OBD (`encoding.quantize`), garantizando que entrenamiento e inferencia viven
   en la MISMA resolución que el adaptador real. *Origen: hallazgo empírico del smoke en vivo —
   sin esto, las std de PIDs casi constantes difieren en un orden de magnitud entre offline y
   vivo, y el detector marca todo como anómalo.*
5. **Un solo formato de sesión** (JSONL: `RecordedSession` + `OBDReading`, en `shared.session_io`)
   para sintético, replay de datasets reales y captura de vehículo.
6. **Definición canónica de features en `shared`** (`mecanico_contracts.features`): la lista y el
   cálculo determinan `ModelManifest.expected_features`, luego son contrato
   entrenamiento↔inferencia, no una utilidad duplicable.

## Emulación en vivo (hallazgos de implementación verificados)

- El emulador re-mezcla siempre `default`+`AT`+escenario y resuelve colisiones por la clave
  `Priority` (menor gana; 10 por defecto): nuestras entradas dinámicas llevan `Priority: 1`.
  Sin esto, las entradas de serie ensombrecen las nuestras y responden valores estáticos.
- La alimentación en vivo usa el dict `answer` actualizado por un hilo a la frecuencia del
  escenario, con el MISMO `iter_ticks` que la generación offline (una sola fuente de dinámica).
- `Elm.terminate()` puede colgarse al parar sesiones repetidas en el mismo proceso: los
  scripts de experimento deben tratar la parada con timeout (deuda menor conocida).

## Alternativas consideradas

- *Modelos físicos de alta fidelidad (GT-Power/Simulink):* fidelidad superior, pero licencias,
  curva de aprendizaje y acoplamiento a herramientas cerradas; desproporcionado para validar
  detección + razonamiento (no simulación de motores). Descartado; declarado como limitación L1.
- *Replay puro de datasets reales con perturbaciones:* excelente realismo de normalidad pero sin
  control causal del fallo (¿qué es ground truth?); se adopta como COMPLEMENTO (calibración y
  validación externa), no como sustituto.
- *Fallos solo vía DTC:* contradice el requisito del plan (detección pre-DTC) y la PI.

## Consecuencias

- La calibración contra HCRL Driving queda como tarea siguiente (mapeo verificado en
  `docs/fase3/dataset_hcrl_verificacion.md`; HCRL carece de MAF y STFT → esos PIDs se calibran
  con literatura técnica y se declara).
- El catálogo de fallos es extensible por definición (`FaultDef`), y su justificación técnica
  (IN-8) debe completarse con citas en la memoria.
