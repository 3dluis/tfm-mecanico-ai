# 2. Objetivos

**Estructura en tres niveles (alineación científica v4, 2026-08-27):** los objetivos
científicos producen evidencia para la PI; los instrumentales construyen lo necesario para
obtenerla; la ingeniería y la administración habilitan la ejecución y **no se presentan como
contribuciones científicas**. Fuente canónica: [`docs/alineacion_v4/01_nucleo_cientifico.md`](alineacion_v4/01_nucleo_cientifico.md) §4. Correspondencia con los objetivos de las versiones anteriores al final.

## 2.1 Objetivo general (científico)

Diseñar y evaluar experimentalmente un agente basado en recuperación aumentada por evidencia (RAG) que explique diagnósticos vehiculares obtenidos a partir de datos OBD-II reales, manteniendo una correspondencia verificable entre cada afirmación de la explicación y la evidencia que la sostiene, y que se abstenga de explicar cuando la evidencia disponible resulte insuficiente, bajo las restricciones de cómputo de una plataforma embarcada.

## 2.2 Nivel 1 — Objetivos científicos específicos

**OE-C1 — Contexto diagnóstico verificable.** Construir el contexto diagnóstico a partir de telemetría OBD-II real —ventanas, eventos operativos y detección de anomalías ya validada en la serie F3–F22— y definir el objeto de entrada del razonamiento con su procedencia registrada.
*CV: contexto reproducible por semilla, con `feature_vector` y sesión identificados, y calidad de la segmentación evaluada (EXP-SEG-001).* — Habilita todas las hipótesis; instrumental.

**OE-C2 — Recuperación de evidencia.** Diseñar y evaluar la recuperación de evidencia documental pertinente para un diagnóstico dado, sobre un corpus con manifiesto y con disponibilidad de evidencia controlada.
*CV: EXP-RET-001 con Recall@k y Precision@k sobre la evidencia de referencia congelada, y verificación del control de disponibilidad.* — Contrasta H-GRD.

**OE-C3 — Explicación trazable.** Definir una representación de la explicación en afirmaciones atómicas con referencia de evidencia, y un procedimiento que verifique que la correspondencia afirmación→evidencia→dato es efectiva y no meramente declarada.
*CV: corrección y completitud de la citación, y profundidad de traza hasta el `feature_vector`, medidas de forma determinista y contrastadas frente a un control de atribución trivial.* — Contrasta H-TRC y H-GRD.

**OE-C4 — Suficiencia y abstención.** Operacionalizar el criterio de suficiencia de la evidencia e implementar una política de abstención que distinga la explicación sostenida de la declaración de evidencia insuficiente.
*CV: política implementada en el grafo del agente, con umbral explícito, y evaluada en el escenario de evidencia retirada (tasas de abstención correcta, falsa abstención y falsa aceptación).* — Contrasta H-ABS.

**OE-C5 — Evaluación experimental.** Evaluar el agente bajo disponibilidad de evidencia controlada, midiendo exactitud diagnóstica, soporte y fidelidad de la explicación, corrección y completitud de la trazabilidad, y calidad de la abstención, dentro del presupuesto edge.
*CV: EXP-EVID-001 (3 brazos × 2 escenarios × 40 casos) con las co-primarias Q1–Q5, los controles CN1–CN4 y CN7–CN9 y el criterio transversal edge.* — Contrasta H-MAIN y H-SEL.

## 2.2-bis Nivel 2 — Objetivos instrumentales

- **OI1 — Banco experimental reproducible:** entorno emulado, escenarios parametrizables, ground truth de eventos y benchmarks congelados por hash con criterio de cobertura efectiva (`suite_v2`, `cases_v2`).
- **OI2 — Adquisición y persistencia:** captura de PID, validación, persistencia con esquema documentado y procedencia registrada.
- **OI3 — Corpus documental con disponibilidad controlada:** construcción y congelación de las variantes C-A (evidencia suficiente), C-B (evidencia ausente) y C-B′ (evidencia parcial), con manifiesto, checksum y evidencia de referencia por caso.
- **OI4 — Artefacto experimental:** retriever, generador de explicación en afirmaciones, verificador determinista de soporte, política de suficiencia y abstención, integrados en el grafo del agente.
- **OI5 — Instrumentación experimental:** registro de runs, manifiestos y semillas, auditoría ejecutable de la exclusión del corpus, medición de recursos corregida y juez calibrado.

## 2.2-ter Nivel 3 — Ingeniería y administración

- **OA1 — Demostrador:** API REST documentada e interfaz mínima. Entregable de producto; sin pretensión científica.
- **OA2 — Memoria del TFM:** redacción conforme a la plantilla UAX, con las afirmaciones de novedad ajustadas a `estado_del_arte/afirmaciones_novedad.md`.

**Correspondencia con la alineación v3:** OE-C1(v4) ← OE-C2(v3), degradado a instrumental conservando toda su evidencia · OE-C2(v4) y OE-C3(v4) ← OE-C3(v3), dividido y ampliado con trazabilidad · OE-C4(v4) ← OE-C1(v3), reorientado (la exclusión ya no define novedad, define insuficiencia de evidencia) · OE-C5(v4) ← OE-C4(v3), sin la parte de consolidación validada. Correspondencia con los OE1–OE10 originales: `docs/correspondencia_nomenclatura.md`.

**Objetivos retirados del alcance científico:** la evaluación de la memoria con validación y de la consolidación de conocimiento, y la comparación de arquitecturas multiagente, pasan a trabajo futuro con su diseño conservado ([`05_fuera_de_alcance.md`](alineacion_v4/05_fuera_de_alcance.md)).

## 2.3 Objetivos explícitamente secundarios (solo si el cronograma lo permite)

- **OS1:** Aplicación móvil Flutter consumiendo la API (en su defecto, la interfaz del OE9 será web mínima).
- **OS2:** Sincronización cloud bidireccional con resolución de conflictos (en su defecto, exportación/carga manual de la memoria de casos).
- **OS3:** Despliegue y medición en Raspberry Pi física (en su defecto, medición en contenedor ARM64 con límites de recursos, declarando la diferencia metodológica).

La distinción OE/OS es deliberada: los OE caben en el plazo de septiembre de 2026; los OS no condicionan la aprobación del TFM y se abordarán solo tras completar OE1–OE10.
