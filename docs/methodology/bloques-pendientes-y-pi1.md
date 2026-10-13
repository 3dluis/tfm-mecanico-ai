# Dos bloques de trabajo: pendientes del tutor y reejecución de PI.1

**Fecha:** 12 de octubre de 2026 · **Estado:** plan, con las dependencias **comprobadas** en el
código y en los manifiestos, no supuestas.

Los tres pendientes del tutor son prioritarios para la entrega final y PI.1 no puede consumir su
tiempo. El trabajo se organiza en dos bloques y lo primero es saber qué los une de verdad.

## 1. Estado real de los tres pendientes

### P1 · Rediseño de la condición con distractor

**Estado: criterio pre-registrado, nada construido.**

Lo que hay: `docs/methodology/politica-condicion-distractor.md`, del 4 de septiembre, fija **antes de
construir nada** cuatro requisitos que una condición con distractor tiene que cumplir —`D-1` el
distractor entra en el conjunto recuperable; `D-2` el conjunto recuperado difiere del de la condición
parcial; `D-3` el distractor es semánticamente plausible; `D-4` no es evidencia suficiente, por una
razón declarada de antemano—. Y declara qué hacer si no puede construirse: **eliminar la condición
del experimento principal** y pasarla a limitación. Tres condiciones reales valen más que cuatro con
una falsa.

Lo que falla hoy: con el filtro de motor activo, la condición recupera **exactamente los mismos
fragmentos** que la condición parcial en los tres fallos. El distractor declarado en el conjunto
anotado es, en los cinco casos, un procedimiento del motor **LF**, y el filtro lo bloquea antes de
que llegue al verificador. El resultado histórico se conserva con la etiqueta
`DISTRACTOR_V1_INVALID_AS_INDEPENDENT_CONDITION`.

**Lo que no hace falta, y conviene saberlo:** no hace falta ingerir documentos nuevos. Las variantes
de corpus se construyen **por exclusión en el momento de la consulta** —`exclude_documents` y
`exclude_chunks` en `rag/store.py`—, no modificando el corpus. El rediseño es una cuestión de **qué
documento se elige como distractor**: uno del motor Z6 o ZJ, que pase el filtro, y que sea
insuficiente por sistema, alcance o versión en lugar de por motor.

**Lo que sí hace falta, y es la dependencia dura:** el conjunto anotado
`configs/goldset_mazda3_bk.yaml` está fijado **por huella** en el manifiesto de E19
(`annotated_set.file_sha256_16 = 7fadc49fc7daaad1`, comprobado: coincide hoy). **Editarlo rompería
la verificación de la congelación de E19.** El rediseño tiene que escribir un **fichero nuevo**, no
modificar ese. Desde hoy el conjunto anotado está en el censo de artefactos históricos, de modo que
una edición accidental se detecta.

### P2 · Reentrenamiento del adaptador sin contaminación

**Estado: diagnosticado y declarado como limitación abierta; no ejecutado.**

El adaptador LoRA `models/slm_lora_v2` se entrenó con datos generados **antes** de la corrección del
espacio de embeddings mezclado. La reejecución pre-registrada `RERUN-A`, del 13 y 14 de septiembre,
comprobó que las **decisiones** no cambiaron y que los **conjuntos recuperados** sí, en 10 de 17
casos; por el criterio fijado de antemano, «sin efecto detectable con este instrumento». Lo que
quedó abierto es el adaptador, y así figura en `docs/limitations.md`.

**La dependencia con E19:** el manifiesto de E19 fija el redactor
—`transformers-lora@slm_lora_v2`, con el modelo base, su revisión y las huellas de los pesos del
adaptador—. Un adaptador nuevo **en un directorio nuevo** (`models/slm_lora_v3`) no toca nada de
eso. Lo que no puede hacerse es reentrenar **sobre** `slm_lora_v2`.

`run_training_data` escribía su registro en `experiments/E13b_training_data.json`, ruta fija: desde
hoy toma etiqueta y se niega a sobrescribir.

### P3 · Ablaciones de E18 sobre el conjunto de prueba

**Estado: ejecutadas sobre validación el 1 de octubre; sobre prueba, ahora posibles y no hechas.**

E18 midió las cuatro ablaciones sobre los diecisiete casos anotados de `synthetic_v2` en modo
oracular, **sobre validación**, porque el conjunto de prueba estaba cerrado. Ya no lo está: E19 lo
abrió el 12 de octubre. Repetirlas sobre prueba es por tanto posible y es el pendiente más directo
de los tres.

Dos cosas que exige, y las dos están implementadas desde hoy:

1. **Etiqueta obligatoria.** `run_ablations` escribía en `experiments/E18_ablacion_{A1..A4}.json` y
   `tables/E18_ablacion_{A1..A4}.csv`, rutas fijas: una repetición habría borrado la ejecución
   publicada. Sobre una partición distinta de validación la etiqueta es **obligatoria** y el
   ejecutor falla sin ella.
2. **Una apertura más del conjunto de prueba, registrada.** `run_ablations` toma ahora `particion`,
   `allow_test` y `reason`, y la razón queda en el artefacto. El ejecutor no puede obligar a
   escribir el registro de aperturas, pero sí a declarar el motivo; escribir la entrada en
   `docs/methodology/registro-aperturas-test.md` sigue siendo obligación del protocolo, **antes** de
   ejecutar.

## 2. Los dos bloques

**BLOQUE A — pendientes del tutor.** P3 → P2 → P1, en ese orden, por los motivos de la sección 3.

**BLOQUE B — reejecución controlada de PI.1.** Fases A a I de `docs/diseno-pi1/10-plan-reejecucion.md`.

## 3. Dependencias reales, comprobadas

### 3.1 Dentro del bloque A: P3 antes de P1

Es la única dependencia de orden **estricta** que hay, y no es obvia.

Las ablaciones de E18 sobre prueba solo son interpretables si se comparan con las de validación, y
para eso el corpus y el espacio de embeddings tienen que ser **los mismos**. El rediseño del
distractor cambia qué documento llega al verificador en las condiciones con distractor; si además
obligase a relajar el filtro de motor o a reingerir algo, cambiaría la recuperación de **todos** los
casos. Hacer P1 primero dejaría la comparación de E18 sin referencia.

**P3 antes de P1.** P2 puede ir en medio: no toca ni el corpus ni el índice.

### 3.2 Entre el bloque A y el bloque B: independientes en el dato, no en el artefacto

| Recurso | Lo toca A | Lo toca B | ¿Choca? |
|---|---|---|---|
| Conjuntos sintéticos | no | sí, **crea `synthetic_v4`**; `v1`, `v2` y `v3` no se tocan | **no** |
| `data/processed/` | no | sí, con prefijo `synthetic_v4_` | **no** |
| Corpus documental y espacio de embeddings | **sí** (P1) | no | **no** |
| Adaptador LoRA y redactor | **sí** (P2) | no | **no** |
| Conjunto anotado `goldset_*.yaml` | **sí** (P1), en fichero nuevo | no | **no**, si es fichero nuevo |
| Conjunto de prueba | **sí** (P3): una apertura más | **no**: PI.1 mide sobre validación | **no** |
| `experiments/`, `tables/`, `figures/`, `models/` | sí | sí | **sí**, y se resuelve con etiqueta |
| Modelos de diagnóstico (bosque, GRU) | no | sí, con protocolo revisado y etiqueta propia | **no** |

**La conclusión es que A y B pueden ejecutarse en paralelo**, con dos condiciones:

1. **Toda ejecución lleva etiqueta.** Los siete ejecutores la toman y comprueban sus destinos antes
   de escribir el primero; un test parametrizado los recorre y falla si se añade uno sin ella.
2. **El censo se verifica después de cada bloque.** 144 artefactos con su huella SHA-256 en
   `configs/artefactos_historicos.json`. `tables/`, `figures/`, `data/` y `models/` están fuera del
   control de versiones y no tienen otra protección.

### 3.3 Lo que sí compite: el tiempo

El coste de cómputo de B es pequeño —unos 35 minutos, 120 celdas— y el de A, menor. **Lo que compite
no es la máquina: es el análisis.** Por eso el orden propuesto es terminar A antes de ejecutar las
fases de B que producen cifras, y usar el tiempo de preparación de B mientras A está en marcha.

## 4. Orden propuesto

| # | Qué | Bloque | Depende de | Abre prueba |
|---|---|---|---|---|
| 1 | Entrada en el registro de aperturas, **antes** de ejecutar | A | — | — |
| 2 | **P3**: E18 sobre prueba, cuatro ablaciones con etiqueta | A | 1 | **sí**, cuarta apertura |
| 3 | **P2**: adaptador en `models/slm_lora_v3`, con datos posteriores a RERUN-A | A | — | no |
| 4 | **P1**: distractor nuevo en un conjunto anotado nuevo, contra los cuatro requisitos | A | 2 | no |
| 5 | Fases A–D de PI.1: correcciones, procedencia, `synthetic_v4`, subconjuntos | B | — | no |
| 6 | Fases E–F: protocolo simétrico y las 120 celdas | B | 5 | no |
| 7 | Fases G–I: análisis por fallo, matriz de conclusiones, trazabilidad | B | 6 | no |

Los pasos 3 y 5 no dependen de nada y pueden adelantarse. El paso 4 espera al 2.

## 5. Lo que este plan no decide

**Si P1 puede construirse.** El criterio está fijado y es previo al resultado: si con el corpus
actual no se puede construir una condición que cumpla los cuatro requisitos **sin introducir casos
artificiales**, se elimina del experimento principal y pasa a limitación. Esa decisión se toma
cuando el paso 4 se ejecute, comprobando `D-1` y `D-2` **antes** de mirar ningún veredicto.

**Si el adaptador nuevo sustituye al anterior.** P2 produce un adaptador en un directorio nuevo. Que
pase a ser el redactor canónico es una decisión del autor, y mientras no se tome, el redactor de E19
sigue siendo `slm_lora_v2`, que es lo que su manifiesto fija.

**Nada de PI.1 se ejecuta sin autorización.** Las fases A–I están diseñadas y no iniciadas.
