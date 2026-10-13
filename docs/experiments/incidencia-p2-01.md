# INC-P2-01 — El ajuste del adaptador v3 se detuvo por agotamiento de memoria

**Fecha:** 13 de octubre de 2026 · **Qué se detuvo:** el reentrenamiento de
`models/slm_lora_v3` (P2) · **Estado:** **no completado**; los datos y la configuración
congelada quedan listos · **Qué se escribió:** nada. `models/slm_lora_v3` no existe

## Qué pasó

El ajuste se lanzó bajo `launchd` con la configuración congelada en
`configs/congelacion-adaptador-v3.json`: Qwen2.5-3B-Instruct, LoRA de rango 16, cuatro épocas, 94
ejemplos de entrenamiento y 18 de validación interna.

A las **3 h 07 min** de reloj no había producido ni una época. La medición del proceso explica por
qué:

| Medida | Valor | Qué significa |
|---|---|---|
| Tiempo de reloj | 3 h 07 min | — |
| **Tiempo de CPU** | **15 min 26 s** | el proceso estuvo esperando el **92 %** del tiempo |
| **Memoria residente** | **25 MB** | imposible para un modelo de 3 000 millones de parámetros: estaba casi todo paginado fuera |
| Estado | `U` | espera ininterrumpible, es decir bloqueado en entrada/salida |

Y el estado de la máquina:

```
Memoria libre:  12 %
Swap:           12 796 MB usados de 14 336 MB
Pageins:        23 280 686
```

**El proceso no iba lento: estaba paginando.** Con el 88 % de la memoria ocupada y 12,8 GB de
intercambio en uso, cada paso del ajuste exigía traer de disco pesos que acababan de expulsarse. Un
ajuste que con memoria suficiente tarda del orden de dos horas no habría terminado en un día.

Se detuvo deliberadamente. No se escribió ningún adaptador parcial: `finetune` guarda al final, de
modo que `models/slm_lora_v3` no existe y no hay nada ambiguo en disco.

## Qué sí quedó hecho, y es la mayor parte

| Pieza | Estado |
|---|---|
| Auditoría de contaminación | **completa**, y encontró una contaminación mayor que la declarada |
| Ejemplos sin contaminación | **generados y verificados**: 112 ejemplos, cero solape con validación y prueba |
| Preparación al formato del modelo | **hecha**: 94 de entrenamiento, 18 de validación interna |
| Configuración congelada | **escrita antes de ajustar**, con hiperparámetros, semilla, criterios de parada y métricas |
| Huellas de los ficheros de ajuste | **registradas** en la congelación |
| Protección de `slm_lora_v2` | **comprobada**: el ejecutor se niega a sobrescribirlo |

Lo único que falta es ejecutar el ajuste. **No hay que rehacer nada**, y la configuración congelada
garantiza que la ejecución que se haga sea la misma que se declaró.

## La conexión con INC-E19-01, que ahora tiene explicación

Los dos primeros intentos de E19 murieron tras sellar la anotación, y su informe dejó la causa como
**una hipótesis ambiental no demostrada**: no hubo informe de fallo, ni *jetsam*, ni suspensión, y la
reproducción sobre validación terminó con un pico de 1,93 GB.

Esta incidencia aporta la medición que faltaba. El patrón —un proceso que carga un modelo de 3 000
millones de parámetros en una máquina con el 88 % de la memoria ocupada y 12,8 GB de intercambio en
uso— es compatible con lo que les pasó: el redactor de E19 carga exactamente ese modelo.

**No se declara demostrado.** La hipótesis de E19 sigue siendo una hipótesis, porque aquellos
procesos no se midieron mientras ocurría y no se puede volver atrás. Lo que sí cambia es que ahora
existe una causa **medida** en el mismo equipo, con el mismo modelo, y eso la hace más plausible que
antes. El informe de E19 no se modifica: se añade esta referencia.

## Qué se corrige en el procedimiento

1. **Comprobar la memoria antes de lanzar un ajuste**, no después de tres horas. Una ejecución que
   necesita varios gigabytes residentes en una máquina con el 12 % libre no va a terminar.
2. **Medir tiempo de CPU además de tiempo de reloj** al vigilar un proceso largo. El reloj por sí
   solo no distingue «va lento» de «está parado»: fue la relación 15 min de CPU en 187 de reloj la
   que lo delató.
3. **Guardar el adaptador por épocas**, para que una interrupción no obligue a empezar de cero. No
   se cambia ahora: tocar el ejecutor con la configuración ya congelada sería cambiar el
   experimento. Queda anotado para después de P2.

## Cómo se retoma

Con la máquina descargada, y sin tocar nada de lo congelado:

```bash
uv run mecanico-exp finetune-slm \
  --datos sin_contaminacion --adapter-dir slm_lora_v3 --epochs 4
```

Antes de lanzarlo conviene comprobar que hay memoria: el ajuste necesita varios gigabytes
residentes y la máquina debe tener holgura real, no intercambio.

Las huellas de los cuatro ficheros de ejemplos están en
`configs/congelacion-adaptador-v3.json`; si no coinciden, el ajuste no es el declarado y hay que
pararse.
