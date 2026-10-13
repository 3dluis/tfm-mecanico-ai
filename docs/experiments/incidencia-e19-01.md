# Incidencia `INC-E19-01`: la primera ejecución de E19 quedó interrumpida

**Fecha de la ejecución:** 2 de octubre de 2026; la única marca de tiempo que quedó es la del sellado
de la anotación, **02:31:30 UTC**, de modo que la apertura de la partición ocurrió poco antes y su
instante exacto no consta: el cargador la imprime sin marca y esa salida se perdió ·
**Commit:** `5b64504`, árbol limpio ·
**Estado: NO COMPLETADA.** No hay ninguna medición de suficiencia, de trazabilidad ni de redacción
sobre el conjunto de prueba. · **Causa:** interrupción del proceso, que es una de las condiciones de
invalidez previstas en la sección 6 de `docs/methodology/declaracion-apertura-e19.md`.

Este documento existe porque la regla lo exige: la sección 8 de las reglas congeladas manda
registrar una ejecución que no termina, con su causa, **antes** de aplicar el criterio de validez. Y
porque el artefacto que el propio ejecutor habría escrito no se escribió: está previsto para el caso
en que un caso lance una excepción, y aquí el proceso no falló, lo mataron.

## 1. Qué llegó a ocurrir, y qué no

| Paso | Estado |
|---|---|
| Verificación de la congelación, diez comprobaciones | **PASS**, registrada dentro de la anotación |
| Índice: recuentos, huella de contenido, huella de vectores, espacio único, sin desajuste de vehículo | **PASS** |
| Revisiones de los dos modelos, pesos del adaptador, prompt | **PASS** |
| Árbol de trabajo limpio y destinos libres | **PASS** |
| Carga del redactor antes de abrir | completada |
| **Apertura de la partición de prueba** | **ocurrió**, con su razón escrita |
| Predicciones del bosque sobre las 98 ventanas | completadas |
| Generación de las ejecuciones de los tres estratos | completada |
| **Sellado de la anotación** | **completado** a las 02:31:30 UTC, `experiments/E19_anotacion.json`, huella `57d0e3c33e9ef82f` |
| Recorrido de los casos: recuperación, verificación, redacción | **interrumpido** |
| Registro de la evaluación, tabla de resultados | **no se escribieron** |

La ejecución se lanzó en segundo plano y el proceso terminó sin dejar constancia cuando la sesión de
trabajo se cerró. La salida de consola se perdió con el directorio temporal de esa sesión, de modo
que **no se puede saber cuántos casos se habían completado**. Da igual para lo que importa: las filas
se acumulan en memoria y el registro se escribe al final, así que no sobrevivió ninguna medición
parcial. El registro de recuperaciones de la base de datos no aporta nada, porque solo lo escribe el
ejecutor de E12.

## 2. Lo que sí se conserva, y por qué vale

La anotación sellada, que es el referente contra el que se mide la política. Se escribió **antes** de
que el verificador viera un solo caso, lleva su huella, y su contenido se ha comprobado:

- no contiene ninguna salida del verificador —ni veredicto, ni cobertura, ni comprobaciones de
  soporte—, de modo que la no circularidad se sostiene;
- cada ejecución lleva sus tres entradas permitidas y nada más: etiqueta verdadera, clase predicha
  por el recorrido evaluado y condición de evidencia;
- los denominadores cuadran: 22 = 8 + 14 en el estrato operativo.

| Estrato | Ejecuciones | Ventanas | Sesiones | Deben explicar | Deben abstenerse |
|---|---|---|---|---|---|
| **operativo** (responde a la pregunta) | 22 | 10 | 10 | 8 | 14, sobre 7 ventanas |
| comparativo (descriptivo) | 11 | 5 | 5 | 5 | 6, sobre 3 ventanas |
| adverso (descriptivo) | 2 | 2 | 2 | 0 | 2 |

Tres casos del estrato adverso quedan **no evaluables por ausencia de ventanas**: `C01_maf_drift`,
`C03_o2_slow_response` y `C05_vacuum_leak`, porque el modelo no clasifica mal ninguna ventana de esas
condiciones en la partición de prueba. Es un hecho de la partición, está declarado como tal y no
entra en ningún numerador ni denominador.

El estrato operativo da exactamente los recuentos declarados antes de abrir: veintidós ejecuciones
sobre diez ventanas de diez sesiones.

## 3. El diagnóstico sobre las ventanas elegidas

De las diez ventanas del estrato operativo, el modelo acierta ocho y falla dos, las dos en la misma
dirección —las clasifica como funcionamiento normal—:

| Ventana | Condición | Predicción |
|---|---|---|
| `F03_thermostat_stuck__warmup__11@120s` | termostato bloqueado | `F00_normal` |
| `F05_misfire__highway__01@120s` | fallo de encendido | `F00_normal` |

Por eso ocho ejecuciones deben explicar y catorce deben abstenerse: las doce de las condiciones con
evidencia parcial y ausente, más las dos con evidencia completa cuyo diagnóstico es incorrecto. Y por
eso el estrato adverso solo tiene dos ejecuciones: son las únicas dos condiciones con una ventana mal
clasificada.

Esto **no es un resultado de E19**: es la anotación, que describe qué debería hacer el sistema. Lo que
el sistema hizo no se ha medido.

## 4. Lo que esto no es

No es un resultado desfavorable. No es un defecto del sistema evaluado ni de la política. No es una
excusa para cambiar nada: ni umbrales, ni casos, ni reglas, ni modelos, ni consultas, ni política.

## 5. Qué exige el procedimiento a partir de aquí

1. La ejecución interrumpida **se conserva** con su motivo, que es este documento, y con la anotación
   sellada que produjo.
2. La decisión de repetir es del autor, no del procedimiento. Una repetición es una **versión
   experimental nueva** con su propio identificador de intento, y no sustituye a esta: el nombre
   `E19_anotacion.json` está ocupado, de modo que el ejecutor se detendrá si alguien lo intenta sin
   identificador. Es la sección 11 funcionando.
3. La repetición no reabre ninguna decisión. La declaración de apertura quedó aprobada por el autor
   el 1 de octubre de 2026 con la autorización `OPEN_TEST_AND_RUN_E19`, su aprobación consta en la
   propia declaración y el diseño sigue congelado; lo único que cambia es el identificador del
   intento.
4. Para que no vuelva a ocurrir, la repetición debe lanzarse de forma que sobreviva al cierre de la
   sesión de trabajo, y su salida de consola debe guardarse fuera del directorio temporal de la
   sesión. Eso resuelve además lo que aquí faltó: la línea con que el cargador anuncia la apertura no
   lleva marca de tiempo, y un fichero de salida permite acotar el instante. **No se toca el código
   para añadirla:** el diseño está congelado y la declaración fija el commit con el que se mide.

`[AUTHOR_DECISION_REQUIRED]` — autorizar o no el intento `v2`. Sin esa autorización no se ejecuta nada.

---

> **Añadido el 13 de octubre de 2026.** La causa quedó aquí como una hipótesis ambiental no
> demostrada. `docs/experiments/incidencia-p2-01.md` aporta una medición en el mismo equipo y con el
> mismo modelo: un proceso que carga Qwen2.5-3B con el 88 % de la memoria ocupada y 12,8 GB de
> intercambio en uso consumió 15 minutos de CPU en 187 de reloj, es decir pasó el 92 % del tiempo
> paginando. **No demuestra** lo que les ocurrió a los dos intentos de E19 —aquellos procesos no se
> midieron y no se puede volver atrás— pero hace la hipótesis más plausible de lo que era. Este
> informe no se modifica.
