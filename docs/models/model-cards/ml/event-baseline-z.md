# Model Card — event-baseline-z (anomalía contextual por evento)

**Fuente:** informe F6 §3 · tests-integration/test_event_slice.py · ADR-0021.

## Identificación
- **model_id:** `event-baseline-z` · **version:** 0.1.0 · **status: CANDIDATE**
- **model_type:** ml (familia zscore_contextual) · **purpose:** detectar eventos
  anómalos PARA UN VEHÍCULO EN UN CONTEXTO comparando su EventFeatureVector contra el
  EventBaseline del mismo `context_signature` (anomaly_scope=EVENT)
- **owner:** `diagnostic-agent:events.baseline`

## Origen y configuración
- **algorithm:** z-score robusto por feature contra distribución acumulada
  (mean/std/percentiles) con suelo de σ = max(std, 0.05·|mean|, 1e-3); anomalía si
  max|z| ≥ 4.0 (umbral inicial, a calibrar) y sample_count ≥ 5
- **features:** `efv:1` (20 features de evento) · **preprocessing:** pp:1
- **baseline:** por (vehicle_id, event_type, context_signature); versionado, auditable

## Métricas (slice F6 — evidencia preliminar, NO experimento formal)
- Baseline: 30 aceleraciones normales comparables (6 semillas, contexto
  `ACCELERATION|0-40|warm|d8-30s`)
- Held-out normal (semilla 99): **0/5 falsas alarmas**
- Trip con maf_drift (drift 0.25): **5/6 aceleraciones señaladas**; firma correcta
  (ltft_mean, total_trim_mean, stft_mean); el fallo omitido cae en la rampa inicial

## Limitaciones y modos de fallo (✍)
- Evidencia de UN escenario de fallo (maf_drift) y UN contexto: NO generalizar hasta el
  experimento ventana-vs-evento (E1/R1).
- Baselines inmaduros (n<5) no detectan: vehículo nuevo = periodo ciego por contexto.
- Fragmentación de contextos si las bandas se afinan (mitigación: bandas anchas v1).
- z univariante por feature: anomalías RELACIONALES dentro del evento (correlaciones
  rotas con features individuales normales) pueden escapar — la extensión natural es un
  detector multivariable POR CONTEXTO (candidato futuro).
- Riesgo de contaminación del baseline si acumula eventos anómalos no filtrados
  (política de actualización pendiente de diseño fino).
- **Unsupported:** diagnóstico del fallo (señala desviación contextual, no causa).
