# Auditoría de contaminación del adaptador, antes de reentrenarlo (P2)

**Fecha:** 13 de octubre de 2026 · **Qué audita:** de dónde salieron los ejemplos con que se ajustó
`models/slm_lora_v2` y sobre qué se midió después su calidad · **Resultado:** se encuentra una
contaminación **mayor que la que estaba documentada**.

## 1. La contaminación que estaba declarada

`docs/limitations.md` declara que el adaptador «se entrenó sobre el conjunto anterior y no se
reentrenó» tras la corrección del espacio de embeddings mezclado. Es decir: sus ejemplos llevan
paquetes de evidencia producidos por una recuperación defectuosa.

Es cierto, y es la razón por la que P2 está en la lista de pendientes. **No es la peor.**

## 2. La contaminación que esta auditoría encuentra

`run_training_data` construye los ejemplos de ajuste a partir de la **partición de validación**:

```python
validacion = load_partition("validation", dataset_id=dataset_id)
...
indices = np.flatnonzero((validacion.y == fault_id) & aciertos)[:ventanas_por_condicion]
```

Y E13 y E15 miden la calidad del redactor **también sobre validación**. Medido:

| | Ventanas | Sesiones |
|---|---|---|
| Ejemplos de ajuste de `slm_lora_v2` | 43 | 9 |
| Evaluación de E15 (canónica, oracular) | 5 | 5 |
| **Solape de ventanas** | **3** | — |
| **Solape de sesiones** | — | **4** |

**Tres de las cinco ventanas sobre las que se evaluó al redactor son exactamente las mismas con que
se ajustó**, y cuatro de las cinco sesiones coinciden:

```
F02_maf_drift__highway__01@120s
F03_thermostat_stuck__urban__08@120s
F04_o2_lag__idle__02@120s
```

### Qué significa y qué no

**Lo que queda comprometido:** las cifras de calidad de redacción de E13 y E15 sobre validación
—«9/9 salidas válidas», «17/17 tras RERUN-A»— se midieron, en su mayor parte, sobre los mismos
paquetes de evidencia con que el adaptador se ajustó. No son una estimación de cómo redacta ante
evidencia nueva.

**Lo que no queda comprometido, y conviene decirlo con la misma claridad:**

1. **El verificador no es el redactor.** Las decisiones EXPLAIN/ABSTAIN de E15 las toma un criterio
   determinista que **no usa el modelo de lenguaje**. El 15/17 de E15 no depende del adaptador.
2. **E19 está limpio.** Su medición es sobre la partición de **prueba**, y el solape con los
   ejemplos de ajuste es **cero ventanas y cero sesiones**. Comprobado contra
   `artifacts/tables/E19_evaluacion_final_v3.csv`. Las cifras de redacción de la evaluación final no
   están contaminadas por esta vía.
3. **Las ablaciones de E18 no redactan.** Su pre-registro lo declara: se ejecutan sin proveedor de
   lenguaje.

De modo que la contaminación afecta a **las cifras de redacción de E13 y E15 sobre validación**, y no
a la evaluación final ni a las decisiones de suficiencia.

## 3. Por qué pasó, que es lo instructivo

El reparto por sesión se diseñó para el **modelo de diagnóstico**: entrenamiento para ajustar,
validación para medir. Cuando se añadió el redactor, sus ejemplos se generaron de donde había
predicciones correctas y evidencia ya montada —validación— sin reparar en que esa partición era
también donde se le iba a medir.

Es el mismo patrón que ya apareció dos veces en este trabajo: una salvaguarda correcta para un
componente que no se propagó al siguiente. La primera fue la condición con distractor, cuya salvedad
no viajó del conjunto anotado a los informes. La segunda, los nombres fijos de artefacto, que se
arreglaron para el identificador de conjunto y no para el de experimento.

## 4. Qué hace P2 con esto

El reentrenamiento en `models/slm_lora_v3` corrige **las dos** contaminaciones:

1. **Los ejemplos se generan desde la partición de entrenamiento**, no desde validación. El reparto
   es por sesión, de modo que la disyunción con validación y prueba es estructural y no depende de
   que nadie se acuerde.
2. **Con la recuperación corregida**, posterior al espacio de embeddings mezclado.

Y se comprueba **antes de entrenar**, no después: el generador de ejemplos verifica que ninguna
ventana ni ninguna sesión de los ejemplos aparece en validación ni en prueba, y se detiene si
alguna lo hace.

## 5. Lo que no se hace

**No se tocan `models/slm_lora_v2` ni sus registros.** Siguen siendo el redactor congelado de E19 y
la evidencia de lo que se midió. El adaptador nuevo es otro, con su propio directorio y sus propios
registros.

**No se busca que el adaptador nuevo dé mejores cifras.** El objetivo es eliminar la contaminación y
medir su comportamiento en condiciones controladas. Si el adaptador limpio redacta **peor**, ese es
el resultado y se publica: significaría que parte de la calidad atribuida al redactor venía de haber
visto los casos.

**No se usan los resultados de P3 para decidir nada de esto.** La auditoría y el diseño de P2 son
anteriores y no dependen de ellos.

## 6. Qué cambia en lo publicado

| Documento | Qué hay que marcar |
|---|---|
| `docs/limitations.md` | la limitación del adaptador es **más amplia** de lo declarado: no es solo la recuperación anterior, es que se ajustó sobre las ventanas en que se le midió |
| `docs/experiments/E13_agente_slm.md` | sus cifras de validez de salida se miden sobre ventanas vistas en el ajuste |
| `docs/experiments/E15_suficiencia.md` | la parte de **redacción**, no la de decisión |
| `docs/experiment-index.md` | fila E13 |

Las cifras **no se retiran ni se recalculan**: se marcan con lo que son. Recalcularlas exigiría
reentrenar, que es justo lo que P2 hace, y entonces serían otras cifras de otro adaptador.
