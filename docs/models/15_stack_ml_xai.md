# 15 — Stack tecnológico de ML, análisis y XAI (fuente canónica de versiones)

**Auditado el 2026-08-14 sobre el estado real del repositorio** (manifiestos, `uv.lock`,
imports por AST y configs de experimentos). **Este documento es la ÚNICA fuente canónica
de versiones**: el resto de la documentación referencia aquí en lugar de repetirlas, para
evitar divergencia. Inventario reproducible: `uv run python tools/dep_inventory.py`
(verificado por `tests-integration/test_dependency_inventory.py`).

> Nada de lo que sigue se ha asumido por convención: cada fila procede de un import real
> localizado en el árbol de código o de una declaración en un `pyproject.toml`.

## 1. Entorno reproducible

| Elemento | Valor |
|---|---|
| Python | **3.11** (`.python-version`; `requires-python = ">=3.11"` en el lock) |
| Gestor | **uv** (ADR-0032), workspace de 5 miembros |
| Lockfile | `uv.lock` committeado — **única fuente de versiones** |
| Instalación base | `make install` → `uv sync --all-packages --locked` |
| Grupo `dev` | ruff, mypy, pytest, pytest-cov, pre-commit, types-PyYAML + extras `ai-models[export]` y `diagnostic-agent[detection]` |
| Grupo `train` | `ai-models[deep]` (torch, onnx) + shap + matplotlib — **no entra en dev** para no arrastrar torch a CI ni al edge |
| Instalar entrenamiento | **`make install-train`** → `uv sync --all-packages --group train --locked` |
| Verificar antes de un experimento | **`make check-train-env`** — lo invocan los targets `experiments-*`, de modo que un run largo no arranca con el entorno incompleto |

**Aviso operativo verificado en esta auditoría:** `uv sync --all-packages --locked` (sin
`--group train`) **desinstala torch, shap y matplotlib** y puede resolver versiones
distintas de numpy/scipy. Los experimentos de la línea ML deben ejecutarse siempre con
`--group train`; los tests que dependen de torch/shap se saltan solos (`importorskip`).

**El lock es universal y contiene varias versiones del mismo paquete** seleccionadas por
marcadores de entorno (p. ej. numpy 2.3.5 / 2.4.6 / 2.5.2). Por eso la tabla siguiente
distingue **versión instalada** (la que realmente ejecutó) de **versiones presentes en el
lock**. Las cifras publicadas en los informes de fase proceden de la versión instalada en
tiempo de ejecución (p. ej. `shap.__version__` registrado en los artefactos XAI).

## 2. Inventario real (auditado)

| Librería | Instalada | En lock | Declarada en | Dónde se usa | Clasificación | Propósito |
|---|---|---|---|---|---|---|
| **numpy** | 2.4.6 | 2.3.5 / 2.4.6 / 2.5.2 | ai-models, diagnostic-agent[detection] | 41 ficheros: source, tests, experiments, tools | **CORE** | álgebra, matrices wide, ventanas, features, métricas |
| **scikit-learn** | 1.9.0 | 1.9.0 | ai-models | 10 ficheros: source, tests, experiments | **CORE** | detectores clásicos, escalado, PCA, métricas |
| **scipy** | 1.17.1 | 1.17.1 / 1.18.0 | ai-models *(declarada en esta auditoría)* | `ai_models.xai.metrics` | **CORE** (XAI) | correlación de rango (Spearman) |
| **torch** | 2.13.0 (+cu130) | 2.13.0 | ai-models[deep] → grupo `train` | AE denso, LSTM/GRU-AE, runner E8 | **EXPERIMENTAL** | entrenamiento de autoencoders |
| **shap** | 0.51.0 | 0.51.0 / 0.52.0 | grupo `train` | `ai_models.xai.shap_runner`, runner E8 | **EXPERIMENTAL** (XAI) | atribución (Permutation y Gradient) |
| **matplotlib** | 3.11.1 | 3.11.1 | grupo `train`, ai-models[research] | 4 runners de figuras (`e6/e7/e8/e9_figs`) | **VISUALIZATION_ONLY** | figuras de los informes |
| **onnxruntime** | 1.28.0 | 1.28.0 | diagnostic-agent[detection], ai-models[export] | detector edge, `tools/edge_validate.py` | **CORE (edge)** | inferencia en el edge |
| **skl2onnx** | 1.20.0 | 1.20.0 | ai-models[export] | `ai_models.export.onnx_export` | **CORE (deployment)** | conversión sklearn → ONNX |
| **onnx** | — | 1.22.0 | ai-models[deep] y [export] | sin import directo | **TRANSITIVE** + `DECLARED_BUT_UNUSED` | formato; lo usa skl2onnx |
| ~~pandas~~ | — | 3.0.5 (transitiva) | **RETIRADA en F20** | ningún import | eliminada del stack | — |
| pyyaml | 6.0.3 | 6.0.3 | obd-lab, grupo dev | suites, configs, tests | CORE (datos) | escenarios y configs |
| pydantic / pydantic-settings | 2.13.4 / 2.15.0 | ídem | todos los paquetes | contratos | CORE | contratos tipados (ADR-0007) |
| pytest | 9.1.1 | 9.1.1 | grupo dev | 20 ficheros | **TEST_ONLY** | suite de pruebas |
| sqlalchemy / pgvector | 2.0.52 / 0.5.0 | ídem | diagnostic-agent, cloud-platform | persistencia | CORE (fuera de ML) | PostgreSQL + pgvector (ADR-0030) |
| fastapi / httpx / uvicorn | 0.141.1 / 0.28.1 | ídem | agente y cloud | API | CORE (fuera de ML) | servicios |
| obd / ELM327-emulator | 0.7.3 / 3.0.5 | ídem | obd-lab[emulator] | laboratorio | OPTIONAL | emulación OBD-II (fuera del lock, ADR-0003) |
| langgraph / langchain-core | 1.2.11 | ídem | grupo dev, [reasoning] | runtime agéntico | EXPERIMENTAL | capa agente (no ML) |
| **seaborn** | — | **ausente** | **no declarada** | **ningún import** | **NO FORMA PARTE DEL STACK** | — |
| **umap-learn** | — | **ausente** | **no declarada** | **ningún import** | **solo propuesto documentalmente** | — |

Declaradas sin import directo pero **justificadas**: tooling del gate (ruff, mypy,
pytest-cov, pre-commit, types-PyYAML), extras de la capa LLM aún no implementada
(chromadb, sentence-transformers, ollama), driver usado vía SQLAlchemy (psycopg),
migraciones por CLI (alembic), entorno de investigación (jupyterlab) y `onnx` (rango
fijado para skl2onnx). El test de higiene falla si aparece una nueva sin justificar.

## 3. Stack por capas (estado real)

```
Data / Numerical        NumPy · PyYAML          (pandas RETIRADA en F20)
Estadística             SciPy (spearmanr)
Classical ML            scikit-learn
Deep Learning           PyTorch                 (solo grupo `train`)
Explainable AI          SHAP                    (Permutation + GradientExplainer)
Reducción dimensional   PCA (scikit-learn)      (UMAP: NO implementado)
Visualización           Matplotlib              (Seaborn: NO forma parte del stack)
Deployment / Edge       skl2onnx → ONNX → ONNX Runtime
```

## 4. Detalle por librería

### NumPy — CORE
Presente en 41 ficheros y transversal a todo el camino de datos: matriz columnar wide
(`ai_models.data.snapshot_matrix`), ventaneo y secuencias (`sequence_dataset`), cálculo de
features del contrato (`mecanico_contracts.features`), entradas de modelo, métricas de
evaluación (`ai_models.evaluation.protocol`), métricas XAI y de auditoría, y generación
sintética. Es la única dependencia científica que también viaja al **edge**
(`diagnostic-agent[detection]`).

### pandas — RETIRADA (F20)
Estuvo declarada en `ai-models` desde el inicio y **sin un solo import** en todo el repositorio:
el pipeline trabaja con arrays NumPy por decisión de rendimiento (F11/F12: materializar
objetos por fila costaba 1.2 GB de RSS). Los artefactos de experimentos se serializan en
JSON/CSV con la librería estándar. **Retirada en F20** (aprobada por el autor tras verificar 0 imports), con
`uv lock` + `uv sync` + gate completo en verde y el inventario reproducible como prueba.
No era legacy ni accidental: fue una previsión de uso que el diseño acabó no necesitando.
Sigue presente en el lock como transitiva de otros paquetes, que es lo correcto.

### SciPy — CORE (XAI)
Un único uso, pero en el camino crítico: `scipy.stats.spearmanr` en
`ai_models.xai.metrics.rank_correlation`, que sustenta la métrica de *agreement* entre
SHAP y el error por feature (Adenda XAI v1 §9). **Estaba importada sin declarar**: hueco
de reproducibilidad detectado por esta auditoría y **corregido** (`scipy>=1.11` en
`ai-models`). Llegaba al entorno como transitiva de scikit-learn/shap, de modo que un
checkout que resolviera sin ellas habría fallado.

### scikit-learn — CORE

| Componente | Módulo | Experimentos |
|---|---|---|
| `LocalOutlierFactor` | `ai_models.anomaly.baselines` | EXP-ANOM-001 (SELECTED) · brazo congelado en 002/005/006/007/008/009 |
| `IsolationForest` | `ai_models.anomaly.baselines` | EXP-ANOM-001 (REJECTED) |
| `OneClassSVM` | `ai_models.anomaly.baselines` | EXP-ANOM-001 (2º paquete) |
| `StandardScaler` / `RobustScaler` | `baselines`, `autoencoder` | EXP-ANOM-006 (comparación de escalado) y siguientes |
| `Pipeline` | `baselines`, `export.onnx_export` | paquete ONNX de LOF |
| `PCA` | runners E6/E7/E8/E9 | EXP-ANOM-007/008/009 (D2) y auditoría F19 |
| `metrics` (roc_auc, average_precision, silhouette, curvas) | runners y tests | EXP-ANOM-006…009 |

### PyTorch — EXPERIMENTAL

| Modelo | Módulo | Experimento |
|---|---|---|
| Autoencoder denso (42→32→16→8) | `ai_models.anomaly.autoencoder` | EXP-ANOM-006/007/008 |
| LSTM-AE y GRU-AE (`nn.LSTM` / `nn.GRU`) | `ai_models.anomaly.recurrent_autoencoder` | EXP-ANOM-009 |

- **Versión instalada: 2.13.0+cu130** — la rueda por defecto de PyPI en linux x86 arrastra
  binarios CUDA (triton, nvidia-*). **El código NUNCA selecciona dispositivo**: no hay
  `.cuda()`, `.to(device)`, `mps` ni `device=` en ningún módulo, de modo que el
  entrenamiento y la inferencia son **CPU-only por construcción**. No se declara soporte
  de CUDA ni de MPS porque no hay evidencia de uso en código.
- **Determinismo**: `torch.manual_seed(seed)` + `torch.Generator().manual_seed(seed)` para
  el barajado; verificado por tests de reproducibilidad en ambos modelos.
- **Serialización**: `torch.save` / `torch.load(weights_only=False)` de un diccionario con
  `state_dict`, configuración, estado del scaler e historia de pérdida. Es formato de
  **investigación**, no de distribución: al edge solo va ONNX (ADR-0009, docs/models/10).
- **Import perezoso** (`_torch()`), con error explícito si falta el grupo `train`.

### SHAP — EXPERIMENTAL (XAI)

Incorporado en F15 (ADR-0033) y ejecutado por primera vez en F16.

| Aspecto | Valor real |
|---|---|
| Versión | **0.51.0** (registrada en los artefactos de cada run) |
| Explainer estático | `shap.explainers.Permutation` con `maskers.Independent` |
| Explainer secuencial | `shap.GradientExplainer` (expected gradients) — elegido tras comprobar que `DeepExplainer` es **incompatible** con celdas LSTM/GRU, y validado contra Permutation |
| Función explicada | `reconstruction_error(x)` / `f(sequence) = reconstruction_error(sequence)` — siempre declarada |
| Background | exclusivamente train normal, selección determinista por semilla y **hasheada** |
| Muestreo | estratificado (TP por fallo, FP, TN), reproducible |
| Métricas implementadas | AR@K y Precision@K con baseline hipergeométrico, Jaccard@K, Spearman (SciPy), clases de agreement, estabilidad entre seeds y bajo perturbación; nivel temporal: FAR@K, TAR@K, FTH@K y estabilidad de celdas |
| Experimentos | EXP-ANOM-007 (D3 ADOPT), 008 (confirmado), 009 (extensión temporal) |

**SHAP no participa en el entrenamiento.** Su lugar en el ciclo es:
`entrenamiento → validación → diagnóstico del modelo → evaluación XAI → selección`.
Es offline: nunca en el camino de inferencia del edge.

### Matplotlib — VISUALIZATION_ONLY
Cuatro runners de figuras, todos con backend `Agg`: curvas de pérdida, PR y ROC,
distribuciones de score, FPR por escenario, recall por fallo y severidad, barrido de
longitud de secuencia, variabilidad entre seeds, fidelidad XAI, efecto de la cuantización
y matriz de cobertura. **Es dependencia canónica del reporting experimental** (las figuras
de los informes de fase se regeneran desde los JSON de resultados), pero **nunca** de
producción ni del edge.

### Seaborn — respuesta explícita
**No se utiliza.** No está declarada en ningún manifiesto, no aparece en `uv.lock` y no hay
un solo import en el repositorio. No se añade: matplotlib cubre el reporting actual y
añadir seaborn solo por convención introduciría una dependencia sin uso.

### UMAP — respuesta explícita
**Solo propuesto documentalmente.** `umap-learn` no está instalado, ni declarado, ni
importado. Aparece únicamente como candidato en el Protocolo ML v1 §nivel-2/3 y como
descartado explícitamente en el informe F18 («UMAP no se usó: no está en el entorno
aprobado»). La reducción dimensional realmente ejecutada es **PCA (scikit-learn)**.

### ONNX / ONNX Runtime — deployment
- **`skl2onnx`** convierte pipelines **sklearn** (scaler + detector) a ONNX en
  `ai_models.export.onnx_export`, junto a un `ModelManifest` con hash y umbral.
- **`onnxruntime`** ejecuta el paquete en el edge (`diagnostic_agent.detection.detector`,
  `providers=["CPUExecutionProvider"]`) y en `tools/edge_validate.py`.
- **Modelos exportados hoy: los de scikit-learn** (paquete LOF con paridad exacta
  sklearn↔ONNX verificada en F3/F4). **Los autoencoders de PyTorch NO se exportan todavía**:
  ningún experimento ha promovido un AE (D1 = REJECT en 006/007/008/009), de modo que no
  hay artefacto que exportar. `torch.onnx` no se usa.
- Cubierto por tests en `ai-models/tests/test_model_registry.py`,
  `diagnostic-agent/tests/test_agent_detection.py` y
  `tests-integration/test_traceability_e2e.py`. **La validación ARM64/QEMU sigue
  PENDIENTE** (tareas A2/A3): nada se declara validado en hardware real.

## 5. Librería → modelo

| Modelo | Framework | Estado |
|---|---|---|
| LOF k=10 | scikit-learn | SELECTED (EXP-ANOM-001) |
| Isolation Forest | scikit-learn | REJECTED |
| OC-SVM | scikit-learn | SELECTED (2º paquete) |
| Autoencoder denso | PyTorch | EXPERIMENTING (D1 REJECT ×3) |
| LSTM-AE / GRU-AE | PyTorch | REJECTED (F18) |
| `event-baseline-z`, máquina de estados `ed:1` | NumPy puro (sin framework) | SELECTED complementario |
| Distancias de auditoría (Mahalanobis, AUC, Cohen d) | NumPy + SciPy | instrumentación F19, no detectores |

## 6. Librería → experimento

| Experimento | Librerías científicamente relevantes |
|---|---|
| EXP-ANOM-001 (F3) | scikit-learn (LOF, IForest, OC-SVM, StandardScaler), NumPy |
| EXP-ANOM-002/003 (F8/F9) | NumPy, scikit-learn |
| EXP-ANOM-005 (F13) | NumPy, scikit-learn (paridad wide↔long) |
| EXP-ANOM-006 (F14) | **PyTorch** (AE denso), scikit-learn (scalers, silhouette), NumPy |
| EXP-ANOM-007 (F16) | PyTorch, **SHAP** (Permutation), scikit-learn (PCA, métricas), SciPy, Matplotlib |
| EXP-ANOM-008 (F17) | PyTorch, SHAP, scikit-learn, SciPy, Matplotlib |
| EXP-ANOM-009 (F18) | **PyTorch** (LSTM/GRU), **SHAP** (Gradient + Permutation), scikit-learn, Matplotlib |
| AUDIT-DATA-001 (F19) | NumPy, SciPy, scikit-learn (PCA), Matplotlib — **sin PyTorch ni SHAP nuevos** |
| EXP-PAT-* | no ejecutados |

## 7. Matriz training / evaluation / edge

| Librería | Training | Evaluation | Edge inference | Cloud/offline XAI |
|---|---|---|---|---|
| NumPy | sí | sí | **sí** | sí |
| SciPy | no | sí | no | sí |
| scikit-learn | sí | sí | **no** (ADR-0009) | no |
| PyTorch | sí | sí | **no** | no |
| SHAP | no | sí | **no** | **sí** |
| Matplotlib | no | sí (reporting) | **no** | sí |
| skl2onnx | no (exportación) | no | no | no |
| onnxruntime | no | paridad | **sí** | no |
| pandas | — | — | — | — |

Regla operativa: **la Raspberry Pi 5 solo necesita `onnxruntime` + `numpy`** (extra
`diagnostic-agent[detection]`). Ni scikit-learn ni PyTorch ni SHAP ni Matplotlib se
instalan en el edge — es exactamente lo que garantiza la separación de ADR-0009.

## 8. Capas de entorno (separación explícita)

| Capa | Qué instala | Comando | Contiene |
|---|---|---|---|
| **runtime / edge** | extra `diagnostic-agent[detection]` | imagen edge | `onnxruntime` + `numpy` **y nada más del stack científico** |
| **development** | grupo `dev` | `make install` | ruff, mypy, pytest, extras de export y detección |
| **training** | grupo `train` | **`make install-train`** | torch, shap, matplotlib (sobre el anterior) |
| **XAI / evaluación** | incluida en `train` | ídem | shap + matplotlib + scipy; **offline, nunca en el edge** |

`make check-train-env` verifica la capa de entrenamiento antes de lanzar un experimento.
Motivo documentado: `uv sync --all-packages --locked` **sin** `--group train` desinstala
torch, shap y matplotlib sin avisar.

## 9. Política de exportación de modelos (vía futura, aún no ejercida)

```
modelo scikit-learn            modelo PyTorch promovido
        ↓                              ↓
     skl2onnx                 evaluar exportación torch.onnx
        ↓                              ↓
      ONNX                    verificar paridad y compatibilidad ONNX
        ↓                              ↓
  ONNX Runtime                     ONNX Runtime
```

**Regla:** si en el futuro se promueve un AE denso, LSTM-AE o GRU-AE, su vía preferente es
**PyTorch → ONNX → ONNX Runtime**, condicionada a demostrar paridad numérica y
compatibilidad (el mismo listón que se aplicó al paquete LOF en F3/F4). **No se mantiene
PyTorch completo en la Raspberry Pi solo porque el entrenamiento se hiciera con PyTorch.**
Hoy la vía no está ejercida: ningún autoencoder ha sido promovido (D1 = REJECT en
EXP-ANOM-006/007/008/009), de modo que no existe artefacto que exportar y `torch.onnx` no
se usa en el repositorio.

## 10. Recomendaciones pendientes

1. Mantener `onnx` declarado: fija el rango que necesita `skl2onnx`, aunque no se importe.
2. Revisar los extras de la capa LLM (`chromadb`, `sentence-transformers`, `ollama`) cuando
   se aborde el runtime agéntico: hoy son previsión, no uso.

## 11. Software / Technology references

Documentación **oficial** de cada proyecto. Estas referencias son **técnicas** y no forman
parte de la bibliografía científica del TFM (que recoge los trabajos que justifican
metodología y evidencia; ver `docs/estado_del_arte/`). Se mantienen separadas
deliberadamente.

- NumPy — <https://numpy.org/doc/stable/>
- pandas — <https://pandas.pydata.org/docs/>
- SciPy — <https://docs.scipy.org/doc/scipy/>
- scikit-learn — <https://scikit-learn.org/stable/>
- PyTorch — <https://pytorch.org/docs/stable/>
- SHAP — <https://shap.readthedocs.io/en/latest/>
- Matplotlib — <https://matplotlib.org/stable/>
- ONNX — <https://onnx.ai/onnx/>
- ONNX Runtime — <https://onnxruntime.ai/docs/>
- uv — <https://docs.astral.sh/uv/>
