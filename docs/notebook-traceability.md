# Trazabilidad: de la pregunta de investigación al notebook

**Actualizado:** 12 de octubre de 2026

Esta matriz existe para que el tribunal pueda ir de una afirmación del TFM a la evidencia que la
sostiene sin buscar. Se lee de izquierda a derecha:

> pregunta de investigación → objetivo → experimento → datos → metodología → notebook → gráfico →
> resultado → interpretación → limitación

## La pregunta principal

> ¿Puede un sistema inteligente híbrido identificar patrones de fallo no representados en su
> conocimiento disponible, generar hipótesis diagnósticas a partir del análisis contextual y
> longitudinal de datos OBD-II y validarlas mediante evidencia antes de incorporarlas como
> conocimiento reutilizable?

## PI.1 — Diagnóstico a partir de OBD-II

**Criterio vigente:** el diagnóstico supera a la clase mayoritaria con margen amplio y su confianza
se puede calibrar.

| Objetivo | Experimento | Datos | Metodología | Notebook | Figura | Resultado | Limitación |
|---|---|---|---|---|---|---|---|
| Comprobar que las señales contienen estructura diagnóstica | E2, E4 | `synthetic_sample`, 18 sesiones | descriptivos, delta de Cliff, auditoría de 12 comprobaciones | [`01_exploracion_obd`](notebooks/html/01_exploracion_obd.html) §6–§10 | `FIG-NB01-01`, `FIG-NB01-02`, `FIG-NB01-04` | ninguna señal separa por sí sola; las relaciones declaradas están presentes | el conjunto es sintético; seis señales son casi redundantes |
| Fijar la unidad temporal del análisis | E5 | `synthetic_v2` | estudio de ventana, 10–180 s | [`01_exploracion_obd`](notebooks/html/01_exploracion_obd.html) §11 | `FIG-NB01-05` | 120 s con paso de 60 s | compromiso global; perjudica al fallo de encendido |
| Evaluar sin fuga temporal | E5 | `synthetic_v2` | reparto **por sesión** | [`01_exploracion_obd`](notebooks/html/01_exploracion_obd.html) §12 | — | 48/12/12 sesiones | disjunto no es independiente |
| Establecer la línea base | E6 | `synthetic_v2`, validación | bosque, 400 árboles, semilla 20260901 | [`02_comparacion_modelos`](notebooks/html/02_comparacion_modelos.html) §7 | `FIG-NB02-01` | **F1 macro 0,8788** frente a 0,0741 de la clase mayoritaria | una ejecución; sin intervalo |
| Comprobar si el modelo temporal aporta | E7 | `synthetic_v2`, validación | GRU bidireccional, 19 014 parámetros | [`02_comparacion_modelos`](notebooks/html/02_comparacion_modelos.html) §7–§8 | `FIG-NB02-01`, `FIG-NB02-02` | **0,8230: NO supera** a la línea base | representación y estimador cambian a la vez |
| Caracterizar el tipo de error | E6, E7 | ídem | matriz de confusión | [`02_comparacion_modelos`](notebooks/html/02_comparacion_modelos.html) §9 | `FIG-NB02-03` | el bosque falla por omisión; la red cruza diagnósticos | vale para esta partición, no en general |
| Comprobar que la confianza es calibrable | E6, E7 | ídem | ECE de diez tramos | [`02_comparacion_modelos`](notebooks/html/02_comparacion_modelos.html) §10 | `FIG-NB02-04` | ECE 0,1439 y 0,1317: **los dos sobreconfiados** | ninguno de los dos calibra; el ECE es frágil con 98 ventanas |
| Sostener el diagnóstico fuera de validación | E19 | `synthetic_v2`, **prueba** | política v2.2 congelada | [`03_analisis_e19`](notebooks/html/03_analisis_e19.html) §6 | `FIG-NB03-01` | se sostiene sobre prueba | denominadores pequeños |

**Pregunta abierta dentro de PI.1.** *¿En qué tipos de fallo el contexto temporal aporta señal
diagnóstica adicional y en cuáles no?* **Sin responder**, por dos confusores documentados en
[`02_comparacion_modelos`](notebooks/html/02_comparacion_modelos.html) §11 y `FIG-NB02-05`: volumen y
calibración del generador cambian juntos entre `v2` y `v3`; representación y estimador cambian juntos
entre los dos recorridos. El diseño para responderla está en `docs/diseno-pi1/` y **no se ha
ejecutado**. No habrá notebook hasta que haya resultados.

## PI.2 — Explicación trazable

| Objetivo | Experimento | Datos | Metodología | Notebook | Resultado | Limitación |
|---|---|---|---|---|---|---|
| Anclar toda afirmación en observación o documento | E14, E15 | goldset de 17 casos | cobertura de afirmaciones | **pendiente** (FULL) · cifras en [`03_analisis_e19`](notebooks/html/03_analisis_e19.html) §6 | cobertura 1,00 en las condiciones con evidencia | exige el corpus, que no se redistribuye |

## PI.3 — Reconocimiento de insuficiencia

**Es la subpregunta que vertebra el trabajo.**

| Objetivo | Experimento | Datos | Metodología | Notebook | Figura | Resultado | Limitación |
|---|---|---|---|---|---|---|---|
| Comprobar que el sistema calla cuando no sabe | E15 | validación | EXPLAIN/ABSTAIN al retirar evidencia | **pendiente** (FULL) | — | 15/17 | revisión no ciega, declarada |
| Medir qué aporta cada componente | E18 | validación | cuatro ablaciones | **pendiente** | — | sin criterio de suficiencia, falsa confianza 6/9; con umbral único, 9/9 | sobre validación; **sobre prueba, pendiente** |
| Medir la falsa confianza sobre prueba | E19 | **prueba** | criterio compuesto, umbrales congelados | [`03_analisis_e19`](notebooks/html/03_analisis_e19.html) §6–§9 | `FIG-NB03-01`, `FIG-NB03-02`, `FIG-NB03-03` | **falsa confianza 0/14**; abstención innecesaria 2/8; cobertura 6/10 | **0/14 no es riesgo cero**: 14 observaciones de 7 sesiones |
| Comprobar que no es una política trivial | E19 | prueba | comparación con abstenerse/explicar siempre | [`03_analisis_e19`](notebooks/html/03_analisis_e19.html) §12 | — | obtiene el cero de la conservadora reteniendo 6 de 10 respuestas | sin modelo de coste que pondere las dos cosas |
| Informar los diagnósticos incorrectos | E19 | prueba | sin descartarlos | [`03_analisis_e19`](notebooks/html/03_analisis_e19.html) §9 | — | 4 de 22; el sistema se abstuvo en todos | no los detecta: los filtra por confianza baja |

## PI.4 — Rechazo de evidencia no pertinente

| Objetivo | Experimento | Estado | Notebook | Por qué |
|---|---|---|---|---|
| Rechazar un distractor plausible pero inaplicable | E17 | **invalidado** | ninguno | con el filtro de motor, la condición recuperaba **los mismos** fragmentos que la condición parcial: era la condición parcial contada dos veces. Criterio de rediseño pre-registrado en `methodology/politica-condicion-distractor.md`; **no construido** |

**Mientras el rediseño no exista, las condiciones realmente independientes son cuatro y no cinco**, y
PI.4 no puede interpretarse. Está así en el índice de experimentos y en las limitaciones.

## De la figura a la sección del TFM

| Figura | Notebook | De dónde salen sus números | Capítulo |
|---|---|---|---|
| `FIG-NB00-01_recorrido` | `00` | arquitectura, dibujada desde su descripción | 4, marco metodológico |
| `FIG-NB01-01_sesion_sana` | `01` | `data/samples/synthetic_sample.parquet` | 4, datos |
| `FIG-NB01-02_normal_vs_fallo` | `01` | ídem | 4, datos |
| `FIG-NB01-03_termostato_calentamiento` | `01` | sesiones regeneradas, **ilustrativas** | 5, discusión del límite físico |
| `FIG-NB01-04_correlaciones` | `01` | ídem muestra | 4, datos |
| `FIG-NB01-05_estudio_ventana` | `01` | `artifacts/tables/E5_estudio_ventana.csv` | 4, preprocesado |
| `FIG-NB02-01_agregado` | `02` | `experiments/E6_*.json`, `E7_*.json` | 5, resultados |
| `FIG-NB02-02_por_clase` | `02` | ídem | 5, resultados |
| `FIG-NB02-03_confusion` | `02` | `artifacts/tables/E6_*_confusion_*.csv`, `E7_*` | 5, análisis de errores |
| `FIG-NB02-04_calibracion` | `02` | `experiments/E6_*.json`, `E7_*.json` | 5, calibración |
| `FIG-NB02-05_confusor_volumen` | `02` | los cuatro registros de E6 y E7 | 5, limitaciones |
| `FIG-NB03-01_primario` | `03` | `artifacts/tables/E19_evaluacion_final_v3.csv` | 5, evaluación final |
| `FIG-NB03-02_decisiones` | `03` | ídem | 5, evaluación final |
| `FIG-NB03-03_abstenciones` | `03` | ídem | 5, análisis de la abstención |

Las figuras de los notebooks salen en `notebooks/salida/<notebook>/`, en PNG y SVG. **No sustituyen
a las publicadas** de `artifacts/figures/`, que no se sobrescriben.

## Resultados negativos, y dónde están explicados

Un trabajo que solo documentara lo que funcionó no serviría como evidencia.

| Resultado negativo | Dónde se explica |
|---|---|
| El modelo temporal no supera a la línea base | [`02`](notebooks/html/02_comparacion_modelos.html) §7, §12 |
| La explicación «faltaban datos» quedó retirada | [`02`](notebooks/html/02_comparacion_modelos.html) §11 · `SUPERSEDED` en el informe de E7 |
| La red genera diagnósticos cruzados que el bosque no genera | [`02`](notebooks/html/02_comparacion_modelos.html) §9 |
| Ninguno de los dos modelos está calibrado | [`02`](notebooks/html/02_comparacion_modelos.html) §10 |
| Dos abstenciones innecesarias de ocho | [`03`](notebooks/html/03_analisis_e19.html) §8 |
| Cuatro diagnósticos incorrectos de veintidós | [`03`](notebooks/html/03_analisis_e19.html) §9 |
| La condición con distractor no medía lo que decía | [`00`](notebooks/html/00_introduccion.html) §8 |
| Dos cifras del termostato publicadas sin registro | [`00`](notebooks/html/00_introduccion.html) §8 · marcadas no utilizables |
| Ventanas etiquetadas sin señal observable del fallo | [`01`](notebooks/html/01_exploracion_obd.html) §8, §14 |

## Lo que no se puede reproducir, y por qué

| Qué | Por qué | Qué se entrega en su lugar |
|---|---|---|
| El corpus documental | manual de taller, propiedad del fabricante | los registros de E10–E12 y sus tablas |
| Los pesos del adaptador LoRA | decenas de MB, no versionables con sentido | el registro de su ajuste |
| `synthetic_v2` y `v3` completos | `data/raw/**` fuera del control de versiones | la muestra de 18 sesiones **y** el generador, que los reconstruye bit a bit |
| El reentrenamiento de la GRU | MPS no es bit a bit determinista | las cifras de su registro |
| Una reejecución de E19 | el conjunto de prueba se abre una vez | los artefactos congelados, que el notebook reanaliza |
