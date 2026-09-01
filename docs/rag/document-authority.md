# Autoridad documental

## La similitud no es autoridad

Un fragmento de foro y un procedimiento de manual de taller pueden tener la misma
puntuación de similitud frente a una consulta. No valen lo mismo.

La autoridad se declara en el manifiesto, viaja con cada fragmento y **manda
sobre la puntuación de similitud** en el ordenamiento de evidencia.

## Niveles de fuente

| Nivel | Qué es | Ejemplos |
|---|---|---|
| **A** | Fabricante u OEM | Repair Manual, TSB, diagramas eléctricos, formación técnica, Owner's Manual, guía de mantenimiento |
| **B** | Organismos oficiales | NHTSA, SAE cuando esté legalmente disponible, documentación regulatoria |
| **C** | Técnica secundaria contrastada | Solo con justificación y procedencia completa |

Foros, blogs, respuestas de usuarios y páginas optimizadas para buscadores **no
son nivel C por defecto**. No se tratan como equivalentes a un manual OEM.

## Jerarquía de evidencia

Menor número, mayor autoridad:

| Rango | Tipo de documento |
|---|---|
| 1 | OEM Repair Manual |
| 2 | OEM Technical Service Bulletin |
| 3 | OEM Electrical Wiring Diagram |
| 4 | OEM Technical Training |
| 5 | OEM Owner's Manual |
| 6 | OEM Maintenance Guide / New Car Features |
| 7 | Documentación regulatoria u oficial |
| 8 | Fuente técnica secundaria contrastada |

Codificada en `JERARQUIA_EVIDENCIA`, accesible como `entry.evidence_rank`.

## Lo que la jerarquía no resuelve

Que un manual de taller esté en el corpus **no convierte una explicación en
sostenida**. La autoridad de la fuente y el soporte de la afirmación son cosas
distintas: un procedimiento del fabricante, correctamente citado, puede no decir
lo que la explicación le atribuye.

La verificación del soporte es independiente y se trata en la política de
suficiencia.
