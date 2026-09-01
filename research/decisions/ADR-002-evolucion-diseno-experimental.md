# ADR-002 — Evolución material del diseño experimental y régimen del pre-registro

**Fecha:** 1 de septiembre de 2026
**Estado:** aceptado
**Ámbito:** diseño experimental, pre-registro
**Depende de:** [ADR-001](ADR-001-canonical-tfm-research-framework.md)

---

## Contexto

ADR-001 fija `mecanico-ia-exp` como marco canónico. Ese cambio **no altera el enunciado de la
pregunta de investigación** —es literalmente el mismo texto en ambos repositorios— pero sí
produce una **modificación material del diseño experimental**, y existe un pre-registro
congelado (`prereg-v1.0`, 2026-08-18, enmienda ENM-001) que fue escrito para el diseño
anterior.

Un pre-registro solo vale si no se reescribe cuando estorba. Por eso este ADR existe: para
documentar el cambio en lugar de disimularlo.

## Problema

¿Qué se hace con un pre-registro congelado cuyo diseño experimental ha sido sustituido?

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Reescribir `prereg-v1.0`** para que describa el diseño actual | Un solo documento coherente | **Destruye la función del pre-registro.** Un pre-registro modificable a posteriori no pre-registra nada. Descartada sin discusión |
| **B. Anularlo y declararlo sin efecto** | Simple | Se pierde el historial. Y no es cierto: varios de sus principios siguen rigiendo |
| **C. Conservarlo íntegro, clasificar sus elementos y registrar la evolución en un ADR** | Preserva la historia real; separa lo que sigue vigente de lo que no; el cambio queda fechado y justificado | Exige mantener dos documentos y una clasificación |

## Decisión

**Opción C.**

1. `prereg-v1.0` **se conserva íntegro y sin modificar** en `mecanico-ia/docs/experiments/`.
   No se edita, no se recorta, no se «actualiza».
2. Sus elementos se clasifican en
   [`research/prereg-classification.md`](../prereg-classification.md) como
   `STILL_APPLICABLE`, `SUPERSEDED`, `PARTIALLY_APPLICABLE`, `OUT_OF_SCOPE` o
   `REQUIRES_DECISION`.
3. **ENM-001 no se anula retroactivamente.** Queda como parte del historial.
4. El marco canónico necesitará **su propio pre-registro congelado**; su momento de
   congelación es una decisión abierta (ver más abajo).

## Qué cambió materialmente, y qué no

### No cambió

- **El enunciado de la pregunta de investigación.** Idéntico.
- **Los principios metodológicos**: pre-registro antes de ejecutar, conjunto de test
  intocable, banco inmutable congelado antes de ver salidas, sin paradas opcionales, sin
  cambio de métrica tras ver datos, los fallos de ejecución cuentan y no se excluyen del
  denominador.
- **La lógica de control de disponibilidad de evidencia**: retirar del corpus la evidencia
  relevante, con manifiesto y suma de verificación, y auditarlo de forma ejecutable.
- **La prudencia de alcance**: no se afirma descubrimiento de fallos desconocidos.

### Sí cambió

| Dimensión | Antes | Ahora |
|---|---|---|
| Descomposición de la pregunta | PI.a-PI.f (6 subpreguntas) | PI.1-PI.4 (4 subpreguntas) |
| Hipótesis | H-EVT, H-MEM, H-MAS, H-PERS, H-EXP, H-MAIN | enunciadas por subpregunta, con criterio de refutación por fila |
| Experimentos | EXP-* | E1-E20 |
| Métricas | 24, agrupadas por propiedad | 6 grupos, con métricas de atención prioritaria declaradas |
| Condiciones de evidencia | Escenarios A/B (presencia/ausencia) | FULL / PARTIAL / ABSENT / **DISTRACTOR** (presencia **y pertinencia**) |
| Origen del diagnóstico | detección de anomalías no supervisada (LOF) | modelo especializado supervisado con confianza calibrada |
| Papel de la confianza | no entraba en la decisión | **alimenta el criterio de suficiencia**, y por eso la calibración pasa a ser obligatoria |
| Decisión de suficiencia | política de abstención sobre umbral de soporte | componente determinista **fuera del modelo de lenguaje**, criterio conjuntivo de cuatro señales |
| Datos | generación determinista por semilla | sintéticos (E2) **y reales** (E3, pendiente) |
| Presupuesto edge | criterio de aceptación transversal | `[AUTHOR_DECISION_REQUIRED]`: criterio o medición descriptiva |

### El cambio de fondo

El diseño anterior preguntaba si el sistema reacciona a la **presencia** de evidencia. El
actual pregunta además si reacciona a su **pertinencia**. La condición `DISTRACTOR` —evidencia
parecida pero incorrecta— es un contraste que el diseño anterior no tenía, y es el que
distingue un sistema que sostiene afirmaciones de uno que las decora con citas plausibles.

Añadir esa condición **no es un ajuste**: cambia qué se puede concluir del experimento. Por
eso este ADR, y no una nota al pie.

## Régimen del pre-registro canónico

El marco canónico ya tiene por escrito, y **antes de ejecutar**:

- las cuatro subpreguntas con su hipótesis, dataset, experimento, métrica y criterio;
- los tres desenlaces admitidos (sostenida, parcialmente sostenida, no sostenida);
- cuatro desenlaces que refutarían la pregunta, enumerados de antemano;
- la regla de que los umbrales se calibran **solo con validación** y el test permanece cerrado
  hasta E19.

Le falta: los **valores numéricos** de los umbrales (por diseño, se fijan al cerrar E15), un
**documento congelado con fecha y hash**, y el **catálogo de controles negativos** de E17-E18.

`[AUTHOR_DECISION_REQUIRED]` — **Cuándo se congela.** Dos caminos legítimos:

- **Congelar ahora**, con los umbrales declarados como «a fijar en E15 sobre validación, por
  enmienda fechada». Es lo más cercano a la práctica anterior del proyecto.
- **Congelar al cerrar E15**, con los umbrales ya calibrados sobre validación y el test aún
  cerrado.

Ambos son defendibles. Lo que **no** es defendible es no elegir: sin documento congelado, la
diferencia entre «umbral calibrado sobre validación» y «umbral elegido tras ver resultados»
queda a merced de la memoria de quien lo cuente.

## Impacto

| Elemento | Impacto |
|---|---|
| `prereg-v1.0` | intacto; clasificado |
| ENM-001 | intacta; `SUPERSEDED` |
| Capítulo 4 | debe narrar **esta evolución**, no solo el diseño final. Un TFM que oculta que cambió de diseño pierde la parte más instructiva de su método |
| Capítulo 6 | la pérdida de un pre-registro ya congelado se declara en limitaciones |
| Auditor de contaminación | candidato de import prioritario (`legacy-map.md`) |

## Evidencia

| Tipo | Fuente |
|---|---|
| E5 | `mecanico-ia/docs/experiments/pre-registro-v1.md` (490 líneas, congelado 2026-08-18) |
| E5 | `mecanico-ia-exp/docs/matriz_validacion_pi.md` y `docs/methodology/experimental-design.md` |
| E4 | [ADR-001](ADR-001-canonical-tfm-research-framework.md) |
| E2 | `mecanico-ia/docs/fase28/informe_f28.md` — los dos bloqueos que motivaron el cambio |

## Reversibilidad

La clasificación es reversible: no destruye nada. La sustitución del diseño no lo es sin
rehacer el capítulo 4.
