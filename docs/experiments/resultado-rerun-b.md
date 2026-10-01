# Resultado de RERUN-B: la puerta de códigos con requisito explícito (v2.2)

**Fecha de ejecución:** 1 de octubre de 2026 · **Commit:** `d5fc372` · **Pre-registro:**
`docs/methodology/preregistro-e18-ablaciones.md` §5, congelado antes de medir · **Política
medida:** v2.2, definida en `docs/methodology/politica-puerta-dtc.md` · **Hallazgo que cierra:**
`EMPTY-DTC-GATE-BYPASS` (`docs/experiments/hallazgo-puerta-dtc-ausente.md`).

Los artefactos de v2.1 no se tocan. La ejecución escribe
`experiments/E15_suficiencia_v2_2.json`, `E15_suficiencia_non_oracle_v2_2.json` y
`E15_suficiencia_adverse_v2_2.json`, con el sufijo que el selector de política impone justamente
para que una medición de RERUN-B no pueda sobrescribir el registro canónico.

## Lo que cambia la política

Una sola cosa: el requisito de la puerta de códigos se lee de la **declaración** del diagnóstico
en el mapa de códigos —`DTC_REQUIRED`, `DTC_NOT_APPLICABLE`, `DTC_MAPPING_UNAVAILABLE` o
`DTC_OPTIONAL`— en lugar de exigirse siempre. Bajo v2.1, cuando la lista de códigos venía vacía la
comprobación no se ejecutaba y desaparecía una de las cuatro condiciones de soporte.

## Resultado, modo a modo

| Modo | Decisiones frente a v2.1 | Motivos de abstención | Afirmaciones sostenidas |
|---|---|---|---|
| Oracular, 17 casos | **idénticas** | idénticos | idénticas |
| No oracular, 17 casos | **idénticas** | idénticos | idénticas |
| Adverso, 6 ejecuciones | **idénticas** | idénticos | **cambian en dos** |

**El modo oracular confirma la predicción registrada.** Los cinco diagnósticos del conjunto están
declarados con códigos, de modo que el requisito es `DTC_REQUIRED` en todos y la puerta se
comporta igual. La regla de parada del pre-registro —si en oracular cambiara alguna decisión, el
cambio de política habría tocado más de una variable— no se activó.

**El modo adverso mide el hallazgo.** En ese escenario el diagnóstico del modelo es «sin fallo»,
que no está declarado en el mapa de códigos; el requisito pasa de `DTC_REQUIRED` a
`DTC_NOT_APPLICABLE` y ninguna afirmación puede sostenerse en evidencia documental:

| Caso | v2.1: afirmaciones sostenidas | v2.2 | Cobertura de afirmaciones |
|---|---|---|---|
| C02 termostato, evidencia completa | 2 de 3 | **0 de 3** | 0,67 → 0,00 |
| C04 fallo de encendido, evidencia completa | 2 de 3 | **0 de 3** | 0,67 → 0,00 |
| C10 a C13, termostato con evidencia retirada, parcial y con distractor | 0 de 3 | 0 de 3 | 0,00 → 0,00 |

Las seis ejecuciones terminaban ya en abstención bajo v2.1, y siguen terminando en abstención
bajo v2.2. Lo que cambia es **por qué**: bajo v2.1 el sistema aceptaba como soporte dos de las tres
afirmaciones construidas para un diagnóstico incorrecto, y se abstenía solo porque la cobertura,
0,67, no alcanzaba el umbral de 0,80. Bajo v2.2 no acepta ninguna.

## Qué queda cerrado y qué no

Queda cerrado el hallazgo: la puerta ya no se abre cuando el diagnóstico no tiene códigos
declarados, y está medido sobre el escenario donde eso ocurría. El efecto sobre el resultado
principal es **nulo**, y conviene decirlo así: la corrección no mejora ninguna cifra del conjunto
de diecisiete casos, porque en ese conjunto el requisito nunca fue otro que `DTC_REQUIRED`. Lo que
elimina es un soporte falso que el escenario adverso había dejado a la vista.

No queda cerrado qué política será la canónica para la evaluación final. v2.1 es la vigente y la
que sostiene las cifras publicadas; v2.2 es más estricta, no cambia ninguna decisión del conjunto
principal y corrige un defecto declarado. Adoptarla como canónica obligaría a reejecutar y
reescribir las cifras de recuperación y suficiencia una vez más, y es una decisión del autor:
queda registrada como pendiente, con la recomendación de adoptarla en la evaluación final, donde
el cambio entra con el conjunto de prueba y no reabre nada ya publicado.
