# Limitaciones

Resumen para el tribunal del registro de limitaciones del proyecto. **La fuente es
`research/limitations-register.md`**: cada entrada tiene allí qué limita, de dónde procede,
severidad, estado y qué haría falta para levantarla. Este documento no añade limitaciones ni
cambia severidades; ordena las existentes por lo que importa a quien evalúa el trabajo.

## Las dos críticas

**L-01 · Los datos sintéticos no tienen validez externa.** Toda la telemetría OBD-II es
generada por un simulador paramétrico calibrado contra el manual de taller del vehículo. La
validación con datos reales (E3) no se ejecutó: desde ADR-003 es validación externa, no
precondición de la pregunta, pero sigue sin fuente. Nada de lo medido sobre diagnóstico
(E6, E7, E9) puede extrapolarse a vehículos reales.

**L-20 · Espacios de embeddings mezclados en toda la recuperación** (hallazgo
`MIXED-EMBEDDING-SPACE`, 4-09-2026). El índice contenía dos representaciones vectoriales de
cada fragmento y ninguna búsqueda declaraba cuál usaba. La corrección está implementada y
probada; los resultados de recuperación anteriores (E12, E15, E13) quedaron marcados como
reproducibles pero no canónicos. La reejecución pre-registrada RERUN-A se ejecutó el 13 y 14 de
septiembre: las decisiones no cambiaron y los conjuntos recuperados sí, en 10 de 17 casos; por
el criterio fijado de antemano, «sin efecto detectable con este instrumento». Queda abierto el
adaptador LoRA, entrenado sobre el conjunto anterior y no reentrenado
(`docs/experiments/resultado-rerun-a.md`).

## Alcance de lo que se puede afirmar

| Id | Limitación | Severidad |
|---|---|---|
| L-17 | Todas las cifras disponibles son de validación; el conjunto de test está cerrado por excepción y nunca se abrió | baja (por diseño), pero condiciona toda lectura |
| L-19 | Los resultados describen un solo vehículo (Mazda 3 BK 2007, motor Z6) | alta |
| L-13 | El alcance ejecutado es más estrecho que el alcance aprobado por la dirección (pregunta abierta P-03) | alta |
| L-21 | El catálogo de fallos del modelo de diagnóstico es cerrado: cinco condiciones más normal | media |
| L-15 | Dos de las seis condiciones no son plenamente detectables, por motivos distintos | media |
| L-02 | Dos de los cinco fallos son invisibles en las medias de las señales | alta |
| L-14 | La confianza del baseline está mal calibrada (ECE 0,144 sin calibrar; 0,085 con calibración isotónica) | alta |
| L-18 | Dos ejecuciones con resultado negativo (NX-01, NX-02) no llegaron al capítulo de resultados | alta |
| L-10 | La afirmación de novedad sobre PI.4 (distractores) es más estrecha de lo que parecía; resuelta parcialmente | alta |

## Método y evidencia documental

| Id | Limitación | Severidad |
|---|---|---|
| L-07 | Se abandonó un pre-registro ya congelado (`prereg-v1.0`, 18-08-2026); el marco canónico documenta el cambio en ADR-002 en lugar de reescribirlo | alta |
| L-03 | Las fichas de fallo del generador no tienen respaldo documental verificado | alta |
| L-06 | La atribución (SHAP) no es causalidad | alta |
| L-16 | El descriptor informado por la física no está validado con datos reales | media |
| L-12 | Se desconoce si un juez basado en modelo de lenguaje sería fiable aquí; por eso el verificador es determinista | media |
| L-08 | El barrido documental del marco teórico no es un flujo PRISMA formal | alta |
| L-09 | Tres trabajos relevantes sin leer a texto completo | media |
| L-05 | Una correlación marginal baja no implica ausencia de relación | media |
| L-04 | El reparto por régimen de conducción está desequilibrado | baja |
| L-11 | El presupuesto de cómputo se mide sobre hardware de sobremesa (Apple M4 Pro); nada se validó en dispositivos embarcados | alta |

L-22 (incorporación de conocimiento reutilizable) se retiró el 12-09-2026 con ADR-004: pertenecía
a la formulación amplia de la pregunta, descartada por la dirección.

## Limitaciones que este repositorio añade como artefacto

No están en el registro porque no son del experimento sino de su entrega, y se declaran aquí:

- El corpus documental (manual de taller, 3 055 PDF) **no se redistribuye** y entra por un
  enlace simbólico a la máquina del autor; un tercero no puede ejecutar E11–E15 sin
  conseguirlo por su cuenta (`corpus/vehicles/mazda-3-bk-2007/manifest.yaml`).
- Siete registros JSON anteriores al 4-09-2026 carecen de `commit` y `executed_at`; su
  procedencia se reconstruye solo por el historial Git.
- Los registros no graban la máquina (plataforma, versiones); se conoce por E1 y `uv.lock`.
- No existe integración continua: los gates de calidad se ejecutan a mano.
