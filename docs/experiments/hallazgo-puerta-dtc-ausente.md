# Hallazgo EMPTY-DTC-GATE-BYPASS

**Identificador:** `EMPTY-DTC-GATE-BYPASS` · **Fecha:** 4 de septiembre de 2026 ·
**Clase:** hallazgo experimental. Lo reveló el escenario adverso, no una lectura del código ·
**Versión del verificador afectada:** v2.1, y también v1 y v2 · **Estado:** registrado, **no
corregido**. El verificador no se toca mientras se evalúan estas dimensiones.

## Enunciado

> Cuando el diagnóstico del modelo no tiene códigos de avería asociados, el verificador
> **omite silenciosamente** una de sus cuatro condiciones de soporte en lugar de declarar que
> no puede comprobarla.

## Mecanismo, verificado en el artefacto

`check_support` exige cuatro condiciones: mención de la señal, contenido diagnóstico, porte
del código esperado y papel de procedimiento. La tercera se evalúa así:

```python
lleva_dtc: bool | None = None
if expected_dtc:
    lleva_dtc = bool(set(evidencia.dtc_codes) & set(expected_dtc))
...
if lleva_dtc is False:
    return resultado(False, "...")
```

Con `expected_dtc` vacío, `lleva_dtc` queda en `None`, la comprobación **no se ejecuta**, y
cualquier fragmento con papel de procedimiento que mencione la señal sostiene la afirmación.

`expected_dtc` sale de `DIAGNOSTICO_A_DTC[diagnóstico]`. El diagnóstico `F00_normal` —«no hay
avería»— no está en ese mapa, y no puede estarlo: no existe un código de avería para la
ausencia de avería.

**Es el mismo patrón que `SIGNAL_MAPPING_UNAVAILABLE`**, en otro punto del verificador:
ausencia de correspondencia tratada como ausencia de restricción, en vez de como incapacidad
declarada de comprobar. Allí la consecuencia era una abstención mal atribuida; aquí es una
**restricción que desaparece**, que es más grave.

## Cómo apareció

En el escenario adverso con la regla `ENM-A01`, los seis casos evaluados tienen diagnóstico
`F00_normal`: el modelo no detecta el fallo que existe. Las 24 comprobaciones de soporte de esa
ejecución salen **todas** con la puerta de DTC sin evaluar.

| Ejecución | Comprobaciones sin puerta de DTC |
|---|---|
| `E15_suficiencia.json`, oracular | 0 de 150 |
| `E15_suficiencia_non_oracle.json` | 0 de 150 |
| `E15_suficiencia_adverse.json` | **24 de 24** |

**El resultado vigente de 15/17 no está afectado.** Los cinco diagnósticos que allí aparecen
son averías reales con códigos asociados, y la puerta se evalúa en las 150 comprobaciones.

## Por qué importa, con la cifra

En el caso adverso del fallo de encendido, el modelo diagnostica «normal» con confianza
calibrada **0,984** y el verificador acepta **cuatro citas** de procedimientos que mencionan
las señales observadas. La cobertura de afirmaciones sale 0,667.

El sistema se abstuvo **únicamente porque el umbral de cobertura es 0,8**. Con un umbral de
0,6 habría emitido una explicación trazable, con cuatro citas de procedimientos reales del
vehículo, respaldando un diagnóstico falso.

Eso es el desenlace D-1 de la política congelada —explicación incorrecta aparentemente bien
respaldada— evitado **por el margen de un umbral**, no porque el verificador detectara nada.
Presentar la abstención de estos casos como mérito del verificador sería incorrecto.

## Segunda cara: el motivo publicado es falso

Las citas aceptadas se registran con el motivo «procedimiento diagnóstico del vehículo que
menciona la señal **y porta el código**». No porta ningún código esperado: no había ninguno que
portar. El registro afirma que se comprobó algo que no se comprobó, y ese texto es el rastro
de auditoría del sistema.

## Qué se puede y qué no se puede afirmar

**Se sostiene:**

> Ante un diagnóstico incorrecto y confiado, el sistema no emitió ninguna explicación
> incorrecta en los seis casos evaluados.

**No se sostiene:**

> El verificador impide que un diagnóstico incorrecto produzca una explicación aparentemente
> bien respaldada.

En estos casos el verificador **perdió una de sus cuatro condiciones** y la abstención se
decidió en el umbral de cobertura. La afirmación correcta acota el mérito a la política de
cobertura y declara que la condición de código no se evaluó.

## Qué motiva

Una revisión del verificador que trate la ausencia de códigos asociados como **incapacidad
declarada** y no como ausencia de restricción, en la línea de `SIGNAL_MAPPING_UNAVAILABLE`. No
se implementa ahora: cambiar el instrumento mientras se miden estas dimensiones invalidaría la
comparación. Se propone, se registra y se decide después.
