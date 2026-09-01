# Matriz claim → evidencia

**Estado: vacía por diseño.** Se rellena cuando se redacte cada sección, no antes.

Escribir aquí un claim que todavía no tiene sección sería construir la narrativa antes que
la evidencia, que es exactamente lo que el método prohíbe.

## Formato

| Claim | Enunciado abreviado | Tipo | Fuente | Nivel | Uso | Lenguaje admitido |
|---|---|---|---|---|---|---|
| C-001 | | E1 | REF-014 | fuerte | Cap. 3 §3.2 | «los estudios revisados muestran» |

**Tipos:** E1 evidencia externa · E2 evidencia experimental propia · E3 inferencia ·
E4 decisión metodológica · E5 contexto descriptivo.

**Niveles:** fuerte · medio · débil · ninguno. Un claim de nivel «ninguno» no se afirma.

## Estado de la evidencia disponible a 1 de septiembre de 2026

| Tipo | Disponibilidad |
|---|---|
| **E1** — evidencia externa | **144 referencias** consolidadas en `references.md`, procedentes del barrido legacy. Verificadas en fuente primaria según declara el origen; con campos APA incompletos |
| **E2** — evidencia experimental propia, marco canónico | **E1 y E2 cerradas** (entorno y datos sintéticos). Ningún resultado de modelo, recuperación, explicación, trazabilidad ni abstención |
| **E2** — evidencia experimental propia, marco legacy | 14 estudios ejecutados, sujetos al control de relevancia de `legacy-map.md` |
| **E3** — inferencias | ninguna registrada |
| **E4** — decisiones metodológicas | ADR-001 (marco canónico) y las 5 decisiones abiertas del plan experimental |
| **E5** — contexto descriptivo | plan experimental, modelo de evidencia, política de abstención, diseño experimental |

## Consecuencia

**Ninguna afirmación del capítulo 5 puede escribirse todavía**, porque no hay E2 en el marco
canónico más allá de la caracterización de los datos sintéticos. Lo que sí puede sostenerse
con E1 es el capítulo 3, y con E4/E5 el capítulo 4.
