# Criterio de selección del umbral de confianza

**Fecha de fijación: 4 de septiembre de 2026.** Este documento se escribe y se registra en el
historial **antes** de ejecutar el barrido con que se aplica. El commit que lo introduce es
anterior al que produce el artefacto: esa es la prueba de que el criterio no se eligió después
de mirar la tabla.

## Por qué existe este documento

El umbral `min_confidence = 0.80` del criterio de suficiencia se describía como «calibrado
sobre validación, no elegido a ojo», con una tabla de cuatro puntos dentro de un docstring.
La revisión encontró tres problemas: el criterio «precisión ≥ 0,93» no constaba en ningún
documento anterior al barrido, el barrido no tenía script ni artefacto, y sus cifras se
calculaban por ventana sin declarar cuántas sesiones independientes había detrás.

Sin criterio previo, la diferencia entre calibrar y elegir depende de la palabra de quien lo
escribe. Este documento la hace comprobable.

## Declaración de honestidad, necesaria

**Esto no es un pre-registro ciego.** Existe una tabla de cuatro puntos de un barrido
anterior, y quien escribe este criterio la ha visto. Un criterio fijado después de ver
resultados no adquiere la condición de predicción por escribirse ahora.

Lo que sí puede hacerse, y es lo que se hace: dejar de llamar «calibración» a lo que es una
**elección declarada de punto de operación sobre una curva medida**, registrar la curva
completa en lugar de cuatro puntos, y comprobar si la elección cambia el resultado. Esa
comprobación es la que da valor científico al ejercicio, no la palabra.

## Qué se mide

Sobre la **partición de validación** de `synthetic_v2`, y solo sobre ella. El conjunto de test
permanece cerrado: `load_partition("test")` lanza excepción y este barrido no la abre. Un
umbral seleccionado con el test dejaría de ser una predicción sobre datos no vistos y
convertiría la evaluación final en una descripción.

Para cada umbral candidato se registran:

| Magnitud | Definición |
|---|---|
| `coverage_windows` | Proporción de ventanas cuya confianza calibrada alcanza el umbral, es decir, en las que el sistema decidiría explicar |
| `precision_windows` | Proporción de aciertos del modelo entre esas ventanas |
| `n_windows_covered` | Numerador de la cobertura, en ventanas |
| `coverage_sessions`, `precision_sessions` | Las mismas magnitudes agregadas primero **por sesión** y promediadas después |
| `n_sessions` | Unidad de independencia real: las ventanas de una misma sesión no son observaciones independientes |

El barrido recorre el rango completo en pasos finos, no cuatro puntos elegidos. La curva
entera es el artefacto; el punto de operación es una lectura de la curva.

## Criterio de selección, fijado aquí

> **El punto de operación es el umbral más bajo cuya precisión de decisión sobre validación
> alcanza 0,93, medida por ventana.**

Dos precisiones sobre esta formulación:

1. **El valor 0,93 es una elección de política, no un hallazgo.** Expresa que se acepta como
   máximo un error de decisión de 7 entre 100 explicaciones emitidas. Se declara como
   política y no se presenta como derivado de los datos.
2. **«El más bajo» importa.** Entre dos umbrales que cumplen la precisión exigida se prefiere
   el que abstiene menos. Un sistema que se abstiene de más parece prudente y es inútil, y
   ese desenlace está enumerado desde el principio entre los que refutarían el trabajo.

## Comprobación de robustez, obligatoria

Se registra el **intervalo de umbrales en que las decisiones de los casos anotados no
cambian**. Si el intervalo es amplio y contiene el punto de operación, el resultado del
experimento no depende de la elección, y así debe decirse. Si es estrecho, el resultado sí
depende del umbral y eso es una limitación de primer orden que hay que declarar.

## Qué se hará con el resultado

- Si el criterio selecciona **0,80**, se mantiene el umbral, se publica la curva y se declara
  que el punto de operación es una política declarada sobre una curva medida, no un
  pre-registro ciego.
- Si el criterio selecciona **otro valor**, se adopta ese valor, se reejecutan las fases que
  dependen de él y se reporta el cambio con sus consecuencias. **No se ajusta el criterio para
  que seleccione 0,80.**
- En ambos casos se retira de la memoria y del informe de fase la frase «los umbrales están
  calibrados, no elegidos», que no describe lo que ocurrió.

## Lo que este criterio no cubre

Los otros cinco umbrales del criterio de suficiencia —fragmentos de apoyo, fuentes distintas,
cobertura de afirmaciones, puntuación de recuperación y aplicabilidad admitida— no se
seleccionan con un barrido. Tres son estructurales (un valor distinto de uno o de cero no
tendría sentido con la evidencia disponible), uno está desactivado por no discriminar, y el
de aplicabilidad es una decisión de diseño. Se declara así, en lugar de extender a los seis la
palabra que solo puede aplicarse a uno.
