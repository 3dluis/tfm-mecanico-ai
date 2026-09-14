# Resultado de RERUN-A: reejecución canónica tras MIXED-EMBEDDING-SPACE

**Fecha de ejecución:** 13 y 14 de septiembre de 2026 · **Commit del código:** `e93dda9`
(pasos B, D, F, G) y `487e98a` (paso I) · **Pre-registro:** `docs/methodology/preregistro-rerun-a.md`
(con ENM-S01, S02 y S03), congelado el 4-09-2026 · **Manifiesto:** `configs/manifest_rerun_a.json`
v1.3.0 · **Plan:** `docs/methodology/plan-reejecucion-canonica.md`.

**Lo que no se tocó:** ni el pre-registro, ni el manifiesto, ni el verificador (v2.1), ni el
umbral (0,79), ni el conjunto (`synthetic_v2`, semilla 20260901), ni el índice (2 × 6 158
vectores, ambos en `mps`, comprobado antes de medir). Los artefactos anteriores siguen en
`experiments/pre_mixed_embedding_fix/` y no se sobrescribieron. La comparación es
**descriptiva**, como exige el pre-registro §8: ningún valor p, ningún intervalo.

## Pregunta y respuesta corta

> ¿Modifica la corrección del espacio de embeddings la evidencia que llega al agente y las
> decisiones que toma, sobre exactamente el mismo conjunto, modelo, umbral y política?

**La evidencia recuperada cambia; las decisiones no.** En 10 de los 17 casos de suficiencia el
conjunto de fragmentos aplicables creció (entre 2 y 3 fragmentos nuevos por caso; ningún
fragmento anterior desapareció). Las 17 decisiones EXPLAIN/ABSTAIN son idénticas a las
anteriores, en modo oracular y en modo no oracular: **15/17** en ambos. Las cuatro líneas base
invariantes se reproducen elemento a elemento (regla de parada no activada). Según el criterio
fijado en el pre-registro §6, esto se lee como **«sin efecto detectable con este instrumento»**
y como **«el defecto tocaba candidatos redundantes»**. **No** se lee como validación del
verificador v2.1: con cobertura binaria, techo saturado y N = 5 ventanas, el instrumento no
tiene resolución para detectar un efecto pequeño.

Bandera roja del pre-registro: el resultado nuevo no es mejor en toda dimensión (es igual en
decisiones y en métricas de recuperación salvo un nDCG), así que no hay motivo para sospechar
un segundo cambio no declarado. El único cambio de código adicional, la propagación del filtro
de motor en la degradación, ya estaba declarado en el pre-registro §2 y no altera ninguna celda.

## Paso B · E12 recuperación (seis casos, cinco estrategias)

Registro: `experiments/E12_retrieval.json` (13-09-2026 22:57 UTC, `dirty: false`,
`embedding_space_id` declarado). Antes: `experiments/pre_mixed_embedding_fix/E12_retrieval.json`.

| Estrategia | hit-rate antes → después | MRR | nDCG@10 | casos con distractor por encima del relevante |
|---|---|---|---|---|
| semantic | 0,00 → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 | 1 → 1 |
| semantic+engine | 0,20 → 0,20 | 0,04 → 0,04 | 0,149 → 0,149 | 0 → 0 |
| semantic+authority | 0,40 → 0,40 | 0,107 → 0,107 | 0,468 → 0,468 | 0 → 0 |
| hybrid | 0,40 → 0,40 | 0,107 → 0,107 | 0,468 → 0,468 | 0 → 0 |
| diagnosis-guided | 1,00 → 1,00 | 0,467 → 0,467 | 0,642 → **0,653** | 0 → 0 |

Denominadores (ENM-S02 S-9): 6 evaluados, 5 puntuados, 1 excluido (`C06`, sin ficheros
relevantes). El rango del primer relevante por caso en `diagnosis-guided` no cambia (2, 1, 6,
3, 3). El único movimiento es el nDCG de esa estrategia, que sube una centésima por
reordenación de posiciones no relevantes.

**M5 · duplicados por mezcla de espacios** (unidad del pre-registro §7): **0 / 300** posiciones
en los 30 conjuntos recuperados del artefacto nuevo. El artefacto anterior no guarda los
conjuntos, así que la prevalencia «antes» sigue sin unidad definida
(`UNIT_UNDEFINED_IN_LEGACY_RESULT`); no se reconstruye.

## Paso D · E15/E17 suficiencia, modo oracular, verificador v2.1

Registro: `experiments/E15_suficiencia.json` (22:57 UTC). Antes:
`pre_mixed_embedding_fix/E15_suficiencia.json` (commit `43f56dc`, 4-09).

| Métrica pre-registrada | Antes | Después |
|---|---|---|
| M1 vector de decisiones | 15/17 correctas | **15/17, idéntico caso a caso** (fallan C01 y C04, igual que antes) |
| M2 vector de motivos de abstención | — | idéntico en 16 casos; en `C09_distractor_sin_filtro` desaparece el motivo `TOO_FEW_SUPPORTING_CHUNKS` y queda solo `LOW_CLAIM_COVERAGE` (los fragmentos aplicables pasan de 1 a 3) |
| M3 señales continuas | — | confianza calibrada idéntica en los 17 (no depende de la recuperación); cobertura de afirmaciones idéntica; documentos aplicables suben en 10 casos (por ejemplo C05 5 → 7, C09 1 → 3, C13 3 → 4) |
| M4 conjuntos de fragmentos | — | cambian en **10 de 17** casos: el conjunto anterior está siempre contenido en el nuevo; se añaden de 2 a 3 fragmentos por caso; ninguno se retira |
| M6 líneas base invariantes (vector B por caso) | ALWAYS_ABSTAIN 12/17 · ALWAYS_EXPLAIN 5/17 · ALWAYS_EXPLAIN_WHEN_MODEL_CONFIDENT 3/17 | **idénticas, elemento a elemento** → regla de parada no activada |
| ABSTAIN_IF_NO_EVIDENCE_RETRIEVED (se recalcula) | 8/17 sobre el artefacto anterior | 8/17 |
| Techo alcanzable | 15/17 (pre-registro) | no recalculado: su definición no está implementada en código |

Nota sobre la línea base `ABSTAIN_IF_NO_EVIDENCE_RETRIEVED`: el pre-registro la cita como
6/17 «antes»; recalculada sobre el artefacto congelado con la regla «abstiene si no hay
documentos aplicables» da 8/17. La diferencia procede de la definición, no de la reejecución
(el pre-registro no fija cómo se cuenta); se declara y no se elige la más favorable.

Detalle por caso, cobertura y conjuntos: `artifacts/metrics/rerun_a_comparison.json`.

## Paso E · Diagnóstico de la condición de distractor (no puntuado)

Criterios D-1 y D-2 de ENM-S02 S-5, evaluados sobre `bundle.documents` del artefacto oracular
canónico, comparando siempre con la condición parcial de la misma ventana (ENM-S03 S-13):

| Caso | Condición | D-1 (fragmento de fichero distractor presente) | D-2 (diferencia simétrica con la parcial) | Clasificación |
|---|---|---|---|---|
| C08_distractor | DISTRACTOR | sí | 2 | `VALID_CONDITION` |
| C09_distractor_sin_filtro | DISTRACTOR_NO_FILTER | sí | 6 | `VALID_CONDITION` |
| C12_thermostat_distractor | DISTRACTOR | **no** | **0** | `REDUNDANT_WITH_PARTIAL` |
| C13_thermostat_distractor_sin_filtro | DISTRACTOR_NO_FILTER | sí | 7 | `VALID_CONDITION` |
| C16_o2_distractor | DISTRACTOR | **no** | **0** | `REDUNDANT_WITH_PARTIAL` |
| C17_o2_distractor_sin_filtro | DISTRACTOR_NO_FILTER | sí | 6 | `VALID_CONDITION` |

Lectura: **con el filtro de motor activo, la condición de distractor es redundante con la
parcial en dos de los tres fallos** (termostato y sonda de oxígeno): recupera exactamente los
mismos fragmentos. Solo en la fuga de vacío (C08) entra un fragmento del fichero distractor.
Sin filtro, el distractor entra en los tres fallos. Esto confirma, ahora con recuperación
canónica, lo que `docs/methodology/politica-condicion-distractor.md` había adelantado con
recuperación no canónica: la condición no manipula una variable observable de forma uniforme.
Consecuencia sobre K (ENM-S02 S-8, S-12): `K_valid` no puede incluir DISTRACTOR como condición
homogénea en los tres bloques; el estadístico principal `T-PRINCIPAL` exige el mismo K en
todos los bloques y **no aplica**. Se reporta descriptivo, como el pre-registro prevé, y **no
se calcula ningún valor p**.

## Paso F · Suficiencia, modo no oracular

Registro: `experiments/E15_suficiencia_non_oracle.json`. Los tres canales de oráculo cerrados
(`oracle_channels_open` todos `false`). **15/17, con el vector de decisiones idéntico al del
modo oracular nuevo y al del no oracular anterior.** La predicción registrada en NX-01 se
mantiene con recuperación canónica.

## Pasos G y H · Conjunto de ajuste del SLM y su linaje

Registro: `experiments/E13b_training_data.json` (`dataset_hash` train `70bd0d7e6c406319`,
valid `ac81346e6d48548a`). Antes: `pre_mixed_embedding_fix/E13b_training_data.json` (1-09,
sin commit ni fecha).

| | Antes | Después |
|---|---|---|
| Ejemplos | 62 | **66** |
| Casos | 44 | 43 |
| Reparto | `case_id` | `source_window` |
| Distribución | FULL/EXPLAIN 27 · FULL/ABSTAIN 10 · PARTIAL/ABSTAIN 10 · ABSENT/ABSTAIN 10 · PARTIAL/EXPLAIN 5 | 28 · 11 · 11 · 11 · 5 |
| Fuga de texto del manual | 0 problemas | 0 problemas |

**Segunda variable declarada:** la regla de reparto cambió de `case_id` a `source_window` en el
commit `d2c7f55` (4-09, «Correcciones de los tres gates»), posterior al conjunto anterior. La
diferencia de 62 → 66 ejemplos mezcla, por tanto, dos causas (recuperación canónica y regla de
reparto) que este diseño no separa. El adaptador LoRA vigente (`models/slm_lora_v2`) se entrenó
sobre el conjunto anterior; **no se ha reentrenado** (decisión aparte, con coste declarado en el
plan §1), y sigue marcado `NON_CANONICAL_PENDING_REGENERATION`.

## Paso I · Agente E13 sobre recuperación canónica

Registros: `experiments/E13_agente_transformers-lora@slm_lora_v2.json` (canónico, 14-09-2026
00:20 UTC, commit `487e98a`), `E13_agente_transformers.json` y `E13_agente_transformers-lora.json`
(mismo commit). Antes: las tres copias en `pre_mixed_embedding_fix/` (4-09, commit `68cb5f5`).
El campo `dirty: true` de los tres se debe a que el runner escribe primero el registro de
suficiencia (fichero versionado) y después el del agente, dentro de la misma ejecución; el
árbol estaba limpio al lanzarla (`HEAD 487e98a`, `git status` vacío, anotado en el registro de
ejecución).

**Segunda variable declarada, y es grande:** el conjunto anotado pasó de 9 a 17 casos el
4-09-2026 (P-03, commit `14f800a`), **después** de las ejecuciones del agente que se comparan.
La comparación estricta antes/después es, por tanto, sobre los 9 primeros casos (el mismo
subconjunto); las cifras sobre 17 son la nueva medición canónica, sin equivalente anterior.

| Configuración | Antes (9 casos, 4-09) | Después, mismos 9 casos | Después, 17 casos (canónico) |
|---|---|---|---|
| Base (`transformers`) | 7/9 válidas · 7/7 evaluables respetan el veredicto · 0 citas inventadas · 2 fallos de esquema | 7/9 · 7/7 · 0 · 2 | 15/17 válidas · 15/15 · 0 · 2 fallos de esquema |
| Base + LoRA v1 | 7/9 · 7/7 · 0 · 2 | 6/9 · 6/6 · 0 · 3 | 11/17 · 11/11 · 0 · **6 fallos de esquema** |
| **Base + LoRA v2** | 9/9 · 9/9 · 0 · 0 | **9/9 · 9/9 · 0 · 0** | **17/17 · 17/17 · 0 · 0** |

Lectura: con recuperación canónica y los mismos nueve casos, la configuración canónica (LoRA
v2) reproduce exactamente su resultado anterior; el modelo base también; LoRA v1 pierde una
salida válida (6/9). Sobre los 17 casos, LoRA v2 mantiene 17/17 y 0 citas inventadas, mientras
LoRA v1 falla el esquema en 6 casos: el defecto de vocabulario que motivó v2 se manifiesta más
al ampliar el conjunto. En ninguna configuración, antes ni después, apareció una cita
inventada: la barrera externa que rechaza identificadores no entregados sigue haciendo su
trabajo con independencia del adaptador.

**Sobre el «9/9» publicado para el respeto del veredicto** (`docs/experiments/E13_agente_slm.md`,
`docs/memoria/cap5_resultados.md`): los registros del 4-09 tienen `respected_verdict: null` en
los dos runs con fallo de esquema del modelo base y en los dos de LoRA v1; la cifra correcta es
**7 de 7 evaluables**, no 9/9. Se corrige en ambos documentos con nota fechada
(`docs/experiment-index.md` §Discrepancias, D-3).

El adaptador v2 sigue entrenado sobre el conjunto anterior: esta reejecución mide el mismo
adaptador sobre evidencia canónica; no lo regenera.

## Pasos no ejecutados

- **C · `E-EMBED-MULTILINGUAL`**: no existe runner ni comando para la evaluación pre-registrada
  en `docs/methodology/preregistro-embed-multilingual.md`; ejecutarla exigiría escribir código
  nuevo, fuera del alcance de esta reejecución. Sigue `PLANNED`.
- **J · líneas base**: computadas aquí a partir de los registros (vector B, ABSTAIN_IF_NO_EVIDENCE);
  el techo alcanzable no tiene definición en código y no se recalcula.
- **RERUN-B (política v2.2, puerta de DTC)**: fuera del plan de RERUN-A por diseño; sigue
  implementada, probada y sin medir.
- **Modo adverso (NX-02)**: retirado del plan por decisión previa (plan §1).

## Estado que se deriva

| Elemento | Estado anterior (`estados-provisionales.md`) | Estado tras RERUN-A |
|---|---|---|
| E12 recuperación | `SUPERSEDED_BY_EMBEDDING_SPACE_FIX` | **canónico** el registro del 13-09 (`experiments/E12_retrieval.json`); el anterior queda como histórico no canónico |
| E15 oracular y no oracular | ídem | **canónicos** los registros del 13-09; cifras iguales a las anteriores (15/17), ahora con procedencia determinada |
| Condición de distractor | `PENDING_CANONICAL_RETRIEVAL_DIAGNOSIS` | diagnosticada: `VALID_CONDITION` en un fallo, `REDUNDANT_WITH_PARTIAL` en dos (con filtro); sin filtro válida en los tres |
| `TRAINING_DATASET_V1` | `SUPERSEDED_PENDING_CONFIRMATION` | superseded por el conjunto del 13-09 (66 ejemplos), con la segunda variable declarada |
| Adaptador LoRA | `NON_CANONICAL_PENDING_REGENERATION` | sin cambios: no reentrenado; medido sobre evidencia canónica con resultado idéntico en los 9 casos comunes |
| Medición translingüe | `NOT_VERIFIABLE` | sin cambios |
| `MIXED-EMBEDDING-SPACE` (L-20) | corregido en código, reejecución pendiente | reejecución hecha; **cerrado en cuanto a recuperación y suficiencia**; abierto en cuanto al adaptador |
