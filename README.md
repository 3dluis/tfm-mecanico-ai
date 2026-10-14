# Trabajo práctico del TFM · paquete de entrega

Este directorio **es** el trabajo práctico del Trabajo Fin de Máster en Inteligencia Artificial
(UAX, Luis Daniel Díaz, 2026), empaquetado para que se pueda leer, ejecutar y verificar sin
depender de ningún otro repositorio ni de la máquina en que se construyó.

> **Estado: BORRADOR PARA REVISIÓN DEL TUTOR.** No es la entrega definitiva. Quedan decisiones
> abiertas sobre la extensión, el título y los datos institucionales de la portada.

## Qué hay aquí

| Dónde | Qué es |
|---|---|
| `memoria/` | la memoria académica, en `.docx` editable y en `.pdf` |
| `notebooks/` | los siete notebooks científicos, uno por bloque experimental |
| `notebooks/html/` | **los mismos notebooks ya ejecutados**, con sus figuras dentro: se abren en un navegador sin instalar nada |
| `src/mecanico_ia_exp/` | el código: generador de señales, modelos, recuperación, verificador de suficiencia y las funciones de visualización |
| `artifacts/` | las tablas, las métricas, las figuras del documento y el análisis contrafactual |
| `experiments/` | el registro JSON de cada ejecución, con su commit, su semilla y sus métricas |
| `data/` | la muestra redistribuible y los conjuntos sintéticos que sí pueden viajar |
| `configs/` | la configuración, los manifiestos y el censo de artefactos históricos |
| `docs/` | la documentación del laboratorio: metodología, decisiones, auditorías y limitaciones |
| `scripts/` | instalación, ejecución y verificación del paquete |
| `tests/` | las pruebas que sostienen lo anterior |
| `.git/` | **el historial completo**, 424 commits desde el 1 de septiembre de 2026 |

## Por dónde empezar, según lo que se quiera hacer

**Leer sin instalar nada.** `memoria/memoria.pdf` y, para ver la evidencia, los HTML de
`notebooks/html/`. No hacen falta Python ni Jupyter: se abren en cualquier navegador y traen
dentro sus figuras y sus tablas.

**Revisar en quince minutos.** [`JURY_GUIDE.md`](JURY_GUIDE.md).

**Ejecutar los notebooks.**

```bash
bash scripts/instalar.sh            # necesita internet UNA vez, para las dependencias
bash scripts/ejecutar_notebooks.sh  # a partir de aquí, sin red
```

**Comprobar que el paquete está completo.**

```bash
uv run python scripts/verificar_entrega.py
```

Recorre nueve familias —ficheros, dependencias, notebooks, figuras, métricas, datos,
documentación, huellas y Git— y termina con código distinto de cero si algo falta. Las huellas
que compara están en `MANIFEST.json`, que se regenera con `scripts/generar_manifiesto.py`.

## Qué se puede reproducir y qué no

**Se reproduce.** Todas las figuras del documento se regeneran desde los registros congelados
con `uv run python scripts/figuras_memoria.py`. El conjunto canónico `synthetic_v2` se
reconstruye **bit a bit** desde su plan y su semilla, y hay una medición que lo comprueba sesión
a sesión. Los siete notebooks se ejecutan en CPU, sin red y sin servicios externos.

**No se reproduce, y está dicho dónde.** Dos conjuntos, `synthetic_v1` y `synthetic_v3`, son
anteriores a la calibración del generador contra el manual de taller: el generador publicado
produce **otras señales**, de modo que no se pueden reconstruir y no se intenta. Dos figuras son
artefactos históricos cuya rutina ya no existe o cuyos datos intermedios no se guardaron; viajan
con su huella y con el motivo. El anexo C de la memoria lo detalla.

**No viaja, y por qué.** El manual de taller del fabricante tiene una licencia que no permite
redistribuirlo, y con él no viajan el índice documental ni los embeddings, que se construyen de
él. Los adaptadores del modelo de lenguaje pesan 28 MB cada uno y derivan de un modelo base con
licencia propia: viaja su configuración, que es lo que hace auditable el ajuste. `MANIFEST.json`
enumera cada exclusión con su motivo.

## Las dos modalidades

**DEMO** es lo que este paquete entrega entero: CPU, sin GPU, sin PostgreSQL, sin credenciales y
sin red durante la ejecución. Permite explorar las señales, regenerar las figuras, consultar las
métricas y las atribuciones, analizar la evaluación final y leer los resultados negativos.

**FULL** reejecuta las fases que dependen de los recursos de arriba. **No es autónoma**: exige
el manual, el índice vectorial y, para el ajuste del redactor, una GPU. Donde una prueba o un
notebook necesita algo que no está, **se detiene diciendo qué falta y cómo obtenerlo**, en lugar
de saltarse el paso en silencio.

## El historial

El repositorio conserva el historial real del trabajo: **424 commits** entre el 1 de septiembre
y el 14 de octubre de 2026, en dieciséis ramas, con sus fechas y su autoría originales. Se
construyó **por clonación**, sin reescribir nada, de modo que los identificadores de commit son
los mismos que los del repositorio de trabajo y cualquier referencia de la documentación a un
commit sigue resolviendo.

```bash
git log --oneline --graph --all | head -40      # la evolución
git log --format='%h %ad %s' --date=short       # con fechas
git show <commit>                               # un cambio concreto
git fsck --full                                 # integridad de los objetos
```

Incluye lo que salió mal: la interrupción de la evaluación final y sus tres intentos, la
contaminación del adaptador, la retirada de una conclusión sobre el volumen de datos y las
correcciones de la memoria, cada una con su commit.

## Verificar una huella

```bash
shasum -a 256 memoria/memoria.pdf
uv run python -c "import json;print(json.load(open('MANIFEST.json'))['huellas_sha256']['memoria/memoria.pdf'])"
```

---

# Mecánico IA: repositorio experimental del TFM

Artefacto experimental del Trabajo Fin de Máster en Inteligencia Artificial (UAX, Luis Daniel
Díaz, 2026). Contiene el código, los registros de ejecución, las decisiones y las auditorías
con los que se construyó la evidencia de la memoria. No es un producto: es el laboratorio, con
su historial completo, incluidos los resultados que no salieron como se esperaba.

## 1. Qué se investiga

Cuando un sistema de diagnóstico de vehículos explica una avería a partir de telemetría OBD-II,
la explicación suele evaluarse por si el diagnóstico final es correcto. Este trabajo estudia
otra propiedad: si **cada afirmación de la explicación puede seguirse hasta la evidencia que la
sostiene** (una observación de la telemetría o un fragmento identificable del manual de taller)
y si el sistema es capaz de **abstenerse** cuando esa evidencia no basta, en lugar de producir
una hipótesis sin fundamento.

## 2. Pregunta de investigación

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis
> sin fundamento?

Enunciada en `docs/memoria/cap1_introduccion.md`; fijada como canónica por
`research/decisions/ADR-004-pregunta-de-investigacion-canonica.md` tras dos revisiones
documentadas (ADR-003 retiró el requisito de datos reales; ADR-004 descartó una formulación
más amplia). Se descompone en cuatro subpreguntas (PI.1 diagnóstico y calibración, PI.2
recuperación y trazabilidad, PI.3 abstención con evidencia insuficiente, PI.4 rechazo de
evidencia parecida pero no aplicable), cada una con su hipótesis y su criterio de refutación
en `docs/memoria/cap4_marco_metodologico.md` (Tabla 4.6).

## 3. El vacío que se aborda

Según la revisión del capítulo 3 (`docs/memoria/cap3_marco_teorico.md`), y solo entre los
trabajos revisados: los sistemas de diagnóstico sobre OBD-II clasifican, detectan y atribuyen,
y ahí terminan; los sistemas de recuperación sobre documentación técnica anclan la respuesta
en documentos, pero miden si la respuesta final es correcta, no si cada afirmación puede
seguirse hasta el fragmento que la sostiene; y la abstención se trata como una disposición del
modelo de lenguaje, no como una propiedad de la evidencia disponible. Este trabajo sitúa la
decisión de explicar o abstenerse fuera del modelo de lenguaje, en un verificador determinista
que examina la evidencia. La revisión no es un flujo PRISMA formal (L-08) y tres trabajos no se
leyeron a texto completo (L-09): el vacío se afirma con ese alcance.

## 4. Arquitectura experimental

```
telemetría OBD-II sintética, calibrada contra el manual del vehículo    (E2)
  → ventanas de 120 s y 139 descriptores, reparto por sesión              (E5)
  → modelo de diagnóstico con confianza calibrada                         (E6 bosque · E7 GRU)
  → atribución SHAP: evidencia observacional                              (E9)
  → recuperación sobre el manual de taller, filtrada por vehículo y motor (E11 · E12)
  → verificador determinista de suficiencia → EXPLAIN / ABSTAIN           (E15 · E15b umbral)
  → redactor SLM (Qwen2.5-3B + LoRA) con citas comprobadas contra el índice (E13)
```

El modelo de lenguaje no diagnostica ni decide: redacta la evidencia que los componentes
anteriores produjeron, y cada cita se comprueba contra el índice. El conjunto de test está
cerrado por excepción en el código y nunca se abrió: todas las cifras son de validación (L-17).
Vehículo de referencia: Mazda 3 BK 2007, motor Z6 (`docs/memoria/cap4_marco_metodologico.md`,
Tabla 4.1). Detalle de fases, políticas y pre-registros: `docs/methodology/`.

## 5. Experimentos más importantes

| Exp. | Qué responde | Dónde está el registro |
|---|---|---|
| E6 | Línea base de diagnóstico y calibración de la confianza | `experiments/E6_baseline_synthetic_v2.json` |
| E7 | Si un modelo temporal aporta algo sobre la línea base | `experiments/E7_temporal_synthetic_v{2,3}.json` |
| E12 | Cuánto aporta filtrar la recuperación por vehículo, motor y autoridad | `experiments/E12_retrieval.json` |
| E15 | Si el verificador decide EXPLAIN/ABSTAIN correctamente bajo cuatro condiciones de evidencia | `experiments/E15_suficiencia*.json` |
| E15b | Qué umbral de confianza es estable | `experiments/E15b_barrido_umbral.json` |
| E13 | Si el redactor produce explicaciones válidas, respeta el veredicto y no inventa citas | `experiments/E13_agente_*.json` |
| RERUN-A | Si un defecto metodológico descubierto el 4-09 (`MIXED-EMBEDDING-SPACE`) alteraba los resultados de recuperación | `docs/experiments/resultado-rerun-a.md` |

Índice completo con estado de cada experimento (VALIDATED, NEGATIVE, INCONCLUSIVE,
SUPERSEDED, NON-CANONICAL, PLANNED): [`docs/experiment-index.md`](docs/experiment-index.md).

## 6. Qué se encontró

Cifras de validación sobre datos sintéticos de un solo vehículo. Cada una procede del registro
indicado; la lectura prudente es la del capítulo 5 de la memoria.

- **Diagnóstico (PI.1).** El bosque aleatorio alcanza macro-F1 0,879 frente a 0,074 de la clase
  mayoritaria, con una confianza mal calibrada (ECE 0,144; 0,085 tras calibración isotónica).
  El modelo temporal GRU **no lo supera** en `synthetic_v2` (0,823) y lo supera por 0,0125 en
  `synthetic_v3`, un margen que el propio informe declara inconcluso.
- **Recuperación (PI.2).** La similitud semántica sin filtros no recupera el procedimiento
  relevante en ningún caso (hit-rate 0,00); guiada por el diagnóstico y filtrada por motor y
  autoridad lo recupera en los cinco casos puntuables (hit-rate 1,00, MRR 0,467). Seis casos
  anotados; uno excluido de la métrica por no tener fichero relevante.
- **Suficiencia y abstención (PI.3).** El verificador determinista v2.1 decide correctamente
  15 de 17 casos; abstiene en los 3/3 con evidencia retirada y en los 3/3 con evidencia parcial;
  falla en dos casos con evidencia completa. El resultado es idéntico sin canales de oráculo.
  En un escenario adverso con seis ventanas mal clasificadas por el modelo, abstiene en las seis,
  pero el análisis reveló una puerta de comprobación que se omitía en silencio.
- **Distractores (PI.4).** Con el filtro de motor activo, la condición «distractor» resulta
  redundante con la condición parcial en dos de los tres fallos: recupera los mismos fragmentos.
  La subpregunta queda bajo diagnóstico, y la novedad que se reclamaba sobre ella es más
  estrecha (L-10).
- **Redactor (E13).** Con el adaptador LoRA, 9 de 9 explicaciones válidas, 9 de 9 con el
  veredicto respetado y 0 citas inventadas; el modelo base produce 7 de 9 válidas. El ajuste
  corrigió el formato, no el diagnóstico.
- **RERUN-A.** Tras corregir la mezcla de espacios de embeddings, los conjuntos recuperados
  cambian en 10 de 17 casos y las decisiones no cambian en ninguno. Por el criterio fijado en el
  pre-registro, esto se lee como «sin efecto detectable con este instrumento», no como
  validación del verificador.

## 7. Qué no se pudo demostrar

- Nada sobre vehículos reales: la telemetría es sintética y la validación externa (E3) no se
  ejecutó (L-01, crítica).
- Que el modelo temporal aporte algo sobre la línea base (E7, negativo o inconcluso).
- Que la condición de distractor manipule una variable observable en los tres fallos
  (redundante en dos); por eso no hay inferencia confirmatoria sobre PI.4 y **ningún valor p**
  se publica (pre-registro de RERUN-A, ENM-S01/S02).
- Que el verificador sea correcto cuando el diagnóstico no lleva códigos de avería asociados:
  la puerta de códigos se omitía (`EMPTY-DTC-GATE-BYPASS`), la corrección v2.2 está
  implementada y **sin medir** (RERUN-B).
- Que el adaptador LoRA sea canónico: se entrenó sobre un conjunto generado con recuperación
  de procedencia indeterminada y no se ha reentrenado.
- Ninguna ablación (E18), ninguna evaluación final sobre test (E19).

Registro completo: [`docs/limitations.md`](docs/limitations.md) y
`research/limitations-register.md`. Hallazgos y correcciones documentadas:
`docs/experiments/hallazgo-*.md`.

## 8. Notebooks: leer la evidencia sin ejecutar nada

Cuatro notebooks documentan los experimentos cerrados como documentos científicos ejecutables.
Se pueden **leer sin instalar nada** —hay copia en HTML con sus figuras dentro— y ejecutar con un
clon del repositorio, sin GPU, sin base de datos y sin descargas.

| Notebook | Qué responde | Leer | Experimentos |
|---|---|---|---|
| `00_introduccion` | el recorrido completo y el estado de la evidencia | [HTML](notebooks/html/00_introduccion.html) | E1–E19 |
| `01_exploracion_obd` | si las señales OBD-II contienen estructura diagnóstica | [HTML](notebooks/html/01_exploracion_obd.html) | E2, E4, E5 |
| `02_comparacion_modelos` | si el modelo temporal supera a la línea base | [HTML](notebooks/html/02_comparacion_modelos.html) | E6, E7 |
| `03_analisis_e19` | si el criterio de suficiencia evita la falsa confianza | [HTML](notebooks/html/03_analisis_e19.html) | E19 |

```
uv sync --extra nb
uv run jupyter lab notebooks/
```

Cada notebook declara su **modalidad** —reproducción, reanálisis, visualización de evidencia
histórica o demostración ilustrativa—, porque no todos hacen lo mismo con la evidencia y
confundirlas sería grave. Índice y criterios: [`docs/notebooks/indice.md`](docs/notebooks/indice.md).
Qué notebook corresponde a cada resultado:
[`docs/notebook-traceability.md`](docs/notebook-traceability.md). Qué puede ejecutar de verdad quien
no tenga el equipo del autor: [`docs/notebooks/auditoria-portabilidad.md`](docs/notebooks/auditoria-portabilidad.md).

Ninguno escribe donde viven los artefactos históricos, y 104 comprobaciones de
`tests/test_notebooks.py` lo verifican, incluida la ejecución de los cuatro desde un kernel limpio.

## 9. Cómo reproducir

**Desde un clon limpio, en seis pasos**, comprobados clonando el repositorio y ejecutándolos:

```
uv sync --extra nb --extra ml
bash scripts/reconstruir_datos.sh    # reconstruye lo que no se distribuye, y COMPRUEBA sus huellas
uv run pytest                        # 902 pasan sin reconstruir; 919 tras reconstruir
uv run ruff check . && uv run mypy src
uv run jupyter lab notebooks/
```

`data/raw/**` y `data/processed/**` están fuera del control de versiones: `synthetic_v2` son 43 200
muestras. No hace falta distribuirlo porque el generador lo reconstruye **bit a bit**, y el guion
contrasta las cuatro huellas contra las que el manifiesto de E19 congeló antes de abrir el conjunto
de prueba. De `synthetic_v2` salen la línea base de diagnóstico, el modelo temporal y la evaluación
final. `synthetic_v3`, del que sale solo la comparación de volumen de E7, **no** se reconstruye y el
guion se niega: es anterior a la calibración del generador. Sin reconstruir, doce pruebas se detienen diciendo la orden exacta en lugar de fallar.

Detalle completo, con lo que **no** se puede reproducir y por qué:
[`docs/reproducir-desde-cero.md`](docs/reproducir-desde-cero.md).

Entorno verificado: macOS sobre Apple Silicon, `uv`, PostgreSQL 14+ con `pgvector`. El bloque
de telemetría (E2 → E9, E15b) se reproduce sin base de datos ni manual:

```
uv sync --all-extras
uv run mecanico-exp doctor --no-db
bash scripts/reproduce_baseline.sh          # E2 → E5 → E6 sobre synthetic_v2, y diff con el registro versionado
```

El bloque documental (E11 → E15, E13) requiere el manual de taller del vehículo, que **no se
redistribuye** desde este repositorio (`data/README.md` explica qué falta y cómo obtenerlo), y
PostgreSQL con pgvector:

```
bash scripts/init_db.sh
uv run python scripts/ingest_mazda.py multilingual
bash scripts/reproduce_main_results.sh      # E12, E15 oracular y no oracular, E13 con LoRA v2
```

Versiones exactas, semillas, comandos y riesgos: [`docs/reproducibility.md`](docs/reproducibility.md).
Secuencia completa de 17 comandos: `docs/EXPERIMENTO_PASO_A_PASO.md`. Gate de calidad:
`uv run ruff check . && uv run mypy src && uv run pytest`.

## Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `src/mecanico_ia_exp/` | Código científico: generador OBD-II, descriptores, modelos, XAI, RAG, verificador de suficiencia, agente SLM, un runner por experimento |
| `experiments/` | Registros JSON de cada ejecución; `pre_mixed_embedding_fix/` conserva los anteriores a la corrección del 4-09 |
| `artifacts/` | Figuras, tablas y métricas usadas en la memoria, con su procedencia (`artifacts/README.md`) |
| `docs/experiments/` | Un informe por fase, los hallazgos (`hallazgo-*.md`) y el resultado de RERUN-A |
| `docs/methodology/` | Políticas escritas antes de implementarse, criterios de umbral, pre-registros y enmiendas |
| `docs/memoria/` | Texto fuente de la memoria por capítulos |
| `docs/tfm/`, `docs/audits/` | Revisión integral, auditorías, plan de corrección e informes del tutor |
| `research/` | Decisiones (ADR-001…004), matriz de trazabilidad, registro de limitaciones, referencias |
| `configs/` | Calibración del generador, conjunto anotado, estado congelado de RERUN-A |
| `data/` | Muestra redistribuible en `data/samples/`; el resto se regenera (`data/README.md`) |
| `notebooks/` | Documentos científicos ejecutables; importan del paquete y no duplican lógica. Escritos desde `scripts/notebooks/` |
| `notebooks/salida/` | Donde escriben los notebooks. **Nunca** en `experiments/`, `tables/`, `figures/` ni `data/` |
| `notebooks/html/` | Copia en HTML de cada notebook, legible sin ejecutar nada |
| `tests/` | 400 pruebas: políticas de suficiencia, aislamiento de embeddings, contrato de RERUN-A, cierre del test |

## Trazabilidad

Pregunta (`cap1`) → subpreguntas e hipótesis (`research/traceability-matrix.md`) → objetivos
(`cap2`) → política escrita antes de medir (`docs/methodology/`) → ejecución con commit y
semilla (`experiments/*.json`) → tabla o figura (`artifacts/`) → sección del capítulo 5 →
conclusión (`cap6`). Matriz que lo recorre: [`docs/tfm-traceability.md`](docs/tfm-traceability.md).

El historial Git (170 commits del 1 al 13 de septiembre de 2026, más los de preparación para el
tribunal) es la cronología real del trabajo. El 13-09 se normalizaron 69 mensajes para retirar
metadatos automáticos de la herramienta de desarrollo; los SHA anteriores a esa fecha citados en
registros y documentos se resuelven con `docs/git-sha-mapping.md` o directamente contra la rama
de archivo `backup/pre-history-cleanup-20260913-1815`, que se conserva de forma permanente.

## Relación con la memoria del TFM

Este repositorio es el artefacto experimental asociado a la memoria. Ninguna cifra llega a la
memoria sin proceder de un registro de `experiments/`. Las discrepancias detectadas entre
documentos y registros, y cómo se resolvieron, están en `docs/experiment-index.md`
§Discrepancias.
