# Paquete de diseño de PI.1 — solo protocolos, nada ejecutado

**Fecha:** 12 de octubre de 2026 · **Estado: diseño, pendiente de aprobación.** No se ha ejecutado
ningún experimento, no se ha generado ningún conjunto de datos, no se ha reentrenado ningún modelo, no
se ha tocado ningún conjunto histórico y no se ha abierto ninguna partición de prueba.

## Para qué es esto, y para qué no

El tutor reformuló PI.1: no «¿pasamos el conjunto a series temporales?» sino **¿en qué tipos de fallo
el contexto temporal aporta señal diagnóstica adicional y en cuáles no?**. La auditoría del 5 de
octubre (`docs/auditoria-pi1-contexto-temporal.md`) encontró que la comparación ya existía, ejecutada
dos veces, y que tres cosas la invalidaban como evidencia: la asimetría en la selección de época, la
confusión entre representación y estimador, y que el conjunto grande se generó **antes** de calibrar el
generador contra el manual.

Este paquete diseña cómo arreglarlo. No es una línea de investigación nueva.

**Y conviene decir qué no es.** La pregunta de investigación del TFM es si un sistema híbrido puede
identificar patrones no representados en su conocimiento disponible, generar hipótesis diagnósticas
desde el análisis contextual y longitudinal de datos OBD-II, y validarlas con evidencia antes de
incorporarlas como conocimiento reutilizable. PI.1 es **una pieza** de eso: qué información diagnóstica
aporta cada representación de la telemetría y cuáles son sus límites. **No es una investigación
independiente sobre qué arquitectura de aprendizaje automático es superior**, y si en algún momento
estos protocolos empiezan a parecerlo, hay que recortarlos. El objeto de evaluación sigue siendo el
sistema completo.

## Los doce documentos

| # | Documento | Fase | Qué decide |
|---|---|---|---|
| 1 | `01-correcciones-e7-e2.md` | A | Qué corregir en el informe de E7 y en la fila E2 del índice, con la evidencia de cada corrección |
| 2 | `02-protocolo-synthetic-v4.md` | B | Cómo se genera el conjunto canónico nuevo, y por qué no sustituye a `synthetic_v2` |
| 3 | `03-manifiesto-procedencia.md` | B | El esquema que permite responder «¿con qué configuración exacta se generó esta sesión?» |
| 4 | `04-subconjuntos-anidados.md` | C | Los cuatro volúmenes, cómo se anidan y cómo se evita la fuga |
| 5 | `05-protocolo-comparacion.md` | D | El protocolo simétrico entre bosque y red recurrente |
| 6 | `06-plan-replicas.md` | E | Cuántas réplicas, con qué semillas, a qué coste y cómo se resume la dispersión |
| 7 | `07-ablacion-representacion.md` | F | Las tres representaciones, y qué comparación aísla qué |
| 8 | `08-analisis-por-fallo.md` | G | Cómo se comprueba —no se asume— qué pasa con el termostato y con el encendido |
| 9 | `09-matriz-conclusiones-afectadas.md` | H | Qué afirmaciones del capítulo 5 siguen válidas, cuáles hay que matizar y cuáles caen |
| 10 | `10-plan-reejecucion.md` | I | El orden, las dependencias, el coste, los criterios de integridad y de parada |
| 11 | `11-riesgos-metodologicos.md` | — | Lo que puede salir mal y qué lo detectaría |
| 12 | `12-trazabilidad-pi1.md` | — | La cadena de PI.1 de la pregunta al artefacto |

## Las cinco decisiones que piden aprobación

1. **`synthetic_v4` se genera pero no se adopta como canónico.** La cadena de E19 queda congelada sobre
   `synthetic_v2`, y `v4` sirve solo a PI.1. Adoptarlo obligaría a regenerar E4, E5, E6, E9 y toda la
   cadena de suficiencia, que acaba de cerrarse.
2. **La curva de volumen se mide dentro de `v4`**, con subconjuntos anidados de entrenamiento y
   validación fija, no comparando conjuntos distintos.
3. **La selección de época pasa a una partición interna de entrenamiento.** Sin eso ninguna comparación
   entre los dos modelos es interpretable, y esto cambia las cifras de E7 que hoy están publicadas.
4. **Cinco semillas, declaradas en este paquete antes de ejecutar.** Las comparaciones se hacen
   **apareadas** por semilla.
5. **La comparación entre bosque y red recurrente se enuncia como diferencia entre dos recorridos
   completos**, no como efecto del contexto temporal, mientras no exista un diseño 2×2 que lo aísle.
   Ese diseño 2×2 **no** se propone: ampliaría el alcance del TFM.

## Lo que este paquete deja fuera a propósito

El rediseño de la condición con distractor, el reentrenamiento del adaptador y las ablaciones de E18
sobre el conjunto de prueba, que son las tres prioridades que el tutor puso por delante de cualquier
ampliación temporal. Y la validación externa con telemetría real, que sigue siendo trabajo posterior.
