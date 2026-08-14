# Adenda XAI — extensión temporal (F18)

**Estado: VIGENTE para trabajo EXPLORATORIO · 2026-08-14 · extiende la
[Adenda XAI v1](protocolo_ml_v1_adenda_xai.md) (ADR-0033) sin sustituirla ni modificar
sus definiciones · CONGELADA ANTES de ejecutar EXP-ANOM-009**

La Adenda XAI v1 §19 dejó declarado el nivel 3 («feature×tiempo en roadmap») como
alcance futuro. EXP-ANOM-009 introduce modelos secuenciales (LSTM-AE / GRU-AE) sobre
secuencias crudas `[T × PID]`, y con ellos la atribución deja de ser un vector por
ventana para pasar a ser una **matriz**. Este documento fija ese nivel ANTES de ver
resultados; las métricas nuevas no se inventan a posteriori (regla del autor, F18).

## 1. Representación canónica (no colapsable)

La salida base de la explicación es la matriz

```
A[t, f]      t ∈ {0 … T-1} pasos de la secuencia
             f ∈ PIDs canónicos (en el nivel secuencial las features SON las señales)
```

Los agregados **se derivan** de `A`, nunca la sustituyen:

| Vista derivada | Definición | Pregunta que responde |
|---|---|---|
| Atribución por feature | `a_f = Σ_t \|A[t,f]\|` | ¿qué señal? |
| Atribución por instante | `a_t = Σ_f \|A[t,f]\|` | ¿cuándo? |
| Ranking de celdas | Top-K `(t,f)` por `\|A[t,f]\|` | ¿qué combinación señal-momento? |

Implementación: `ai_models.xai.temporal` (agregados, rankings, GT y métricas).

## 2. Ground truth temporal (solo datos SIMULATED)

Se amplía el GT de la adenda §7 con la dimensión que el escenario ya declara:

```
injected_features       PIDs afectados = FAULT_AFFECTED_PIDS[fault]  (congelado en F16)
anomaly_start / end     [fault_start_s, fault_end_s) del ScenarioSpec
affected_relationships  pares de señales de los fallos relacionales (informativo)
```

Un paso `t` de una secuencia que empieza en `sequence_start_s` pertenece a `GT_t` si
`sequence_start_s + t/sample_rate_hz ∈ [fault_start_s, fault_end_s)`. Si la secuencia es
íntegramente anterior al fallo, `GT_t = ∅` y las métricas temporales **no están
definidas** para ella (se excluye explícitamente, no se puntúa como 0).

## 3. Métricas (congeladas)

Las tres comparten la forma del baseline aleatorio hipergeométrico ya congelado en la
adenda §8 (`random_recall_baseline(n, |GT|, K)`): ningún valor es interpretable sin él.

| Métrica | Definición | `n` del azar |
|---|---|---|
| **FAR@K** (Feature Attribution Recall) | `\|GT_f ∩ TopK_f\| / min(\|GT_f\|, K)` sobre `a_f` | `n_features` |
| **TAR@K** (Temporal Attribution Recall) | `\|GT_t ∩ TopK_t\| / min(\|GT_t\|, K)` sobre `a_t` | `n_steps` |
| **FTH@K** (Feature-Time Hit) | celdas Top-K dentro de `GT_f × GT_t`, `/ min(\|GT_f\|·\|GT_t\|, K)` | `n_steps · n_features` |

K ∈ {1, 3, 5} para FAR (como AR@K); para TAR y FTH se declara K por experimento en la
config **antes** de medir (EXP-ANOM-009: K ∈ {5, 10, 20}, elegido por el tamaño típico
de `GT_t` en las secuencias con fallo, no por los resultados).

**Estabilidad**: Jaccard@K medio entre los Top-K de **celdas** de matrices equivalentes
(seeds distintas; entrada perturbada con σ = 0.05·std por feature, semilla fija) —
`cell_stability_jaccard`. Es más exigente que la estabilidad de features de la adenda
§10: dos explicaciones pueden coincidir en «qué señal» y discrepar en «cuándo».

**Agreement**: se compara `A[t,f]` con el error de reconstrucción temporal
`error[t][f]` del propio modelo, con Jaccard@K de celdas y las clases cualitativas ya
definidas (AGREE ≥ 0.6 · PARTIAL 0.2–0.6 · DISAGREE < 0.2). La discrepancia no se trata
como error automático (adenda §9).

## 4. Reglas que NO cambian

- `atribución XAI ≠ causalidad mecánica ≠ diagnóstico confirmado` (adenda §1, ADR-0033).
- La función explicada se declara siempre y de forma explícita
  (`f(sequence) = reconstruction_error(sequence)`); jamás se explican estados internos
  de las celdas recurrentes.
- Background EXCLUSIVAMENTE de train normal, selección determinista y hasheada.
- El explainer **no se fija de antemano**: se comprueba compatibilidad real con los
  modelos recurrentes de PyTorch y se registra `shap_version`, `explainer`,
  `explained_function`, `background`, `background_hash`, `samples`, `runtime`.
- XAI es offline: nunca en el camino de inferencia del edge.

## 5. Reparto de atribución en modelos temporales (limitación declarada)

En secuencias, la atribución puede repartirse **entre features y entre pasos** a la vez.
Dos consecuencias que se asumen antes de medir:

1. Un FTH@K moderado con FAR@K alto es compatible con una explicación correcta cuya
   masa temporal está distribuida (p. ej. drift lento): no se interpreta como fallo.
2. En anomalías relacionales, la señal «culpable» puede ser cualquiera de las dos de la
   relación; el GT es un conjunto y así se evalúa (adenda §7).

## 5.bis Dominio de aplicabilidad de TAR@K (adición F19, tras EXP-ANOM-009)

**TAR@K solo discrimina si la anomalía ocupa una FRACCIÓN de la ventana.** Si el
intervalo inyectado cubre la secuencia entera, `GT_t` = todos los pasos, el baseline
aleatorio vale 1.0 y la métrica deja de informar: un TAR@K de 1.0 en ese caso no dice
nada sobre la calidad de la localización temporal. Verificado empíricamente en
EXP-ANOM-009 (TAR@10 = 1.000 con azar = 1.000 en los tres fallos explicados).

Regla: **la métrica no se elimina; se declara su dominio.** TAR@K se reporta solo cuando
`|GT_t| / n_steps ≤ 0.5`; en caso contrario se marca `NO APLICABLE (GT temporal satura la
ventana)` y la evaluación temporal se apoya en FTH@K, que sí conserva discriminación
porque su espacio de celdas incluye la dimensión de features.

Corolario para el diseño experimental: para evaluar localización temporal hacen falta
escenarios con fallos **cortos respecto a la ventana** (o ventanas más largas que el
episodio). Es un requisito de diseño de datos, no del explicador.

## 5.ter Separación XAI-feature / XAI-time (adición F19)

Las dos dimensiones de la matriz `A[t,f]` tienen madurez distinta y **se decide sobre
ellas por separado**:

| Dimensión | Estado (F18/F19) | Uso admitido |
|---|---|---|
| **XAI-feature** (`Σ_t |A[t,f]|`) | por encima del azar y estable (0.61–0.81 entre seeds y bajo perturbación) | evidencia y diagnóstico, como en F16 |
| **XAI-time** (`Σ_f |A[t,f]|`, celdas) | localización **no fiable**: dos variantes de SHAP coinciden en solo 0.14–0.26 de sus Top-K celdas | exploratorio; no sustenta decisiones |

Una decisión D3 puede por tanto ser ADOPT en el nivel de feature y NEEDS MORE EVIDENCE
en el nivel de celda simultáneamente, y así debe declararse.

## 6. Riesgo añadido

| Riesgo | Mitigación |
|---|---|
| coste computacional de la atribución `T×F` | muestreo estratificado reducido + registro de runtime; si el explainer exacto es inviable se documenta y se usa la variante soportada, declarándolo |
| sobreinterpretación del «cuándo» | TAR@K siempre junto a su azar; secuencias sin `GT_t` excluidas, no puntuadas |
| estabilidad temporal frágil | `cell_stability_jaccard` obligatorio; explicación inestable = motivo legítimo de no-promoción (adenda §14) |
