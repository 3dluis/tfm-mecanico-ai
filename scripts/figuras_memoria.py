"""Exporta las figuras de la memoria a `artifacts/figures/memoria/`.

**Qué es y qué no es.** Es el **registro** de qué figura lleva cada número en el
documento y la orden de consola que las produce. **No contiene código de dibujo**:
ese vive en `mecanico_ia_exp.visualization.memoria`, dentro del paquete, bajo
comprobación de tipos y disponible para los notebooks. La separación existe para
que no haya dos implementaciones de la misma figura.

**De dónde lee.** De las tablas versionadas de `artifacts/tables/`, de los
registros de `experiments/` y, en una figura, del conjunto procesado
`synthetic_v2`, cuyas huellas congela el manifiesto de la evaluación final.
**No ejecuta ningún experimento, no abre ningún conjunto de prueba y no escribe
fuera de su directorio de salida.**

**Qué no puede redibujar.** Cuatro figuras se copian de donde ya estaban, porque
regenerarlas exigiría algo que no está autorizado o que ya no existe:

- la serie pareada de E4 **no se puede redibujar**: la función que la hace genera
  sus propias sesiones con el generador vigente, y el generador cambió el 1 de
  septiembre de 2026. Redibujarla hoy daría otra figura;
- el límite de evidencia del termostato necesita la predicción **por ventana**,
  que el registro de E6 no guarda y que solo existió durante aquella ejecución;
- la expresión efectiva del fallo y el recorrido experimental los produce un
  notebook, que es su única fuente.

    uv run python scripts/figuras_memoria.py            # todas
    uv run python scripts/figuras_memoria.py 5.6 5.11   # solo esas
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from matplotlib.figure import Figure

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.visualization.memoria import (
    fig_ablaciones,
    fig_calibracion,
    fig_compromiso,
    fig_confusiones,
    fig_confusor_de_volumen,
    fig_decisiones_y_umbral,
    fig_f1_por_clase,
    fig_forma_del_fallo,
    fig_mezcla_pobre,
    fig_objetivos,
    fig_pareja_contrafactual,
    fig_particiones,
    fig_recuperacion,
    fig_separabilidad,
    fig_ventana_y_descriptor,
    guardar,
)
from mecanico_ia_exp.visualization.memoria.base import DESTINO, HISTORICAS, SALIDA_NOTEBOOKS


@dataclass(frozen=True)
class Figura:
    """Una figura del documento, con la cadena que la une al dato que la produjo.

    Los campos de trazabilidad no son adorno: son la fuente de la que se emite
    `docs/figuras-tfm.md`. Mantenerlos aquí evita que la tabla del documento y el
    registro que produce las figuras se separen, que es lo que pasó al renumerar
    el capítulo 5 y dejó la tabla describiendo figuras que ya no llevaban ese
    número.
    """

    identificador: str
    nombre: str
    dibuja: Callable[[], Figure] | None = None
    copia_de: Path | None = None
    motivo_de_la_copia: str = ""
    extras: tuple[str, ...] = field(default_factory=tuple)
    #: Trazabilidad: experimento → conjunto → partición → notebook → ubicación.
    experimento: str = ""
    conjunto: str = ""
    particion: str = ""
    notebook: str = ""
    ubicacion: str = ""
    limitaciones: str = ""

    @property
    def capitulo(self) -> str:
        inicial = self.identificador.split(".")[0]
        return f"anexo {inicial}" if inicial.isalpha() else f"capítulo {inicial}"

    @property
    def produce(self) -> str:
        if self.dibuja is not None:
            return f"`{self.dibuja.__module__.rsplit('.', 1)[-1]}.{self.dibuja.__name__}()`"
        assert self.copia_de is not None
        return f"copiada de `{self.copia_de.name}`"

    def huella(self) -> str:
        ruta = DESTINO / f"{self.nombre}.png"
        if not ruta.is_file():
            return "—"
        return hashlib.sha256(ruta.read_bytes()).hexdigest()[:16]


FIGURAS: tuple[Figura, ...] = (
    Figura(
        "5.1",
        "FIG-5-01_particiones",
        fig_particiones,
        experimento="E5, ventanado y reparto",
        conjunto="synthetic_v2",
        particion="las tres",
        notebook="01_exploracion_obd",
        ubicacion="cap. 5 · Análisis descriptivo de la muestra",
        limitaciones="describe el diseño, no la dificultad de cada clase",
    ),
    Figura(
        "A.1",
        "FIG-A-01_series_normal_vs_fallo",
        copia_de=HISTORICAS / "FIG-E4-01_series_normal_vs_fallo.png",
        motivo_de_la_copia=(
            "no se puede redibujar: la función genera sus propias sesiones con el generador "
            "vigente, y el generador cambió el 1-09-2026"
        ),
        experimento="E4",
        conjunto="synthetic_v1",
        particion="sesiones pareadas",
        notebook="01_exploracion_obd",
        ubicacion="anexo A · §A.6",
        limitaciones="no regenerable: su generador cambió el 1-09-2026",
    ),
    Figura(
        "5.2",
        "FIG-5-02_separabilidad",
        fig_separabilidad,
        experimento="E4, análisis exploratorio",
        conjunto="synthetic_v1",
        particion="bloques de 60 s",
        notebook="01_exploracion_obd",
        ubicacion="cap. 5 · Análisis descriptivo de la muestra",
        limitaciones="ordena pero no explica; `synthetic_v1` no se reconstruye (L-25)",
    ),
    Figura(
        "5.3",
        "FIG-5-03_forma_del_fallo",
        fig_forma_del_fallo,
        experimento="análisis contrafactual T2, derivado de E2 y E5",
        conjunto="synthetic_v2",
        particion="entrenamiento",
        notebook="06_expresion_del_fallo",
        ubicacion="cap. 5 · Análisis descriptivo de la muestra",
        limitaciones="una sesión por condición; describe el instrumento, no un motor real",
    ),
    Figura(
        "5.4",
        "FIG-5-04_mezcla_pobre",
        fig_mezcla_pobre,
        experimento="E4 y E5",
        conjunto="synthetic_v2",
        particion="entrenamiento",
        notebook="01_exploracion_obd",
        ubicacion="cap. 5 · Análisis descriptivo de la muestra",
        limitaciones="efecto descriptivo sin contraste; separabilidad no es rendimiento demostrado",
    ),
    Figura(
        "A.2",
        "FIG-A-02_pareja_contrafactual",
        fig_pareja_contrafactual,
        experimento="análisis contrafactual T2, derivado de E2 y E5",
        conjunto="synthetic_v2",
        particion="entrenamiento",
        notebook="06_expresion_del_fallo",
        ubicacion="anexo A · §A.7",
        limitaciones="una sesión por condición; una desviación observable no implica detectabilidad",
    ),
    Figura(
        "5.5",
        "FIG-5-05_confusiones",
        fig_confusiones,
        experimento="E6 y E7",
        conjunto="synthetic_v2",
        particion="validación",
        notebook="02_comparacion_modelos",
        ubicacion="cap. 5 · PI.1 · Diagnóstico, calibración y atribución",
        limitaciones="una ejecución por modelo, sin repeticiones ni intervalos",
    ),
    Figura(
        "B.1",
        "FIG-B-01_f1_por_clase",
        fig_f1_por_clase,
        experimento="E6 y E7",
        conjunto="synthetic_v2",
        particion="validación",
        notebook="02_comparacion_modelos",
        ubicacion="anexo B · §B.2",
        limitaciones="una ejecución por modelo, sin repeticiones",
    ),
    Figura(
        "5.10",
        "FIG-5-10_calibracion",
        fig_calibracion,
        experimento="E6, calibrado en E15",
        conjunto="synthetic_v2",
        particion="validación",
        notebook="02_comparacion_modelos",
        ubicacion="cap. 5 · PI.1",
        limitaciones="dos puntos, no una curva de fiabilidad: E6 no guarda la confianza por ventana",
    ),
    Figura(
        "5.7",
        "FIG-5-07_limite_evidencia_termostato",
        copia_de=HISTORICAS / "FIG-E6-02_limite_evidencia_f03.png",
        motivo_de_la_copia=(
            "necesita la predicción por ventana, que el registro de E6 no guarda y que solo "
            "existió durante aquella ejecución"
        ),
        experimento="E6",
        conjunto="synthetic_v2",
        particion="validación, las 14 ventanas de F03",
        notebook="02_comparacion_modelos",
        ubicacion="cap. 5 · PI.1",
        limitaciones="no regenerable: necesita la predicción por ventana, que E6 no guarda",
    ),
    Figura(
        "5.8",
        "FIG-5-08_expresion_del_fallo",
        copia_de=SALIDA_NOTEBOOKS / "06_expresion" / "FIG-N06-01_expresion_y_aciertos.png",
        motivo_de_la_copia="la produce el notebook 06; duplicar su código daría dos fuentes de verdad",
        extras=("svg",),
        experimento="E6, fase G del diseño de PI.1",
        conjunto="synthetic_v2",
        particion="validación, las 70 ventanas con fallo",
        notebook="06_expresion_del_fallo",
        ubicacion="cap. 5 · PI.1",
        limitaciones="no está comprobado que las cinco ventanas sin señal sean las cinco falladas",
    ),
    Figura(
        "5.6",
        "FIG-5-06_confusor_volumen",
        fig_confusor_de_volumen,
        experimento="E6 y E7 sobre los dos conjuntos",
        conjunto="synthetic_v2 y synthetic_v3",
        particion="validación",
        notebook="02_comparacion_modelos",
        ubicacion="cap. 5 · PI.1",
        limitaciones="cambian dos cosas a la vez: volumen y generador; `synthetic_v3` no se reconstruye",
    ),
    Figura(
        "5.9",
        "FIG-5-09_ventana_y_descriptor",
        fig_ventana_y_descriptor,
        experimento="E5 y E6",
        conjunto="synthetic_v2",
        particion="entrenamiento, una ventana",
        notebook="01_exploracion_obd",
        ubicacion="cap. 5 · PI.1",
        limitaciones="una ventana como ilustración; en ralentí la caída queda truncada por el suelo físico",
    ),
    Figura(
        "5.11",
        "FIG-5-11_mapa_atribucion",
        copia_de=SALIDA_NOTEBOOKS / "04_explicabilidad" / "FIG-NB04-01_mapa_atribucion.png",
        motivo_de_la_copia="la produce el notebook 04, que calcula el mapa de señales declaradas",
        extras=("svg",),
        experimento="E9, atribución",
        conjunto="synthetic_v2",
        particion="validación, 18 casos",
        notebook="04_explicabilidad",
        ubicacion="cap. 5 · PI.1",
        limitaciones="atribución no es causalidad; solo las diez principales por caso",
    ),
    Figura(
        "5.12",
        "FIG-5-12_recuperacion",
        fig_recuperacion,
        experimento="E12, reejecución canónica",
        conjunto="corpus del vehículo",
        particion="6 casos, 5 puntuados",
        notebook="no tiene notebook propio",
        ubicacion="cap. 5 · PI.2 · Recuperación y trazabilidad",
        limitaciones="n = 5 casos puntuados: recuentos, no tasas",
    ),
    Figura(
        "5.13",
        "FIG-5-13_aplicables_vs_cobertura",
        copia_de=SALIDA_NOTEBOOKS / "05_suficiencia" / "FIG-N05-01_aplicables_vs_cobertura.png",
        motivo_de_la_copia="la produce el notebook 05, corregido el 13-10-2026 para dibujar las cinco condiciones",
        extras=("svg",),
        experimento="E15, verificador v2.1",
        conjunto="synthetic_v2",
        particion="17 casos sobre 5 ventanas",
        notebook="05_suficiencia_y_abstencion",
        ubicacion="cap. 5 · PI.3 y PI.4",
        limitaciones="17 casos de 5 ventanas: no son observaciones independientes",
    ),
    Figura(
        "5.14",
        "FIG-5-14_ablaciones",
        fig_ablaciones,
        experimento="E18, cuatro ablaciones",
        conjunto="synthetic_v2",
        particion="los mismos 17 casos",
        notebook="04_explicabilidad",
        ubicacion="cap. 5 · Contribución de cada componente",
        limitaciones="A2 quedó INCONCLUSA; denominadores de 9 y de 5 ejecuciones",
    ),
    Figura(
        "5.15",
        "FIG-5-15_evaluacion_final",
        copia_de=SALIDA_NOTEBOOKS / "03_analisis_e19" / "FIG-NB03-01_primario.png",
        motivo_de_la_copia="la produce el notebook 03",
        extras=("svg",),
        experimento="E19, tercer intento",
        conjunto="synthetic_v2",
        particion="**prueba**",
        notebook="03_analisis_e19",
        ubicacion="cap. 5 · La evaluación final sobre el conjunto de prueba",
        limitaciones="recuentos con intervalo de Wilson; cero observado no es riesgo cero",
    ),
    Figura(
        "5.16",
        "FIG-5-16_decisiones_e19",
        copia_de=SALIDA_NOTEBOOKS / "03_analisis_e19" / "FIG-NB03-02_decisiones.png",
        motivo_de_la_copia="la produce el notebook 03",
        extras=("svg",),
        experimento="E19, tercer intento",
        conjunto="synthetic_v2",
        particion="**prueba**",
        notebook="03_analisis_e19",
        ubicacion="cap. 5 · La evaluación final sobre el conjunto de prueba",
        limitaciones="22 ejecuciones del estrato operativo, que repiten casos",
    ),
    Figura(
        "5.17",
        "FIG-5-17_decisiones_y_umbral",
        fig_decisiones_y_umbral,
        experimento="E19, tercer intento",
        conjunto="synthetic_v2",
        particion="**prueba**",
        notebook="03_analisis_e19",
        ubicacion="cap. 5 · La evaluación final sobre el conjunto de prueba",
        limitaciones="observación descriptiva sobre dos errores; el umbral no se revisa a su vista",
    ),
    Figura(
        "6.2",
        "FIG-6-02_objetivos_y_evidencia",
        fig_objetivos,
        experimento="E1–E19 (uno por fila)",
        conjunto="sin conjunto: es documental",
        particion="—",
        notebook="no tiene notebook propio",
        ubicacion="cap. 6 · Conclusiones sobre los objetivos",
        limitaciones="documental: no es evidencia",
    ),
    Figura(
        "6.3",
        "FIG-6-03_compromiso_cobertura_abstencion",
        fig_compromiso,
        experimento="E15",
        conjunto="synthetic_v2",
        particion="validación",
        notebook="05_suficiencia_y_abstencion",
        ubicacion="cap. 6 · Limitaciones",
        limitaciones="el compromiso se dibuja sobre 17 casos",
    ),
    Figura(
        "6.1",
        "FIG-6-01_recorrido_experimental",
        copia_de=SALIDA_NOTEBOOKS / "00_introduccion" / "FIG-NB00-01_recorrido.png",
        motivo_de_la_copia="la produce el notebook 00",
        extras=("svg",),
        experimento="E1–E19 (etiquetas de etapa)",
        conjunto="sin conjunto: es la arquitectura",
        particion="—",
        notebook="00_introduccion",
        ubicacion="cap. 6 · Conclusiones sobre los objetivos",
        limitaciones="ilustrativa: no es evidencia",
    ),
)


def producir(figura: Figura) -> Path | None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    if figura.dibuja is not None:
        return guardar(figura.dibuja(), figura.nombre)
    assert figura.copia_de is not None
    if not figura.copia_de.is_file():
        print(
            f"  {figura.identificador:5s} FALTA el origen: "
            f"{figura.copia_de.relative_to(paths.ROOT)}",
            file=sys.stderr,
        )
        return None
    destino = DESTINO / f"{figura.nombre}.png"
    shutil.copy2(figura.copia_de, destino)
    for extra in figura.extras:
        origen = figura.copia_de.with_suffix(f".{extra}")
        if origen.is_file():
            shutil.copy2(origen, DESTINO / f"{figura.nombre}.{extra}")
    return destino


#: El entregable del que se leen las páginas de la matriz de procedencia.
PDF_ENTREGABLE = paths.ROOT / "entregables" / "memoria.pdf"


def paginas_del_pdf(ruta: Path | None = None) -> dict[str, int]:
    """En qué página del PDF entregado aparece el pie de cada figura.

    Se busca el pie —«Figura 5.3.»— y no la imagen, porque el pie es texto y la
    imagen no: una búsqueda sobre el texto extraído es verificable por quien
    quiera repetirla. Si el PDF no está, se devuelve vacío y la matriz sale sin
    esa columna en lugar de fallar: el registro tiene que poder emitirse en un
    clon recién hecho, donde `entregables/` no existe.
    """
    destino = ruta or PDF_ENTREGABLE
    if not destino.is_file():
        return {}
    try:
        from pypdf import PdfReader
    except ImportError:
        return {}
    lector = PdfReader(str(destino))
    paginas: dict[str, int] = {}
    for numero, pagina in enumerate(lector.pages, 1):
        texto = pagina.extract_text() or ""
        for figura in FIGURAS:
            if figura.identificador in paginas:
                continue
            if f"Figura {figura.identificador}." in texto:
                paginas[figura.identificador] = numero
    return paginas


def trazabilidad() -> str:
    """La matriz de procedencia, emitida desde el registro.

    Se emite y no se escribe a mano porque las dos cosas se separan: al renumerar
    el capítulo 5 la tabla del documento quedó describiendo figuras que ya no
    llevaban ese número, y nada lo detectó. Generándola desde aquí, el número, el
    fichero y la función no pueden discrepar.
    """
    orden = sorted(
        FIGURAS,
        key=lambda f: (
            f.identificador[0].isalpha(),
            f.identificador.split(".")[0],
            int(f.identificador.split(".")[1]),
        ),
    )
    paginas = paginas_del_pdf()
    lineas = [
        "| Fig. | Experimento | Conjunto | Partición | Notebook | Función o copia | Fichero | "
        "Huella (SHA-256, 16) | Ubicación | Pág. PDF |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    lineas += [
        f"| {f.identificador} | {f.experimento} | `{f.conjunto}` | {f.particion} | "
        f"`{f.notebook}` | {f.produce} | `{f.nombre}.png` | `{f.huella()}` | {f.ubicacion} | "
        f"{paginas.get(f.identificador, '—')} |"
        for f in orden
    ]
    lineas += ["", "| Fig. | Limitaciones declaradas en su pie |", "|---|---|"]
    lineas += [f"| {f.identificador} | {f.limitaciones} |" for f in orden]
    return "\n".join(lineas)


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("identificadores", nargs="*")
    analizador.add_argument(
        "--trazabilidad",
        action="store_true",
        help="emite la matriz de procedencia en Markdown y no dibuja nada",
    )
    args = analizador.parse_args(argv)

    if args.trazabilidad:
        print(trazabilidad())
        return 0

    pedidas = set(args.identificadores)
    faltan = pedidas - {f.identificador for f in FIGURAS}
    if faltan:
        print(f"no existen: {', '.join(sorted(faltan))}", file=sys.stderr)
        return 1

    fallos = 0
    for figura in FIGURAS:
        if pedidas and figura.identificador not in pedidas:
            continue
        destino = producir(figura)
        if destino is None:
            fallos += 1
            continue
        como = "dibujada" if figura.dibuja is not None else "copiada"
        print(f"  {figura.identificador:5s} {como:9s} {destino.relative_to(paths.ROOT)}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
