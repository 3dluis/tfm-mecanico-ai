# 05 · Revisión estadística — resumen consolidado

**Skill:** `tfm-statistical-reviewer`, modo `/stat-review-full` + `/stat-recheck` ·
**Informe completo:** `statistical-reports/STATISTICAL-REVIEW-20260903.md` (30 secciones,
12 análisis, quince preguntas del veredicto) · **Instantánea:** `mecanico-ia-exp`, 3 de
septiembre de 2026 · **Lectura únicamente**, ningún fichero del repositorio modificado.

## Veredicto

**`BLOCKED`.** Cinco hallazgos `MAJOR` abiertos, ninguno `CRITICAL`. Dos gates en `FAIL`:
consistencia de resultados (10) y trazabilidad estadística (12, para tres análisis). El
bloqueo no procede de un análisis inválido: procede de cifras publicadas que no se
reproducen desde los artefactos vigentes y de un umbral cuya procedencia no está registrada.

**Lo que no está en discusión.** No hay ninguna prueba de hipótesis, ningún valor p y ningún
intervalo en todo el TFM, y el capítulo 4 declara que el análisis es comparativo y por caso.
Esa declaración es correcta y se cumple: los doce análisis obtienen `NO_TEST_NEEDED` y el
gate de selección de prueba pasa sin observaciones. No se exige aquí ninguna prueba que el
texto no necesite.

## Análisis revisados

| ID | Análisis | Exp. | N_RAW / N_INDEPENDIENTE | Incertidumbre | Resultado |
|---|---|---|---|---|---|
| STAT-001 | delta de Cliff frente a suelo de ruido | E5 | 588 ventanas / 72 sesiones | no cuantificada | PARTIALLY_SUPPORTED |
| STAT-002 | separabilidad por señal y correlaciones | E4 | 360 bloques / 36 sesiones | — | NOT_APPLICABLE (descriptivo) |
| STAT-003 | bosque frente a clase mayoritaria | E6 | 98 ventanas / 12 sesiones (2 por clase) | no cuantificada | PARTIALLY_SUPPORTED (magnitud verificada) |
| STAT-004 | calibración ECE 0,144 → 0,085 | E6/E15 | 98 ventanas / 12 sesiones, 10 bins | no cuantificada | INCONCLUSIVE en lo afirmado; cifra sin registro |
| STAT-005 | GRU frente a bosque | E7 | 98 / 12 (v2); 343 / 36 (v3) | no cuantificada | **INCONCLUSIVE** (el orden se invierte con más datos) |
| STAT-006 | resumen de atribución | E9 | 18 ventanas / 3 por clase | — | NOT_APPLICABLE (descriptivo) |
| STAT-007 | métricas de recuperación por estrategia | E12 | 5 casos con relevante / 5 | no cuantificada | PARTIALLY_SUPPORTED |
| STAT-008 | recuperación translingüe top-500 | E12 | 5 casos / 5 | no cuantificada | PARTIALLY_SUPPORTED (sin registro) |
| STAT-009 | umbral de confianza 0,80 | E15 | 98 ventanas / 12 sesiones | — | **INCONCLUSIVE en su procedencia** |
| STAT-010 | matriz de abstención 7/9, cobertura 3/5 | E15 | 9 casos / **5 ventanas distintas**; 1 fallo con las cuatro condiciones | — | SUPPORTED en el contraste del caso probado |
| STAT-011 | tres configuraciones del modelo de lenguaje | E13 | 9 casos apareados / 9 | — | SUPPORTED en recuento |
| STAT-012 | soporte de afirmaciones (PI.2) | E15 | 27 afirmaciones, 63 comprobaciones / 9 casos | — | SUPPORTED como descriptivo |

## Gates (STAT-GATE-01..14)

| Gate | Estado |
|---|---|
| 01 unidad de análisis · 02 independencia · 03 tipo de variable · 05 supuestos · 06 tamaño muestral · 07 tamaño del efecto · 08 incertidumbre · 09 comparaciones múltiples · 11 interpretación · 13 negativos e inconclusos · 14 reproducibilidad | PASS_WITH_OBSERVATIONS |
| 04 selección de prueba | PASS |
| **10 consistencia de resultados** | **FAIL** (STAT-MAJ-001, STAT-MAJ-006, STAT-MIN-013) |
| **12 trazabilidad estadística** | **FAIL** para STAT-004, STAT-008 y STAT-009 |

## Hallazgos

Severidad en la escala del encargo: CRITICAL→BLOCKER, MAJOR→MAJOR, MINOR→MODERATE,
INFO→MINOR. Ninguno es BLOCKER.

| ID | Severidad | Archivo | Sección/línea | Problema | Evidencia | Corrección propuesta | Riesgo | Estado |
|---|---|---|---|---|---|---|---|---|
| STAT-MAJ-001 | MAJOR | `docs/experiments/E5_preprocesamiento.md`; `docs/memoria/cap4_marco_metodologico.md` | E5 l.51-56, 87-92, 112; cap4 l.95-107 | Los suelos de ruido (0,369/0,399/0,438/0,512), los deltas de F05 y la narrativa «a 30 s el mejor descriptor es la temperatura» no se reproducen con los datos y el código actuales (0,326/0,365/0,426/0,513; a 30 s la sonda lambda, declarada) | recálculo independiente §21 del informe; fechas del CSV (15:43) frente al dataset regenerado (19:43 UTC) y al commit de calibración | Decidir dataset canónico de E5: regenerar informe y capítulo desde la tabla actual, o restaurar el original bajo otro identificador | La conclusión cualitativa (120 s) se mantiene; el ejemplo «en miniatura» describe un dataset que ya no existe bajo ese identificador | **NOT_FIXED** (del dry-run) |
| STAT-MAJ-005 | MAJOR | `docs/memoria/cap5_resultados.md` | l.45, 52-62 | El capítulo concluye «el modelo temporal no supera al tabular» y «F05 se detecta en la mitad, anticipado» desde una ejecución, una semilla, 12 sesiones, con selección de época de la GRU sobre la misma validación; omite que el propio informe E7 ejecutó una sensibilidad con `synthetic_v3` donde el orden se invierte (+0,013) y F05 sube a F1 0,911 | E7 l.63-121; registros `E7_temporal_synthetic_v{2,3}.json` | Reescribir como inconcluso con las dos cifras y la sensibilidad, o ejecutar el reanálisis apareado por sesión con varias semillas | Presenta como negativo lo que es inconcluso; afecta a la lectura de PI.1 y a L-15 | OPEN |
| STAT-MAJ-006 | MAJOR | `docs/memoria/cap5_resultados.md`; `docs/experiments/E12_*`; `docs/matriz_validacion_pi.md` | cap5 l.82-92 y 98-105; E12 l.50-56; matriz l.167-173 | La tabla de recuperación del capítulo no se reproduce desde `experiments/E12_retrieval.json` ni desde `tables/E12_*.csv`; los denominadores difieren (dice «cinco casos» con Hit 0,25 = 1/4); el conjunto anotado cambió entre ejecuciones; el capítulo cita como registro el informe Markdown. La medición translingüe top-500 no tiene registro | comparación registro ↔ capítulo ↔ matriz | Declarar la ejecución canónica y regenerar la tabla desde el JSON; registrar la medición top-500 como artefacto | La conclusión cualitativa (0,00 semántica frente a 1,00 guiada) se mantiene; el capítulo mezcla dos ejecuciones | OPEN |
| STAT-MAJ-007 | MAJOR | `src/mecanico_ia_exp/abstention/sufficiency.py`; `docs/experiments/E15_suficiencia.md`; `docs/memoria/cap5_resultados.md` | sufficiency l.62-78; E15 l.213-227; cap5 l.123-125 | El criterio «precisión ≥ 0,93» no consta en ningún documento anterior al barrido; el barrido se calcula sobre la misma partición de la que salen los nueve casos; no existe script ni registro del barrido; precisión y cobertura por ventana sin N por sesión | tabla del barrido solo en un docstring y en el informe; `prereg-classification.md` l.117-128 reconoce el problema | Registrar el barrido como artefacto reproducible con criterio fechado, **o** declarar 0,80 como elección de política y retirar «calibrados, no elegidos» | Las nueve decisiones son idénticas para cualquier umbral en (0,5999, 0,9078], verificado: el resultado no depende del umbral. Lo que no se sostiene es la frase | OPEN |
| STAT-MAJ-008 | MAJOR | `docs/memoria/cap5_resultados.md`; `src/mecanico_ia_exp/experiments/sufficiency_runner.py` | cap5 l.66-71; runner l.76-86, 219-249 | La fila «Calibrado: ECE 0,085 · confianza media 0,886 · sesgo +0,009» no existe en ningún registro: el runner la imprime en consola y no la escribe en el JSON que el capítulo cita como fuente | inspección del runner y del JSON | Reejecutar E15 escribiendo el bloque de calibración (ECE, confianza, acierto, sesgo, bins, n por bin, antes y después) en el registro | No cambia el signo (ejecución determinista); cambia la clase de evidencia: la mitad del criterio de PI.1 es una transcripción de consola | OPEN |
| STAT-MIN-002 | MODERATE | `src/mecanico_ia_exp/data/exploration.py` | l.278-319 | El suelo de ruido se reporta como punto (p90) sin dispersión de las 30 repeticiones | sin cambios desde el dry-run | Reportar dispersión o intervalo del suelo | Bajo | **NOT_FIXED** |
| STAT-MIN-009 | MODERATE | `docs/memoria/cap5_resultados.md`; `docs/matriz_validacion_pi.md` | cap5 l.12-15, 52-54, 59; matriz l.57-61 | La memoria nunca dice que las 98 ventanas de validación son 12 sesiones, 2 por condición; cada tasa por clase descansa en dos trayectos; el capítulo llama «casos» a las ventanas | `tables/E5_reparto.csv` | Declarar N de sesiones junto a cada tabla por clase; sustituir «casos» por «ventanas» | Las cifras siguen válidas como descripción; las regularidades no pueden presentarse sin ese N | OPEN |
| STAT-MIN-010 | MODERATE | `docs/memoria/cap5_resultados.md`; `docs/matriz_validacion_pi.md` | cap5 l.127-140, 151-156; matriz l.39, 102-120 | De las nueve filas, cinco son la misma ventana bajo cinco condiciones; ABSENT, PARTIAL y DISTRACTOR existen para un solo fallo; «7 de 9» agrega observaciones dependientes | `tables/E15_suficiencia.csv` | Reportar N de ventanas distintas y N de fallos con cada condición junto a la tasa; acotar «la decisión cambia limpiamente entre las cuatro condiciones» al único fallo que las tiene | El diseño (mismo caso, cuatro condiciones) es el correcto; el agregado sugiere nueve observaciones independientes | OPEN |
| STAT-MIN-011 | MODERATE | `docs/memoria/cap5_resultados.md` | l.172-176, 189 | La «latencia media» (20,4 → 14,7 → 13,1 s) está dominada por un caso de 100,7 s; las medianas son 4,9 → 6,0 → 5,4 s: en el caso típico los adaptadores no son más rápidos | registros `E13_agente_transformers*.json` | Reportar mediana y máximo, o los nueve valores | M6 es descriptiva; el cambio es de redacción | OPEN |
| STAT-MIN-012 | MODERATE | `docs/memoria/cap4_marco_metodologico.md`; `docs/matriz_validacion_pi.md` | cap4 l.163; matriz l.37, 189, 233 | El criterio «supera con margen amplio» no fija margen; la conclusión dice «muy por encima del azar» donde el comparador medido es la clase mayoritaria | lectura | Fijar el margen o declararlo cualitativo; decir «clase mayoritaria» donde dice «azar» | Un criterio de refutación sin número no puede refutar | OPEN |
| STAT-MIN-013 | MODERATE | `docs/matriz_validacion_pi.md`; informes E6/E7 | matriz l.39, 65-73, 230 | La matriz combina cifras de tres momentos (4/6 y 7/9; 41 % frente al 43 % del registro vigente); los informes E6/E7 son anteriores a la recalibración | registros vigentes | Regenerar la matriz y los informes desde los registros, o fechar cada cifra con su ejecución | El capítulo 5 ya lo señala con `[RECONCILIAR]` | OPEN |
| STAT-MIN-014 | MODERATE | `docs/memoria/cap5_resultados.md` | l.64-74, 204-206 | ECE con 10 bins sobre 98 ventanas sin declarar bins ni n por bin, leído como «significa lo que aparenta» | `src/mecanico_ia_exp/evaluation/metrics.py` l.60-83 | Reportar bins y n por bin; cambiar el verbo a «reduce el error de calibración» | La dirección no cambia (el sesgo pasa de −0,140 a +0,009, robusto a los bins) | OPEN |
| STAT-INF-003, STAT-INF-004 | MINOR | E5, `exploration.py` | l.113-129 | Umbral p90 y cortes sin procedencia documentada; control no estratificado con ventanas previas al fallo en el grupo normal | sin cambios | Documentar | Bajo | **NOT_FIXED** |
| STAT-INF-015..020 | MINOR | varios | — | Selección de época sobre la partición reportada (solo la GRU); efecto sin escala en «gana en F03»; otros | informe §23 | Declarar | Bajo | OPEN |

## Reanálisis requerido

| Análisis | Condición | Qué haría falta |
|---|---|---|
| STAT-005 (E7) | Solo si se quiere sostener un orden entre GRU y bosque en cualquier dirección | Predicciones por ventana con `session_id`, varias semillas, diferencia apareada por sesión con bootstrap o permutación, selección de época sobre partición interna |
| STAT-009 (umbral) | Obligatorio si se mantiene «umbrales calibrados, no elegidos» | Barrido registrado en script y artefacto, con precisión y cobertura por ventana y por sesión, y criterio fechado antes de leer la tabla |
| STAT-004 (ECE) | Registro, no reanálisis | Reejecutar E15 escribiendo el bloque de calibración en el JSON |

`STAT-MAJ-001` y `STAT-MAJ-006` no exigen reanálisis: exigen decisión sobre la ejecución
canónica y regeneración documental.

## Decisiones que corresponden al autor

1. **Dataset canónico de E5**: regenerar informe y capítulo 4 desde la tabla actual, o
   restaurar el dataset original bajo otro identificador.
2. **E7 en el capítulo 5**: reportar la sensibilidad con `synthetic_v3` y la corrección del
   informe, o ejecutar el reanálisis; decidir cuál es el conjunto oficial.
3. **Ejecución canónica de E12** y registro de la medición translingüe.
4. **Umbral 0,80**: fechar el criterio y registrar el barrido, o declararlo política.
5. **Registro de la calibración** en E15.

## Fortalezas verificadas

- **No hay estadística ritual.** Ninguna prueba innecesaria, ningún p, ningún «significativo»
  sin prueba. El capítulo 4 declara el análisis como comparativo y por caso y lo cumple.
- **El control de E5 es correcto**: suelo de ruido por permutación de sesiones, en la unidad
  de independencia adecuada, con 30 repeticiones y semilla declarada.
- **Las magnitudes están reportadas en la escala de la métrica** en todos los análisis, y las
  decisivas son grandes: +0,805 de F1 macro frente a la clase mayoritaria, 0 frente a 1 en
  recuperación, cambio de decisión en abstención.
- **Las comparaciones del modelo de lenguaje son apareadas por construcción** (mismas nueve
  preguntas, mismo motor, decodificación determinista) y el recuento 9/9 se verificó desde
  los registros.
- **El control de comparaciones múltiples existe donde importa**: los 139 descriptores se
  comparan contra un suelo medido, no contra cero.
- **La cobertura acompaña a la abstención** en el capítulo 5 (3 de 5), que es la condición
  que hace interpretable cualquier tasa de abstención.
