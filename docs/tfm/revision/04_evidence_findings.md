# 04 · Verificación de evidencia — resumen consolidado

**Skill:** `tfm-evidence-verifier`, modo `/evidence-full` + `/evidence-recheck` ·
**Informe completo:** `evidence-reports/EVIDENCE-VERIFICATION-20260903.md` (24 secciones, 78 claims,
matriz claim ↔ evidencia y bloque `EVIDENCE_VERIFIER_HANDOFF`) · **Matriz persistente:**
`evidence-reports/claims/claims.md` · **Instantánea:** `mecanico-ia-exp`, commit `d45caad`,
3 de septiembre de 2026, árbol limpio · **Lectura únicamente**, ningún fichero del repositorio
modificado salvo este resumen. **Informe anterior:** `evidence-reports/EVIDENCE-DRY-RUN-01.md`
(commit `8d55def`), cuyos identificadores de claim y de hallazgo se conservan.

**Alcance:** toda la memoria (`docs/memoria/00_resumen.md`, `cap1`–`cap6`, `bibliografia.md`)
y `docs/matriz_validacion_pi.md`.

## Veredicto

**`FAIL`.** Once hallazgos `MAJOR` abiertos, **ninguno `CRITICAL`**. Cinco de los catorce gates en
`FAIL`: suficiencia de la evidencia (05), soporte de fuentes científicas (06), integridad numérica
(08), manejo de evidencia contradictoria (11) e integridad de la fuente de verdad (12).

El fallo **no procede de un razonamiento inválido ni de una conclusión inventada**. Procede de dos
cosas:

1. **Cuatro tablas centrales publican cifras que no se reproducen desde ningún artefacto vigente**
   —la de recuperación de `cap5` l.82-89, la de suelo de ruido de `cap4` l.95-100, la fila calibrada
   de `cap5` l.66-71 y el bloque PI.2 de la matriz—, y dos afirmaciones del propio texto sobre el
   estado de su evidencia resultan falsas al comprobarlas: «toda cifra publicada procede de un
   registro de ejecución reproducible» y «dos informes de fase dan cifras distintas de sus registros
   (E6 y E7)», cuando son al menos cuatro.
2. **Dos contradicciones que el repositorio registra y la memoria no declara**: la sensibilidad de E7
   sobre `synthetic_v3`, que invierte el orden entre el bosque y la GRU y corrige la lectura sobre el
   fallo de encendido; y la iteración 5 del registro de búsqueda, que refuta la afirmación de novedad
   tal como `cap1` la enuncia.

Y de un tercer problema, más barato de corregir que los anteriores y de mayor efecto en una defensa:
**PI.3 y PI.4 se declaran sostenidas sobre un solo fallo**. El trabajo acota con rigor la procedencia
sintética de sus datos en cinco documentos, y no acota el número de casos en ninguno.

**Lo que no está en discusión.** El experimento central es reproducible celda a celda: las 54 celdas
de la tabla de suficiencia coinciden con `experiments/E15_suficiencia.json`, y las cinco filas del
contraste comparten `bundle.case_id` y `calibrated_confidence` 0.9078, de modo que la variable
manipulada es realmente una. La doble trazabilidad está implementada y se reconstruye a nivel de
afirmación en las dos ramas. El respeto del veredicto y la ausencia de citas inventadas se verifican
en 63 ejecuciones. Ninguna conclusión afirma comportamiento en vehículo real.

**Por qué ningún `CRITICAL`.** Se buscaron los cinco disparadores. No hay valor fabricado: las once
cifras en conflicto proceden de ejecuciones reales localizables en el historial o en un informe
fechado. No hay fuente inexistente. No hay conclusión central sin cadena. No hay resultado principal
irrastreable. Y no hay ocultación: en las dos contradicciones no declaradas, el documento que las
registra es del propio autor, en el mismo repositorio.

## Gates (EVID-GATE-01..14)

| Gate | Estado | Motivo |
|---|---|---|
| 01 Identificación de claims | PASS | 78 claims con ID, tipo, criticidad y ubicación; los 18 anteriores conservados |
| 02 Atomicidad | PASS | ninguna frase compuesta con un solo veredicto |
| 03 Disponibilidad de evidencia | PASS_WITH_OBSERVATIONS | nueve claims sin evidencia localizable, todos con marcador |
| 04 Relevancia de la evidencia | PASS_WITH_OBSERVATIONS | `C-0012b`, `C-0072` |
| **05 Suficiencia de la evidencia** | **FAIL** | siete claims CRITICAL sostienen PI.3 y PI.4 sobre un solo fallo, sin acotar el n |
| **06 Soporte de fuentes científicas** | **FAIL** | la afirmación de novedad está contradicha por L-10 y el registro de búsqueda; once citas quedan `UNVERIFIABLE` porque el propio registro declara no verificado el contenido |
| 07 Soporte de resultados experimentales | PASS_WITH_OBSERVATIONS | soporte condicional al DTC anotado; M4 sin implementar |
| **08 Integridad numérica** | **FAIL** | `CONFLICTING_NUMBER` en 8 celdas de la tabla de recuperación, 4 del suelo de ruido y 4 cifras de la matriz |
| 09 Trazabilidad claim → run | PASS_WITH_OBSERVATIONS | tres cadenas rotas: `C-0005` (métrica), `C-0054` (run), `C-0055` (artefacto) |
| 10 Soporte de conclusiones | PASS_WITH_OBSERVATIONS | cadena completa hasta la PI; omiten cobertura y n |
| **11 Evidencia contradictoria** | **FAIL** | dos contradicciones registradas en el repositorio y no declaradas en la memoria |
| **12 Integridad de la fuente de verdad** | **FAIL** | conflictos sin declarar en cifras centrales (E5, E12, matriz) y recuento de discrepancias falso |
| 13 Alcance y generalización | PASS_WITH_OBSERVATIONS | procedencia declarada; `OVERGENERALIZED_SCOPE` respecto al n |
| 14 Validación de claims CRITICAL | PASS_WITH_OBSERVATIONS | las diez preguntas respondidas para los doce |

Score (opcional y secundario): claims 22/25 · evidencia 13/25 · conclusiones 16/25 · integridad
11/25 → **62/100**. No determina el estado.

## Claims por estado y por capítulo

| Documento | Claims | SUPPORTED | PARTIALLY | UNSUPPORTED | CONTRADICTED | UNVERIFIABLE |
|---|---|---|---|---|---|---|
| `00_resumen.md` | 6 | 2 | 3 | 0 | 0 | 1 |
| `cap1_introduccion.md` | 8 | 1 | 2 | 0 | 2 | 3 |
| `cap2_objetivos.md` | 2 | 1 | 1 | 0 | 0 | 0 |
| `cap3_marco_teorico.md` | 6 | 3 | 1 | 0 | 1 | 1 |
| `cap4_marco_metodologico.md` | 8 | 3 | 1 | 0 | 4 | 0 |
| `cap5_resultados.md` | 30 | 15 | 12 | 0 | 1 | 2 |
| `cap6_conclusiones.md` | 6 | 2 | 1 | 1 | 1 | 1 |
| `matriz_validacion_pi.md` | 12 | 2 | 5 | 0 | 4 | 1 |
| **Total** | **78** | **29** | **26** | **1** | **13** | **9** |

Criticidad: CRITICAL 12 · HIGH 28 · MEDIUM 31 · LOW 7. De los doce claims CRITICAL, cinco quedan
`SUPPORTED` (`C-0006`, `C-0007`, `C-0018`, `C-0023`, `C-0059`; los dos primeros, para el caso
evaluado) y siete `PARTIALLY_SUPPORTED`. Ninguno queda `UNSUPPORTED`, `CONTRADICTED` ni
`UNVERIFIABLE`: esa es la razón de que no haya ningún BLOCKER.

## Matriz claim ↔ evidencia (claims CRITICAL y HIGH)

| Claim | Evidence | Source | Experiment | Metric | Status |
|---|---|---|---|---|---|
| C-0001 las cuatro subpreguntas quedan sostenidas | agregada de PI.1-PI.4 | `cap5` l.203-205 | E6, E12, E13, E15 | M1, M2, M4, M5 | PARTIALLY_SUPPORTED |
| C-0004 toda afirmación admitida es trazable | `support_checks`, `claim_coverage` | `experiments/E15_suficiencia.json` | E15, E17 | M4 cobertura | PARTIALLY_SUPPORTED (condicional) |
| C-0006 la decisión cambia al retirar la evidencia | C05 EXPLAIN ↔ C06 ABSTAIN, conf 0.9078 | `E15_suficiencia.json` | E15, E17 | M5 | SUPPORTED (n = 1 fallo) |
| C-0007 la evidencia parecida no se acepta | `cases_with_distractor_above_relevant`; C08, C09 | `E12_retrieval.json`, `E15_suficiencia.json` | E12, E15 | M2, M5 | SUPPORTED en lo evaluado |
| C-0017 sí puede, cuando la decisión no depende del LLM | agregada | `cap6` l.14-23 | E13, E15, E17 | M3, M4, M5 | PARTIALLY_SUPPORTED |
| C-0018 vale para sintéticos, no validada en real | L-01, `dataset_type: synthetic` | `research/limitations-register.md` | — | E4 | SUPPORTED |
| C-0021 explica con evidencia, se abstiene sin ella | ídem C-0006 | `00_resumen.md` l.27-29 | E15, E17 | M5 | PARTIALLY_SUPPORTED |
| C-0022 respeta la decisión y no inventa citas | 9/9 ×3, 0 citas falsas; **`ollama` 7/9** | `E13_agente_*.json` | E13 | M3, M4 citas | PARTIALLY_SUPPORTED |
| C-0023 declara la procedencia y acota los resultados | declarada en cinco documentos | resumen, cap1, cap4, cap5, cap6 | — | E4 | SUPPORTED |
| C-0059 mismo caso, misma confianza, solo cambia el índice | `bundle.case_id` y 0.9078 ×5 | `E15_suficiencia.json` | E15, E17 | M5 | SUPPORTED |
| C-0067 las cuatro subpreguntas se cumplen | agregada | `matriz` l.184-196 | E6-E17 | M1-M5 | PARTIALLY_SUPPORTED |
| C-0076 el mecanismo funciona | ídem C-0006 | `matriz` l.199-203 | E15, E12 | M5 | PARTIALLY_SUPPORTED |
| C-0002 diagnostica muy por encima de la referencia mínima | 0,8788 frente a 0,0741 | `E6_baseline_synthetic_v2.json` | E6 | M1 | SUPPORTED |
| C-0003 la confianza calibrada significa lo que aparenta | ECE 0,085 **sin registro** | `E15_suficiencia.md` l.102 | E15 | M1 calibración | PARTIALLY_SUPPORTED |
| C-0005 la distancia entre completitud y soporte es cero | ninguna; M4 no implementada | `cap5` l.208 | E14 pendiente | M4 | UNVERIFIABLE |
| C-0009 respeta la decisión en todos los casos | 9/9 ×3; `ollama` 7/9 | `E13_agente_*.json` | E13 | M3 | PARTIALLY_SUPPORTED |
| C-0010 no sostienen nada sobre un vehículo real | L-01 | `limitations-register.md` | — | E4 | SUPPORTED |
| C-0020 una variable, cuatro condiciones | C05-C09, un solo fallo | `E15_suficiencia.json` | E15, E17 | M5 | PARTIALLY_SUPPORTED |
| C-0027 la recuperación reduce pero no elimina | REF-106, REF-016 sin contenido verificado | `cap1` l.29-30 | — | E1 | UNVERIFIABLE |
| C-0028 ninguno de los revisados lo comprueba | L-10; `search-log.md` it. 5 | `cap1` l.54-57 | — | E1 | **CONTRADICTED** |
| C-0032 constantes ancladas una por una con su página | fichero y cita literal, sin página | `configs/calibracion_mazda3_bk.yaml` | E2 | E4 | PARTIALLY_SUPPORTED |
| C-0036 el tabular no fue superado por el secuencial | v2 sí; **v3 lo invierte** | `E7_temporal_synthetic_v{2,3}.json` | E7 | M1 | PARTIALLY_SUPPORTED |
| C-0037 ninguno de los trabajos revisados lo mide | L-10; `search-log.md` it. 5 | `cap3` l.150-152 | — | E1 | **CONTRADICTED** |
| C-0038 semántica 0,00 → guiada 1,00 | `hit_rate` 0,0 y 1,0 en R1 y R2 | `E12_retrieval.json` | E12 | M2 | SUPPORTED |
| C-0041 toda cifra procede de un registro con su commit | cinco cifras sin registro; ningún registro con `commit` | `cap4` l.22-24 | — | E4 | **CONTRADICTED** |
| C-0046 casos de validación correctamente clasificados | `(validacion.y == fault_id) & aciertos` | `sufficiency_runner.py` l.111-112 | E15 | E4 | SUPPORTED |
| C-0047 M4 se calcula de forma determinista | sin implementación; E14 pendiente | `cap4` l.222-225 | E14 | M4 | **CONTRADICTED** |
| C-0049 tabla PI.1 (0,286/0,074 · 0,878/0,879 · 0,827/0,823) | seis valores | `E6/E7_*_synthetic_v2.json` | E6, E7 | M1 | SUPPORTED |
| C-0050 el temporal no supera al tabular | v2 sí; v3 lo invierte | `E6/E7_*_synthetic_v3.json` | E7 | M1 | PARTIALLY_SUPPORTED |
| C-0053 tabla de calibración | fila 1 en E6; **fila 2 sin registro** | `E6…v2.json`; `E15_suficiencia.md` | E6, E15 | M1 | PARTIALLY_SUPPORTED |
| C-0054 tabla de recuperación por estrategia | **R1 sustituido por R2** | `git show 355d475:…` frente a `E12_retrieval.json` | E12 | M2 | **CONTRADICTED** |
| C-0056 cobertura 1,00 en las cinco condiciones | `claim_coverage` 1.0 ×5 | `E15_suficiencia.json` | E15 | M4 | SUPPORTED (condicional) |
| C-0058 tabla de nueve casos; 7 de 9 correctas | 54 celdas | `E15_suficiencia.json` | E15, E17 | M5 | SUPPORTED |
| C-0060 dos líneas de defensa independientes | filtro (6 casos); validador (1 caso) | `E12_retrieval.json`, `E15…json` | E12, E15 | M2, M5 | PARTIALLY_SUPPORTED |
| C-0061 tabla E13 + 0,24 % + 55 ejemplos | 18 celdas; `finetune_config.json` | `E13_agente_*.json`, `models/slm_lora*/` | E13 | M3 | SUPPORTED |
| C-0064 dos informes dan cifras distintas (E6 y E7) | E5 y E12 también | `cap6` l.100-101; `cap5` l.7-8 | E5, E12 | — | **CONTRADICTED** |
| C-0069 18 afirmaciones, 51 comprobaciones, 41 % | registro: 27, 63, 42,9 % | `E15_suficiencia.json` | E15 | M4 | **CONTRADICTED** |
| C-0072 muy por encima del azar | el comparador medido es la clase mayoritaria | `matriz` l.189 | E6 | M1 | PARTIALLY_SUPPORTED |
| C-0073 tabla del hallazgo transversal | R2 vigente; **≠ `cap5`** | `E12_retrieval.json` | E12 | M2 | SUPPORTED contra R2 |
| C-0077 la cadena de procedencia se reconstruye por completo | `retrieval_run` no viaja en los registros | `E15_suficiencia.json`; `rag/store.py` l.519 | E15 | M4 | PARTIALLY_SUPPORTED |

## Hallazgos

Severidad en la escala del encargo: CRITICAL→BLOCKER, MAJOR→MAJOR, MINOR→MODERATE, INFO→MINOR
(COSMETIC si es puro formato). **Ninguno es BLOCKER.**

| ID | Severidad | Archivo | Sección/línea | Problema | Evidencia | Corrección propuesta | Riesgo | Estado |
|---|---|---|---|---|---|---|---|---|
| EVID-MAJ-002 | MAJOR | `docs/memoria/cap5_resultados.md`; `cap6_conclusiones.md`; `00_resumen.md`; `docs/matriz_validacion_pi.md` | cap5 l.203-211; cap6 l.17-23; resumen l.25-29; matriz l.37-40, 187-203 | PI.3 y PI.4 se declaran sostenidas, y la conclusión y el resumen afirman que el agente se abstiene al retirar la evidencia y ante evidencia parecida, sobre **un solo fallo** bajo cuatro condiciones. Las conclusiones omiten además la cobertura 3 de 5 | `experiments/E15_suficiencia.json`: C05-C09 comparten `bundle.case_id` `F01_vacuum_leak__idle__10@120s`; ABSENT, PARTIAL y DISTRACTOR solo existen para `F01` | Acotar a «en el caso evaluado bajo las cuatro condiciones» y «en tres de los cinco casos con evidencia», o extender PARTIAL y DISTRACTOR a los demás fallos, que la propia matriz l.218 lista como pendiente | El contraste sigue siendo válido y reproducible; lo que no se sostiene es leerlo como propiedad del agente. Es el punto con más superficie de ataque en una defensa | **NOT_FIXED** (del dry-run) |
| EVID-MAJ-013 | MAJOR | `docs/memoria/cap5_resultados.md` | l.82-89 | La tabla de recuperación reproduce R1 celda a celda; ocho celdas no coinciden con el registro vigente R2, que la matriz sí publica. El capítulo cita como «Registro» un informe Markdown | `git show 355d475:experiments/E12_retrieval.json` (5 casos, 20:21) frente a `experiments/E12_retrieval.json` (6 casos, 21:32); `semantic+engine` pasa de Hit 0,00 a 0,20 | Declarar la ejecución canónica de E12 y regenerar la tabla desde el JSON; alinear `cap5` con la matriz | La conclusión cualitativa (0,00 semántica → 1,00 guiada) se sostiene en ambas ejecuciones; el capítulo mezcla dos runs | OPEN |
| EVID-MAJ-014 | MAJOR | `docs/memoria/cap4_marco_metodologico.md`; `research/limitations-register.md` | cap4 l.95-108; L-15 | Las cuatro cifras del suelo de ruido y la narrativa de la ventana proceden del informe de fase y no coinciden con el registro vigente | `tables/E5_estudio_ventana.csv`: 0,3259 / 0,3653 / 0,4261 / 0,5133 frente a 0,369 / 0,399 / 0,438 / 0,512; a 30 s el mejor descriptor de F05 ya es `oxygen_sensor_mean`, declarado | Decidir el conjunto canónico de E5 y regenerar informe, `cap4` y L-15 desde la tabla vigente, o restaurar el original bajo otro identificador | La conclusión cualitativa (120 s) se mantiene: a 120 s las cinco condiciones tienen descriptor declarado y por encima del suelo | OPEN |
| EVID-MAJ-015 | MAJOR | `docs/memoria/cap5_resultados.md`; `cap3_marco_teorico.md`; `cap6_conclusiones.md`; `research/limitations-register.md` | cap5 l.52-62, 221-222; cap3 l.82-84; cap6 l.47-49; L-15 | La memoria conserva «el temporal no supera al tabular» y «el fallo de encendido se detecta en la mitad» sin mencionar la ejecución de sensibilidad que el propio proyecto registró y cuya conclusión el informe E7 declara corregida | `E7_temporal_synthetic_v3.json` F1 macro **0,9446** frente a `E6_baseline_synthetic_v3.json` 0,9321; F05 F1 0,8602 y 0,9111 frente a 0,6667 y 0,5; `E7_modelo_temporal.md` l.90-96 | Reportar la sensibilidad con su n de sesiones y su condición de exploratoria, y la corrección del informe; actualizar L-15; o dejar por escrito por qué no se incorpora | Afecta a la lectura de PI.1, a la justificación de conservar el bosque y a la interpretación de C01 y C04 como «casos difíciles» | OPEN |
| EVID-MAJ-016 | MAJOR | `docs/memoria/cap1_introduccion.md`; `cap3_marco_teorico.md` | cap1 l.54-57; cap3 l.150-152, 209-211 | La afirmación de novedad sobre PI.4 está contradicha por el registro de búsqueda y el registro de limitaciones del propio proyecto. `cap3` l.214-219 lleva la corrección; `cap1` y `cap3` l.150-152 no | L-10: «la búsqueda del 1 de septiembre **refutó** la hipótesis»; `search-log.md` l.116, *The Distracting Effect: Understanding Irrelevant Passages in RAG* (2025) | Propagar el alcance de L-10 y `cap3` l.214-219 a `cap1` y a `cap3` §Vacío; adoptar el vocabulario existente que L-10 recomienda; cerrar el `[CONSENSUAR CON EL DIRECTOR]` | Es la afirmación que sostiene el vacío y la contribución. Un tribunal que lea L-10 antes que `cap1` encuentra la contradicción sin buscarla | OPEN |
| EVID-MAJ-017 | MAJOR | `docs/memoria/cap5_resultados.md`; `cap6_conclusiones.md` | cap5 l.7-8; cap6 l.100-101 | La memoria declara, con recuento explícito, que las discrepancias informe ↔ registro son dos y son E6 y E7. Son al menos cuatro: E5 y E12 también | EVID-MAJ-013 y EVID-MAJ-014 | Sustituir el recuento cerrado por uno actualizado, o completar la lista con E5 y E12 y marcarlas `[RECONCILIAR]` como ya se hace con E6 y E7 | Una declaración de completitud sobre el estado de la evidencia es barata de comprobar y afecta a la credibilidad del resto, que en general es correcta. No se imputa intención | OPEN |
| EVID-MAJ-018 | MAJOR | `docs/matriz_validacion_pi.md` | l.39, 65-73, 216-217, 230 | El bloque PI.2 publica cifras de una ejecución anterior, la fila resumen dice «4 de 6» donde el propio documento dice «7 de 9», y la tabla «Lo que falta» declara pendientes dos cosas que el cuerpo describe como hechas | `experiments/E15_suficiencia.json`: 27 afirmaciones, 15 con soporte, 63 comprobaciones, 27 aceptadas (42,9 %), 7 de 9 decisiones correctas | Regenerar el bloque PI.2, la fila de PI.3 y la tabla «Lo que falta» desde el registro, o fechar cada cifra con su ejecución | La matriz es el documento que enuncia el veredicto sobre la PI y el primero que se lee tras el resumen. Se eleva a MAJOR por eso | OPEN |
| EVID-MAJ-019 | MAJOR | `docs/memoria/cap4_marco_metodologico.md`; `cap1_introduccion.md` | cap4 l.19-24 y l.326-328; cap1 l.81-83 | El compromiso «toda cifra publicada procede de un registro de ejecución reproducible, con su commit» se incumple en cinco cifras y en todos los registros en cuanto al commit; el propio `cap4` l.326-328 lo declara pendiente y se contradice con l.22-24 | Ningún JSON de `experiments/` tiene campo `commit`; cifras sin registro: ECE calibrado, tabla multilingüe, tabla de E12, suelo de ruido, 54,3/70,7 °C | Registrar las cinco cifras y añadir `commit` al esquema, o enunciar la regla con su excepción y alinear `cap1` con `cap4` l.326-328 | Es la regla que hace verificable todo lo demás; su incumplimiento es la causa común de cuatro hallazgos | OPEN |
| EVID-MAJ-001 | MAJOR | `docs/memoria/cap5_resultados.md`; `cap4_marco_metodologico.md` | cap5 l.208; cap4 l.222-225 | La distancia entre completitud y soporte se enuncia como resultado medido y M4 se describe como calculada de forma determinista; ninguna de las dos métricas está implementada | `grep` de `citation_completeness` y `claim_support_rate` en `src/` y `tests/` sin resultados; `docs/methodology/metrics.md` l.41-46 las define; `docs/experiments/README.md` l.23 marca E14 pendiente | Ejecutar E14, o reformular la frase como inferencia a partir de la cobertura de E15 y corregir `cap4` l.225 | PI.2 se apoya en una métrica declarada y no calculada; E3 presentado como E2; OE4 queda parcialmente sin resultado | **NOT_FIXED** (del dry-run) |
| EVID-MAJ-003 | MAJOR | `docs/memoria/cap5_resultados.md` | l.207-208, 109-113 | El soporte «verificado» de cada afirmación se comprueba con el código de avería derivado de la etiqueta anotada, y la consulta que recupera se guía con el mismo código; el claim omite la condición | `sufficiency_runner.py` l.166 `expected_dtc=DIAGNOSTICO_A_DTC.get(fault_id)`; `retrieval_runner.py` l.170 | Declarar en `cap4` o `cap5` que la verificación de soporte y la recuperación guiada usan el DTC anotado | **Alcance reducido**: la otra condición, que los casos son ventanas correctamente clasificadas, sí está declarada en `cap4` l.143-147 | **NOT_FIXED**, alcance reducido |
| EVID-MAJ-004 | MAJOR | `docs/memoria/cap5_resultados.md` | l.66-71 | La fila «Calibrado» (ECE 0,085; confianza 0,886; sesgo +0,009) existe solo en el informe de fase; el registro que el capítulo cita no la contiene | `experiments/E15_suficiencia.json` clave `calibration` es la cadena `"isotonic, cv=5 sobre entrenamiento"`, sin métricas | Reejecutar E15 escribiendo el bloque de calibración en el registro y citarlo; corregir la atribución de la fila «Sin calibrar» a `E6_baseline_synthetic_v2.json` | La mitad «calibración» de PI.1 no es rastreable a registro. El signo no cambia: la ejecución es determinista | **NOT_FIXED** (del dry-run) |
| EVID-MIN-005 | MODERATE | `docs/memoria/cap5_resultados.md` | l.211-212 | «la pieza en la que **la literatura** sitúa el riesgo»: sin cita local y con vocabulario que el proyecto prohíbe | MET-15 sí está citada en `cap1` l.28 y `cap3` l.123 | Citar MET-15 aquí y sustituir «la literatura» por «los trabajos revisados» | Bajo; el claim pasa de `UNSUPPORTED` a `PARTIALLY_SUPPORTED` al ampliar el alcance | **NOT_FIXED** |
| EVID-MIN-006 | MODERATE | `docs/memoria/cap5_resultados.md` | l.221-222 | «dos fallos que el modelo no distingue bien»: falso para F02 (F1 1,000) y debilitado para F05 por la ejecución v3 | `E6_baseline_synthetic_v2.json` F02 F1 1,0; `E6…v3.json` F05 F1 0,8602 | Acotar a F05 y a `synthetic_v2`, o explicar que lo bajo es la confianza calibrada de una ventana | Bajo | **NOT_FIXED**, agravado |
| EVID-MIN-007 | MODERATE | `docs/memoria/cap5_resultados.md` | l.47-50 | Informes E6 y E7 con cifras distintas de sus registros | ya declarado por el proyecto como `[RECONCILIAR]` | Regenerar los informes | Bajo: el capítulo cita el registro y declara el conflicto | **NOT_FIXED** |
| EVID-MIN-020 | MODERATE | `docs/memoria/cap5_resultados.md`; `cap3_marco_teorico.md` | cap5 l.94-105; cap3 l.175-177 | La tabla translingüe top-500 no tiene registro: existe solo en `docs/rag/multilingual.md`, que el capítulo cita como «Registro» | `grep` de las cuatro filas en `experiments/`, `tables/`, `results/` sin resultados | Registrar la medición como artefacto reproducible, o presentarla como observación de desarrollo | Es la evidencia con la que se justifica el cambio a modelo multilingüe | OPEN |
| EVID-MIN-021 | MODERATE | `docs/memoria/cap5_resultados.md`; `cap6_conclusiones.md`; `00_resumen.md` | cap5 l.212-213; cap6 l.22-23; resumen l.29 | «respeta la decisión en todos los casos» no acota el motor de inferencia; una cuarta configuración medida respeta 7 de 9 y no aparece en la memoria | `experiments/E13_agente_ollama.json`: `respected_verdict` 7/9, mismo modelo base | Trasladar la acotación que `cap5` l.166 ya hace («con el mismo motor de inferencia») a las tres frases, y reportar la medición | Moderado: la afirmación es exacta para las tres configuraciones publicadas y no para la cuarta medida | OPEN |
| EVID-MIN-022 | MODERATE | `docs/memoria/cap1_introduccion.md` | l.113-115 | «Todo el código, la documentación, los registros de experimentos… están versionados»: `tables/**`, `models/**`, `data/raw/**` y `figures/**` están ignorados, y la memoria cita ficheros de tres de esos directorios | `git check-ignore -v`; `.gitignore` l.32-40; `cap5` l.139 cita `tables/E15_suficiencia.csv`, `cap4` l.86 cita `synthetic_v2.meta.json` | Acotar la frase a lo versionado y decir que tablas, figuras, modelos y datos se regeneran; o versionar los CSV citados | Un tercero que clone no obtiene `tables/E5_estudio_ventana.csv`, único artefacto vigente del suelo de ruido | OPEN |
| EVID-MIN-023 | MODERATE | `docs/memoria/cap4_marco_metodologico.md`; `cap6_conclusiones.md` | cap4 l.66-69; cap6 l.28-29 | «con la cita de la página de la que proceden» / «con su página del manual»: el fichero de calibración documenta el **fichero** del manual y la **cita literal**, no la página | `configs/calibracion_mazda3_bk.yaml`: `fuente: srvc/B3E011002000W01.pdf` + `cita: "…"` | Decir «con el fichero del manual y la cita literal de la que proceden» | Bajo: la evidencia real es al menos tan fuerte como la descrita | OPEN |
| EVID-INF-008 | MINOR | `docs/experiments/E15_suficiencia.md` | l.213-222 | El barrido del umbral está en el informe, no en el registro | `E15_suficiencia.json` `thresholds` guarda el valor | Registrar el barrido, o declarar 0,80 como política | `STATISTICAL_DEPENDENCY` con STAT-MAJ-007 | **NOT_FIXED** |
| EVID-INF-009 | MINOR | `docs/EXPERIMENTO_PASO_A_PASO.md` | l.406-417 | El inventario de errores no incluye los tres hallados por la suite | E5, E12, informes E6/E7 | Completar el inventario | Refuerza el propio claim | **NOT_FIXED** |
| EVID-INF-010 | MINOR | `research/references/evidence-matrix.md` | todo | Matriz canónica vacía, con estado del 1 de septiembre | lectura | Consolidar las 78 filas de `evidence-reports/claims/claims.md` | Bajo (área Shared rules) | **NOT_FIXED** |
| EVID-INF-011 | MINOR | `docs/memoria/cap5_resultados.md` | l.237-239 | La comparación con los trabajos del capítulo 3 sigue pendiente | declarado por el texto | Ejecutarla tras E19 | `cap3` §Vacío queda sin cierre en resultados | **NOT_FIXED** |
| EVID-INF-012 | MINOR | `experiments/E15_suficiencia.json` | `thresholds` | `min_distinct_sources` = 1 frente a una política de fuentes independientes | registro | Declararlo | Coherente con un manual único | **NOT_FIXED** |
| EVID-INF-024 | MINOR | `docs/memoria/cap4_marco_metodologico.md` | l.329 | «283 tests» frente a 290 recolectados | `uv run pytest --collect-only -q` | Actualizar la cifra o retirarla | Nulo sobre los resultados | OPEN |
| EVID-INF-025 | MINOR | `docs/memoria/cap5_resultados.md` | l.119 | «Los cuatro informes conservan la afirmación falsa tachada»: solo dos llevan tachado | `E11_carga_rag.md` l.160, `E12_evaluacion_recuperacion.md` l.33; otros dos la documentan sin tachar | Decir «dos con tachado y dos con la corrección documentada» | Bajo | OPEN |
| EVID-INF-026 | MINOR | `docs/memoria/cap2_objetivos.md`; `docs/experiments/README.md` | cap2 l.96; README l.26 | `cap2` dice E17 ejecutada; el índice la lista pendiente y no hay informe | commit `7fb2255` sí regeneró `E15_suficiencia.json` bajo ese nombre | Actualizar el índice y escribir el informe de E17 | Índice desactualizado, no resultado ausente | OPEN |
| EVID-INF-027 | MINOR | `docs/memoria/cap6_conclusiones.md` | l.45-49 | L-15 aparece entre las limitaciones «Altas»; el registro la clasifica como media | `limitations-register.md` l.199, l.235 | Alinear la clasificación | COSMETIC | OPEN |
| EVID-INF-028 | MINOR | `research/limitations-register.md` | L-15 | Efecto 0,734 frente a suelo 0,512 (1,43×); el CSV da 0,6426 y 0,5133 (1,25×) | `tables/E5_estudio_ventana.csv` | Regenerar con EVID-MAJ-014 | Propagación de EVID-MAJ-014 | OPEN |
| EVID-INF-029 | MINOR | `docs/matriz_validacion_pi.md` | l.78 | La cadena documentada nombra `retrieval_run`, que no viaja en los registros publicados ni está versionado | `rag/store.py` l.519 (tabla de base de datos) | Incluir el identificador de recuperación en el registro, o describir la cadena desde el fragmento | Desde el fragmento en adelante la cadena sí se reconstruye | OPEN |
| EVID-INF-030 | MINOR | `docs/memoria/cap6_conclusiones.md` | l.95-97 | «un solo ejemplo entre 26» no se reconstruye | `E13b_training_data.json`: 30 abstenciones de 62 | Recalcular el denominador desde el registro | Bajo | OPEN |
| EVID-INF-031 | MINOR | `docs/memoria/cap3_marco_teorico.md` | l.24 | 144 referencias sin recoger la reconciliación 144 ↔ 153 que el registro declara pendiente | `search-log.md` l.22-25 | Reconciliar antes del depósito | Bajo | OPEN |

## Decisiones que corresponden al autor

1. **Ejecución canónica de E12**: declarar cuál de las dos ejecuciones es la oficial y regenerar
   `cap5` l.82-89 desde ella, alineando el capítulo con `docs/matriz_validacion_pi.md`
   (EVID-MAJ-013). `[AUTHOR_DECISION_REQUIRED]`.
2. **Conjunto canónico de E5**: regenerar informe, `cap4` l.95-107 y L-15 desde
   `tables/E5_estudio_ventana.csv`, o restaurar el conjunto original bajo otro identificador
   (EVID-MAJ-014). `[AUTHOR_DECISION_REQUIRED]`.
3. **Sensibilidad de E7 sobre `synthetic_v3`**: incorporarla al capítulo 5 con su condición de
   exploratoria y la corrección que el informe registra, o dejar por escrito la razón de no hacerlo,
   y decidir cuál es el conjunto oficial (EVID-MAJ-015). `[AUTHOR_DECISION_REQUIRED]`.
4. **Alcance de la novedad sobre PI.4**: fijar el enunciado que L-10 y `cap3` l.214-219 ya
   permiten, propagarlo a `cap1` y cerrar el `[CONSENSUAR CON EL DIRECTOR]` (EVID-MAJ-016).
5. **Acotación del n en PI.3 y PI.4**: acotar el texto, o extender PARTIAL y DISTRACTOR a los demás
   fallos antes del depósito (EVID-MAJ-002).
6. **Regla de la cifra con registro**: cumplirla (registrar las cinco cifras, añadir `commit` al
   esquema) o enunciarla con su excepción declarada (EVID-MAJ-019).
7. **Registro de la calibración** en E15 y **ejecución o retirada de la métrica M4** de completitud y
   soporte (EVID-MAJ-004, EVID-MAJ-001).

## Referencias remitidas al auditor de referencias

`[VERIFY_SOURCE]`. El reparto es el declarado: existencia y metadatos son del auditor de
referencias; «¿la fuente dice esto?» es de este skill, y sin acceso al texto de las fuentes queda
`UNVERIFIABLE`. El propio `research/references/references.md` lo declara en su cabecera: «Lo NO
verificado: que el trabajo **diga** lo que el TFM le atribuye».

| Referencia | Por qué | Claim que sostiene |
|---|---|---|
| MET-15 Ji et al. (2023) | contenido no verificado | `C-0019`, `C-0026`, y por remisión `C-0008` |
| REF-106 Shuster et al. (2021) | autores y DOI incompletos en el depósito | `C-0027` (HIGH) |
| REF-016 Béchard y Ayala (2024) | versión publicada disponible (NAACL 2024) | `C-0027` |
| REF-049 Hossain et al. (2024) | autores completos, páginas y DOI | `C-0025` |
| REF-078 Michailidis et al. (2025) | contenido no verificado | `C-0025` |
| REF-098 Rimpas et al. (2020) | contenido no verificado | `C-0025` |
| REF-059 Jun et al. (2025) | revista, volumen y DOI | cap1, cap3 |
| REF-071 Li y van Leeuwen (2023) | volumen, páginas y DOI | cap3 |
| REF-074 Liu et al. (2025) | DOI | cap3 |
| REF-097 Ramai et al. (2022) | revista, volumen y DOI | cap3 |
| MET-19 ISO 15031-5 | edición sin fijar | cap1, cap3 |

## Fortalezas verificadas

- **El experimento central es reproducible celda a celda.** Las 54 celdas de la tabla de suficiencia
  coinciden con `experiments/E15_suficiencia.json`, y las cinco filas del contraste comparten
  `bundle.case_id` y `calibrated_confidence` 0.9078: la variable manipulada es realmente una.
- **La doble trazabilidad está implementada, no prometida.** Cada afirmación lleva
  `observational_evidence` con señal, estadístico, valor, dirección y ventana temporal, y
  `documentary_evidence` con fragmento, sección, página, manual, editor y URL de origen, más un
  `support_check` por par. La salida del modelo de lenguaje lo preserva.
- **La disciplina causal está impuesta por código.** `llm/schema.py` l.69-74 rechaza lenguaje causal
  y `tests/test_llm_agent.py` l.112 lo comprueba; la salida real incluye la limitación explícita.
- **El distractor entra en la recuperación y aun así no cuenta.** En C05 el documento con la
  puntuación más alta (0,653) es un procedimiento del motor inaplicable; su aplicabilidad es
  `COMPATIBLE` y el criterio solo admite `EXACT_MATCH`.
- **La abstención se reporta con su cobertura** (3 de 5) y con el motivo registrado por caso.
- **Los desenlaces que refutarían el trabajo se enumeraron antes y se recorren después**, uno a uno,
  diciendo cuáles ocurrieron: dos de cinco se materializaron y se reportan.
- **La procedencia sintética se declara en los cinco documentos donde puede leerse una cifra**, y
  ninguna conclusión afirma comportamiento en vehículo real.
- **El capítulo declara conflictos en lugar de elegir cifra** donde los ha detectado (`[RECONCILIAR]`).
- **Las diecisiete limitaciones están ancladas**: cada entrada lleva el informe o documento del que
  procede; ninguna es ceremonial.
- **El error del propio instrumento se cuenta con su consecuencia**: el mapeo diagnóstico→DTC y la
  falsa ausencia de evidencia bajo el código genérico, con el comentario del código explicando por
  qué la corrección no fue «ajustar para acertar».
- **Ninguna métrica que responde a una subpregunta depende de un juicio humano o de un modelo de
  lenguaje**, y la limitación correspondiente lo declara.
