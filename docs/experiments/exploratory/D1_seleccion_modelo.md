# D1 — selección del modelo de lenguaje local (instrumental, EXPLORATORIO)

**27 de agosto de 2026 · banco `cases_d1` (20 casos, semillas 60000–60019) · `cb:2` ·
Qwen2.5-3B-Instruct Q4_K_M · ollama 0.33.0 · macOS arm64**

Instrumental: no contrasta ninguna hipótesis y su resultado no se combina con evidencia
confirmatoria. Artefacto: `ai-models/experiments/d1/d1-selection.json`.

---

## 1. Por qué un banco nuevo

R2 dejó D1 sin fijar y propuso reevaluar sobre `cases_v2`. **Esa propuesta era incorrecta**:
`cases_v2` es el banco confirmatorio de `EXP-EVID-001`, y elegir el modelo por su rendimiento
en él sería selección sobre el conjunto de evaluación.

Se construye por tanto `cases_d1`, **disjunto**: bloque de semillas 60000–60019 (anomalías
70000–70019), sin intersección con suite v1 (101–322), benchmark v1 (31–9001), suite-v2
(11000–20036), `cases_v2` y variantes (30000–30079, anomalías 40000–40039), `sequences_v1`
(55000) ni suite-v2-multi. Generador determinista: `tools/gen_cases_d1.py`.

**Composición:** 15 casos con fallo (3 por cada mecanismo conocido) y 5 normales. El
`input_context` **se deriva de las features medidas** de la ventana de mayor desviación de la
sesión emulada, no se redacta a mano: redactarlo reintroduciría la circularidad de que quien
escribe el contexto conoce la respuesta.

**Control trivial declarado por adelantado:** responder siempre el mismo mecanismo acierta
3/20 = 0.15; responder siempre `none` acierta 5/20 = 0.25. Un candidato debe superarlos.

## 2. `cb:2` — corrección del instrumento de R2

Cambia **una sola cosa** respecto de `cb:1`: declara el vocabulario controlado que el
corrector exige por igualdad exacta. `cb:1` pedía `failure_mode` como cadena libre, de modo
que medía el formato de la etiqueta y no el acierto. **Los resultados de `cb:1` y `cb:2` no
son comparables entre sí.**

## 3. Resultado

| Brazo | top-1 | top-3 |
|---|---|---|
| Modelo, sin evidencia | 0.15 | 0.15 |
| Modelo, con evidencia recuperada de C-A | 0.15 | 0.15 |
| Modelo, con bandas de referencia normales explícitas | 0.15 | — |
| Control constante `vacuum_leak` / `maf_drift` / `thermostat_stuck` / `o2_lag` / `misfire` | 0.15 | 0.15 |
| **Control constante `none`** | **0.25** | **0.25** |

Conformidad de esquema 20/20 en los tres brazos con modelo; latencia mediana 3,2–3,8 s.

### 3.1 El hallazgo: colapso de modo

**El modelo respondió `misfire` en los veinte casos, en los tres brazos.** Su 0.15 procede
íntegramente de los tres casos cuyo mecanismo de referencia es, en efecto, `misfire`. No es
una tasa de acierto: es el resultado de responder siempre lo mismo.

Se descartaron dos explicaciones alternativas antes de atribuirlo al modelo:

1. **¿Falta de referencia de normalidad?** Se repitió el banco añadiendo al contexto las
   bandas normales explícitas de cada PID. **El colapso persistió idéntico**: `misfire` ×20,
   top-1 = 0.15.
2. **¿Formato?** Conformidad de esquema 20/20 y vocabulario respetado en todos los casos. El
   modelo entiende la tarea y responde bien formado; simplemente responde lo mismo.

## 4. Segundo hallazgo: la formulación de la consulta no está especificada

El brazo «con evidencia» **no mide nada**, por un defecto de instrumento distinto. El
`input_context` es una plantilla fija en la que sólo cambian los números; como el recuperador
es léxico, la consulta tiene los mismos términos en los veinte casos y **devuelve los mismos
tres documentos para todos ellos** (`own-normalidad-y-contexto`, `own-trims-fundamentos`,
`own-combustion-irregular`), ninguno de ellos el documento causal del mecanismo evaluado.

Esto afecta directamente a **`EXP-RET-001`**: el diseño experimental asume que la consulta se
deriva del contexto diagnóstico, pero **no especifica cómo**. Con un contexto numérico y un
recuperador léxico, la recuperación es constante y M3/M4/M5 medirían cero información. Las
pruebas de F27 no lo detectaron porque usaban consultas por síntoma redactadas a mano.

La formulación de la consulta es, por tanto, una **variable de diseño pendiente de declarar**
antes de ejecutar `EXP-RET-001`: o se define una traducción determinista de features a
enunciado de síntoma, o se pasa a recuperación densa. Cualquiera de las dos debe congelarse
antes de medir.

## 5. Conclusión

**D1 = Qwen2.5-3B-Instruct Q4_K_M queda RECHAZADO como generador diagnóstico** en esta
configuración. No supera al control trivial y es indistinguible de un generador constante.

Alcance de la afirmación, que no debe excederse: lo medido es **este modelo, con esta
cuantización, este contexto y este banco de veinte casos, sin ejemplos ni razonamiento
intermedio**. No se ha probado que el modelo sea incapaz de la tarea en otras
configuraciones, ni que otro modelo lo sea.

Sigue siendo cierto lo que R2 estableció: como **runtime** el modelo es viable (formato,
idioma, velocidad y latencia dentro del presupuesto edge). Lo que no está sostenido es su uso
como generador de hipótesis diagnósticas.

## 6. Qué hacer con este resultado

1. **Probar candidatos alternativos** sobre este mismo banco y con este mismo control: un
   modelo mayor (7–8 B Q4) es el siguiente escalón natural dentro del presupuesto edge.
2. **Probar configuraciones de prompt** antes de descartar la familia: ejemplos resueltos y
   razonamiento intermedio antes de la respuesta estructurada.
3. **Declarar la formulación de la consulta** (§4) antes de `EXP-RET-001`.
4. Si ningún candidato viable supera al control, es un **resultado negativo del TFM** con
   consecuencias sobre el alcance, no un motivo para relajar el criterio: el brazo B1 del
   experimento central presupone que el modelo puede explicar un diagnóstico.

## 7. Qué NO se ha hecho

- No se ha tocado `cases_v2` ni `cases_v1`, ni se ha ejecutado nada sobre ellos.
- No se ha modificado `cb:1` ni sus artefactos.
- No se han probado otros modelos: la comparación entre candidatos está pendiente.
- No se ha fijado D1b (modelo juez).
