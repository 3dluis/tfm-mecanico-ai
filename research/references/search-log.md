# Registro de búsqueda documental

**Consolidado el 1 de septiembre de 2026** a partir de las entregas 1-3 de revisión sistemática
del repositorio legacy (`mecanico-ia/docs/estado_del_arte/`). **Nada se ha recalculado ni
estimado**: las cifras son las que declaran esos documentos.

## Naturaleza del barrido

**Procedimiento inspirado en PRISMA**, ejecutado en cuatro iteraciones documentadas
(entregas 1-4). **No es un flujo PRISMA formal** y así se declara en el propio capítulo.

| Magnitud | Valor declarado |
|---|---|
| Consultas ejecutadas | ≈ 170, a lo largo de cuatro iteraciones |
| Registros visualizados | ≈ 1 350 |
| Candidatos evaluados en fuente primaria | ≈ 250 |
| Referencias incluidas | 153 |
| De ellas, preprints marcados | 27 |
| Fecha de cierre del barrido | agosto de 2026 |
| Ventana de publicación | 2021-2026, más fundacionales marcados como tales |

> **Discrepancia detectada al consolidar.** La lista maestra del capítulo contiene **144**
> entradas y el texto declara **153 referencias**; el recuento de preprints da **28** al
> parsear frente a los **27** declarados. La diferencia puede deberse a referencias citadas
> fuera del capítulo o a entradas agrupadas. `[VERIFY_SOURCE: reconciliar 144 vs 153 antes
> del depósito]`. No se ha ajustado ninguna de las dos cifras para hacerlas coincidir.

## Limitación operativa declarada

La búsqueda se ejecutó **mediante buscador web general con verificación posterior de cada
registro en la página del editor** (MDPI, Springer/Nature, ACM DL, ACL Anthology, PHM
Society, OpenProceedings, JMLR, arXiv).

El acceso automatizado a **IEEE Xplore y ScienceDirect estuvo parcialmente bloqueado**
(robots/403). Los candidatos de esas plataformas que no pudieron verificarse en fuente
primaria **se descartaron en lugar de citarse sin verificar**. Cuatro candidatos relevantes
se recuperaron después por vías alternativas a nivel de metadatos; su lectura a texto
completo sigue pendiente.

**En consecuencia, los recuentos de esta tabla corresponden al barrido preliminar por web y
no a totales de bases indexadas.** Esta limitación se declara en la memoria mientras persista.

## Fuentes objetivo del protocolo

IEEE Xplore · ACM Digital Library · ScienceDirect · Springer · Scopus · Web of Science ·
MDPI · SAE International. Google Scholar y búsqueda web para descubrimiento. arXiv solo para
trabajos relevantes y recientes, **siempre marcados como preprint**.

## Criterios de inclusión

- Publicaciones 2021-2026, o anteriores si son fundacionales y se marcan como tales.
- Estudios de diagnóstico, anomalías, pronóstico o mantenimiento.
- Telemetría vehicular, o técnicas directamente transferibles.
- Metodología verificable.

## Criterios de exclusión

- Material comercial.
- Ausencia de metodología.
- Conducción autónoma no pertinente.
- Ciberseguridad CAN pura, salvo técnicas de anomalías reutilizables.
- Duplicados.
- Información insuficiente.
- **Imposibilidad de verificación en fuente primaria.**

## Pendiente antes del depósito

1. **Ejecutar las cadenas en Scopus, Web of Science e IEEE Xplore** con acceso institucional
   y registrar números exactos por base y por cadena. La sintaxis está preparada
   (entrega 2, §9; ampliada en entrega 3, §9). Solo entonces puede construirse el diagrama
   PRISMA formal.
2. **Tres lecturas pendientes a texto completo**: Takara et al. (ESWA 2025), Min et al.
   (EAAI 2024), Onsu et al. (IoT 2025). Los vacíos no se consideran definitivos hasta
   entonces.
3. **Búsqueda adversarial de vigilancia** inmediatamente antes del depósito, dada la
   proporción de trabajos de 2025-2026.

## Plantilla de registro para la consulta formal

| Base | Cadena | Fecha | Filtros | Resultados | Exportación |
|---|---|---|---|---|---|
| Scopus | | | años 2021-2026, tipo de documento | | RIS/CSV |
| Web of Science | | | `PY=(2021-2026)` | | |
| IEEE Xplore | | | | | |

## Nota de marco

Este barrido se realizó bajo la pregunta de investigación del marco **legacy**. La pregunta
canónica es la misma en su enunciado, pero su descomposición cambia. **Antes de reutilizar
esta revisión hay que comprobar que las cadenas de búsqueda siguen cubriendo las cuatro
subpreguntas canónicas** — en particular la condición DISTRACTOR, que el marco anterior no
contemplaba. Ver `research/legacy-map.md`.

---

## Iteración 5 — búsqueda dirigida de GAP-02 (1 de septiembre de 2026)

**Motivo:** la reconstrucción de la trazabilidad detectó que PI.4 —rechazo de evidencia
engañosa— no tenía vacío que la justificara (incidencia I-03).

**Herramienta:** búsqueda web general. **No sustituye al PRISMA formal**, que sigue pendiente.

| # | Cadena ejecutada | Resultados relevantes |
|---|---|---|
| C5.1 | `RAG distractor documents evaluation retrieval "hard negatives" LLM citation faithfulness abstain benchmark` | 4 |
| C5.2 | `RAG negative rejection benchmark "counterfactual robustness" RGB information integration LLM retrieval evaluation` | 3 |
| C5.3 | `automotive fault diagnosis RAG LLM abstention "insufficient evidence" claim-level attribution evaluation OBD telemetry 2025 2026` | 5 |

**Verificación de identificadores:** los cuatro candidatos principales resuelven en Crossref o
DataCite. **Lectura a texto completo: pendiente** — `[VERIFY_SOURCE]`.

| Candidato | Identificador | Estado |
|---|---|---|
| Chen, Lin, Han & Sun (2024). *Benchmarking LLMs in RAG* (banco **RGB**). AAAI 38(16), 17754-17762 | 10.1609/aaai.v38i16.29728 · arXiv:2309.01431 | verificado (metadatos) |
| *The Power of Noise: Redefining Retrieval for RAG Systems* (2024) | arXiv:2401.14887 | verificado (metadatos) |
| *The Distracting Effect: Understanding Irrelevant Passages in RAG* (2025) | arXiv:2505.06914 | verificado (metadatos) |
| *Correctness is not Faithfulness in RAG Attributions* (2024) | arXiv:2412.18004 | verificado (metadatos) |

**Candidatos adicionales del dominio automotriz, sin verificar:** trabajos sobre RAG guiado por
grafo de conocimiento para análisis de causa raíz en validación HiL de automoción, y
clasificación de fallos por conjunto de modelos en HiL (2026, preprints).
`[VERIFY_SOURCE]`.

### Resultado: la hipótesis de vacío queda refutada

**La distinción presencia/pertinencia está estudiada**, tiene banco público (RGB) y vocabulario
establecido desde 2024: «rechazo negativo» y «robustez contrafactual».

Se reformula el vacío de forma más estrecha y defendible. Detalle en
`references/project/gaps.md`, GAP-02 revisado.

**Nota de método.** Esta búsqueda se ejecutó para comprobar una hipótesis de vacío, no para
confirmarla. Salió que no. **Se reporta que no.** Un vacío que se estrecha tras buscar es un
vacío que sobrevivirá a la defensa.

## Iteración 6 — verificación de identificadores del corpus (1 de septiembre de 2026)

Consulta programática a **Crossref** y **DataCite** con el identificador de cada una de las 144
entradas de `references.md`.

| Resultado | Entradas |
|---|---|
| Resuelto en Crossref | 74 |
| Resuelto en DataCite | 36 |
| **Total verificado** | **110** |
| Sin identificador en la lista de origen | 34 |
| **Identificadores rotos o inexistentes** | **0** |

**Dos entradas que Crossref no encontró resuelven correctamente en DataCite** (OpenProceedings
y Borealis). No son referencias inexistentes; se hace constar para que nadie las retire por
error.

**Recuperado:** 28 títulos que la lista de origen tenía elididos, 52 venues ausentes, y
volumen, número y páginas donde el registro los publica.

**Detectado:** 7 discrepancias de año entre la lista y el registro. Ninguna es una referencia
inventada; son ambigüedades de año de registro que APA obliga a resolver a uno solo.

**Alcance de esta verificación:** confirma que el identificador resuelve y cuáles son sus
metadatos de registro. **No confirma que el trabajo diga lo que se le atribuye.**
