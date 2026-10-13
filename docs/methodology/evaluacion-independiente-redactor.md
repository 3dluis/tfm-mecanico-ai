# Un conjunto de evaluación del redactor que ningún adaptador ha visto

**Fecha:** 13 de octubre de 2026 · **Qué fija:** las quince ventanas sobre las que se medirá al
redactor, congeladas **antes de que exista el adaptador que se va a medir** ·
**Congelación:** `configs/evaluacion-independiente-redactor.json`, huella de la selección
`9c114d92ef7d3ff1` · **Comprobable:** `tests/test_evaluacion_independiente.py`, nueve pruebas, seis de ellas en cualquier clon

## 1. Por qué hace falta, y por qué no basta con «otras ventanas»

La auditoría de contaminación midió que once de los diecisiete casos con que se evaluó al redactor
están sobre ventanas con las que el adaptador se ajustó. Reentrenar sin contaminación —P2— corrige
el ajuste, pero no resuelve el otro lado del problema: **sobre qué se mide al adaptador nuevo**.

Tres cosas quedan prohibidas de antemano, y conviene decir por qué cada una:

| Qué no se usa | Por qué |
|---|---|
| **Las cinco ventanas de evaluación de E15** | tres las vio el adaptador v2. Usarlas haría la comparación entre adaptadores injusta en favor del viejo, y la del nuevo irreproducible como medida de evidencia nueva |
| **La partición de prueba de `synthetic_v3`** | se ha abierto cinco veces. Una partición abierta cinco veces no es un conjunto plenamente independiente, y reutilizarla como si lo fuera sería la misma clase de error que esta auditoría descubrió |
| **Ventanas elegidas después de ver un resultado** | mediría la búsqueda, no al redactor |

## 2. Lo que se midió al buscar el conjunto, y es un hallazgo

La primera idea era evidente: usar validación de `synthetic_v2`, el mismo conjunto de E13 y E15,
descontando lo que el adaptador vio. Se midió:

```
validación de synthetic_v2:               98 ventanas en  12 sesiones
  − 9 sesiones que vio slm_lora_v2
  − 5 sesiones de la evaluación de E15
  ────────────────────────────────────────────────────────────────────
  quedan:                                 18 ventanas en   2 sesiones
  y las dos son de clase F00_normal: CERO ventanas de cualquier fallo
```

**Dentro de `synthetic_v2` no existe un conjunto independiente para evaluar al redactor.** No es
que sea pequeño: es que no hay ni una ventana de ninguna de las cinco clases de fallo que el
adaptador no haya visto, directa o indirectamente a través de su sesión.

Ese resultado dice algo sobre el diseño original que conviene no suavizar. Con doce sesiones de
validación y cuarenta y tres ventanas de ajuste tomadas de ahí, la partición quedó **consumida**
por el ajuste. La disyunción entre ajustar y medir no se perdió por descuido en una línea: se
perdió porque no había margen, y nadie lo comprobó.

## 3. De dónde sale el conjunto, entonces

De la partición de **validación de `synthetic_v3`**, que tiene 42 sesiones, excluyendo por
**sesión** —no por ventana— todo lo que cualquiera de los dos adaptadores ha visto o va a ver:

```
validación de synthetic_v3:              343 ventanas en  42 sesiones
  − las 9 sesiones que vio slm_lora_v2
  − las 5 sesiones de la evaluación de E15
  − las 48 sesiones de train de synthetic_v2, de donde salen los ejemplos de v3
  ────────────────────────────────────────────────────────────────────────────
  quedan:                                247 ventanas en  30 sesiones, seis clases
```

**Por sesión y no por ventana**, porque dos ventanas consecutivas de la misma sesión comparten la
mitad de sus muestras: excluir solo la ventana vista deja entrar la de al lado, que es casi la
misma. Es la misma razón por la que el reparto interno del ajuste de v3 se hace por sesión.

**Por qué validación de `synthetic_v3` sí.** Es la partición que no se ha abierto: E19 midió sobre
la de **prueba**. Y ninguno de los dos adaptadores tiene ejemplos de ahí —los de v2 salieron de
validación de `synthetic_v2`, los de v3 de su train—, de modo que los dos ven estas sesiones por
primera vez. Eso es lo que hace la comparación emparejada justa.

## 4. La regla de selección, escrita antes de aplicarla

> Para cada una de las cinco clases de fallo, las **tres sesiones de menor identificador** en orden
> lexicográfico entre las libres; de cada sesión, la **ventana de menor `t_start` con el fallo
> activo**.

Quince ventanas, quince sesiones distintas, una por sesión para que no solapen muestras entre sí.
La regla es determinista y no mira ninguna predicción, confianza ni veredicto.

**Dónde se puede comprobar qué, que es una distinción que la validación en un clon limpio obligó a
hacer.** Las entradas de la regla —las 43 ventanas que vio el adaptador, las 5 de la evaluación de
E15, las 48 sesiones de ajuste de `synthetic_v2`— están **registradas en la congelación**, porque
salen de `data/processed`, que no se versiona. Con ellas, seis de las nueve pruebas verifican la
selección y su exclusión en cualquier clon, sin un solo fichero no distribuido. Las otras tres
llevan el marcador `artefactos` y solo corren donde están los ficheros procesados: comprueban que
las entradas registradas siguen coincidiendo con ellos y que la regla, aplicada sobre
`synthetic_v3`, reproduce la huella.

**Y esa última comprobación tiene un límite que hay que declarar:** `synthetic_v3` **no es
reconstruible** —es pre-calibración (L-25)—, de modo que un tercero no puede rehacer la selección
desde el conjunto. Puede verificar la regla contra las entradas registradas, que es menos, y es lo
que hay.

| Clase | Ventanas |
|---|---|
| `F01_vacuum_leak` | `__highway__33@120s` · `__idle__18@120s` · `__urban__12@120s` |
| `F02_maf_drift` | `__highway__25@120s` · `__highway__33@120s` · `__idle__22@120s` |
| `F03_thermostat_stuck` | `__urban__20@120s` · `__urban__28@120s` · `__urban__32@120s` |
| `F04_o2_lag` | `__highway__25@120s` · `__idle__14@120s` · `__urban__32@120s` |
| `F05_misfire` | `__highway__21@120s` · `__highway__33@120s` · `__urban__16@120s` |

En las quince el fallo está activo, y los tres regímenes aparecen.

## 4 bis. Lo que hay que documentar antes de usarlo

El encargo pide seis cosas documentadas **antes** de utilizar este conjunto. Aquí están, y la última
es la que más acota lo que se podrá decir.

### 4 bis.1 Procedencia

Partición de **validación** de `synthetic_v3`, generado el 1 de septiembre de 2026 a las 14:58
locales con semilla 20260901 y 36 sesiones por condición. Las quince ventanas se eligen con la regla
de §4, determinista y comprobable. No se ha generado ningún dato para este conjunto.

### 4 bis.2 Distribución de condiciones

| | Este conjunto | La evaluación original de E15 |
|---|---|---|
| **Conjunto de datos** | `synthetic_v3` | `synthetic_v2` |
| **Ventanas distintas** | **15** | **5** |
| **Clases de fallo** | las cinco, **tres ventanas cada una** | las cinco, pero **desiguales**: termostato 5, sonda 5, fuga 5, caudalímetro 1, encendido 1 |
| **Regímenes** | autopista 6, urbano 6, ralentí 3 · **ninguno de calentamiento** | no equilibrados por diseño |
| **Condiciones de corpus** | **2**: `FULL` y `ABSENT` | **5**: `FULL`, `ABSENT`, `PARTIAL`, `DISTRACTOR`, `DISTRACTOR_NO_FILTER` |
| **Casos** | 30 | 17 |

**Qué gana y qué pierde respecto del original.** Gana en ventanas —quince frente a cinco— y en
equilibrio entre clases. **Pierde las tres condiciones de corpus que son el núcleo de PI.3 y PI.4**:
la parcial, que es la informativa, y las dos de distractor. Las quince ventanas no llevan conjunto
anotado con ficheros relevantes, de soporte y distractores declarados caso a caso, que es lo que
permite construir esas condiciones; construirlo exigiría anotar quince casos a mano contra el manual.

### 4 bis.3 Independencia respecto del entrenamiento

Verificado por construcción y comprobado con pruebas:

| Respecto de | Solape | Cómo se garantiza |
|---|---|---|
| Ejemplos de ajuste de `slm_lora_v2` | **cero sesiones** | sus 43 ventanas salen de validación de `synthetic_v2`; sus 9 sesiones están excluidas |
| Ejemplos de ajuste de `slm_lora_v3` | **cero sesiones** | salen de `train` de `synthetic_v2`; sus 48 sesiones están excluidas |
| Evaluación de E15 | **cero sesiones** | sus 5 sesiones están excluidas |
| Ajuste del **modelo de diagnóstico** | **las quince son de validación**, no de entrenamiento | el reparto es por sesión |

**Y una dependencia que no es cero y hay que declarar:** la **calibración** del modelo de diagnóstico
se ajusta con validación cruzada sobre entrenamiento, pero el **umbral** de confianza —0,79— se eligió
con un barrido sobre validación de `synthetic_v2`. Las confianzas de estos paquetes no son fuera de
muestra respecto de ese umbral.

### 4 bis.4 Las diferencias entre generadores, y por qué importan aquí

**Este conjunto sale de un generador distinto del de la evaluación original.** `synthetic_v3` es
**pre-calibración**: se generó antes del commit que calibró el generador contra el manual de taller.
Diferencias medidas entre los dos:

| | `synthetic_v2` | `synthetic_v3` |
|---|---|---|
| Generado | 14 de septiembre | **1 de septiembre, antes de la calibración** |
| Ralentí sin fallo, mediana | 690 rpm, dentro del rango 640–740 del manual | **820 rpm**, sin respaldo documental |
| Avance de encendido, primera muestra | 10,15° | 15,05° |
| `GENERATOR_VERSION` | `1.0.0` | `1.0.0` — **no los distingue** |
| Reproducible con el código publicado | **sí**, bit a bit | **no**: 0 de 216 sesiones idénticas |

**Consecuencia para el modelo de diagnóstico.** Medir sobre `synthetic_v3` exige un bosque ajustado
sobre el `train` de `synthetic_v3`, que **no es el modelo de E6 ni el de E19**. Los paquetes de
evidencia que el redactor recibirá vendrán de otro modelo, con otras confianzas y otras atribuciones.

### 4 bis.5 Alcance de las conclusiones posibles

Lo que una medición sobre este conjunto **podrá** sostener:

1. Una **comparación emparejada entre adaptadores** —`slm_lora_v2` frente al nuevo— sobre las mismas
   quince ventanas y los mismos paquetes de evidencia. Los dos las ven por primera vez, y esa es la
   pregunta que P2 hace.
2. Una descripción de **cuántas de las treinta salidas** son válidas, respetan el veredicto, no
   inventan citas y, si el validador numérico existe, no alteran cifras.

Lo que **no** podrá sostener, y conviene fijarlo antes de medir:

1. **Ninguna comparación con las cifras publicadas de E13 y E15.** Son otras ventanas, otras
   condiciones de corpus, otro conjunto de datos, otro generador y otro modelo de diagnóstico.
   **Cinco variables cambian a la vez.** Decir «el adaptador nuevo da 28 de 30 frente a 17 de 17 del
   viejo» sería comparar cosas distintas, y este documento lo prohíbe de antemano.
2. **Nada sobre PI.3 ni PI.4.** Faltan las condiciones parcial y de distractor.
3. **Ninguna estimación con intervalo útil.** Treinta casos sobre quince sesiones.
4. **Nada sobre el régimen de calentamiento**, que no está representado, y es justamente donde el
   termostato no se expresa.

### 4 bis.6 Por qué, aun así, vale

Porque la pregunta que P2 hace no es «¿cuánto vale el redactor?» sino **«¿cuánta de la calidad
atribuida al redactor venía de haber visto los casos?»**, y eso solo se responde con un conjunto que
ninguno de los dos adaptadores haya visto. Este lo es, y dentro de `synthetic_v2` no existe.

**No es una evaluación equivalente a la original y no se presentará como tal.** Es una medición nueva,
con su propio alcance, que responde a una pregunta que la original no podía responder.

## 5. Qué se mide y qué no

**Qué se mide:** en dos condiciones de corpus —`FULL` y `ABSENT`, treinta casos— tres cosas del
texto producido: si la salida es válida contra el esquema, si respeta el veredicto del verificador y
si inventa alguna cita. Comparación **emparejada por caso** entre `slm_lora_v2` y el adaptador nuevo.

**Qué no se mide, y es importante no confundirlo.** No se mide la calidad del diagnóstico. El modelo
de diagnóstico se ajustó sobre train de `synthetic_v3` y su calibración usó validación, de modo que
**las confianzas de estos paquetes no son fuera de muestra**. Lo que estas quince ventanas evalúan
es el texto del redactor ante paquetes de evidencia que no ha visto, no el acierto de la predicción
que los encabeza.

## 6. Lo que este conjunto no permitirá afirmar

1. **Nada sobre generalización** a otros vehículos, motores o corpus: son quince sesiones sintéticas
   del mismo generador.
2. **Ninguna estimación con intervalo útil.** Treinta casos sobre quince sesiones describen treinta
   situaciones. Si el resultado fuera 30/30, el intervalo de Wilson al 95 % llega hasta 0,88 por
   abajo: compatible con un redactor que falla uno de cada ocho.
3. **No corrige las cifras de E13 ni de E15.** Serían otras medidas, de otro adaptador, sobre otro
   conjunto. Las de E13 y E15 conservan su marca de afectadas; no se recalculan ni se retiran.

## 7. Cuándo deja de ser válido

- Si la regla de selección se cambia después de ver un resultado.
- Si alguna de estas quince sesiones se usa para ajustar cualquier adaptador.
- Si la huella de la selección deja de coincidir al reejecutar la regla: entonces algo cambió en el
  reparto y hay que pararse antes de medir nada.

## 8. Estado

**Congelado y no ejecutado.** El adaptador que había que medir no existe: su ajuste se detuvo por
memoria insuficiente, con la causa medida en
[`incidencia-p2-02.md`](../experiments/incidencia-p2-02.md). El conjunto queda listo y comprobado
para cuando haya adaptador, y su valor no depende de que lo haya: lo que fija es **cómo** se medirá,
decidido cuando todavía no se podía elegir en función del resultado.
