# Mapa de evidencia legacy

**Inventario, no importación.** Este documento cataloga qué contiene
`mecanico-ia` (`LEGACY_RESEARCH_SOURCE`, ADR-001) que **podría** servir al marco canónico.
**Nada se ha importado.** Todas las decisiones están en `PENDIENTE`.

Fecha del inventario: 1 de septiembre de 2026.

## Cadena de control

Ningún elemento entra en el TFM sin recorrerla entera:

```
LEGACY ARTIFACT
  → RELEVANCE CHECK          ¿sirve a PI.1-PI.4?
  → COMPATIBILITY CHECK      ¿es compatible con E1-E20 y M1-M6?
  → RESEARCH QUESTION CHECK  ¿responde a la pregunta canónica o a la anterior?
  → METHODOLOGY CHECK        ¿su diseño sigue siendo válido bajo el marco actual?
  → EVIDENCE CHECK           ¿la evidencia se sostiene sin el contexto que la produjo?
  → DECISION
  → IMPORT | REJECT
```

**Regla de importación:** todo elemento importado conserva su identificador de origen y recibe
uno canónico. Las métricas legacy se citan siempre como `LEG-M{n}` para evitar la colisión
real entre `M1` legacy (exactitud diagnóstica top-1) y `M1` canónica (grupo de diagnóstico).

**Regla de copia:** la reutilización se hace **por copia y con procedencia documentada**. El
laboratorio no importa el otro proyecto, no depende de rutas hacia él y no lo modifica.

---

## A. Instrumentos y código

Prioridad alta: son piezas construidas y probadas que ahorran semanas.

| ID | Artefacto | Relevancia para PI.1-PI.4 | Compatibilidad | Riesgo | Recomendación | Decisión |
|---|---|---|---|---|---|---|
| LEG-A01 | **`tools/contamination_audit.py`** — auditor ejecutable de exclusión de evidencia, con especificación declarativa | **Alta.** Es el instrumento que construye y verifica la condición `ABSENT` por construcción, no por simulación | Alta: la lógica E-RAG es la de `ABSENT`. Hay que reexpresar la especificación para las cuatro condiciones canónicas | Bajo | **Import prioritario.** Tiene un hallazgo real a su favor: detectó la violación de E-RAG en `corpus_v1` | PENDIENTE |
| LEG-A02 | **Descomposición en afirmaciones y verificación de soporte** — determinista, sin modelo de lenguaje; comprueba que la referencia existe, resuelve y sostiene | **Máxima.** Es el núcleo de PI.2 y de las métricas M4 | Alta. El plan canónico ya lo clasifica como `REUSE` y lo llama «el componente más valioso a reutilizar» | Bajo | **Import prioritario** | PENDIENTE |
| LEG-A03 | Mecanismo de **variantes controladas del corpus** (exclusión explícita de documentos con manifiesto y suma de verificación) | Alta. Produce FULL / PARTIAL / ABSENT | Alta. Falta añadir `DISTRACTOR`, que es nueva | Bajo | Import, con extensión | PENDIENTE |
| LEG-A04 | **Catálogo de señales OBD-II** con unidades y rangos | Media. Instrumental | Alta. Ya reexpresado en E2 (`obd/signals.py`, 12 señales) | — | **Ya reutilizado en E2**, con procedencia documentada | IMPORTADO (E2) |
| LEG-A05 | Escenarios de inyección de fallos | Media. Instrumental | Media. Reexpresados en E2 con `fault_id`, señales afectadas y patrón temporal | — | **Ya reutilizado en E2** | IMPORTADO (E2) |
| LEG-A06 | Perfiles de régimen de conducción | Media | Alta. Adaptados en E2, más aceleración y deceleración sostenidas | — | **Ya reutilizado en E2** | IMPORTADO (E2) |
| LEG-A07 | **Ventanado y conjunto de secuencias** | Media. Instrumental para E5 | Alta | Bajo | Import en E5 | PENDIENTE |
| LEG-A08 | **Extractor de descriptores temporales** | Media | Alta, **con una condición**: E2 demostró que los descriptores no pueden limitarse a medias, o dos de los cinco fallos son indetectables por construcción | Medio | Import **solo si** cubre varianza, conteo de eventos y extremos | PENDIENTE |
| LEG-A09 | **Ejecutor de SHAP** con reglas fijadas: función explicada declarada, explainer agnóstico, fondo solo de entrenamiento | Alta para E9 | Alta. «Esas reglas son exactamente las que este laboratorio necesita» | Bajo | Import | PENDIENTE |
| LEG-A10 | **Corpus documental con procedencia** y fichero de fuentes | Alta para E10 | Media. Hay que garantizar que la procedencia sobrevive al troceado, que es lo que la PI exige | Medio | Import con verificación de procedencia | PENDIENTE |
| LEG-A11 | **Recuperador léxico determinista** | Media. Baseline y CI sin red | Alta | Bajo | Import como baseline | PENDIENTE |
| LEG-A12 | Abstracción de proveedores de modelo de lenguaje + **proveedor determinista sin red** | Media. Imprescindible para tests | Alta. Falta ampliar a proveedores remotos y registrar parámetros de cada llamada | Bajo | Import y ampliación | PENDIENTE |
| LEG-A13 | **Política de suficiencia** | Alta para E15 | Media. La política existe; los umbrales hay que calibrarlos aquí, solo con validación | Medio | Import de la lógica, **no de los umbrales** | PENDIENTE |
| LEG-A14 | Registro de experimentos y de modelos entrenados | Media | Alta | Bajo | Import | PENDIENTE |
| LEG-A15 | Exportación a ONNX | Ninguna | — | — | **Rechazo propuesto**: sirve al despliegue, no al experimento | PENDIENTE |
| LEG-A16 | Runtime multiagente, memoria evolutiva, consolidación de conocimiento | Ninguna bajo el marco canónico | — | — | **Rechazo propuesto**: `FUTURE` explícito en el plan | PENDIENTE |

## B. Evidencia experimental producida

**Aviso metodológico.** Ninguno de estos estudios se ejecutó bajo el marco canónico. Ninguno
puede reportarse como resultado del TFM sin declarar su procedencia y su marco de origen. La
mayoría son **evidencia instrumental o metodológica**, no respuestas a PI.1-PI.4.

| ID | Estudio (fase) | Qué estableció | Valor bajo el marco canónico | Recomendación | Decisión |
|---|---|---|---|---|---|
| LEG-B01 | EXP-ANOM-001 (F3) | Selección de detector; LOF elegido | Bajo: el marco canónico usa modelo supervisado, no detector no supervisado | Rechazo propuesto para resultados; conservar como contexto | PENDIENTE |
| LEG-B02 | EXP-ANOM-005 (F13) | Control de integridad de la serie (ancla 0.163197) | Metodológico | Mencionable en metodología legacy | PENDIENTE |
| LEG-B03 | EXP-ANOM-006 (F14) | **Negativo**: autoencoder denegado frente a LOF | Bajo bajo el marco actual | Rechazo propuesto | PENDIENTE |
| LEG-B04 | EXP-ANOM-007 (F16) | XAI sobre la detección; AR@K muy por encima del azar | **Medio-alto**: antecedente directo de E9, y evidencia de que la atribución aporta señal | **Candidato a discusión**, no a resultado | PENDIENTE |
| LEG-B05 | EXP-ANOM-008 (F17) | **Negativo**: representación fs2-lite rechazada | Bajo | Rechazo propuesto | PENDIENTE |
| LEG-B06 | EXP-ANOM-009 (F18) | **Negativo**: autoencoders temporales peores | Bajo-medio: informa la elección de arquitectura de E7 | **Candidato**: puede justificar por qué E7 no elige esa vía | PENDIENTE |
| LEG-B07 | AUDIT-DATA-001 (F19) | 7 de 8 anomalías separables sin modelos | **Alto valor metodológico**: fundamenta que un fallo de detección sea del modelo y no del banco. E2 replica esta preocupación por su cuenta | **Candidato a metodología** | PENDIENTE |
| LEG-B08 | EXP-ANOM-010 (F21) | **Negativo mayor**: la cobertura declarada de un banco no es su cobertura efectiva | **Alto.** Hallazgo metodológico reutilizable e independiente de la pregunta | **Candidato fuerte a discusión y a metodología** | PENDIENTE |
| LEG-B09 | EXP-ANOM-010-R2 (F22) | Con cobertura efectiva, FPR 0,0086 | Bajo: es un resultado del detector legacy | Rechazo propuesto para resultados | PENDIENTE |
| LEG-B10 | F24 — auditoría de contaminación | `corpus_v1` viola E-RAG | **Alto.** Demuestra que la exclusión de evidencia hay que auditarla, no declararla | **Candidato fuerte a metodología** | PENDIENTE |
| LEG-B11 | **F28 / D1 — rechazo del generador** | El candidato respondió lo mismo en los 20 casos y en los 3 brazos; su 0,15 procede de responder siempre igual; **el mejor control constante (0,25) lo superó** | **Alto.** Es evidencia directa de que un control trivial puede superar al sistema, y de que la conformidad de esquema no implica capacidad | **Candidato fuerte a discusión y a limitaciones** | PENDIENTE |
| LEG-B12 | **F28 — la consulta no discriminaba** | Con contexto numérico y recuperación léxica, los 20 casos devolvían los mismos tres documentos: las métricas de recuperación habrían medido cero información | **Alto.** Advertencia de diseño directamente aplicable a E12 | **Candidato fuerte a metodología** | PENDIENTE |

### Nota sobre los resultados negativos

`NEGATIVE_RESULT != FAILED_RESEARCH`.

LEG-B08, LEG-B10, LEG-B11 y LEG-B12 son los cuatro elementos de mayor valor de todo este
inventario, y los cuatro son negativos. Ninguno se descarta. Su destino previsible no es el
capítulo 5 —no responden a PI.1-PI.4— sino el **capítulo 4** (como decisiones de diseño
justificadas) y el **capítulo 5, apartado de discusión** (como contraste).

**Pero eso todavía no se decide.** Primero resultado → evidencia → interpretación →
implicación. Construir ahora la narrativa que los aprovecha sería exactamente el orden
invertido que el método prohíbe.

## C. Datos

| ID | Artefacto | Valor | Riesgo | Recomendación | Decisión |
|---|---|---|---|---|---|
| LEG-C01 | `suite_v2`, `cases_v2` (bancos confirmatorios congelados en F25) | Medio. Generados bajo otro régimen | **Alto**: usarlos como banco canónico importaría los sesgos de un diseño distinto | Rechazo propuesto como banco; posible material de contraste | PENDIENTE |
| LEG-C02 | `cases_d1` (banco de selección disjunto) | Bajo | — | Rechazo propuesto | PENDIENTE |
| LEG-C03 | Corpus C-A / C-B / C-B′ con manifiesto y suma de verificación | **Alto**: es un corpus con variantes de disponibilidad ya construido y auditado | Medio: falta la variante `DISTRACTOR` | **Candidato fuerte** para E10 | PENDIENTE |
| LEG-C04 | Clases held-out congeladas (`corr_break_rpm_maf`, `load_coolant_decouple`, `joint_slow_drift`) | Medio | Medio | Evaluar en E17 | PENDIENTE |

## D. Documentación

| ID | Artefacto | Valor | Recomendación | Decisión |
|---|---|---|---|---|
| LEG-D01 | **Estado del arte**: 144 referencias verificadas en fuente primaria, 3 entregas de revisión sistemática, 4 líneas temáticas | **Máximo.** Es E1: su validez no depende del marco experimental | **Import**, con revisión de cadenas para cubrir `DISTRACTOR`. Ya consolidado en `research/references/` | PARCIAL |
| LEG-D02 | 37 ADR técnicos | Alto como contexto de decisiones de ingeniería | Citar como procedencia; no renumerar | PENDIENTE |
| LEG-D03 | `prereg-v1.0` + ENM-001 | Alto | **Clasificado**, no importado. Ver `prereg-classification.md` | CLASIFICADO |
| LEG-D04 | Alineación v4 (núcleo científico, trazabilidad, fuera de alcance, historial de la PI) | Alto como historial | Fuente del capítulo 4 al narrar la evolución del diseño (ADR-002) | PENDIENTE |
| LEG-D05 | 28 informes de fase | Medio | Fuente de trazabilidad histórica | PENDIENTE |
| LEG-D06 | Borrador de la memoria (`docs/memoria/`, 10 625 palabras) | **Alto para los capítulos 1-3; nulo para 4-6** | Los capítulos 1 y 3 son reutilizables casi tal cual. El 2 necesita ajuste. El 4 describe el marco legacy y **se rehace**. El 5 y el 6 son esqueletos | PENDIENTE |

## E. Aprendizajes metodológicos

No son artefactos: son cosas que este proyecto ya sabe y que no debería volver a aprender.

| ID | Aprendizaje | Origen | Aplicación canónica |
|---|---|---|---|
| LEG-E01 | La cobertura declarada de un banco no es su cobertura efectiva | F21 | Verificar la cobertura efectiva del banco de E17 antes de interpretar nada |
| LEG-E02 | Un corpus puede violar su propia exclusión sin que nadie lo note; hay que auditarlo de forma ejecutable | F24 | E10 y E17 |
| LEG-E03 | Un control constante trivial puede superar al sistema | F28 / D1 | E6 y E19: el baseline de clase mayoritaria no es una formalidad |
| LEG-E04 | Conformidad de esquema no implica capacidad: 20/20 bien formadas y 0 información | F28 / D1 | E13: la tasa de salidas válidas (M3) no puede leerse como calidad |
| LEG-E05 | Una variable de diseño no declarada acaba decidiendo el resultado sin que nadie la haya decidido | F28 (formulación de la consulta) | E12: declarar y congelar cómo se construye la consulta **antes** de medir |
| LEG-E06 | El banco de selección nunca puede ser el de evaluación | F28 §1 | E15: umbrales solo con validación; test cerrado hasta E19 |
| LEG-E07 | Una correlación marginal baja no implica ausencia de relación | E2 (canónico) | E9: al interpretar la atribución |

## Resumen del inventario

| Categoría | Elementos | Ya importados | Candidatos fuertes | Rechazos propuestos |
|---|---|---|---|---|
| A. Instrumentos y código | 16 | 3 (en E2) | 5 | 2 |
| B. Evidencia experimental | 12 | 0 | 4 | 4 |
| C. Datos | 4 | 0 | 1 | 2 |
| D. Documentación | 6 | 1 parcial | 2 | 0 |
| E. Aprendizajes | 7 | — | 7 | — |

**Ningún elemento de la categoría B se propone como resultado del TFM.** Los cuatro
candidatos fuertes lo son para metodología, discusión o limitaciones.

## Siguiente paso

Este inventario **no autoriza ninguna importación**. Cada `PENDIENTE` se resuelve al llegar
a la fase que lo necesita (E5, E9, E10, E12, E15, E17), aplicando la cadena de control
completa y anotando la decisión aquí con su fecha.
