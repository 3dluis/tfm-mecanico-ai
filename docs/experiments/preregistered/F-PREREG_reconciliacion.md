# F-PREREG — Reconciliación de los pre-registros

**16 de agosto de 2026 · pasos 1 y 2 de [F-PREREG](F-PREREG_tarea.md) · el tag
`prereg-v1.0` NO se ha creado y no se creará sin aprobación explícita.**

## 0. Inventario: qué documentos tienen pretensión de pre-registro

| Documento | Alcance | Estado declarado | ¿Vincula hoy? |
|---|---|---|---|
| **A** — [`preregistered/PROTO-CONF-001.md`](PROTO-CONF-001.md) | Solo **H-EVT** | PRE-REGISTRADO, no ejecutado | Sí, pero solo para H-EVT |
| **B** — [`pre-registro-v1.md`](../pre-registro-v1.md) | **Seis familias** + criterio edge | v1.0-rc1 PROPUESTO; «hasta entonces este documento no vincula» | **No** |
| `preregistered/r2_artefactos.md` | Artefactos de R2 (smoke del SLM) | Instrumental | No es pre-registro de hipótesis |
| `protocolo_ml_v1.md` + 2 adendas XAI | Línea **exploratoria** ML | Protocolo, no pre-registro confirmatorio | No para lo confirmatorio |
| `ai-models/configs/exp-anom-*.yaml` (11) | Pre-especificación **por experimento** | Congeladas antes de cada ejecución | Sí, cada una para su experimento **exploratorio** |

Los dos últimos grupos **no compiten** con A y B: gobiernan la línea exploratoria y quedan
fuera de esta reconciliación salvo por una consecuencia, la del elemento §1.14.

---

## 1. Tabla de reconciliación

> **A** = PROTO-CONF-001 · **B** = pre-registro-v1 · «Estado actual» = lo que el proyecto ha
> hecho realmente a 16-08-2026.

| # | Elemento | Pre-registro A | Pre-registro B | Estado actual del proyecto | Propuesta canónica | Justificación |
|---|---|---|---|---|---|---|
| 1.1 | **Pregunta de investigación** | No la enuncia; deriva una pregunta experimental para H-EVT (PI.2) | **PI Opción B:** ¿puede un sistema híbrido descubrir y explicar patrones de fallo no documentados mediante análisis contextual y longitudinal de OBD-II? Con precisión terminológica de «no documentado» | La documentación viva (docs/01, docs/02) usa la PI Opción B | **B** | A no enuncia PI; no hay conflicto real, solo cobertura desigual |
| 1.2 | **Familias de hipótesis** | H-EVT únicamente (C1 principal, C2 secundaria, C3 calidad del brazo) | H-MAIN, H-EVT, H-MEM, H-MAS (secundaria), H-PERS, H-EXP + criterio edge transversal | Ninguna familia confirmatoria ejecutada | **B**, absorbiendo H-EVT de A | B cubre A; A no cubre B. Ninguna se ha ejecutado ⇒ coste de cambio nulo |
| 1.3 | **Mapeo H1/H2/H3/H4** | No lo trata | H4 → **criterio transversal edge**, deja de ser hipótesis. Las demás vía `correspondencia_nomenclatura.md` | `correspondencia_nomenclatura.md` (en `main`): H1 → **precondición de H-EVT**; H2 → integrada en **H-EXP**; H3 → subsumida en **H-MEM**; H4 → criterio edge | **B** + la tabla de correspondencia | Es la nomenclatura ya vigente en `main`. **Ver aviso §2.1: cerrar «H1 exploratorio» NO cierra H-EVT** |
| 1.4 | **Dataset confirmatorio** | `suite_conf_v1.yaml`: 15 sesiones nuevas, oculto hasta ejecutar | `obd-lab-suite-v2`: **R = 10 réplicas** de la estructura v1 con normalidad de train ampliada (22 train / 7 val / 8 test por réplica) | **Ninguno de los dos se ha generado.** Existen v1, v2 y v3, todos exploratorios y congelados por hash | **B**, *con la enmienda de cobertura efectiva del §2.2* | 40 episodios held-out frente a 5: más potencia. Pero su composición actual arrastra un confound medido (§2.2) |
| 1.5 | **Splits** | development / exploratory (gastado) / confirmatory | train = solo normal; validation = normal + fallos conocidos; test = control FP + fallos conocidos con semillas nuevas + held-out | La estructura de splits de v1 se ha respetado en las 22 fases; el test histórico nunca se ha tocado | **B** (idéntica a A en estructura) | No hay conflicto: A y B describen la misma anti-circularidad |
| 1.6 | **Clases held-out** | Relacional replicado en ambos perfiles + `coolfreeze` y `jointdrift` como test de techo | **3 congeladas:** `corr_break_rpm_maf`, `load_coolant_decouple`, `joint_slow_drift` | Las mismas 3. `joint_slow_drift` y `load_coolant_decouple` siguen en recall **0.000** en toda la serie exploratoria | **B** | Coinciden. El recall 0.000 es un hallazgo exploratorio robusto que la fase confirmatoria debe esperar, no ignorar |
| 1.7 | **Semillas** | **901–925** (confirmatorias ocultas) | Bloques **11000–20036** (réplica r → `[10000+1000r, +999]`); runner 42; `cases_v2` 30000–30039 | **Ambos bloques intactos.** La regla vigente reserva 901-925, 11000-20036, 30000-30079, 55000, 111000+ y se ha respetado en las 22 fases | **B como principal**, conservando 901-925 reservadas | Ninguna semilla se ha gastado por ninguna vía ⇒ ambas opciones siguen disponibles |
| 1.8 | **Brazos de H-EVT** | AM-W · AM-E-v0.2.0 · AM-WE-d (3) | E0 · E1 · E3 · E4 (condicionado a D2) · W∨E (5). **E2 excluido** por decisión pre-registrada | Ninguno ejecutado en modo confirmatorio | **B** | Superconjunto de A: E1 = AM-W, E3 ≈ AM-E, W∨E = AM-WE-d, y añade referencia inferior E0 |
| 1.9 | **Umbrales de los modelos** | **Congelados con checksum:** LOF 0.163197; eventos 57.496; `arms-freeze-v1.json` con sha256 por fichero | Mismos modelos (`anom-lof@0.1.0`, `event-baseline-z@0.2.0`, AM-WE-d) pero **sin manifiesto de checksums** | El umbral **0.163197 se ha reproducido exactamente** en F18, F21 y F22, en dos plataformas distintas | **B + el manifiesto de checksums de A** | Es la aportación exclusiva de A y ha demostrado su utilidad: es el control P4 que valida 22 fases de comparabilidad |
| 1.10 | **Métricas primarias** | FPR tick-level; recall de episodios held-out relacionales; recall tick agregado | (P1) FPR por tick condicionado a recall ≥ E1; (P2) recall de episodios held-out. Co-primarias declaradas | La serie exploratoria usa F1/FPR/recall por ventana y por evento, sin *point adjustment* | **B** | Formaliza las co-primarias y su condicionamiento; A no lo hace |
| 1.11 | **Umbrales de éxito** | C1: ≥ episodios held-out que AM-W con FPR ≤ +0.02 **absoluto**; C3: FPR eventos ≤ 0.02 y precisión de evento ≥ 0.90 | FPR **≥ 30 % relativo** menor con recall ≥, **o** recall held-out **≥ 0.15 absoluto** mayor, sin violar el presupuesto edge | Sin equivalente confirmatorio. En exploratorio, D1 exige FPR ≤ 0.03 y F1 ≥ 0.70 | **B**, conservando C3 de A como criterio de calidad del brazo de eventos | Son criterios distintos, no contradictorios: B mide la mejora, C3 de A protege contra un brazo de eventos degenerado |
| 1.12 | **Criterios de refutación** | Refutación parcial/total se documenta igual; sin promoción a VALIDATED | Refutación cuando el IC 95 % excluye el umbral mínimo en la dirección hipotetizada; el resto **no concluyente** y se reporta como tal | La política de resultados negativos se ha aplicado en F17, F18, F21 sin excepción | **B** | B distingue tres estados (acepta / refuta / no concluyente); A solo dos |
| 1.13 | **Análisis estadístico** | Recuento e IC exactos (Clopper-Pearson). **Sin tests de significación** sobre 5 episodios; la limitación se declara | α = 0.05 unilateral; Wilcoxon pareado; **Holm dentro de cada familia** (H-EVT: 4 contrastes); efecto + IC bootstrap BCa; δ de Cliff; sin paradas opcionales ni repesca | La serie exploratoria reporta mediana y dispersión multi-semilla, sin inferencia | **B** | Con 40 episodios el test es posible; con 5 no lo era. La honestidad de A sobre su falta de potencia es lo que justifica adoptar el diseño de B |
| 1.14 | **Evidencia exploratoria previa** | No la enumera | §11 lista EXP-ANOM-001/002/003 y fija su límite de uso | **Incompleta:** faltan EXP-ANOM-005…010-R2 y AUDIT-DATA-001, todos exploratorios | **B, con §11 actualizada** antes de congelar | Congelar con §11 incompleta dejaría fuera del registro 8 experimentos exploratorios que **sí** informaron decisiones de diseño |
| 1.15 | **Reglas confirmatorias** | Una sola ejecución; re-ejecución íntegra solo por fallo técnico; desviaciones registradas con timestamp | Congelación previa; held-out intocable; umbrales solo con train; sin exclusiones silenciosas; equidad entre brazos; evidencia exploratoria separada; benchmark inmutable | Se han respetado de facto en las 22 fases (P4 lo demuestra) | **B**, incorporando de A la verificación sha256 previa a ejecutar | B es más completo; A aporta el mecanismo de comprobación |
| 1.16 | **Criterio edge** | No lo trata (menciona que EDGE_APPROVED requiere matriz ARM64 aparte) | **Presupuesto fijado a priori:** detección ≤ 5 s/sesión y ≤ 512 MB; SLM ≤ 3.5 GB, ≥ 3 tok/s, TTFT ≤ 15 s; agente p95 ≤ 120 s con ≤ 10 % de abortos; sistema ≤ 6 GB | **Nada medido en ARM64.** Y `peak_rss_mb()` es incorrecto fuera de Linux (hallazgo F22): infla ×1024 | **B**, *bloqueado por la corrección de `peak_rss_mb()`* | Un presupuesto de RAM no puede verificarse con un instrumento que mide mal la RAM |
| 1.17 | **Parámetros diferidos** | Ninguno declarado | **D1** (SLM definitivo, tras el smoke R2) · **D1b** (modelo juez) · **D2** (perfiles de vehículo) | **R2 preparado desde F9 y nunca ejecutado** ⇒ D1 sin fijar ⇒ EXP-MEM-001, EXP-EXP-001, EXP-MAS-001 y EXP-MAIN-001 bloqueados | **B** | Hace explícito el bloqueante real del programa agéntico |
| 1.18 | **Promoción de modelos** | Si se confirma: CANDIDATE → VALIDATED, con aprobación final del autor | Aceptación por familia según §8 | F22 dejó el AE denso en **`PROMOTE_CANDIDATE` = CANDIDATE FOR PROMOTION**, explícitamente **no adopción** | **B** + la regla de aprobación del autor de A | El estado actual del AE es exploratorio: no entra en la cadena de promoción confirmatoria sin pasar por ella |

---

## 2. Contradicciones que impiden congelar hoy

### 2.1 «H1 cerrada» no significa «H-EVT resuelta» — riesgo de confusión en la memoria

F22 cerró **H1 exploratorio** con estado `SUPPORTED` (`HX-ML-5`). En la nomenclatura vigente,
H1 es **precondición de H-EVT**, no H-EVT. La familia confirmatoria H-EVT —¿aporta el
contexto por eventos frente a ventanas?— **no se ha tocado**: sus brazos E0/E1/E3/E4/W∨E
nunca se han ejecutado en modo confirmatorio.

**Riesgo concreto:** que la memoria presente el resultado de F22 como si respondiera a H-EVT.
No lo hace. Son preguntas distintas —«¿basta con cubrir la normalidad?» frente a «¿aporta el
evento como contexto?»— y solo la primera tiene respuesta.

### 2.2 El banco confirmatorio de B reproduciría el fallo de cobertura que F22 acaba de diagnosticar

Éste es el hallazgo de mayor consecuencia de esta reconciliación, y es **nuevo**: no podía
detectarse cuando se redactó B, el 12 de agosto.

B especifica que cada réplica de `suite-v2` lleva 22 sesiones de train «replicando la
composición del train total v1.1». Medido:

| Dato | Valor | Fuente |
|---|---|---|
| Duraciones de la composición v1 + train_ext | **1 200 s (×4), 1 500 s (×8), 1 800 s (×25)** | `suite_v1.yaml`, `suite_v1_train_ext.yaml` |
| Cobertura efectiva de LTFT de train v1.1 | `positive_level_share` = **0.0000** | `e12_benchmark_v3.json` (F22) |
| P(sesión con nivel positivo sostenido) a 1 800 s | **0.0512** | sonda del mecanismo, F21 |

Con 22 sesiones de ≈1 800 s por réplica, el número esperado de sesiones con nivel positivo de
LTFT es ≈ 1,1 y **P(ninguna) ≈ 0,32**. Es decir: **aproximadamente una de cada tres réplicas
tendría cobertura efectiva nula en la dimensión que F22 demostró que domina el FPR**, y las
demás tendrían una o dos sesiones.

La consecuencia es grave para el diseño estadístico de B: la réplica es **la unidad
experimental** del Wilcoxon pareado (n = 10). Introducir varianza no controlada, entre
réplicas, justo en la variable que gobierna la métrica primaria (FPR), contamina el contraste
principal de H-EVT.

> B ya intuía el problema —cita el piloto EXP-ANOM-003 y que «2 sesiones/perfil son
> insuficientes para representar la deriva LTFT entre sesiones»— pero lo resolvió **contando
> sesiones**, que es exactamente el instrumento que F20 usó y F21 refutó. La corrección de
> F22 es medir en el espacio de features.

**Enmienda necesaria antes de congelar:** el train de cada réplica de `suite-v2` debe
satisfacer el criterio de cobertura efectiva (`positive_level_share ≥ 0.03` y
`negative_level_share ≥ 0.03` sobre sus ventanas, verificado con
`ai_models.audit.coverage`), lo que exige sesiones más largas —del orden de 5 400 s— o un
número mayor de ellas. Sin esta enmienda, el confirmatorio de H-EVT nace con un confound
medido y conocido.

### 2.3 Dos datasets confirmatorios distintos para la misma hipótesis

A oculta `suite_conf_v1` (15 sesiones, semillas 901-925); B genera `suite-v2` (10 réplicas,
semillas 11000-20036). **Ninguno existe todavía** y ambos bloques de semillas siguen
intactos, así que la elección es libre y sin coste. Se propone B por potencia (40 episodios
frente a 5), conservando 901-925 reservadas por si se quisiera una réplica independiente.

### 2.4 El registro de evidencia exploratoria está incompleto

§11 de B recoge tres experimentos; se han ejecutado once más. Congelar así dejaría fuera del
pre-registro los pilotos que **de hecho** motivaron el diseño actual, incluidos F19 (la
auditoría del banco), F21 (la refutación de la cobertura declarada) y F22 (el criterio de
cobertura efectiva). Debe completarse, manteniendo su límite de uso: **evidencia exploratoria,
nunca confirmatoria, nunca meta-analizada con ella**.

### 2.5 El criterio edge no es verificable con la instrumentación actual

B fija un presupuesto de RAM (≤ 512 MB de detección, ≤ 6 GB de sistema). F22 detectó que
`peak_rss_mb()` asume `ru_maxrss` en KB, cierto en Linux y falso en macOS, donde son bytes:
las cifras salen infladas ×1024. Hay que corregirlo **antes** de que ninguna medición de
presupuesto entre en un registro confirmatorio.

---

## 3. Propuesta canónica, en una frase

**Adoptar `pre-registro-v1.md` como pre-registro maestro**, incorporándole (i) el manifiesto
de congelación por checksums y la verificación sha256 previa de `PROTO-CONF-001`, (ii) su
criterio C3 de calidad del brazo de eventos, y (iii) **tres enmiendas obligatorias antes de
congelar**: cobertura efectiva del banco confirmatorio (§2.2), actualización del registro de
evidencia exploratoria (§2.4) y corrección de la instrumentación de memoria (§2.5).
`PROTO-CONF-001` queda **superseded**, no borrado, según la regla de ADRs del repositorio.

## 4. Qué falta para poder congelar

| # | Acción | Bloquea el tag |
|---|---|---|
| 1 | Aprobar la propuesta canónica de §3 | Sí |
| 2 | Redactar la enmienda de cobertura efectiva del banco confirmatorio (§2.2) | Sí |
| 3 | Completar §11 con los once experimentos exploratorios posteriores (§2.4) | Sí |
| 4 | Corregir `peak_rss_mb()` fuera de Linux (§2.5) | Sí, para el criterio edge |
| 5 | Marcar `PROTO-CONF-001` como superseded conservando su manifiesto | Sí |
| 6 | Decidir si se conserva 901-925 como réplica independiente o se libera | No |
| 7 | Ejecutar R2 para fijar D1 | No para el tag; sí para los confirmatorios agénticos |

**El tag `prereg-v1.0` no se crea hasta que apruebes §3 y estén hechas las acciones 2-5.**
No debe congelarse un documento que todavía contiene las contradicciones de §2.
