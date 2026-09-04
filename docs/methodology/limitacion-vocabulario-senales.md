# Limitación declarada: el vocabulario de señales del verificador

**Fecha:** 4 de septiembre de 2026 · **Estado:** limitación conocida del instrumento, **no**
un defecto pendiente de corregir. Se declara aquí, se publica en la memoria y no se elimina
en esta fase.

## 1. Qué es

Las señales del conjunto de datos se identifican con nombres de descriptor —`ltft_bank1`,
`coolant_temperature`— y el manual de taller las nombra con otras palabras, en inglés y con
las abreviaturas del fabricante. El verificador traduce de unas a otras con un diccionario
construido **a mano**, leyendo el corpus.

| Hecho | Valor |
|---|---|
| Señales que contiene | **doce** |
| Cobertura del conjunto experimental actual | **completa**: las seis señales que aparecen en los diecisiete casos están en él |
| ¿Cambió entre v1, v2 y v2.1? | **No.** Es idéntico en las tres versiones |
| ¿Depende de los tres fallos del banco? | **No.** Seis de las doce señales no intervienen en ningún caso del banco |
| ¿Interviene en la clasificación del papel de la sección? | **No.** `classify_section` y `classify_chunk` no lo consultan |
| Dónde interviene | únicamente en `mentions_signal`, la comprobación de que un fragmento habla de la señal observada |
| Qué limita | la generalización a señales no incluidas: sobre ellas el verificador **no puede pronunciarse** |

## 2. Por qué no se amplía ahora

Añadir sinónimos automáticamente, o generarlos con un modelo de lenguaje, introduciría una
variable experimental nueva en mitad de una secuencia de mediciones cuya validez depende de
que solo cambie una cosa cada vez. El diccionario se conserva tal cual. Medir su efecto queda
como **ablación separada**, no como corrección de este ciclo.

## 3. Lo que se corrigió: el silencio, no el diccionario

Hasta el 4 de septiembre de 2026, una señal ausente del diccionario caía a una comparación
literal del identificador. Si esa comparación fallaba, la salida era indistinguible de la de
una señal conocida sobre la que el manual calla:

- **el manual no habla de esta señal** → resultado sobre el corpus;
- **el verificador no sabe con qué palabras buscarla** → límite del instrumento.

Ahora `check_support` devuelve `SIGNAL_MAPPING_UNAVAILABLE` en el segundo caso, con motivo
propio, y lo publica en el registro de cada comprobación. La afirmación **no se sostiene** en
ninguno de los dos casos, pero el registro dice cuál de los dos es. La distinción importa para
la abstención: abstenerse porque no hay evidencia es un resultado; abstenerse porque el
instrumento no sabe mirar es una limitación, y presentarlas como lo mismo sobreestima lo que
el sistema demuestra.

## 4. Hallazgo que destapó el cambio

Al hacer explícita la ausencia de correspondencia, **siete pruebas dejaron de pasar**: tres de
la suite de v2 y cuatro de la de v2.1. Todas eran precisamente las que demostraban que la
política funciona con códigos y señales ajenos al banco experimental, y todas usaban señales
inventadas —`brake_pressure`, `steering_angle`, `can_bus_load`, `airbag_resistance`— que no
están en el diccionario.

Es decir: **la demostración de generalidad de ambas versiones se apoyaba en el comportamiento
silencioso que ahora se elimina.** Las pruebas pasaban porque la comparación literal encontraba
«throttle position» en un texto escrito por el propio test, no porque el verificador supiera
tratar una señal desconocida.

Es el mismo patrón que `LEXICAL-SUPPORT-CONFOUND`: un test que codificaba como comportamiento
correcto una debilidad del instrumento. Se registra por eso, y no se oculta.

**Reparación, mínima y anotada.** Las pruebas de generalidad pasan a usar cuatro señales que
sí están en el diccionario y **no intervienen en ningún caso del banco** —posición de
mariposa, velocidad, carga del motor y avance de encendido— junto a códigos de frenos,
dirección, red y `airbag`. La generalidad de la **regla estructural** frente a señales
desconocidas se comprueba aparte, al nivel donde esa regla opera: la clasificación de la
sección es correcta y el soporte se deniega por la puerta de vocabulario, con su motivo
propio. `tests/test_support_policy_v2.py` recibió con esto su **única** edición posterior a la
congelación de v2; ninguna aserción cambió y la cabecera del fichero lo registra.

## 5. Impacto sobre los resultados publicados

**Ninguno.** Las seis señales de los diecisiete casos están mapeadas, todas las comprobaciones
del registro vigente salen `MAPPED`, y la reejecución da las mismas quince decisiones
correctas, caso a caso. El cambio añade información al registro y no altera ninguna decisión.

## 6. Cómo debe enunciarse en la memoria

> El verificador comprueba que un fragmento habla de la señal observada mediante un
> vocabulario de doce señales construido manualmente a partir del corpus. Cubre por completo
> el conjunto experimental, no cambió a lo largo de las tres versiones del criterio de
> suficiencia y no interviene en la clasificación del papel documental. Para una señal fuera
> de ese vocabulario el sistema lo declara explícitamente y se abstiene, en lugar de concluir
> que no existe evidencia. La construcción manual limita la generalización a señales no
> incluidas, y medir ese efecto queda como trabajo futuro.
