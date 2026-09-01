"""Genera los notebooks del laboratorio con su estructura documental obligatoria.

Cada notebook abre declarando qué pregunta responde y bajo qué criterio se
consideraría refutado, y cierra registrando qué produjo. La plantilla se genera
una sola vez: a partir de ahí cada notebook se edita a mano en su fase.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"

# (fichero, título, fase, objetivo, relación con la PI)
SPEC: list[tuple[str, str, str, str, str]] = [
    (
        "00_environment_check",
        "Comprobación del entorno",
        "E1",
        "Verificar que la máquina reúne intérprete, acelerador, base de datos y "
        "extensión vectorial, y dejar constancia de la configuración exacta.",
        "No responde a la PI. Establece la base sobre la que cualquier resultado "
        "posterior es reproducible y comparable.",
    ),
    (
        "01_synthetic_obd_generation",
        "Generación de OBD-II sintético",
        "E2",
        "Producir señales OBD-II plausibles y reproducibles, con relaciones "
        "físicas aproximadas entre variables y escenarios de fallo controlados.",
        "Aporta el control experimental: permite conocer la verdad de referencia "
        "y manipular la evidencia disponible sin ambigüedad.",
    ),
    (
        "02_real_obd_ingestion",
        "Ingesta de OBD-II real",
        "E3",
        "Incorporar registros OBD-II reales, normalizar sus señales al catálogo "
        "del laboratorio y conservar la metadata de procedencia.",
        "La PI se formula sobre datos reales: este notebook aporta el dato sobre "
        "el que se responde.",
    ),
    (
        "03_timeseries_eda",
        "Análisis exploratorio temporal",
        "E4",
        "Caracterizar las señales como series temporales: distribuciones, "
        "ausencias, comportamiento móvil, correlaciones y contraste normal/fallo.",
        "Determina qué señales y qué ventanas pueden sostener una observación, "
        "que es el primer eslabón de la traza de evidencia.",
    ),
    (
        "04_preprocessing_features",
        "Preprocesamiento y descriptores",
        "E5",
        "Definir el ventanado, el particionado sin fuga temporal y los "
        "descriptores extraídos de cada ventana.",
        "Fija la unidad de análisis a la que se anclará cada observación citada "
        "en una explicación.",
    ),
    (
        "05_model_training",
        "Entrenamiento del modelo especializado",
        "E6-E7",
        "Entrenar un baseline y un modelo temporal sobre las mismas particiones "
        "y con semillas registradas.",
        "El diagnóstico lo produce este modelo, no el LLM. Su salida es el objeto "
        "que después hay que explicar y justificar.",
    ),
    (
        "06_model_evaluation",
        "Evaluación del modelo",
        "E8",
        "Medir el rendimiento y la calibración del modelo en el conjunto de test aislado.",
        "La confianza del modelo entra en el criterio de suficiencia: solo es "
        "utilizable si está calibrada.",
    ),
    (
        "07_xai",
        "Atribución sobre el modelo",
        "E9",
        "Obtener, para cada caso, qué señales y qué tramo temporal sostienen la "
        "predicción, con su dirección de contribución.",
        "Convierte la predicción en evidencia observacional localizable. La "
        "atribución no es causalidad y no se presentará como tal.",
    ),
    (
        "08_rag_corpus",
        "Corpus documental y troceado",
        "E10-E11",
        "Construir el corpus, trocearlo conservando fuente, sección y página, e "
        "indexarlo en PostgreSQL con pgvector.",
        "Aporta la evidencia documental. Sin procedencia intacta no hay traza "
        "posible desde una afirmación hasta su origen.",
    ),
    (
        "09_retrieval_evaluation",
        "Evaluación de la recuperación",
        "E12",
        "Medir la calidad de la recuperación contra un conjunto de referencia anotado.",
        "Delimita cuánta de la evidencia relevante llega realmente al agente, y "
        "por tanto qué puede y qué no puede sostener.",
    ),
    (
        "10_llm_agent",
        "Integración del agente",
        "E13",
        "Componer el prompt con diagnóstico, confianza, evidencia observacional, "
        "atribución y fragmentos recuperados, y obtener salida estructurada.",
        "El LLM redacta y organiza; no diagnostica ni aporta conocimiento propio como fuente.",
    ),
    (
        "11_evidence_sufficiency",
        "Suficiencia de la evidencia",
        "E15",
        "Calibrar, solo sobre validación, el criterio que decide si la evidencia "
        "disponible sostiene una explicación.",
        "Es el componente que la PI interroga directamente: reconocer cuándo la "
        "evidencia no basta.",
    ),
    (
        "12_abstention",
        "Abstención",
        "E16",
        "Analizar cuándo el agente se abstiene, y separar la abstención correcta "
        "de la injustificada.",
        "La abstención es una salida válida del sistema, no un fallo. La PI "
        "pregunta si el agente sabe cuándo callar.",
    ),
    (
        "13_integrated_experiment",
        "Experimento integrado",
        "E17",
        "Ejecutar el pipeline completo bajo las cuatro condiciones de "
        "disponibilidad de evidencia: FULL, PARTIAL, ABSENT y DISTRACTOR.",
        "Es el diseño que permite atribuir el comportamiento del agente a la "
        "evidencia disponible y no a otra cosa.",
    ),
    (
        "14_final_evaluation",
        "Evaluación final",
        "E19",
        "Consolidar las métricas M1-M6, contrastarlas con los criterios de "
        "refutación y emitir el veredicto sobre la PI.",
        "Responde a la PI en los términos fijados de antemano: sostenida, "
        "parcialmente sostenida o no sostenida.",
    ),
    (
        "15_tfm_demo",
        "Demostración",
        "E20",
        "Mostrar el mismo caso real con y sin la evidencia relevante en el "
        "corpus, y contrastar explicación trazable frente a abstención.",
        "Es la escenificación directa de la PI ante el tribunal.",
    ),
    (
        "TFM_EXPERIMENTO_COMPLETO",
        "Experimento completo",
        "E20",
        "Ejecutar la cadena entera de extremo a extremo en una sola pasada "
        "reproducible, desde el dato OBD-II hasta las métricas finales.",
        "Reúne en un solo artefacto el recorrido completo que responde a la PI.",
    ),
]

PI = (
    "¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de "
    "datos OBD-II reales, rastreando cada explicación hasta su evidencia de "
    "origen, y reconocer cuándo la evidencia disponible no es suficiente para "
    "sostener una explicación en lugar de generar una hipótesis sin fundamento?"
)


def md(source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def cabecera(titulo: str, fase: str, objetivo: str, relacion: str) -> str:
    return f"""# {titulo}

**Fase:** {fase}

## Objetivo

{objetivo}

## Relación con la pregunta de investigación

> {PI}

{relacion}

## Hipótesis

_Por declarar antes de ejecutar la fase._

## Datos

_Dataset, versión y partición utilizados._

## Método

_Procedimiento, parámetros y semillas._

## Métricas

_Qué se mide y con qué instrumento._

## Criterio de éxito o refutación

_Fijado antes de mirar los resultados._
"""


CIERRE = """## Resultados

_Lo observado, sin interpretación._

## Interpretación

_Qué significa, y qué no significa._

## Limitaciones

_Qué queda fuera del alcance de lo mostrado._

## Conclusión experimental

_Respuesta al criterio fijado en la cabecera._

## Artefactos generados

_Ficheros producidos, con su ruta._
"""

PREAMBULO = """# Los notebooks importan del paquete; no duplican lógica científica.
import sys
from pathlib import Path

RAIZ = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(RAIZ / "src"))

import mecanico_ai_exp

mecanico_ai_exp.__version__
"""


def cuerpo(nombre: str) -> list[dict[str, object]]:
    if nombre == "00_environment_check":
        return [
            code(
                "from mecanico_ai_exp.config.environment import audit, resolve_device\n"
                "\n"
                "informe = audit()\n"
                "print(informe)\n"
            ),
            md(
                "El dispositivo de cómputo se resuelve explícitamente. Si MPS no "
                "estuviera disponible el laboratorio funciona en CPU, pero eso "
                "queda registrado: no se oculta el fallback."
            ),
            code("resolve_device()\n"),
            md("Rutas del laboratorio, ancladas a la raíz del repositorio."),
            code(
                "from mecanico_ai_exp.config import paths\n"
                "\n"
                'nombres = ("DATA_RAW_REAL", "CORPUS_PROCESSED", "RESULTS", "FIGURES")\n'
                "for nombre in nombres:\n"
                "    ruta = getattr(paths, nombre)\n"
                "    relativa = ruta.relative_to(paths.ROOT)\n"
                '    print(f"{nombre:20s} {relativa}  existe={ruta.exists()}")\n'
            ),
        ]
    return [
        md("_Contenido pendiente de la fase correspondiente._"),
        code("# Implementación en la fase indicada en la cabecera.\n"),
    ]


def main() -> None:
    NOTEBOOKS.mkdir(parents=True, exist_ok=True)
    for nombre, titulo, fase, objetivo, relacion in SPEC:
        destino = NOTEBOOKS / f"{nombre}.ipynb"
        if destino.exists():
            print(f"omitido (ya existe): {destino.name}")
            continue
        celdas = [md(cabecera(titulo, fase, objetivo, relacion)), code(PREAMBULO)]
        celdas.extend(cuerpo(nombre))
        celdas.append(md(CIERRE))
        cuaderno = {
            "cells": celdas,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3 (mecanico-ai-exp)",
                    "language": "python",
                    "name": "python3",
                },
                "language_info": {"name": "python", "version": "3.11"},
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        destino.write_text(json.dumps(cuaderno, indent=1, ensure_ascii=False) + "\n")
        print(f"creado: {destino.name}")


if __name__ == "__main__":
    main()
