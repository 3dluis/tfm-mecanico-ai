# Informe de conformidad del documento con la plantilla oficial

**Fecha:** 14 de octubre de 2026 · **Documento:** `entregables/memoria.docx`, montado con
`scripts/montar_docx.py` · **Estado: PRELIMINAR.** No es la entrega definitiva, y el apartado 6 dice
por qué · **Cómo se reproduce:** las tres órdenes de `docs/entrega-docx.md` §1

## 1. Lo que el documento cumple

| Requisito de la plantilla | Estado | Comprobado así |
|---|---|---|
| Portada institucional, con el escudo y los rótulos de la titulación | **sí** | se trae de la plantilla, verbatim, con su sección y su configuración de página |
| Márgenes | **sí** | 2,5 cm arriba y abajo, 3,0 cm a izquierda y derecha, 1,25 cm de encabezado y pie: los de la plantilla, sin tocar |
| Encabezados y pies | **sí** | escudo y autor en el encabezado, título y número de página en el pie, en las 133 páginas salvo las de portada |
| Estilos propios de la titulación | **sí**, cinco de siete | «Título 1», «Título Apartado», «Título subapartado», «Cita Literal APA» y «Bibliografía APA». Los dos restantes son los de viñeta, y el texto no usa listas con viñeta |
| Numeración de apartados | **sí**, y reiniciada por capítulo | cada capítulo tiene su propia instancia de la lista; sin ello el primer apartado del capítulo 5 salía como «17» |
| Índice general | **sí**, campo nativo | se actualiza desde Word con F9 |
| Índice de figuras | **sí**, campo nativo | construido por estilo de párrafo sobre los 18 pies de figura |
| Índice de tablas | **sí**, campo nativo | construido por estilo sobre los 36 pies de tabla |
| Bibliografía con sangría francesa | **sí** | las 40 referencias con el estilo «Bibliografía APA» |
| Figuras a resolución de impresión | **sí** | las 18 a 300 puntos por pulgada; la única imagen por debajo es el escudo de la plantilla, que no es una figura del trabajo |
| Pies pegados a su figura y a su tabla | **sí** | 59 párrafos con «conservar con el siguiente»: título, imagen y procedencia viajan juntos |
| La plantilla fuente, sin modificar | **sí** | el guion la abre **solo en lectura** y escribe en una copia |

El verificador estructural —`scripts/verificar_docx.py`— termina con **«el documento conserva todo
lo que esta comprobación sabe medir»** y devuelve 0.

## 2. Lo que no cumple, y por qué

| Requisito | Estado | Motivo |
|---|---|---|
| **Extensión mínima de 50 000 palabras** | **no**: 38 803 | es la decisión abierta `D-01`. **Auditoría normativa completa en `requisitos-extension-tfm.md`**: la rúbrica oficial, recuperada el 14-10-2026, **no puntúa la extensión**; la única cifra con consecuencia declarada es la de 60 páginas sin anexos, y el documento tiene 91 páginas de capítulos |
| **Director y fecha en la portada** | **pendientes** | su dato no consta en el repositorio y no se inventa. El documento **enseña los marcadores** `[Director/a]` y `[Fecha (mes y año)]`, para que no pasen inadvertidos. Se rellenan en `configs/portada-tfm.json` |
| **Título** | **el registrado** | la decisión abierta `D-06` observa que ya no describe el alcance ejecutado, que es más estrecho. Cambiarlo es del autor y del director |
| **Referencias cruzadas con campos `REF`** | **no las hay** | decisión declarada: la numeración de figuras y tablas es literal en el texto fuente y una prueba comprueba que sea correlativa. El razonamiento está en `docs/entrega-docx.md` §5 |

## 3. Seis defectos encontrados al montar, y corregidos

Los tres primeros no los habría encontrado ninguna comprobación estructural.

| # | Qué pasaba | Cómo se vio | Corregido |
|---|---|---|---|
| 1 | **el fichero no lo abría ningún programa** | las comprobaciones estructurales lo daban por bueno; falló al convertirlo a PDF. La portada usa prefijos de espacio de nombres que Pandoc no declara, y el error aparece al cargar | se unen los prefijos de la plantilla y se retiran las marcas de comentario, que apuntaban a comentarios inexistentes |
| 2 | **los apartados se numeraban de corrido**: «17. Análisis descriptivo» en el capítulo 5 | mirando el PDF | una instancia de lista por capítulo, con el inicio forzado a 1 |
| 3 | **las tablas ocupaban el triple**: una de seis filas llenaba dos páginas | mirando el PDF | sus párrafos heredaban el espaciado del cuerpo; un estilo compacto propio. El documento pasó de 152 páginas a 117 |
| 4 | bajo cada imagen aparecía un **pie duplicado** con su texto alternativo | mirando el PDF | se retira; el texto alternativo sigue dentro de la imagen, para los lectores de pantalla |
| 5 | el **título de figura** salía en cursiva pequeña y debajo de la imagen | mirando el PDF | en negrita y encima, con la procedencia debajo |
| 6 | la portada, el encabezado y el pie mostraban **los marcadores** de la plantilla | mirando el PDF | se rellenan desde el fichero de portada; los que no tienen dato se dejan a la vista a propósito |

## 4. Revisión visual del PDF

Revisadas a tamaño real las páginas de portada, los tres índices, el inicio de cada capítulo, las
dieciocho que llevan figura, las de las tablas 5.5 y 5.8 —las dos más largas—, la bibliografía y los
tres anexos.

| Qué se miró | Resultado |
|---|---|
| Figuras cortadas | ninguna |
| Figuras separadas de su título o de su procedencia | ninguna |
| Leyendas superpuestas | ninguna; las tres que las tenían se redibujaron antes de incorporarlas |
| Tablas partidas entre páginas | las dos largas se parten, y repiten su fila de cabecera |
| Proporciones | respetadas: Word escala al ancho útil y no recorta |
| Legibilidad | **corregida el 14-10-2026.** Las figuras se dibujan ahora a 5,9 pulgadas, el ancho útil de la página, de modo que Word no las escala y un punto de la figura es un punto en el papel. Las de dos paneles pasaron a paneles apilados |
| URL largas en la bibliografía | el texto justificado las estira y aparecen con espacios dentro. Es cosmético y se corrige en Word si molesta |

## 5. Control de calidad

| Comprobación | Resultado |
|---|---|
| `ruff check` · `ruff format --check` · `mypy src` | sin incidencias, 79 ficheros |
| Suite completa sin recursos externos | **919 pruebas** en verde |
| `tests/test_memoria_figuras.py` | numeración de figuras y de tablas correlativa en los tres documentos, las dieciocho existen a 300 ppp, ningún pie omite un campo, ninguna imagen sin texto alternativo ni sin interpretación, ninguna ruta local, todas mencionadas en prosa por su número, todas en el guion que las genera |
| Validación de notebooks | los siete, reejecutados y reexportados, en verde |
| Censo de artefactos históricos | **0 desviaciones** |
| Verificación del DOCX | **0 incumplimientos** de lo exigido |
| Inspección visual del PDF | apartado 4 |

## 6. Por qué el documento es preliminar

Cinco cosas quedan abiertas, y ninguna es de formato:

1. **El reentrenamiento del adaptador**, detenido por memoria insuficiente, que `P2` mantiene como
   `BLOCKED — INFRASTRUCTURE`. No bloquea la preparación documental, pero sí cambiaría una tabla y
   dos párrafos si se ejecuta.
2. **El nombre del director** y **la fecha de convocatoria**.
3. **El título**, por `D-06`.
4. **La extensión**, por `D-01`.
5. **Las entradas `N-3` a `N-6` y las `A-` restantes** de la matriz de impacto, que son decisiones
   del autor sobre qué más incorporar.

Montar la entrega definitiva antes de resolverlas significaría montarla dos veces, con el riesgo de
que una corrección se quede solo en una de las dos versiones.
