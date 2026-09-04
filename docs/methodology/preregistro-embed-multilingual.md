# Pre-registro de E-EMBED-MULTILINGUAL

**Fecha:** 4 de septiembre de 2026 · **Estado:** pre-registrado, **sin ejecutar** ·
**Sustituye a:** la medición translingüe anterior, que queda `NOT_VERIFIABLE` por no tener
guion, artefacto, configuración ni resultado reproducible.

**No es una reconstrucción de la cifra antigua.** Es una evaluación nueva. Si sus resultados no
coinciden con lo publicado, mandan los nuevos.

## 1. Qué es y qué no es

Es evidencia de una **decisión de ingeniería**: por qué el sistema usa un modelo de embeddings
multilingüe y no uno monolingüe. **No forma parte de la pregunta de investigación** y no
sostiene ninguna de sus subpreguntas.

## 2. Pregunta

> ¿Recupera mejor un modelo multilingüe que uno monolingüe inglés cuando la consulta está en
> español y el corpus en inglés?

## 3. Diseño

| | |
|---|---|
| **Consultas** | las de los seis casos del conjunto de recuperación original, en sus dos versiones, española e inglesa |
| **Idiomas** | consulta en español y en inglés; corpus solo en inglés |
| **Verdad de referencia** | los ficheros relevantes ya anotados en el conjunto |
| **Modelos comparados** | `all-MiniLM-L6-v2` frente a `paraphrase-multilingual-MiniLM-L12-v2` |
| **Espacios** | uno por modelo, **filtrados**: es justamente lo que el defecto impedía |
| **Métricas** | tasa de acierto, precisión y ganancia acumulada descontada en la posición 10, y posición del primer relevante |
| **Unidad** | consulta |
| **Denominadores, propios de este experimento** | `n_evaluated = 6` consultas por idioma y modelo · `n_scored` = las que tienen ficheros relevantes en la verdad de referencia, **por determinar antes de ejecutar** · `n_excluded_from_metric` con su motivo |
| **Condición** | sin filtro por código ni por motor, para que solo compita la semántica |

## 4. Criterio de interpretación, fijado antes

| Desenlace | Lectura |
|---|---|
| El multilingüe supera al monolingüe **con consulta en español** | la elección del modelo queda justificada, con N = 6 y sin generalizar |
| No lo supera | **se retira la afirmación de superioridad translingüe** y el modelo se presenta como decisión técnica sin respaldo empírico |
| Ninguno recupera lo relevante en español | el resultado es sobre el corpus, no sobre los modelos, y así se dice |

**Consecuencia aceptada de antemano:** si la evaluación no reproduce la ventaja, **el modelo por
defecto del sistema queda sin justificación empírica**, y eso se escribe.

**No hereda el denominador de la recuperación.** Es otro experimento: fija su propia unidad,
sus propios evaluados y puntuados, y sus propias exclusiones. Compartir «N = 6» por comodidad
fue el error que arrastró este documento en su primera versión, y viene de la misma familia que
confundir evaluados con puntuados.

## 5. Precondición

Exige un índice con **ambos** espacios completos: 6 158 vectores de cada modelo. Se comprueba
antes de ejecutar, no se supone.

## 6. Alcance

N = 6 consultas, un vehículo, un corpus. No autoriza ninguna afirmación general sobre modelos
de embeddings. Si al diseñarla se concluye que añade demasiado alcance al trabajo, se elimina la
afirmación de superioridad y el modelo se presenta como decisión técnica. **Lo que no se hace
es conservar una cifra sin artefacto.**
