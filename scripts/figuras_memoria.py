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
    identificador: str
    nombre: str
    dibuja: Callable[[], Figure] | None = None
    copia_de: Path | None = None
    motivo_de_la_copia: str = ""
    extras: tuple[str, ...] = field(default_factory=tuple)


FIGURAS: tuple[Figura, ...] = (
    Figura("5.1", "FIG-5-01_particiones", fig_particiones),
    Figura(
        "A.1",
        "FIG-A-01_series_normal_vs_fallo",
        copia_de=HISTORICAS / "FIG-E4-01_series_normal_vs_fallo.png",
        motivo_de_la_copia=(
            "no se puede redibujar: la función genera sus propias sesiones con el generador "
            "vigente, y el generador cambió el 1-09-2026"
        ),
    ),
    Figura("5.2", "FIG-5-02_separabilidad", fig_separabilidad),
    Figura("5.3", "FIG-5-03_forma_del_fallo", fig_forma_del_fallo),
    Figura("5.4", "FIG-5-04_mezcla_pobre", fig_mezcla_pobre),
    Figura(
        "A.2",
        "FIG-A-02_pareja_contrafactual",
        fig_pareja_contrafactual,
    ),
    Figura("5.5", "FIG-5-05_confusiones", fig_confusiones),
    Figura("B.1", "FIG-B-01_f1_por_clase", fig_f1_por_clase),
    Figura("5.10", "FIG-5-10_calibracion", fig_calibracion),
    Figura(
        "5.7",
        "FIG-5-07_limite_evidencia_termostato",
        copia_de=HISTORICAS / "FIG-E6-02_limite_evidencia_f03.png",
        motivo_de_la_copia=(
            "necesita la predicción por ventana, que el registro de E6 no guarda y que solo "
            "existió durante aquella ejecución"
        ),
    ),
    Figura(
        "5.8",
        "FIG-5-08_expresion_del_fallo",
        copia_de=SALIDA_NOTEBOOKS / "06_expresion" / "FIG-N06-01_expresion_y_aciertos.png",
        motivo_de_la_copia="la produce el notebook 06; duplicar su código daría dos fuentes de verdad",
        extras=("svg",),
    ),
    Figura("5.6", "FIG-5-06_confusor_volumen", fig_confusor_de_volumen),
    Figura("5.9", "FIG-5-09_ventana_y_descriptor", fig_ventana_y_descriptor),
    Figura(
        "5.11",
        "FIG-5-11_mapa_atribucion",
        copia_de=SALIDA_NOTEBOOKS / "04_explicabilidad" / "FIG-NB04-01_mapa_atribucion.png",
        motivo_de_la_copia="la produce el notebook 04, que calcula el mapa de señales declaradas",
        extras=("svg",),
    ),
    Figura("5.12", "FIG-5-12_recuperacion", fig_recuperacion),
    Figura(
        "5.13",
        "FIG-5-13_aplicables_vs_cobertura",
        copia_de=SALIDA_NOTEBOOKS / "05_suficiencia" / "FIG-N05-01_aplicables_vs_cobertura.png",
        motivo_de_la_copia="la produce el notebook 05, corregido el 13-10-2026 para dibujar las cinco condiciones",
        extras=("svg",),
    ),
    Figura("5.14", "FIG-5-14_ablaciones", fig_ablaciones),
    Figura(
        "5.15",
        "FIG-5-15_evaluacion_final",
        copia_de=SALIDA_NOTEBOOKS / "03_analisis_e19" / "FIG-NB03-01_primario.png",
        motivo_de_la_copia="la produce el notebook 03",
        extras=("svg",),
    ),
    Figura(
        "5.16",
        "FIG-5-16_decisiones_e19",
        copia_de=SALIDA_NOTEBOOKS / "03_analisis_e19" / "FIG-NB03-02_decisiones.png",
        motivo_de_la_copia="la produce el notebook 03",
        extras=("svg",),
    ),
    Figura("5.17", "FIG-5-17_decisiones_y_umbral", fig_decisiones_y_umbral),
    Figura("6.2", "FIG-6-02_objetivos_y_evidencia", fig_objetivos),
    Figura("6.3", "FIG-6-03_compromiso_cobertura_abstencion", fig_compromiso),
    Figura(
        "6.1",
        "FIG-6-01_recorrido_experimental",
        copia_de=SALIDA_NOTEBOOKS / "00_introduccion" / "FIG-NB00-01_recorrido.png",
        motivo_de_la_copia="la produce el notebook 00",
        extras=("svg",),
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


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("identificadores", nargs="*")
    args = analizador.parse_args(argv)

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
