# ADR-0009 — Ciclo de vida de modelos ML: ONNX + manifiesto + registry mínimo

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 2

## Contexto

Los modelos se entrenan en `ai-models` (Mac/cloud) y se ejecutan en `diagnostic-agent`
(RPi/contenedor limitado). Hace falta un camino gobernado entrenamiento→edge sin plataforma
MLOps completa. Además, la separación estricta ML/LLM exigida por el autor debe materializarse.

## Decisión

1. **Formato de intercambio: ONNX** para todos los modelos matemáticos (IForest vía
   skl2onnx; autoencoder vía export PyTorch→ONNX, cuantización INT8 opcional). El edge solo
   depende de `onnxruntime` — nunca de scikit-learn/PyTorch.
2. **Paquete de modelo** `model-<nombre>-<semver>/` = artefacto(s) `.onnx` + `manifest.json`
   (contrato `ModelManifest`: nombre, semver, tipo de detector, hash sha256, features esperadas
   con orden y normalización, tamaño de ventana, umbral de decisión, métricas de validación,
   semilla, fechas, `schema_version`).
3. **Registry mínimo en `cloud-platform`:** tabla + volumen de artefactos; `POST /models`,
   `GET /models/latest?type=…`, descarga con verificación de hash. En desarrollo, el "registry"
   puede ser un directorio compartido por volumen — misma convención de paquete.
4. **Carga segura en el edge:** `models_runtime` valida manifiesto contra las features runtime;
   incompatible ⇒ conserva el modelo anterior (rollback = no borrar el previo). Modelo activo
   registrado en SQLite para trazabilidad de cada `DetectedAnomaly` (qué modelo/versión la produjo).
5. **Los LLM quedan fuera de este ciclo:** se referencian por tag de Ollama en configuración.
   El LLM no produce `DetectedAnomaly` jamás (separación ML/LLM: la detección es matemática;
   el LLM razona sobre anomalías ya detectadas).

## Alternativas consideradas

- *MLflow / registry formal:* excelente, pero añade servicio+DB+UI que nadie más usará;
  desproporcionado para 2 familias de modelos y un solo autor. Descartado (reevaluable post-TFM).
- *Pickle/joblib directo:* ata el edge a versiones exactas de sklearn y es un vector de
  ejecución de código; descartado.
- *TFLite:* ecosistema centrado en TensorFlow; nuestro stack es sklearn/PyTorch → ONNX es la
  ruta natural con runtime ARM64 oficial. Descartado.

## Consecuencias

- `ai-models/export` y `diagnostic-agent/models_runtime` comparten solo `ModelManifest` (shared).
- La trazabilidad modelo→anomalía→diagnóstico queda garantizada para la memoria del TFM.
- Deuda consciente: sin firma criptográfica de artefactos (hash solamente); declarado suficiente
  para prototipo académico.
