# Memoria del TFM — texto fuente por capítulos

**Autor:** Luis Daniel Díaz Díaz · **Titulación:** Máster Universitario en Inteligencia Artificial, Universidad Alfonso X el Sabio · **Convocatoria:** noviembre o diciembre de 2026 (`[DECISIÓN DEL AUTOR]`).

Este directorio es la **fuente de verdad del texto de la memoria**. Se escribe en Markdown, versionado en Git, y se vuelca en la plantilla oficial de Word (`24-25 Plantilla TFM`, en la raíz de `TFM/`) usando exclusivamente sus estilos: *Título Capítulo*, *Título Apartado*, *Título Subapartado*, *Texto TFM*, *Viñetas TFM*, *Cita Literal APA*, *Bibliografía*. El documento Word queda fuera del control de versiones.

## Correspondencia con la plantilla oficial

| Fichero | Capítulo de la plantilla | Estado a 2 de septiembre de 2026 |
|---|---|---|
| `00_resumen.md` | Resumen (exigido por la sesión informativa 25-26) | redactado |
| `cap1_introduccion.md` | Capítulo 1: Introducción · Justificación · Presentación | redactado |
| `cap2_objetivos.md` | Capítulo 2: Objetivos · General · Específicos | redactado; objetivo general y OE alineados con la pregunta acotada tras el feedback del director (septiembre de 2026) |
| `cap3_marco_teorico.md` | Capítulo 3: Marco Teórico | estructura realineada y apartados con referencias verificadas; el resto marcado |
| `cap4_marco_metodologico.md` | Capítulo 4: Población y muestra · Objetivos de investigación · Variables e instrumentos · Diseño experimental · Modelo de análisis | redactado sobre el diseño ejecutado |
| `cap5_resultados.md` | Capítulo 5: Análisis descriptivo · Resultados · Discusión | resultados parciales sobre validación, actualizados a la reejecución del 13/14-09-2026; se completa con E19 |
| `cap6_conclusiones.md` | Capítulo 6: Limitaciones · Prospectiva · Consideraciones finales | conclusiones provisionales por objetivo; la respuesta definitiva depende de E19 |
| `bibliografia.md` | Bibliografía (APA 6.ª, según la plantilla) | solo referencias verificadas en fuente primaria |

## Reglas que gobiernan este texto

1. **Nada se afirma sin registro.** Toda cifra procede de un fichero de `experiments/` o `results/` y se cita con su identificador. Lo no ejecutado se declara no ejecutado.
2. **Ninguna referencia sin verificar.** Solo entran las de `research/references/` (144, verificadas en fuente primaria) y las de método verificadas en Crossref o arXiv el 2 de septiembre de 2026 (`research/references/referencias-metodo.md`). La sesión informativa 25-26 advierte de que una fuente inexistente puede suponer un *no apto*.
3. **Los datos son sintéticos y se dice en cada capítulo.** La pregunta de investigación no exige datos reales (ADR-003, 3 de septiembre de 2026); cada resultado declara la procedencia de su dato (`dataset_type`) y la validez externa se trata como limitación. No se suaviza y no se presenta un resultado sintético como comportamiento real.
4. **Un solo verbo en el objetivo general**, en infinitivo, verificable al terminar.
5. **Vocabulario canónico** (ADR-001): PI.1–PI.4, E1–E20, M1–M6, condiciones FULL / PARTIAL / ABSENT / DISTRACTOR. No se mezcla con la nomenclatura del repositorio heredado.
6. Las decisiones que corresponden al director **no se resuelven en el texto ni se marcan dentro de él**: van al registro `preguntas-abiertas-al-director.md`, con su procedencia y con lo que bloquean. El cuerpo de la memoria queda redactado de forma neutral, sin dar por supuesta ninguna respuesta y sin corchetes editoriales visibles para el lector.

## Lo que este texto no puede cerrar todavía

| Depende de | Afecta a |
|---|---|
| Dataset de la evaluación final (E19) y, si la hay, fuente de datos reales (E3) | Cap. 4 «Población y muestra» (versión final), Cap. 5 apartados finales, Cap. 6 conclusiones |
| Reunión con el director | Título definitivo, objetivos reformulados (P-01, P-02), extensión (tres cifras oficiales incompatibles), edición de APA (P-04), convocatoria |
| E18, ablaciones | Cap. 5 «Discusión» (contribución de cada componente) |
| Reconciliación de la lista maestra de referencias (144 frente a 153 declaradas) | Bibliografía |

## Cómo se vuelca a Word

Capítulo a capítulo, sin sangrías propias ni estilos nuevos. Las tablas Markdown se convierten en tablas de Word con el estilo de la plantilla. Las citas van en formato autor-año; la bibliografía, en el estilo *Bibliografía*. Todo texto entre corchetes de la plantilla se elimina de la versión final.


## Regla de adición bibliográfica

`docs/memoria/bibliografia.md` contiene **solo** las referencias citadas en los capítulos redactados, y su fuente de verdad es `research/references/references.md` para las de dominio y `research/references/referencias-metodo.md` para las de método.

> **Cuando un capítulo cite una referencia nueva, su entrada se añade en el mismo cambio.**

Esta regla encabezaba el fichero de bibliografía como bloque de estado y se perdió al retirar esos bloques el 10 de septiembre de 2026. Su incumplimiento es exactamente lo que produjo que una referencia citada en el capítulo 3 quedara sin entrada durante seis días. Se restituye aquí, donde vive el resto del estado, en lugar de devolverla al cuerpo del documento.

Una verificación contra fuente primaria debe propagarse a **las tres vistas**: el fichero de depósito, la lista maestra y `bibliography.bib`. Corregir solo la primera hace que el proyecto publique un identificador que su propia lista maestra declara inexistente.

## Estado por capítulo

Esta información encabezaba cada fichero como bloque de cita. Se traslada aquí el 10 de septiembre de 2026: eran notas de trabajo visibles para cualquier lector del borrador, y la regla 6 de este documento prohíbe dejar dentro del texto las decisiones que corresponden al director. Lo sustantivo de aquellos bloques se reescribió como texto académico en su capítulo.

| Fichero | Estado | Pendiente de |
|---|---|---|
| `00_resumen.md` | redactado sobre resultados sintéticos; extensión orientativa 250–300 palabras | E19: se reescriben las cifras y la última frase |
| `cap1_introduccion.md` | redactado; actualizado el 3 de septiembre de 2026 a la pregunta sin requisito de datos reales (ADR-003) | decisión sobre la reescritura sin confirmar que arrastró el commit `9c388d9` |
| `cap2_objetivos.md` | OE3 y OE5 realineados el 14-09-2026 con la pregunta acotada; sin restos de la formulación amplia | P-03 (alcance ejecutado frente al aprobado) |
| `cap3_marco_teorico.md` | estructura realineada al marco canónico; solo referencias verificadas | — |
| `cap4_marco_metodologico.md` | redactado sobre el diseño ejecutado, E1–E17 sobre datos sintéticos | «Población y muestra» espera el conjunto de evaluación final |
| `cap5_resultados.md` | revisado el 15-09-2026 tras seis auditorías: tablas 5.1–5.7 con rótulo; dos tipos de error con ejecuciones, ventanas y políticas de referencia; PI.4 no interpretable con el diseño actual | E19 |
| `cap6_conclusiones.md` | conclusiones provisionales OE1→OE5→OG con grado de cumplimiento; limitaciones del agente añadidas el 15-09 | E19. Fuente: `research/limitations-register.md`, 21 entradas |
| `bibliografia.md` | solo las referencias citadas, verificadas en fuente primaria | edición de APA (P-04); sin marcas `[VERIFY_SOURCE]` pendientes |


## Numeración para la composición

El texto fuente no numera los apartados: la numeración la aplica la plantilla al componer. La
jerarquía de encabezados produce esta numeración, que es la que debe verse en el índice
automático del documento Word tras actualizarlo. La versión en Word del 28-08-2026 tenía el
capítulo 3 desplazado un nivel (3.2.3 como primer subapartado, 3.2.4 repetido, «Modelos de
lenguaje y recuperación aumentada» como 3.3.1 y salto de 3.3.2 a 3.3.4); se corrige al volcar.

```
1   Introducción · 1.1 Justificación · 1.2 Presentación
2   Objetivos · 2.1 General · 2.2 Específicos · 2.3 Correspondencia entre objetivos y evaluación
3.1 Propósito y procedimiento de la revisión
3.2 Diagnóstico vehicular a partir de OBD-II · 3.2.1 Puerto y señales · 3.2.2 Datos · 3.2.3 Modelos
3.3 Explicabilidad de los modelos de diagnóstico
3.4 Modelos de lenguaje y recuperación aumentada · 3.4.1 El problema · 3.4.2 Aplicaciones
    · 3.4.3 Ajuste del modelo pequeño · 3.4.4 Recuperación semántica, léxica y filtrada
3.5 Abstención ante evidencia insuficiente · 3.6 Vacío y posicionamiento
4.1 Población y muestra · 4.1.1 Población · 4.1.2 Telemetría · 4.1.3 Corpus · 4.1.4 Casos
4.2 Objetivos de investigación
4.3 Variables e instrumentos · 4.3.1 Manipulada · 4.3.2 Controladas · 4.3.3 Medidas · 4.3.4 Instrumentos
4.4 Diseño experimental · 4.4.1 Experimento central · 4.4.2 Particiones y cierre del test
    · 4.4.3 Fases del agente (4.4.3.1 recuperación · 4.4.3.2 construcción · 4.4.3.3 verificación
      · 4.4.3.4 decisión · 4.4.3.5 redacción) · 4.4.4 Unidades de análisis · 4.4.5 Métricas
    · 4.4.6 Reproducibilidad · 4.4.7 Ablaciones · 4.4.8 Trabajo pendiente
4.5 Modelo de análisis de datos
5.1 Análisis descriptivo · 5.2 Resultados (5.2.1 PI.1 · 5.2.2 PI.2 · 5.2.3 PI.3 y PI.4
    · 5.2.4 Modelo de lenguaje) · 5.3 Discusión (5.3.1 Lo que sostienen · 5.3.2 Lo que no
    · 5.3.3 El patrón)
6.1 Conclusiones provisionales · 6.2 Limitaciones · 6.3 Prospectiva · 6.4 Consideraciones finales
```

Tablas: 2.1; 4.1–4.14 (la 4.3 son las señales; la 4.13 incluye unidad de independencia y
recuentos); 5.1–5.7. La memoria no contiene figuras.

## Historial editorial del capítulo 5 (retirado del cuerpo el 15-09-2026)

Una revisión del 10-09-2026 localizó cinco discrepancias entre el capítulo 5 y los registros
que citaba: las cifras del modelo de diagnóstico, distintas de los informes de fase; la tabla
de recuperación, que no se reproducía desde su registro; las latencias del modelo de lenguaje,
que ningún registro producía; el umbral de confianza (0,80 publicado, 0,79 registrado tras la
enmienda ENM-U01); y la matriz de decisiones, que recogía nueve de diecisiete casos y una
celda de la versión v1 del verificador. El 15-09 se resolvieron citando el registro vigente.
En la tabla del modelo de lenguaje se publicaba «9/9» de respeto al veredicto para el modelo
base y el primer adaptador; la cifra correcta es 7 de 7 evaluables. El detalle está en
`docs/experiment-index.md` §Discrepancias y en los informes de auditoría del 15-09.

## Revisión del 15-09-2026 tras el feedback del director

Correcciones aplicadas a partir de seis auditorías independientes del commit `ebca11e`
(`TFM/experiment-reports/`, `evidence-reports/`, `rag-reports/`, `statistical-reports/`,
`reference-reports/`, `authenticity-reports/`, todos `EXPERIMENT-AUDIT|…-20260915-memoria.md`)
y de la auditoría diferencial `docs/audits/scope_change/DIFERENCIAL-v2.0-a-acotada-20260915.md`.
No aplicado: la reescritura del apartado 4.4.1 que propone AUTH-MAJ-001, porque ese texto lo
aprobó el autor el 14-09 y la propuesta reintroducía una frase que el autor retiró.
