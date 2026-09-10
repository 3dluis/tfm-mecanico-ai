# 12 · Registro de correcciones

Una entrada por iteración del ciclo IMPLEMENTAR → AUDITAR → CLASIFICAR → CORREGIR →
REEVALUAR → CERRAR. Cada corrección declara el hallazgo que la origina, la evidencia
que la sostiene y cómo se verifica que quedó cerrada.

---

## Iteración 3 · 10 de septiembre de 2026 · commit `d0fa412`

**Entrada:** informe `tutor-reports/TUTOR-CIERRE-20260910.md` sobre `b0e13e2`, veredicto
BLOCKED, ocho acciones bloqueantes declaradas todas editoriales.

**Resultado:** cuatro cerradas, cuatro bloqueadas por la congelación del capítulo 5, un
hallazgo nuevo levantado al verificar una de ellas.

### Cerradas

| Hallazgo | Corrección | Verificación |
|---|---|---|
| `TUTOR-MAJ-020` | El capítulo 4 decía «cuatro más pertenecen al tramo pendiente»; el índice da seis. Se corrige a seis y se nombran (E3, E14, E16, E18, E19, E20); se añade el recuento de cerradas | `docs/experiments/README.md` líneas 10-29: once cerradas, E10 parcial, ocho pendientes de las que dos ya se nombraban aparte |
| `TUTOR-MIN-026` | `cap1` afirmaba registro con métricas para las veinte fases; ahora declara once cerradas y remite al capítulo 4 | `cap1` y `cap4` dan el mismo recuento |
| `TUTOR-MAJ-021` (parte no bloqueada) | `cap6` acotaba el «sí puede» con «siete ejecuciones evaluables, de nueve», que es la columna de *salidas válidas* del modelo base. Se sustituye por el respeto al veredicto real: 9 de 9 en la configuración desplegada, 7 de 7 evaluables en las dos anteriores | `experiments/E13_agente_transformers*.json`, campo `respected_verdict` sobre `verdict_evaluable` |
| `TUTOR-MIN-023` | «Cuarenta y cinco ejecuciones del redactor» no declaraba su base. Son las cinco mediciones con el motor `transformers` por nueve preguntas | Cinco ficheros `E13_agente_transformers*.json` × 9 ejecuciones = 45; `fake_citations` vacío en las 45 |
| `TUTOR-MAJ-022` | L-18 y L-19 se citaban en `cap6` sin existir en `research/limitations-register.md`. Se dan de alta con la ficha de campos del registro, se recoloca L-20 en su orden y el resumen pasa de 17 a 20 entradas | El registro llega a L-20 sin huecos; las severidades del resumen suman veinte |
| `TUTOR-MAJ-025` | El capítulo 2 había perdido las remisiones a P-02 (OE3 de no supervisado a supervisado) y P-03 (alcance). Restituidas en el cuerpo | `grep P-0` sobre `cap2` devuelve P-01, P-02 y P-03 |
| `TUTOR-MIN-024` | Doble línea en blanco en `cap5`; `LEEME.md` declaraba cinco marcas `[VERIFY_SOURCE]` cuando la bibliografía tiene cero; L-20 aparecía antes que L-18 | `grep -c VERIFY_SOURCE bibliografia.md` = 0 |

### Bloqueadas por la congelación del capítulo 5

Las cuatro exigen **introducir cifras o interpretación** en un capítulo que el autor declaró
congelado. No se ejecutan; se dejan aquí formuladas para el momento en que se levante.

1. Acotar la cobertura agregada de `cap5:113`, que el propio capítulo declara inexistente en
   ningún artefacto (`EVID-CRT-051`, único CRITICAL vivo).
2. Escribir **15 de 17** junto a la nota de la tabla de suficiencia, donde hoy dice
   «distinto», y declarar que las ocho filas omitidas son todas correctas.
3. Dar las cifras de la secuencia del verificador: 9/17 → 14/17 → 15/17.
4. Llevar al capítulo 5 el oráculo de selección de ventana (O-1), la línea base trivial de
   12/17 y las cinco ventanas, que hoy solo viven en el capítulo 6.

### Hallazgo nuevo · `CORR-MAJ-001` · cifra no sostenida dentro del capítulo congelado

**Alcance:** `cap5`, tabla del redactor, columna «Respeta el veredicto», filas «Base» y
«Base con adaptador v1».

**Evidencia:** la tabla publica **9/9** en las tres configuraciones. En
`experiments/E13_agente_transformers.json` y `E13_agente_transformers-lora.json`, el campo
`respected_verdict` es cierto en **7 de 9** ejecuciones, y `verdict_evaluable` es cierto en
esas mismas 7: las dos ejecuciones restantes fallaron el esquema y no tienen veredicto que
respetar. El enunciado sostenido por el registro es **7 de 7 evaluables**, no 9 de 9. La
tercera fila, la configuración desplegada, sí es 9/9 con las nueve evaluables.

**Impacto:** la columna no invalida ninguna conclusión —el respeto al veredicto es total en
todo lo evaluable, en las tres configuraciones— pero publica un denominador que el artefacto
no sostiene, y es la fila que el capítulo 6 citaba mal.

**Por qué no se corrige aquí:** cambiarla altera una cifra del capítulo congelado. Requiere
decisión del autor.

**Se verifica cuando:** la columna dé 7/7, 7/7 y 9/9, y el capítulo 6 repita ese mismo
denominador.

### Sigue abierto y no depende de esta iteración

`EXP-CRT-120`, `STAT-MAJ-029`, `STAT-MAJ-031`, `JURY-MAJ-005`, `EVID-MAJ-014`, `REF-MAJ-102`,
`AUTH-MAJ-006`, y todo lo que depende de la reejecución canónica. Las decisiones P-01 a P-04
son de la dirección.
