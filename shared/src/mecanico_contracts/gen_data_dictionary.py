"""Genera el diccionario de datos (markdown) DESDE los contratos Pydantic.

Única fuente de verdad: los modelos. Este script produce
``docs/data-architecture/02_diccionario_datos.md``; el diccionario nunca se edita a mano
(requisito de no-divergencia documentación↔contratos↔schemas↔BD).

Uso: ``python -m mecanico_contracts.gen_data_dictionary [ruta_salida]`` (o ``make data-docs``).
"""

import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel

import mecanico_contracts as mc
from mecanico_contracts.export_schemas import EXPORTABLE

#: Metadatos por entidad que no viven en el schema: clasificación, productor, consumidor,
#: residencia (edge/cloud) y papel en la pregunta de investigación (PI).
ENTITY_META: dict[str, dict[str, str]] = {
    "OBDReading": {
        "clase": "RAW",
        "produce": "acquisition (edge) / obd-lab",
        "consume": "telemetry, storage",
        "vive": "edge (retención corta) → cloud opcional",
        "papel": "Observación directa del vehículo: base empírica de toda la cadena",
    },
    "TelemetrySession": {
        "clase": "contexto (agrupa RAW)",
        "produce": "acquisition / obd-lab",
        "consume": "todos",
        "vive": "edge + cloud (histórico)",
        "papel": "Reproducibilidad exacta de experimentos (fuente, semilla, versiones)",
    },
    "TelemetryPoint": {
        "clase": "NORMALIZED",
        "produce": "telemetry (edge)",
        "consume": "windows, features",
        "vive": "edge (retención media) → cloud resúmenes",
        "papel": "Esquema canónico: aísla al resto del sistema de la fuente concreta",
    },
    "TelemetryWindow": {
        "clase": "DERIVED",
        "produce": "telemetry (edge)",
        "consume": "features, trazabilidad",
        "vive": "edge (retención larga en metadatos)",
        "papel": "Unidad de análisis temporal (multivariable, requisito de la PI)",
    },
    "FeatureVector": {
        "clase": "DERIVED",
        "produce": "detection (edge) / ai-models",
        "consume": "modelos ML, verify",
        "vive": "edge → cloud (con anomalías)",
        "papel": "Contrato train↔inferencia; entrada exacta de los detectores",
    },
    "ModelInference": {
        "clase": "INFERRED",
        "produce": "detection (edge)",
        "consume": "anomalías, auditoría",
        "vive": "edge → cloud",
        "papel": "Toda ejecución de modelo queda auditada (qué modelo/versión/umbral)",
    },
    "DetectedAnomaly": {
        "clase": "INFERRED",
        "produce": "detection (edge)",
        "consume": "agente (disparador)",
        "vive": "edge → cloud (prioridad alta)",
        "papel": "El hecho a explicar; jamás la produce el LLM (separación ML/LLM)",
    },
    "DTCRecord": {
        "clase": "RAW",
        "produce": "acquisition",
        "consume": "agente",
        "vive": "edge → cloud",
        "papel": "Síntoma estándar; la detección NO depende de él",
    },
    "DiagnosticCase": {
        "clase": "INFERRED",
        "produce": "agente (edge)",
        "consume": "API, móvil, cloud, memoria",
        "vive": "edge → cloud (prioridad alta)",
        "papel": "Unidad de razonamiento explicable; nunca solo texto",
    },
    "DiagnosticHypothesis": {
        "clase": "INFERRED",
        "produce": "agente:hypothesize",
        "consume": "verify, report, feedback",
        "vive": "edge → cloud",
        "papel": "Causa candidata con estado y ranking auditables",
    },
    "DiagnosticEvidence": {
        "clase": "INFERRED (referencia datos RAW/DERIVED)",
        "produce": "agente:verify",
        "consume": "report, tribunal/memoria del TFM",
        "vive": "edge → cloud (permanente)",
        "papel": "Sustento verificable de cada hipótesis (a favor Y en contra)",
    },
    "ProvenanceRecord": {
        "clase": "metadatos",
        "produce": "agente",
        "consume": "auditoría, experimentos",
        "vive": "edge → cloud (permanente)",
        "papel": "Responde '¿de dónde salió este diagnóstico?' con un solo objeto navegable",
    },
    "CaseMemory": {
        "clase": "INFERRED (memoria episódica)",
        "produce": "agente:memorize",
        "consume": "recall",
        "vive": "edge (local) + cloud (consolidada)",
        "papel": "Experiencia recuperable; su nivel epistemológico pondera su peso",
    },
    "LearnedPattern": {
        "clase": "INFERRED (memoria semántica)",
        "produce": "consolidación (diseñada, no automática)",
        "consume": "recall, investigación",
        "vive": "cloud (maestro) + subset edge",
        "papel": "LA memoria evolutiva: candidato a 'patrón no documentado' de la PI",
    },
    "PatternRelation": {
        "clase": "metadatos",
        "produce": "consolidación",
        "consume": "análisis",
        "vive": "cloud + subset edge",
        "papel": "Grafo ligero de relaciones entre patrones",
    },
    "DiagnosticFeedback": {
        "clase": "verdad externa",
        "produce": "obd-lab (ground truth) / humano",
        "consume": "evaluación",
        "vive": "edge → cloud (permanente)",
        "papel": "Cierra el lazo: mide si la memoria mejora el diagnóstico (H3)",
    },
    "MaintenanceEvent": {
        "clase": "RAW (evento externo)",
        "produce": "usuario/taller",
        "consume": "agente, análisis",
        "vive": "edge → cloud",
        "papel": "Permite estudiar intervención→efecto en telemetría",
    },
    "AgentRun": {
        "clase": "metadatos de ejecución",
        "produce": "agente",
        "consume": "auditoría, experimentos",
        "vive": "edge → cloud",
        "papel": "Working memory trazable; variable memory_mode del experimento H3",
    },
    "AgentStep": {
        "clase": "metadatos de ejecución",
        "produce": "agente",
        "consume": "auditoría",
        "vive": "edge → cloud",
        "papel": "E/S estructuradas por nodo (sin chain-of-thought)",
    },
    "RetrievalEvent": {
        "clase": "metadatos de ejecución",
        "produce": "agente:recall/retrieve",
        "consume": "métricas RAG",
        "vive": "edge → cloud",
        "papel": "Grounding medible: qué participó en cada diagnóstico",
    },
    "KnowledgeDocument": {
        "clase": "corpus",
        "produce": "ingesta (con licencia)",
        "consume": "retrieve",
        "vive": "cloud (maestro) + cache edge",
        "papel": "Conocimiento citable del RAG",
    },
    "KnowledgeChunk": {
        "clase": "corpus",
        "produce": "ingesta",
        "consume": "retrieve",
        "vive": "cloud + cache edge",
        "papel": "Unidad de recuperación y de cita",
    },
    "ModelManifest": {
        "clase": "metadatos de modelo",
        "produce": "ai-models:export",
        "consume": "models_runtime",
        "vive": "cloud (registry) + edge (activo)",
        "papel": "Gobernanza del ciclo modelo→edge",
    },
    "ScenarioSpec": {
        "clase": "configuración experimental",
        "produce": "suites obd-lab",
        "consume": "generador, evaluación",
        "vive": "repo (YAML)",
        "papel": "Ground truth y reproducibilidad de escenarios",
    },
    "RecordedSession": {
        "clase": "cabecera de archivo",
        "produce": "obd-lab",
        "consume": "ai-models, replay",
        "vive": "archivos JSONL",
        "papel": "Serialización de TelemetrySession + inventario del archivo",
    },
    "SyncEnvelope": {
        "clase": "transporte",
        "produce": "sync (edge)",
        "consume": "cloud",
        "vive": "outbox edge",
        "papel": "Push idempotente priorizado edge→cloud",
    },
    "VehicleEvent": {
        "clase": "INFERRED (event_class marca observed/inferred/estimated)",
        "produce": "event detector (edge) / obd-lab (ground truth)",
        "consume": "event features, baselines, agente, análisis",
        "vive": "edge → cloud (metadatos; la telemetría se referencia, no se duplica)",
        "papel": "Unidad formal de análisis contextual (F6): segmenta sin perder el RAW",
    },
    "EventFeatureVector": {
        "clase": "DERIVED",
        "produce": "event features (edge)",
        "consume": "baselines, detección contextual, comparación de eventos",
        "vive": "edge → cloud",
        "papel": "Hace comparables eventos equivalentes (misma context_signature)",
    },
    "EventBaseline": {
        "clase": "INFERRED (normalidad acumulada)",
        "produce": "baseline builder (edge)",
        "consume": "detección contextual, agente",
        "vive": "edge (por vehículo) → cloud (respaldo)",
        "papel": "'Lo normal PARA ESTE vehículo en ESTE contexto' (H6/PI.5)",
    },
    "TrainingRun": {
        "clase": "metadatos de experimentación",
        "produce": "ai-models (entrenamiento)",
        "consume": "registry, provenance, memoria del TFM",
        "vive": "ai-models (JSON) → cloud futuro",
        "papel": "Un entrenamiento reproducible: datos+config+seed+commit+métricas (F7)",
    },
    "ModelExperiment": {
        "clase": "metadatos de experimentación",
        "produce": "ai-models (experimentos)",
        "consume": "informes de comparación, selección de modelos",
        "vive": "ai-models (JSON+YAML) → cloud futuro",
        "papel": "Comparación válida: mismos datos/split/features/protocolo (F7)",
    },
    "ModelEvaluation": {
        "clase": "metadatos de experimentación",
        "produce": "ai-models / validación edge",
        "consume": "registry, model cards, matriz hardware",
        "vive": "ai-models (JSON)",
        "papel": "Evaluación bajo protocolo con hardware explícito (interpreta latencias)",
    },
    "ModelRegistryEntry": {
        "clase": "catálogo",
        "produce": "ai-models:registry",
        "consume": "diagnostic-agent (ModelRouter), despliegue",
        "vive": "ai-models/registry/ (filesystem+JSON) → cloud futuro",
        "papel": "Catálogo común ML/LLM/embedding con ciclo de vida y capacidades (F7)",
    },
    "ModelDeployment": {
        "clase": "estado de despliegue",
        "produce": "despliegue manual (TFM)",
        "consume": "edge runtime, rollback",
        "vive": "edge (activo) + registro",
        "papel": "active/previous por dispositivo: rollback posible aunque sea manual",
    },
    "HardwareValidation": {
        "clase": "metadatos de validación",
        "produce": "validación por objetivo hardware",
        "consume": "registry, decisión EDGE_APPROVED",
        "vive": "registry (embebido)",
        "papel": "Matriz mac/arm64/RPi: EDGE_APPROVED nunca solo por métricas offline",
    },
}


def _fmt_type(prop: dict[str, Any]) -> str:
    if "$ref" in prop:
        return str(prop["$ref"]).split("/")[-1]
    if "anyOf" in prop:
        return " \\| ".join(_fmt_type(p) for p in prop["anyOf"])
    t = prop.get("type", "any")
    if t == "array":
        return f"list[{_fmt_type(prop.get('items', {}))}]"
    if t == "object":
        return "dict"
    return str(t)


def _constraints(prop: dict[str, Any]) -> str:
    keys = ("pattern", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "enum")
    parts = [f"{k}={prop[k]}" for k in keys if k in prop]
    return "; ".join(str(p) for p in parts) or "—"


def render_model(model: type[BaseModel]) -> str:
    schema = model.model_json_schema()
    meta = ENTITY_META.get(model.__name__, {})
    required = set(schema.get("required", []))
    lines = [f"### {model.__name__}", ""]
    doc = (model.__doc__ or "").strip().split("\n")[0]
    lines.append(doc)
    lines.append("")
    if meta:
        lines.append(
            f"**Clasificación:** {meta['clase']} · **Produce:** {meta['produce']} · "
            f"**Consume:** {meta['consume']} · **Vive en:** {meta['vive']}"
        )
        lines.append(f"**Papel en la investigación:** {meta['papel']}")
        lines.append("")
    lines.append("| Campo | Tipo | Req. | Descripción | Restricciones |")
    lines.append("|---|---|---|---|---|")
    for name, prop in schema.get("properties", {}).items():
        req = "✔" if name in required else "opc."
        desc = str(prop.get("description", "—")).replace("|", "\\|")
        lines.append(f"| `{name}` | {_fmt_type(prop)} | {req} | {desc} | {_constraints(prop)} |")
    lines.append("")
    return "\n".join(lines)


HEADER = """# 02 — Diccionario de datos (AUTOGENERADO)

> **No editar a mano.** Este documento se genera desde los contratos Pydantic con
> `make data-docs` (módulo `mecanico_contracts.gen_data_dictionary`). La cadena
> documentación ↔ contratos ↔ JSON Schema ↔ BD se mantiene sin divergencia porque los
> tres últimos derivan del mismo modelo y este documento se regenera en CI.

Clasificación de datos (ADR-0012): **RAW** = observado directamente · **NORMALIZED** =
transformado a esquema canónico · **DERIVED** = calculado (features/ventanas) ·
**INFERRED** = producido por modelos o por el agente. *Un dato inferido nunca se presenta
como observación real*: la clase de cada entidad consta en su ficha y la API/UI deben
etiquetarlo.

Convenciones globales: tiempos en UTC (ISO-8601); ids globalmente únicos (UUID/texto);
todo mensaje lleva `schema_version` (política de versionado en `07_provenance_versionado.md`);
unidades canónicas: rpm, km/h, %, °C, g/s, kPa, V, grados.

---
"""


def main() -> int:
    out = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path("docs/data-architecture/02_diccionario_datos.md")
    )
    body = "\n".join(render_model(m) for m in EXPORTABLE)
    enums_doc = ["## Enumeraciones", ""]
    for enum_cls in (
        mc.SessionSource,
        mc.DataClass,
        mc.EventClass,
        mc.AnomalyScope,
        mc.CaseStatus,
        mc.HypothesisStatus,
        mc.EvidenceKind,
        mc.EvidenceRole,
        mc.EpistemicLevel,
        mc.PatternStatus,
        mc.PatternRelationKind,
        mc.FeedbackKind,
        mc.FeedbackVerdict,
        mc.MemoryMode,
        mc.StepStatus,
        mc.ModelType,
        mc.ModelStatus,
        mc.ModelCapability,
        mc.HardwareValidationStatus,
        mc.Severity,
        mc.DetectorKind,
        mc.TransportKind,
        mc.AgentNode,
        mc.SyncEntity,
    ):
        values = ", ".join(f"`{v.value}`" for v in enum_cls)
        enums_doc.append(f"- **{enum_cls.__name__}**: {values}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(HEADER + body + "\n" + "\n".join(enums_doc) + "\n", encoding="utf-8")
    print(f"Diccionario generado: {out} ({len(EXPORTABLE)} entidades)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
