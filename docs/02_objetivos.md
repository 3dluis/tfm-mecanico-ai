# 2. Objetivos

**Estructura en tres niveles (alineación científica v3, 2026-08-18):** los objetivos
científicos producen evidencia para la PI; los instrumentales construyen lo necesario para
obtenerla; la ingeniería y administración habilitan la ejecución y **no se presentan como
contribuciones científicas**. Fuente canónica: [`docs/alineacion_v3/01_nucleo_cientifico.md`](alineacion_v3/01_nucleo_cientifico.md) §4. Correspondencia con los OE1–OE10 originales al final.

## 2.1 Objetivo general (científico)

Diseñar y evaluar experimentalmente un sistema inteligente híbrido capaz de identificar patrones de fallo no representados en su conocimiento disponible, formular hipótesis diagnósticas a partir del análisis contextual y longitudinal de datos OBD-II, contrastarlas mediante evidencia y consolidar únicamente aquellas que satisfagan criterios de validación como conocimiento reutilizable.

## 2.2 Nivel 1 — Objetivos científicos específicos

**OE-C1 — Operacionalizar «patrón no representado».** Delimitar y operacionalizar el concepto de patrón de fallo no representado en el conocimiento disponible, con su protocolo de exclusión triple (E-DET/E-RAG/E-MEM) y su verificación anti-contaminación.
*CV: definición formal publicada, matriz de contaminación verificable antes de cada run, exclusiones auditadas en EXP-MAIN-001.* — Habilita H-MAIN.

**OE-C2 — Detección contextual y longitudinal.** Evaluar el efecto del análisis contextual, longitudinal y personalizado sobre la identificación de anomalías (pasos 1–3 de la cadena).
*CV: EXP-SEG-001 + EXP-ANOM-004 (E0–E4) + brazo de personalización, con las métricas y unidades pre-registradas.* — Contrasta H-EVT, H-PERS.

**OE-C3 — Hipótesis verificadas por evidencia.** Evaluar la capacidad de generar hipótesis diagnósticas trazables y verificarlas mediante evidencia, incluida la evidencia contradictoria y las causas alternativas (pasos 5–7).
*CV: EXP-EXP-001 (LLM / +RAG / +RAG+verificación, control heurístico) y EXP-MAS-001 (A0–A6) con exactitud factual como métrica principal.* — Contrasta H-EXP, H-MAS.

**OE-C4 — Cadena completa con consolidación validada.** Evaluar la cadena completa mediante protocolo held-out/open-set con exclusión simultánea del detector, del corpus RAG y de la memoria, incluida la consolidación validada, la abstención y los controles negativos.
*CV: EXP-MEM-001 (M0/M1/M2) y EXP-MAIN-001 con P1–P5 y CN1–CN9.* — Contrasta H-MAIN, H-MEM.

## 2.2-bis Nivel 2 — Objetivos instrumentales

- **OI1 — Banco experimental reproducible:** entorno emulado, banco de fallos parametrizable con held-out, ground truth de eventos, benchmarks congelados por hash con criterio de **cobertura efectiva** (F22).
- **OI2 — Adquisición y persistencia:** captura de PIDs, validación, persistencia con esquema documentado y procedencia.
- **OI3 — Artefacto experimental:** detectores, segmentación de eventos, generador de hipótesis, RAG con manifiesto de corpus, verificador, memoria con estados epistemológicos, runtime multiagente, partición Edge–Cloud.
- **OI4 — Instrumentación experimental:** registro de runs, manifiestos y semillas, matriz de contaminación ejecutable, medición de recursos corregida, juez calibrado.

## 2.2-ter Nivel 3 — Ingeniería y administración

- **OA1 — Demostrador:** API REST documentada e interfaz mínima (antes OE9). Entregable de producto; sin pretensión científica.
- **OA2 — Memoria del TFM:** redacción conforme a la plantilla UAX, con las afirmaciones de novedad ajustadas a `estado_del_arte/afirmaciones_novedad.md` (antes OE10).

**Correspondencia con los objetivos originales:** OE-C1 ← (nuevo; formaliza la «precisión terminológica» de docs/01 v1) · OE-C2 ← OE4 + extensión de eventos · OE-C3 ← OE5+OE6 · OE-C4 ← OE7+OE8 · OI1 ← OE2 · OI2 ← OE3 · OI3 ← OE5/OE6/OE7 (construcción) · OI4 ← (implícito en OE8) · OA1 ← OE9 · OA2 ← OE10 · el estado del arte (antes OE1) pasa a ser método de la base de conocimiento (PRISMA dentro de DSR), con el mismo CV. Tabla completa: `docs/correspondencia_nomenclatura.md`.

## 2.3 Objetivos explícitamente secundarios (solo si el cronograma lo permite)

- **OS1:** Aplicación móvil Flutter consumiendo la API (en su defecto, la interfaz del OE9 será web mínima).
- **OS2:** Sincronización cloud bidireccional con resolución de conflictos (en su defecto, exportación/carga manual de la memoria de casos).
- **OS3:** Despliegue y medición en Raspberry Pi física (en su defecto, medición en contenedor ARM64 con límites de recursos, declarando la diferencia metodológica).

La distinción OE/OS es deliberada: los OE caben en el plazo de septiembre de 2026; los OS no condicionan la aprobación del TFM y se abordarán solo tras completar OE1–OE10.
