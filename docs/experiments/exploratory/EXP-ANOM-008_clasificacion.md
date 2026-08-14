# EXP-ANOM-008 — Clasificación: EXPLORATORY (F17)

**Decisión del autor (aprobación de F17):** exploratorio bajo el Protocolo ML v1 +
Adenda XAI v1. Sin seeds confirmatorias, sin tocar arms-freeze-v1; LOF participa
exclusivamente como brazo CONGELADO (fs1, train v1.0, umbral 0.163197 — jamás
re-entrenado ni reajustado). **Validez declarada: entorno emulado/sintético** — sin
HCRL (dataset real/replay) ni validación ARM64/RPi5, que son tareas dependientes
registradas APARTE y cuya ausencia no bloquea la fase exploratoria pero sí acota
cualquier conclusión (sin validez externa).

## Inventario de decisiones

**Existían ANTES de ejecutar:**
- Alcance de fs2-lite limitado por la instrucción F17 a las tres candidatas YA
  justificadas (LTFT_session_drift, std multiescala, correlaciones lag-1); prohibido
  promover fs2-lite a esquema canónico antes de resultados.
- Decisión de diseño DECLARADA antes de entrenar: la deriva de sesión SUSTITUYE a los
  absolutos `LONG_FUEL_TRIM_1_mean`/`total_trim_mean` (mantenerlos dejaría la patología
  de EXP-ANOM-007 intacta por construcción); referencia = primeros 120 s de la propia
  sesión (sin leakage entre sesiones; computable en streaming).
- Brazos fijados por la instrucción: {fs1, fs2-lite} × {AE-S, AE-M} + LOF congelado;
  mismo train v1.1, misma normalización, umbral solo-train (ADR-0011); desgloses
  exigidos (FPR por escenario normal; recall por fallo/severidad/duración; fallos foco
  joint_slow_drift, load_coolant_decouple, corr_break_rpm_maf, degradación progresiva).
- XAI como PARTE de la decisión (sin promoción automática si F1 mejora con
  explicaciones inestables); GT parametrizado por esquema congelado antes de medir;
  ≥3 seeds para la comparación.

**Tomadas DURANTE el análisis:**
- Ninguna que afecte al ajuste: umbrales intactos tras ver test; ningún re-entreno tras
  ver resultados; el diagnóstico de la deriva cuantizada se hizo SOBRE los datos ya
  generados (sin regenerar sesiones para «mejorar» el resultado, regla §29).
- Réplica seeds 43/44 ejecutada para los 4 brazos AE (no solo finalistas): la decisión
  de esquema necesita la comparación completa estable.

**Consecuencia de resultados OBSERVADOS:**
- **Esquema de features = KEEP fs1** (fs2-lite NO se promueve; ver comparación).
- D1 = REJECT (tercera vez) · D2 = NEEDS MORE EVIDENCE · D3 = ADOPT confirmado.
- Causa refinada: evento discreto de adaptación del LTFT cuantizado (J1979, paso
  0.7812), raro en train (2/22 sesiones) y legítimo en normales largos de test — un
  problema de contexto TEMPORAL, no de representación estática de ventana.
- Siguiente (directiva F17): EXP-ANOM-009 — modelos temporales (LSTM-AE/GRU-AE,
  HX-ML-3). EXP-PAT-001 NO se abre (D2 ≠ PROMOTE).

## Estado en el registro

- `ai-models/registry/experiments/EXP-ANOM-008.json` (`study_type: exploratory`)
- Artefactos: `e7_results.json` (brazos + seeds + embeddings + XAI comparado),
  `runs.jsonl` (una entrada por brazo), figuras en `docs/fase17/figs/`.
- Informe: [`fs2_lite_ablation_v1`](../../models/comparisons/fs2_lite_ablation_v1.md).
