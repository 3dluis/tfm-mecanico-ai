# Diagnóstico de la primera entrega

Estado de la memoria a 10 de septiembre de 2026, antes de la entrega al tutor. Alcance:
preliminares, capítulos 1 a 4 y bibliografía. Los capítulos 5 y 6 no se cierran.

`PI_STATUS = LOCKED` · `SYNTHETIC_DATA_STATUS = EXPERIMENTAL_BASE` ·
`REAL_OBD_DATA_STATUS = EXTERNAL_VALIDATION_PENDING` · `DISTRACTOR_STATUS = BAJO_DIAGNÓSTICO`

## Fuentes consultadas antes de editar

Memoria en `docs/memoria/` (siete ficheros); plantilla oficial `24-25 Plantilla TFM MUIA2.docx`;
decisiones en `research/decisions/` y `docs/memoria/preguntas-abiertas-al-director.md`; índice de
fases en `docs/experiments/README.md`; registros de ejecución en `experiments/`; registro de
búsqueda documental y lista maestra en `research/references/`; registro de limitaciones en
`research/limitations-register.md`; definiciones de los once skills en `TFM/.claude/skills/`.

El estado del proyecto **no se infirió del texto de la memoria**: cada afirmación de este
diagnóstico se contrastó con el código o con un registro.

## Estado por apartado

| Apartado | Estado | Observación |
|---|---|---|
| Resumen y abstract | READY | 309 palabras en formato IMRyD, cinco palabras clave, abstract en inglés añadido |
| Capítulo 1 · Introducción | MINOR_REVISION | 4,1 páginas frente a una recomendación de 5-10; falta desarrollo del vacío en 1.1 |
| Capítulo 2 · Objetivos | MINOR_REVISION | objetivo general alineado con la pregunta; dos de sus cinco términos sin objetivo específico que los desarrolle |
| Capítulo 3 · Marco teórico | READY | 10,6 páginas, dentro de la recomendación; base conceptual del patrón no representado incorporada |
| Capítulo 4 · Marco metodológico | MINOR_REVISION | completo; pendiente de que la reejecución canónica cierre las cifras de recuperación |
| Bibliografía | MINOR_REVISION | 144 referencias, 110 con identificador verificado; edición de APA sin decidir (P-04) |
| Capítulo 5 · Resultados | NOT_REQUIRED_FIRST_SUBMISSION | congelado; cuatro acciones editoriales y `CORR-MAJ-001` esperando el deshielo |
| Capítulo 6 · Conclusiones | NOT_REQUIRED_FIRST_SUBMISSION | estructura provisional; limitaciones al día |

## Hallazgos

### H-01 · `UNREPRESENTED_PATTERN_VALIDATION = BLOCKED`

**Capítulo 4, población y muestra · CRÍTICO · toca el primer término de la pregunta.**

El generador produce seis clases etiquetadas y el detector se entrena sobre esas mismas seis. La
recuperación se guía por un diccionario que asocia cada clase a sus códigos de avería. La
partición de test cierra **casos**, no clases: búsqueda de `holdout`, `held_out`,
`excluded_class` y `leave_one_class` en `src/`, cero coincidencias.

Un fallo generado sintéticamente está, por construcción, representado en el conocimiento del
detector y del corpus. **Evidencia necesaria para desbloquear:** definición operacional de «no
representado», una condición que retenga al menos una clase fuera del entrenamiento y del
diccionario, y una medida del conocimiento paramétrico del modelo de lenguaje sobre esa clase.

**Corregible ahora: no.** Registrado como `L-21`, sin tocar la pregunta.

### H-02 · `REUSABLE_KNOWLEDGE_VALIDATION = PENDING`

**Capítulo 2 y capítulo 4 · CRÍTICO · toca el último término de la pregunta.**

No existe mecanismo que incorpore una hipótesis validada ni que la recupere después: cero
coincidencias de `reutilizab`, `knowledge_base` y `write_back` en `src/`. Tampoco existe la
barrera inversa que impediría a una hipótesis no validada entrar en memoria, porque no hay
memoria. Ninguna de las veinte fases del plan lo contempla.

**Corregible ahora: no.** Registrado como `L-22`. No se afirma en ningún punto que esté
demostrado, y no se elimina de la pregunta.

### H-03 · Dos términos del objetivo general sin objetivo específico

**Capítulo 2 · MAYOR.** El objetivo general compromete cinco capacidades; OE1-OE5 desarrollan
tres. La plantilla dice que los objetivos «no son deseos para el futuro». Declarado en el
capítulo 2, en el 4 y en el 6. **Requiere decisión del autor**, no corrección editorial.

### H-04 · Capítulo 1 por debajo de la extensión recomendada

**MENOR.** 4,1 páginas frente a 5-10 recomendadas. La sección 1.2 está en su proporción; el
margen está en 1.1, donde la justificación del vacío se apoya en el capítulo 3 en lugar de
anunciarlo. **Corregible ahora: sí**, con contenido real, no con relleno.

### H-05 · Reconciliación bibliográfica abierta

**MENOR.** El registro de búsqueda declara 153 referencias incluidas y la lista maestra contiene
144. La memoria usa 144, que es lo que la lista sostiene. La marca
`[VERIFY_SOURCE: reconciliar 144 vs 153 antes del depósito]` sigue abierta desde el 1 de
septiembre.

### H-06 · La memoria no contiene ninguna figura

**MENOR, estructural.** Cero imágenes, diagramas o esquemas gráficos en los siete ficheros. No
se crean: una figura de arquitectura es una decisión de contenido. Candidatas anotadas.

### H-07 · Cifras de recuperación pendientes de reejecución canónica

**MAYOR, ya declarado.** `L-20`. Afecta a cuatro tablas del capítulo 5 y a los datos de ajuste
del redactor. No bloquea la primera entrega porque los capítulos afectados no se entregan como
cerrados.

## Correcciones aplicadas en esta revisión

Documentadas una a una en `docs/audits/full_memory_review/12_CORRECTION_LOG.md`,
`14_TABLES_FIGURES_INVENTORY.md` y `15_PENDING_CH5_INSERTIONS.md`.

---

> **Superado por `ADR-004`, 12 de septiembre de 2026.** La dirección resolvió `SD-01` a favor de
> la pregunta acotada y descartó la formulación amplia. Lo que este documento registra sobre los
> componentes de esa formulación era cierto cuando se escribió y se conserva como tal; ya no
> describe el alcance vigente del trabajo.
