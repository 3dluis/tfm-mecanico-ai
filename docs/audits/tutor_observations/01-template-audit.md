# 01 · Auditoría de restos de plantilla

**Fecha:** 10 de septiembre de 2026 · **Origen:** primera petición del director, revisión de
septiembre de 2026 · **Alcance:** `docs/memoria/`.

## Criterio de clasificación

| Clase | Qué es | Qué se hace |
|---|---|---|
| 1 · basura de plantilla | texto heredado de la plantilla, sin contenido propio | se elimina |
| 2 · comentario de trabajo | nota resoluble con el material del proyecto | se resuelve y se elimina |
| 3 · decisión metodológica | criterio que el autor ya ha tomado y no está redactado | se incorpora como texto académico |
| 4 · pregunta abierta al director | decisión que no corresponde al autor | se traslada a `preguntas-abiertas-al-director.md` |

La distinción importa: **una pregunta metodológica genuina no es basura de plantilla**, y
borrarla habría eliminado una decisión pendiente en lugar de resolverla.

## Hallazgos

| Marca | Ubicación | Clase | Acción | Estado |
|---|---|---|---|---|
| `[CONSENSUAR]` estilo de cita: ¿rige IEEE? | `bibliografia.md:6` | 2 | La plantilla oficial fija **APA** de forma expresa. Resuelto objetivamente; queda abierta solo la edición (P-04) | **CERRADO** |
| `[CONSENSUAR]` objetivo general: dos verbos y cláusula embarcada | `cap2_objetivos.md:31` | 4 | Trasladado a P-01. Texto reescrito declarando la divergencia sin suponer respuesta | **TRASLADADO** |
| `[CONSENSUAR]` OE3: no supervisado → supervisado | `cap2_objetivos.md:64` | 4 | Trasladado a P-02. El texto declara qué condiciona el cambio | **TRASLADADO** |
| `[CONSENSUAR]` OE5: dos escenarios → cuatro condiciones | `cap2_objetivos.md:84` | 2 | **Resuelto por el correo del director**, que valida expresamente el diseño de cuatro condiciones | **CERRADO** |
| `[CONSENSUAR]` acotación de alcance sin constancia formal | `cap2_objetivos.md:107` | 4 | Trasladado a P-03 | **TRASLADADO** |
| `[CONSENSUAR]` alcance más estrecho, L-13 | `cap6_conclusiones.md:69` | 4 | Trasladado a P-03, misma cuestión | **TRASLADADO** |
| `[CONSENSUAR]` alcance de la novedad de PI.4 | `cap3_marco_teorico.md:214` | 3 | Incorporado como acotación académica del alcance | **CERRADO** |
| `[DECISIÓN DEL AUTOR]` motor, cilindrada y transmisión | `cap4_marco_metodologico.md` | 3 | Incorporado: supuesto de trabajo del generador, con su justificación documental y qué cambia si entran datos reales | **CERRADO** |
| `[DECISIÓN DEL AUTOR: criterio o descriptiva]` en M6 | `cap4_marco_metodologico.md` | 3 | Resuelto: **descriptiva**, porque el trabajo no fija presupuesto de latencia al haber quedado el despliegue embarcado fuera del alcance | **CERRADO** |
| `[AMPLIAR]` ×3 más encabezado | `cap3_marco_teorico.md:8,63,135,191` | 2 | Se resuelven al desarrollar el capítulo 3 | **EN CURSO, tarea C** |
| `[RECONCILIAR]` ×2 | `cap5_resultados.md:8,47` | 2 | **Bloqueado**: el capítulo 5 está congelado hasta la reejecución canónica de recuperación. La discrepancia entre informe y registro está además abierta como hallazgo de auditoría desde hace cinco pases | **BLOQUEADO** |
| `[VERIFY_SOURCE]` ×8 | `bibliografia.md` | 2 | Cuatro se verifican en la tarea E; las demás quedan declaradas | **PARCIAL** |

## Lo que no se ha hecho, y por qué

**Ninguna marca se ha borrado sin resolverse.** Las siete de decisión se han clasificado una
por una: dos se resolvieron con material objetivo —la plantilla y el correo del director—, tres
se incorporaron como texto académico porque eran decisiones ya tomadas y sin redactar, y cuatro
se trasladaron íntegras al registro de preguntas abiertas.

Las dos de `cap5_resultados.md` **permanecen**. Resolverlas exige elegir entre dos cifras de F1
que no coinciden, y el capítulo está congelado: cualquier cifra nueva debe proceder de una
ejecución posterior al cierre de las auditorías pendientes.

## Estado

Marcas en el cuerpo de la memoria antes: **18**. Después: **6**, de las cuales 4 se cierran con
la tarea C y 2 están bloqueadas por la congelación del capítulo 5.
