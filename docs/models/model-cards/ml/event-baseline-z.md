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

## Métricas (EXP-ANOM-002, suite v1, marco por tick — evaluación formal)
- Test: F1 0.58 · FPR 0.149 · episodios 4/6 · held-out 2/4 · retardo medio 177 s
- NO sustituye a LOF-ventana (F1 0.67/FPR 0.067); SÍ aporta señal complementaria:
  held-out relacional urbano R=0.73 (LOF 0.25) con retardo 17 s; la ablación confirma
  la aportación del context_signature (F1 0.58 vs 0.52 sin contexto; held-out 2/4 vs 1/4)
- FPR concentrado en normales de autovía (0.41–0.52): 2 sesiones train/perfil no bastan
- Cobertura: 87.7 % de eventos con baseline aplicable (111/902 sin puntuar, honesto)
- Detalle: [comparación v1](../../comparisons/anomaly_window_vs_event_v1.md)

## Limitaciones y modos de fallo (✍)
- Evaluado formalmente en EXP-ANOM-002 (arriba); pierde thermostat_stuck (contextos fríos
  sin baseline) y misfire (firma de alta frecuencia diluida por medias por evento).
- Baselines inmaduros (n<5) no detectan: vehículo nuevo = periodo ciego por contexto.
- Fragmentación de contextos si las bandas se afinan (mitigación: bandas anchas v1).
- z univariante por feature: anomalías RELACIONALES dentro del evento (correlaciones
  rotas con features individuales normales) pueden escapar — la extensión natural es un
  detector multivariable POR CONTEXTO (candidato futuro).
- Riesgo de contaminación del baseline si acumula eventos anómalos no filtrados
  (política de actualización pendiente de diseño fino).
- **Unsupported:** diagnóstico del fallo (señala desviación contextual, no causa).
