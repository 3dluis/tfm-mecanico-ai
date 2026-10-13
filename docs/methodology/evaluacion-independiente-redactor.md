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
