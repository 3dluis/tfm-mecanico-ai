# 6. Plan de investigación: estado del conocimiento, datasets, contribuciones y delimitación investigación/ingeniería

> **⚠ Nota de vigencia (2026-08-27, ADR-0036).** Documento de planificación anterior a la
> acotación de la pregunta de investigación. Las contribuciones vigentes son **C1**
> (protocolo de disponibilidad de evidencia controlada), **C2** (trazabilidad
> afirmación→evidencia→dato) y **C3** (caracterización empírica de la abstención):
> `docs/alineacion_v4/01_nucleo_cientifico.md` §7. Las contribuciones enunciadas aquí que
> dependían de la memoria evolutiva y de la integración de la cadena completa pasan a
> trabajo futuro (`05_fuera_de_alcance.md`). El plan de datasets y la delimitación
> investigación/ingeniería siguen vigentes.

## 6.1 Investigaciones necesarias (lista de trabajo, Fase 1)

Cada ítem tiene un producto concreto. **Ninguna referencia se citará en la memoria sin haber sido verificada** (acceso al texto, autores, año, venue).

| ID | Tema a investigar | Producto |
|----|-------------------|----------|
| IN-1 | Diagnóstico y mantenimiento predictivo vehicular con OBD-II/CAN: enfoques ML clásicos y deep learning, qué señales usan, qué fallos cubren | Tabla comparativa + limitaciones identificadas |
| IN-2 | Detección de anomalías en series temporales multivariantes en edge: técnicas, coste computacional, benchmarks habituales | Shortlist justificada de 2 técnicas a implementar (OE4) |
| IN-3 | Agentes LLM con herramientas y memoria (tool use, memoria episódica/semántica, arquitecturas tipo grafo) | Marco conceptual para C6 y C5b; vocabulario para la memoria |
| IN-4 | RAG en dominios técnicos: chunking, evaluación de recuperación, reducción de alucinación; limitaciones de LLM-as-judge | Diseño de la evaluación de H2 (RI4) |
| IN-5 | SLM en hardware limitado: benchmarks de modelos 1–4 B cuantizados en ARM/Raspberry Pi | Selección justificada de candidatos LLM (D6) |
| IN-6 | **Verificación de datasets** (§6.2): disponibilidad real, licencia, variables incluidas | Decisión documentada de qué datasets se usan |
| IN-7 | Estándares: SAE J1979 (PIDs), J2012 (DTC), J1962, ISO 15031, ISO 15765 (CAN); qué puede citarse desde fuentes accesibles | Base normativa del capítulo de contexto |
| IN-8 | Modelos de fallo de motor de gasolina documentados (relación causa→firma en PIDs: fuga de vacío→LTFT+, MAF derivado→carga incoherente, etc.) para diseñar la inyección de fallos con fundamento | Especificación justificada de los 5+ escenarios de fallo (C1, RI1) |
| IN-9 | Trabajos que evalúan el soporte de una explicación por la evidencia recuperada, la atribución verificable de citas y la abstención ante evidencia insuficiente | Línea D de la revisión (`estado_del_arte/linea_d_trazabilidad_fidelidad_abstencion.md`); sostiene el vacío V4\* |

Presupuesto temporal: IN-1 a IN-9 concentradas en Fase 1 (véase `07`), con actualización puntual durante la escritura.

## 6.2 Datasets: necesidades y candidatos

**Necesidades:** (N1) series temporales OBD-II de conducción real para validar externamente la detección de anomalías; (N2) datos de operación normal variada para modelar la normalidad del emulador con realismo; (N3) corpus documental para RAG; (N4) catálogo de DTC estándar.

**Candidatos a verificar en IN-6** (existencia, licencia y contenido deben confirmarse antes de comprometerlos en la memoria; esta lista es de partida, no un compromiso):

- Datasets de conducción con OBD-II publicados en repositorios abiertos (Kaggle, IEEE DataPort, Mendeley Data, Zenodo) — búsqueda sistemática con criterios: incluye PIDs de motor crudos, frecuencia ≥ 0,2 Hz, licencia que permita uso académico.
- UAH-DriveSet (conducción naturalista; verificar qué señales OBD incluye).
- Datasets académicos de detección de intrusiones en CAN (p. ej. los publicados por grupos coreanos tipo HCRL): útiles solo si contienen tráfico OBD interpretable; probablemente fuera de dominio (su etiqueta es ataque, no fallo mecánico) — evaluar y probablemente descartar con justificación.
- Benchmarks genéricos de mantenimiento predictivo (NASA C-MAPSS/turbofán, AI4I 2020): **no vehiculares**; solo se usarían para sanity-check de las técnicas de detección, nunca para conclusiones del dominio.

**Datos generados por el propio proyecto (fuente principal, N2 y validación de H1):** sesiones emuladas con escenarios normales y de fallo, publicables como dataset sintético reproducible junto al código (posible contribución, §6.3-C4).

**Corpus RAG (N3, N4):** descripciones de DTC estándar (compilaciones de licencia abierta a verificar), documentación técnica libre (p. ej. materiales educativos de diagnóstico con licencia compatible), y fichas de fallo redactadas para el proyecto a partir de fuentes citadas. Los manuales propietarios de fabricante quedan excluidos (L4).

## 6.3 Posibles contribuciones científicas

Ordenadas de mayor a menor solidez esperable:

- **C1.** Evidencia empírica sobre la viabilidad y límites de un agente LLM de diagnóstico con RAG y memoria ejecutando íntegramente en recursos de clase Raspberry Pi (medidas de latencia/memoria/calidad y análisis del compromiso edge vs. cloud).
- **C2.** Diseño y evaluación de una arquitectura de agente (grafo explícito con nodo de verificación de hipótesis contra telemetría) para diagnóstico explicable anclado en datos, con trazas auditables.
- **C3.** Cuantificación del efecto de una memoria episódica de casos en el rendimiento diagnóstico de un agente LLM pequeño (H3), positiva o negativa.
- **C4.** Banco de pruebas reproducible y abierto: emulador de escenarios de fallo OBD-II parametrizable + dataset sintético + protocolo de evaluación. Posiblemente la contribución más reutilizable por terceros.
- **C5.** Metodología de evaluación de explicaciones diagnósticas (rúbrica + verificación de anclaje factual en el corpus recuperado), con análisis de acuerdo evaluador humano/LLM.

## 6.4 Posibles publicaciones derivadas

Sin comprometer venues concretos (dependerá de resultados y de convocatorias vigentes tras la defensa):

- **P1.** Artículo de sistema/experimentos: el agente edge completo y su evaluación (C1+C2) — congreso o revista de sistemas inteligentes, IA aplicada o edge computing.
- **P2.** Artículo corto/demo: el banco de pruebas reproducible (C4) — track de demos/recursos de un congreso, o repositorio con DOI (Zenodo) citado desde un artículo.
- **P3.** Estudio focalizado: efecto de la memoria episódica en agentes SLM (C3), si el resultado —positivo o negativo— es nítido.

Decisión sobre a cuál apuntar: después de la Fase 4 (resultados), con el tutor.

## 6.5 Aspectos innovadores del proyecto

1. La **trazabilidad verificable** entre cada afirmación de una explicación diagnóstica y la evidencia que la sostiene, con doble anclaje documental y telemétrico. Las piezas existen por separado en los trabajos revisados; su verificación conjunta sobre diagnóstico OBD-II no fue identificada.
2. El **nodo de verificación** del agente: contrastar cada hipótesis del LLM contra la telemetría real antes de emitirla (reduce alucinación por diseño, no solo por prompt).
3. La **abstención ante evidencia insuficiente** como comportamiento diseñado, implementado y medido —con su curva riesgo-cobertura— y no como una advertencia en el texto de la respuesta. *(La memoria evolutiva, que esta lista enunciaba antes en este punto, pasa a trabajo futuro: `docs/alineacion_v4/05_fuera_de_alcance.md`.)*
4. El **banco de fallos inyectables reproducible** para un dominio donde los datos de fallo etiquetados son escasos.
5. La evaluación **honesta de la frontera edge/cloud**: mismo agente, dos LLM, cuantificación del coste de la autonomía local.

## 6.6 Qué es investigación y qué es ingeniería

| Bloque | Naturaleza | Justificación |
|---|---|---|
| Estado del arte (OE1) | Investigación | Revisión estructurada con hueco justificado |
| Definición de modelos de fallo e inyección (C1/IN-8) | Investigación (metodología experimental) | Instrumento de medida del estudio; requiere fundamento y diseño anti-circularidad (RI1) |
| Comparación de detectores (OE4) | Investigación empírica | Pregunta PI.1/H1 con métricas |
| Arquitectura del agente y nodo de verificación (OE6) | Investigación aplicada + ingeniería | El diseño es contribución (C2); su implementación es ingeniería |
| Efecto de RAG en explicaciones (OE5/H2) | Investigación empírica | Experimento controlado A/B |
| Efecto de la memoria (OE7/H3) | Investigación empírica | Experimento controlado |
| Viabilidad de recursos (H4) | Investigación empírica (con limitación L2) | Medición sistemática |
| Adquisición, persistencia, API, UI (OE3, OE9) | Ingeniería | Soporte necesario sin pregunta de investigación propia |
| Entorno Docker/emulación (OE2) | Ingeniería (con valor metodológico) | Reproducibilidad del estudio |
| Memoria del TFM (OE10) | Comunicación científica | — |

Esta tabla se trasladará a la introducción de la memoria para dejar claro al tribunal dónde está el aporte investigador.
