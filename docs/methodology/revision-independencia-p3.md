# Revisión de independencia antes de repetir E18 sobre el conjunto de prueba

**Fecha:** 12 de octubre de 2026 · **Qué autoriza, si pasa:** una **cuarta apertura** del conjunto de
prueba, para repetir las cuatro ablaciones de E18 ya definidas · **Qué no autoriza:** nada más.

El conjunto de prueba ya se abrió tres veces durante E19. Una cuarta apertura tiene que justificarse
antes, no después, y el riesgo concreto a descartar es que sus resultados acaben usándose para
modificar el sistema. Esta revisión comprueba las siete condiciones una a una, con la evidencia al
lado, **antes** de ejecutar nada.

## Las siete condiciones

### 1. El protocolo original existe y es verificable

`docs/methodology/preregistro-e18-ablaciones.md`, huella `7874e971d37faa73`. Define las cuatro
ablaciones, qué cambia cada una, qué mide, qué métricas se publican y cómo se interpreta cada
desenlace posible —incluido que una ablación **mejore** una tasa, que se publica «igual y sin
reinterpretarla»—.

**CUMPLE.**

### 2. Las ablaciones estaban definidas antes de observar el test

| Hito | Momento |
|---|---|
| Pre-registro de E18 congelado | **1 de octubre, 12:38** (`fc0fa89`) |
| Ejecución de E18 sobre validación | 1 de octubre (`67b09e2`) |
| **Primera apertura del conjunto de prueba** | **2 de octubre, ~02:31 UTC** (`v1`, interrumpida) |
| Medición completa sobre prueba | 12 de octubre (`v3`) |

El pre-registro es **anterior** a la primera apertura y **no se ha modificado desde**: su historial
tiene dos commits, los dos del 1 de octubre.

`src/mecanico_ia_exp/experiments/ablation_runner.py` sí cambió después, el 12 de octubre. Revisado el
`diff` completo entre `9189a87` y `HEAD`: **cincuenta y tres líneas añadidas, todas de
infraestructura** —destinos con etiqueta, parámetro de partición, el motivo de apertura en el
registro—. **Ni una toca `ABLACIONES`, `CAMBIO_OPERATIVO`, los umbrales ni la lógica de decisión.**

**CUMPLE.**

### 3. No se ajustarán hiperparámetros

`src/mecanico_ia_exp/abstention/sufficiency.py`, donde viven los umbrales, **no se modifica desde el
4 de septiembre**: `git log --since=2026-10-02` sobre ese fichero devuelve vacío. Los umbrales son
los congelados —confianza 0,79, cobertura 0,80, 2 fragmentos, 1 fuente— y el ejecutor los toma de
`SufficiencyThresholds()` sin parámetro que los altere desde la línea de órdenes.

**CUMPLE.**

### 4. No se seleccionarán variantes después de observar resultados

Las cuatro ablaciones están fijadas en el código y en el pre-registro. Se ejecutan **las cuatro**, no
una selección. La regla de selección de ventana —`seleccionar_ventana`— es determinista y está
congelada desde el 4 de septiembre: en modo oracular toma la **primera ventana correctamente
clasificada** de cada condición, sin intervención humana.

**CUMPLE**, con una salvedad que se declara en el apartado siguiente.

### 5. La nueva apertura queda registrada

Se escribe en `docs/methodology/registro-aperturas-test.md` **antes** de ejecutar, con la misma
estructura que las tres anteriores: motivo, configuración, alcance, exposición, métricas y si influyó
en alguna decisión.

**CUMPLE**, por construcción: la entrada es parte de este bloque de trabajo y precede a la orden.

### 6. Las métricas y los criterios están definidos

En el pre-registro: decisión por caso con su motivo, falsa confianza y abstención innecesaria **con
su número de ejecuciones y de ventanas independientes**, cobertura sobre los casos con evidencia
completa, fragmentos aplicables y cobertura de afirmaciones. Y los dos desenlaces posibles con su
lectura fijada de antemano.

**CUMPLE.**

### 7. Los artefactos históricos permanecerán intactos

Tres mecanismos, ninguno de buena voluntad:

1. **Sobre una partición distinta de validación la etiqueta es obligatoria**: el ejecutor falla sin
   ella.
2. **Los destinos se comprueban antes de escribir el primero** y se niega a sobrescribir.
3. **El censo de 142 artefactos** se verifica después, y una desviación detiene el bloque.

**CUMPLE.**

## Dos salvedades que hay que declarar, y no son menores

### El analista ya ha visto los resultados de E19 sobre prueba

No se puede deshacer. Las ablaciones están pre-registradas y el código congelado, de modo que
**ninguna decisión del experimento** puede contaminarse: no hay nada que elegir en tiempo de
ejecución. Lo que sí ocurre con conocimiento previo es la **interpretación**.

Por eso la lectura de los resultados se limita a lo que el pre-registro ya fijó, y esta revisión deja
escrito, antes de medir, qué se hará con cada desenlace:

- si una ablación **empeora** la falsa confianza sobre prueba, confirma lo medido en validación;
- si alguna **mejora** una tasa, se publica igual y **sin reinterpretarla**;
- si los resultados **difieren** de los de validación, se publica la diferencia **sin corregir
  nada**: sería un hallazgo sobre la estabilidad del criterio, no un motivo para ajustarlo.

**Lo que no se hará en ningún caso:** usar estos resultados para rediseñar P1, ajustar P2, mover un
umbral o cambiar la política. Esa restricción es del encargo y se asume como condición de la
ejecución.

### E18 sobre prueba no es una estimación operativa

La regla de selección elige ventanas que **el modelo clasifica bien**, consultando sus predicciones.
Es la misma limitación que E19 declaró para su estrato comparativo: las ventanas se eligen mirando al
modelo, de modo que el resultado describe el comportamiento en condiciones favorables y **no estima
ninguna tasa poblacional**.

Esto estaba así en el pre-registro de E18 y no es un defecto nuevo. Pero conviene escribirlo aquí
para que el resultado sobre prueba no se lea como si fuera del estrato operativo de E19, que sí
eligió sus ventanas sin consultar al modelo.

## Qué aporta esta ejecución, y qué no

**Aporta** una respuesta a una pregunta que el pre-registro ya planteaba: si lo que las ablaciones
mostraron sobre validación —que retirar el criterio de suficiencia lleva la falsa confianza de 0 a 6
de 9, y que un umbral único la lleva a 9 de 9— se sostiene fuera de la partición con la que se
ajustó el criterio.

**No aporta** ninguna estimación nueva de las tasas del sistema, ni ningún motivo para cambiarlo.

## Veredicto

**Las siete condiciones se cumplen.** Se procede, con las dos salvedades declaradas y la entrada de
apertura escrita antes de la orden.

Si alguna no se hubiera cumplido, la alternativa prevista era no ejecutar y publicar las ablaciones
solo sobre validación, declarando que su validez fuera de ella no se comprobó. No ha hecho falta.
