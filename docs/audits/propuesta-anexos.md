# Propuesta de anexos

**Fecha:** 13 de octubre de 2026 · **Qué es:** qué material complementario merece ir en los anexos y
qué no · **Qué NO es:** los anexos escritos. Es una selección razonada, para que la decisión sea del
autor · **Regla de la plantilla oficial que gobierna esta propuesta:** los anexos **no puntúan**, se
estima un máximo del 20 % del contenido del trabajo, y debe existir un motivo claro para cada uno —
«sin este anexo no se comprende de la misma forma el trabajo»

## 1. El criterio, antes de la lista

Un anexo se justifica cuando se cumplen las tres cosas a la vez: el material **existe y está
verificado**, el cuerpo del TFM **lo necesita pero no lo soporta** —por extensión o por nivel de
detalle—, y un lector que no lo abra sigue entendiendo el capítulo. Si falla la primera, no es
material; si falla la segunda, su sitio es el cuerpo; y si falla la tercera, el capítulo está
incompleto y el anexo lo estaría tapando.

Con ese criterio, de los seis bloques propuestos **se recomiendan tres** y se descartan tres.

## 2. Los tres que se recomiendan

### Anexo B · Dataset sintético OBD-II

| | |
|---|---|
| **Qué contiene** | la ficha de generación —doce señales, cuatro regímenes de conducción, duración y frecuencia de muestreo—, la tabla de parámetros de cada una de las cinco condiciones de fallo con su mecanismo declarado, la **Figura B.1** con la señal testigo de cada condición comparada con la misma sesión sin fallo, y la ficha de calibración del generador contra el manual de taller |
| **Por qué hace falta** | el capítulo 5 afirma cosas sobre lo que cada fallo deja ver y sobre lo que no, y el lector no tiene forma de juzgarlas sin ver una señal averiada al lado de una sana. Es, además, la respuesta a la primera pregunta que un tribunal hace ante datos sintéticos: ¿qué hay exactamente dentro? |
| **Por qué no va en el cuerpo** | la Figura B.1 ocupa una página entera con cinco paneles, y la tabla de parámetros es una ficha técnica |
| **Qué hay que declarar dentro** | que procede de `synthetic_v1` y del generador **anterior** a su calibración, y que ese conjunto no se reconstruye con el generador publicado |
| **Extensión estimada** | 3 a 4 páginas |

### Anexo D · Resultados complementarios

| | |
|---|---|
| **Qué contiene** | la **Figura D.1**, F1 por condición de los dos modelos de diagnóstico con su diferencia; las tablas por clase de E6 y E7 completas; la tabla de atribución de E9 con las seis señales principales de cada condición; y el barrido de umbral de E15b del que salió el 0,79 |
| **Por qué hace falta** | el capítulo da los agregados y cita el detalle por clase en prosa. Quien quiera comprobar la frase «acierta dos ventanas más en el termostato» necesita la tabla, y quien quiera discutir la elección del umbral necesita el barrido |
| **Por qué no va en el cuerpo** | la Figura D.1 se solapa con la 5.3, que ya muestra adónde van los errores de cada modelo; añade la magnitud por clase, que es detalle y no argumento |
| **Qué hay que declarar dentro** | que el barrido del umbral es anterior a la enmienda del criterio, y que la enmienda se escribió después de ver ese barrido |
| **Extensión estimada** | 4 a 5 páginas |

### Anexo F · Reproducibilidad y repositorio

| | |
|---|---|
| **Qué contiene** | el procedimiento de reproducción desde un clon limpio, con sus seis pasos y sus órdenes exactas; la tabla de **lo que no se puede reproducir y por qué**, con los dos conjuntos no reconstruibles y su medición; las tres categorías de prueba con sus recuentos; y el índice de los siete notebooks entregados con su modalidad |
| **Por qué hace falta** | es la parte verificable del trabajo, y es lo que convierte «los resultados son reproducibles» en una afirmación comprobable en lugar de una promesa. Es también donde quedan declarados, en un solo sitio, los dos límites de reproducibilidad que el capítulo 6 menciona de pasada |
| **Por qué no va en el cuerpo** | son órdenes de consola y tablas de ficheros; el capítulo 6 ya dice lo que de ahí se concluye |
| **Qué hay que declarar dentro** | lo que no se distribuye —el corpus del manual, el índice documental, los pesos del adaptador— y qué pruebas quedan sin ejecutar por ello |
| **Extensión estimada** | 3 a 4 páginas |

## 3. Los tres que se descartan, y por qué

| Bloque | Por qué no |
|---|---|
| **A · Arquitectura experimental** | el capítulo 4 la describe y la Figura 6.1 la dibuja. Un anexo con lo mismo en más páginas no añade comprensión: añade volumen, y el volumen de los anexos cuenta contra el límite del 20 % sin puntuar |
| **C · Protocolos experimentales** | los pre-registros, las enmiendas fechadas y las políticas de evaluación son numerosos y están en el repositorio con su historia. Llevarlos al documento los congelaría en una versión y dejaría de verse lo que los hace valiosos, que es **cuándo** se escribió cada uno respecto de cuándo se midió. Lo que sí conviene es que el anexo F los enumere con su ruta |
| **E · Validación de hipótesis y abstención** | es el núcleo de PI.3 y PI.4, y está en el cuerpo del capítulo 5 con sus tablas 5.5 a 5.8 y sus figuras 5.10 y 5.11. Un anexo aquí movería evidencia principal fuera del texto que la argumenta, que es exactamente lo que un anexo no debe hacer |

## 4. Lo que esta propuesta deja decidido y lo que no

**Decidido, si el autor acepta:** las figuras `B.1` y `D.1` ya están generadas en
`artifacts/figures/memoria/` y registradas en `docs/figuras-tfm.md` con su procedencia, de modo que
incorporarlas es copiar un bloque, no producir nada nuevo.

**Pendiente de decisión del autor:** si los tres anexos entran, si entra solo alguno, y si el anexo
F se escribe como anexo o se sustituye por una referencia al repositorio. La tercera opción es
defendible: el procedimiento de reproducción vive en `docs/reproducir-desde-cero.md`, se valida
desde un clon limpio y se queda obsoleto en el documento en cuanto cambie una orden.

**Lo que esta propuesta no hace:** no escribe ningún anexo, no mueve ningún contenido fuera de los
capítulos y no toca la numeración de las figuras del cuerpo.
