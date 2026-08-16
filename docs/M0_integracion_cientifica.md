# M0 — Integración controlada del paquete de alineación científica

**16 de agosto de 2026 · rama de origen `backup-alineacion-cientifica` · integración
selectiva fichero a fichero, sin merge de rama.**

Este documento registra qué se incorporó a `main`, qué no, y por qué. La rama de origen **no
se borra**: queda como respaldo verificable de la procedencia.

## 1. Por qué no se hizo un merge de rama

Un `git merge` habría sido destructivo en la práctica. La rama de backup se separó antes de
F13 y por tanto **no contiene 71 ficheros de documentación posteriores** —toda la serie
F13–F22, los ADR 0031-0035, el protocolo ML v1 y sus adendas, las clasificaciones
exploratorias, las comparativas de modelos y el esqueleto de la memoria—, además de tener
versiones anteriores de otros 23. Integrar la rama entera habría revertido cuatro fases de
trabajo. Se incorporaron por tanto solo los ficheros exclusivos con valor científico vigente.

## 2. Clasificación

### ADOPT — incorporados íntegros a `main` (9)

| Fichero | Palabras | Qué es |
|---|---|---|
| `docs/estado_del_arte/capitulo2_estado_del_arte.md` | 10 814 | Capítulo de estado del arte redactado (Entrega 4). **Fuente primaria del capítulo 3 de la memoria** |
| `docs/estado_del_arte/estado_del_arte_y_metodologia_tutor.md` | 15 391 | Estado del arte + metodología, en formato de entrega al tutor |
| `docs/estado_del_arte/entrega1_revision_sistematica.md` | 6 431 | Primera iteración de la revisión sistemática |
| `docs/estado_del_arte/entrega2_revision_sistematica.md` | 7 615 | Segunda iteración |
| `docs/estado_del_arte/entrega3_revision_sistematica.md` | 6 520 | Tercera iteración |
| `docs/estado_del_arte/resumen_ejecutivo_estado_del_arte.md` | 829 | Resumen ejecutivo |
| `docs/estado_del_arte/afirmaciones_novedad.md` | 928 | Afirmaciones de novedad y su nivel |
| `docs/auditoria_alineacion_investigacion.md` | 3 256 | Auditoría de alineación de la investigación |
| `docs/propuesta_alineacion_final.md` | 1 965 | Propuesta de alineación — **adoptado como documento de trazabilidad**, no como norma vigente |

**Conflictos:** ninguno. Los cinco ficheros de `docs/estado_del_arte/` que ya existían en
`main` (`00_sintesis`, `linea_a`, `linea_b`, `linea_c`, `referencias_baselines`) son
**byte a byte idénticos** en ambas ramas, comprobado por hash. Los nueve adoptados son
nuevos y no pisan nada.

### MERGE_MANUALLY (2)

| Fichero | Resolución |
|---|---|
| `docs/experiments/pre-registro-v1.md` | **Incorporado a `main` como documento de entrada, explícitamente NO canónico.** Sin él, F-PREREG no podría trabajar sobre fuentes disponibles en `main`. Se le añadió una nota de adopción fechada que (a) declara que su reconciliación con `PROTO-CONF-001` se resuelve en F-PREREG y (b) advierte de que, por estar fechado el 12-08, su §11 solo recoge EXP-ANOM-001/002/003 y **debe completarse con EXP-ANOM-005…010-R2 y AUDIT-DATA-001 antes de congelar**. No se modificó su contenido |
| `docs/08_roadmap_tecnico.md` | **Se conserva la versión de `main`. No se incorpora nada de backup.** Verificado por diff: el núcleo §8.1–8.4 de backup está contenido **byte a byte** en `main`, que además añade los bloques de actualización de F5 a F22. `main` (18 499 B) es un **superconjunto estricto** de backup (6 279 B): no hay contenido que rescatar |

### DO_NOT_ADOPT (23 ficheros modificados en ambas ramas)

`docs/07`, `docs/adr/README.md`, `docs/agent-runtime/README.md`,
`docs/correspondencia_nomenclatura.md`, `docs/data-architecture/*` (2),
`docs/experiments/README.md`, los informes de F1–F9 y F12 (9), y `docs/models/*` (5).

En **todos** los casos la versión de `main` es igual o posterior. Se verificó tamaño a
tamaño: los nueve informes de fase donde backup aparecía como «mayor» difieren en
**exactamente +1 byte**, que corresponde a la corrección de la denominación aplicada
en `main` el 16-08. Ningún fichero de esta categoría contiene material que `main` haya
perdido.

### ARCHIVE_REFERENCE (0)

Ninguno. Todo lo exclusivo con valor científico se incorporó; lo no incorporado está
superado por `main`, no archivado.

## 3. Consecuencia para la memoria

**El capítulo 3 ya puede citar exclusivamente fuentes disponibles en `main`.** Su fuente
primaria —`docs/estado_del_arte/capitulo2_estado_del_arte.md`, con sus ≈153 referencias
verificadas en fuente primaria— está ahora en la rama principal, y con ella las tres
entregas de revisión sistemática que la sustentan. El aviso de procedencia que advertía de
lo contrario se retira de `docs/memoria/README.md`.

## 4. Lo que este documento no hace

No reescribe retrospectivamente ningún documento adoptado. Los ficheros entran con su
contenido y su fecha originales; lo único añadido es la nota de adopción del pre-registro,
marcada como tal y fechada, porque leerlo como canónico sería un error material.
