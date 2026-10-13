# Auditoría de portabilidad de los notebooks

**Fecha:** 12 de octubre de 2026 · **Pregunta que responde:** ¿qué puede ejecutar de verdad alguien
que clone este repositorio y no tenga mi equipo?

Todo lo que sigue está **comprobado ejecutando**, no supuesto.

## 1. Lo que ya existía

Diecisiete notebooks en `notebooks/`, uno por fase. La buena noticia es que su **portabilidad ya es
correcta**: ninguno contiene una ruta absoluta, ninguno trae credenciales, todos anclan la raíz con
`Path.cwd().parent if Path.cwd().name == "notebooks"` y todos importan del paquete en lugar de
duplicar lógica.

La mala es que **son plantillas, no entregables**. El recuento:

| Notebook | Celdas | Código / Markdown | Caracteres de código |
|---|---|---|---|
| `00_environment_check` | 8 | 4 / 4 | 624 |
| `01_synthetic_obd_generation` | 9 | 4 / 5 | 1 272 |
| `02_real_obd_ingestion` | 5 | 2 / 3 | **325, vacío** |
| `03_timeseries_eda` | 9 | 4 / 5 | 702 |
| `04_preprocessing_features` | 9 | 4 / 5 | 1 145 |
| `05_model_training` | 6 | 2 / 4 | 845 |
| `06_model_evaluation` | 8 | 4 / 4 | 647 |
| `07_xai` | 9 | 4 / 5 | 992 |
| `08_rag_corpus` | 9 | 4 / 5 | 1 519 |
| `09_retrieval_evaluation` | 8 | 3 / 5 | 595 |
| `10_llm_agent` | 8 | 5 / 3 | 2 158 |
| `11_evidence_sufficiency` | 8 | 4 / 4 | 1 027 |
| `12_abstention` | 8 | 3 / 5 | 1 254 |
| `13_integrated_experiment` | 5 | 2 / 3 | **325, vacío** |
| `14_final_evaluation` | 5 | 2 / 3 | **325, vacío** |
| `15_tfm_demo` | 8 | 4 / 4 | 1 333 |
| `TFM_EXPERIMENTO_COMPLETO` | 5 | 2 / 3 | **325, vacío** |

Cuatro están literalmente vacíos: su única celda de código dice
`# Implementación en la fase indicada en la cabecera.` Y los trece restantes conservan sin rellenar
las secciones de la plantilla —«_Lo observado, sin interpretación._», «_Qué significa, y qué no
significa._»—, de modo que **ninguno cumple hoy los quince contenidos obligatorios**.

Decisión: **no se duplican ni se tiran.** Los que se reescriben en esta entrega conservan su número y
su fase; los demás quedan como están, marcados en el índice con lo que les falta.

## 2. Lo que un clon del repositorio sí trae

Esto es lo que decide qué puede ejecutarse sin mi equipo. Comprobado con `git ls-files`:

| Qué | Cuánto | Sirve para |
|---|---|---|
| `experiments/*.json` | **48 registros** | toda cifra publicada; E19 incluida |
| `artifacts/tables/*.csv` | **25 tablas** | resultados por clase, matrices de confusión, atribuciones |
| `artifacts/figures/*.png` | **12 figuras** | las figuras publicadas de E4, E5, E6, E7 |
| `artifacts/metrics/*.json` | 2 | resumen de ablaciones, comparación de RERUN-A |
| `data/samples/synthetic_sample.parquet` | **18 sesiones, 10 800 muestras** | exploración y series temporales |
| `configs/*.{json,yaml}` | 8 | calibración, conjunto anotado, manifiestos de congelación |
| `src/`, `tests/` | 78 + 33 | el código, ejecutable |

**`artifacts/` es la copia versionada de `tables/` y `figures/`**, que están fuera del control de
versiones. Los notebooks leen de `artifacts/`, no de `tables/`: es la única de las dos que el jurado
tiene.

## 3. Lo que un clon NO trae, y qué se hace con cada cosa

| Qué falta | Por qué | Qué se hace |
|---|---|---|
| `data/raw/synthetic/*.parquet` | `data/raw/**` está en `.gitignore`; `synthetic_v2` son 43 200 muestras y `v3`, 129 600 | **el generador las reconstruye**: es determinista y bit a bit reproducible desde su semilla. Comprobado: `synthetic_sample` regenerado desde `build_balanced_specs(seed=20260901, sessions_per_fault=3)` sale **idéntico bit a bit** en las doce señales |
| `data/processed/*.npy` | mismo motivo | el modo FULL las regenera con `preprocess`; el modo DEMO no las necesita |
| PostgreSQL 14 + pgvector | servicio externo | **los notebooks de recuperación y suficiencia no son DEMO.** Leen sus resultados de `experiments/` y `artifacts/`, y declaran qué haría falta para reejecutarlos |
| `models/slm_lora_v2` | pesos del adaptador, no versionados | igual: el notebook del agente lee el registro de E13, no carga el modelo |
| Corpus documental del manual | documento propiedad del fabricante | no se redistribuye, y así está declarado desde E10 |
| GPU o Apple Silicon | el jurado puede tener cualquier cosa | **DEMO funciona en CPU.** El único notebook que entrena, el de comparación, lo hace con el bosque (segundos en CPU) y **lee** las cifras de la red de su registro |

## 4. El hallazgo que resuelve la portabilidad del dato

**No hace falta redistribuir los conjuntos.** El generador es determinista por semilla y su
reproducibilidad está comprobada en dos sentidos:

1. `synthetic_sample.parquet`, que **sí** está versionado, se regenera idéntico bit a bit desde su
   especificación;
2 .el manifiesto de procedencia (`obd/procedencia.py`) permite regenerar **cualquier sesión** desde
   su ficha, y hay un test que lo comprueba para las doce sesiones de un conjunto de prueba.

De modo que un notebook DEMO puede **generar su propio dato en segundos** y obtener exactamente el
mismo que produjo las cifras publicadas, en lugar de pedir un fichero que no está. Lo que no puede
regenerar son los conjuntos grandes en tiempo de notebook —`synthetic_v2` tarda del orden de un
minuto; `v3`, tres— y por eso el modo DEMO usa la muestra de 18 sesiones y el modo FULL documenta el
comando.

## 5. Dependencias externas, por notebook

| Notebook | Necesita | Modo |
|---|---|---|
| introducción, exploración, series, generación | nada más que `nb` | **DEMO** |
| comparación de modelos | `ml` (scikit-learn; torch **no**, la red se lee de su registro) | **DEMO** |
| análisis de E19 | nada más que `nb` | **DEMO** |
| preprocesado, atribución | `ml`, y regenerar el conjunto | FULL |
| corpus, recuperación, suficiencia, abstención, ablaciones | PostgreSQL + pgvector + `embeddings` + corpus | FULL |
| agente, incorporación de conocimiento | lo anterior + `slm` + pesos del adaptador | FULL |

## 6. Limitaciones de portabilidad que no se pueden resolver

Se declaran en lugar de disimularse:

1. **El corpus documental no se redistribuye.** Es el manual de taller de un fabricante. Todo lo que
   dependa de él es FULL y no reproducible por un tercero sin el documento. Esto ya era una
   limitación declarada del trabajo, no una del notebook.
2. **Los pesos del adaptador LoRA no se versionan.** Son del orden de decenas de megabytes y no
   caben en el repositorio con sentido. El registro de su ajuste sí está.
3. **MPS no es bit a bit determinista** en algunas reducciones. La semilla acota la variación y no la
   elimina, y así consta desde E7: una reejecución del modelo temporal puede dar cifras ligeramente
   distintas. Por eso el notebook de comparación **no reentrena la red**: leería un número distinto
   del publicado y parecería una contradicción.
4. **Los cinco registros de E6, E7 y E9 no tienen cabecera de identificación** —ni `commit`, ni
   `executed_at`—. Son anteriores a la convención y no se regeneran, porque regenerar cambiaría las
   cifras publicadas. Los notebooks que los citan lo declaran.

## 7. Qué se entrega en esta primera tanda

| # | Entregable | Estado |
|---|---|---|
| 1 | Esta auditoría | hecho |
| 2 | Índice de notebooks (`docs/notebooks/indice.md`) | hecho |
| 3 | Entorno reproducible (`uv`, extra `nb`, instrucciones) | hecho |
| 4 | `00_introduccion.ipynb` | hecho |
| 5 | `01_exploracion_obd.ipynb` | hecho |
| 6 | `02_comparacion_modelos.ipynb` | hecho |
| 7 | `03_analisis_e19.ipynb` | hecho |
| 8 | Validación automática (`tests/test_notebooks.py`) | hecho |

Los demás se incorporan conforme se cierren sus experimentos, y el índice dice cuáles y por qué.
