# Procedimiento de entrega: del Markdown al DOCX y al PDF

**Fecha:** 13 de octubre de 2026 · **Qué es:** cómo se produce el documento entregable a partir de
los capítulos en Markdown, qué conserva cada vía y qué hay que hacer a mano · **Qué NO es:** la
entrega. **No se genera todavía el documento definitivo**, porque quedan resultados pendientes

## 1. El punto de partida, y por qué esto hace falta

Los capítulos viven en `docs/memoria/*.md` y el entregable es un documento de Word sobre la
plantilla oficial de la titulación. Entre una cosa y otra hay una conversión, y la conversión es el
sitio donde se pierden en silencio los elementos que no son texto: los estilos institucionales, el
índice automático, el índice de figuras, los pies pegados a su imagen, las referencias cruzadas y
los márgenes. Que el fichero resultante se abra y se lea bien no significa que conserve nada de eso.

Por eso el procedimiento tiene tres partes y no una: convertir, **completar a mano lo que ninguna
conversión hace**, y comprobar el resultado por inspección del fichero.

## 2. Lo que la plantilla impone

Medido sobre la propia plantilla con `scripts/verificar_docx.py`:

| Qué | Valor |
|---|---|
| Márgenes | superior e inferior 2,5 cm; izquierdo y derecho 3,0 cm; encabezado y pie 1,25 cm |
| Estilos propios | `Título 1` (capítulo), `Título Apartado`, `Título subapartado`, `Viñeta TFM`, `Viñeta Numerada TFM`, `Bibliografía APA`, `Cita Literal APA` |
| Índice | campo automático, ya presente en la plantilla |
| Índice de figuras | **no está en la plantilla**, pero el estilo `Tabla de ilustraciones` sí está declarado, de modo que añadirlo no la contradice |
| Pie de figura | la plantilla **no trae estilo propio**. Se usa la convención que los capítulos ya aplican a las tablas: título en negrita encima, procedencia en cursiva debajo |

La plantilla advierte además que no se modifiquen sus estilos ni su formato. El procedimiento lo
respeta: la conversión escribe **dentro** de la plantilla, no al lado.

## 3. Las dos vías, y qué conserva cada una

Ninguna de las dos está instalada en este entorno. La elección es del autor y condiciona el resto.

| | **Vía A · pandoc con documento de referencia** | **Vía B · guion propio con `python-docx`** |
|---|---|---|
| Qué es | `pandoc cap5.md -o cap5.docx --reference-doc=plantilla.docx` | un guion del repositorio que recorre el Markdown y escribe párrafos con el estilo que les toca |
| Qué hace falta | instalar pandoc en el sistema | añadir `python-docx` como dependencia del grupo de documentación |
| Estilos de la plantilla | los **hereda** del documento de referencia para los estilos estándar: encabezados, texto, tablas. Los propios de la titulación —`Viñeta TFM`, `Cita Literal APA`— no se aplican solos | se aplican **uno a uno y a propósito**, que es más trabajo y más control |
| Imágenes y pies | incrusta la imagen y escribe el pie como párrafo suelto: **no quedan pegados** | se pueden pegar con «conservar con el siguiente» |
| Índice y referencias cruzadas | no los genera | se pueden insertar como campos |
| Esfuerzo | bajo para la primera versión, alto para dejarla fina | alto al principio, bajo después |
| Reproducibilidad | depende de la versión de pandoc instalada | depende solo del repositorio |

**Recomendación.** Vía A para las primeras revisiones, porque produce algo legible en minutos y lo
que se revisa en esta fase es el contenido. Vía B si la entrega final se va a repetir varias veces,
porque entonces el coste de completar a mano cada versión supera al de escribir el guion una vez.

## 4. Lo que ninguna conversión hace, y hay que hacer en Word

Esta lista no es opcional y conviene tenerla delante al montar el documento.

1. **Actualizar el índice automático** una vez insertado todo el contenido.
2. **Insertar el índice de figuras** —referencias cruzadas, tabla de ilustraciones— con el estilo
   `Tabla de ilustraciones` que la plantilla declara.
3. **Convertir las menciones a figuras en referencias cruzadas**, para que «la Figura 5.4» siga
   apuntando a la figura correcta si se inserta una antes.
4. **Pegar cada pie a su imagen** con «conservar con el siguiente», y pegar el título a la imagen.
   Es el defecto más frecuente y el más visible: una figura al final de una página y su pie al
   principio de la siguiente.
5. **Revisar los saltos de página** para que ninguna figura quede cortada.
6. **Comprobar el ancho de las figuras apaisadas**: las de dos paneles miden 9,6 pulgadas y hay que
   escalarlas al ancho útil de 15 cm, no recortarlas.
7. **Aplicar `Bibliografía APA`** a la bibliografía, que necesita sangría francesa.

## 5. La comprobación, que es la parte que no se salta

```bash
uv run python scripts/verificar_docx.py memoria.docx \
    --plantilla "../24-25 Plantilla TFM MUIA.docx"
```

Abre el fichero, lo descomprime y cuenta lo que hay dentro: qué estilos de la plantilla se usan y
cuáles están declarados, si existe el campo del índice automático, si existe el índice de figuras,
cuántos pies tienen la forma «Figura N.M.», cuántas líneas de procedencia hay, cuántas imágenes se
han incrustado y a qué resolución, cuántas tablas, los márgenes de sección y el recuento de
palabras. Devuelve 1 si falta algo de lo exigido, de modo que sirve de puerta.

Pasada sobre la propia plantilla vacía, el guion informa de lo que cabría esperar: estilos
correctos, índice presente, y ni índice de figuras ni pies, porque la plantilla no tiene contenido.
Esa pasada es la referencia contra la que se compara el documento montado.

## 6. El PDF

Se genera **desde Word**, con «Guardar como PDF», y no desde una conversión intermedia: cualquier
otra vía vuelve a tocar la paginación y el documento revisado deja de corresponderse con el
entregado. El PDF es para revisión visual —que ninguna figura quede cortada, que los pies acompañen
a su imagen, que las figuras se lean a tamaño de página— y la revisión se hace **sobre papel o a
tamaño real**, no al 40 % en pantalla, porque es ahí donde se ve si una leyenda de 7 puntos es
legible.

## 7. El recuento de palabras, que condiciona el montaje

La plantilla fija un mínimo de 50 000 palabras y un máximo de 60 000, y estima los anexos en un 20 %
como mucho. El guion de comprobación da el recuento del DOCX montado; conviene mirarlo **antes** de
decidir qué anexos entran, y no después.

## 8. Cuándo se monta la entrega definitiva

No todavía. Quedan dos cosas abiertas que cambiarían el documento: el reentrenamiento del adaptador
del modelo de lenguaje, detenido por memoria insuficiente y pendiente de una máquina adecuada, y la
decisión sobre los anexos. Montar la entrega antes significaría montarla dos veces, y la segunda vez
con el riesgo de que una corrección se quede solo en una de las dos versiones.
