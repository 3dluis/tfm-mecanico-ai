"""Presentación visual de las copias HTML de los notebooks.

El HTML que produce `nbconvert` con la plantilla `lab` es correcto pero austero:
una columna de celdas sin navegación. Este módulo le añade, **sin tocar el
contenido**, lo que hace falta para leerlo como un documento:

- una cabecera con el título del trabajo y enlaces a los otros seis notebooks;
- un índice lateral construido a partir de los títulos del propio notebook;
- tipografía, tablas y figuras pensadas para leer, y el apartado «En un minuto»
  destacado;
- un botón para ocultar el código (modo lectura) y una hoja de estilo de impresión.

Todo va **dentro del fichero**: sin fuentes ni scripts externos, para que el HTML
se abra sin red y viaje suelto. Las salidas, las figuras y el texto no cambian.
"""

from __future__ import annotations

import html
import re

#: Los siete notebooks, en orden de lectura, con la etiqueta corta de la navegación.
NAVEGACION: tuple[tuple[str, str], ...] = (
    ("00_introduccion", "Introducción"),
    ("01_exploracion_obd", "Datos OBD-II"),
    ("02_comparacion_modelos", "Modelos"),
    ("03_analisis_e19", "Evaluación final"),
    ("04_explicabilidad", "Explicabilidad"),
    ("05_suficiencia_y_abstencion", "Suficiencia"),
    ("06_expresion_del_fallo", "Expresión del fallo"),
)

TITULO_TRABAJO = "Mecánico IA · trabajo práctico del TFM"

#: Autor que figura en los metadatos de cada página.
AUTOR = "Luis Daniel Diaz"

CSS = """
:root {
  --mi-tinta: #1f2328;
  --mi-suave: #59636e;
  --mi-fondo: #fbfaf7;
  --mi-papel: #ffffff;
  --mi-linea: #e3e0d8;
  --mi-acento: #1f5f8b;
  --mi-acento-claro: #e8f1f7;
  --mi-aviso: #8a5a00;
  --mi-aviso-claro: #fdf4e3;
  --mi-ancho: 920px;
  --mi-lateral: 270px;
  --mi-cabecera: 56px;
}
html { scroll-padding-top: calc(var(--mi-cabecera) + 16px); }
body.mi-doc {
  background: var(--mi-fondo) !important;
  color: var(--mi-tinta);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial,
    sans-serif;
  margin: 0;
}
/* ---------------------------------------------------------------- cabecera */
.mi-cabecera {
  position: sticky; top: 0; z-index: 50;
  height: var(--mi-cabecera);
  display: flex; align-items: center; gap: 18px;
  padding: 0 24px;
  background: #16324a; color: #fff;
  box-shadow: 0 1px 6px rgba(0, 0, 0, .18);
}
.mi-marca { font-weight: 650; letter-spacing: .2px; white-space: nowrap; font-size: 15px; }
.mi-nav { display: flex; gap: 4px; overflow-x: auto; flex: 1; scrollbar-width: none; }
.mi-nav a {
  color: #cfe0ee; text-decoration: none; font-size: 13px; white-space: nowrap;
  padding: 6px 10px; border-radius: 6px;
}
.mi-nav a:hover { background: rgba(255, 255, 255, .12); color: #fff; }
.mi-nav a.mi-actual { background: #fff; color: #16324a; font-weight: 600; }
.mi-boton {
  border: 1px solid rgba(255, 255, 255, .45); background: transparent; color: #fff;
  border-radius: 6px; padding: 6px 12px; font-size: 13px; cursor: pointer; white-space: nowrap;
}
.mi-boton:hover { background: rgba(255, 255, 255, .12); }
/* ------------------------------------------------------------------ índice */
.mi-indice {
  position: fixed; top: calc(var(--mi-cabecera) + 20px); left: 20px;
  width: var(--mi-lateral); max-height: calc(100vh - var(--mi-cabecera) - 40px);
  overflow-y: auto; font-size: 13px; line-height: 1.35;
  padding: 14px 14px 14px 16px; background: var(--mi-papel);
  border: 1px solid var(--mi-linea); border-radius: 10px;
}
.mi-indice h2 {
  font-size: 11px; text-transform: uppercase; letter-spacing: .8px;
  color: var(--mi-suave); margin: 0 0 8px; border: 0; padding: 0;
}
.mi-indice a {
  display: block; color: var(--mi-tinta); text-decoration: none;
  padding: 4px 6px; border-radius: 5px; border-left: 2px solid transparent;
}
.mi-indice a.mi-n3 { padding-left: 18px; color: var(--mi-suave); font-size: 12px; }
.mi-indice a:hover { background: var(--mi-acento-claro); }
.mi-indice a.mi-activo {
  border-left-color: var(--mi-acento); color: var(--mi-acento); font-weight: 600;
  background: var(--mi-acento-claro);
}
/* ---------------------------------------------------------------- documento */
body.mi-doc main, body.mi-doc .jp-Notebook {
  max-width: var(--mi-ancho); margin: 28px auto 60px !important;
  padding: 36px 48px !important; background: var(--mi-papel);
  border: 1px solid var(--mi-linea); border-radius: 12px;
  box-shadow: 0 2px 14px rgba(30, 30, 20, .05);
}
@media (min-width: 1300px) {
  body.mi-doc main, body.mi-doc .jp-Notebook {
    margin-left: calc(var(--mi-lateral) + 60px + max(0px, (100vw - var(--mi-lateral) - 60px
      - var(--mi-ancho) - 40px) / 2)) !important;
  }
}
@media (max-width: 1299px) { .mi-indice { display: none; } }
.jp-Cell { padding: 2px 0 !important; }
.jp-InputPrompt, .jp-OutputPrompt { display: none !important; }
.jp-RenderedMarkdown {
  font-size: 15.5px !important; line-height: 1.62 !important; color: var(--mi-tinta);
}
.jp-RenderedMarkdown h1 {
  font-size: 30px !important; line-height: 1.2; margin: 6px 0 14px !important;
  color: #16324a; letter-spacing: -.3px;
}
.jp-RenderedMarkdown h2 {
  font-size: 21px !important; margin: 34px 0 10px !important; padding-bottom: 6px;
  border-bottom: 2px solid var(--mi-linea); color: #16324a;
}
.jp-RenderedMarkdown h3 { font-size: 17px !important; margin: 22px 0 6px !important; }
.jp-RenderedMarkdown a.anchor-link { display: none; }
.jp-RenderedMarkdown p { margin: 0 0 12px !important; }
.jp-RenderedMarkdown strong { color: #10202e; }
.jp-RenderedMarkdown code {
  background: #f1efe9; border-radius: 4px; padding: 1px 5px; font-size: .9em;
}
.jp-RenderedMarkdown blockquote {
  margin: 14px 0; padding: 10px 16px; border-left: 4px solid var(--mi-aviso);
  background: var(--mi-aviso-claro); border-radius: 0 8px 8px 0; color: var(--mi-tinta);
}
.jp-RenderedMarkdown hr { border: 0; border-top: 1px solid var(--mi-linea); margin: 26px 0; }
/* tablas del texto y de las salidas */
.jp-RenderedMarkdown table, .jp-RenderedHTMLCommon table {
  border-collapse: collapse !important; width: auto; max-width: 100%;
  font-size: 13.5px !important; margin: 10px 0 18px !important; display: block; overflow-x: auto;
}
.jp-RenderedMarkdown th, .jp-RenderedHTMLCommon th {
  background: #eef2f5 !important; color: #16324a; font-weight: 600 !important;
  text-align: left !important; padding: 7px 10px !important;
  border-bottom: 2px solid #c9d3dc !important;
}
.jp-RenderedMarkdown td, .jp-RenderedHTMLCommon td {
  padding: 6px 10px !important; border-bottom: 1px solid var(--mi-linea) !important;
  text-align: left !important; vertical-align: top;
}
.jp-RenderedMarkdown tr:nth-child(even) td, .jp-RenderedHTMLCommon tr:nth-child(even) td {
  background: #faf9f6 !important;
}
/* ficha del notebook: la primera tabla */
.mi-ficha table td:first-child { white-space: nowrap; color: var(--mi-suave); width: 1%; }
/* «En un minuto» y «Cómo leer este notebook» */
.mi-caja { border-radius: 10px; padding: 2px 22px 8px; margin: 18px 0; }
.mi-caja > h2, .mi-caja > h3 {
  font-size: 13px !important; text-transform: uppercase; letter-spacing: .8px;
  border: 0 !important; margin: 14px 0 6px !important; padding: 0 !important;
}
.mi-caja-minuto { background: var(--mi-acento-claro); border: 1px solid #c4dbea; }
.mi-caja-minuto > h2, .mi-caja-minuto > h3 { color: var(--mi-acento) !important; }
.mi-caja-minuto li { margin-bottom: 6px; }
.mi-caja-leer { background: #f6f5f1; border: 1px solid var(--mi-linea); font-size: 14.5px; }
.mi-caja-leer > h2, .mi-caja-leer > h3 { color: var(--mi-suave) !important; }
/* código */
.jp-CodeCell .jp-InputArea {
  border: 1px solid var(--mi-linea); border-radius: 8px; overflow: hidden; margin: 6px 0;
}
.jp-CodeCell .jp-InputArea-editor, .jp-CodeCell .highlight {
  background: #f6f5f1 !important; font-size: 12.5px !important;
}
.jp-OutputArea-output pre {
  font-size: 12.5px !important; line-height: 1.45; background: #fcfcfb;
  border-left: 3px solid #d5dde4; padding: 8px 12px !important; border-radius: 0 6px 6px 0;
}
.jp-OutputArea-output img {
  display: block; margin: 10px auto; max-width: 100%; height: auto;
  border: 1px solid var(--mi-linea); border-radius: 8px; background: #fff;
}
body.mi-sin-codigo .jp-CodeCell .jp-Cell-inputWrapper { display: none !important; }
/* pie */
.mi-pie {
  max-width: var(--mi-ancho); margin: 0 auto 40px; color: var(--mi-suave); font-size: 12px;
  text-align: center;
}
@media (min-width: 1300px) {
  .mi-pie { margin-left: calc(var(--mi-lateral) + 60px + max(0px, (100vw - var(--mi-lateral)
    - 60px - var(--mi-ancho) - 40px) / 2)); }
}
/* impresión */
@media print {
  .mi-cabecera, .mi-indice, .mi-boton { display: none !important; }
  body.mi-doc { background: #fff !important; }
  body.mi-doc main, body.mi-doc .jp-Notebook {
    margin: 0 !important; padding: 0 !important; border: 0; box-shadow: none; max-width: none;
  }
  .jp-Cell { break-inside: avoid; }
  .jp-RenderedMarkdown h2 { break-after: avoid; }
}
"""

JS = """
(function () {
  var cuerpo = document.body;
  cuerpo.classList.add('mi-doc');
  // La ficha es la primera celda de texto.
  var celdas = document.querySelectorAll('.jp-MarkdownCell');
  if (celdas.length) { celdas[0].classList.add('mi-ficha'); }
  // «En un minuto» y «Cómo leer»: el título y lo que le sigue hasta el próximo título
  // del mismo nivel o superior se envuelven en un recuadro, estén en la celda que estén.
  function enCaja(patron, clase) {
    document.querySelectorAll('.jp-RenderedMarkdown h2, .jp-RenderedMarkdown h3').forEach(
      function (h) {
        if (!patron.test(h.textContent)) { return; }
        var caja = document.createElement('div');
        caja.className = 'mi-caja ' + clase;
        h.parentNode.insertBefore(caja, h);
        var nodo = h;
        while (nodo) {
          var siguiente = nodo.nextSibling;
          caja.appendChild(nodo);
          if (siguiente && /^(H1|H2|H3|HR)$/.test(siguiente.nodeName)) { break; }
          nodo = siguiente;
        }
      });
  }
  enCaja(/^\\s*En un minuto/i, 'mi-caja-minuto');
  enCaja(/^\\s*Cómo leer este notebook/i, 'mi-caja-leer');
  // Índice lateral a partir de los títulos de nivel 2 y 3.
  var indice = document.getElementById('mi-indice-lista');
  var titulos = document.querySelectorAll('.jp-RenderedMarkdown h2, .jp-RenderedMarkdown h3');
  var enlaces = [];
  titulos.forEach(function (h, i) {
    if (!h.id) { h.id = 'mi-seccion-' + i; }
    var a = document.createElement('a');
    a.href = '#' + h.id;
    a.textContent = h.textContent.replace(/\\u00b6\\s*$/, '').trim();
    var entrada = h.parentNode.classList.contains('mi-caja');
    a.className = h.tagName === 'H3' && !entrada ? 'mi-n3' : 'mi-n2';
    indice.appendChild(a);
    enlaces.push([h, a]);
  });
  // Resalta en el índice la sección que se está leyendo.
  function marcar() {
    var actual = null;
    for (var i = 0; i < enlaces.length; i++) {
      if (enlaces[i][0].getBoundingClientRect().top < 120) { actual = enlaces[i][1]; }
    }
    enlaces.forEach(function (p) { p[1].classList.toggle('mi-activo', p[1] === actual); });
  }
  document.addEventListener('scroll', marcar, { passive: true });
  marcar();
  // Modo lectura: oculta el código, conserva salidas y figuras.
  var boton = document.getElementById('mi-boton-codigo');
  var clave = 'mecanico-ia-sin-codigo';
  function aplicar(oculto) {
    cuerpo.classList.toggle('mi-sin-codigo', oculto);
    boton.textContent = oculto ? 'Mostrar código' : 'Ocultar código';
  }
  var guardado = false;
  try { guardado = window.localStorage.getItem(clave) === '1'; } catch (e) {}
  aplicar(guardado);
  boton.addEventListener('click', function () {
    var oculto = !cuerpo.classList.contains('mi-sin-codigo');
    aplicar(oculto);
    try { window.localStorage.setItem(clave, oculto ? '1' : '0'); } catch (e) {}
  });
})();
"""


def _cabecera(actual: str) -> str:
    marca_actual = ' class="mi-actual"'
    enlaces = "".join(
        f'<a href="{nombre}.html"{marca_actual if nombre == actual else ""}>'
        f"{html.escape(etiqueta)}</a>"
        for nombre, etiqueta in NAVEGACION
    )
    return (
        '<header class="mi-cabecera">'
        f'<span class="mi-marca">{html.escape(TITULO_TRABAJO)}</span>'
        f'<nav class="mi-nav" aria-label="Notebooks">{enlaces}</nav>'
        '<button class="mi-boton" id="mi-boton-codigo" type="button">Ocultar código</button>'
        "</header>"
        '<aside class="mi-indice" aria-label="Índice"><h2>En este notebook</h2>'
        '<div id="mi-indice-lista"></div></aside>'
    )


def decorar(cuerpo: str, nombre: str, *, commit: str, fecha: str) -> str:
    """Devuelve el HTML de `nbconvert` con cabecera, índice, estilo y pie."""
    titulo = dict(NAVEGACION).get(nombre, nombre)
    cuerpo = re.sub(r"<html([^>]*)\blang=\"[^\"]*\"", r'<html\1lang="es"', cuerpo, count=1)
    cuerpo = re.sub(
        r"<title>.*?</title>",
        f"<title>{html.escape(titulo)} · Mecánico IA</title>",
        cuerpo,
        count=1,
        flags=re.S,
    )
    cuerpo = cuerpo.replace(
        "</head>",
        f'<meta name="author" content="{AUTOR}">\n<style>{CSS}</style>\n</head>',
        1,
    )
    cuerpo = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + _cabecera(nombre), cuerpo, count=1)
    pie = (
        '<footer class="mi-pie">'
        f"Copia ejecutada de <code>notebooks/{html.escape(nombre)}.ipynb</code> · commit "
        f"<code>{html.escape(commit)}</code> · exportada el {html.escape(fecha)}. "
        "El contenido es el del notebook; esta página solo cambia su presentación."
        "</footer>"
    )
    return cuerpo.replace("</body>", f"{pie}<script>{JS}</script>\n</body>", 1)
