# EXP-ANOM-005 — Clasificación: EXPLORATORY (validación de infraestructura, F13)

**Decisión del autor (apertura de la línea ML, F13):** experimento exploratorio. No
produce evidencia confirmatoria ni toca semillas reservadas, brazos congelados o held-out
del pre-registro; su objeto es la VALIDEZ DEL CAMINO DE DATOS, no la selección de modelos.

## Inventario de decisiones

**Existían ANTES de ejecutar:**
- Protocolo de evaluación ADR-0011 (umbral 1 % FPR solo-train, sin point-adjustment,
  episodios, held-out intocable) — congelado desde F3.
- Dataset obd-lab-suite-v1@1, split suite-v1-split-1, features fs1 (42), ventana 60/30,
  seed 42 — todos congelados en arms-freeze-v1.
- Los 4 detectores y sus hiperparámetros (make_baselines, idénticos a EXP-ANOM-001).
- Criterio de éxito pre-declarado (config exp-anom-005.yaml): paridad EXACTA de features,
  etiquetas, offsets, métricas y umbrales entre camino long (referencia) y wide (candidato).

**Tomadas DURANTE el análisis:**
- Ninguna: el experimento es binario (paridad sí/no) y se cumplió en la primera ejecución.

**Consecuencia de resultados OBSERVADOS:**
- El snapshot wide queda VALIDADO como entrada canónica para ML (condición de migración
  gradual de ADR-0025 satisfecha para el consumidor ML); los experimentos EXP-ANOM-006+
  y EXP-PAT-* se construirán sobre el camino wide.

## Estado en el registro

- `ai-models/registry/experiments/EXP-ANOM-005.json` (`study_type: exploratory`)
- Artefactos: `ai-models/experiments/e4_parity.json`, `e4_results.csv`, `runs.jsonl`
- Informe: `docs/models/comparisons/wide_path_parity_v1.md`
