# Enmienda ENM-A01 a la política de evaluación del escenario adverso

**Fecha:** 4 de septiembre de 2026 · **Enmienda a:**
`docs/methodology/politica-evaluacion-no-oracular.md`, commit `f290263` ·
**Posterior a:** la primera ejecución adversa, commit `3b02cf8` ·
**Estado:** aceptada, y aplicada **antes** de interpretar ningún resultado adverso.

Esta enmienda es posterior a la primera ejecución. No la oculta: aquel resultado y el defecto
que lo produjo quedan registrados y se publican junto al resultado revisado.

## 1. El defecto

La política congelada define **qué** se observa en el escenario adverso y **cómo** se
interpreta, pero no dice **qué ventana** se elige entre las que el modelo clasifica mal. La
implementación tomó la primera por orden de índice, que es una decisión arbitraria heredada
del modo no adverso.

Consecuencia, medida sobre las 98 ventanas de validación:

| | |
|---|---|
| Ventanas mal clasificadas | 12 |
| Confianza calibrada de las elegidas por orden de índice | 0,360 y 0,445 |
| Confianza calibrada máxima entre las mal clasificadas | **0,984** |
| Umbral de operación | 0,79 |

Las seis ejecuciones adversas se abstuvieron **todas** con el motivo `LOW_MODEL_CONFIDENCE`.
Es decir: el escenario nunca llegó a poner a prueba el verificador, porque la calibración
detuvo el caso antes. Y no por una propiedad del sistema, sino porque el orden de índice
seleccionó errores poco confiados existiendo errores muy confiados.

**Un escenario adverso que elige el caso menos adverso disponible no es un escenario adverso.**

## 2. La regla, definida de forma general

> **A-1 · Selección adversa.** Entre las ventanas de una condición que el modelo clasifica
> mal, se elige aquella con **mayor confianza calibrada** en su predicción incorrecta.
>
> **A-2 · Salida vacía.** Si la condición no tiene ninguna ventana mal clasificada, se declara
> y no se sustituye por otra cosa.

**Por qué es la regla correcta y no un ajuste al resultado.** La afirmación bajo prueba es que
un diagnóstico incorrecto no produce una explicación incorrecta aparentemente bien respaldada.
El caso que más puede refutarla es el error **más confiado**, porque es el único que supera la
puerta de confianza y llega al verificador. Elegir el peor caso disponible es lo que define un
ensayo adverso; elegir el primero por índice no responde a ningún criterio.

La regla se define sin referencia a ningún resultado: no menciona qué caso falla, ni qué
desenlace se desea, ni ningún valor de confianza concreto. Es aplicable a cualquier condición y
a cualquier partición.

## 3. Lo que esta enmienda no cambia

- **Los cuatro desenlaces D-1 a D-4 y su interpretación** siguen siendo exactamente los de la
  política congelada. No se añade ninguno ni se reinterpreta ninguno.
- **D-2 por confianza baja sigue sin acreditar al verificador**, solo a la calibración.
- El verificador, el umbral, el conjunto, el corpus, el modelo y el filtro de motor no cambian.
- La separación entre etiqueta anotada, diagnóstico del modelo, texto de consulta y decisión
  anotada se mantiene intacta.

## 4. Conocimiento previo, declarado

Al escribir esta enmienda se conoce la estructura de errores del modelo en validación: de las
doce ventanas mal clasificadas, once son un fallo real clasificado como **normal** y una es un
fallo confundido con otro fallo, esta última con confianza 0,579. **Ningún diagnóstico erróneo
hacia otro fallo supera el umbral.** Se declara aquí porque acota de antemano lo que el
escenario revisado puede y no puede probar, y ocultarlo sería el defecto que esta enmienda
corrige.
