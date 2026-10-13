# P1 — Protocolo del rediseño de la condición con distractor

**Fecha:** 13 de octubre de 2026 · **Estado:** **diseño, congelado antes de ejecutar** ·
**Criterio que lo gobierna:** los cuatro requisitos `D-1`…`D-4` de
[`politica-condicion-distractor.md`](politica-condicion-distractor.md), pre-registrados el 4 de
septiembre de 2026 · **Qué no hace:** no modifica el conjunto anotado congelado de E19

## 1. Qué se midió antes de diseñar nada

La política pre-registrada exige comprobar `D-1` y `D-2` **antes de mirar ningún veredicto**. Se ha
hecho, y el resultado **corrige el diagnóstico que estaba escrito**.

### Lo que decía el diagnóstico de septiembre

> «Con el filtro de motor activo, la condición de distractor recupera **exactamente los mismos
> fragmentos** que la condición de evidencia parcial, en los tres fallos.»

Y atribuía la causa al filtro de motor, que bloquea los procedimientos del motor LF antes de que
lleguen al verificador.

### Lo que se mide ahora

| Pareja | `D-1` ¿llega el distractor? | `D-2` diferencia con `PARTIAL` |
|---|---|---|
| `C07_partial` ↔ `C08_distractor` | **SÍ**, los dos ficheros declarados | **2 fragmentos** |
| `C11_thermostat_partial` ↔ `C12_thermostat_distractor` | **NO** | **0** |
| `C15_o2_partial` ↔ `C16_o2_distractor` | **NO** | **0** |

Y la causa de los dos que fallan **no es el filtro de motor**:

```
C11_thermostat_partial excluye 1 fichero · C12_thermostat_distractor excluye 1 fichero
  solo en PARTIAL: []        solo en DISTRACTOR: []

C15_o2_partial excluye 1 · C16_o2_distractor excluye 1
  solo en PARTIAL: []        solo en DISTRACTOR: []
```

**`C12` y `C16` tienen exactamente la misma configuración que `C11` y `C15`.** El único campo que
difiere es `distractor_files`, y **el recorrido de suficiencia no lo lee**: `distractor_files` solo
lo usa E12, como etiqueta para puntuar la recuperación, no como mecanismo de inyección.

De modo que esas dos condiciones nunca fueron distintas de la parcial, y no porque un filtro
bloqueara algo, sino porque **no había nada que bloquear**: su configuración era idéntica.

El caso de la fuga de vacío es distinto y mejor de lo que se creía: `C08` excluye cinco ficheros
menos que `C07`, los distractores declarados **sí** llegan al verificador y el conjunto recuperado
**sí** difiere, en dos fragmentos.

**Esto reemplaza al diagnóstico anterior**, que se conserva marcado. La invalidación de la condición
sigue siendo correcta —no medía lo que decía medir— pero su causa era otra.

## 2. Por qué el primer intento de rediseño no sirvió, y qué enseñó

Se buscaron distractores del **mismo motor** —para que pasaran el filtro— entre documentos
semánticamente vecinos:

| Fallo | Candidato | Resultado |
|---|---|---|
| Termostato | `srvc/B3E011215171W01.pdf`, *THERMOSTAT REMOVAL/INSTALLATION [ZJ, Z6]* | **no aparece en los 40 primeros** |
| Sonda lambda | `srvc/B3E014018860W06.pdf`, *FRONT HO2S INSPECTION [ZJ, Z6]* | **no aparece en los 40 primeros** |

Los dos son plausibles para un lector y ninguno llega al verificador. El motivo es el mecanismo de
recuperación: la estrategia vigente es **guiada por el diagnóstico**, es decir filtra por los códigos
DTC de la hipótesis. Esos dos documentos **no llevan ningún DTC**, de modo que nunca entran en el
conjunto candidato.

**La lección, que acota el espacio de diseño:** un distractor solo es alcanzable si **lleva el mismo
DTC** que el fallo. No basta con que trate del mismo componente.

## 3. El espacio de diseño que queda, medido

Documentos que llevan el DTC del fallo, son del motor **ZJ/Z6** —y por tanto pasan el filtro— y
**no son el procedimiento de diagnóstico** de ese código:

| Documento | Qué es | Aparece en |
|---|---|---|
| `srvc/node_S07_0000.pdf` | **CONTROL SYSTEM WIRING DIAGRAM [ZJ, Z6]** | los **cinco** fallos |
| `srvc/B3E010200102T08.pdf` | **DIAGNOSTIC TEST MODE [ZJ, Z6]** | termostato, caudalímetro |
| `srvc/B3E010200102T10.pdf` | **KOEO/KOER SELF-TEST [ZJ, Z6]** | fuga de vacío, encendido |

Los tres cumplen lo que hace falta:

- **`D-1`** llevan el DTC, así que la recuperación guiada los alcanza, y son del motor correcto, así
  que el filtro no los bloquea;
- **`D-3`** son semánticamente plausibles: mismo sistema, mismos códigos, vocabulario solapado. Un
  esquema eléctrico del sistema de control **parece** evidencia del diagnóstico de un código de ese
  sistema;
- **`D-4`** **no** son evidencia suficiente, y la razón se declara de antemano: **alcance
  equivocado**. Un esquema de cableado es un plano, no un procedimiento de diagnóstico; un
  *self-test* describe cómo entrar en modo de prueba, no cómo diagnosticar el código.

**La razón declarada para `D-4` cambia respecto del diseño anterior**: antes era *motor equivocado*
—y por eso el filtro lo bloqueaba, que es lo que invalidó la condición—; ahora es **alcance
equivocado**, que el filtro no puede bloquear porque no tiene nada que objetar.

## 4. El rediseño

### 4.1 El mecanismo

La condición con distractor se construye **por exclusión diferencial**, que es como de verdad
funciona el recorrido:

| Condición | Qué se excluye | Qué queda disponible |
|---|---|---|
| `FULL` | nada | el procedimiento de diagnóstico y todo lo demás |
| `PARTIAL` | el procedimiento de diagnóstico **y** los documentos de alcance equivocado | solo material tangencial |
| `DISTRACTOR` v2 | **solo** el procedimiento de diagnóstico | el esquema de cableado y el *self-test* quedan arriba |

Así `D-2` se cumple **por construcción**: los dos conjuntos excluidos son distintos, de modo que los
recuperados tienen que serlo.

### 4.2 Los casos nuevos

En un **fichero nuevo**, `configs/goldset_mazda3_bk_distractor_v2.yaml`. El conjunto anotado de E19
—`configs/goldset_mazda3_bk.yaml`, huella `7fadc49fc7daaad1`— **no se toca**: está fijado por huella
en el manifiesto de la evaluación final y editarlo rompería su verificación.

| Caso nuevo | Fallo | Distractor que se deja pasar | Razón declarada de insuficiencia |
|---|---|---|---|
| `D01_vacuum_leak_distractor` | fuga de vacío | `node_S07_0000` + `B3E010200102T10` | alcance: esquema y *self-test*, no diagnóstico |
| `D02_thermostat_distractor` | termostato | `node_S07_0000` + `B3E010200102T08` | ídem |
| `D03_o2_distractor` | sonda lambda | `node_S07_0000` | ídem |

### 4.3 Qué se comprueba antes de mirar ningún veredicto

Las cuatro, en este orden, y la ejecución **se detiene** si alguna falla:

1. **`D-1`** el identificador de al menos un fragmento del distractor aparece entre los candidatos
   que llegan al verificador;
2. **`D-2`** la diferencia simétrica de identificadores frente a la condición parcial **no es vacía**;
3. **`D-3`** se justifica por escrito, con la sección y el sistema del documento;
4. **`D-4`** la razón de insuficiencia se declara **antes**: alcance equivocado.

**`D-1` y `D-2` se comprueban con una ejecución de solo recuperación**, sin verificador y sin
redactor, de modo que ningún veredicto se observa antes de que la condición esté validada.

## 5. Criterios de evaluación, fijados ahora

**Qué se mide:** la decisión del verificador en los tres casos nuevos, con su motivo, y si el informe
redactado cita algún fragmento del distractor como si sostuviera el diagnóstico.

**Qué resultado apoyaría PI.4:** que el sistema **se abstenga** en los tres, y que el motivo
registrado sea la insuficiencia de la evidencia y no la baja confianza del modelo. Si se abstiene por
confianza baja, la condición no habrá medido el rechazo de evidencia impertinente: habrá medido otra
vez la puerta de confianza.

**Qué lo cuestionaría:** que explique citando el esquema de cableado como respaldo.

**Qué no se hace:** elegir el distractor por el resultado que produzca. Los tres candidatos se fijan
en este documento, antes de ejecutar, y si el resultado es desfavorable se publica.

## 6. Lo que este protocolo no resuelve

1. **La condición sin filtro de motor no cambia.** `C09`, `C13` y `C17` miden la última línea de
   defensa con el filtro desactivado y siguen siendo válidas tal como están.
2. **Los resultados históricos de la condición con distractor no se recalculan.** Conservan su
   etiqueta `DISTRACTOR_V1_INVALID_AS_INDEPENDENT_CONDITION` y ahora también la corrección del
   diagnóstico: la causa no era el filtro.
3. **Esto no reabre E19.** Su conjunto anotado excluye las seis condiciones con distractor, y esa
   exclusión sigue siendo correcta.
4. **Tres casos nuevos no son una estimación de nada.** Con `n = 3`, lo que se obtenga describe tres
   situaciones construidas.

## 7. Estado y qué hace falta para ejecutar

**Diseñado y congelado. No ejecutado.** Hace falta:

1. escribir `configs/goldset_mazda3_bk_distractor_v2.yaml` con los tres casos;
2. ejecutar la comprobación de `D-1` y `D-2` **sin verificador**;
3. si pasan, ejecutar el experimento y publicarlo con su informe;
4. si no pasan, aplicar lo que la política pre-registrada ya decidió: **eliminar la condición del
   experimento principal** y pasarla a limitación y trabajo futuro. «Tres condiciones reales valen
   más que cuatro con una falsa.»
