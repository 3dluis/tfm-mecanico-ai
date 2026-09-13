# 14 · Inventario y normalización de tablas y figuras

Auditoría editorial y estructural. **No modifica ninguna decisión científica**: ni pregunta,
ni objetivos, ni metodología, ni métricas, ni valores, ni resultados, ni estado experimental.

`PI_STATUS = LOCKED` · `DISTRACTOR_STATUS = BAJO_DIAGNÓSTICO`

## Sistema adoptado

Numeración por capítulo, `Tabla X.Y` y `Figura X.Y`. Título descriptivo tras el número, en
minúscula salvo inicio, nombres propios y acrónimos. Procedencia bajo el elemento. Toda tabla
se menciona en el cuerpo por su número, nunca por su posición.

## Tablas normalizadas

| Número | Capítulo | Título | Procedencia | Mencionada | Estado científico | Acción |
|---|---|---|---|---|---|---|
| Tabla 2.1 | 2 | Trazabilidad entre objetivos específicos, fases experimentales y métricas | elaboración propia | sí | METODOLOGÍA | numerada |
| Tabla 4.1 | 4 | Vehículo de referencia y documentación técnica asociada | elaboración propia | sí | METODOLOGÍA | numerada |
| Tabla 4.2 | 4 | Parámetros de generación de la muestra sintética de telemetría OBD-II | elaboración propia a partir de la ficha de calibración | sí | METODOLOGÍA | numerada |
| Tabla 4.3 | 4 | Suelo de ruido de los descriptores según la longitud de la ventana temporal | elaboración propia a partir del registro de E4 | sí | **MEDIDO** | numerada · `PLACEMENT_REVIEW_REQUIRED` |
| Tabla 4.4 | 4 | Composición del corpus documental del vehículo de referencia | elaboración propia | sí | METODOLOGÍA | numerada |
| Tabla 4.5 | 4 | Subpreguntas de investigación con sus desenlaces de sostenimiento y refutación | elaboración propia | sí | METODOLOGÍA | numerada |
| Tabla 4.6 | 4 | Condiciones experimentales de disponibilidad y pertinencia de la evidencia documental | elaboración propia | sí | METODOLOGÍA | numerada |
| Tabla 4.7 | 4 | Agrupación en bloques de las veinte fases del plan experimental | elaboración propia | sí | METODOLOGÍA | numerada |
| Tabla 4.8 | 4 | Instrumentación de la fase de recuperación de evidencia | elaboración propia | sí | METODOLOGÍA | numerada |
| Tabla 4.9 | 4 | Instrumentación de la fase de construcción de la explicación | elaboración propia | sí | METODOLOGÍA | numerada |
| Tabla 4.10 | 4 | Instrumentación de la fase de verificación del soporte | elaboración propia | sí | METODOLOGÍA | numerada |
| Tabla 4.11 | 4 | Instrumentación de la fase de decisión entre explicar y abstenerse | elaboración propia | sí | METODOLOGÍA | numerada |
| Tabla 4.12 | 4 | Unidades de observación independientes por métrica | elaboración propia | sí | METODOLOGÍA | numerada |
| Tabla 4.13 | 4 | Estado de definición, implementación y cálculo de las métricas de OE4 | elaboración propia | sí | METODOLOGÍA | numerada |

## Tablas del capítulo 5 · propuesta, no aplicada

El capítulo 5 permanece congelado. Se prepara la numeración y no se toca el fichero.

| Número propuesto | Título propuesto | Procedencia | Estado científico |
|---|---|---|---|
| Tabla 5.1 | Exactitud y F1 macro de los modelos de diagnóstico evaluados | resultados de E6 y E7 | MEDIDO · pendiente del conjunto de evaluación final |
| Tabla 5.2 | Error de calibración esperado y sesgo de confianza del modelo desplegado | resultados de E6 | MEDIDO · pendiente del conjunto de evaluación final |
| Tabla 5.3 | Métricas de recuperación por estrategia de consulta | resultados de E12 | MEDIDO · **pendiente de reejecución canónica (L-20)** |
| Tabla 5.4 | Comportamiento de los modelos de embeddings según el idioma de la consulta | resultados de E12 | MEDIDO · **pendiente de reejecución canónica (L-20)** |
| Tabla 5.5 | Decisión de suficiencia por caso y condición de evidencia | resultados de E15 | MEDIDO · **DISTRACTOR bajo diagnóstico** |
| Tabla 5.6 | Validez, respeto al veredicto y latencia del redactor por configuración | resultados de E13 | MEDIDO · `CORR-MAJ-001` abierto |

Referencias relativas que deberán sustituirse cuando se levante la congelación: «Sobre la tabla
que sigue» y «para que la tabla no se lea», ambas en la sección de suficiencia.

## Figuras

**La memoria no contiene ninguna figura.** Cero imágenes, cero diagramas, cero esquemas
gráficos: la búsqueda de `![...]()`, `<img`, bloques `mermaid` y bloques de diagrama sobre los
siete ficheros devuelve cero resultados.

No se crea ninguna, porque inventarlas está fuera del alcance de una tarea editorial y porque
una figura de arquitectura o de flujo experimental es una decisión de contenido. Se registra
como hallazgo: `FIGURE_NUMBERING = N/A`, y las candidatas naturales —arquitectura funcional del
sistema, secuencia de generación y validación de una hipótesis, diseño de las cuatro
condiciones— quedan a decisión del autor.

## Hallazgos abiertos

### `PLACEMENT_REVIEW_REQUIRED` · Tabla 4.3

Contiene **valores obtenidos experimentalmente** —el suelo de ruido para ventanas de 10, 30, 60
y 120 segundos— dentro del capítulo de metodología. Por el criterio de separación entre
definición y resultado correspondería al capítulo 5.

No se traslada, por dos razones: moverla escribiría en el capítulo congelado, y el capítulo 4
**sí define formalmente la medida** antes de darla —máximo entre los 139 descriptores de una
condición sin fallo, partida en dos mitades por sesión, en treinta repeticiones—, de modo que
el término «suelo de ruido» no queda huérfano. `TERMINOLOGY_REVIEW_REQUIRED` no se activa por
esa definición previa, pero conviene comprobar que ningún lector la confunda con una magnitud
estadística estándar.

### `UAX_TEMPLATE_REVIEW_REQUIRED` · resuelto

Verificado sobre `24-25 Plantilla TFM MUIA2.docx`: la plantilla **no contempla índice de tablas
ni índice de figuras**. Su índice es un `TOC` de encabezados de nivel 1 a 4 y no menciona
tablas ni figuras en ningún punto. No se añade ninguno: la estructura oficial no se modifica
unilateralmente.

### Numeración automática en el documento final

La memoria vive en Markdown y se compone después. Los números de este inventario son texto en
el fuente. Al generar el DOCX deben convertirse en campos de rótulo y referencia cruzada de
Word, para que la inserción de una tabla renumere las siguientes. Mientras la fuente sea
Markdown, la renumeración es manual y este inventario es el control.

## Estado de cierre

| Control | Estado |
|---|---|
| `TABLE_NUMBERING` | PASS en capítulos 2 y 4 · propuesto en 5 |
| `FIGURE_NUMBERING` | N/A — no hay figuras |
| `CAPTION_CONSISTENCY` | PASS |
| `CROSS_REFERENCES` | PASS en 2 y 4 · dos relativas pendientes en el 5 congelado |
| `SOURCE_ATTRIBUTION` | PASS |
| `PLACEMENT_CONSISTENCY` | `PLACEMENT_REVIEW_REQUIRED` en Tabla 4.3 |
| `UAX_FORMAT_REVIEW` | PASS — sin índices de tablas ni figuras en la plantilla |

**Veredicto: `BLOCKED_REQUIRES_DECISION`**, por dos asuntos que no se resuelven sin tocar
ciencia o el capítulo congelado: la ubicación de la Tabla 4.3 y la numeración del capítulo 5.

---

> **Superado por `ADR-004`, 12 de septiembre de 2026.** La dirección resolvió `SD-01` a favor de
> la pregunta acotada y descartó la formulación amplia. Lo que este documento registra sobre los
> componentes de esa formulación era cierto cuando se escribió y se conserva como tal; ya no
> describe el alcance vigente del trabajo.
