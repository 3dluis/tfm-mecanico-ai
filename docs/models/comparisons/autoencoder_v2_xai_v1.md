# EXP-ANOM-007 — AE v2 (train v1.1, ablaciones) + primera evaluación XAI formal

**Fase 16 · 2026-08-13 · exploratorio · runner `ai-models/experiments/e6_ae_v2.py` ·
config `exp-anom-007.yaml` · seed 42 (+43/44) · sandbox-x86 (4 CPU / 8 GB, CPU) ·
figuras en [`docs/fase16/figs/`](../../fase16/figs/)**

## 1. Diagnóstico previo de EXP-ANOM-006 (antes de cambiar el modelo)

Reproducción determinista del AE-standard de E5 y disección de sus FP
(`e6_diagnosis.json`):

- **Sin contaminación** (0 ventanas de fallo en train) y **sin overfitting severo**:
  ratio de generalización val/train 1.43, pérdida aún descendiendo suavemente al final.
- **Los FP se concentran por sesión, no uniformemente**: `t-normal-b` (autovía, test)
  FPR 0.271 y `v-normal-a` (urbano, val) 0.186, frente a 0.017–0.068 en las otras dos.
- **Las features de error en los FP son de fuel trim**: total_trim_mean,
  LTFT/STFT (mean/std/slope), O2 — en las 4 sesiones normales con FP.
- **Drift train↔test brutal y localizado**: el shift estandarizado de
  `LONG_FUEL_TRIM_1_mean` es ~10⁷ — el train v1.0 tiene varianza inter-sesión de LTFT
  casi nula, así que cualquier offset de LTFT nuevo cae fuera de la normalidad
  aprendida. Es EXACTAMENTE la insuficiencia de normalidad que F9 midió para eventos
  (ratio entre/intra 1.56 en LTFT de autovía).
- Desbalance operacional del train v1.0: {urban 2, highway 2, idle 1, cold_start 1}.

**Hipótesis de la iteración** (precedente F9): ampliar la normalidad (train v1.1, 22
sesiones) debería corregir el FPR.

## 2. Brazos (60/30, test; un cambio por brazo; umbral 1 % FPR solo-train)

| Brazo | Cambio único | Umbral | F1 | FPR | FPR autovía | FPR urbano | Held-out R | PR-AUC | ROC-AUC | Episodios | Retardo | Params |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ae_s_v10 (ref. E5) | — | 0.3631 | 0.724 | 0.112 | 0.271 | 0.068 | 0.456 | 0.863 | 0.815 | 6/6 | 185.0 s | 4 114 |
| **ae_s_v11** | train v1.1 | 0.3155 | 0.702 | **0.129** | 0.475 | 0.017 | 0.419 | 0.816 | 0.793 | 6/6 | 115.0 s | 4 114 |
| ae_m_v11 | capacidad (64-32, lat. 16) | 0.0463 | **0.754** | 0.168 | 0.508 | 0.034 | **0.563** | 0.850 | 0.851 | 6/6 | 95.0 s | 10 218 |
| ae_s_v11_wd | weight decay 1e-4 | 0.3581 | 0.691 | 0.134 | 0.492 | 0.000 | 0.400 | 0.812 | 0.782 | 4/6 | 22.5 s | 4 114 |
| lof_frozen | NINGUNO (freeze) | 0.163197 | 0.645 | **0.035** | 0.085 | 0.000 | 0.250 | 0.838 | 0.786 | 4/6 | 37.5 s | — |

Seeds 43/44 del candidato: F1 0.699/0.691, FPR 0.138/0.142 — el resultado es estable
entre seeds (no es un artefacto del run). Ventanas del candidato: 10 s F1 0.570/FPR
0.121 · 30 s 0.665/0.131 · 120 s 0.747/0.143 — el FPR persiste en toda la rejilla.
Temporales (candidato): persistencia 0.61, falsa alarma media 290 s (autovía),
retardo 115 s. Recall por duración: todos los episodios de test duran 1 200 s; el
recall intra-episodio distingue mecanismos (corr_break-h 1.0 vs joint_drift 0.025).

**Resultado central (negativo y valioso): el precedente de F9 NO transfiere al AE.**
El train v1.1 diversificó la normalidad y el modelo la reconstruye mejor (umbral baja
0.363→0.315), pero el FPR de autovía EMPEORA (0.27→0.47): los offsets de LTFT de las
sesiones normales de evaluación siguen fuera de lo reconstruible, y con el umbral más
bajo se marcan más. Ni capacidad ni weight decay lo corrigen. La causa no es el
modelo ni los datos: son las **features absolutas de fuel trim** (fs1 representa el
NIVEL de LTFT, que varía legítimamente entre sesiones). La corrección pertenece al
nivel de features (fs2-draft: `LTFT_session_drift`), exactamente la candidata que F9
dejó declarada.

Recall por anomalía (candidato vs LOF congelado): corr_break 0.81 vs 0.50 · maf 0.98
vs 0.95 · vacuum 1.0 vs 1.0 · joint_drift 0.025 vs 0.0 · load_coolant 0.025 vs 0.0.
Severidad (sweep exploratorio): el candidato mantiene el patrón de E5 (episodio de
corr_break detectado a toda severidad; FPR de controles 0.077/0.026).

## 3. Embeddings (D2)

| Modelo | Silhouette entre fallos | (E5: ae_s_v10 = 0.1175) | PCA var. 2c |
|---|---|---|---|
| ae_s_v10 | 0.1175 | referencia | 0.879 |
| ae_s_v11 | 0.1061 | ligeramente peor | 0.915 |
| **ae_m_v11** | **0.2022** | **+72 %** | 0.922 |

La capacidad extra (latente 16) mejora la separación entre mecanismos, pero el espacio
sigue dominado por la dimensión de trims (la misma patología). No se promueve todavía.

## 4. XAI — primera ejecución formal de D3 (Adenda XAI v1)

Configuración registrada: SHAP 0.51.0, `shap.explainers.Permutation` (no Kernel),
función explicada `reconstruction_error(x)`, background = 100 ventanas de train v1.1
normal (determinista, hash `1ddf84d0f336…`), 33 muestras estratificadas
{TP,FN}×fallo + 8 FP + 4 TN, runtime 9.1 s.

**Fidelidad contra el ground truth sintético** (media sobre TP; azar = baseline
hipergeométrico de la adenda):

| Fallo | n | \|GT\| | AR@1 | AR@3 | AR@5 | Azar@K | P@1/P@3/P@5 |
|---|---|---|---|---|---|---|---|
| vacuum_leak | 4 | 16 | **1.00** | **1.00** | **1.00** | 0.38 | 1.0/1.0/1.0 |
| maf_drift | 4 | 12 | **1.00** | **1.00** | **0.85** | 0.29 | 1.0/1.0/0.85 |
| corr_break_rpm_maf | 4 | 10 | **1.00** | 0.67 | 0.70 | 0.24 | 1.0/0.67/0.70 |
| joint_slow_drift | 1 | 8 | 1.00 | 0.33 | 0.20 | 0.19 | (n=1) |
| load_coolant_decouple | 1 | 8 | 0.00 | 0.00 | 0.20 | 0.19 | (n=1) |

HX-XAI-1 **soportada** en los fallos bien detectados (≫ azar); en los apenas
detectados la atribución queda ≈ azar — coherente: no hay señal aprendida que atribuir.
HX-XAI-3 soportada en corr_break (masa distribuida en el conjunto relacional).

**Agreement SHAP ↔ per-feature error**: Jaccard@5 medio 0.419 — 7 AGREE, 13
PARTIAL_AGREEMENT, 2 DISAGREE (ejemplos concretos conservados en `e6_results.json`).
**Estabilidad**: entre seeds 0.595, ante perturbación (0.05·std) 0.683 — moderada
(HX-XAI-2 parcialmente soportada). **Global**: el top-5 de mean|SHAP| son las cinco
features de fuel trim — la firma de la patología del FPR. **FP explicados**: 7/8
dominados por LTFT_mean/slope/std y total_trim — **SHAP diagnosticó la causa del FPR
de forma independiente y coincidente con el diagnóstico §1**; este es el caso de uso
«SHAP como diagnóstico del modelo» de la adenda §3 funcionando de extremo a extremo.

**Contrafactual** (sev-corrbreak-high vs gemelo sin fallo, mismo seed): ventanas
pre-fallo **byte a byte idénticas** (gemelo válido); score medio post-inyección 0.886
vs 0.129 del gemelo; la atribución del par vira de {RPM_std, STFT_mean} (gemelo) a
{corr_ENGINE_LOAD_MAF, corr_RPM_SPEED, …} (fallo). Caveat declarado: gemelo exacto
solo pre-fallo (el generador comparte rng con la inyección).

**Sonda de fingerprint sintético**: el perfil de atribución en ventanas normales
difiere fuertemente entre escenarios (cos 0.05 urbano↔autovía) — consistente con la
patología de trims más que con huella del generador; sin datos reales aún no es
separable; se conserva como resultado y se re-evaluará con replay real.

## 5. Decisiones

- **D1 — AE como detector: REJECT.** Ningún brazo respeta el FPR de LOF; la mejora
  barata precedentada (v1.1) empeoró el FPR y el mecanismo está identificado con
  precisión. No se maquilla: el resultado negativo queda registrado con causa.
- **D2 — representación: NEEDS MORE EVIDENCE.** Mejora real con capacidad (0.20 vs
  0.12) pero insuficiente y contaminada por la misma patología; se re-evalúa tras la
  corrección de features.
- **D3 — SHAP/XAI: ADOPT** como mecanismo de evaluación, diagnóstico y evidencia
  estructurada (NO como decisión automática): fidelidad ≫ azar donde hay señal,
  agreement parcial informativo, estabilidad moderada declarada, coste trivial y valor
  demostrado (identificó la causa del FPR). Limitaciones vigentes: atribución repartida
  entre trims correlacionados (adenda §13), n bajo en fallos apenas detectados.

## 6. Limitaciones

Una seed por brazo de ablation (3 solo en el candidato); n=1 en la fidelidad de los
fallos casi indetectados; entorno emulado (fingerprint no separable de la patología);
retardos promediados sobre pocos episodios; sin export ONNX ni medición ARM64 (D1 =
REJECT: no hay candidato edge); Precision@K solo donde |GT| ≥ K (definición congelada).

## 7. Próximo experimento recomendado

**EXP-ANOM-008 — ablation de features fs2-lite vs fs1** (`LTFT_session_drift` +
std multiescala + correlaciones lag-1, las tres candidatas YA declaradas en fs2-draft
con justificación previa): es la corrección al nivel donde vive la causa, respaldada
por dos diagnósticos independientes (per-feature error §1 y SHAP §4), y a la vez la vía
de mejora de D2 (un espacio latente sin la dimensión espuria de offsets). Los modelos
secuenciales siguen pospuestos: la patología identificada no es de orden temporal.
fs2 NO se promueve a contrato: la ablation se ejecuta en ai-models y solo con evidencia
se propondría la promoción (Protocolo §4, regla §14 de la instrucción de fase).
