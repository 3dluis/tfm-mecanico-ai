# 2. Protocolo del conjunto canónico `synthetic_v4` (Fase B)

**Estado: diseño. No se ha generado nada.** Este documento es el protocolo que el autor revisa antes de
que se ejecute una sola orden del generador.

## 2.1 Por qué hace falta un conjunto nuevo, y por qué no sustituye al actual

Hace falta porque el único conjunto grande que existe, `synthetic_v3`, se generó antes de calibrar el
generador contra el manual de taller: su ralentí sin fallo está en 820 rpm, el valor que la calibración
retiró por no tener respaldo documental, frente a los 690 rpm de `synthetic_v2`, dentro del rango
640-740 que el manual documenta para el motor Z6. Cualquier comparación de volumen entre los dos
confunde volumen con fenómeno.

**Y no sustituye a `synthetic_v2`.** La cadena de E19 —preprocesado, bosque, atribución, recuperación,
suficiencia, redacción— está congelada sobre `v2` por huella de sus cuatro ficheros, y la evaluación
final acaba de medirse ahí. Adoptar `v4` como canónico obligaría a regenerar E4, E5, E6, E9, E12, E13,
E15, E18 y E19. **`v4` sirve exclusivamente a PI.1**, y así hay que declararlo en el índice: el
conjunto oficial del TFM sigue siendo `synthetic_v2`.

`synthetic_v4` está libre: el repositorio contiene `synthetic_sample`, `v1`, `v2` y `v3`, y nada más.

## 2.2 Qué se genera

| Parámetro | Valor | Por qué |
|---|---|---|
| Sesiones | **216**, 36 por condición | Es el volumen que permite cuatro puntos de curva con 22 sesiones de entrenamiento por condición; ver `04-subconjuntos-anidados.md` |
| Condiciones | las seis existentes: sin fallo y F01 a F05 | No se añade ninguna. El fenómeno no cambia |
| Regímenes | los declarados en `obd/regimes.py`, con el mismo reparto equilibrado que `build_balanced_specs` produce hoy | Cambiar el reparto introduciría otra variable |
| Frecuencia de muestreo | 1 Hz | La del conjunto oficial |
| Duración de sesión | **600 s**, la que `build_balanced_specs` usa hoy para todos los regímenes | Es la de `v2` y `v3`. El tipo `Regime` define fases, no duración, de modo que «la que define el régimen» no existe; y elegir una distinta cambiaría el número de ventanas por sesión y con él la comparación de volumen |
| Semilla global | **20260901**, la del proyecto | Para que el conjunto sea reproducible desde un único número |
| Generador | el **calibrado**, es decir el `obd/engine.py` vigente, cuyas constantes llevan los valores del manual —`_IDLE_RPM = 690.0` y las demás—. El YAML de calibración documenta su procedencia pero **ningún módulo lo lee** | Es la única diferencia que se busca frente a `v3` |
| Ventanado y reparto | 120 s con paso de 60 s, reparto **por sesión** estratificado, test cerrado | Idénticos a `v2`, para que la geometría no sea una variable más |

Con 36 sesiones por condición el reparto por sesión da, por condición, **22 de entrenamiento, 7 de
validación y 7 de prueba**, que es exactamente lo que `synthetic_v3` produce hoy y lo que permite la
curva de volumen.

## 2.3 La variación dirigida, que **no** entra en esta versión

La auditoría propuso generar más realizaciones del régimen de calentamiento variando la temperatura
ambiente y la duración, porque es donde el termostato se vuelve indetectable. **No entra en `v4`** por
una razón de método: si `v4` lleva a la vez más volumen y una distribución distinta de regímenes, la
curva de volumen vuelve a estar confundida. La variación dirigida, si se hace, será un conjunto aparte
—`synthetic_v5`— con su propio protocolo y su propia pregunta, y solo después de que el análisis por
fallo de `08-analisis-por-fallo.md` confirme que hace falta.

## 2.4 Lo que hay que cambiar en el código antes de generar

Tres cosas, pequeñas, y las tres son de **procedencia**, no de fenómeno. Ninguna altera la señal que el
generador produce.

| # | Cambio | Por qué |
|---|---|---|
| 1 | La ficha del conjunto debe registrar la **lista completa de `SessionSpec`** | Hoy guarda la semilla global y los identificadores, y nada más. Sin esto no se puede responder «¿con qué configuración se generó esta sesión?», que es lo que el autor pide |
| 2 | La ficha debe registrar la **versión efectiva del generador**: su commit, la huella del fichero de calibración y la huella de `obd/faults.py`, `obd/regimes.py` y `obd/synthetic.py` | `GENERATOR_VERSION = "1.0.0"` no distinguió `v2` de `v3`, que son fenómenos distintos. Una constante escrita a mano no sirve como identidad |
| 3 | La ficha debe registrar las **huellas de integridad** de los ficheros producidos | Es lo que permite comprobar después que nadie los sustituyó, como ya se hace con `v2` en el manifiesto de E19 |
| 4 | Los datos crudos deben llevar una columna **`fault_expressed`** que diga, por muestra, si el fallo **modificó** esa muestra | La columna existente, `fault_active`, dice solo que la función del fallo se aplicó: para el encendido vale cierto en ventanas sin ningún episodio. Sin esta columna el análisis por fallo de la Fase G no se puede hacer sobre bases firmes. Es un booleano que la función del fallo ya calcula; no consume números aleatorios y no cambia ningún valor de señal |

El esquema exacto está en `03-manifiesto-procedencia.md`. Los tres primeros cambios afectan al
ejecutor del generador y al del preprocesado. El cuarto sí toca `obd/faults.py`, porque es ahí donde cada
función sabe si modificó la muestra, y por eso lleva su propia comprobación: regenerar una sesión con la
columna y verificar que **los valores de señal son idénticos** a los de la misma semilla sin ella. Con
esa comprobación en verde, `synthetic_v2` y `synthetic_v3` siguen siendo reproducibles tal como están.

## 2.5 Criterios de integridad de la generación

1. **Determinismo comprobado:** dos ejecuciones con la misma semilla producen **los mismos datos**. La
   huella se toma sobre los artefactos deterministas —el parquet de sesiones y los `.npy` del
   preprocesado— y, para la ficha y el manifiesto, sobre su contenido **excluyendo los campos de
   marca de tiempo**: `DatasetMetadata.created_at` lleva `datetime.now(UTC)` por omisión, de modo que
   exigir huella idéntica del fichero completo haría fallar el criterio a una generación correcta. Es
   el criterio que E2 ya declara, aquí con el alcance escrito.
2. **El ralentí sin fallo cae dentro del rango del manual**, 640-740 rpm para el Z6. Se comprueba sobre
   el conjunto generado y se registra la mediana y los percentiles 5 y 95. Es la comprobación que
   habría detectado el problema de `v3` el día que se generó.
3. **La auditoría de fuga del reparto pasa**: ninguna sesión en dos particiones, ninguna partición
   vacía, las seis condiciones presentes en las tres.
4. **El reparto por condición es 22/7/7.** Si no lo fuera, la curva de volumen no se puede construir y
   hay que parar antes de entrenar nada.
5. **La ficha responde a la pregunta de procedencia** para una sesión elegida al azar, a mano, antes de
   usar el conjunto.

Si cualquiera de los cinco falla, el conjunto no se usa y el fallo se documenta. No se corrige a
posteriori.

## 2.6 Qué se conserva de lo anterior

`synthetic_v2` intacto y canónico. `synthetic_v3` intacto, sin renombrar, etiquetado como
pre-calibración, con sus registros de E6 y E7 conservados: son la evidencia del resultado anterior a la
calibración y la base de la corrección `SUPERSEDED-E7-02`. **No se regenera ninguno de los dos.**
