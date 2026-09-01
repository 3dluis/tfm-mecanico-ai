# Modelo de evidencia

## Dos clases de evidencia

**Observacional.** Procede de los datos del vehículo: una señal, en una ventana
temporal concreta, con un valor o un patrón concreto. La produce la cadena
OBD-II → ventanado → descriptores → modelo → atribución.

**Documental.** Procede del corpus: un fragmento de un documento, con su fuente,
sección y página. La produce la recuperación.

Una explicación diagnóstica se sostiene sobre ambas. La observacional dice *qué
se ve en este vehículo*; la documental dice *qué significa eso*. Ninguna de las
dos basta por sí sola.

## Cadena de trazabilidad

```
claim → observation → signal → time window → value/pattern
     └→ chunk → document → source → section/page
```

Toda afirmación de una explicación debe poder recorrerse hasta el final de al
menos una de las dos ramas. Una afirmación que no lo consiga es una afirmación
sin soporte, y se contabiliza como tal.

## Registro de la atribución

```
explanation_id
model_id
case_id
signal
window
importance
direction
```

La atribución identifica siempre qué función del modelo se está explicando.
Explicar una salida sin declarar cuál se explica no es explicar.

**La atribución no es causalidad.** Indica de qué depende la salida del modelo,
no qué le ocurre al vehículo. Un descriptor puede dominar la atribución por estar
correlacionado con la causa real sin ser la causa. Ningún artefacto del
laboratorio —código, figura o texto— presentará la atribución como causa.

## Procedencia documental

Cada fragmento conserva, como mínimo:

```
document_id, chunk_id, title, source, section, page,
dtc, vehicle_system, reference
```

La procedencia se conserva **durante** el troceado, no se reconstruye después.
Un fragmento que ha perdido su página no se puede citar: no hay forma de que un
lector verifique la afirmación que se apoya en él, y una cita que no se puede
verificar no cumple su función.

## Lo que la recuperación no garantiza

Que un fragmento sea recuperado significa que es **similar** a la consulta. No
significa que sea correcto, ni pertinente, ni suficiente.

- Similitud no es pertinencia: la condición DISTRACTOR existe precisamente para
  medir esta diferencia.
- Recuperación no es verdad: el corpus puede contener afirmaciones erróneas.
- Un fragmento no es soporte: para serlo, su contenido tiene que sostener la
  afirmación concreta que lo cita, y eso se verifica aparte.

## Verificación del soporte

No basta con citar. Para cada afirmación se comprueba, de forma determinista y
sin intervención de un modelo de lenguaje:

1. que la referencia **existe** en el corpus;
2. que **resuelve** al fragmento que dice resolver;
3. que su contenido **sostiene** lo afirmado.

Los tres pasos son necesarios. Una referencia que existe y resuelve pero no
sostiene lo afirmado es exactamente el fallo que este trabajo busca detectar: una
cita de aspecto impecable respaldando algo que no dice.

## Distinciones que no se colapsan

| | |
|---|---|
| **Anomalía** | el comportamiento se aparta de lo esperado |
| **Predicción** | la salida de un modelo |
| **Diagnóstico** | una conclusión sobre el estado del vehículo |
| **Evidencia** | lo que sostiene una afirmación |
| **Causalidad** | una relación de causa y efecto |

Una anomalía no es un fallo confirmado. Una predicción no es un diagnóstico
confirmado. Una atribución no es una causa. Un fragmento recuperado no es una
verdad. El texto de un modelo de lenguaje no es una fuente técnica.
