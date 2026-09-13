# Git History Report

Estado: **propuesta, pendiente de aprobación**. Este informe se rellenará con los SHA nuevos,
la validación y las instrucciones de rollback cuando (y si) el autor apruebe la ejecución de las
fases 5–9 descritas en `docs/git-history-audit.md` y `docs/commit-plan.md`. Nada de lo que
sigue se ha ejecutado todavía.

## Estado inicial

| | |
|---|---|
| HEAD original | `3b001d4c210a696efb88fe73bfa54829d8065926` |
| Branch | `main` |
| Working tree | limpio en el momento de la auditoría (13-09-2026); sin untracked, sin stash |
| Remote | `origin` = `https://github.com/3dluis/-mecanico-ai-exp.git`, **vacío** (nunca se ha hecho push) |
| Tags | ninguno |

## Backup

Referencia de recuperación: rama `backup/pre-history-cleanup-20260913-1815` → `3b001d4`.
Creada el 13-09-2026 antes de cualquier otra operación. No se borra en ninguna fase.

## Tabla commit → propósito → experimento → acción propuesta

Acción propuesta según la opción A de `docs/git-history-audit.md` §5.3:
«**quitar trailers**» = eliminar las dos líneas `Co-Authored-By: Claude Opus 5 (1M context)
<noreply@anthropic.com>` y `Claude-Session: …`; el resto del mensaje, el árbol, el autor y las
fechas no cambian. «**SHA nuevo**» = el commit no tiene trailers pero desciende de uno que sí,
por lo que su SHA cambia sin que cambie nada de su contenido. «**sin cambios**» = ni el mensaje
ni el SHA se tocan.

| # | Commit | Date | Technical Purpose | Experiment | Proposed Action |
|--:|--------|------|-------------------|------------|-----------------|
| 1 | `3a2ce39` | 2026-09-01 13:21 | Andamiaje del laboratorio experimental | — | sin cambios |
| 2 | `9b84894` | 2026-09-01 13:21 | Configuración tipada y auditoría del entorno | — | sin cambios |
| 3 | `41d06f0` | 2026-09-01 13:21 | Base de datos: Alembic y creación reproducible | — | sin cambios |
| 4 | `619940c` | 2026-09-01 13:21 | Notebooks con estructura documental obligatoria | — | sin cambios |
| 5 | `eaee16c` | 2026-09-01 13:21 | Plan experimental, metodología y guías de instalación | — | sin cambios |
| 6 | `f110fae` | 2026-09-01 13:22 | Ajustar el generador de notebooks a los gates de estilo | — | sin cambios |
| 7 | `7b5fe34` | 2026-09-01 13:45 | Renombrar el laboratorio a mecanico-ia-exp | — | sin cambios |
| 8 | `e53dd31` | 2026-09-01 13:59 | E2: generador OBD-II sintético con verdad de referencia | E2 | sin cambios |
| 9 | `057bd3a` | 2026-09-01 14:12 | E4: análisis exploratorio temporal | E4 | sin cambios |
| 10 | `a8e9f6c` | 2026-09-01 14:32 | E5: ventanado, descriptores y reparto sin fuga | E5 | sin cambios |
| 11 | `a031c29` | 2026-09-01 14:51 | E6: baseline con bosque aleatorio | E6 | sin cambios |
| 12 | `27b9f8d` | 2026-09-01 15:06 | E7: modelo temporal GRU sobre MPS | E7 | sin cambios |
| 13 | `dffe031` | 2026-09-01 15:16 | E10: corpus documental condicionado por vehículo | E10 | sin cambios |
| 14 | `35f8302` | 2026-09-01 15:28 | Candidato Mazda 3 BK 2007 con manual de taller verificado en contenido | — | sin cambios |
| 15 | `770ce70` | 2026-09-01 15:46 | Calibrar el generador OBD-II contra el manual de taller del Mazda 3 BK | — | sin cambios |
| 16 | `be5433b` | 2026-09-01 16:15 | E11: carga del corpus del Mazda 3 BK en pgvector | E11 | sin cambios |
| 17 | `355d475` | 2026-09-01 16:23 | E12: evaluacion de la recuperacion sobre conjunto anotado | E12 | sin cambios |
| 18 | `09ca1e5` | 2026-09-01 16:50 | E9: atribucion SHAP sobre el modelo especializado | E9 | sin cambios |
| 19 | `4437d07` | 2026-09-01 17:07 | E15: verificador de suficiencia, sin modelo de lenguaje | E15 | sin cambios |
| 20 | `bd671b9` | 2026-09-01 17:21 | Corpus multilingüe: español e inglés | — | sin cambios |
| 21 | `7a0d714` | 2026-09-01 17:30 | Guía de reproducción paso a paso y correccion propagada | — | sin cambios |
| 22 | `be0516d` | 2026-09-01 17:33 | Matriz de validacion de la PI con resultados medidos | — | sin cambios |
| 23 | `c5f6c66` | 2026-09-01 17:50 | Plan actualizado y notebooks rellenados | — | sin cambios |
| 24 | `15a131e` | 2026-09-01 17:51 | Relajar reglas de importacion en los notebooks | — | sin cambios |
| 25 | `7fb2255` | 2026-09-01 19:49 | E17: las cuatro condiciones de evidencia y umbrales calibrados | E17 | sin cambios |
| 26 | `9bbbf81` | 2026-09-01 20:23 | E13: agente con SLM local, herramientas y salida estructurada | E13 | sin cambios |
| 27 | `a6057fd` | 2026-09-01 21:38 | E13b: conjunto de ajuste del SLM y entrenador PyTorch+PEFT | E13b | sin cambios |
| 28 | `6171407` | 2026-09-01 22:04 | Proveedor transformers con adaptador LoRA y correccion del entrenador | — | sin cambios |
| 29 | `e2d7c59` | 2026-09-02 12:08 | E13: un solo vocabulario de motivos de abstención y registro auditable del agente | E13 | sin cambios |
| 30 | `76c5bfe` | 2026-09-02 12:10 | E13: documentar el ajuste ejecutado y la primera medición antes/después | E13 | sin cambios |
| 31 | `0612026` | 2026-09-02 12:15 | E13: resumen antes/después en el paquete y cuaderno 10 con hipótesis y criterio | E13 | sin cambios |
| 32 | `1b4d299` | 2026-09-02 12:26 | E13: cerrar la iteración 1 del ajuste y preparar la iteración 2 | E13 | sin cambios |
| 33 | `144bef1` | 2026-09-02 12:26 | E13: serializar el identificador del caso anotado en el registro del agente | E13 | sin cambios |
| 34 | `8ae57b4` | 2026-09-02 12:28 | E13: el cuaderno 10 lee el registro de la iteración 2 cuando exista | E13 | sin cambios |
| 35 | `ffca7f9` | 2026-09-02 13:43 | E13: cerrar el ajuste del SLM con la iteración 2 (9/9 sobre el conjunto anotado) | E13 | sin cambios |
| 36 | `3f8eac3` | 2026-09-02 14:28 | Memoria: texto fuente de los capítulos que no dependen de los datos reales | — | sin cambios |
| 37 | `ce9be6d` | 2026-09-03 13:42 | ADR-003: la pregunta de investigación deja de exigir datos OBD-II reales | ADR-003 | sin cambios |
| 38 | `d8d8d32` | 2026-09-03 13:42 | Procedencia de datos: taxonomía cerrada real / synthetic / simulated / public_dataset | — | sin cambios |
| 39 | `18a51be` | 2026-09-03 13:42 | PI sin requisito de datos reales: matriz de validación, plan, diseño y notas de fase | — | sin cambios |
| 40 | `fbebb91` | 2026-09-03 13:42 | Trazabilidad tras ADR-003: I-07 resuelta, GATE-01 en PASS, OE-M2 desbloqueado | ADR-003 | sin cambios |
| 41 | `8b4f0d6` | 2026-09-03 13:42 | Cuadernos: PI enmendada en la cabecera de los diecisiete y E3 como validación externa | E3 | sin cambios |
| 42 | `c94a3d6` | 2026-09-03 13:42 | Memoria: PI enmendada y procedencia declarada en lugar de resultados condicionales | — | sin cambios |
| 43 | `b7a68f9` | 2026-09-03 13:42 | Informe de impacto y changelog del cambio de la PI (ADR-003) | ADR-003 | sin cambios |
| 44 | `ef61ee2` | 2026-09-03 13:47 | Correcciones tras la auditoría independiente del cambio de la PI | — | sin cambios |
| 45 | `8d55def` | 2026-09-03 13:47 | Informe del tutor sobre el cambio de la PI: FAIL por un MAJOR, corregido y reevaluado | — | sin cambios |
| 46 | `ac428e6` | 2026-09-03 18:26 | Informe del tutor: estados FIXED también en el bloque de traspaso | — | sin cambios |
| 47 | `d45caad` | 2026-09-03 18:35 | Revisión integral: línea base, inventario de skills y auditoría de plantilla UAX | — | sin cambios |
| 48 | `2313c39` | 2026-09-03 22:15 | Revisión integral: informe estadístico consolidado y actualización del inventario de skills | — | sin cambios |
| 49 | `a6a5f40` | 2026-09-03 22:39 | Revisión integral: auditoría de referencias consolidada (BLOCKED, 4 mayores) | — | sin cambios |
| 50 | `ee5cb0b` | 2026-09-03 22:40 | Revisión integral: auditoría RAG consolidada (FAIL, 11 mayores) | — | sin cambios |
| 51 | `880a4eb` | 2026-09-03 22:43 | Revisión integral: auditoría experimental consolidada (FAIL, 12 mayores) | — | sin cambios |
| 52 | `8725ea1` | 2026-09-03 22:57 | Revisión integral: verificación de evidencia consolidada (FAIL, 11 mayores, 78 claims) | — | sin cambios |
| 53 | `1162d1e` | 2026-09-03 23:30 | Revisión integral: evaluación académica del tutor consolidada (FAIL 55/99, 13 mayores) | — | sin cambios |
| 54 | `cda9676` | 2026-09-03 23:32 | Revisión integral: plan de corrección consolidado (STOP GATE 1) | — | sin cambios |
| 55 | `af008f9` | 2026-09-03 23:33 | Revisión: rutas del entorno de trabajo escritas de forma neutra en los documentos de revisión | — | sin cambios |
| 56 | `42116d6` | 2026-09-03 23:55 | Plan de corrección detallado: reclasificación de severidad, reejecuciones y decisiones | — | sin cambios |
| 57 | `f6396fe` | 2026-09-04 00:07 | Grupo 1 · P-06 y RX-00: corregir los tres defectos de instrumento y registrar la ejecución | P-06, RX-00 | sin cambios |
| 58 | `081c309` | 2026-09-04 00:08 | Criterio del umbral de suficiencia, fijado antes de ejecutar el barrido | — | sin cambios |
| 59 | `f9c5c0c` | 2026-09-04 00:10 | RX-04: barrido del umbral registrado como artefacto sobre validación | RX-04 | sin cambios |
| 60 | `35d2360` | 2026-09-04 00:15 | ENM-U01: enmienda al criterio del umbral, con regla de estabilidad cuantitativa | ENM-U01 | sin cambios |
| 61 | `f1d76d7` | 2026-09-04 00:18 | ENM-U01 aplicada: el punto de operación pasa a 0,79 con su procedencia registrada | ENM-U01 | sin cambios |
| 62 | `24e94d1` | 2026-09-04 00:19 | RX-01: suficiencia reejecutada con instrumento corregido y umbral 0,79 | RX-01 | sin cambios |
| 63 | `68cb5f5` | 2026-09-04 00:21 | P-05 y P-06C: separar lo medido de lo invariante y declarar la selección de época | P-05, P-06C | sin cambios |
| 64 | `ed27aad` | 2026-09-04 00:47 | RX-02: agente reejecutado en las tres configuraciones con el denominador corregido | RX-02 | sin cambios |
| 65 | `14f800a` | 2026-09-04 00:51 | P-03: las cuatro condiciones se extienden de un fallo a tres, y aparece un fallo del verificador | P-03 | sin cambios |
| 66 | `8c3ec98` | 2026-09-04 06:06 | El registro de suficiencia estampa la versión de la política | — | sin cambios |
| 67 | `be3d897` | 2026-09-04 06:07 | Congelar el resultado del verificador v1 y registrar el hallazgo que reveló | — | sin cambios |
| 68 | `c474e81` | 2026-09-04 06:08 | Política de suficiencia v2, documentada antes de implementarse | — | sin cambios |
| 69 | `100082d` | 2026-09-04 06:11 | Verificador v2: el soporte exige que el fragmento sea un procedimiento | — | sin cambios |
| 70 | `9d44037` | 2026-09-04 06:13 | Verificador v2 medido sobre los mismos casos: 14/17, con una abstención falsa nueva | — | sin cambios |
| 71 | `c1108b8` | 2026-09-04 06:31 | Política de suficiencia v2.1, documentada antes de implementarse | — | sin cambios |
| 72 | `a34bab2` | 2026-09-04 06:37 | Verificador v2.1: la seccion como unidad de papel | — | quitar trailers |
| 73 | `10ed541` | 2026-09-04 06:41 | Resultado del verificador v2.1: 15/17, sin regresiones nuevas | — | quitar trailers |
| 74 | `478ebe0` | 2026-09-04 06:41 | Impacto del nuevo resultado canonico de E15 sobre lo ya escrito | E15 | quitar trailers |
| 75 | `1a58376` | 2026-09-04 07:08 | Ausencia de correspondencia de senal, declarada en vez de silenciada | — | quitar trailers |
| 76 | `f290263` | 2026-09-04 07:09 | Politica de evaluacion no oracular y adversa, congelada antes de medir | — | quitar trailers |
| 77 | `43f56dc` | 2026-09-04 07:11 | Modos no oracular y adverso del experimento de suficiencia | — | quitar trailers |
| 78 | `3b02cf8` | 2026-09-04 07:12 | Corregir el nombre de artefacto en el mensaje final del runner | — | quitar trailers |
| 79 | `f34f625` | 2026-09-04 07:14 | Enmienda ENM-A01: el escenario adverso elige el error mas confiado | ENM-A01 | quitar trailers |
| 80 | `c502f9a` | 2026-09-04 07:14 | Aplicar ENM-A01 y congelar la primera ejecucion adversa | ENM-A01 | quitar trailers |
| 81 | `465563a` | 2026-09-04 07:17 | Resultados NX-01 y NX-02, y hallazgo EMPTY-DTC-GATE-BYPASS | NX-01, NX-02 | quitar trailers |
| 82 | `9139dcd` | 2026-09-04 07:38 | Politica de la puerta de DTC, documentada antes de implementarse | — | quitar trailers |
| 83 | `4c17732` | 2026-09-04 07:39 | Puerta de DTC con requisito explicito (v2.2), IMPLEMENTED sin ejecutar | — | quitar trailers |
| 84 | `0292f72` | 2026-09-04 11:02 | Decisiones del autor tras las cinco auditorias, y lineas base | — | quitar trailers |
| 85 | `3964961` | 2026-09-04 11:04 | Condicion distractor invalidada, rediseno adversarial y refutacion del filtro de motor | — | quitar trailers |
| 86 | `7a3ef51` | 2026-09-04 11:05 | Pruebas de v2.2 en las ocho categorias exigidas, y una correccion que destaparon | — | quitar trailers |
| 87 | `54071a2` | 2026-09-04 12:58 | Politica de aislamiento del espacio de embeddings, antes de tocar codigo | — | quitar trailers |
| 88 | `c6a95be` | 2026-09-04 12:59 | Pruebas que reproducen MIXED-EMBEDDING-SPACE, y artefactos congelados | — | quitar trailers |
| 89 | `43e2e87` | 2026-09-04 13:04 | Corregir MIXED-EMBEDDING-SPACE: el espacio se deriva del proveedor | — | quitar trailers |
| 90 | `6b5b92d` | 2026-09-04 13:04 | Plan de reejecucion canonica, pendiente del gate de diseno | — | quitar trailers |
| 91 | `3845c07` | 2026-09-04 13:59 | Pre-registro de RERUN-A, congelado antes de cualquier medicion | RERUN-A | quitar trailers |
| 92 | `b79dfa7` | 2026-09-04 14:03 | Plan corregido y estados provisionales del ciclo | — | quitar trailers |
| 93 | `7ff9949` | 2026-09-04 16:28 | Correcciones de los tres gates: procedencia, conjunto acotado y ENM-S01 | ENM-S01 | quitar trailers |
| 94 | `df003f0` | 2026-09-04 16:56 | Mapa congelado, manifiesto de estado y ENM-S02 | ENM-S02 | quitar trailers |
| 95 | `57b6c93` | 2026-09-04 17:08 | Corregir el mapa congelado: omitia F04_o2_lag | — | quitar trailers |
| 96 | `aed6fe2` | 2026-09-04 17:12 | Cerrar residuos: la tabla legacy sale de la columna «antes» | — | quitar trailers |
| 97 | `7d52627` | 2026-09-04 18:39 | ENM-S03 y el dispositivo como quinta variable | ENM-S03 | quitar trailers |
| 98 | `9c388d9` | 2026-09-10 00:46 | Memoria: resolver las marcas editoriales y separar las preguntas al director | — | SHA nuevo (descendiente) |
| 99 | `1d61772` | 2026-09-10 00:47 | Objetivos: desarrollar OE4 con sus cuatro fases y el estado real de sus metricas | OE4 | SHA nuevo (descendiente) |
| 100 | `191bd84` | 2026-09-10 00:48 | Formalizar el Mazda 3 BK 2007 como vehiculo de referencia | — | SHA nuevo (descendiente) |
| 101 | `a80f14a` | 2026-09-10 00:49 | Conclusiones: L-17, los resultados describen un solo vehiculo | — | SHA nuevo (descendiente) |
| 102 | `77281a9` | 2026-09-10 00:50 | Marco teorico: desarrollar los cuatro frentes y cerrar cada uno con su limite | — | SHA nuevo (descendiente) |
| 103 | `2550bc1` | 2026-09-10 00:57 | Verificar cuatro referencias en fuente primaria: una no sostiene lo citado | — | SHA nuevo (descendiente) |
| 104 | `e2151ca` | 2026-09-10 00:58 | Matriz de alineacion, y corregir la asignacion de subpreguntas en OE4 | OE4 | SHA nuevo (descendiente) |
| 105 | `701f1c4` | 2026-09-10 01:07 | OE4: corregir los hallazgos de la auditoria experimental y estadistica | OE4 | SHA nuevo (descendiente) |
| 106 | `d0866ce` | 2026-09-10 01:16 | OE4, iteracion 2: corregir lo que la reevaluacion encontro, incluido lo mio | OE4 | SHA nuevo (descendiente) |
| 107 | `6b65345` | 2026-09-10 06:45 | Objetivos: ajustar el capitulo a las 3 paginas que recomienda la plantilla | — | SHA nuevo (descendiente) |
| 108 | `dc12963` | 2026-09-10 06:47 | Objetivos: recuperar OE5, que el traslado se habia llevado, y corregir su presentacion | OE5 | SHA nuevo (descendiente) |
| 109 | `f210021` | 2026-09-10 06:49 | Memoria: retirar las referencias a la plantilla del cuerpo del texto | — | SHA nuevo (descendiente) |
| 110 | `94a08e4` | 2026-09-10 06:56 | Marco teorico: corregir una atribucion que contradecia a sus dos fuentes | — | SHA nuevo (descendiente) |
| 111 | `4223508` | 2026-09-10 06:58 | Memoria: sacar los bloques de estado editorial del cuerpo de los capitulos | — | SHA nuevo (descendiente) |
| 112 | `4a87700` | 2026-09-10 07:02 | OE4: voz academica en lugar de inventario de fases, y terminologia de validacion | OE4 | SHA nuevo (descendiente) |
| 113 | `ae9dfc3` | 2026-09-10 07:04 | Conclusiones: acotar el «si puede» a lo que la evidencia sostiene | — | SHA nuevo (descendiente) |
| 114 | `a0cc296` | 2026-09-10 07:05 | Conclusiones: acotar la mitad de trazabilidad y declarar dos negativos no reportados | — | SHA nuevo (descendiente) |
| 115 | `0c519fe` | 2026-09-10 07:10 | Declarar en la memoria el hallazgo que congela las cifras de recuperacion | — | SHA nuevo (descendiente) |
| 116 | `2903ecb` | 2026-09-10 07:11 | Resultados: declarar las cinco discrepancias y el oraculo de la comparacion | — | SHA nuevo (descendiente) |
| 117 | `5e87ae8` | 2026-09-10 07:14 | Bibliografia: propagar las verificaciones a la lista maestra y corregir el apellido | — | SHA nuevo (descendiente) |
| 118 | `76e1046` | 2026-09-10 07:27 | Resultados: alinear las subpreguntas con el estado real y retirar la defensa doble | — | SHA nuevo (descendiente) |
| 119 | `0f5e3b0` | 2026-09-10 12:33 | Memoria: sustituir el lenguaje metadocumental por lenguaje de metodo | — | SHA nuevo (descendiente) |
| 120 | `b5ca3b3` | 2026-09-10 12:39 | Memoria: corregir el capitulo 1 y alinear los estados de fase con el indice | — | SHA nuevo (descendiente) |
| 121 | `32c6a7d` | 2026-09-10 12:40 | Bibliografia: transcribir los datos que la lista maestra ya tenia | — | SHA nuevo (descendiente) |
| 122 | `b0e13e2` | 2026-09-10 12:40 | Fichero de citas: desambiguar las claves repetidas | — | SHA nuevo (descendiente) |
| 123 | `0400ed2` | 2026-09-10 12:42 | Politica de expresion academica del TFM, vinculante | — | SHA nuevo (descendiente) |
| 124 | `835a317` | 2026-09-10 12:51 | Registrar SD-01: dos preguntas de investigacion en circulacion, con evidencia | — | SHA nuevo (descendiente) |
| 125 | `5a61194` | 2026-09-10 12:53 | Inventario del trabajo para la revision integral | — | SHA nuevo (descendiente) |
| 126 | `615ebeb` | 2026-09-10 12:53 | Matriz de trazabilidad de la pregunta, con sus cinco huecos | — | SHA nuevo (descendiente) |
| 127 | `4a0c6d8` | 2026-09-10 12:54 | Objetivos: ajustar al limite de la plantilla | — | SHA nuevo (descendiente) |
| 128 | `d0fa412` | 2026-09-10 13:04 | Cerrar cuatro observaciones del tutor y ajustar el capitulo 2 a la plantilla | — | quitar trailers |
| 129 | `cc7eefd` | 2026-09-10 13:05 | Registro de correcciones: iteracion 3 | — | quitar trailers |
| 130 | `456e9a0` | 2026-09-10 13:23 | Objetivos: apertura con funcion metodologica en lugar de descripcion del documento | — | quitar trailers |
| 131 | `1d368e0` | 2026-09-10 13:26 | Introduccion: la presentacion presenta, y la trazabilidad se va a metodologia | — | quitar trailers |
| 132 | `32e7c99` | 2026-09-10 13:31 | Resumen: reescrito segun la plantilla, con abstract en ingles | — | quitar trailers |
| 133 | `038c20c` | 2026-09-10 13:42 | Resumen del autor, y la comprobacion del ciclo de la pregunta | — | quitar trailers |
| 134 | `6f0e21d` | 2026-09-10 14:06 | Introduccion: 1.2 con el orden del argumento y la pregunta completa | — | quitar trailers |
| 135 | `12b665a` | 2026-09-10 14:12 | Objetivos: los objetivos concretan la pregunta, no la transforman | — | quitar trailers |
| 136 | `d7bdaef` | 2026-09-10 14:17 | Objetivos: objetivo general alineado con la pregunta, y fuera la historia editorial | — | quitar trailers |
| 137 | `6515210` | 2026-09-10 14:40 | Objetivos especificos reescritos, y las dos capacidades sin instrumentar declaradas | — | quitar trailers |
| 138 | `d3ddde8` | 2026-09-10 15:06 | Marco teorico: agosto como metodologia, y fuera los resultados propios | — | quitar trailers |
| 139 | `c395368` | 2026-09-10 15:07 | Marco teorico: lo que la revision puede sostener, y no mas | — | quitar trailers |
| 140 | `43e1151` | 2026-09-10 15:15 | Marco teorico: precision en 3.1 y declaracion del alcance de PRISMA | — | quitar trailers |
| 141 | `521123c` | 2026-09-10 16:05 | Marco teorico: teoria en el capitulo 3, metodo en el 4, y que es un patron no representado | — | quitar trailers |
| 142 | `6f7ec0f` | 2026-09-10 17:20 | Normalizar tablas y figuras, y dejar el criterio en un skill | — | quitar trailers |
| 143 | `c617d14` | 2026-09-10 18:47 | Poblacion y muestra: prosa academica, y el resultado de ventana fuera del metodo | — | quitar trailers |
| 144 | `5e7f95d` | 2026-09-10 18:49 | Primera entrega: diagnostico, informe de preparacion y niveles de agregacion | — | quitar trailers |
| 145 | `66198d9` | 2026-09-10 22:35 | Objetivos alcanzan la pregunta, y se disena lo que falta para ejecutarlos | — | quitar trailers |
| 146 | `3d7ab90` | 2026-09-11 03:52 | Memoria: un parrafo, una linea | — | quitar trailers |
| 147 | `e7aeb14` | 2026-09-11 04:13 | Muestra: caracterizacion legible, y las doce senales con su propia tabla | — | quitar trailers |
| 148 | `95d4e71` | 2026-09-11 05:08 | Fase de recuperacion: informacion documental, no evidencia todavia | — | quitar trailers |
| 149 | `6d95a25` | 2026-09-11 05:17 | Fases del agente: diseno en el capitulo 4, incidentes en el 5 | — | quitar trailers |
| 150 | `e4dfdf1` | 2026-09-11 05:44 | Reproducibilidad: separada del control de calidad, y la huella dice sobre que se calcula | — | quitar trailers |
| 151 | `4cac4ae` | 2026-09-11 05:49 | Modelo de analisis: analisis, no resultados previstos | — | quitar trailers |
| 152 | `cd52cdb` | 2026-09-11 05:51 | Marco teorico: romper la enumeracion formulaica de las cinco situaciones | — | quitar trailers |
| 153 | `37f1294` | 2026-09-11 05:54 | Conclusiones: alineadas con la pregunta, y sin el exceso de forma | — | quitar trailers |
| 154 | `0b0864b` | 2026-09-11 05:57 | Introduccion: deshacer un eco entre parrafos contiguos | — | quitar trailers |
| 155 | `8be7fc2` | 2026-09-11 06:04 | Conclusiones provisionales para la primera entrega | — | quitar trailers |
| 156 | `4e9e4a6` | 2026-09-11 06:05 | Conclusiones: ritmo y ultimo conector de apertura | — | quitar trailers |
| 157 | `daddffd` | 2026-09-11 06:11 | Separar prospectiva de trabajo pendiente dentro del TFM | — | quitar trailers |
| 158 | `4a6358b` | 2026-09-11 07:00 | Marco teorico: reescribir el proposito y procedimiento de la revision | — | quitar trailers |
| 159 | `9bb8c6c` | 2026-09-11 07:11 | Fijar la voz de referencia del TFM y aplicarla donde mas se desviaba | — | quitar trailers |
| 160 | `23208b0` | 2026-09-11 07:14 | Marco teorico: aplicar la voz de referencia a todo el capitulo | — | quitar trailers |
| 161 | `e5242d0` | 2026-09-11 07:17 | Marco teorico: moderar el vaiven del proposito y procedimiento | — | quitar trailers |
| 162 | `8220261` | 2026-09-11 07:34 | Fijar el criterio de escritura del TFM | — | quitar trailers |
| 163 | `fad82f6` | 2026-09-11 07:40 | Marco teorico: devolver al proposito y procedimiento su registro denso | — | quitar trailers |
| 164 | `03ab04f` | 2026-09-11 07:43 | Marco teorico: registro denso en todo el capitulo | — | quitar trailers |
| 165 | `0505a2b` | 2026-09-13 11:17 | Observaciones del tutor: lo que no depende de la decision sobre la pregunta | — | quitar trailers |
| 166 | `4cb4de5` | 2026-09-13 11:24 | ADR-004: la pregunta canonica es la acotada, decidido por la direccion | ADR-004 | quitar trailers |
| 167 | `089d48f` | 2026-09-13 11:36 | Cerrar el feedback del tutor tambien fuera de la memoria | — | quitar trailers |
| 168 | `636cf15` | 2026-09-13 12:27 | Retirar las marcas de trabajo del capitulo 4 y documentar las del 5 | — | quitar trailers |
| 169 | `167e17e` | 2026-09-13 13:16 | Registro denso en los dos apartados que quedaban | — | quitar trailers |
| 170 | `3b001d4` | 2026-09-13 17:35 | Introduccion: anunciar el vacio, que solo vivia en el capitulo 3 | — | quitar trailers |

Resumen: 69 commits con trailers a eliminar; 30 commits sin trailers que reciben SHA nuevo por
descender de los anteriores; 71 commits intactos.

## Commits nuevos

Pendiente. Se registrarán aquí los commits de la Fase 5 (`docs/commit-plan.md`) con su SHA
definitivo.

| SHA | Tipo | Descripción |
|-----|------|-------------|
| — | — | (sin ejecutar) |

## Commits históricos modificados

Pendiente. Tras la reescritura se volcará aquí el mapa completo `SHA anterior → SHA nuevo`
que produce `git filter-repo` (`.git/filter-repo/commit-map`), 99 filas.

| SHA anterior | SHA nuevo | Motivo |
|--------------|-----------|--------|
| — | — | (sin ejecutar) |

## Metadatos eliminados

Pendiente. Previsto: exactamente 69 líneas `Co-Authored-By: Claude Opus 5 (1M context)
<noreply@anthropic.com>` y 69 líneas `Claude-Session: https://claude.ai/code/session_…`
(26 con `session_01BxABErdF9ssaDxuxRUb1Dk`, 43 con `session_01J6War2vaULRmaHQZYtffHr`).
Ningún comentario de código: no existe ninguno que eliminar (auditoría §3.2).

## Cambios deliberadamente conservados

Referencias a IA/LLM que permanecen por ser parte del sistema o del registro científico
(detalle y clasificación en `docs/git-history-audit.md` §3.2):

- `LLMProviderName` con el valor `anthropic` en `src/mecanico_ia_exp/config/settings.py` y su
  documentación en `.env.example` y `docs/setup/llm-providers.md`: son los proveedores de modelo
  de lenguaje que el sistema puede consumir.
- El rol `assistant` del protocolo de chat en `llm/agent.py` y `llm/training_data.py`.
- El título de la referencia REF-107 («LLM-Based Automotive Assistant») en la bibliografía.
- Los informes de revisión y auditoría de `docs/tfm/revision/`, `docs/audits/`,
  `tutor-reports/` y el inventario `research/available-skills.md`, que declaran qué
  herramientas de revisión se usaron y cuándo. Son registro histórico del proceso y los
  commits posteriores se remiten a ellos.

## Validación

Pendiente de ejecución (Fase 8). Comandos definidos por el proyecto
(`docs/EXPERIMENTO_PASO_A_PASO.md:452`, `docs/setup/macos-local.md:80-83`):

```
uv sync --all-extras
uv run ruff check .
uv run ruff format --check src tests
uv run mypy src
uv run pytest
```

Tests: — · Lint: — · Types: — · Build: —

## Estado final

Pendiente: `git status` y `git log --graph --decorate --oneline` tras la ejecución.

## Rollback

Instrucciones válidas ya, con el backup actual:

```
cd mecanico-ia-exp
git checkout main
git reset --hard backup/pre-history-cleanup-20260913-1815
git remote add origin https://github.com/3dluis/-mecanico-ai-exp.git   # solo si filter-repo lo eliminó
```

Esto devuelve `main` exactamente a `3b001d4` con su historial original. Los ficheros nuevos
sin confirmar (borradores de esta entrega) no se ven afectados por el `reset` salvo que se
hayan confirmado; en ese caso quedarán en el reflog y en la rama de archivo.
