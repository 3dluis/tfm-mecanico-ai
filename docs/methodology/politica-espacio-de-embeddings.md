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

**Cifra canónica, con la unidad definida en `preregistro-rerun-a.md` §7:**

> **27 posiciones duplicadas de 140 posiciones recuperadas, en 10 de 14 ejecuciones con
> conjunto no vacío.**

Es **idéntica en los cinco artefactos no adversos**, como debe ser: mide el índice, no el
verificador. Verificada de forma independiente por dos auditorías y por recuento propio desde
la definición.

**Reconstrucciones históricas, conservadas y no comparables entre sí.** La primera versión de
este documento publicaba «24 de 150» sin declarar la unidad, y distintas reconstrucciones daban
24/150, 27/195, 6/99 y 8/50 **para la misma recuperación**. No eran prevalencias distintas:
eran unidades distintas, y algunas medían el verificador en lugar del índice. Se marcan
`UNIT_UNDEFINED_IN_LEGACY_RESULT` y **no se comparan** con la cifra canónica ni entre ellas.

El escenario adverso queda aparte porque usa otra estrategia de recuperación, cuya fusión
colapsa los duplicados en lugar de eliminarlos: su cero **no significa que estuviera libre**.

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

---

## 9. Enmienda ENM-E01, durante la implementación

**Fecha:** 4 de septiembre de 2026, posterior a la §5 y anterior a reejecutar.

Al implementar E-2 el verificador de tipos destapó que **el defecto estaba un nivel más
arriba**: `recuperar()` también declaraba `embedding_model` como parámetro opcional con valor
nulo. Hacer obligatorio el parámetro en la capa de almacenamiento y seguir pasándolo a mano
desde tres sitios dejaba viva la misma clase de error, un escalón por encima.

**E-2 se sustituye por:**

> **E-2'.** `recuperar()` **no acepta** el espacio como parámetro: lo **deriva** de
> `provider.identity.model`, el mismo proveedor que vectoriza la consulta. Consulta e índice
> quedan en el mismo espacio por construcción, y no hay nada que un llamante pueda olvidar.

Es estrictamente más fuerte que lo documentado en §5 y sirve mejor a su intención. Se registra
como enmienda en lugar de corregir §5 en silencio.

## 10. Lo que la corrección destapó en las propias pruebas

Al hacer obligatorio el parámetro, **nueve búsquedas de la suite de integración dejaron de
compilar**: ninguna declaraba el espacio. Dos consecuencias:

**Primera.** El patrón defectuoso no estaba en tres sitios sino en doce, y la suite lo
reproducía en lugar de detectarlo. La única búsqueda que sí declaraba el espacio era la del
test que sostenía la garantía documentada, y era la única que no pasaba por la ruta real.

**Segunda, y peor:** esas pruebas construyen su vector de consulta con el proveedor `hashing` y
buscan contra un índice de vectores de `sentence-transformers`. Coinciden en dimensión y no en
espacio. Pasaban porque comprueban **propiedades estructurales** —orden, filtros, exclusiones—
que se cumplen con cualquier vector, y porque sin filtro la búsqueda siempre devolvía algo.

Quedan corregidas declarando el espacio del índice, con la salvedad escrita en el fichero: son
pruebas de estructura y no de relevancia. La observación se registra porque **una prueba que
consulta en un espacio ajeno no puede detectar un defecto de espacios**.
