# 6. Réplicas y semillas (Fase E)

**Las semillas quedan fijadas aquí, antes de ejecutar.** Elegirlas después de ver resultados invalidaría
todo lo demás, y por eso se escriben en este documento, que se comitea antes de la primera ejecución.

## 6.1 Las semillas

| Réplica | Semilla |
|---|---|
| R1 | **20260901** |
| R2 | **20260902** |
| R3 | **20260903** |
| R4 | **20260904** |
| R5 | **20260905** |

La primera es la del proyecto, de modo que R1 reproduce las condiciones con que se midió todo lo
anterior. Las otras cuatro son consecutivas: no se buscan, no se eligen y no se sustituyen. **Si una
réplica falla por una causa técnica, se documenta y se repite con la misma semilla**; no se cambia por
otra.

La semilla gobierna a la vez el bosque, la inicialización y el orden de lotes de la red, el fondo de
atribución y los muestreos. **No** gobierna el reparto del conjunto ni la permutación de los
subconjuntos anidados: esos están fijados por `20260901` en el protocolo del conjunto y son los mismos
en las cinco réplicas, porque lo que se quiere medir es la variación del modelo, no la de la partición.

## 6.2 Cuántas, y por qué cinco

Cinco es el mínimo que permite dar mediana y rango sin pretender una estimación de la varianza, y
suficiente para ver si una diferencia de dos o tres ventanas sobre catorce sobrevive al cambio de
semilla. **No se proponen más** porque el factor limitante de este trabajo no es el cómputo: es que las
unidades de independencia son pocas —siete sesiones por condición en validación— y más réplicas no
crean sesiones nuevas.

Con cinco réplicas, cuatro puntos de volumen y **seis** representaciones —`A1`, `A2`, `A3`, `A4`, `B`
y `C`—, la rejilla tiene **120 celdas**. Cinco de las seis son variantes del bosque y cuestan segundos;
la red recurrente son veinte de las ciento veinte.

## 6.3 Coste computacional

Estimado a partir de lo medido en E7 y E6:

| Modelo | Punto más pequeño | Punto más grande | Por réplica, los cuatro puntos |
|---|---|---|---|
| Bosque, las cinco variantes de la escalera | segundos cada una | segundos cada una | menos de cinco minutos las veinte celdas |
| Red recurrente | ~20 s | ~135 s | ~5 min las cuatro celdas |

Cinco réplicas: **alrededor de media hora de cómputo** para las ciento veinte celdas, más el
preprocesado del conjunto, que se hace una vez. La calibración no añade ajustes nuevos, por lo que se
explica en `05-protocolo-comparacion.md`: se ajusta sobre la partición interna de desarrollo, que ya
existe para seleccionar la época, y no por validación cruzada. Entra holgadamente en una sesión de trabajo, lo que importa porque los
dos intentos fallidos de E19 murieron al cerrarse la sesión; las ejecuciones largas irán bajo `launchd`,
como la que funcionó.

El cómputo **no** es la restricción de esta fase. La restricción es no confundir variables.

## 6.4 Qué se resume, y cómo

Por cada celda de la rejilla se registra la ejecución completa con su cabecera —commit, semilla,
conjunto, punto de volumen, representación, modelo—. Sobre las cinco réplicas:

| Cantidad | Resumen | Por qué así |
|---|---|---|
| F1 macro, exactitud, exactitud equilibrada | **mediana y rango** (mínimo-máximo) entre las cinco | Con cinco valores la mediana es más honesta que la media y el rango dice más que una desviación típica |
| F1 por clase | mediana y rango, **por clase** | Es la cifra que responde a la pregunta del tutor |
| Diferencia entre modelos | **apareada por semilla**: para cada semilla, F1 del recorrido secuencial menos F1 del tabular; se reporta la mediana de las cinco diferencias y cuántas son positivas | Aparear elimina la variación de semilla de la comparación, que es la que confunde una diferencia de 0,0125 |
| Error de calibración | mediana y rango, antes y después de calibrar | |

**Intervalos de confianza.** Se dan solo si se piden explícitamente, y por **remuestreo de sesiones**
—la unidad de independencia—, con 1 000 réplicas, sobre la celda que se quiera describir. Se declarará
que describen el punto medido y no lo eligen, que es la misma cautela con que se trató el remuestreo
del umbral en E15b. Con siete sesiones por condición en validación, cualquier intervalo saldrá ancho, y
eso es información, no un defecto del cálculo.

**Lo que no se hará:** ninguna prueba de significación entre los dos modelos. Con cinco réplicas sobre
la misma partición de validación, las observaciones no son independientes entre réplicas —comparten las
ventanas— y una prueba daría un número sin sustento. La comparación apareada con su mediana y su
recuento de signos dice lo que se puede decir.

## 6.5 Criterio de integridad

Las cinco semillas de este documento aparecen en los registros de las **ciento veinte** celdas. Si un registro
trae una semilla que no está aquí, la celda se descarta y se documenta. La comprobación es automática y
va en una prueba, igual que la del anclaje de E19.
