# 06 · Auditoría de referencias — resumen consolidado

**Skill:** `tfm-reference-auditor`, modo `/ref-audit-full` + `/ref-recheck` ·
**Informe completo:** `reference-reports/REFERENCE-AUDIT-20260903.md` (28 secciones, 179
fichas, diecisiete preguntas del veredicto) · **Registro persistente:**
`reference-reports/verification-register.json` · **Instantánea:** `mecanico-ia-exp`, 3 de
septiembre de 2026 · **Lectura únicamente**, ningún fichero del repositorio modificado.

## Veredicto

**`BLOCKED`.** Cuatro hallazgos `MAJOR` abiertos, ninguno `CRITICAL`. Dos gates bloqueados:
integridad cita ↔ referencia (03) y validación de referencias críticas (14). El bloqueo no
procede de una bibliografía defectuosa: procede de dos entradas del vacío que no identifican
la obra que sí existe, de cuatro fuentes verificadas que sostienen el vacío de PI.4 y no
están citadas ni en la bibliografía, y de una entrada del corpus que ningún registro
consultado localiza.

**Lo que no está en discusión.** Cero referencias inexistentes, cero DOI rotos, cero DOI que
resuelvan a otra obra, cero metadatos compuestos, cero fuentes retractadas, cero citas sin
entrada y cero entradas de la bibliografía de depósito sin cita. En las 137 fichas con
registro externo no hay ni un `TITLE_MISMATCH`, ni un `AUTHOR_MISMATCH`, ni un
`VENUE_MISMATCH`. La norma con sanción más dura de la UAX —«fuentes inexistentes pueden
suponer un no apto»— no está incumplida en ninguna referencia citada.

`APA_VERSION = 6` (plantilla oficial), con `UAX-RULE-CONFLICT-03` **registrado y no
resuelto**: la decisión entre APA 6.ª y 7.ª corresponde al autor con el director y cambia el
veredicto de uno de los hallazgos.

## Gates (REF-GATE-01..14)

| Gate | Estado |
|---|---|
| 06 identificadores · 02 extracción de citas · 09 localización de citas textuales | PASS |
| 01 fuente de verdad · 04 existencia · 05 metadatos · 07 duplicados · 08 APA · 10 estado de acceso · 11 versiones · 12 legacy y excluidas · 13 trazabilidad | PASS_WITH_OBSERVATIONS |
| **03 integridad cita ↔ referencia** | **BLOCKED** (REF-MAJ-011) |
| **14 validación de referencias críticas** | **BLOCKED** (REF-049 y REF-106 en L2) |

## Recuentos

| Magnitud | Valor |
|---|---|
| Fichas en el registro | **179** (144 `REF` + 19 `MET` + 5 fichas de las 4 obras de GAP-02 + 11 de la propuesta aprobada) |
| Referencias citadas en la memoria | **39** (20 `REF` + 19 `MET`), en 70 citas |
| **Verificadas** (`VERIFIED`, L3) | **133** — de ellas 36 citadas |
| **Parcialmente verificadas** (`PARTIALLY_VERIFIED`) | **37** — 33 entradas sin identificador con existencia confirmada por búsqueda, MET-19, GAP-02/03/04 |
| **No verificadas** (`UNVERIFIED`) | **9** — REF-051 y 8 de la propuesta aprobada |
| **No encontradas** (`NOT_FOUND`) | **0** |
| `CONFLICTING_METADATA` | **0** |
| **Duplicadas** | **2 pares** — REF-117/REF-119 · REF-070/MET-10 |
| **Huérfanas** | **0** en la bibliografía de depósito (124 entradas de la maestra sin citar son legacy con control pendiente) |
| **Citas sin entrada** | **0** |
| **DOI rotos** | **0** (89 DOI resueltos, 47 identificadores de arXiv, 0 malformados, 0 duplicados) |
| **Discrepancias de metadatos** | **3** — REF-049 (título parafraseado) · REF-106 (título truncado) · REF-034 (año no declarado) |
| Niveles de verificación | L3 137 · L2 33 · L1 9 · **L4 0** |
| Referencias críticas | **29**, de ellas 27 en L3 y 2 en L2 |

## Referencias problemáticas, una a una

| Referencia | Problema |
|---|---|
| **REF-049** Hossain et al. (2024) | Título parafraseado, autores incompletos, sin DOI ni páginas. Sostiene el vacío. L2 |
| **REF-106** Shuster et al. (2021) | Título truncado, autores incompletos, sin DOI ni páginas; entrada de depósito sin ID. Sostiene el vacío. L2 |
| **REF-051** Huang et al. (2025) «POPPER» | Única de las 144 sin existencia confirmada: la entrada da el acrónimo por título y no hay identificador; sin coincidencia en Crossref ni DataCite. No citada. L1 |
| **GAP-01..GAP-04** (Chen et al. 2024 RGB; Cuconasu et al. 2024; Amiraz et al. 2025; Wallat et al. 2024) | Verificadas en L3 y **fuera de toda bibliografía**; sostienen la afirmación de `docs/memoria/cap3_marco_teorico.md` l.213-218, que no cita ninguna fuente |
| **REF-070** ↔ **MET-10** Lewis et al. (2020) | Misma obra bajo dos IDs en las dos listas maestras; MET-10 citada y verificada, REF-070 sin identificador y sin citar |
| **REF-117** ↔ **REF-119** Wang et al. (2024) | Duplicado exacto: mismo título, mismo autor, mismo año, mismo identificador candidato. Ninguna citada |
| **REF-034** Fu et al. | Año 2025 en las tres vistas del proyecto, 2026 en Crossref; no figura entre las 7 discrepancias declaradas |
| **REF-039, REF-061** | El «año del registro» anotado en la tabla de discrepancias ya no es el que devuelve Crossref, que hoy coincide con el año citado |
| **REF-133** Yeh et al. | Tres años en juego: 2016 citado, 2017 en la lista y el bib, 2018 en el registro |
| **REF-015, REF-016, REF-066** | Preprints con versión publicada localizada; REF-016 con el orden de autores invertido respecto al registro; REF-066 con la publicada (2022) anterior al preprint citado (2023) |
| **REF-059, REF-071, REF-074, REF-097** | El depósito marca `[VERIFY_SOURCE: tomar de REF-NNN]` sobre DOI que la maestra ya trae verificados; REF-059 y REF-097 además sin revista, volumen ni DOI en el depósito |
| **MET-19** ISO 15031-5 | Sin año ni edición en la lista de método y en el depósito. La propuesta aprobada aporta «2015», pendiente de confirmar |
| **MET-18** SAE J1979-DA | Falso positivo del script (autor corporativo frente a comité redactor). Sin defecto |
| **PROP-01, 02, 03, 07, 08, 09, 10, 11** | Ocho referencias de un documento oficial entregado a la universidad, sin entrada bibliográfica, sin identificador y sin decisión de incorporación o descarte |
| Claves `Chen2024`, `Wang2023`, `Wang2024` | 7 colisiones de clave BibTeX en 9 entradas |

## Hallazgos

Severidad en la escala del encargo: CRITICAL→BLOCKER, MAJOR→MAJOR, MINOR→MODERATE,
INFO→MINOR (COSMETIC si es puro formato). **Ninguno es BLOCKER.** Los identificadores
`REF-MAJ-001`, `REF-MAJ-002` y `REF-MIN-003..010` se conservan del informe anterior
`REFERENCE-DRY-RUN-01`; los nuevos siguen la numeración correlativa desde 011.

| ID | Severidad | Archivo | Sección/línea | Problema | Evidencia | Corrección propuesta | Riesgo | Estado |
|---|---|---|---|---|---|---|---|---|
| REF-MAJ-001 | MAJOR | `research/references/references.md`; `docs/memoria/bibliografia.md`; `docs/memoria/cap1_introduccion.md`; `docs/memoria/cap3_marco_teorico.md` | references l.87 y l.226; bibliografia l.36; cita cap1 l.17 y cap3 l.63-64 | REF-049 (referencia del vacío) tiene el título parafraseado, «Hossain et al.» por autores y ningún identificador; la entrada del depósito conserva «et al.» en el campo de autor, que ninguna versión de APA admite | Crossref, 3 sep 2026 (repetido): `10.32604/cmes.2024.056022` → «Artificial Intelligence-Driven Vehicle Fault Diagnosis to Revolutionize Automotive Maintenance: A Review», Hossain, Rahman, Ramasamy, *CMES* 141(2), 951-996 | Adoptar título, tres autores, páginas y DOI del registro, con `[VERIFY_SOURCE]` hasta cotejarlo con la primera página del artículo | La obra existe y el venue, volumen, número y año coinciden: el riesgo no es de fabricación sino de no poder localizarla por título exacto | **NOT_FIXED** (del dry-run) |
| REF-MAJ-002 | MAJOR | `research/references/references.md`; `docs/memoria/bibliografia.md`; `cap1`; `cap3` | references l.144 y l.237; bibliografia l.84 (sin ID); cita cap1 l.30 y cap3 l.127 | REF-106 (referencia del vacío) con título truncado, «Shuster et al.» por autores, sin DOI ni páginas y sin ID en la entrada del depósito | Crossref, 3 sep 2026 (repetido): `10.18653/v1/2021.findings-emnlp.320` → «Retrieval Augmentation Reduces Hallucination in Conversation», Shuster, Poff, Chen, Kiela, Weston, *Findings of ACL: EMNLP 2021*, 3784-3803 | Completar título, cinco autores, páginas y DOI; asignar ID a la entrada del depósito | Sostiene con REF-016 y MET-15 la afirmación de cap1 l.30; identificable hoy solo por título parcial | **NOT_FIXED** (del dry-run) |
| REF-MAJ-011 | MAJOR | `docs/memoria/cap3_marco_teorico.md`; `research/references/search-log.md`; `research/references/references.md`; `docs/memoria/bibliografia.md` | afirmación en cap3 l.213-218; fuentes en search-log § Iteración 5 | La afirmación «existen trabajos sobre robustez de la recuperación a documentos irrelevantes en dominios generales» —el pasaje que estrecha el vacío de PI.4— no cita ninguna fuente, y las cuatro obras que lo documentan no están en la lista maestra, ni en el bib, ni en la bibliografía de depósito, ni citadas en ningún capítulo | Crossref y DataCite, 3 sep 2026: `10.1609/aaai.v38i16.29728` (Chen, Lin, Han, Sun, 2024, AAAI 38(16), 17754-17762; preprint `arXiv:2309.01431`) · `arXiv:2401.14887` · `arXiv:2505.06914` · `arXiv:2412.18004`. Las cuatro en L3 | Incorporarlas a la lista maestra con ID propio y a la bibliografía, y citarlas en el pasaje del vacío, tras leerlas a texto completo `[VERIFY_SOURCE]` | Es la afirmación de novedad más discutible del trabajo y hoy no tiene apoyo bibliográfico visible; el propio proyecto concluyó que citarlas «hace el trabajo comparable; no citarlo lo aísla» | OPEN |
| REF-MAJ-012 | MAJOR | `research/references/references.md`; `research/references/bibliography.bib`; `research/references/source-index.md` | references l.89 y l.227; entrada `Huang2025` del bib | REF-051 «Huang et al. (2025). POPPER. ICML 2025, PMLR 267» no aporta título de obra ni identificador, y no aparece en ninguno de los tres registros consultados. Es la única de las 144 cuya existencia no se ha podido confirmar | Crossref `query.bibliographic` (dos cadenas), DataCite (dos consultas por título y autor), API de arXiv (`au:Huang AND ti:Popper`); todas sin coincidencia. arXiv devolvió HTTP 429 el 3 de septiembre | Consultar las actas PMLR de ICML 2025 —registro adecuado al tipo, no consultado aquí— y registrar título, autores e identificador; si no se localiza, retirarla del corpus con motivo escrito | No está citada, de modo que no compromete ningún capítulo hoy. **No se afirma fabricación**: la búsqueda no está agotada y la evidencia acumulada no la sostiene | OPEN |
| REF-MIN-003 | MODERATE | `docs/memoria/bibliografia.md` | 8 marcas en 4 entradas (REF-059, 071, 074, 097) | El depósito marca `[VERIFY_SOURCE: tomar de REF-NNN]` sobre datos que la maestra y el bib ya traen | `compare_sources.py`: 8 filas `VERIFY_SOURCE_WHILE_MASTER_HAS_IDENTIFIER`; los cuatro DOI verificados en L3 | Completar el depósito desde la maestra | La bibliografía de depósito aparenta menos verificación de la que el proyecto tiene | **NOT_FIXED** |
| REF-MIN-004 | MODERATE | `research/references/references.md`; `docs/memoria/bibliografia.md` | REF-016 (y, por el mismo patrón, REF-015 y REF-066) | Se cita el preprint existiendo versión publicada; en REF-016 el registro invierte el orden de autores | Crossref: `10.18653/v1/2024.naacl-industry.19` (Ayala, O.; Bechard, P.; pp. 228-238) · `10.1109/Humanoids65713.2025.11203101` · `10.1109/ITSC55140.2022.9922158` | Citar la publicada e indicar el preprint solo si fue lo consultado; confirmar el orden de autores | En REF-015 la corrección resuelve además una de las 7 discrepancias de año | **NOT_FIXED**, ampliado |
| REF-MIN-005 | MODERATE | `research/references/references.md`; `research/references/bibliography.bib` | REF-117 y REF-119 | Duplicado exacto: misma obra con dos IDs | `detect_duplicates.py` (título normalizado idéntico) **y** mismo identificador candidato `10.18653/v1/2024.acl-long.511` en ambas fichas | Conservar una; la maestra tiene 143 obras distintas, no 144 | Ninguna está citada: no infla ningún recuento publicado, sí el de la lista | **NOT_FIXED**, reforzado |
| REF-MIN-006 | MODERATE | `research/references/bibliography.bib` | l.210/219, 1227/1238/1248/1288, 1260/1269/1279/1300 | 7 colisiones de clave BibTeX en 9 entradas (`Chen2024`, `Wang2023`, `Wang2024`) | `bib_parse.py` | Renombrar solo si el bib se va a compilar; las claves no se renombran por iniciativa del auditor | MODERATE mientras nada cite por clave; pasa a MAJOR en cuanto se compile con LaTeX o pandoc | **NOT_FIXED** |
| REF-MIN-007 | MODERATE | `research/references/referencias-metodo.md`; `docs/memoria/bibliografia.md` | MET-19 | ISO 15031-5 sin año ni edición; APA exige año | El DOI BSI `10.3403/30301556` resuelve a la norma; la propuesta aprobada cita «ISO 15031-5:2015» | Fijar la edición con ese dato, `[VERIFY_SOURCE: confirmar en el organismo]` | Es una de las dos normas que sostienen la descripción del protocolo en cap1 y cap3 | **NOT_FIXED**, con dato nuevo |
| REF-MIN-008 | COSMETIC | `docs/memoria/bibliografia.md` | 38 entradas | «&» en la bibliografía frente a «y» en el texto y en la plantilla | lectura | Unificar según APA 6.ª en español | Formato; no afecta a la identificación | **NOT_FIXED** |
| REF-MIN-009 | MODERATE | `research/legacy-map.md`; `research/references/references.md` | LEG-D01 (`PARCIAL`); todas las decisiones en `PENDIENTE` | Las 144 entradas proceden del marco legacy y la maestra exige el control de relevancia «antes de citarse»; no consta para ninguna de las 20 citadas | lectura de `legacy-map.md` | Registrar la decisión de importación por referencia citada | Un tribunal puede preguntar por qué se cita material de un marco anterior sin control documentado | **NOT_FIXED**, ampliado a las 144 |
| REF-MIN-010 | MODERATE | `docs/memoria/bibliografia.md` | entradas de Jun (REF-059) y Ramai (REF-097) | Sin revista, volumen ni DOI en el depósito, teniéndolos la maestra | comparación entre vistas | Completar desde la maestra | Formato y verificabilidad de la vista que se deposita | **NOT_FIXED** |
| REF-MIN-013 | MODERATE | `research/references/references.md`; `research/references/referencias-metodo.md` | REF-070 y MET-10 | Misma obra bajo dos IDs en las dos listas maestras; MET-10 citada en cap3 l.126, REF-070 sin identificador y sin citar | Identificador candidato de REF-070 (`arXiv:2005.11401`) idéntico al identificador verificado de MET-10 | Decidir cuál conserva el ID en la reconciliación 144/153 | Hoy no infla ningún recuento; al unir las dos listas se convertiría en duplicado exacto no declarado | OPEN |
| REF-MIN-014 | MODERATE | `research/references/references.md`; `research/references/bibliography.bib`; `research/references/source-index.md` | REF-034; tabla «Discrepancias de año» l.186-205 | REF-034 usa 2025 en las tres vistas y Crossref devuelve 2026: es una octava discrepancia no declarada. Además, en REF-039 y REF-061 el «año del registro» anotado ya no coincide con el registro actual, y REF-133 tiene tres años en juego | comparación ficha a ficha con el registro, 3 sep 2026 | Ampliar la tabla a 8 entradas y volver a fijar el criterio de año por entrada | Ninguna es referencia inventada: todas son ambigüedades online-first frente a número asignado. Ninguna está citada | OPEN |
| REF-MIN-015 | COSMETIC | `docs/memoria/cap1_introduccion.md`; `docs/memoria/cap3_marco_teorico.md` | cap1 l.17, 26, 30, 62, 87, 88; cap3 l.57, 78, 103 | «et al.» en la **primera** mención de trabajos con 3-5 autores en 10 citas (REF-002, 049, 062, 075, 086, 097, 106; MET-04, 16, 17); APA 6.ª obliga a nombrarlos todos la primera vez | recuento de autores desde el registro de cada ficha | Desarrollar los autores en la primera mención **o** resolver `UAX-RULE-CONFLICT-03` a favor de APA 7.ª, donde la forma actual es correcta | El hallazgo **desaparece** si el director opta por APA 7.ª: es una consecuencia del conflicto normativo, no un descuido | OPEN |
| REF-MIN-016 | MODERATE | `research/references/search-log.md`; `research/references/references.md` | search-log § Naturaleza del barrido; references § Qué falta, punto 3 | El recuento de preprints tiene cuatro cifras: 27 declaradas, 28 «al parsear», 32 tipadas `preprint` y 34 con identificador de arXiv; tres de ellas ya tienen versión publicada; REF-016 y REF-066 llevan arXiv y están tipadas «documento técnico» | recuento propio sobre las 144 entradas | Fijar criterio (tipo declarado o identificador) y fecha antes de declarar cualquier cifra en la memoria | La memoria no publica hoy ninguna de estas cifras: publica «144 referencias», que es correcta | OPEN |
| REF-MIN-017 | MODERATE | `references/project/propuesta-aprobada.md` (espejo del skill del investigador) | § Once referencias iniciales | Ocho de las once referencias del documento oficial entregado a la universidad siguen sin entrada bibliográfica, sin identificador y sin decisión: tres normas ISO, dos documentaciones de producto, un repositorio y dos conjuntos de datos | fichas `PROP-01..11` del registro: 3 verificadas en L3 por DataCite, 8 en L1 | Verificarlas en el registro adecuado a su tipo e incorporarlas o descartarlas con motivo escrito | Figuran en un documento oficial; un tribunal puede preguntar por ellas aunque no estén citadas | OPEN |
| REF-INF-018 | MINOR | herramientas compartidas del investigador | `validate_references.py`, `validate_citations.py` | Devuelven 38 huérfanas falsas y «0 citas detectadas» sobre esta memoria: comparan apellido y año y no leen los IDs inline ni las citas partidas entre líneas | ejecución de ambos scripts, 3 sep 2026 | Registrar la limitación; la regla compartida no se corrige desde la auditoría | El cribado heredado no sirve como evidencia de integridad en este proyecto | OPEN |
| REF-INF-019 | MINOR | `research/references/evidence-matrix.md` | fichero completo | Vacía por diseño: no existe cadena registrada claim → referencia, de modo que el traspaso al verificador se construye por lectura | lectura | Rellenarla al redactar cada sección, como el propio fichero declara | Coincide con `EVID-INF-010` del verificador de evidencia | CONFIRMADO |
| REF-INF-020 | MINOR | conflicto normativo `UAX-RULE-CONFLICT-03` | — | `APA_VERSION = 6` es provisional: la plantilla dice APA 6.ª y la sesión informativa menciona el estilo IEEE para el formato de página | registro de conflictos normativos | Confirmar con el director; **no se resuelve aquí** | Determina el veredicto de REF-MIN-015 | REGISTRADO |
| REF-INF-021 | MINOR | `reference-reports/verification-register.json` | ficha MET-18 | El script marcó `CONFLICTING_METADATA` al comparar «SAE International» con el comité redactor que devuelve Crossref | revisión: variante editorial de autor corporativo; título, año, editor e identificador coinciden | Ninguna: ficha revisada a `VERIFIED` con el estado del script conservado en el historial | Sin defecto | RESUELTO |
| REF-INF-022 | MINOR | `docs/memoria/` | figuras y tablas | Ninguna figura o tabla de los capítulos redactados reproduce material de terceros ni lleva línea «Fuente:» | lectura de cap1, cap3, cap4 y cap5 | Ninguna | Sin defecto; se hace constar para que no se lea como omisión | Sin defecto |

## Referencias críticas para el verificador de evidencia

29 referencias sostienen el vacío, la justificación del capítulo 1, el posicionamiento del
capítulo 3 o el diseño del capítulo 4. **27 en L3, 2 en L2.** El detalle con `CLAIM_ID` y
`SOURCE_LOCATION` está en el bloque `REFERENCE_AUDITOR_HANDOFF` del informe completo.

| Sostiene | Referencias | Nivel |
|---|---|---|
| Vacío, telemetría OBD-II (cap1 l.16-17; cap3 l.53-64) | REF-078, REF-098, REF-097 · **REF-049** | L3 · **L2** |
| Vacío, modelos de lenguaje sobre documentación de vehículo (cap1 l.25-26; cap3 l.137-141) | REF-072, REF-077, REF-086, REF-062 | L3 |
| Vacío, alucinación y su reducción (cap1 l.29-30; cap3 l.123-128) | MET-15, REF-016, MET-10 · **REF-106** | L3 · **L2** |
| Vacío de PI.4, rechazo de evidencia no pertinente (cap3 l.213-218) | GAP-01, GAP-02, GAP-03, GAP-04 — **verificadas y no citadas** | L3 |
| Método: diagnóstico, calibración y explicabilidad | MET-01 a MET-07 | L3 |
| Método: abstención y predicción selectiva | MET-08, MET-09 | L3 |
| Método: recuperación y modelo de lenguaje | MET-11 a MET-14 | L3 |
| Método: marco de investigación | MET-16, MET-17 | L3 |
| Protocolo OBD-II | MET-18 · MET-19 (sin edición) | L3 |

**Ninguna referencia alcanza L4.** El nivel L3 significa que el identificador resuelve y sus
metadatos coinciden; **no** significa que la fuente diga lo que se le atribuye. Esa pregunta
es del verificador de evidencia.

## Decisiones que corresponden al autor

1. **REF-049 y REF-106**: adoptar los metadatos del registro y completar las cuatro vistas.
2. **GAP-01 a GAP-04**: incorporarlas a la lista maestra y a la bibliografía, y citarlas en
   el pasaje del vacío de PI.4, tras leerlas a texto completo.
3. **REF-051**: consultar las actas PMLR de ICML 2025, o retirarla del corpus con motivo.
4. **Versión frente a preprint** en REF-015, REF-016 y REF-066, y orden de autores en REF-016.
5. **REF-117 / REF-119**: cuál se conserva. **REF-070 / MET-10**: cuál conserva el ID.
6. **Criterio de año** por entrada en las 7 discrepancias declaradas y en REF-034.
7. **Convención de IDs inline** `(Autor, año, REF-NNN)` en las 70 citas antes del depósito.
8. **APA 6.ª frente a 7.ª** (`UAX-RULE-CONFLICT-03`): determina el veredicto de REF-MIN-015.
9. **Control de relevancia legacy** por referencia citada.
10. **Reconciliación 144 frente a 153**: la aritmética de la unión da 161, no 153.
11. **Las 8 referencias pendientes de la propuesta aprobada**: incorporar o descartar.

## Fortalezas verificadas

- **Cero referencias inexistentes en 179 fichas.** 137 identificadores resueltos contra
  Crossref, DataCite o arXiv; ninguno devuelve «no encontrado», ninguno resuelve a otra obra,
  ninguno tiene aviso de retracción en el campo `update-to` de Crossref.
- **Cero discrepancias sustanciales de metadatos.** Ni un `TITLE_MISMATCH`, ni un
  `AUTHOR_MISMATCH`, ni un `VENUE_MISMATCH`, ni un caso de metadatos compuestos en las 137
  fichas con registro. Es lo que separa una bibliografía verificada de una plausible.
- **Correspondencia biunívoca completa** en la bibliografía de depósito: 39 citas, 39
  entradas, 0 huérfanas, 0 citas sin entrada, 0 ambigüedades autor-año, 0 sufijos a/b mal
  usados, 0 fuentes secundarias presentadas como directas, 0 citas textuales sin página.
- **El proyecto no inventa metadatos.** Las 34 entradas sin identificador siguen sin él,
  marcadas `[VERIFY_SOURCE]` campo a campo; el depósito marca lo que no tiene en lugar de
  rellenarlo. Es exactamente la conducta que la norma de la UAX premia.
- **El proyecto declara sus propias discrepancias** antes de que nadie se las señale: 144
  frente a 153, 27 frente a 28, las 7 de año, el bloqueo de acceso a dos bases y las tres
  lecturas pendientes.
- **Las 19 referencias de método están en L3** y citan la versión publicada cuando el
  registro no deposita DOI (PMLR, NeurIPS).
- **El registro de búsqueda documenta un vacío refutado y lo reporta como refutado**
  (iteración 5, GAP-02). Es la clase de traza que sostiene una defensa; lo que falta es su
  consecuencia bibliográfica, que es REF-MAJ-011.

## Limitaciones de esta auditoría

Ninguna referencia se verificó a texto completo (L4 = 0): se ha comprobado existencia,
identidad y metadatos, no contenido. El alcance de consulta se limitó a Crossref, DataCite y
la API de arXiv; no se consultaron IEEE, ACM, Springer, Elsevier, PMLR, ISO ni catálogos de
biblioteca, lo que deja `UNVERIFIED` —nunca `NOT_FOUND`— a REF-051 y a ocho referencias de la
propuesta. La API de arXiv devolvió HTTP 429 y 19 fichas se resolvieron por DataCite, con
reverificación pendiente. El control de relevancia legacy y el listado nominal de exclusiones
no existen todavía, de modo que la reintroducción de fuentes excluidas se reporta como **no
comprobable**, no como ausente.
