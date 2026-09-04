# Hallazgo ENGINE-FILTER-PERMISSIVE

**Identificador:** `ENGINE-FILTER-PERMISSIVE` · **Fecha:** 4 de septiembre de 2026 ·
**Clase:** **refutación de una afirmación publicada** · **Detectado por:** evaluación
independiente de recuperación, `RAG-MAJ-032` · **Estado:** afirmación retirada; política de
sustitución propuesta y **sin implementar**.

## 1. Afirmación anterior, publicada

En `docs/experiments/hallazgo-lexical-support-confound.md` y en
`docs/methodology/politica-suficiencia-v2.md`:

> «El filtro de aplicabilidad por motor **sí funciona** y se aísla del problema: en las
> condiciones sin filtro, el procedimiento del motor incorrecto se degrada a coincidencia
> parcial y no se acepta.»

## 2. Evidencia que la refuta

Con el filtro **activo**, en la condición de distractor de la fuga de vacío, el procedimiento
del motor incorrecto entra en el conjunto de candidatos con aplicabilidad de **coincidencia
exacta**, papel de **procedimiento diagnóstico** y **el código esperado**. Pasa tres de las
cuatro condiciones de soporte. Lo único que lo detiene es que no menciona la señal observada.

Es decir: la defensa que se atribuía al filtro de motor la estaba haciendo el vocabulario.

## 3. Causa, y son dos defectos distintos

**Primero, los metadatos.** Hay 48 fragmentos pertenecientes a secciones de un motor que
declaran **los tres motores a la vez**. La sección dice una cosa y el fragmento otra.

**Segundo, el predicado.** De 6 158 fragmentos, **4 175 no declaran motor alguno**, y el
predicado de aplicabilidad los deja pasar siempre. Tratar «no consta» como «vale para todos» es
la misma clase de defecto que `SIGNAL_MAPPING_UNAVAILABLE` y `EMPTY-DTC-GATE-BYPASS`: **ausencia
de información tratada como ausencia de restricción**. Es la tercera vez que aparece el mismo
patrón en este verificador, y esa recurrencia es en sí un resultado del trabajo.

## 4. Qué se puede afirmar ahora

**No se sostiene** que el filtro de aplicabilidad por motor proteja frente al procedimiento del
vehículo equivocado.

**Se sostiene**, con la salvedad de que el mecanismo es otro del que se creía: en la condición
sin filtro, el procedimiento del motor incorrecto **no llega a sostener** una afirmación. El
mecanismo real es la exigencia de **coincidencia exacta** al construir las afirmaciones, no las
cuatro condiciones del verificador ni el predicado de búsqueda.

**No se dirá que «funciona parcialmente»** hasta medirlo con una política explícita.

## 5. Política de aplicabilidad propuesta, sin implementar

Cinco estados, con lo que cada uno autoriza. **Pendiente de auditoría antes de escribir una
línea de código**: si los evaluadores consideran que la taxonomía no encaja con la estructura
del corpus, no se implementa.

| Estado | Cuándo | ¿Evidencia suficiente por sí sola? |
|---|---|---|
| `EXACT_MATCH` | el fragmento declara el motor del vehículo | **sí** |
| `COMPATIBLE` | declara un motor documentado como equivalente para ese sistema | **sí, con la justificación registrada** |
| `UNKNOWN` | no declara motor | **no** |
| `MULTI_ENGINE` | declara varios motores, entre ellos el del vehículo | **no**, salvo evidencia adicional |
| `INCOMPATIBLE` | declara motor y ninguno es el del vehículo | **rechazado** |

El estado `MULTI_ENGINE` es nuevo y existe por los 48 fragmentos del defecto: hoy se
confunden con coincidencia exacta.

## 6. Lo que hay que medir antes de afirmar nada

Cuántos fragmentos caen en cada estado, y qué le ocurre a cada condición del experimento
central al aplicar la política. Sin esa medición, la única afirmación disponible es la
refutación de la anterior.
