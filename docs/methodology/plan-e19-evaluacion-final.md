# Plan de E19, la evaluación final, y gate previo a abrir el conjunto de prueba

**Fecha:** 1 de octubre de 2026 · **Estado:** plan, **el conjunto de prueba sigue cerrado**. Este
documento no abre nada: fija qué debe estar cerrado antes de abrirlo, qué se medirá, con qué
política y en qué orden. · **Convocatoria objetivo:** diciembre de 2026, con el informe de
seguimiento 2 el 6 de noviembre y el depósito el 4 de diciembre.

El cierre técnico del conjunto de prueba está en el código: el cargador lanza una excepción y
abrirlo exige una declaración explícita y una razón por escrito, que se imprime en la salida de la
ejecución. Este plan es esa razón escrita, y no surte efecto hasta que el autor lo apruebe.

## 1. Gate previo, con su estado

Ninguna de estas comprobaciones se da por superada por haberse escrito: cada una dice dónde está
su evidencia.

| # | Comprobación | Estado | Evidencia |
|---|---|---|---|
| 1 | Pregunta de investigación acotada y objetivos alineados con ella | **PASS** | la pregunta se enuncia una vez, en el capítulo 1; OE3 y OE5 reescritos el 15 de septiembre; auditoría diferencial frente a la versión amplia en `docs/audits/scope_change/` |
| 2 | E18 cerrado, con sus limitaciones declaradas | **PASS** | cuatro ablaciones ejecutadas, registros `E18_ablacion_A1..A4.json`, informe de fase y Tabla 5.8; `A2` declarada inconclusa con su enmienda, y la variante tratada como medición nueva |
| 3 | RERUN-B cerrado | **PASS** | registros con sufijo de política para los tres modos, informe de fase, y dos pruebas de regresión que reproducen el bypass y su cierre |
| 4 | Falsa confianza y abstención innecesaria verificadas | **PASS** | definidas en el capítulo 4 (M5) con sus denominadores y unidades; publicadas en la Tabla 5.6 con ejecuciones y ventanas independientes; recalculadas por un segundo camino en `A4`, que coincide celda a celda con la política de referencia |
| 5 | La condición con distractor sigue declarada bajo diagnóstico | **PASS** | no se ha rediseñado: el capítulo 5 dice que con el filtro de motor no añade ningún distractor que la condición parcial no tuviera, y PI.4 figura como no sostenida con el diseño actual |
| 6 | Segunda versión de la política preparada para congelarse | **PASS** | implementada, probada, medida en los tres modos y seleccionable por parámetro, con artefactos que no pueden sobrescribir los de la política anterior |
| 7 | Conjunto de prueba cerrado | **PASS** | ninguna cifra de la memoria procede de él; tres pruebas comprueban el cierre y el mensaje de la excepción |

Con los siete en PASS, lo que falta para E19 no es verificación: es la decisión del autor de abrir
el conjunto y la ejecución misma.

## 2. Qué se mide en E19, y con qué se compara

La evaluación final no introduce experimentos nuevos: repite sobre el conjunto de prueba las
mediciones que el capítulo 5 publica sobre validación, con **la segunda versión de la política**
como canónica.

| Bloque | Qué se mide | Comparación |
|---|---|---|
| Diagnóstico | exactitud, F1 macro y calibración del bosque sobre las 98 ventanas de prueba | frente a la clase mayoritaria de esa partición y frente a las cifras de validación |
| Suficiencia | las dos tasas de error con sus denominadores y unidades, y la cobertura, sobre los casos anotados que se construyan con ventanas de prueba | frente a las dos políticas triviales de referencia, recalculadas sobre la misma partición |
| Trazabilidad | afirmaciones con observación, con cita y con soporte | frente a validación, declarando que el soporte sigue siendo una propiedad del verificador mientras no haya anotación independiente |
| Redactor | salidas válidas, respeto del veredicto y citas fuera de lo entregado | frente a validación, con el adaptador que esté vigente y declarando si se reentrenó |

**Qué no se mide:** la condición con distractor, que no puede interpretarse hasta su rediseño, y la
variante léxica de la ablación, que es una medición nueva y no entra en la evaluación final.

## 3. Transición de política, versionada y explícita

| | Política anterior | Política nueva |
|---|---|---|
| Qué cambia | el requisito de la puerta de códigos se exige siempre | el requisito se lee de la declaración del diagnóstico |
| Qué sostiene | todas las cifras publicadas hasta el 1 de octubre de 2026 | la evaluación final |
| Artefactos | `E15_suficiencia*.json` sin sufijo | registros con sufijo de política, y los de E19 ya bajo la nueva |
| Regla | **no se reabren las cifras publicadas.** La transición entra con el conjunto de prueba, no antes | el capítulo 5 dirá, en la tabla de resultados finales, bajo qué política se midió cada bloque |

## 4. Orden de ejecución

1. Construir los casos anotados sobre ventanas de la partición de prueba, con la misma estructura
   del conjunto actual y las condiciones de evidencia completa, parcial y ausente. La anotación se
   cierra **antes** de ejecutar nada.
2. Declarar la apertura del conjunto de prueba con su razón escrita, y registrarla.
3. Medir el diagnóstico y la calibración sobre prueba.
4. Medir suficiencia y redacción, con la política nueva, en modo oracular y no oracular.
5. Escribir el informe de fase y llevar las cifras al capítulo 5 con su procedencia, su semilla, su
   versión, sus parámetros y su unidad de análisis.
6. Reevaluar con los auditores independientes y el tribunal simulado, y cerrar el capítulo 6.

Entre el paso 1 y el 2 hay un punto de no retorno: una vez abierto el conjunto, ningún umbral,
criterio ni anotación puede ajustarse. Lo que esté mal ajustado se queda así y se declara.

## 5. Qué queda fuera de E19

El rediseño de la condición con distractor, el reentrenamiento del adaptador del modelo de lenguaje,
la anotación de afirmaciones admisibles que convertiría la trazabilidad en una medición
independiente, la validación externa con telemetría de vehículos reales y la variante léxica de la
ablación. Las cinco están declaradas como trabajo posterior, y ninguna condiciona la respuesta a la
pregunta dentro del alcance acordado.
