# Hallazgo LEXICAL-SUPPORT-CONFOUND

**Identificador:** `LEXICAL-SUPPORT-CONFOUND` · **Fecha:** 4 de septiembre de 2026 ·
**Clase:** hallazgo experimental. No es un defecto de implementación encontrado leyendo
código: es una debilidad del criterio de suficiencia que **el propio experimento reveló** al
ampliar su conjunto de evaluación.

**Experimento que lo reveló:** E15/E17 con el conjunto anotado ampliado de un fallo a tres en
las cuatro condiciones de disponibilidad de evidencia.
**Resultado que lo contiene:** `experiments/E15_suficiencia_verifier_v1.json`, congelado.
**Versión del verificador afectada:** `v1`.

## Enunciado

> La política de suficiencia puede confundir **coincidencia léxica** y **aplicabilidad
> documental** con **suficiencia diagnóstica** cuando un fragmento de tabla contiene a la vez
> el código de avería esperado y el nombre de la señal observada.

## Cómo apareció

El experimento central manipula una sola variable, la evidencia documental disponible, en
cuatro condiciones. Hasta el 4 de septiembre de 2026 existía **para un solo fallo**, la fuga
de vacío, y el resultado era 7 decisiones correctas de 9: el agente explicaba con evidencia
completa y se abstenía al retirarla, con evidencia parcial y ante un distractor.

Al extender las cuatro condiciones a otros dos fallos —termostato bloqueado y sonda de oxígeno
lenta— usando los mismos ficheros que el conjunto ya tenía anotados, el resultado cayó a
**9 de 17**:

| Condición | Aciertos |
|---|---|
| Evidencia completa | 3/5 |
| Evidencia retirada | 3/3 |
| Evidencia parcial | 1/3 |
| Con distractor | 1/3 |
| Con distractor y sin filtro de motor | 1/3 |

Por fallo: fuga de vacío 5/5, termostato 2/5, sonda de oxígeno 2/5.

En las condiciones parcial y con distractor de los dos fallos nuevos, el agente **explicó**
con cobertura de soporte 1,00 donde debía abstenerse.

## Mecanismo, verificado en el artefacto

`check_support` acepta un fragmento como soporte de una afirmación si cumple tres condiciones:
menciona la señal, es contenido diagnóstico y porta el código esperado. La segunda se decide
en `is_diagnostic_content`, que devuelve verdadero **en cuanto el fragmento lleva cualquier
código de avería**:

```python
if evidencia.document_type not in TIPOS_DIAGNOSTICOS:
    return False
if evidencia.dtc_codes:
    return True          # ← aquí
```

Como todo el corpus es un manual de taller, el tipo de documento no discrimina nada. Y llevar
un código no prueba que el fragmento diagnostique: las **tablas** de códigos llevan decenas.

Los fragmentos aceptados en los casos que fallan son tablas:

| Caso | Fragmento aceptado | Sección | Códigos que porta |
|---|---|---|---|
| Termostato, parcial y distractor | `srvc/B3E010200102T10.pdf` | KOEO/KOER SELF-TEST [ZJ, Z6] | 18 |
| Termostato, parcial y distractor | `srvc/B3E010200102T08.pdf` | tabla de códigos | 18 |
| Sonda de oxígeno, parcial y distractor | `srvc/B3E010200102T09.pdf` | DTC DETECTION LOGIC AND CONDITIONS | 3–5 |

Un procedimiento diagnóstico de este manual porta **un** código y contiene pasos, criterios de
decisión y valores esperados. Una tabla enumera códigos y su lógica de detección, y no dice
cómo se comprueba nada.

## Por qué el primer resultado parecía correcto

La abstención de la fuga de vacío **era contingente del vocabulario**, no del criterio. Las
tablas que portan `P2187` describen la mezcla pobre sin escribir «fuel trim», de modo que
fallaban la comprobación de señal y el fragmento se rechazaba. Las tablas que portan `P0125`
sí escriben «coolant temperature», y pasaban.

Dicho de otro modo: el sistema se abstenía en la condición parcial porque el manual, para ese
código concreto, usaba otras palabras. Presentar eso como «el sistema distingue presencia de
pertinencia» era **sobregeneralizar a partir de un caso**.

## Segunda cara del mismo hallazgo

`build_claims` acepta los dos primeros fragmentos que pasan la comprobación y se detiene. Como
los candidatos llegan ordenados por puntuación de recuperación, **una tabla bien puntuada
puede ocupar las dos plazas y el procedimiento correcto no llega a examinarse**.

Verificado en el caso de la sonda de oxígeno con evidencia completa: el procedimiento
`srvc/B3E010200100W13.pdf` estaba entre los documentos recuperados y aplicables, y no aparece
en ninguna comprobación de soporte. Las dos plazas las ocuparon `T09` y `T10`.

Ese caso **acertó** —explicó, y debía explicar— pero por la evidencia equivocada.

## Qué se puede y qué no se puede afirmar con el verificador v1

**Se sostiene**, ahora sobre tres fallos y no sobre uno:

> Retirar del índice la evidencia relevante provoca la abstención del agente, manteniendo
> constantes los datos, el modelo, la atribución y la confianza calibrada.

Las tres condiciones con evidencia retirada abstienen, con cero documentos aplicables y la
confianza intacta.

**No se sostiene todavía:**

> El sistema distingue de forma general entre presencia y pertinencia de la evidencia.

La formulación correcta antes de la corrección es que **el verificador v1 puede aceptar como
soporte fragmentos que portan el código y nombran la señal sin constituir un procedimiento
diagnóstico**, y que por tanto su rechazo de evidencia no pertinente depende del vocabulario
del fragmento y no del criterio.

## Consecuencia sobre las subpreguntas

| | Estado con v1 |
|---|---|
| Explicación trazable | sostenida, con la salvedad de que una cita aceptada puede ser una tabla |
| Reconocimiento de insuficiencia por **ausencia** de evidencia | **sostenida en los tres fallos** |
| Rechazo de evidencia no pertinente | **no sostenida**: 1 de 3 en parcial y 1 de 3 con distractor |

El filtro de aplicabilidad por motor **sí funciona** y se aísla del problema: en las
condiciones sin filtro, el procedimiento del motor incorrecto se degrada a coincidencia
parcial y no se acepta. Lo que falla no es la defensa contra el vehículo equivocado, sino la
distinción entre un procedimiento y una tabla.

## Qué motiva

Una revisión del criterio de suficiencia **a nivel de fragmento**, no de documento, y una
nueva medición sobre exactamente el mismo conjunto de casos. La política revisada se documenta
en `docs/methodology/politica-suficiencia-v2.md` antes de implementarse, y su resultado se
compara con este, que no se sobrescribe.

## Valor del hallazgo

Es la razón por la que el experimento se amplió. Un conjunto de evaluación de un solo caso
producía una lectura favorable y estable que **no era generalizable**, y ningún gate, ningún
test y ninguna de las seis auditorías previas lo detectó: hizo falta ejecutar el experimento
sobre más fallos. Queda registrado como resultado, no como incidencia cerrada.
