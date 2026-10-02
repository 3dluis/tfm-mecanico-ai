# Declaración formal de apertura del conjunto de prueba (E19)

**Estado: BORRADOR, pendiente de aprobación del autor. El conjunto de prueba sigue cerrado.**

Este documento no abre nada por existir. Es el texto que el autor aprueba y firma, y la
aprobación es lo que autoriza ejecutar E19. Hasta entonces el cargador sigue lanzando una
excepción y ninguna cifra de la memoria procede de la partición de prueba.

| | |
|---|---|
| **Redactada** | 1 de octubre de 2026 |
| **Aprobada** | `[PENDIENTE: fecha y hora que el autor escriba al aprobarla]` |
| **Ejecutada** | la marca de tiempo exacta la escribe el propio registro en su campo `executed_at`, en UTC, junto al commit y al estado del árbol |

## 1. Qué se abre y por qué

Se abre la partición de prueba del conjunto `synthetic_v2` —doce sesiones, noventa y ocho
ventanas— para ejecutar **una sola vez** la evaluación final descrita en
`docs/methodology/plan-e19-evaluacion-final.md`, bajo las reglas congeladas en
`docs/methodology/congelacion-anotacion-e19.md`.

La razón es que el gate previo está completo: las ocho comprobaciones en PASS, el ejecutor
escrito, revisado y ensayado sobre validación, y las reglas de selección y anotación congeladas
antes de mirar la partición. Lo único que queda por hacer con el conjunto de prueba es medir.

## 2. Estado congelado que esta ejecución declara

| Pieza | Valor |
|---|---|
| **Commit de la ejecución** | `4fd2be8` en el momento de redactar esta declaración. Si al ejecutar fuera otro, el registro lo dirá y habrá que justificar la diferencia |
| **Reglas congeladas** | `docs/methodology/congelacion-anotacion-e19.md`, huella `7ef74d8a6ffa45fa` |
| **Estado congelado** | `configs/manifest_e19.json`, huella `6ddaf83854e23a54` |
| **Anclaje** | `configs/congelacion-e19.anchor.json`, commit de congelación `de6207f` |
| **Cadena de versiones congeladas** | `345beba` → `af26819` → `e77d730` → `8d3bd5c` → `163df72` → `9f33dbe` → `4705a3f` → `de6207f`, cada una con su motivo y su fecha en el propio anclaje. Las ocho son anteriores a esta declaración y ninguna responde a un resultado de prueba |
| **Política del verificador** | **v2.2**, que pasa a canónica con esta evaluación y solo con ella. Las cifras publicadas hasta el 1 de octubre de 2026 se midieron con la anterior y **no se reabren** |
| **Umbrales** | confianza 0,79 · fragmentos de soporte 2 · fuentes distintas 1 · cobertura de afirmaciones 0,80 · puntuación de recuperación desactivada · aplicabilidad, solo coincidencia exacta |
| **Semilla** | 20260901, en reparto, bosque, fondo de atribución y muestreos |
| **Conjunto de datos** | `synthetic_v2`, `dataset_type: synthetic`. Sus cuatro ficheros, por huella: `42e3031653498bf4` (ventanas), `c8fa7068c13a274e` (descriptores), `ffef0c525d441988` (metadatos), `e63be72934a75f7c` (manifiesto de preprocesado) |
| **Modelo de diagnóstico** | bosque aleatorio de 400 árboles, hoja mínima 2, pesos equilibrados, calibración isotónica con validación cruzada de 5 pliegues ajustada **sobre entrenamiento**. Sin reentrenar |
| **Corpus** | `mazda-3-bk-2007`, versión 0.1.0, 6 158 fragmentos de 3 055 ficheros, huella de contenido `7ac722bdda12595d` |
| **Vectores** | espacio `sentence-transformers[mps]/…/d384/v1.0.0`, huella `ad0b27a17798d042`, revisión del modelo `e8f8c211226b894fcb81acc59f3b34ba3efd5f42` |
| **Redactor** | `transformers-lora@slm_lora_v2` sobre `Qwen/Qwen2.5-3B-Instruct`, revisión `aa8e72537993ba99e69dfaafa59ed015b17504d1`, prompt `agent-2026-09-04`, pesos del adaptador `14e9db475a79943f` y `e6fccee67dc370bd`. Sin reentrenar |
| **Recuperación** | guiada por el diagnóstico, profundidad 10, filtros de vehículo y motor, reordenación por autoridad |
| **Canales de oráculo** | `O-2` y `O-3` cerrados: la recuperación y el requisito de la puerta de códigos se derivan de la clase predicha. `O-1` cerrado en el estrato operativo |

El ejecutor comprueba las piezas de esta tabla antes de abrir la partición y detiene
la ejecución si alguna no coincide **o si no puede comprobarla**.

## 3. Lo que se espera encontrar, dicho antes de abrir

| | Esperado |
|---|---|
| Sesiones de prueba | 12, dos por condición de fallo |
| Ventanas de prueba | 98 |
| Ventanas con caso | 10, una por sesión de las cinco condiciones de fallo; las dos sesiones sin fallo no generan casos |
| Ejecuciones del estrato operativo | **22** = once condiciones de evidencia × dos sesiones |
| Ejecuciones del estrato comparativo | hasta 11, una por condición de evidencia |
| Ejecuciones del estrato adverso | hasta 5, solo evidencia completa, y solo donde el modelo falle |

Los dos «hasta» son hechos de la partición y no fallos: un caso sin ventana del tipo que su
estrato pide se declara **no evaluable por ausencia de ventanas** y no entra en ningún numerador
ni denominador. Si el estrato operativo no diera 22 ejecuciones sobre 10 sesiones, el registro lo
dirá en su campo `declared_vs_observed` y habrá que declararlo con las cifras.

**Los denominadores de las dos tasas no se declaran aquí**, y no es un olvido: dependen de
cuántas ventanas clasifique bien el modelo sobre prueba, que es exactamente lo que no se ha
mirado. Quedan fijados en la anotación sellada, antes de medir.

## 4. Métricas primarias y análisis descriptivos

**Primarias, del estrato operativo, que es el único que responde a la pregunta:**

- falsa confianza y abstención innecesaria, cada una con numerador, denominador en ejecuciones y
  número de ventanas y de sesiones distintas, publicadas **por separado** y nunca sumadas;
- las dos políticas triviales de referencia sobre las mismas ejecuciones;
- exactitud, F1 macro, F1 ponderado, exactitud equilibrada y métricas por clase del diagnóstico
  sobre las 98 ventanas, frente a la clase mayoritaria;
- calibración: error esperado con 10 tramos, confianza media, acierto y sesgo, sin calibrar y
  calibrado;
- trazabilidad: afirmaciones con observación, con cita y con soporte, con su denominador, y el
  mismo bloque acotado a las ejecuciones con evidencia completa;
- redacción: salidas válidas de esquema, fallos de esquema, ejecuciones con citas fuera de lo
  entregado, respeto del veredicto.

**Descriptivos, que no responden a ninguna subpregunta y no se mezclan con las primarias:** el
estrato comparativo, que existe para separar el efecto de la partición del efecto de haber
cambiado la regla de selección, y el estrato adverso, que prueba el escenario del diagnóstico
incorrecto.

**Qué no se mide:** la condición con distractor, que no puede interpretarse hasta su rediseño, y
la variante léxica de la ablación, que es una medición nueva.

## 5. Confirmación de que el conjunto de prueba no se ha usado

Se declara, y se puede comprobar:

1. **Ninguna cifra publicada procede de la partición de prueba.** Los umbrales se fijaron sobre
   validación con el criterio escrito antes del barrido (`criterio-umbral.md` y su enmienda); el
   modelo y su calibración se ajustaron sobre entrenamiento; las decisiones de E15, E18 y la
   segunda versión de la política se midieron sobre validación.
2. **Las reglas de selección y anotación se congelaron sin mirar la partición.** Para escribirlas
   se leyó únicamente el reparto de sesiones del manifiesto de preprocesado y sus recuentos, que
   son la aritmética del reparto estratificado publicada desde E5. Está declarado en la sección 0
   del documento de congelación.
3. **El cierre es técnico, no una promesa.** Pedir la partición de prueba exige una declaración
   explícita y una razón por escrito; tres pruebas comprueban el cierre y el mensaje de la
   excepción. Cada apertura queda impresa en la salida de la ejecución.
4. **El ejecutor se auditó sobre validación.** Sus artefactos de ensayo llevan sufijo, declaran
   dentro de sí mismos que no son resultados de E19 y no pueden sobrescribir a los de la
   evaluación final.
5. **Ninguna de las ocho versiones congeladas responde a un resultado de prueba.** Cada una
   declara su motivo en el anclaje, y los ocho son huecos descubiertos al implementar o en la
   revisión del diff.

## 6. Qué invalidaría técnicamente la ejecución

La lista es cerrada y todas sus causas son ajenas al resultado: una pieza con versión distinta de
la congelada; el índice incompleto, con contenido o vectores distintos de los congelados, o con un
vector que apunte a un fragmento de otro vehículo; el espacio vectorial resuelto en otro
dispositivo, o un nombre de modelo que identifique más de un espacio; una revisión de modelo
distinta de la congelada; los pesos del adaptador distintos de los congelados; un artefacto de
entrada ausente o corrupto; el árbol de trabajo con ficheros modificados; la interrupción del
proceso; y un defecto demostrable en el código de instrumentación que no afecte a la política
evaluada.

Añadido, por lo que es: **una comprobación que el entorno no pueda realizar invalida igual que una
que falle.** Una ejecución que no pueda demostrar bajo qué reglas se midió no vale menos que otra;
no vale nada.

## 7. Lo que **no** invalida la ejecución

Que las cifras sean peores de lo esperado. Que una hipótesis no se sostenga. Que aparezca un
defecto en el sistema evaluado: un defecto en el sistema evaluado **es** el resultado.

**Un resultado desfavorable no es motivo para repetir la ejecución.** Si las tasas salen altas, si
el sistema explica donde debía abstenerse o se abstiene donde debía explicar, eso es el hallazgo y
se publica tal cual, con su interpretación y sus limitaciones.

## 8. La regla que gobierna todo lo posterior

> **A partir de esta declaración, cualquier modificación de reglas, selección de casos, umbrales,
> política, modelos o configuración dará lugar a una nueva versión experimental y no sustituirá
> silenciosamente los resultados de E19.**

En la práctica: el registro de una ejecución inválida se conserva con su motivo y su causa
documentados; una repetición se publica con su propio identificador de intento y no puede
sobrescribir los artefactos de la anterior, porque el ejecutor se detiene si el destino está
ocupado; y si el defecto apareciera después de abrir y afectara a la política evaluada, la
ejecución se conserva, el defecto se declara, y cualquier medición posterior es una versión nueva
y no una corrección de esta.

## 9. Lo que el autor aprueba al firmar

Que se abra la partición de prueba una vez, en las condiciones de la sección 2, para medir lo de la
sección 4, con la razón escrita de la sección 1, sabiendo lo de las secciones 6 a 8.

La orden que ejecuta esta declaración, una vez aprobada:

```
uv run mecanico-exp final-evaluation \
  --partition test \
  --open-test \
  --reason "Evaluacion final E19 autorizada por el autor el <fecha>; declaracion en docs/methodology/declaracion-apertura-e19.md; reglas congeladas en el commit de6207f" \
  --llm transformers-lora@slm_lora_v2
```

`[AUTHOR_DECISION_REQUIRED]` — aprobación, fecha y hora. Sin eso, este documento es un borrador y
el conjunto de prueba sigue cerrado.
