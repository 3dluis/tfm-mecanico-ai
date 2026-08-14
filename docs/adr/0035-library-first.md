# ADR-0035 — Library-first: reutilizar implementaciones científicas maduras

**Estado:** Aceptada (regla permanente del autor, F20 · 2026-08-14)
**Relacionada con:** ADR-0032 (uv y entorno), [docs/models/15](../models/15_stack_ml_xai.md)
(stack auditado y fuente canónica de versiones), Protocolo ML v1

## Contexto

El TFM debe dedicar su esfuerzo a la investigación —la pregunta sobre descubrimiento y
explicación de patrones de fallo—, no a reimplementar utilidades que el ecosistema
científico ya resuelve de forma probada. Cada línea de código propio equivalente a una
función de librería añade superficie de error, carga de mantenimiento y riesgo de
divergencia numérica que después contamina resultados experimentales.

## Decisión

**Siempre que exista una librería madura, mantenida, ampliamente adoptada y adecuada al
problema, se usa esa librería antes que escribir código propio equivalente.**

Ámbitos donde la regla se aplica con especial rigor: álgebra y operaciones numéricas ·
métricas estadísticas · preprocesamiento · scalers · splits · algoritmos de ML · métricas
de evaluación · XAI · visualización · serialización/intercambio de modelos · inferencia.

**Comprobación previa obligatoria** antes de escribir una implementación propia: verificar
si la funcionalidad existe ya en NumPy, SciPy, scikit-learn, PyTorch, SHAP, Matplotlib,
ONNX / ONNX Runtime, o en otra librería especializada suficientemente mantenida y
justificada.

**No se reimplementan** (si la versión de librería cubre el caso): `StandardScaler`,
`RobustScaler`, `PCA`, `LocalOutlierFactor`, `IsolationForest`, `OneClassSVM`, correlación
de Spearman, métricas ROC/PR, explainers de SHAP.

### Condiciones que justifican código propio

Basta con que se cumpla **una**, y la decisión **debe quedar documentada**:

1. No existe una implementación adecuada.
2. La implementación existente no soporta nuestro contrato temporal/OBD-II.
3. Existe una necesidad científica específica del experimento.
4. Hay que adaptar una técnica publicada no disponible en una librería estable.
5. La dependencia externa introduciría un coste, tamaño o incompatibilidad **edge**
   desproporcionados.

### Wrappers vs adaptadores

- **Prohibido:** el wrapper que solo replica una API existente sin aportar nada.
- **Permitido:** el adaptador pequeño que sostiene un contrato interno, la trazabilidad o
  la separación edge/training — por ejemplo envolver un detector de scikit-learn para
  cumplir el `Detector` Protocol y registrar su umbral y su manifiesto.

## Auditoría del código propio existente (F20)

| Implementación propia | Condición que la justifica | Nota |
|---|---|---|
| `ai_models.audit.detectability.auc` (Mann–Whitney) | 3 | métrica de auditoría sin ajuste ni umbral; **verificada contra `sklearn.metrics.roc_auc_score`** en test |
| `cohens_d`, `standardized_shift`, `overlap_coefficient` | 3 | tamaños de efecto con la convención declarada en el protocolo; no hay equivalente directo con la misma semántica en las librerías del stack |
| `signal_to_normal_ratio`, `quantization_absorption`, `coverage_bucket` | 2, 3 | dependen del contrato OBD-II (paso de cuantización J1979, régimen operativo): no existen fuera del dominio |
| `classify_detectability` | 3 | reglas de decisión del protocolo F19, no una técnica estadística |
| `ai_models.xai.metrics` (AR@K, baseline hipergeométrico, Jaccard@K) | 4 | métricas de la Adenda XAI v1; `rank_correlation` **sí delega en `scipy.stats.spearmanr`** |
| `ai_models.xai.temporal` (FAR/TAR/FTH) | 3, 4 | métricas temporales definidas por el proyecto |
| `AutoencoderDetector`, `RecurrentAutoencoderDetector` | 2 | modelos construidos **sobre `torch.nn`**; el código propio es el ensamblaje y el contrato (semillas, máscara, error temporal), no el álgebra |
| `evaluation.protocol` (umbral por cuantil, métricas por episodio) | 2, 3 | ADR-0011 exige protocolo sin point-adjustment y por episodio: no es la semántica de `sklearn.metrics` |
| `mecanico_contracts.features` (fs1) | 2 | contrato entrenamiento↔inferencia versionado; se apoya en NumPy |
| `data.snapshot_matrix`, `data.sequence_dataset` | 2, 5 | ventaneo con máscara NULL≠0 y trazabilidad por sesión; pandas se evaluó y **se retiró por no aportar** (docs/models/15) |

Delegaciones ya vigentes que la regla consolida: escalado (`StandardScaler`/`RobustScaler`),
detectores clásicos (LOF, IForest, OC-SVM), `PCA`, curvas y AUC (`sklearn.metrics`),
Spearman (`scipy.stats`), explainers (`shap`), figuras (`matplotlib`), exportación
(`skl2onnx`) e inferencia edge (`onnxruntime`).

## Consecuencias

- Toda iteración futura comprueba primero la existencia en librería; si introduce código
  propio, lo justifica por una de las cinco condiciones en el informe de fase.
- La revisión de código propio pasa a ser parte del cierre de fase, junto al gate de
  calidad.
- Riesgo asumido: dependencia del ecosistema. Mitigado por el lock committeado, la fuente
  canónica de versiones y la separación estricta de lo que viaja al edge (solo
  `onnxruntime` + `numpy`).
