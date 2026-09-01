# Evaluación de la recuperación

## Contra un conjunto anotado, no contra respuestas bonitas

Cada caso declara de antemano:

```
vehicle · diagnosis · relevant_document · relevant_section · relevant_chunk
```

Eso permite medir Recall@K, Precision@K, MRR y tasa de acierto en lugar de
inspeccionar a ojo si la respuesta del modelo suena convincente. Una respuesta
bien redactada sobre evidencia equivocada suena igual de bien.

## Condiciones experimentales

| Condición | Corpus | Comportamiento esperado |
|---|---|---|
| **FULL** | Manual de taller o fuente adecuada disponible | EXPLAIN con traza completa |
| **PARTIAL** | Solo manual del propietario o documentación general que menciona el sistema sin sustentar el diagnóstico | ABSTAIN, salvo explicación limitada declarada como tal |
| **ABSENT** | Se retiran del índice los fragmentos necesarios | ABSTAIN |
| **DISTRACTOR** | Documentación legítima pero de otro diagnóstico, otra condición o, en la versión exigente, **otro modelo o año** | Rechazo del distractor |

El distractor de otro modelo o año es la prueba más dura, y la que justifica todo
el aparato de aplicabilidad: el filtro por `vehicle_id` debe impedir que se use
como evidencia válida aunque su texto sea casi idéntico.

## Estado actual — bloqueado

Estas condiciones **no se pueden construir todavía**, por dos razones
independientes:

1. **No hay documentos.** Ningún documento del corpus piloto se ha podido
   obtener. Ver [ingestion.md](ingestion.md).
2. **No hay datos OBD-II del vehículo piloto.** Los datos actuales son
   sintéticos: los genera un modelo paramétrico que no corresponde a ningún
   vehículo real. Su `vehicle_id` no puede casar legítimamente con documentación
   de un Corolla, y el validador de aplicabilidad lo rechazará correctamente.

La condición FULL requiere que ambas cosas se resuelvan: documentación del
vehículo **y** datos OBD-II de ese mismo vehículo.

## La regla científica final

Una explicación diagnóstica no es trazable solo porque el sistema recuperó un
texto semánticamente parecido. Debe existir correspondencia verificable entre:

```
vehículo analizado + evidencia OBD-II + documentación aplicable + afirmación producida
```

y conservarse la procedencia completa de esa evidencia.
