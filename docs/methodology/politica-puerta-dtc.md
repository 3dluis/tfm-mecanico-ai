# Política de la puerta de códigos de avería

**Fecha:** 4 de septiembre de 2026 · **Motivada por:** hallazgo `EMPTY-DTC-GATE-BYPASS`
(`docs/experiments/hallazgo-puerta-dtc-ausente.md`, problema `P-14`) · **Estado:** documentada
**antes** de implementarse y de volver a medir. El commit que introduce este documento precede
al del código y al del resultado.

**Versión del verificador que introduce:** v2.2. v2.1 y sus resultados quedan congelados.

## 1. El problema que resuelve

`check_support` exige que el fragmento citado porte uno de los códigos que documentan el
diagnóstico. Esa lista sale de `DIAGNOSTICO_A_DTC[diagnóstico]`. Cuando la lista viene vacía,
la comprobación **no se ejecuta** y desaparece una de las cuatro condiciones de soporte.

Hoy la lista puede venir vacía por razones distintas que el código no distingue, y el resultado
es el mismo en todas: la puerta se abre.

## 2. Lo que no se va a hacer

**No se adopta la regla «lista vacía ⇒ rechazar».** Convertiría «este diagnóstico no se
documenta con códigos» en un error del sistema, que es tan falso como abrir la puerta. El
problema no es qué decidir cuando la lista está vacía: es que **«vacía» significa cuatro cosas
distintas** y el verificador las trata como una.

## 3. Taxonomía del requisito

El requisito es una propiedad del **diagnóstico**, no del fragmento, y se determina antes de
mirar ninguna evidencia.

| Requisito | Cuándo aplica | Qué hace la puerta | ¿Puede sostenerse una afirmación? |
|---|---|---|---|
| `DTC_REQUIRED` | el diagnóstico está declarado con **uno o más** códigos que lo documentan | exige que el fragmento porte alguno | **Sí**, si además se cumplen las otras tres condiciones |
| `DTC_NOT_APPLICABLE` | el diagnóstico está declarado **sin** códigos: por su naturaleza ninguno lo documenta | no se ejecuta, y se declara | **No.** La evidencia documental de este corpus está anclada en códigos; sin ancla no hay soporte documental que comprobar |
| `DTC_MAPPING_UNAVAILABLE` | el diagnóstico **no está declarado**: nadie ha establecido qué códigos lo documentan | no se ejecuta, y se declara | **No.** El instrumento no sabe comprobarlo, que no es lo mismo que haber comprobado y no encontrado |
| `DTC_OPTIONAL` | el diagnóstico está declarado con códigos que lo documentan **parcialmente**: portarlos refuerza, no portarlos no descalifica | no descalifica; se registra si el fragmento porta alguno | **Sí**, con las otras tres condiciones |

**Cómo se determina, de forma general:** el requisito se lee de la **declaración** del
diagnóstico en el mapa de códigos, no de su nombre ni de ninguna lista de casos.

| Estado de la declaración | Requisito |
|---|---|
| presente, con códigos | `DTC_REQUIRED` |
| presente, sin códigos | `DTC_NOT_APPLICABLE` |
| ausente | `DTC_MAPPING_UNAVAILABLE` |

`DTC_OPTIONAL` **no se asigna a ningún diagnóstico hoy** y requiere declaración expresa. Se
define porque la distinción es real —hay condiciones que un manual documenta sin código
propio— y porque adoptarlo por defecto reproduciría exactamente el defecto que esta política
corrige. Que exista la categoría no autoriza a usarla para salvar un caso.

## 4. Por qué la regla es general y no está escrita para «sin avería»

La regla no menciona ningún diagnóstico. Lee si el autor del mapa **declaró** los códigos de
una condición y si esa declaración está vacía. Un diagnóstico nuevo entra en una de las tres
categorías por cómo se le declare, no por cómo se llame.

Que la condición «sin avería» quede en `DTC_NOT_APPLICABLE` es una consecuencia de un hecho del
dominio —no existe un código de avería para la ausencia de avería— y ese hecho se declara como
**dato**, añadiéndola al mapa con lista vacía. La regla no la conoce.

## 5. Lo que cambia en el registro

Cada comprobación de soporte pasa a publicar el requisito que se le aplicó, junto al resultado
de la puerta. Desaparece el motivo actual «procedimiento diagnóstico del vehículo que menciona
la señal **y porta el código**» en los casos donde no se comprobó ningún código: ese texto
afirmaba algo que no había ocurrido, en el propio rastro de auditoría del sistema.

## 6. Lo que no cambia

Umbral de confianza 0,79 · conjunto `synthetic_v2` · semilla 20260901 · corpus 0,1,0 ·
modelo de embeddings · bosque aleatorio con calibración isotónica · filtro de motor ·
clasificación del papel por sección, que es v2.1 sin tocar · los diecisiete casos.

**Predicción declarada antes de ejecutar.** Los cinco diagnósticos de avería del banco están
declarados con códigos, luego quedan en `DTC_REQUIRED` y la puerta se comporta exactamente
igual que hoy: **el resultado de 15/17 no debe cambiar en ninguna decisión**. Si cambiara,
habría que detenerse y buscar la causa antes de seguir.

En el escenario adverso, los seis casos tienen diagnóstico «sin avería» y pasan a
`DTC_NOT_APPLICABLE`, de modo que **ninguna cita puede sostener**. La cobertura de afirmaciones
debe caer a cero y la abstención debe pasar a decidirse por ausencia de soporte. Eso
convertiría los dos casos `D-2` en `D-4`.

**Lo que ese cambio no demostraría.** Que el sistema se abstenga por la razón correcta después
de corregir el instrumento no prueba que se abstuviera por la razón correcta antes. El
resultado congelado de NX-02 y su contraejemplo se conservan y se publican.
