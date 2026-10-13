# Traslado de P2 a una máquina con más memoria (alternativa D)

**Fecha:** 13 de octubre de 2026 · **Autorizado:** alternativa D de
[`incidencia-p2-02.md`](incidencia-p2-02.md) · **Estado:** **preparado, no ejecutado.** No hay
máquina de destino todavía · **Qué no se hace:** ningún intento más en el equipo actual de 24 GB

## 1. Por qué hace falta otra máquina, con el número

Seis intentos en el equipo del autor. Los tres primeros se colgaron paginando; los tres siguientes,
con techo al asignador, fallaron rápido y **dijeron cuánto faltaba**:

| Intento | Techo | Dónde falló | Necesidad medida |
|---|---|---|---|
| 1 y 2 | sin techo | ninguna época en 3 h 07 y 1 h 33 | — |
| 3 | sin techo | detenido con `vmmap`: 25,4 GB de huella, 22,8 GB en el asignador de Metal | — |
| 4 | 0,70 · 12,43 GB | pasada hacia adelante | ~13,0 GB |
| 5 | 0,85 · 15,10 GB | pasada hacia atrás | ~15,6 GB |
| 6 | 0,95 · 16,87 GB | pasada hacia atrás, **tras entrenar 10 ejemplos** | **~17,0 GB** |

El sexto dejó la primera cifra que P2 ha producido: «época 1 · paso 10/101 · pérdida 1,0785».

**Y la necesidad no es un pico fijo: crece con la longitud del ejemplo.** Medido con el tokenizador
del modelo sobre los 101 ejemplos de ajuste: mínimo 984 tokens, mediana 2 874, máximo 4 361, y **47
de 101 llegan al tope de 3 072 y se recortan**. Los que topan son los que piden 17 GB, y el orden en
que llegan lo fija la semilla.

El equipo actual tiene 24 GB físicos y MPS recomienda como máximo **17,76 GB**. Con el margen del
40 % que la tabla de arriba justifica, hacen falta **23,8 GB** de memoria de acelerador. No cabe, y
el guion de comprobación se niega a intentarlo.

## 2. Qué máquina sirve

| Requisito | Valor | Por qué |
|---|---|---|
| **Memoria de acelerador** | **≥ 24 GB** disponibles para el proceso | 17,0 GB medidos más el 40 % de margen que la variabilidad de los ejemplos exige |
| Apple Silicon | **48 GB o 64 GB** de memoria unificada | con 48 GB, MPS recomienda del orden de 36 GB: holgura real, no ajustada |
| Alternativa GPU | ≥ 24 GB de VRAM | cambia el *backend* de MPS a CUDA, y eso **exige** la evaluación de equivalencia de la sección 5 |
| Lo que **no** sirve | 32 GB de memoria unificada | MPS recomendaría del orden de 24 GB, justo en el límite. Cabría el pico medido y no el margen |

**Preferencia declarada por el autor:** Apple Silicon de 48–64 GB. Es además la opción que **no
cambia nada**: mismo dispositivo `mps`, mismo *backend*, misma precisión.

## 3. Lo que no se modifica, por instrucción

| Pieza | Estado |
|---|---|
| Los ejemplos congelados | 110 ejemplos · 101 de ajuste y 9 de validación interna · cuatro huellas verificadas |
| Las particiones | reparto por sesión; ajuste desde `train`, disjunto de validación y prueba |
| Los hiperparámetros | rango 16, alpha 32, dropout 0,05, 4 épocas, tasa 2e-4, tope 3 072, semilla 20260901 |
| La arquitectura | Qwen2.5-3B-Instruct con LoRA sobre las cuatro proyecciones de atención |
| La longitud máxima de secuencia | **3 072, sin tocar.** Bajarla haría que cupiera y cambiaría qué se ajusta |
| Los criterios de evaluación | los de la congelación |
| `models/slm_lora_v2` | intacto desde el 2 de septiembre. El ejecutor se niega a sobrescribirlo |
| Destino del adaptador nuevo | `models/slm_lora_v3/` |

**Lo único que difiere de los tres primeros intentos** son dos campos de gestión de memoria —techo
del asignador y vaciado del caché por paso—, autorizados como alternativa A, que no cambian los
pesos, el orden de los ejemplos, la semilla ni ninguna operación en coma flotante.

## 4. Las diez comprobaciones, automatizadas

```bash
# En la máquina de destino, dentro del clon:
uv sync --extra nb --extra ml --extra embeddings --extra finetune --extra llm
uv run python scripts/preparar_traslado_p2.py
```

El guion comprueba las diez en orden y **devuelve distinto de cero si alguna falla**, de modo que
«se comprobó» sea un código de salida y no una afirmación:

| # | Qué comprueba | Qué lo hace fallar |
|---|---|---|
| 1 | compatibilidad del entorno | falta `transformers`, `peft`, `accelerate` o `datasets`; o no hay acelerador |
| 2 | memoria realmente disponible | el acelerador recomienda menos de 23,8 GB |
| 3 | huellas de los datos | alguna de las cuatro no coincide con la congelación |
| 4 | integridad de la congelación | alguno de los siete hiperparámetros difiere del congelado |
| 5 | hardware y versiones | — (registra) |
| 6 | ausencia de diferencias metodológicas | — (declara lo que es igual y lo que no) |
| 7 | estimación del consumo | — (imprime el desglose medido) |
| 8 | **prueba técnica breve** | una pasada hacia adelante y otra hacia atrás sobre el **ejemplo más largo** no caben |
| 9 | **diferencias numéricas del hardware** | la sonda de equivalencia se sale de tolerancia |
| 10 | veredicto | se autoriza el ajuste solo si las nueve pasan |

El paso 8 es el que importa: hace el **caso peor** —el ejemplo de 4 361 tokens recortado a 3 072—
con recomputación de gradientes y pasada hacia atrás, mide el pico del asignador y libera. **No hay
optimizador, no se da ningún paso y no se escribe nada en `models/`.** Si el caso peor cabe, el
ajuste completo cabe.

Ejecutado en el equipo actual, el guion se detiene en el paso 2 con el motivo medido. Eso es la
comprobación de que la comprobación funciona.

## 5. La evaluación de equivalencia, con una cifra tomada de antemano

La instrucción es explícita: *no asumir que los resultados serán idénticos entre plataformas*. Para
poder **medirlo** en lugar de suponerlo, hay una sonda determinista tomada ya en el equipo del autor
y congelada en `configs/sonda-equivalencia-p2.json`.

**Qué mide.** La pérdida del modelo **base** —sin adaptador, sin entrenar, sin gradientes— sobre
seis ejemplos del conjunto congelado: los tres más cortos y los tres más largos, elegidos por número
de tokens. Sin aleatoriedad de ninguna clase.

**La referencia, medida el 13 de octubre de 2026 en Apple Silicon con MPS y `bfloat16`:**

| Ejemplo | Tokens | Sin recortar | Pérdida |
|---|---|---|---|
| 77 | 985 | 984 | 1,820834 |
| 20 | 987 | 986 | 1,817806 |
| 28 | 987 | 986 | 1,814785 |
| 61 | 3 072 | 4 356 | 1,324841 |
| 100 | 3 072 | 4 358 | 1,337618 |
| 62 | 3 072 | 4 361 | 1,334120 |

```bash
# En la máquina de destino:
uv run python scripts/sonda_equivalencia_p2.py --comprobar
```

**Cómo se lee.** Diferencias del orden de 1e-3 en `bfloat16` entre plataformas distintas son
aritmética, no metodología: **se registran y no invalidan el traslado**. Diferencias mayores que la
tolerancia, o un número de tokens distinto —que delataría otro tokenizador—, significan que el
camino numérico no es el mismo, y entonces hace falta la evaluación de equivalencia **antes** de
ejecutar, no después.

**Y lo que la sonda no garantiza, dicho para que nadie lo lea de más:** que las pérdidas del ajuste
sean idénticas. Garantiza que, si difieren, la diferencia no viene del modelo ni del tokenizador.

### Si el traslado exigiera cambiar precisión, *backend* o implementación

Entonces **no se ejecuta** y se presenta primero la evaluación de equivalencia. Los tres casos
previsibles y qué exigiría cada uno:

| Cambio | Por qué podría hacer falta | Qué habría que evaluar antes |
|---|---|---|
| MPS → CUDA | la máquina disponible es una GPU NVIDIA | la sonda en CUDA, y declarar que el *backend* no es el congelado. Es un cambio de configuración, no solo de equipo |
| `bfloat16` → `float16` | alguna GPU antigua sin soporte de `bfloat16` | **no se hace.** El rango dinámico es distinto y el ajuste no sería el declarado |
| Cuantización a 4 u 8 bits | para que quepa en menos memoria | **no se hace.** Cambia el modelo base, no solo su alojamiento |
| Acumulación de gradiente | para reducir el pico | cambia el tamaño efectivo de lote, que es un hiperparámetro |

## 6. Qué se registra al ejecutar, y qué pasa si las cifras difieren

Al terminar el ajuste hay que registrar, además de lo que `finetune_config.json` escribe solo:

1. **El hardware y las versiones** que el paso 5 imprimió.
2. **El resultado de la sonda** en esa máquina, con sus diferencias respecto de la referencia.
3. **Duración de reloj y de CPU**, y el pico del asignador por época.
4. **Las cuatro pérdidas de entrenamiento y las cuatro de validación interna.**
5. **Las huellas del adaptador** resultante.
6. **Cualquier diferencia numérica atribuible al hardware**, con su magnitud.

**Si las pérdidas difieren de lo que esta máquina habría dado:** se registran y se declara que el
ajuste se ejecutó en otra plataforma. No se presentan como equivalentes sin la sonda, y la sonda no
convierte «parecido» en «idéntico». El adaptador resultante es el que es, medido donde se midió.

## 7. Si no hay máquina

P2 queda **pendiente por dependencia de infraestructura**. Esa es la redacción, y la diferencia con
la otra importa:

- **Lo que NO se dice:** que el experimento haya fracasado científicamente. No ha fracasado: está
  diseñado, preparado, congelado, con sus ejemplos sin contaminación verificados y su conjunto de
  evaluación independiente también congelado. Lo único que falta es memoria.
- **Lo que SÍ se dice:** que la contaminación del adaptador del redactor queda **documentada y no
  corregida**, que las cifras de E13 y E15 conservan su marca de afectadas, y que no se sabrá cuánta
  de la calidad atribuida al redactor venía de haber visto los casos.

El guion lo imprime así cuando se niega, para que la redacción no dependa de quién escriba el
informe.
