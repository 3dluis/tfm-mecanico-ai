# E18 sobre el conjunto de prueba — P3

**Fecha de ejecución:** 13 de octubre de 2026, 04:12 UTC · **Commit:** `6d9fdc0` ·
**Pendiente del tutor:** P3 · **Partición:** **prueba**, cuarta apertura ·
**Revisión previa:** [`revision-independencia-p3.md`](../methodology/revision-independencia-p3.md),
las siete condiciones verificadas antes de ejecutar ·
**Registro de la apertura:** [`registro-aperturas-test.md`](../methodology/registro-aperturas-test.md),
fila 4, escrita antes de la orden

Las cuatro ablaciones congeladas el 1 de octubre, repetidas sobre la partición de prueba. Ni una
definición, ni un umbral, ni una variante se tocaron: el `diff` del ejecutor entre la ejecución
publicada y esta son cincuenta y tres líneas de infraestructura.

Los artefactos llevan etiqueta `prueba` y **no sustituyen** a los del 1 de octubre:
`experiments/E18_ablacion_A{1..4}_prueba.json` y `tables/E18_ablacion_A{1..4}_prueba.csv`.

## Resultado

| Ablación | Falsa confianza | Abstención innecesaria | Cobertura con evidencia completa |
|---|---|---|---|
| **Canónica** (criterio compuesto, umbral 0,79) | 0 de 9 | 2 de 5 | 3 de 5 |
| `A1` sin atribución | 0 de 9 | 2 de 5 | 3 de 5 |
| `A2` sin recuperación semántica | 0 de 9 | 5 de 5 | 0 de 5 |
| `A3` sin criterio de suficiencia | **6 de 9** | 0 de 5 | 5 de 5 |
| `A4` umbral único | **9 de 9** | 2 de 5 | 3 de 5 |

Las nueve ejecuciones que deben abstenerse proceden de **tres ventanas** y las cinco con evidencia
completa, de cinco; las diecisiete salen de **cinco sesiones distintas**. Las tasas describen esta
muestra y no estiman nada.

## Lo que hay que mirar antes de interpretar: coinciden con validación en todo

**Las doce tasas son idénticas a las del 1 de octubre. Y no solo las tasas: las 68 decisiones
—diecisiete casos por cuatro ablaciones— coinciden una a una.**

Un resultado así obliga a comprobar que no hay reutilización antes que a celebrarlo.

### No hay reutilización: las ventanas son otras

| Caso | Ventana en validación | Ventana en prueba |
|---|---|---|
| `C01_maf_drift` | `F02_maf_drift__highway__01@120s` | `F02_maf_drift__highway__05@120s` |
| `C02_thermostat_stuck` | `F03_thermostat_stuck__urban__08@120s` | `F03_thermostat_stuck__highway__01@120s` |
| `C04_misfire` | `F05_misfire__highway__09@180s` | `F05_misfire__highway__05@120s` |
| `C05_vacuum_leak` | `F01_vacuum_leak__idle__10@120s` | `F01_vacuum_leak__highway__05@120s` |

Sesiones distintas, instantes distintos, regímenes distintos. Y las confianzas del modelo también
difieren: `C01` pasa de 0,5999 a 0,5731 y `C04` de 0,4621 a 0,4905.

### Por qué coinciden de todos modos, y por qué eso resta valor al resultado

Esta es la parte que importa, y es deflacionaria.

**La decisión de cada caso está determinada casi por completo por cosas que no cambian al cambiar de
partición:**

1. **La condición de evidencia** —`FULL`, `PARTIAL`, `ABSENT`, distractor— se construye **excluyendo
   documentos en el momento de la consulta**, no alterando los datos. Es idéntica en las dos
   particiones por definición.
2. **La recuperación** parte de la misma consulta sobre el mismo corpus, así que el número de
   fragmentos aplicables es el mismo: 6, 8, 6, 4, 7 para los cinco casos con evidencia completa, en
   las dos ejecuciones.
3. **La puerta de códigos** en modo oracular deriva los DTC de la etiqueta anotada, que es la misma.

**Lo único que varía con la ventana** es la confianza del modelo y la cobertura de afirmaciones. Y
esas solo cambian una decisión si **cruzan un umbral**. No lo cruzan: los casos que explican tienen
confianza 1,000 en las dos particiones, y los dos que fallan —`C01` y `C04`— se quedan por debajo de
0,79 en las dos, con valores distintos pero del mismo lado.

**Conclusión honesta:** que las cuatro ablaciones den lo mismo sobre prueba **no es una confirmación
independiente sobre datos nuevos**. Es, en buena medida, la consecuencia de que el experimento mida
la **arquitectura del criterio** —qué pasa si se retira un componente— y la arquitectura no depende
de qué ventana se use. Era más esperable que sorprendente, y presentarlo como «el resultado se
replica en prueba» sería leer de más.

Lo que sí añade, y es poco pero no es nada: que las dos condiciones difíciles del conjunto se
comportan igual en las dos particiones, con ventanas distintas. Es el mismo hecho que la auditoría de
E19 ya había encontrado, con `n = 2`.

## Lo que el pre-registro fijó que se diría de cada desenlace

Se escribió el 1 de octubre y se repite aquí porque es lo que gobierna la lectura:

> «Una ablación **empeora** la falsa confianza → el componente contribuye a evitar el error de mayor
> riesgo, y la magnitud se publica con su denominador.»

`A3` la lleva de 0 a **6 de 9** y `A4` a **9 de 9**. El criterio compuesto y la puerta de cobertura
son, por tanto, los componentes que evitan el error de mayor riesgo, también sobre prueba.

> «Una ablación **mejora** alguna tasa → se publica igual y sin reinterpretarla.»

`A3` lleva la abstención innecesaria a **0 de 5** y la cobertura a **5 de 5**: retirar el criterio de
suficiencia hace que el sistema responda siempre que haya un fragmento aplicable. Se publica sin
reinterpretar: es la otra cara de sus 6 de 9 de falsa confianza, y el intercambio es exactamente lo
que el criterio existe para resolver.

## Resultados negativos y limitaciones

1. **`A1` no cambia nada.** Sustituir la importancia de Shapley por la desviación tipificada produce
   las diecisiete mismas decisiones. La atribución, tal como el recorrido la usa, **no contribuye a
   la decisión**. Ya se midió sobre validación y se confirma sobre prueba.
2. **`A2` deja el sistema mudo.** Sin recuperación semántica se abstiene en los diecisiete casos:
   abstención innecesaria 5 de 5 y cobertura 0 de 5. Útil como control, no como alternativa.
3. **Los denominadores son 9, 5 y 5.** Un solo caso mueve la abstención innecesaria en 0,2.
4. **Tres ventanas independientes** sostienen las nueve ejecuciones que deben abstenerse.
5. **No es una estimación operativa.** La regla de selección elige ventanas que el modelo clasifica
   bien, consultando sus predicciones: describe el comportamiento en condiciones favorables. Es la
   misma limitación que E19 declaró para su estrato comparativo.
6. **La condición con distractor sigue invalidada.** Las cifras entre paréntesis del pre-registro
   —9 de 12 y 12 de 12 incluyéndola— se conservan por continuidad, pero esa condición no mide lo que
   dice medir mientras no se rediseñe (P1).
7. **El analista ya había visto los resultados de E19.** Declarado antes de ejecutar: no hay decisión
   que contaminar, porque no hay nada que elegir en tiempo de ejecución, pero la interpretación
   ocurre con conocimiento previo.

## Integridad

| Comprobación | Resultado |
|---|---|
| Artefactos del 1 de octubre | **intactos**; los nuevos llevan etiqueta `prueba` |
| Censo de artefactos históricos | **0 desviaciones** antes y después |
| Umbrales | los congelados; `sufficiency.py` sin cambios desde el 4-09 |
| Definiciones de las ablaciones | sin cambios desde el pre-registro |
| Conjunto anotado | huella `7fadc49fc7daaad1`, la congelada |

## Qué queda, y qué no se hace con esto

**Cerrado:** P3, el tercero de los pendientes del tutor.

**Lo que estos resultados no autorizan**, por condición de la ejecución y porque está escrito antes
de medir: rediseñar la condición con distractor (P1), ajustar el reentrenamiento del adaptador (P2),
mover un umbral o cambiar la política canónica.
