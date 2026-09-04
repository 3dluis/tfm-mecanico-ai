# Resultados de las variantes no oracular y adversa

**Fecha:** 4 de septiembre de 2026 · **Verificador:** v2.1, sin modificar durante estas
pruebas · **Política congelada antes de medir:**
`docs/methodology/politica-evaluacion-no-oracular.md` y su enmienda `ENM-A01`.

## 1. Los tres canales de oráculo y qué deja abierto cada modo

| Modo | O-1 selección de ventana | O-2 búsqueda acotada por la etiqueta | O-3 códigos exigidos por la etiqueta | Artefacto |
|---|---|---|---|---|
| Oracular | abierto | abierto | abierto | `E15_suficiencia.json` |
| **NX-01 no oracular** | abierto | **cerrado** | **cerrado** | `E15_suficiencia_non_oracle.json` |
| **NX-02 adverso** | **invertido** | **cerrado** | **cerrado** | `E15_suficiencia_adverse.json` |

El resultado de 15/17 se obtiene con los tres canales abiertos y se etiqueta
**ORACLE-ASSISTED UPPER BOUND**.

## 2. NX-01: la comparación oracular frente a no oracular

**Resultado: idéntico, caso a caso.** Quince decisiones correctas de diecisiete, las mismas
quince. No cambia ninguna decisión, ninguna cobertura de afirmaciones, ningún recuento de
documentos aplicables ni de fuentes distintas.

Era la predicción declarada antes de ejecutar, y su cumplimiento significa algo concreto:
**O-2 y O-3 no aportan información que el sistema no posea en ejecución.** Sobre una ventana
que el modelo clasifica bien, derivar los códigos de la etiqueta anotada o del diagnóstico del
modelo es la misma operación.

**Lo que queda demostrado:** el oráculo del experimento central **se reduce a O-1**, la
selección de ventana. La acotación de la búsqueda y la verificación del soporte no lo
necesitan.

**Lo que sigue sin demostrarse, y no lo resuelve NX-01:** el texto de consulta de cada caso lo
redactó una persona que conocía el fallo. Describe síntomas, no nombra el diagnóstico ni el
código, pero no es una consulta ciega. Es una limitación de la construcción del conjunto
anotado.

## 3. NX-02: el escenario adverso

De las diecisiete condiciones, **once no tienen ninguna ventana mal clasificada** y se declaran
vacías. Quedan seis casos, sobre los dos fallos que el modelo confunde.

| Caso | Condición real | Diagnóstico del modelo | Confianza | Cobertura | Citas aceptadas | Decisión | Desenlace |
|---|---|---|---|---|---|---|---|
| C02 | termostato bloqueado | normal | 0,929 | 0,67 | 2 | ABSTIENE | D-2 |
| C04 | fallo de encendido | normal | **0,984** | 0,67 | 4 | ABSTIENE | D-2 |
| C10 | termostato, evidencia retirada | normal | 0,929 | 0,00 | 0 | ABSTIENE | D-4 |
| C11 | termostato, parcial | normal | 0,929 | 0,00 | 0 | ABSTIENE | D-4 |
| C12 | termostato, distractor | normal | 0,929 | 0,00 | 0 | ABSTIENE | D-4 |
| C13 | termostato, distractor sin filtro | normal | 0,929 | 0,00 | 0 | ABSTIENE | D-4 |

**Distribución: D-1 ninguno · D-2 dos · D-3 ninguno · D-4 cuatro.**

**Ninguna explicación incorrecta.** Y esta vez el dato es interpretable, porque las seis
confianzas superan el umbral de 0,79: la calibración **no** detuvo estos casos, a diferencia
de la primera ejecución adversa.

## 4. Tres acotaciones que impiden leer esto como un éxito del verificador

**Primera: D-1 se evitó por el margen de un umbral.** En C04 el sistema aceptó cuatro citas de
procedimientos reales del vehículo para un diagnóstico falso, con cobertura 0,667. Se abstuvo
porque el umbral de cobertura es 0,8. Con 0,6 habría explicado.

**Segunda: el verificador operaba con tres de sus cuatro condiciones.** El diagnóstico
`F00_normal` no tiene códigos de avería asociados, y con la lista vacía la puerta del código
**no se evalúa**. Las veinticuatro comprobaciones de esta ejecución salen sin ella. Registrado
como `EMPTY-DTC-GATE-BYPASS` en `docs/experiments/hallazgo-puerta-dtc-ausente.md`, y **no
corregido**, porque cambiar el instrumento en mitad de la evaluación invalidaría la
comparación.

**Tercera: solo se probó el error por omisión.** Los seis diagnósticos incorrectos son
`F00_normal`: el modelo no ve el fallo que hay. El caso peligroso —un fallo confundido con
**otro fallo**, con confianza alta, que llevaría al sistema a buscar y citar procedimientos de
una avería equivocada— **no está en esta ejecución porque no existe en validación**: de las
doce ventanas mal clasificadas, once son fallo hacia normal y la única de fallo hacia fallo
tiene confianza 0,579, por debajo del umbral.

## 5. Qué se puede afirmar

**Se sostiene:**

> Sobre las ventanas evaluadas, un diagnóstico incorrecto y confiado del modelo especializado
> no produjo ninguna explicación incorrecta: el sistema se abstuvo en los seis casos, y la
> abstención no la causó el umbral de confianza sino la vía de la evidencia.

**No se sostiene:**

> El verificador impide que un diagnóstico incorrecto produzca una explicación aparentemente
> bien respaldada.

El mérito de estas seis abstenciones corresponde a la **política de cobertura de
afirmaciones**, no a la comprobación de códigos, que no llegó a ejecutarse. Y el margen fue
estrecho en dos de los seis casos.

**No se ha probado en absoluto:**

> El sistema resiste un diagnóstico erróneo hacia otra avería concreta.

Requiere ventanas que no existen en esta partición. Es una limitación del conjunto de datos,
no del diseño, y define el trabajo siguiente.

## 6. Impacto sobre las afirmaciones de la pregunta de investigación

| Subpregunta | Antes | Después |
|---|---|---|
| Explicación trazable | sostenida sobre la cota superior asistida por oráculo | **igual, y ahora sin O-2 ni O-3**: NX-01 da el mismo resultado sin usar la etiqueta para buscar ni para verificar |
| Reconocimiento de insuficiencia por ausencia de evidencia | sostenida | igual |
| Rechazo de evidencia no pertinente | sostenida con v2.1 | igual |
| Comportamiento ante diagnóstico incorrecto | **no evaluado** | **evaluado parcialmente**: sin explicaciones incorrectas ante error por omisión, con tres acotaciones. Sin evidencia sobre el error por sustitución |
