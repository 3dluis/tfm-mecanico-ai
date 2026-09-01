# Plan experimental — MacBook Apple Silicon

Fecha: 1 de septiembre de 2026 · Autor: Luis Daniel Díaz · Entorno: MacBook Pro M4 Pro

Este documento fija el alcance del laboratorio, clasifica cada componente según
si hay que escribirlo, se puede reutilizar o queda fuera, y ordena el trabajo en
veinte fases con criterios de aceptación comprobables.

---

## 1. Pregunta de investigación

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de
> datos OBD-II reales, rastreando cada explicación hasta su evidencia de origen,
> y reconocer cuándo la evidencia disponible no es suficiente para sostener una
> explicación en lugar de generar una hipótesis sin fundamento?

La pregunta tiene tres exigencias separables, y el experimento debe poder
responder que sí o que no a cada una por separado:

1. **Explicación**: producir una explicación diagnóstica a partir de OBD-II real.
2. **Trazabilidad**: que cada afirmación de esa explicación se pueda seguir hasta
   una observación concreta o un fragmento documental concreto.
3. **Reconocimiento de insuficiencia**: que el agente se abstenga cuando la
   evidencia no basta, en lugar de rellenar el hueco con una hipótesis.

La tercera es la que distingue este trabajo. Un sistema que siempre explica
puede parecer excelente en las dos primeras y fallar por completo en la tercera.

## 2. Delimitación

El laboratorio **es** un banco de pruebas científico: genera datos, entrena un
modelo, indexa un corpus, ejecuta el agente, mide y produce figuras y tablas.

El laboratorio **no es** una segunda aplicación de producción, ni una
investigación sobre descubrimiento autónomo de fallos, memoria evolutiva,
aprendizaje continuo, promoción de hipótesis ni agentes científicos autónomos.
Nada de eso entra, aunque aparezca como extensión natural.

Cuatro afirmaciones quedan prohibidas en el código, en las figuras y en la
memoria, porque ninguna se sostiene: que la atribución sea causalidad, que lo
recuperado sea verdad, que la similitud sea evidencia suficiente, que una
anomalía sea un fallo confirmado, que la salida de un clasificador sea un
diagnóstico confirmado y que el LLM sea una fuente técnica.

## 3. Entorno oficial

| Componente | Versión verificada | Nota |
|---|---|---|
| Hardware | Apple M4 Pro, 24 GB | |
| Sistema | macOS 26.6.2 (Darwin 25.6.0), arm64 | |
| Python | 3.11.14 | gestionado por uv |
| uv | 0.10.2 | gestor oficial; sin `pip install` suelto |
| PyTorch | 2.13.0 | MPS disponible y comprobado con una operación real |
| PostgreSQL | 14.15 (Homebrew), servicio activo en 5432 | instalación preexistente |
| pgvector | 0.8.0 | disponible en PG14 e instalada en la base del laboratorio |
| Docker | 29.3.1 + Compose v5.1.1 | solo portabilidad |
| Ollama | instalado | opcional, nunca en resultados oficiales |

La instalación de PostgreSQL ya existía y da servicio a otras bases del autor
(`mgrid`, `portal_bcrd`, `visitordb`, `vmgrid`…). El laboratorio ha creado
**únicamente** la base `mecanico_ai_exp` y ha habilitado en ella `vector` y
`pg_trgm`. Ninguna otra base ha sido consultada, alterada ni eliminada.

Colab no interviene. Docker no es el entorno principal. Ollama no es el modelo
oficial de experimentación.

## 4. Clasificación de componentes

Etiquetas: **NEW** (a escribir aquí), **REUSE** (se copia desde el proyecto de
ingeniería con adaptaciones mínimas), **ADAPT** (existe algo cercano pero hay que
rehacerlo para el propósito experimental), **OPTIONAL** (útil, no crítico),
**FUTURE** (fuera del alcance del TFM).

La reutilización se hace **por copia y con procedencia documentada**. El
laboratorio no importa el otro proyecto, no depende de rutas hacia él y no lo
modifica. Antes de copiar cualquier fichero se registra en
`docs/experiments/` qué se copió y por qué.

### 4.1 Datos y señales

| Componente | Clase | Justificación |
|---|---|---|
| Catálogo de señales OBD-II con unidades y rangos | REUSE | Existe un catálogo de señales consolidado; el trabajo de definir PIDs, unidades y validación ya está hecho y no aporta nada rehacerlo |
| Generador sintético con relaciones físicas | ADAPT | Existe un emulador orientado a alimentar un sistema en marcha; aquí hace falta un generador orientado a control experimental, con semilla por escenario y verdad de referencia explícita |
| Inyección de fallos | ADAPT | Existen escenarios de fallo (fuga de vacío, deriva de MAF, fallo de encendido, retardo de sonda lambda, termostato bloqueado); hay que reexpresarlos con `fault_id`, señales afectadas, patrón temporal y observación esperada |
| Ingesta de OBD-II real | NEW | Depende de la fuente de datos reales que se decida en E3 |
| Metadata de dataset (`dataset_id`, tipo, fuente, versión, tasa de muestreo) | NEW | El registro de procedencia es requisito del experimento, no del producto |
| Particionado sin fuga temporal | NEW | Es el punto donde un error invalida todo lo demás; se escribe aquí con su test |

### 4.2 Modelo especializado y atribución

| Componente | Clase | Justificación |
|---|---|---|
| Ventanado y dataset de secuencias | REUSE | Existe una implementación de conjunto de secuencias reutilizable |
| Extracción de descriptores temporales | REUSE | Existe un extractor de descriptores sobre ventanas |
| Baseline tabular | NEW | Un bosque aleatorio sobre descriptores; trivial de escribir y conviene que sea de aquí |
| Modelo temporal | NEW | Se elige **uno** (GRU, LSTM o CNN-1D) en E7 y se justifica; no se implementan los tres |
| Evaluación y calibración | ADAPT | Existe protocolo de evaluación; hay que añadir calibración, que aquí es requisito porque la confianza entra en el criterio de suficiencia |
| Ejecución de SHAP | REUSE | Existe un ejecutor de SHAP con reglas ya fijadas: función explicada declarada, explainer agnóstico, fondo tomado solo de entrenamiento. Esas reglas son exactamente las que este laboratorio necesita |
| Localización temporal de la atribución | ADAPT | Existe una parte; hay que asegurar que la salida identifica ventana y dirección de contribución |
| Registro de experimentos y modelos | REUSE | Existe registro de experimentos y de modelos entrenados |
| Exportación a ONNX | FUTURE | Sirve al despliegue, no al experimento |

### 4.3 RAG y persistencia

| Componente | Clase | Justificación |
|---|---|---|
| Corpus documental con procedencia | REUSE | Existe un corpus con fuentes propias y externas y un fichero de procedencia. Es material sustancial y ya trazado |
| Troceado conservando fuente, sección y página | ADAPT | Existe troceado; hay que garantizar que la procedencia sobrevive intacta, que es lo que la PI exige |
| Recuperación léxica | REUSE | Existe un recuperador léxico determinista, útil como baseline y para CI sin red |
| Recuperación densa con pgvector | NEW | El recuperador existente es léxico. La recuperación densa sobre pgvector se escribe aquí |
| Esquema de documentos, fragmentos, embeddings y ejecuciones | NEW | Se diseña para el experimento: cada recuperación queda registrada con sus puntuaciones |
| Migraciones | NEW | Alembic, ya inicializado en E1 |
| Variantes controladas del corpus | REUSE | Existe el mecanismo de excluir documentos explícitamente para construir corpus con evidencia completa, parcial o ausente. Es justamente el instrumento del experimento central |
| Conjunto de referencia para evaluar recuperación | NEW | Hay que anotarlo |

### 4.4 Agente, evidencia y abstención

| Componente | Clase | Justificación |
|---|---|---|
| Abstracción de proveedores LLM | ADAPT | Existe una interfaz enchufable con implementación local y una determinista; hay que ampliarla a proveedores remotos por API y registrar los parámetros de cada llamada |
| Proveedor determinista sin red | REUSE | Imprescindible para tests y CI |
| Proveedor Ollama | OPTIONAL | Solo portabilidad |
| Salida estructurada con Pydantic | NEW | Contrato `EXPLAIN` / `ABSTAIN` con afirmaciones y sus referencias |
| Descomposición en afirmaciones y verificación de soporte | REUSE | Existe un módulo que descompone una explicación en afirmaciones atómicas, comprueba que cada referencia existe, resuelve y sostiene lo afirmado, y decide sobre la suficiencia. Es determinista y no usa modelo de lenguaje. Es el componente más valioso a reutilizar |
| Criterio de suficiencia calibrado | ADAPT | La política existe; los umbrales hay que calibrarlos aquí, solo con validación |
| Detección de contradicciones | NEW | |
| Manejo de distractores | NEW | La condición DISTRACTOR es propia de este diseño |

### 4.5 Evaluación y salida

| Componente | Clase | Justificación |
|---|---|---|
| Métricas M1-M6 | ADAPT | Hay métricas de diagnóstico y de trazabilidad; faltan las de abstención y las de recuperación |
| Matriz de abstención | NEW | |
| Conjunto de casos de referencia | NEW | Anotación manual, con acción esperada por caso |
| Juez basado en LLM | OPTIONAL | Solo como apoyo, nunca como único instrumento |
| Exportación a JSON y CSV | NEW | |
| Figuras para la memoria | NEW | |

### 4.6 Explícitamente fuera

Descubrimiento autónomo de fallos, memoria evolutiva de casos, aprendizaje
continuo, promoción automática de hipótesis, agente científico autónomo, API de
servicio, aplicación móvil, despliegue en hardware embarcado, sincronización
nube-borde. Todo ello es **FUTURE**.

## 5. Fases

Cada fase se cierra con sus gates en verde (`ruff`, `mypy`, `pytest`) y un
informe en `docs/experiments/`. No se avanza de fase sin aprobación explícita.

### E1 — Entorno · **cerrada**

- **Objetivo:** dejar la máquina y el repositorio en un estado verificable.
- **Entradas:** ninguna.
- **Salidas:** estructura del repositorio, `pyproject.toml` y `uv.lock`,
  configuración tipada por entorno, auditoría del entorno, base de datos
  `mecanico_ai_exp` con `vector` 0.8.0, Alembic operativo, notebooks con su
  estructura documental, este plan.
- **Tests:** `test_paths`, `test_settings`, `test_environment` (16 casos).
- **Aceptación:** `uv run mecanico-exp doctor` en verde en las cinco
  comprobaciones; `ruff`, `mypy --strict` y `pytest` sin fallos; notebook 00
  ejecutado de principio a fin.
- **Artefactos:** `notebooks/00_environment_check.ipynb`,
  `docs/experiments/E1_entorno.md`.

### E2 — Datos sintéticos

- **Objetivo:** generador reproducible de OBD-II plausible, con relaciones entre
  variables (acelerador↔RPM, RPM↔MAF, MAP↔carga, temperatura↔tiempo,
  ajustes de combustible↔mezcla, velocidad↔RPM), ruido, transitorios, deriva y
  regímenes (ralentí, urbano, carretera, aceleración, deceleración, calentamiento).
- **Salidas:** datasets sintéticos con metadata y verdad de referencia por evento.
- **Tests:** determinismo por semilla; las relaciones declaradas se observan en
  los datos generados.
- **Aceptación:** dos ejecuciones con la misma semilla producen ficheros
  idénticos; las correlaciones esperadas aparecen en el rango declarado.

### E3 — Ingesta de datos reales

- **Objetivo:** incorporar OBD-II real y normalizarlo al catálogo de señales.
- **Decisión abierta:** la fuente concreta (registros propios, conjunto público).
  Se resuelve al inicio de la fase y se documenta.
- **Tests:** normalización de unidades; ningún registro pierde procedencia.
- **Aceptación:** un dataset real cargado, descrito y comparable con el sintético.

### E4 — Análisis exploratorio temporal

- **Objetivo:** caracterizar las señales y decidir qué es utilizable.
- **Salidas:** figuras, y una lista razonada de señales admitidas.
- **Aceptación:** cada figura responde a una pregunta escrita; ninguna se incluye
  por decorado.

### E5 — Preprocesamiento y particionado

- **Objetivo:** ventanado, descriptores y particiones sin fuga temporal.
- **Ventanas candidatas:** 10 s, 30 s, 60 s, 120 s; la elección se justifica con
  evidencia de E4, no por costumbre.
- **Separación:** por vehículo, trayecto, sesión, episodio o evento, según lo que
  los datos permitan. Nunca partición aleatoria de ventanas consecutivas.
- **Tests:** `test_timeseries_windowing`, `test_no_temporal_leakage`.
- **Aceptación:** el test de fuga demuestra que ninguna ventana de test comparte
  origen con una de entrenamiento; las semillas quedan registradas.

### E6 — Baseline

- **Objetivo:** bosque aleatorio sobre descriptores, como referencia inferior.
- **Aceptación:** supera la clase mayoritaria de forma clara en validación.

### E7 — Modelo temporal

- **Objetivo:** un único modelo secuencial, entrenado en MPS.
- **Aceptación:** entrena de forma reproducible; se justifica por escrito la
  elección de arquitectura y se registra el dispositivo empleado.

### E8 — Evaluación del modelo

- **Objetivo:** rendimiento y calibración sobre test aislado.
- **Métricas:** las pertinentes al problema; la calibración es obligatoria
  porque la confianza alimenta el criterio de suficiencia.
- **Tests:** `test_model_prediction_schema`.

### E9 — Atribución

- **Objetivo:** para cada caso, señales relevantes, contribución, ventana y
  dirección.
- **Tests:** `test_xai_output_schema`.
- **Aceptación:** la salida identifica siempre la función explicada; ningún
  artefacto presenta la atribución como causa.

### E10 — Corpus documental

- **Objetivo:** corpus troceado con fuente, sección y página intactas.
- **Tests:** `test_rag_provenance`.
- **Aceptación:** para cualquier fragmento se puede recuperar su documento,
  sección y página de origen.

### E11 — pgvector

- **Objetivo:** esquema de documentos, fragmentos, embeddings, fuentes,
  ejecuciones de recuperación, resultados y citaciones; indexación e inserción.
- **Tests:** `test_retrieval_metadata`.
- **Aceptación:** `alembic upgrade head` sobre una base vacía deja el esquema
  completo; una recuperación queda registrada con sus puntuaciones.

### E12 — Evaluación de la recuperación

- **Objetivo:** conjunto de referencia anotado y medición.
- **Aceptación:** se reporta la calidad de la recuperación por condición de
  corpus, no solo en agregado.

### E13 — Integración del agente

- **Objetivo:** composición del prompt y salida estructurada validada.
- **Entradas al LLM:** diagnóstico, confianza, evidencia observacional,
  atribución, fragmentos recuperados con sus puntuaciones y la decisión de
  suficiencia.
- **Tests:** `test_no_fake_citations`.
- **Aceptación:** ninguna salida contiene una referencia que no resuelva.

### E14 — Trazabilidad de afirmaciones

- **Objetivo:** cada afirmación con sus identificadores de observación y de
  fragmento, y su estado de soporte.
- **Tests:** `test_claim_evidence_mapping`.
- **Aceptación:** desde una afirmación cualquiera se reconstruye su traza
  completa; se exporta en JSON y CSV.

### E15 — Suficiencia de evidencia

- **Objetivo:** componente determinista, fuera del LLM, que decide si la
  evidencia sostiene una explicación.
- **Señales consideradas:** confianza del modelo, calibración, puntuación de
  recuperación, relevancia documental, número de fragmentos de apoyo, número de
  fuentes distintas, cobertura de afirmaciones y presencia de contradicciones.
- **Tests:** `test_supported_evidence`, `test_insufficient_evidence`.
- **Aceptación:** los umbrales se calibran **solo** con validación; el conjunto
  de test no se toca hasta E19.

### E16 — Abstención

- **Objetivo:** producir la abstención como salida válida y evaluarla.
- **Tests:** `test_abstention`.
- **Aceptación:** la matriz de abstención se puede construir; se distingue
  abstención correcta de abstención injustificada.

### E17 — Condiciones de disponibilidad de evidencia

- **Objetivo:** ejecutar el pipeline bajo cuatro condiciones sobre los mismos
  casos.

  | Condición | Corpus | Comportamiento esperado |
  |---|---|---|
  | FULL | evidencia correcta presente | EXPLAIN con traza completa |
  | PARTIAL | evidencia incompleta | ABSTAIN, salvo que el criterio admita una explicación limitada declarada como tal |
  | ABSENT | evidencia retirada | ABSTAIN |
  | DISTRACTOR | evidencia parecida pero incorrecta | rechazo del distractor; ABSTAIN si no queda otra evidencia suficiente |

- **Tests:** `test_distractor_handling`.
- **Aceptación:** la única diferencia entre condiciones es el corpus; datos,
  modelo, semillas y prompt son idénticos.

### E18 — Ablaciones

- **Objetivo:** aislar la contribución de cada pieza (sin atribución, sin
  recuperación densa, sin criterio de suficiencia, con un solo umbral).
- **Aceptación:** cada ablación cambia exactamente un factor.

### E19 — Evaluación final

- **Objetivo:** métricas M1-M6 sobre test, contraste con los criterios de
  refutación y veredicto sobre la PI.
- **Aceptación:** el veredicto se emite contra criterios escritos **antes** de
  mirar los resultados, y admite las tres salidas: sostenida, parcialmente
  sostenida, no sostenida.

### E20 — Demostración

- **Objetivo:** el caso real doble —con y sin evidencia relevante— y la ejecución
  completa de extremo a extremo.
- **Aceptación:** el contraste entre explicación trazable y abstención se ve sin
  necesidad de explicarlo.

## 6. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| No conseguir OBD-II real suficiente o con fallos etiquetados | Alto: la PI se formula sobre datos reales | Resolver la fuente en E3, antes de invertir en E5-E9; si el dato real es escaso, reservarlo íntegro para validación y demostración |
| Fuga temporal no detectada | Alto: invalida todo lo posterior | Test explícito en E5, partición por origen, revisión antes de E6 |
| Umbrales de suficiencia ajustados sobre test | Alto: el resultado dejaría de ser evidencia | Test aislado hasta E19; la calibración solo ve validación |
| Que la abstención resulte trivial (el sistema se abstiene casi siempre) | Medio: el resultado sería vacío | Reportar cobertura junto a corrección; la condición FULL debe producir explicaciones |
| Deriva de alcance hacia el sistema de producción | Medio | La sección 2 delimita; lo que no está en las fases no se hace |
| Coste o indisponibilidad del proveedor LLM | Bajo | Abstracción de proveedor y proveedor determinista para CI |

## 7. Decisiones abiertas

1. **Fuente de datos OBD-II reales** (E3): pendiente.
2. **Arquitectura del modelo temporal** (E7): GRU, LSTM o CNN-1D; se elige una.
3. **Proveedor LLM oficial** (E13): pendiente; el pipeline no depende de cuál sea.
4. **Modelo de embeddings y dimensión** (E11): condiciona el esquema de pgvector.
5. **Conjunto de fallos definitivo** (E2): los cinco heredados del proyecto de
   ingeniería son candidatos, no una decisión tomada. Se confirmará cuáles son
   sostenibles con los datos realmente disponibles.

## 8. Estado

E1 cerrada el 1 de septiembre de 2026. E2 pendiente de aprobación.
