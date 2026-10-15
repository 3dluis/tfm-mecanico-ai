# Informe del trabajo práctico

**Trabajo Fin de Máster en Inteligencia Artificial · Luis Daniel Díaz · octubre de 2026**

Este informe resume qué hay en el repositorio, qué resultados sostiene y hasta dónde llegan. Está
escrito para quien abre el repositorio sin haber leído la memoria: el README explica cómo ejecutar
las cosas, y esto explica **qué se midió y qué permite afirmar**.

> **Estado: borrador para revisión del tutor.** Y una advertencia que atraviesa todo lo que sigue:
> la telemetría es **sintética**. Nada de lo medido aquí describe un vehículo real.

---

## 1. La pregunta

> ¿Puede un agente con RAG explicar el diagnóstico de un vehículo a partir de datos OBD-II,
> rastreando cada explicación hasta su evidencia de origen, y reconocer cuándo la evidencia
> disponible no es suficiente para sostener una explicación en lugar de generar una hipótesis sin
> fundamento?

Tiene tres partes, y conviene separarlas porque se miden de maneras distintas y con distinta
solidez:

| | Qué pregunta | Cómo se mide aquí |
|---|---|---|
| **Explicar** | si el sistema produce una explicación a partir de un diagnóstico obtenido de la telemetría | métricas de clasificación y de calibración |
| **Rastrear** | si cada afirmación de la explicación se puede seguir hasta la observación y el fragmento que la sostienen | recuentos de anclaje sobre casos anotados |
| **Abstenerse** | si reconoce cuándo la evidencia no alcanza y se calla | dos tipos de error sobre el conjunto de prueba |

La tercera es la que da sentido al trabajo. Un sistema que explica siempre no resuelve el problema
que motiva la pregunta: una explicación plausible y sin fundamento es indistinguible de una buena
para quien no puede comprobarla, y el taller es un sitio donde no se comprueba.

## 2. Qué hace el sistema

```
telemetría OBD-II → ventanas → descriptores → modelo de diagnóstico → atribución
                                                                          ↓
                                       recuperación sobre el manual de taller
                                                                          ↓
                                   verificador determinista de suficiencia
                                                                          ↓
                                            explicar  ·  o  ·  abstenerse
```

Dos decisiones de diseño gobiernan el resultado. **La decisión de explicar o callar no la toma el
modelo de lenguaje**: la toma un verificador determinista que comprueba la confianza del diagnóstico
y el soporte documental de cada afirmación. Y **la evidencia tiene que ser aplicable al vehículo**:
el manual documenta tres motores emparentados, de modo que un procedimiento puede llevar el código
de avería correcto y no servir para el motor que se tiene delante.

## 3. Los resultados, con sus denominadores

**Diagnóstico**, sobre 98 ventanas de validación procedentes de 12 sesiones:

| Modelo | F1 macro | Exactitud |
|---|---|---|
| Clase mayoritaria | 0,0741 | 0,2857 |
| **Bosque aleatorio** | **0,8788** | 0,8776 |
| GRU bidireccional | 0,8230 | — |

**El modelo temporal no superó a la línea base.** Es un resultado negativo, se conserva, y el
trabajo lo declara en lugar de buscarle una explicación favorable.

**Evaluación final**, sobre el conjunto de prueba, ejecutada el 12 de octubre de 2026 con un
conjunto anotado sellado antes de abrir la partición:

| Qué | Resultado | Unidades independientes |
|---|---|---|
| Falsa confianza · explicar debiendo callar | **0 de 14** | 7 ventanas, 7 sesiones |
| Abstención innecesaria · callar debiendo explicar | **2 de 8** | 8 ventanas, 8 sesiones |
| Cobertura con evidencia completa | **6 de 10** | 10 ventanas, 10 sesiones |

**El cero no es riesgo cero.** Con catorce ejecuciones, el intervalo de Wilson al 95 % de esa tasa
nula llega hasta **0,215**, y las catorce proceden de siete ventanas, de modo que el intervalo real
es más ancho. Lo medido es que en esa muestra no ocurrió.

La cobertura importa tanto como el cero. Un sistema que se abstuviera siempre también obtendría
0 de 14, y sería inútil. Explicar seis de diez con evidencia completa es lo que descarta esa
lectura.

## 4. El dictamen, y lo que no significa

Las cuatro subpreguntas cumplen el criterio que el capítulo 4 de la memoria les asigna, y la regla
de respuesta global declara ese cumplimiento suficiente. **La pregunta queda sostenida dentro de las
condiciones experimentales evaluadas.** Cuatro lecturas, que conviene no mezclar:

- **Cumplimiento de criterios operativos.** Es lo que el dictamen establece.
- **Validez de las mediciones.** Desigual: dos subpreguntas tienen medición sobre el conjunto de
  prueba, una se cumple por construcción del recorrido y otra está medida sobre tres casos
  construidos.
- **Fuerza confirmatoria.** Es la lectura más débil, y no depende de los resultados. **Tres de los
  cuatro criterios se reformularon después de conocerse parte de los resultados**, y el de la
  primera subpregunta un día después de medirse que el modelo temporal no superaba a la línea base.
  El dictamen **no es una confirmación independiente del protocolo original**.
- **Alcance de la generalización.** Telemetría sintética de un vehículo, cinco mecanismos de fallo
  de un catálogo cerrado, ventanas que el modelo diagnostica correctamente.

## 5. Lo que este trabajo no sostiene

Lo incómodo va aquí, y no en una nota al pie.

**La trazabilidad está verificada en las citas, no en las cifras.** Las tres barreras del recorrido
comprueban que el identificador citado se entregara; ninguna comprueba que el número escrito sea
cierto. En la evaluación final, **siete de las treinta y cinco salidas** del redactor contienen al
menos una cifra que el verificador no produjo: seis afirmaciones distintas transcriben con un dígito
distinto el valor que citan correctamente, y cinco motivos de abstención llevan una cifra sin
origen, incluido uno que compara un valor y un umbral que no figuran en el registro del caso.
Ninguna tasa cambia por ello —las produce el verificador determinista—, pero el texto que el usuario
lee no está garantizado. La corrección está propuesta y **sin implementar**.

**Una de las cuatro ablaciones quedó inconclusa.** La que debía medir qué aporta la recuperación
semántica no midió nada, porque la ruta léxica no recupera con una consulta en prosa. Se conserva
como inconclusa, sin reformularla a posteriori.

**El conjunto de prueba se abrió cinco veces**, cuatro de ellas con exposición de etiquetas y
predicciones. Lo que sostiene la medición final es que el instrumento no cambió entre la primera
apertura y la medición, y eso se comprueba con una orden.

**El adaptador del modelo de lenguaje está contaminado** en la fase de suficiencia: once de
diecisiete casos están sobre ventanas que entraron en su ajuste. Su solape con la evaluación final
es cero.

**Dos de los tres conjuntos sintéticos no se reconstruyen** con el generador publicado, porque son
anteriores a su calibración. El canónico, del que salen todas las cifras publicadas, **sí se
reconstruye bit a bit**.

**La correspondencia entre afirmación y evidencia no se ha contrastado con un juicio experto.** Se
cumple por construcción del verificador, y si sus comprobaciones coinciden con lo que un mecánico
consideraría soporte suficiente no se ha medido.

## 6. Cómo comprobar todo esto sin creerse nada

```bash
bash scripts/instalar.sh                       # dependencias
uv run python scripts/verificar_entrega.py     # 238 comprobaciones sobre el paquete
uv run pytest                                  # 527 pruebas
uv run python scripts/figuras_memoria.py       # regenera las figuras desde los registros
```

Cada figura del documento declara el experimento, el conjunto, la partición y el notebook que la
produce, y **notebook y documento invocan la misma función de Python**. Los notebooks de
`notebooks/html/` se abren en un navegador sin instalar nada y traen dentro sus figuras, sus cifras
y la interpretación de cada una, con sus limitaciones.

Ninguna figura se ha dibujado a mano ni se ha generado con IA: todas salen de un registro de
ejecución o de una tabla versionada, por código que está en `src/`.

## 7. Qué hay en el historial

Los **447 commits** anteriores a esta publicación conservan sus identificadores originales: el
repositorio se construyó por clonación, **sin reescritura**. Eso permite comprobar que esta copia es
la del repositorio de trabajo.

En ese historial está también `docs/`, el laboratorio completo —metodología, auditorías,
pre-registros, incidencias y el texto fuente de la memoria—, retirado del árbol para que el paquete
presente el trabajo práctico y no el cuaderno de obra. Se recupera con una orden:

```bash
git log --oneline -- docs | head -5
git checkout <commit> -- docs
```

**La memoria académica no viaja en el árbol de esta copia** y se entrega por su propio cauce. Sus
versiones están en el historial.

---

*Lo que aquí se publica describe el comportamiento de un sistema sobre telemetría sintética de un
vehículo de referencia. No es un producto, no está validado para uso en taller, y ninguna de sus
cifras debe leerse como una propiedad del sistema fuera de las condiciones en que se midió.*
