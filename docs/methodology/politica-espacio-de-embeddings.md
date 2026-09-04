# Política de aislamiento del espacio de embeddings

**Fecha:** 4 de septiembre de 2026 · **Motivada por:** hallazgo `MIXED-EMBEDDING-SPACE`
(`RAG-CRT-043`, `TUTOR-CRT-001`) · **Estado:** documentada **antes** de tocar código y de
reejecutar. El commit que introduce este documento y sus pruebas precede al de la corrección y
al de los resultados nuevos.

**Severidad:** `CRITICAL`. Es el primer hallazgo de esta clase en el trabajo: no acota una
afirmación, **invalida la procedencia** de todo conjunto recuperado hasta esta fecha.

## 1. El defecto, exacto

El índice contiene **dos vectores por fragmento**, de dos modelos distintos:

| Modelo | Vectores |
|---|---|
| `sentence-transformers/all-MiniLM-L6-v2` | 6 158 |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 6 158 |
| Fragmentos en el corpus | **6 158** |

La convivencia es deliberada: permite comparar modelos. Lo que falla es que **ninguna búsqueda
declara en cuál de los dos busca**. `PgVectorStore.search` acepta `embedding_model`, lo aplica
al SQL solo si no es nulo, y **su valor por defecto es nulo**. `recuperar()` lo propaga
correctamente, pero **ninguno de los cuatro puntos de llamada lo pasa**.

Consecuencia: cada consulta ordenó por distancia sobre **12 316 vectores de dos espacios
semánticos incompatibles**, mientras el artefacto declara uno solo. Un mismo fragmento podía
ocupar dos posiciones del resultado con puntuaciones distintas.

## 2. Agravante, y es lo que convierte esto en un resultado

El propio código **describe el defecto** y la línea siguiente lo permite:

```python
# El modelo de embeddings acota la búsqueda. Un índice puede contener
# vectores de varios modelos --conviven a propósito, para poder
# compararlos-- y mezclarlos en una misma consulta compararía puntos de
# espacios distintos: los resultados serían ruido con aspecto de orden.
condiciones = ["e.vehicle_id = :vehicle_id"]
if embedding_model:                      # ← opcional
```

El razonamiento correcto estaba escrito. Lo que faltó fue hacerlo **obligatorio**. Es la cuarta
aparición del mismo patrón del trabajo: **ausencia de información tratada como ausencia de
restricción** —parámetro nulo, señal sin vocabulario, lista de códigos vacía, motor no
declarado—. Aquí, además, con la advertencia escrita al lado.

La documentación (`docs/rag/multilingual.md`) **afirma que la búsqueda filtra**, y cita como
prueba un test que pasa el parámetro a mano: una garantía que no cubría la ruta real.

## 3. Alcance medido en los artefactos congelados

Posiciones del resultado ocupadas por un fragmento ya presente, por artefacto:

| Artefacto | Posiciones | Repetidas | Casos afectados |
|---|---|---|---|
| `E15_suficiencia.json` (oracular, vigente) | 150 | **24 (16,0 %)** | 6 de 17 |
| `E15_suficiencia_non_oracle.json` | 150 | 24 (16,0 %) | 6 de 17 |
| `E15_suficiencia_verifier_v1.json` | 99 | 6 (6,1 %) | 2 de 17 |
| `E15_suficiencia_verifier_v2.json` | 195 | 27 (13,8 %) | 7 de 17 |
| `E15_suficiencia_verifier_v2_1.json` | 150 | 24 (16,0 %) | 6 de 17 |
| `E15_suficiencia_adverse.json` | 24 | 0 | 0 de 6 |

El escenario adverso queda libre porque usa otra estrategia de recuperación.

## 4. Las tres rutas afectadas

| Ruta | Punto de llamada | Qué produjo |
|---|---|---|
| **R-1 · suficiencia** | `sufficiency_runner.py:207` | E15, E17 y las variantes no oracular y adversa |
| **R-2 · recuperación y agente** | `retrieval_runner.py:180,249` | E12, la tabla de comparación de estrategias, y E13 a través de los paquetes de evidencia |
| **R-3 · datos de ajuste** | `training_runner.py:113` | el conjunto con que se ajustó el adaptador del modelo de lenguaje |

R-3 es la más incómoda: los datos de ajuste **ya están generados** y el adaptador ya está
entrenado sobre ellos.

## 5. Implementación canónica, decidida aquí

> **E-1.** `PgVectorStore.search` **exige** `embedding_model`. Deja de tener valor por defecto.
> Una búsqueda sin espacio declarado es un error, no una búsqueda amplia.
>
> **E-2.** Cada punto de llamada pasa `provider.identity.model`, que es el mismo proveedor que
> vectoriza la consulta. El espacio de la consulta y el del índice son el mismo por
> construcción, no por disciplina de quien escribe la llamada.
>
> **E-3.** El modelo efectivo se registra en cada artefacto, y debe coincidir con el declarado.

E-1 es lo esencial: convierte el defecto en imposible en lugar de en improbable. Con un
parámetro opcional, el fallo reaparece la próxima vez que alguien añada una llamada.

## 6. Qué se reejecuta

E12 recuperación · E15 y E17 suficiencia, en sus tres modos · E13 agente · la generación de
datos de ajuste · y toda evaluación posterior que consumiera recuperación de esas rutas.

**No se presupone que el resultado nuevo sea mejor.** Puede empeorar: la mezcla de espacios
pudo tanto introducir ruido como colocar por casualidad un fragmento útil. Las cifras nuevas
son las canónicas sea cual sea su signo, y las antiguas se conservan congeladas.

## 7. Lo que este defecto no invalida

- La lógica del verificador de suficiencia, que opera **sobre** los fragmentos recuperados y
  cuyas reglas no dependen de cómo llegaron.
- Las mediciones sobre el corpus: 6 158 fragmentos, 4 175 sin motor declarado, 48 multimotor,
  272 secciones de procedimiento.
- Los hallazgos `LEXICAL-SUPPORT-CONFOUND`, `EMPTY-DTC-GATE-BYPASS` y
  `ENGINE-FILTER-PERMISSIVE`, que son propiedades de las reglas y no de la recuperación.
- Las líneas base, que se recalcularán sobre el resultado nuevo pero cuya construcción no
  depende de la recuperación.

## 8. Registro previo de la expectativa

Se declara antes de medir, para que el resultado sea interpretable:

**No hay expectativa direccional.** Eliminar la mitad de los candidatos de un espacio ajeno
puede subir o bajar cualquier cifra. Lo único que se afirma de antemano es que el resultado
nuevo **será interpretable** y el anterior no lo era, porque hasta ahora la procedencia de cada
fragmento recuperado era indeterminada.
