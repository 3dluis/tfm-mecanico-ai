# Memoria del TFM — texto fuente por capítulos

**Autor:** Luis Daniel Díaz Díaz · **Titulación:** Máster Universitario en Inteligencia
Artificial, Universidad Alfonso X el Sabio · **Convocatoria:** noviembre o diciembre de 2026
(`[DECISIÓN DEL AUTOR]`).

Este directorio es la **fuente de verdad del texto de la memoria**. Se escribe en Markdown,
versionado en Git, y se vuelca en la plantilla oficial de Word (`24-25 Plantilla TFM`, en la
raíz de `TFM/`) usando exclusivamente sus estilos: *Título Capítulo*, *Título Apartado*,
*Título Subapartado*, *Texto TFM*, *Viñetas TFM*, *Cita Literal APA*, *Bibliografía*. El
documento Word queda fuera del control de versiones.

## Correspondencia con la plantilla oficial

| Fichero | Capítulo de la plantilla | Estado a 2 de septiembre de 2026 |
|---|---|---|
| `00_resumen.md` | Resumen (exigido por la sesión informativa 25-26) | redactado |
| `cap1_introduccion.md` | Capítulo 1: Introducción · Justificación · Presentación | redactado |
| `cap2_objetivos.md` | Capítulo 2: Objetivos · General · Específicos | redactado; **objetivos reformulados pendientes de consenso con el director** |
| `cap3_marco_teorico.md` | Capítulo 3: Marco Teórico | estructura realineada y apartados con referencias verificadas; el resto marcado |
| `cap4_marco_metodologico.md` | Capítulo 4: Población y muestra · Objetivos de investigación · Variables e instrumentos · Diseño experimental · Modelo de análisis | redactado sobre el diseño ejecutado |
| `cap5_resultados.md` | Capítulo 5: Análisis descriptivo · Resultados · Discusión | **borrador sobre datos sintéticos**; se reescribe cuando haya E19 |
| `cap6_conclusiones.md` | Capítulo 6: Limitaciones · Prospectiva · Consideraciones finales | limitaciones redactadas; el resto depende de E19 |
| `bibliografia.md` | Bibliografía (APA 6.ª, según la plantilla) | solo referencias verificadas en fuente primaria |

## Reglas que gobiernan este texto

1. **Nada se afirma sin registro.** Toda cifra procede de un fichero de `experiments/` o
   `results/` y se cita con su identificador. Lo no ejecutado se declara no ejecutado.
2. **Ninguna referencia sin verificar.** Solo entran las de `research/references/` (144,
   verificadas en fuente primaria) y las de método verificadas en Crossref o arXiv el 2 de
   septiembre de 2026 (`research/references/referencias-metodo.md`). La sesión informativa
   25-26 advierte de que una fuente inexistente puede suponer un *no apto*.
3. **Los datos son sintéticos y se dice en cada capítulo.** La pregunta de investigación no
   exige datos reales (ADR-003, 3 de septiembre de 2026); cada resultado declara la
   procedencia de su dato (`dataset_type`) y la validez externa se trata como limitación.
   No se suaviza y no se presenta un resultado sintético como comportamiento real.
4. **Un solo verbo en el objetivo general**, en infinitivo, verificable al terminar.
5. **Vocabulario canónico** (ADR-001): PI.1–PI.4, E1–E20, M1–M6, condiciones FULL /
   PARTIAL / ABSENT / DISTRACTOR. No se mezcla con la nomenclatura del repositorio heredado.
6. Las decisiones que corresponden al director **no se resuelven en el texto ni se marcan
   dentro de él**: van al registro `preguntas-abiertas-al-director.md`, con su procedencia y
   con lo que bloquean. El cuerpo de la memoria queda redactado de forma neutral, sin dar por
   supuesta ninguna respuesta y sin corchetes editoriales visibles para el lector.

## Lo que este texto no puede cerrar todavía

| Depende de | Afecta a |
|---|---|
| Dataset de la evaluación final (E19) y, si la hay, fuente de datos reales (E3) | Cap. 4 «Población y muestra» (versión final), Cap. 5 apartados finales, Cap. 6 conclusiones |
| Reunión con el director | Título definitivo, objetivos reformulados (P-01, P-02), extensión (tres cifras oficiales incompatibles), edición de APA (P-04), convocatoria |
| E18, ablaciones | Cap. 5 «Discusión» (contribución de cada componente) |
| Reconciliación de la lista maestra de referencias (144 frente a 153 declaradas) | Bibliografía |

## Cómo se vuelca a Word

Capítulo a capítulo, sin sangrías propias ni estilos nuevos. Las tablas Markdown se
convierten en tablas de Word con el estilo de la plantilla. Las citas van en formato
autor-año; la bibliografía, en el estilo *Bibliografía*. Todo texto entre corchetes de la
plantilla se elimina de la versión final.
