# Política de evaluación de las variantes no oracular y adversa

**Fecha:** 4 de septiembre de 2026 · **Estado:** congelada **antes** de implementar y de
medir. El commit que introduce este documento precede al del código y al de los resultados.
**Verificador:** v2.1, sin tocar durante estas pruebas.

Este documento fija qué se mide, qué cuenta como éxito y qué desenlace refutaría cada
afirmación, **antes** de conocer ningún resultado. Es la condición que hace interpretable un
experimento cuyo diseño se decide después de haber visto otros.

## 1. Las cuatro cantidades que no pueden confundirse

| Cantidad | Qué es | De dónde sale | Dónde puede usarse |
|---|---|---|---|
| **GROUND TRUTH** | la condición que realmente generó la sesión | `validation.y`, la etiqueta del conjunto | **solo** para puntuar, al final |
| **MODEL PREDICTION** | lo que el modelo especializado diagnostica | `predicted_class` de la atribución | para acotar la búsqueda y para verificar el soporte |
| **RAG QUERY INPUT** | el texto con que se consulta el índice | descripción de **síntomas** del caso anotado | para recuperar |
| **EXPECTED DIAGNOSIS** | la decisión anotada, EXPLICA o ABSTIENE | `expected_action` del conjunto anotado | **solo** para puntuar, al final |

**Regla que gobierna las variantes no oraculares:** ninguna cantidad de la primera y la cuarta
fila puede alcanzar la búsqueda ni la verificación, ni directamente ni por derivación.

## 2. Los tres canales por los que el oráculo entra hoy

Medido sobre `src/mecanico_ia_exp/experiments/sufficiency_runner.py`, commit `1a58376`:

| Canal | Dónde | Qué filtra |
|---|---|---|
| **O-1 · selección de ventana** | l. 133, `(validacion.y == fault_id) & aciertos` | solo se evalúan ventanas que el modelo **clasifica bien**. El escenario en que el modelo se equivoca queda fuera del experimento por construcción |
| **O-2 · acotación de la búsqueda** | l. 170 de `retrieval_runner.py`, `DIAGNOSTICO_A_DTC[caso["fault_id"]]` | los códigos que acotan la recuperación se derivan de la **etiqueta anotada**, no del diagnóstico del modelo |
| **O-3 · verificación del soporte** | l. 187, `expected_dtc=DIAGNOSTICO_A_DTC.get(fault_id)` | los códigos que un fragmento debe portar para sostener se derivan de la **etiqueta anotada** |

El resultado vigente de 15/17 se obtiene con los tres canales abiertos. Por eso se etiqueta
**ORACLE-ASSISTED UPPER BOUND**: es una cota superior de lo que el sistema haría, no una
estimación de su comportamiento.

## 3. Variante NX-01, no oracular

**Qué cambia:** O-2 y O-3 pasan a derivarse de `predicted_class`. **Qué no cambia:** la
selección de ventana, para que la comparación sea sobre las mismas observaciones.

**Predicción declarada ahora, antes de ejecutar:** sobre las ventanas donde el modelo acierta,
diagnóstico y etiqueta coinciden, de modo que NX-01 debería dar **exactamente las mismas
quince decisiones**. Si así ocurre, queda demostrado que O-2 y O-3 **no aportan información
que el sistema no tenga en ejecución**, y el oráculo del experimento se reduce a O-1.

**Qué refutaría esto:** cualquier decisión distinta. Significaría que la derivación desde la
predicción no es equivalente a la derivación desde la etiqueta ni siquiera cuando coinciden, y
habría que buscar la causa antes de seguir.

**Lo que NX-01 no resuelve, y se dice desde ahora:** el texto de consulta de cada caso lo
escribió una persona que conocía el fallo. Describe **síntomas** y no nombra el diagnóstico ni
el código, pero su redacción no es ciega. Es una limitación de la construcción del conjunto
anotado que NX-01 no elimina y que se declara junto a sus resultados.

## 4. Variante NX-02, escenario adverso

**Qué cambia:** la selección de ventana se invierte. Se evalúan ventanas de la condición cuya
clasificación el modelo **falla**, con el pipeline no oracular completo de NX-01. El sistema
recibe un diagnóstico incorrecto y busca evidencia para él.

**Los cuatro desenlaces posibles, enumerados antes de mirar.** Ninguno es «el esperado»: cada
uno significa algo distinto y los cuatro son resultados publicables.

| Desenlace | Qué se observaría | Qué significaría |
|---|---|---|
| **D-1 · explicación incorrecta bien respaldada** | EXPLICA, cobertura de soporte alta, citas de procedimientos del diagnóstico equivocado | **El peor caso.** El sistema fabrica una explicación trazable de algo falso: la trazabilidad no protege del error del modelo |
| **D-2 · abstención** | ABSTIENE | El sistema calla ante un diagnóstico erróneo. Hay que decir **por qué**: si es por confianza baja, el mérito es de la calibración y no del verificador |
| **D-3 · contradicción detectada** | ABSTIENE con contradicción registrada entre la observación y la evidencia documental | El resultado más fuerte para la pregunta de investigación: el sistema detecta que la evidencia no encaja con lo observado |
| **D-4 · rechazo por ausencia de soporte** | ABSTIENE con cobertura de afirmaciones cero | El corpus no documenta el diagnóstico erróneo para esas señales y el verificador lo nota |

**Cómo se puntúa.** No hay decisión «correcta» anotada para estos casos, porque el conjunto
anota la condición real y aquí el diagnóstico es otro. Se reporta la **distribución de
desenlaces** y, para cada caso: diagnóstico del modelo, condición real, confianza calibrada,
decisión, cobertura de afirmaciones, número de citas aceptadas y motivo. No se calcula una
tasa de acierto: sería inventar un patrón oro que no existe.

**La afirmación que este escenario pone a prueba:**

> Un diagnóstico incorrecto del modelo especializado no produce una explicación incorrecta
> aparentemente bien respaldada.

Se considera **refutada** si se observa D-1 en cualquier caso. Se considera **sostenida con la
fuerza que corresponda** si se observan D-2, D-3 o D-4, con la acotación de cuál de los tres y
por qué motivo. **D-2 por confianza baja no sostiene la capacidad del verificador**, solo la de
la calibración, y así debe reportarse.

## 5. Compromisos que no se revisan después de ver los resultados

- Los cuatro desenlaces y su interpretación quedan fijados aquí. **No se añade un quinto ni se
  reinterpreta uno después de observarlo.**
- El verificador **no se modifica** durante estas pruebas. Si aparece un defecto independiente
  y material, se detiene, se registra y se presenta antes de tocar nada.
- El umbral, el conjunto, el corpus, el modelo, la calibración y el filtro de motor no cambian.
- Si NX-01 o NX-02 contradicen el resultado vigente de 15/17, **manda el resultado no
  oracular** para toda afirmación sobre comportamiento del sistema, y el 15/17 queda como cota
  superior con esa etiqueta.
