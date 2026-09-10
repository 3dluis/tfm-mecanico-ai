# 02 · ¿Puede el aparato experimental cerrar el ciclo de la pregunta?

Comprobación pedida antes de llegar al capítulo 5: si los experimentos existentes permiten
cerrar **identificación de patrón no representado → hipótesis → evidencia → validación →
incorporación**. Verificado contra el código y los registros el 10 de septiembre de 2026.

**Respuesta: no.** Dos de los cinco eslabones no tienen instrumentación y un tercero existe
pero no alimenta al agente. El ciclo se cierra en su tramo central, no de extremo a extremo.

## Eslabón por eslabón

| Eslabón | Estado | Verificación |
|---|---|---|
| **Identificación de patrón no representado** | **sin instrumentación** | Búsqueda de `out_of_distribution`, `unseen`, `novel_fault`, `open_set`, `no_representado` en `src/`: cero coincidencias. El modelo es un clasificador de conjunto cerrado sobre clases etiquetadas. No existe definición operacional de «no representado», ni condición experimental que la construya |
| **Generación de hipótesis** | **sin componente** | `hipótesis`/`hypothes` aparece dos veces en `src/`, ambas en prosa de documentación (`__init__.py:6`, `llm/agent.py:18`). Ningún componente genera una hipótesis diagnóstica: el modelo clasifica y el agente redacta |
| **Evidencia** | **presente** | Recuperación sobre el manual con filtro de aplicabilidad; `n_documents_retrieved` y `n_documents_applicable` en los 17 casos |
| **Validación** | **presente** | Verificador determinista, `claim_coverage`, criterio de suficiencia y abstención. Es el núcleo ejecutado |
| **Incorporación como conocimiento reutilizable** | **sin instrumentación** | Búsqueda de `reutilizab`, `knowledge_base`, `write_back`, `incorpor` en `src/`: cero coincidencias |

## El eslabón que existe y está desconectado

`src/mecanico_ia_exp/models/temporal.py` implementa el modelo recurrente sobre la ventana. Lo
importan `experiments/temporal_runner.py` y `models/training.py`. **No lo importa
`experiments/sufficiency_runner.py`**, que es la ruta del agente y diagnostica con
`RandomForestClassifier` (`sufficiency_runner.py:53-55`).

El «análisis contextual y longitudinal» que enuncia la pregunta existe como componente y no
interviene en el diagnóstico que el agente explica. Esto no es una carencia de implementación:
es una desconexión entre dos piezas que sí están construidas, y por eso se puede cerrar sin
investigación nueva.

## La afirmación del resumen, verificada

> «La disponibilidad de documentación no implica, por sí sola, disponer de evidencia suficiente
> para validar una hipótesis diagnóstica.»

**Se sostiene sin DISTRACTOR.** Registro `E15_suficiencia_verifier_v2_1.json`:

| caso | variante | recuperados | aplicables | cobertura | decisión |
|---|---|---|---|---|---|
| C07 | PARTIAL | 10 | 4 | 0,00 | abstiene · `LOW_CLAIM_COVERAGE` |
| C11 | PARTIAL | 10 | 6 | 0,00 | abstiene · `LOW_CLAIM_COVERAGE` |
| C15 | PARTIAL | 10 | 5 | 0,00 | abstiene · `LOW_CLAIM_COVERAGE` |
| **C04** | **FULL** | **10** | **4** | **0,00** | abstiene · `LOW_MODEL_CONFIDENCE`, `LOW_CLAIM_COVERAGE` |

Tres casos de evidencia parcial, sobre tres fallos distintos, recuperan entre cuatro y seis
documentos **aplicables al vehículo** y ninguna de las afirmaciones queda sostenida. La
afirmación no depende de la condición que sigue bajo diagnóstico.

**C04 es el caso más fuerte y no es de construcción.** Es condición FULL: no se retiró nada del
corpus. El sistema recupera diez documentos, cuatro aplicables, y la cobertura es 0,00. En
PARTIAL la evidencia de soporte se retira a propósito, de modo que la cobertura nula es en parte
consecuencia del diseño; en C04 no se retiró nada y ocurre igual.

**Reserva que conviene conocer.** Los recuentos de recuperación de esta tabla proceden de
búsquedas afectadas por `L-20`: son reproducibles y no canónicas. Si la reejecución canónica
cambia el conjunto recuperado, la cobertura podría cambiar con él. Por eso el resumen dice
«los experimentos registrados muestran» y no «se demuestra».

## Consecuencia

El desequilibrio entre eslabones **no se oculta**: el resumen declara que la identificación de
patrones no representados y la incorporación de conocimiento reutilizable forman parte del ciclo
que define la pregunta y que su evaluación permanece abierta, sin instrumentación en el diseño
ejecutado.

Tres caminos, y la elección no es de esta revisión:

1. **Conectar lo conectable.** El modelo temporal existe; hacer que el agente diagnostique con él
   cierra el «análisis longitudinal» sin investigación nueva. Es la única de las tres carencias
   que se resuelve con trabajo de ingeniería acotado.
2. **Instrumentar los dos eslabones ausentes.** Exige definición operacional de «no
   representado», una condición experimental que la construya, un mecanismo de incorporación y
   fases nuevas. No cabe en el calendario sin desplazar lo demás.
3. **Acotar la pregunta a lo que el aparato mide**, y llevar los dos eslabones a la prospectiva.
   Es lo que recomienda `SD-01`, y exige un ADR y hablarlo con la dirección.
