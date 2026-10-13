# INC-P2-02 — El tercer intento de ajuste se detiene con la causa medida

**Fecha:** 13 de octubre de 2026 · **Qué se detuvo:** el reentrenamiento de `models/slm_lora_v3`
(P2), tercer intento · **Estado:** **no completado**; se detiene por decisión, con los recursos
medidos · **Qué se escribió:** nada. `models/slm_lora_v3` no existe · **Qué quedó intacto:**
`models/slm_lora_v2`, sin tocar desde el 2 de septiembre

## 1. Lo que se registró de esta ejecución

Se registra lo que hay. Lo que no hay se dice, en lugar de dejarlo en blanco.

| Campo | Valor |
|---|---|
| Lanzado | 13-10-2026 12:54:46 −04:00, PID 6512, bajo `launchd`, desacoplado de la sesión |
| Detenido | 13-10-2026 13:06 −04:00, por decisión, con `SIGKILL` tras `SIGTERM` |
| **Duración** | **11 min 30 s de reloj · 1 min 27 s de CPU** → **12,6 % de uso de CPU** |
| Configuración | `configs/congelacion-adaptador-v3.json`, **verificada antes de arrancar**: 4 huellas, origen de los datos y 4 épocas coinciden |
| Semilla | 20260904, fijada en la congelación; `torch.manual_seed` y `torch.mps.manual_seed` |
| Datos | `slm_finetune_prepared_sin_contaminacion`: 101 ejemplos de ajuste · 9 de validación interna |
| **Pérdidas** | **ninguna.** No se alcanzó el final de la primera época |
| **Punto de control** | **ninguno.** `finetune` guarda al final; no hay adaptador parcial |
| **Resultado de validación** | **ninguno** |
| Huellas de los datos | las cuatro de la congelación, comprobadas y coincidentes |

**No se declara ningún resultado de este intento, porque no produjo ninguno.**

## 2. La causa, medida y no inferida

Los dos intentos anteriores (INC-P2-01) dejaron el patrón —92 % del tiempo esperando, memoria
residente absurdamente baja— y una causa **plausible**: la máquina paginando. Esta vez se midió
dónde estaba la memoria, con el proceso vivo. El registro completo está en
`experiments/runs/evidencia/p2_v3_intento3_memoria.txt`.

```
Physical footprint:         25,4 GB
Physical footprint (peak):  27,2 GB

                        VIRTUAL  RESIDENT    DIRTY   SWAPPED   REGIONES
IOAccelerator (graphics)  22,8 GB   22,8 GB   8,9 GB   13,9 GB      1364
mapped file              108,9 MB
```

Y el estado de la máquina en ese momento:

| Medida | Valor |
|---|---|
| Memoria física de la máquina | **24,0 GB** |
| Huella física del proceso | **25,4 GB**, con pico de **27,2 GB** |
| Presupuesto que MPS recomienda aquí | **17,8 GB** (`torch.mps.recommended_max_memory()`) |
| Memoria del asignador de Metal | **22,8 GB en 1364 regiones**, de las que **13,9 GB en intercambio** |
| Páginas comprimidas | 22,5 GB lógicos en 5,1 GB físicos |
| Intercambio | 7,1 GB usados de 8,2 GB, **creciendo** |

**La causa no es que el ajuste sea lento: es que no cabe.** El proceso pide 25,4 GB de huella
física en una máquina de 24 GB, y **el 97 % de esa huella está en el asignador de Metal**, no en
los pesos. Los pesos del modelo base ocupan 5,8 GB en disco; el asignador llegó a 22,8 GB
repartidos en 1364 regiones.

El mecanismo es conocido y aquí queda medido: el asignador de MPS **cachea** los búferes y no los
devuelve. Cada secuencia de longitud distinta reserva búferes de forma nueva, y los ejemplos de
ajuste van de 3 500 a 12 100 caracteres —de unos 900 a unos 3 000 tokens, con el tope en 3 072—, de
modo que casi cada ejemplo estrena formas. Con *gradient checkpointing* y 36 capas, cada forma
nueva deja su rastro en el caché. El asignador crece hasta pasarse del presupuesto recomendado en un
28 %, el sistema empieza a intercambiar búferes de Metal, y entonces cada paso del ajuste espera a
disco. De ahí el 12,6 % de CPU y el estado de espera ininterrumpible.

**Qué añade esto a INC-P2-01 y a INC-E19-01.** La hipótesis ambiental de E19 queda más sostenida, no
demostrada: ahora hay una causa **medida** —el asignador de Metal desbordando la memoria física al
cargar este mismo modelo— en el mismo equipo. Sigue sin poder demostrarse para aquellos dos procesos,
que no se midieron mientras ocurría. Lo que cambia es que la causa ya no es una conjetura sobre la
máquina: es un número.

## 3. Por qué se detiene en lugar de esperar

Por instrucción explícita —si los recursos resultan insuficientes, detener y presentar
alternativas— y porque la medición dice que esperar no sirve: con 13,9 GB de búferes en
intercambio, el ajuste avanza al ritmo del disco. El primer intento estuvo 3 h 07 sin terminar una
época. Este no habría ido mejor, y las tres horas no habrían añadido información que estos once
minutos no hayan dado.

**Lo que no se ha hecho:** cambiar hiperparámetros para que termine antes. La configuración sigue
congelada, sin tocar, tal como se declaró.

## 4. Alternativas, con lo que cada una cuesta

Ninguna se aplica sin autorización. Se ordenan por lo que alteran del experimento declarado, de
menos a más.

### A · Liberar el caché del asignador en cada paso

`torch.mps.empty_cache()` después de cada paso, y `torch.mps.set_per_process_memory_fraction()`
para poner un techo al asignador.

| | |
|---|---|
| **Qué cambia del experimento** | **nada de lo que se mide.** Mismos pesos, mismo orden de ejemplos, misma semilla, mismas operaciones, mismas pérdidas esperadas. Es gestión de memoria, no hiperparámetro |
| **Qué cuesta** | el ajuste va más lento por paso —hay que volver a reservar búferes— pero deja de paginar, que es lo que lo paraliza |
| **Qué hay que tocar** | `src/mecanico_ia_exp/llm/finetune.py`, dos líneas, en el camino de carga y en el bucle |
| **Riesgo** | ese fichero es el que cargó el redactor de E19. El cambio no altera el cálculo, pero sí el código que produjo un resultado publicado, y eso hay que declararlo en el informe de E19 |
| **Si no basta** | se vuelve a medir la huella; si sigue por encima de 24 GB, el problema no era el caché |

### B · Ajustar en CPU en lugar de MPS

| | |
|---|---|
| **Qué cambia del experimento** | el dispositivo, que **sí** está en la configuración congelada. Las operaciones en coma flotante no son bit a bit idénticas entre CPU y MPS, de modo que las pérdidas no serán las mismas |
| **Qué cuesta** | mucho tiempo. Un ajuste LoRA de 3 000 millones de parámetros en CPU se cuenta en decenas de horas |
| **Ventaja** | la memoria queda acotada y medible, sin asignador de Metal que crezca |

### C · Bajar el tope de longitud de secuencia

De 3 072 a, por ejemplo, 2 048.

| | |
|---|---|
| **Qué cambia del experimento** | **el experimento.** Recortaría los paquetes de evidencia más largos, que es justo la entrada que el redactor tiene que aprender a manejar. Cambia qué se ajusta, no cómo |
| **Por qué no se recomienda** | sería modificar un hiperparámetro para que termine antes, que es lo que se ha pedido no hacer |

### D · Otra máquina con más memoria

| | |
|---|---|
| **Qué cambia del experimento** | nada, si se conserva dispositivo y versiones. Habría que registrar el equipo y rehacer la congelación con su huella |
| **Qué cuesta** | depende de qué haya disponible. Con 48 GB el pico de 27,2 GB cabe con holgura |

### E · Cerrar P2 sin ejecutarlo, como limitación declarada

| | |
|---|---|
| **Qué cambia** | la contaminación del adaptador queda **documentada y no corregida**. Las cifras de redacción de E13 y E15 conservan su marca de afectadas, y la memoria declara que el reentrenamiento se diseñó, se preparó y no se pudo ejecutar por memoria insuficiente, con la medición como prueba |
| **Qué se pierde** | no se sabrá cuánta de la calidad atribuida al redactor venía de haber visto los casos |
| **Qué se gana** | es honesto y está medido. Un trabajo que declara con números por qué no pudo hacer algo es más defendible que uno que lo hace mal para poder decir que lo hizo |

## 4 bis. Lo que el autor autorizó, y qué se hizo

**Alternativa A**, el 13 de octubre de 2026. Implementada en `src/mecanico_ia_exp/llm/finetune.py`:

| Qué | Valor | Efecto |
|---|---|---|
| `fraccion_de_memoria` | 0,7 | techo del asignador en 0,7 de los 17,8 GB recomendados, unos 12,5 GB |
| `vaciar_cache_por_paso` | sí | el asignador devuelve en cada paso lo que ya no usa |

Las dos quedan **en el registro del adaptador**, porque van en la configuración y se escriben con
él. Ninguna es un hiperparámetro: rango, alpha, dropout, épocas, tasa de aprendizaje, tope de
longitud, semilla y dispositivo **siguen exactamente como se congelaron el 13 de octubre**, y no se
han tocado en ninguno de los cuatro intentos.

Y hay una ganancia secundaria que importa tanto como la memoria: **con techo, el ajuste falla rápido
y visiblemente** si no cabe, en lugar de paginar durante horas. Un error de memoria de MPS en el
primer minuto es mejor resultado que tres horas sin una época, porque dice algo.

Se añade además el vaciado de los búferes de salida en los avisos de progreso. Los tres intentos
anteriores no imprimieron una sola línea de progreso, y eso llevó a una conclusión equivocada
—«está parado antes de contar parámetros»— cuando la salida estaba en el búfer del proceso. Un
proceso que escribe en un fichero y no vacía el búfer parece muerto sin estarlo.

## 5. Lo que queda hecho y no hay que rehacer

| Pieza | Estado |
|---|---|
| Auditoría de contaminación | **completa**, y midió más contaminación que la declarada |
| Ejemplos sin contaminación | **generados y verificados**: cero solape de ventanas y de sesiones con validación y prueba |
| Preparación al formato del modelo | **hecha**: 101 de ajuste · 9 de validación interna |
| Configuración congelada | **escrita antes de ajustar**, con sus huellas, y **verificada** al arrancar los tres intentos |
| Protección de `slm_lora_v2` | **comprobada tres veces**: el ejecutor se niega a sobrescribirlo |
| Conjunto de evaluación independiente | **definido y congelado**: `docs/methodology/evaluacion-independiente-redactor.md` |
| Causa del fallo | **medida**, no conjeturada |

## 6. Lo que esta incidencia enseña sobre el procedimiento

1. **Una comprobación previa de memoria libre no basta.** Las diez comprobaciones previas pasaron:
   16,0 GB disponibles, ningún entrenamiento activo, congelación verificada. Lo que ninguna podía
   saber es que el proceso pediría 25,4 GB. **Lo que hay que comprobar no es la memoria libre: es la
   huella que el proceso va a pedir**, y eso solo se sabe midiéndolo.
2. **Medir dónde está la memoria, no solo cuánta falta.** `ps` dijo 31 MB residentes y llevó a
   conclusiones equivocadas durante dos intentos. `vmmap -summary` dijo 22,8 GB en el asignador de
   Metal en un minuto. La herramienta importaba más que la insistencia.
3. **Once minutos con la medición correcta valen más que tres horas sin ella.** El primer intento
   esperó 3 h 07 para concluir menos.
