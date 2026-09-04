# Plan de reejecución canónica

**Fecha:** 4 de septiembre de 2026 · **Motivado por:** `MIXED-EMBEDDING-SPACE` ·
**Estado:** propuesto, **pendiente del quality gate de diseño**. No se ejecuta nada hasta que
las cinco auditorías se pronuncien sobre este plan.

**Commit de la corrección:** `43e2e87`. **Commit de las pruebas en rojo:** `c6a95be`.
**Commit de la política:** `54071a2`.

## 1. Orden, y por qué no es «lo barato primero»

Todo lo que cite una cifra de recuperación queda **congelado** hasta que exista el resultado
canónico. Corregir primero la documentación obligaría a corregirla dos veces y publicaría
cifras que van a cambiar.

| # | Paso | Depende de |
|---|---|---|
| 1 | Suficiencia E15/E17, modo oracular | la corrección |
| 2 | Suficiencia, modo no oracular | 1 |
| 3 | Suficiencia, modo adverso | 1 |
| 4 | Recuperación E12, las cuatro estrategias | la corrección |
| 5 | Agente E13 | 1 |
| 6 | Generación de datos de ajuste | la corrección |
| 7 | Líneas base y unidad inferencial, recalculadas | 1 |
| 8 | v2.2 medido, si el gate lo autoriza | 1, 7 |

El paso 6 es el más incómodo: el adaptador del modelo de lenguaje **ya está entrenado** sobre
datos generados con recuperación de procedencia indeterminada. Regenerar los datos no
reentrena el adaptador; decidir si se reentrena es una decisión aparte y posterior, con su
coste declarado.

## 2. Expectativa registrada antes de medir

**No hay expectativa direccional, y se declara para que el resultado sea interpretable.**
Eliminar la mitad de los candidatos —los de un espacio ajeno— puede subir o bajar cualquier
cifra: la mezcla pudo introducir ruido y pudo también colocar por azar un fragmento útil.

Lo único que se afirma de antemano: **el resultado nuevo será interpretable y el anterior no lo
era**, porque hasta ahora la procedencia de cada fragmento recuperado era indeterminada.

**El 15/17 puede cambiar.** Si cambia, manda el nuevo. Si no cambia, tampoco es una
confirmación del anterior: sería que el defecto no alteraba estas cinco ventanas.

## 3. Qué se compara, y en qué unidad

Sobre la **unidad primaria fijada: la ventana de origen, N = 5, y N = 3 para contrastes entre
condiciones.** Los recuentos de 17 decisiones y 14 configuraciones acompañan como descriptivos,
nunca solos.

| Magnitud | Antes | Después |
|---|---|---|
| Decisiones correctas, recuento descriptivo | 15/17 | por medir |
| Línea base `ALWAYS_ABSTAIN`, **obligatoria** | 12/17 | por medir |
| Techo alcanzable | 15/17 | por medir |
| Cobertura de explicación con evidencia completa | 3/5 | por medir |
| Explicaciones sin soporte suficiente | 0 | por medir |
| Posiciones duplicadas por mezcla de espacios | 24 de 150 | **0 esperado** |
| Recuperación E12, las cuatro estrategias | tabla vigente | por medir |

## 4. Condiciones del experimento tras las decisiones

La condición de distractor **queda eliminada** del experimento principal. Las condiciones que
manipulan una variable observable son: evidencia completa, evidencia retirada y evidencia
parcial. La variante sin filtro de motor se conserva **declarada como no verificada**: no
cumple el requisito de que el distractor entre en el conjunto recuperable.

La contaminación de la condición parcial del primer fallo se declara junto a su resultado.

## 5. Lo que no se toca en esta reejecución

Umbral 0,79 · conjunto `synthetic_v2` · semilla 20260901 · corpus · calibración isotónica cv=5
· clasificación del papel por sección (v2.1) · filtro de motor, cuya refutación queda registrada
y cuya política de sustitución **no se implementa** por convertir el sistema en abstencionista.

**Una sola variable cambia: el espacio de embeddings deja de mezclarse.**
