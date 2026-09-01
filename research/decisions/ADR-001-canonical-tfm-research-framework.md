# ADR-001 — Marco de investigación canónico del TFM

**Fecha:** 1 de septiembre de 2026
**Estado:** aceptado
**Ámbito:** marco experimental, pregunta de investigación, alcance
**Decide:** Luis Daniel Díaz (autor)
**Registro:** ADR **académico**. Numeración independiente de los 37 ADR técnicos de
`mecanico-ia/docs/adr/`, que conservan la suya y no se renumeran. Para evitar ambigüedad,
los ADR de este registro se citan siempre como `research/decisions/ADR-NNN`.

---

## Contexto

A 1 de septiembre de 2026 coexistían **dos marcos experimentales** para el mismo Trabajo Fin
de Máster, ambos internamente coherentes y **mutuamente incompatibles como estructura única
de la memoria**.

| | `mecanico-ia` | `mecanico-ia-exp` |
|---|---|---|
| Naturaleza | monorepo de ingeniería, 28 fases documentadas | laboratorio experimental, creado el 2026-09-01 |
| Subpreguntas | PI.a … PI.f (6) | PI.1 … PI.4 (4) |
| Hipótesis | H-MAIN, H-GRD, H-TRC, H-ABS, H-SEL | enunciadas por subpregunta |
| Experimentos | EXP-SEG-001, EXP-RET-001, EXP-EVID-001 | E1 … E20 |
| Métricas | M1 … M24 | M1 … M6 |
| Control de evidencia | Escenarios A/B, corpus C-A / C-B / C-B′ | FULL / PARTIAL / ABSENT / **DISTRACTOR** |
| Datos | generación determinista por semilla | sintéticos (E2, cerrada) + reales (E3, **bloqueada**) |
| Pre-registro | `prereg-v1.0` congelado, enmienda ENM-001 | umbrales a fijar al cerrar E15 |
| Estado experimental | 3 experimentos pendientes, 2 bloqueados | E1 y E2 cerradas, E3 bloqueada |

La pregunta de investigación está enunciada de forma **idéntica** en ambos. Lo que difiere es
su descomposición operativa, la nomenclatura y el régimen de datos.

Mantener los dos vivos producía tres problemas concretos: duplicación de esfuerzo sobre un
calendario con el primer informe de seguimiento a 17 días; imposibilidad de cerrar una matriz
de trazabilidad única; y un capítulo 4 de la memoria que describía un diseño experimental
distinto del que se estaba ejecutando.

## Problema

¿Qué marco define la estructura científica del TFM, y qué se hace con el otro?

## Opciones consideradas

### A. Continuar con `mecanico-ia`

**A favor.** Pre-registro congelado con enmienda fechada. Matriz de trazabilidad completa,
con cobertura directa e inversa y sin experimentos huérfanos. 14 estudios ejecutados, cuatro
resultados negativos publicados y un control de integridad. 37 ADR. Instrumento de auditoría
de contaminación ya implementado y usado.

**En contra.** Su experimento central está bloqueado por dos defectos de instrumento
documentados: el generador diagnóstico fue rechazado (D1) y la formulación de la consulta de
`EXP-RET-001` no está declarada. El diseño no contempla la condición DISTRACTOR. Los datos
son generados, no reales, mientras la pregunta habla de datos reales.

### B. Continuar con `mecanico-ia-exp`

**A favor.** Cadena experimental completa y ordenada en veinte fases con criterios de
aceptación comprobables. Separación explícita entre decisión de suficiencia (determinista,
fuera del modelo de lenguaje) y redacción de la explicación. Condición DISTRACTOR, que mide
*pertinencia* y no solo *presencia* de evidencia. Conjunto de test cerrado hasta E19 y
umbrales calibrados solo con validación. Modelo de evidencia con dos ramas —observacional y
documental— y verificación determinista del soporte en tres pasos. Cuatro afirmaciones
prohibidas por escrito en código, figuras y memoria.

**En contra.** Solo dos fases cerradas. E3 —datos reales— bloqueada por una decisión abierta.
Ningún modelo entrenado, ningún corpus indexado, ningún caso ejecutado. El pre-registro
congelado no le pertenece.

### C. Fusionar ambos marcos

**A favor.** No se pierde nada.

**En contra.** Las nomenclaturas no son biyectivas: PI.a-PI.f no mapean a PI.1-PI.4, y
M1-M24 no mapean a M1-M6 —peor aún, **`M1` significa cosas distintas en cada marco**. Una
fusión produciría una memoria con dos sistemas de identificadores solapados, que es la
situación que esta decisión pretende terminar. El coste de reconciliar excede al de rehacer.

## Decisión

**El marco canónico del TFM es `mecanico-ia-exp`.**

A partir de esta fecha y para todos los efectos de la memoria:

- La **pregunta de investigación vigente** es la de `mecanico-ia-exp`.
- Sus **subpreguntas PI.1-PI.4** constituyen el marco de descomposición actual.
- Sus **experimentos E1-E20** constituyen el marco experimental vigente.
- Sus **métricas M1-M6** son las métricas canónicas.
- Sus **condiciones FULL / PARTIAL / ABSENT / DISTRACTOR** son el diseño experimental vigente.
- E15 y las demás fases se evalúan dentro de esta estructura.

## Tratamiento de `mecanico-ia`

Se clasifica como **`LEGACY_RESEARCH_SOURCE`**.

**No es un segundo marco experimental concurrente.** No se ejecutan experimentos nuevos en él
para este TFM.

Puede contener, y de hecho contiene, material potencialmente reutilizable: experimentos
anteriores, resultados negativos, datasets, código, decisiones, referencias, análisis
exploratorios, métricas y aprendizajes metodológicos.

**Ningún elemento pasa automáticamente al TFM.** Todo traslado atraviesa esta cadena:

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

Inventario y estado de cada candidato: `research/legacy-map.md`.

**Prohibiciones explícitas de nomenclatura.** No se mezclan nunca:

- `PI.a`-`PI.f` con `PI.1`-`PI.4`;
- `M1`-`M24` (legacy) con `M1`-`M6` (canónicas) — **la colisión de `M1` es real y es la
  razón por la que toda métrica legacy se escribe `LEG-M{n}` al citarse**;
- `EXP-*` con `E{n}`;
- Escenarios A/B con FULL/PARTIAL/ABSENT/DISTRACTOR.

Todo elemento importado conserva su identificador de origen y recibe uno canónico, con la
correspondencia escrita.

## Consecuencias

**Ninguna evidencia antigua entra automáticamente en metodología, resultados, discusión ni
conclusiones.** Debe superar antes los gates correspondientes.

| Ámbito | Consecuencia |
|---|---|
| Capítulo 3 (marco teórico) | El barrido documental se conserva: es E1 y su validez no depende del marco experimental. Pero **las cadenas de búsqueda deben revisarse** para cubrir la condición DISTRACTOR, que el barrido anterior no contemplaba |
| Capítulo 4 (metodología) | Se reescribe sobre E1-E20, M1-M6 y las cuatro condiciones. El borrador actual describe el marco legacy |
| Capítulo 5 (resultados) | No puede redactarse: no hay resultados en el marco canónico más allá de la caracterización de los datos sintéticos |
| Capítulo 6 (conclusiones) | Depende del 5 |
| Pre-registro | Ver `research/prereg-classification.md`. **No se modifica retroactivamente** |
| Objetivos | Los OE-M1-OE-M5 de la memoria siguen siendo válidos como objetivos del TFM, pero su correspondencia con los experimentos se rehace: OE-M3, OE-M4 y OE-M5 apuntaban a experimentos legacy |
| Trazabilidad | `research/traceability-matrix.md` se reconstruye sobre el marco canónico |

## Justificación

Tres razones, en orden de peso.

**1. El marco canónico puede ejecutarse; el legacy está bloqueado en su experimento central.**
D1 rechazó el generador y la formulación de la consulta de `EXP-RET-001` sigue sin declarar.
Desbloquear ambos exige decisiones que, tomadas ahora, equivalen a rediseñar.

**2. La condición DISTRACTOR mide algo que el marco anterior no medía.** FULL y ABSENT
comprueban que el sistema responde a la *presencia* de evidencia. DISTRACTOR comprueba que
responde a su *pertinencia*. Un sistema que confunda similitud con soporte pasa las tres
primeras y falla esta. Dado que la pregunta de investigación trata precisamente de distinguir
una explicación sostenida de una plausible, esa condición no es un extra: es el contraste
más directo de la tesis.

**3. La decisión de suficiencia vive fuera del modelo de lenguaje.** Si la tomara el propio
modelo, la respuesta a la pregunta de investigación dependería de su disposición a admitir
que no sabe algo — que es justo lo que no puede darse por supuesto.

**Lo que esta decisión cuesta, y se acepta a sabiendas:** se renuncia a un pre-registro ya
congelado y a una matriz de trazabilidad cerrada, a cambio de un marco que aún tiene que
producir los suyos. El coste es real y se declara en las limitaciones del TFM.

## Impacto

| Elemento | Impacto |
|---|---|
| Pregunta de investigación | enunciado sin cambios; descomposición sustituida |
| Objetivos | vigentes; su cobertura experimental se rehace |
| Experimentos | E1-E20 vigentes; EXP-* pasan a legacy |
| Métricas | M1-M6 vigentes; M1-M24 pasan a `LEG-M*` |
| Capítulos de la memoria | 4, 5 y 6 se rehacen sobre el marco canónico |
| Pre-registro | clasificado, no reescrito. Puede requerir un pre-registro nuevo para E15/E19 |

## Evidencia

| Tipo | Fuente |
|---|---|
| E5 | `mecanico-ia-exp/docs/plan_experimental_macbook.md` — plan por fases y clasificación de componentes |
| E5 | `mecanico-ia-exp/docs/matriz_validacion_pi.md` — PI.1-PI.4, criterios y desenlaces de refutación |
| E5 | `mecanico-ia-exp/docs/methodology/` — modelo de evidencia, diseño experimental, política de abstención, métricas |
| E2 | `mecanico-ia/docs/fase28/informe_f28.md` — D1 rechazado; la formulación de la consulta bloquea `EXP-RET-001` |
| E5 | `mecanico-ia/docs/alineacion_v4/` — núcleo científico y trazabilidad del marco legacy |
| E4 | Instrucción explícita del autor, 1 de septiembre de 2026 |

## Reversibilidad

Revertir exigiría desbloquear D1 y la formulación de la consulta, y rehacer el capítulo 4
sobre el marco legacy. Se perdería la condición DISTRACTOR y la separación explícita de la
decisión de suficiencia. **No se contempla salvo que E3 resulte irresoluble** y el laboratorio
quede sin datos reales — en cuyo caso el problema no sería de marco sino de alcance de la
pregunta, y se resolvería con otro ADR.

---

**Un ADR superado no se borra: se marca como superado y se enlaza el que lo sustituye.**
