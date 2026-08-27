# Alineación científica v4 — Historial de la pregunta de investigación

**2026-08-27 · Nota metodológica.** La pregunta de investigación de este TFM ha cambiado
tres veces antes de su formulación actual. El historial se documenta de forma explícita
porque forma parte del proceso investigador y porque cualquier lector del repositorio
encontrará documentos redactados bajo formulaciones anteriores. **Ninguna versión previa se
oculta ni se reescribe retroactivamente.**

## 1. Las cuatro formulaciones

| Versión | Enunciado (resumen) | Vigencia | Dónde aparece |
|---|---|---|---|
| **PI v1** | ¿Puede un agente híbrido (LLM + no supervisado + memoria + RAG) descubrir y explicar patrones no documentados a partir de OBD-II? | Fase 0 → 12-ago-2026 | docs/01 v1, informes F0–F9 |
| **PI v2** («Opción B») | ¿Puede un sistema híbrido descubrir y explicar patrones de fallo previamente no documentados mediante análisis contextual y longitudinal de OBD-II? | 12-ago → 18-ago-2026 | `propuesta_alineacion_final.md`, pre-registro v1 §1 (hasta ENM-000), consolidado v1.0 |
| **PI v3** | ¿Puede un sistema híbrido identificar patrones no representados en su conocimiento disponible, generar hipótesis diagnósticas y validarlas mediante evidencia antes de incorporarlas como conocimiento reutilizable? | 18-ago → 27-ago-2026 | `alineacion_v3/`, pre-registro v1 (ENM-000), memoria cap. 1–3 |
| **PI v4** (OFICIAL) | ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II reales, rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis sin fundamento? | desde 27-ago-2026 | `alineacion_v4/`, todo documento vivo |

## 2. Por qué cambió

**El propósito original del trabajo era la explicación diagnóstica apoyada en
documentación técnica.** La propuesta temática lo planteaba como un asistente que razona
sobre datos OBD-II reales y justifica sus conclusiones con documentación recuperada, frente
a la opacidad del diagnóstico convencional por DTC. La explicación anclada en evidencia era
el problema; el resto eran mecanismos.

**La revisión sistemática desplazó el enunciado hacia el descubrimiento y el aprendizaje.**
Al mapear los antecedentes se hizo visible que la explicación mediante RAG estaba
comparativamente bien cubierta y que las combinaciones menos exploradas involucraban
novedad relativa, generación de hipótesis y memoria validada. El enunciado se fue ampliando
para ocupar ese hueco: primero incorporando explícitamente «descubrir patrones no
documentados» (v1 y v2) y después la cadena completa de ocho pasos con validación previa a
la consolidación en memoria (v3). *El registro del repositorio muestra que el verbo
«descubrir» ya figuraba en la PI v1 de Fase 0*: la ampliación no fue un salto único sino
una deriva progresiva, y así debe describirse.

**La revisión con el tutor determinó que ese alcance excedía un Trabajo Fin de Máster.**
La cadena de ocho pasos exigía contrastar simultáneamente detección contextual,
reconocimiento de novedad, generación de hipótesis, verificación, consolidación validada y
arquitectura multiagente: seis familias de hipótesis, ocho experimentos encadenados y una
dependencia crítica no resuelta (la elección del modelo de lenguaje). La auditoría interna
lo confirmaba en sus propios términos: *«nada de lo ejecutado responde PI.b–PI.d»*
(`alineacion_v3/02_trazabilidad.md` §2, lectura 4), es decir, la mitad de la cadena carecía
de evidencia propia a seis semanas de la entrega.

**Los hallazgos útiles se mantuvieron.** No se descartó ningún experimento, banco, dataset,
resultado negativo ni decisión técnica. Los catorce estudios ejecutados (F3–F22) siguen
siendo válidos y pasan a sostener instrumentalmente el paso 3 de la nueva cadena; los
bancos congelados (`suite_v2`, `cases_v2`) se reutilizan sin modificación; el mecanismo de
exclusión controlada del corpus, diseñado para operacionalizar la novedad relativa, se
convierte en la palanca experimental que produce la condición de evidencia insuficiente.

**La PI se acotó a explicación, trazabilidad y abstención.** La v4 conserva el núcleo
original del trabajo —explicar un diagnóstico con evidencia— y le añade las dos exigencias
que la revisión sistemática mostró menos evaluadas: que la correspondencia entre afirmación
y evidencia sea **verificable**, y que el sistema **reconozca cuándo no debe explicar**.

## 3. Cómo leer esto

Esto es evolución normal del proceso investigador, no corrección de un error. Un enunciado
se amplía cuando la revisión muestra huecos y se acota cuando el diseño experimental
demuestra que no cabe en el plazo y los recursos disponibles. Lo que sí sería un defecto
metodológico es lo contrario: mantener una pregunta que la evidencia recogida no puede
contrastar, o retirar en silencio los compromisos que no se van a cumplir.

Consecuencias operativas de esta nota:

1. Los documentos históricos cerrados (informes F0–F25, ADRs aceptados, alineaciones v2 y
   v3, pre-registro congelado) **conservan su redacción**. Se leen a través de
   `01_nucleo_cientifico.md` §11 y de `docs/correspondencia_nomenclatura.md`.
2. El pre-registro `prereg-v1.0` se modifica **solo por enmienda fechada** (ENM-001), como
   exige su §2.1 y su §13. La enmienda no es retroactiva porque no se ha ejecutado ningún
   experimento confirmatorio.
3. La memoria del TFM debe incluir esta evolución en su capítulo metodológico. Presentar la
   PI v4 como si hubiera sido la única desde el principio contradiría el propio repositorio.
