# INC-E15-01 — Una tabla local de E15 borrada por un patrón demasiado amplio

**Fecha:** 12 de octubre de 2026 · **Detectado por:** el censo de artefactos históricos, al
reconstruirlo · **Estado:** **no restaurada**, y así se declara.

## Qué pasó

Limpiando los artefactos de una ejecución de comprobación etiquetada `verif`, se usó el patrón
`rm -f tables/*verif*`. Ese patrón **también encaja con `E15_suficiencia_verifier_v1.csv`**, porque
«verifier» contiene «verif». El fichero se borró.

## Qué era

La tabla por caso de la ejecución de E15 con el **verificador v1**, el primero, que el índice de
experimentos marca como `NEGATIVE → SUPERSEDED`: 9 de 17 decisiones correctas, con el hallazgo
`LEXICAL-SUPPORT-CONFOUND` que motivó la política v2.

## Qué se ha perdido y qué no

**No se declara restaurada.** No existe copia versionada en `artifacts/tables/` —no se publicó,
porque la ejecución quedó superada— y regenerarla exigiría PostgreSQL con pgvector y el corpus del
manual, que no se redistribuye. Decir que está restaurada porque los números «deberían ser los
mismos» sería exactamente lo que este trabajo no hace.

**Lo que no se ha perdido, y es lo que sostiene la cifra:**

| | Estado |
|---|---|
| `experiments/E15_suficiencia_verifier_v1.json` | **intacto, versionado y verificado** contra su huella |
| La cifra 9/17 que cita el índice | sale del JSON, no de la tabla |
| El hallazgo `LEXICAL-SUPPORT-CONFOUND` | documentado en `docs/experiments/hallazgo-lexical-support-confound.md` |

**Ninguna figura, tabla, documento o notebook del repositorio citaba ese CSV.** Se comprobó
buscándolo en `docs/`, `research/`, `notebooks/`, `src/`, `scripts/` y los `.md` de la raíz: cero
referencias. Era una salida intermedia de una ejecución superada.

**Su huella se conserva en el censo** (`1adee19a54e3ad9a…`), marcada como no versionada y ausente.
Si alguien la regenera algún día con la cadena documental completa, podrá comprobar si es la misma.

## Por qué el censo lo detectó y Git no

`tables/` está en `.gitignore`. Git no tenía nada que decir sobre ese fichero. El censo sí: al
reconstruirlo apareció entre las entradas conservadas por no estar presentes, y de ahí salió la
pregunta de por qué faltaba.

Es el segundo daño real que el censo detecta en dos días, después de `INC-E5-01`. Los dos los causé
yo mismo, trabajando sobre el repositorio, y ninguno de los dos habría salido a la luz sin él.

## Qué se corrige

1. **El patrón de limpieza.** Los artefactos de una ejecución de comprobación se borran por su ruta
   exacta, obtenida de `destinos_de(...)`, no por un glob escrito a mano. Un glob con un prefijo
   corto encaja con más de lo que se cree.
2. **La etiqueta de las ejecuciones de comprobación** pasa a ser suficientemente específica como
   para no colisionar con un nombre de artefacto existente.
3. **Queda registrado** en lugar de arreglado en silencio.
