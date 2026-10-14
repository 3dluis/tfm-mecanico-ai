# Procedimiento de entrega: del Markdown al DOCX y al PDF

**Fecha:** 13 de octubre de 2026 · **Qué es:** cómo se produce el documento entregable a partir de
los capítulos en Markdown, qué hace cada herramienta y qué hay que hacer a mano · **Estado:**
implementado y ejecutado. **El documento montado es preliminar**, no la entrega definitiva

## 1. En dos órdenes

```bash
uv run python scripts/montar_docx.py                      # entregables/memoria.docx
soffice --headless --convert-to pdf --outdir entregables \
        entregables/memoria.docx                          # entregables/memoria.pdf
uv run python scripts/verificar_docx.py entregables/memoria.docx \
        --plantilla "../24-25 Plantilla TFM MUIA.docx"    # comprobación estructural
```

`entregables/` está fuera del control de versiones. Lo versionado es el procedimiento y el texto
fuente; el binario se regenera.

### Lo que el PDF no trae, y por qué

Los tres índices son **campos nativos de Word**, no texto fijo. El documento lleva la marca
`w:updateFields`, de modo que Word ofrece actualizarlos al abrirlo y `F9` los rellena. La conversión
a PDF de LibreOffice en modo desatendido **no evalúa esos campos**, así que el PDF de revisión
muestra en su lugar la línea «Actualice el índice desde Word (F9)».

No se sustituyen por texto estático: un índice escrito a mano se desincroniza con el documento en
cuanto cambia una página, y el aviso impreso es preferible a una lista de páginas que miente. Para
un PDF con los índices rellenos, el camino es abrir el DOCX en Word, actualizar los campos y
exportar desde allí.

Se intentó actualizarlos mediante el puente UNO de LibreOffice; el proceso no se sostuvo en este
equipo y la vía queda documentada como no resuelta, no como imposible.

## 2. Herramientas, con su versión

| Herramienta | Versión usada | Para qué | Cómo se instala |
|---|---|---|---|
| **Pandoc** | 3.12.1 | convierte el Markdown a DOCX heredando de la plantilla sus estilos, su configuración de página y sus encabezados y pies | `brew install pandoc` |
| **`python-docx`** y la biblioteca estándar | 1.2.0 | ensamblan el resultado: portada, estilos, índices y numeración | extra `docx` del proyecto: `uv sync --extra docx` |
| **LibreOffice** | 26.8.1 | genera el PDF de revisión sin intervención manual | `brew install --cask libreoffice` |

Ninguna ruta del procedimiento es absoluta ni depende de este equipo: la plantilla se pasa por
parámetro y el guion escribe siempre dentro del repositorio.

## 3. Qué hereda Pandoc de la plantilla, y qué no

Comprobado sobre la plantilla real antes de implementar nada.

| | |
|---|---|
| **Sí hereda** | los estilos declarados —los siete propios de la titulación entre ellos—, los márgenes, los encabezados y los pies, y emite un campo `TOC` nativo |
| **No hereda** | la **portada institucional**, porque de un documento de referencia solo toma el formato y nunca el contenido |
| **No acierta** | los **estilos de apartado**: escribe «Título 2» en lugar de «Título Apartado», y el cuerpo con estilos propios en lugar de «Normal» |
| **No hace** | el **índice de figuras** ni el de tablas, ni la **primera sección** con su encabezado distinto |

De ahí que el montaje tenga dos pasos y no uno.

## 4. Qué hace el guion de montaje

1. **Concatena** los nueve ficheros de `docs/memoria/` en el orden de la plantilla y los convierte
   con Pandoc.
2. **Prepende la portada** de la plantilla, cortando por el párrafo que **contiene** el primer
   `sectPr`: en OOXML el salto de sección vive dentro del último párrafo de la sección, y cortar
   antes dejaría la portada sin su configuración de página. Trae además los prefijos de espacio de
   nombres que la portada usa y Pandoc no declara —sin ellos el fichero supera cualquier
   comprobación estructural y **ningún programa puede abrirlo**— y retira las marcas de comentario,
   que apuntan a identificadores que el documento convertido no tiene.
3. **Traduce los estilos**: apartados y subapartados a los de la titulación, cuerpo a «Normal»,
   bloques citados a «Cita Literal APA», y los párrafos de dentro de las tablas a un estilo
   compacto, porque heredar el espaciado del cuerpo convertía una tabla de seis filas en dos
   páginas.
4. **Numera los apartados por capítulo.** La plantilla los numera con una única lista continua, de
   modo que el primer apartado del capítulo 5 salía como «17». Cada capítulo recibe su propia
   instancia de la misma lista, con el inicio forzado a 1.
5. **Pega cada figura y cada tabla a su título y a su procedencia**, con «conservar con el
   siguiente». Es el defecto más visible de un documento montado sin cuidado.
6. **Retira el pie duplicado** que Pandoc escribe bajo cada imagen repitiendo su texto alternativo,
   que ya viaja dentro de la imagen para los lectores de pantalla.
7. **Inserta los tres índices** como campos nativos de Word.
8. **Rellena los marcadores** de la portada, el encabezado y el pie desde `configs/portada-tfm.json`.
   Un campo vacío **deja el marcador a la vista**: un documento que enseña «[Director/a]» avisa de
   que falta un dato; uno que lo borra, no.

La plantilla original no se abre en escritura en ningún momento.

## 5. Los índices, y una decisión declarada

Los tres son **campos nativos** y se actualizan desde Word con F9. El índice general se construye
por nivel de título; el de figuras y el de tablas, **por estilo de párrafo**, sobre los dos estilos
de pie que el guion añade a la copia.

Lo que esa elección implica, y conviene decirlo: **la numeración de las figuras y las tablas es
literal en el texto fuente**, no la genera Word con campos `SEQ`. A cambio, el texto fuente es
legible por sí mismo, ningún campo sin actualizar muestra un error en lugar de un número, y una
prueba del repositorio —`tests/test_memoria_figuras.py`— comprueba que la numeración sea correlativa
y que cada figura se mencione en el cuerpo por su número. La alternativa, `SEQ` más `REF`, daría
numeración automática al precio de las tres cosas anteriores.

## 6. Lo que sigue haciéndose a mano, en Word

1. **Actualizar los tres índices** con F9. Hasta entonces muestran el texto que lo pide.
2. **Revisar los saltos de página** de las figuras más altas.
3. **Comprobar el ancho de las figuras apaisadas**: las de dos paneles miden 9,6 pulgadas y Word las
   escala al ancho útil; conviene mirar que sus leyendas de 7 puntos sigan legibles en papel.
4. **Rellenar el director y la fecha** cuando se decidan, en `configs/portada-tfm.json`, y volver a
   montar.

## 7. El PDF

El de `entregables/memoria.pdf` lo genera LibreOffice y sirve para **revisión visual**: es
reproducible, no necesita intervención y es el que permite mirar todas las páginas con figura. Su
paginación **no es exactamente la de Word**, y la entrega definitiva se exporta desde Word para que
el documento revisado y el entregado se correspondan página a página.

La revisión se hace a tamaño real, no al 40 % en pantalla: es ahí donde se ve si una leyenda de
siete puntos es legible.

## 8. Qué comprueba el verificador

Abre el DOCX, lo descomprime y cuenta: qué estilos de la plantilla se usan y cuáles están
declarados, si existen los tres campos de índice, cuántos pies tienen la forma «Figura N.M.»,
cuántas líneas de procedencia hay, cuántas imágenes se han incrustado y cuáles referencia el cuerpo,
su resolución —sin medir las que vienen de la plantilla sin modificar, que no son figuras del
trabajo—, cuántas tablas, los márgenes de sección y el recuento de palabras. Devuelve 1 si falta
algo de lo exigido, de modo que sirve de puerta.

## 9. El recuento de palabras, y un problema que no está en el formato

La plantilla fija un mínimo de 50 000 palabras y un máximo de 60 000. El documento montado tiene
**35 736**. La diferencia no se arregla con los anexos: no puntúan, y el mínimo que la sesión
informativa del curso fija es «sin anexos». Es la decisión abierta `D-01`, con tres cifras oficiales
incompatibles, y está planteada en `docs/audits/propuesta-anexos.md` §8.

## 10. Cuándo se monta la entrega definitiva

No todavía. Quedan abiertos el reentrenamiento del adaptador —detenido por memoria insuficiente—, el
nombre del director, la fecha de convocatoria, la decisión sobre el título y la de `D-01`. Montar la
entrega antes significaría montarla dos veces, y la segunda vez con el riesgo de que una corrección
se quede solo en una de las dos versiones.
