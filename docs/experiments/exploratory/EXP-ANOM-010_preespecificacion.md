# EXP-ANOM-010 — pre-especificación (F21)

**Escrita y commiteada ANTES de ejecutar.** Documento exploratorio: **no** es un
pre-registro confirmatorio (el pre-registro sigue sin congelar; regla F10). Su valor es
que los criterios numéricos y las predicciones quedan fijados con marca de tiempo de Git
anterior al primer resultado. Config declarativa:
[`ai-models/configs/exp-anom-010.yaml`](../../../ai-models/configs/exp-anom-010.yaml).

## Pregunta

¿El efecto de cobertura medido en el brazo control de EXP-ANOM-009 sobrevive cuando la
normalidad añadida se define **a priori desde el mecanismo del generador** en lugar de
diagnosticando los falsos positivos sobre el test?

## Por qué hace falta la réplica

El brazo control de F18 bajó el FPR de **0.129 → 0.0216** y subió F1 a **0.727**. Es el
mejor resultado de toda la serie de autoencoders, y **no es promovible**: la normalidad que
lo consiguió se eligió después de mirar en qué escenarios fallaba el modelo sobre el
conjunto de test. Eso es un criterio informado por test, y una métrica obtenida así no
puede sostener una adopción. F20 reconstruyó la misma cobertura desde el mecanismo
—paseo aleatorio del LTFT σ = 0.01 %/tick contra el cuanto J1979 de 0.78125 %, luego el
cruce exige **duración**— sin consultar el test. Esta réplica es la comprobación limpia.

## Hipótesis HX-ML-4

> Si el techo de EXP-ANOM-006…009 era **cobertura de normalidad** y no la representación,
> el mismo AE denso fs1 —sin tocar arquitectura ni hiperparámetros— entrenado con el banco
> v2 reproduce sobre el test histórico intacto el comportamiento del brazo control:
> FPR ≈ 0.02 y F1 ≈ 0.73.

Queda **refutada** si el FPR no baja según los criterios de abajo. No se reformula después
de ver los resultados, ni se sustituyen los criterios por otros más laxos.

## Brazos (cambio único = datos de entrenamiento)

| Brazo | Train | Papel |
|---|---|---|
| `lof_frozen` | v1.0, umbral 0.163197 (arms-freeze-v1) | control externo + integridad del pipeline |
| `ae_v11` | v1.1 (22 sesiones) | línea base interna |
| `ae_v2` | v1.1 + expansión v2 (34 sesiones) | **candidato de la réplica** |
| `lof_v2` | banco v2 | informativo; no candidato |

`ae_v11` y `ae_v2` comparten arquitectura, escalador, ventana (60/30), semillas y protocolo
de umbral. **El único cambio entre ellos es la cobertura del train**: eso es lo que hace
interpretable la diferencia.

## Criterios de decisión (fijados a priori)

**D1 — `ae_v2`**, mediana sobre semillas 42/43/44, test histórico:

- **PROMOTE_CANDIDATE**: mediana FPR ≤ 0.03 **y** todas las semillas ≤ 0.05 **y**
  mediana F1 ≥ 0.70 **y** mediana F1 > 0.6448 (LOF congelado).
- **PARTIAL**: mediana FPR ≤ 0.05 y mediana F1 ≥ 0.65 sin cumplir todo lo anterior.
- **REJECT**: mediana FPR > 0.05 **o** mediana F1 < 0.6448.

`PROMOTE_CANDIDATE` significa *candidato*, no adopción: la adopción exige un confirmatorio
posterior al freeze del pre-registro.

## Predicciones falsables

| | Predicción | Referencia |
|---|---|---|
| **P1** | FPR(`ae_v2`) < FPR(`ae_v11`) | F18: 0.1293 |
| **P2** | FPR de perfil `highway` de `ae_v2` ≤ 0.10 | brazo control F18: 0.0847 |
| **P3** | **negativa:** recall de `joint_slow_drift` y `load_coolant_decouple` sigue < 0.10 | la cobertura no arregla lo lento/relacional: es fallo de representación |
| **P4** | `lof_frozen` reproduce exactamente F18 (F1 0.6448, FPR 0.0345) | arms-freeze-v1 |

P3 es una predicción **negativa** deliberada: si falla, la lectura de la serie cambia y se
documenta el cambio en lugar de celebrarlo.

## Regla de parada

1. Si **P4** falla, el pipeline ha derivado: se detiene el experimento y se emite un informe
   de deriva. No se interpretan los brazos.
2. Si **D1 = REJECT**, dentro de F21 **no** se añade capacidad, ni arquitecturas nuevas, ni
   más datos: se emite informe de causa que decida entre *model failure* / *dataset coverage
   failure* / *anomaly construction failure*
   ([tipos de fallo](../tipos_de_fallo_experimental.md)).

## Fuera de alcance

Modificar inyecciones o su intensidad · regenerar datos para mejorar métricas · reoptimizar
LOF · tocar el test · semillas reservadas · cualquier ejecución confirmatoria.
