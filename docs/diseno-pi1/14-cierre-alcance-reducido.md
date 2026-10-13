# Cierre documental de PI.1 con el alcance reducido

**Fecha:** 13 de octubre de 2026 · **Qué cierra:** PI.1, con el alcance que el autor aprobó el 13 de
octubre · **Qué queda aplazado:** `synthetic_v4`, la curva de volumen y las comparaciones extensivas
· **Qué NO se ha ejecutado:** la fase F. Ni una celda

## 1. Lo aprobado, y qué estado tiene cada pieza

| Fase | Decisión del autor | Estado real al cerrar |
|---|---|---|
| **A** · correcciones de E7 y E2 | mantener | **hecha.** Las tres marcas de E7 —`CORRECTED-E7-01`, `SUPERSEDED-E7-02`, `SUPERSEDED-E7-03`— y la de la fila E2 están aplicadas y fechadas el 12-10-2026, con el texto anterior conservado |
| **B** · protocolo de `synthetic_v4` y manifiesto | aplazar la generación | el **manifiesto de procedencia está construido, probado y en uso**; `synthetic_v4` no se genera |
| **C** · subconjuntos anidados | aplazar | el código existe (`data/interno.py`) y pasa sus pruebas; sin `v4` no hay nada que repartir |
| **D** · protocolo de comparación simétrica | conservar como diseño | escrito, sin ejecutar |
| **E** · réplicas y semillas | conservar el pre-registro | las cinco semillas están declaradas en `configs/semillas_pi1.json`; su uso se evalúa aparte (§4) |
| **F** · ablación de representación | **no ejecutar todavía**; evaluar antes su valor científico | **no ejecutada.** La evaluación está en [`15-valor-cientifico-de-f.md`](15-valor-cientifico-de-f.md) |
| **G** · análisis por fallo | integrar con A | **hecha, y es el resultado de este cierre.** §2 |
| **H** · conclusiones afectadas | usar la matriz existente | **fundida** con `docs/audits/matriz-impacto-cap5-cap6.md`, que cubre los dos capítulos completos |
| **I** · plan de reejecución | reducir | reducido a lo de esta tabla |

## 2. Fase G: por qué el bosque acierta donde acierta

Esta es la medición que el cierre aporta, y no necesitó ningún experimento nuevo: es el **instrumento
de expresión efectiva del fallo** aplicado a la **misma partición de validación** de la que salen las
cifras publicadas de E6 y E7.

**Qué se midió.** Para cada una de las 70 ventanas de validación etiquetadas con un fallo —catorce
por condición— cuántas de sus 120 muestras **alteran de verdad la trayectoria** respecto del
contrafactual sin fallo. El indicador se deriva del **generador**, no del modelo, que es el criterio
de integridad que la fase G exigía.

| Fallo | Ventanas etiquetadas | **Sin ninguna señal** | Parcialmente expresadas | Plenamente expresadas | Aciertos del bosque |
|---|---|---|---|---|---|
| F01 fuga de vacío | 14 | 0 | 0 | **14** | **14 de 14** |
| F02 deriva de caudalímetro | 14 | 0 | 1 | 13 | **14 de 14** |
| **F03 termostato** | 14 | **5** | 2 | 7 | **9 de 14** |
| F04 sonda lenta | 14 | 0 | 0 | **14** | **14 de 14** |
| **F05 fallo de encendido** | 14 | 0 | **14** | **0** | **7 de 14** |

*Aciertos del bosque: `recall × soporte` de `experiments/E6_baseline_synthetic_v2.json`. Expresión:
instrumento de `obd/expresion.py` sobre las sesiones reconstruidas desde su `SessionSpec`, que
`synthetic_v2` reproduce bit a bit.*

### Qué se puede leer en esa tabla

**Las tres condiciones que el bosque acierta por completo son las tres que están plenamente
expresadas.** Y las dos que falla son las dos únicas con un problema de expresión, cada una de una
clase distinta:

- **El termostato tiene cinco ventanas sin ninguna señal.** Las cinco son de la misma sesión,
  `F03_thermostat_stuck__warmup__03`, y las cinco consecutivas: de los 120 a los 479 segundos. La
  razón es física y ya estaba descrita: en calentamiento el motor arranca a temperatura ambiente y
  tarda minutos en llegar al tope de 71 °C que el fallo impone; hasta entonces la señal averiada es
  **idéntica** a la sana. La otra sesión del termostato en validación, `__urban__08`, está plenamente
  expresada en sus siete ventanas, y ahí no hay nada que explicar.
- **El fallo de encendido no tiene ninguna ventana plenamente expresada.** Las catorce son parciales,
  y la fracción de muestras alteradas va del 1,7 % al 13 %: entre 2 y 16 muestras de 120. Es
  episódico por construcción, con episodios de 1 a 3 segundos y una tasa de aparición del 2 % por
  segundo.

### Una coincidencia aritmética que **no** se presenta como hallazgo

El bosque falla **exactamente cinco** ventanas del termostato, y **exactamente cinco** ventanas del
termostato no contienen ninguna señal del fallo. La tentación de decir que son las mismas cinco es
evidente, y **no se hace**: los registros de E6 no guardan las predicciones por ventana, de modo que
no se sabe cuáles falló. La comprobación es barata —una reejecución de E6 con predicciones por
ventana, con destino propio y sin sobrescribir el registro histórico— y **no se ha ejecutado**,
porque el alcance aprobado cubre las correcciones documentales y no nuevas ejecuciones.

Mientras no se haga, lo que se puede afirmar es más débil y sigue siendo útil: **el rendimiento por
clase del bosque se ordena igual que la expresión efectiva del fallo**, y las dos condiciones que
falla son las dos que tienen un problema de expresión.

### Qué cambia esto en la lectura de E7

El capítulo 5 dice que el modelo temporal «por clase acierta dos ventanas más en el termostato
bloqueado, 11 de 14 frente a 9 de 14». Las dos cifras se derivan de los registros vigentes
—`recall × soporte`— y son correctas. Lo que la fase G añade es **dónde** está esa diferencia: el
termostato es el único fallo con ventanas sin señal, y siete de sus catorce ventanas vienen de una
sesión de calentamiento donde cinco no contienen nada observable.

**La hipótesis que eso sugiere**, y que se enuncia como hipótesis: la ventaja de dos ventanas del
modelo temporal podría estar en ventanas donde el fallo no se expresa, en cuyo caso no sería una
ventaja de representación sino una regularidad de la sesión o del régimen. **No está comprobada**, y
lo que la comprobaría es la misma reejecución del párrafo anterior.

**Y lo que la tabla sí deja establecido sin hipótesis:** el modelo temporal **no** mejora en agregado
—0,8230 de F1 macro frente a 0,8788— y por clase es **peor** en tres de las seis: normal (25 de 28
frente a 28 de 28), caudalímetro (12 de 14 frente a 14 de 14) y encendido (5 de 14 frente a 7 de 14).
Su única ventaja es el termostato. Decir «acierta dos ventanas más en el termostato» sin decir que
pierde seis repartidas en tres clases es una lectura parcial, y el capítulo 5 debería recogerlo.

## 3. Qué queda sin responder, con nombre

| Pregunta | Por qué queda abierta | Dónde está su diseño |
|---|---|---|
| ¿Mejora el estimador recurrente con más datos? | la curva de volumen no se ejecuta | `04-subconjuntos-anidados.md`, `05-protocolo-comparacion.md` |
| ¿Aporta el contexto temporal, aislado del estimador? | exigiría un diseño 2×2 que **amplía el alcance del TFM** y que el paquete declinó proponer | — |
| ¿Son las cinco ventanas falladas las cinco sin señal? | los registros de E6 no guardan predicciones por ventana | `08-analisis-por-fallo.md` §8.3 |
| Las cifras 54,3 °C y 70,7 °C del termostato | **siguen sin registro** y siguen marcadas como no utilizables. Dependen de las predicciones por ventana | `08-analisis-por-fallo.md` |
| ¿Cuánto varía el resultado entre semillas? | el trabajo es de ejecución única | §4 y [`15-valor-cientifico-de-f.md`](15-valor-cientifico-de-f.md) |

## 4. Las réplicas, que es lo que el autor pide evaluar aparte

La ausencia de réplicas es una limitación del trabajo y el autor la nombra como importante. La
evaluación de si hay un conjunto mínimo de réplicas posible **sin reabrir conjuntos de prueba ni
ampliar el alcance** está en [`15-valor-cientifico-de-f.md`](15-valor-cientifico-de-f.md), junto con
la evaluación del valor científico de la fase F que el encargo exige antes de descartarla.

## 5. Qué no se ha hecho, para que conste

- **No se ha generado `synthetic_v4`.** El riesgo 16 del propio paquete lo decía: `v2` y `v3` no se
  regeneran, y crear un tercer conjunto canónico dos meses antes de entregar añade ocasiones de
  error. La validación en un clon limpio del 13 de octubre mostró que un conjunto con el mismo nombre
  y otro contenido **pasa las pruebas**, porque el ventanado y el reparto reproducen aunque las
  señales no.
- **No se ha ejecutado la fase F.** Ni una celda de las ciento veinte.
- **No se ha reejecutado E6 ni E7.** Las cifras de la tabla de §2 salen de sus registros vigentes.
- **No se ha tocado ningún conjunto histórico**, ningún registro y ninguna partición de prueba.
