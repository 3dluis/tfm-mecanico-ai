# La condición de distractor: invalidación y criterio de rediseño

**Fecha:** 4 de septiembre de 2026 · **Motivada por:** `RAG-MIN-036` y `TUTOR-MAJ-014`, que la
detectan por separado · **Estado:** el criterio de rediseño se fija **antes** de construir ni
ejecutar nada.

## 1. Qué se ha comprobado

Con el filtro de motor activo, la condición de distractor recupera **exactamente los mismos
fragmentos** que la condición de evidencia parcial, en los tres fallos:

| Pareja | Fragmentos que llegan al verificador |
|---|---|
| fuga de vacío: parcial ↔ distractor | idénticos, 3 y 3 |
| termostato: parcial ↔ distractor | idénticos, 4 y 4 |
| sonda: parcial ↔ distractor | idénticos, 4 y 4 |

**Una condición que no cambia lo que llega al sistema no está manipulando la variable que dice
manipular.** Tres de los diecisiete casos no miden nada distinto de otros tres, y «distractor
3/3» no es una quinta condición: es la condición parcial contada dos veces.

> **`CORREGIDO 2026-10-13`.** La tabla de arriba y su explicación —que la causa es el filtro de
> motor— **no son exactas**. Al medirlo de nuevo antes de rediseñar, con la recuperación ya
> corregida, sale esto:
>
> | Pareja | ¿Llega el distractor? | Diferencia con la parcial |
> |---|---|---|
> | fuga de vacío | **sí**, los dos ficheros declarados | **2 fragmentos** |
> | termostato | no | 0 |
> | sonda | no | 0 |
>
> Y la causa de los dos que fallan no es el filtro: **`C12` y `C16` tienen exactamente la misma
> configuración que `C11` y `C15`**. El único campo que difiere es `distractor_files`, que el
> recorrido de suficiencia **no lee** —solo lo usa E12, como etiqueta para puntuar la recuperación—.
> Nunca fueron una condición distinta, y no porque algo las bloqueara, sino porque no había nada que
> bloquear.
>
> La invalidación sigue en pie: la condición no medía lo que decía medir. Lo que cambia es el motivo,
> y con él el rediseño. Ver [`protocolo-distractor-v2.md`](protocolo-distractor-v2.md).

## 2. Esto ya estaba documentado, para un solo fallo

El propio conjunto anotado lo dice, en el comentario del caso sin filtro:

> «C08 no probaba lo que decía probar: el filtro de motor bloquea el procedimiento del LF antes
> de que llegue a ordenarse, así que el distractor nunca alcanzaba al verificador y C08 acababa
> siendo idéntico a PARTIAL.»

La condición sin filtro se creó **precisamente** para arreglarlo. Lo que ocurrió es que, al
ampliar el conjunto de un fallo a tres, la salvedad **no se propagó**: se replicó la condición
defectuosa dos veces más y los documentos de resultados pasaron a presentarla como una
condición independiente.

No es un defecto nuevo descubierto por las auditorías. Es un defecto **conocido y declarado**
que se perdió al escalar, y esa es la lección que se registra: una salvedad escrita en el
conjunto anotado no viaja sola a los informes.

## 3. Estado del resultado histórico

Se conserva íntegro, sin borrarse, con la etiqueta:

> `DISTRACTOR_V1_INVALID_AS_INDEPENDENT_CONDITION`

Las cifras publicadas de esa condición son correctas como recuento de decisiones y **no**
sostienen ninguna afirmación sobre rechazo de evidencia no pertinente que no sostenga ya la
condición parcial.

## 4. Criterio de rediseño, fijado antes de construir

Una condición de distractor es válida si y solo si cumple las cuatro:

| # | Requisito | Cómo se comprueba, antes de mirar ningún resultado |
|---|---|---|
| D-1 | El distractor **entra en el conjunto recuperable** | el identificador de al menos un fragmento del distractor aparece entre los candidatos que llegan al verificador |
| D-2 | El conjunto recuperado **difiere** del de la condición parcial | la diferencia simétrica de identificadores de fragmento no es vacía |
| D-3 | El distractor es **semánticamente plausible** | trata la misma condición o una vecina, con vocabulario que solapa el de la consulta |
| D-4 | El distractor **no es evidencia suficiente** | por una razón declarada de antemano: vehículo, motor, sistema o alcance equivocados |

**Si D-1 y D-2 no se cumplen, la condición no existe**, con independencia de lo que dé su
resultado. La comprobación es previa al veredicto y no depende de él.

## 5. Qué se hará si no puede construirse

Si con el corpus actual no puede construirse una condición que cumpla las cuatro **sin
introducir casos artificiales**, se **elimina del experimento principal** y pasa a limitación y
trabajo futuro. Tres condiciones reales valen más que cuatro con una falsa.

La condición **sin filtro de motor** no se ve afectada por esto: ahí el distractor sí alcanza al
verificador, por construcción, y es la que mide la última línea de defensa. Se conserva.

## 6. Consecuencia sobre lo publicado

Toda cifra por condición pasa a reportarse sobre las condiciones **realmente independientes**.
Mientras el rediseño no exista, son: evidencia completa, evidencia retirada, evidencia parcial
y distractor sin filtro de motor. **Cuatro, no cinco.**
