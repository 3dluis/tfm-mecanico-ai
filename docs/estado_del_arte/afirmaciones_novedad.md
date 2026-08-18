# Afirmaciones de novedad — clasificación para la redacción final

**TFM Mecánico IA · UAX · 2026-08-12.** Cada afirmación que la memoria pueda hacer sobre novedad o vacío, clasificada por su estado de defensa. Regla transversal: toda afirmación de ausencia se formula como "en la literatura analizada no se identificó…", nunca como inexistencia absoluta.

## A. Defendible actualmente (con el corpus verificado de ≈153 referencias)

A1. La formulación del **vacío integrador de cinco ejes** (§2.15.3): ningún antecedente identificado cubre más de tres ejes simultáneamente; la matriz de 15 antecedentes lo documenta componente a componente.

A2. **No se identificó ninguna comparación** entre detección de anomalías de salud vehicular condicionada a eventos operativos discretos y detección continua PID-a-PID (fundamento de C-EVT). CADD usa contexto continuo sin diagnóstico; Molina-Campoverde condiciona consumo, no salud; RAAD-LLM no es vehicular.

A3. **No se identificó ninguna memoria** que combine indexación por tipo de evento operativo, baseline histórico por unidad física y ejecución edge con capa de conocimiento validado (fundamento de la Event Memory dentro de C-MEM); las piezas existen por separado en robótica, TCBR, similarity-based prognostics e indexación de series, y así se citan.

A4. **No se identificó un ciclo de estados de evidencia** con validación previa a la consolidación aplicado a conocimiento diagnóstico declarativo y anclado en validación física (fundamento de C-MEM); los ciclos validados existentes operan sobre habilidades en benchmark (HDSO) o artefactos ejecutables (DS-Agent), y se citan como trabajos hermanos.

A5. La **reformulación de V6**: no consta arquitectura multiagente LLM en edge sobre telemetría OBD-II/powertrain viva con la cadena detección-RAG-hipótesis-verificación-memoria; siempre acompañada de la genealogía MAS (DDAS 2003, HoloMAS 2007) y de los multiagentes LLM no vehiculares (SAGE, LEMAD) y vehiculares de percepción (DriveAgent).

A6. La **formulación sobre datasets**: no existe dataset público identificado de telemetría OBD-II/CAN con clases de fallo mecánico confirmadas y etiquetadas; EngineAD aporta solo anomalías binarias anotadas por expertos sobre componentes PCA. (Defendible; conviene re-verificar la versión de EngineAD antes del depósito.)

A7. Las **condiciones de aplicabilidad de la descomposición multiagente** (síntesis de RQ16) como lectura original de evidencia ajena — es síntesis, no hallazgo empírico propio, y así debe presentarse.

## B. Condicionada al PRISMA formal (Scopus/WoS/IEEE con acceso institucional)

B1. La elevación de las afirmaciones A1–A5 de "en la literatura analizada (barrido web verificado)" a "en la literatura indexada consultada sistemáticamente". Hasta el PRISMA formal, mantener siempre la primera formulación.

B2. Cualquier cifra de cobertura ("X registros identificados en N bases") — actualmente solo existen los recuentos del barrido preliminar y así deben declararse.

B3. La consolidación definitiva de V1–V7 — condicionada además a la lectura a texto completo de Takara (ESWA 2025), Min (EAAI 2024) y Onsu (IoT 2025); si alguno cubre más componentes de los que muestran sus metadatos, se reajusta el vacío correspondiente.

## C. Condicionada a validación experimental (no afirmar como logro hasta tener resultados)

C1. Que la representación por eventos **reduce falsos positivos y mejora** la identificación de anomalías contextuales frente a punto/ventana en salud vehicular (hipótesis de E0–E4; la evidencia externa — CADD, WisCon, QCAD — la motiva pero no la demuestra en nuestro dominio y configuración).

C2. Que la **memoria evolutiva con validación mejora el diagnóstico** y evita la propagación de errores (hipótesis de la ablación de memoria y de los escenarios de propagación).

C3. Que la **descomposición multiagente aporta valor** frente al agente monolítico en nuestro contexto edge (hipótesis de A0–A6; compromiso explícito de reportar el resultado aunque favorezca al monolítico).

C4. Que el **perfil jerárquico por vehículo y evento supera** al modelo global y al individual puro (hipótesis de C-PERS).

C5. Que el pipeline completo **funciona end-to-end dentro del presupuesto edge** (latencia, RAM, t/s del SLM) — las mediciones parciales existentes son preliminares y en emulación.

C6. Que las **explicaciones verificadas alcanzan exactitud factual** superior a la generación no verificada (hipótesis de C-EXP; el antecedente de Mahale demuestra el riesgo, no nuestra solución).

C7. La **capacidad de descubrir y explicar patrones no documentados** (pregunta principal): solo defendible tras el protocolo held-out/open-set sobre datos, corpus RAG y memoria.

## D. No reclamar (la literatura ya lo cubre o la afirmación es indefendible)

D1. Novedad por **usar múltiples agentes** en diagnóstico/mantenimiento (Park, Lee, PARAM, MA-RCA, SAGE, LEMAD; genealogía DDAS/HoloMAS).

D2. Novedad del **esquema funcional multiagente+RAG+memoria+verificación en abstracto** (Jiang & Hu 2025 lo propone conceptualmente; nuestra diferencia es la instancia vehicular validada).

D3. Novedad de la **detección no supervisada de anomalías vehiculares** (Cherdo, Giannoulidis, Abboush, Geglio, EngineAD) ni de los algoritmos one-class empleados.

D4. Novedad del **concepto de anomalía contextual** (Chandola 2009) ni de la **normalidad condicionada al régimen en vehículos** (CADD 2024).

D5. Novedad del principio **"no consolidar sin validar"** (RETAIN de CBR, Voyager, DS-Agent, HDSO); lo defendible es la instancia de A4, no el principio.

D6. Novedad de la **detección de eventos/maniobras de conducción** (línea madura, E1–E9) ni de los métodos de segmentación (CPD, ClaSP, TICC, E2USD).

D7. Novedad del **RAG sobre documentación automotriz** (CarExpert/BMW, Nam, DeepTest) ni del uso de **LLM en diagnóstico** (Mahale, Lin & Miao, FD-LLM, LLMAD).

D8. Novedad de la **arquitectura edge-cloud** para mantenimiento (Bala, Jain, Huo, Syn-Diag) ni de la viabilidad de SLM/detectores en edge (Nguyen, E2USD, MLPerf Tiny).

D9. Cualquier variante de **"no existe ningún sistema similar"** en términos absolutos.

D10. Equiparar **anomalía estadística con fallo nuevo**: la definición de patrón no documentado exige recurrencia, ausencia de correspondencia documental y validación (§2.6.1); un outlier aislado nunca se reporta como descubrimiento.

D11. Presentar los resultados de la literatura sobre ventajas del multiagente como si aplicaran automáticamente a nuestro caso (las ablaciones de SAGE/MA-RCA son de otros dominios; nuestro caso se decide con A0–A6).

---

## Adenda v3 (2026-08-18) — remapeo al vacío central V\*

La alineación científica v3 sustituye V1–V7 por **V\*** con dimensiones S1–S6
(`docs/alineacion_v3/01_nucleo_cientifico.md` §3; correspondencia en
`docs/correspondencia_nomenclatura.md` §5). Efectos sobre esta clasificación:

- **A1 (vacío integrador de cinco ejes):** deja de usarse como argumento científico
  principal. Se conserva como observación de cobertura de la matriz de antecedentes
  (`docs/alineacion_v3/02_trazabilidad.md` §3): ningún trabajo revisado recorre la cadena
  detección→…→consolidación con open-set y evaluación conjunta. La novedad defendible es
  la **transición epistemológica evaluada**, no la integración tecnológica.
- **A2** sostiene S1 (contraste de H-EVT) · **A3–A4** sostienen S4 (memoria validada) ·
  **A5** sostiene S5 (condición habilitante; contribución solo si A0–A6 lo demuestra) ·
  **A6** sostiene S6 (banco held-out) · **A7** se mantiene como síntesis.
- **C7** pasa a enunciarse sobre la PI v3: la capacidad de *identificar un patrón no
  representado, reconocer la insuficiencia, hipotetizar, verificar y consolidar o
  abstenerse* solo será defendible tras EXP-MAIN-001 con la exclusión triple verificada.
- Regla de estilo v3: en documentos vivos se sustituye «literatura (analizada)» por
  «trabajos revisados/analizados» o «estado del conocimiento»; este fichero conserva su
  redacción original de 12-ago por ser documento fechado, y esta adenda fija el uso nuevo.
