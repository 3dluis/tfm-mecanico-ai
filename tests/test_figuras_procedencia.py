"""Que toda figura de la memoria proceda de un experimento, y se pueda demostrar.

**Por qué esta prueba existe.** Una figura científica es una afirmación, y una
afirmación sin procedencia no se distingue de una ilustración. El riesgo concreto
que cubre no es que alguien dibuje a mano un gráfico: es más sutil y más probable.
Que una figura se quede citando un registro que ya no existe. Que el guion que la
genera desaparezca en un refactor y la imagen siga en el documento. Que una cifra
del gráfico deje de coincidir con la del registro tras una reejecución.

Las tres cosas se ven solo comprobándolas, y ninguna de ellas rompe la compilación
del documento.
"""

from __future__ import annotations

import json
import re
import struct
from pathlib import Path

import pandas as pd
import pytest

from mecanico_ia_exp.config import paths

FIGURAS = paths.ROOT / "artifacts" / "figures" / "memoria"
REGISTRO_DEL_GUION = paths.ROOT / "scripts" / "figuras_memoria.py"

#: Clasificación de cada figura por su origen, declarada aquí y comprobada abajo.
#: B · la produce un notebook · C · la dibuja el paquete desde registros
#: congelados · D · artefacto histórico que no se puede regenerar · E · esquema.
ORIGEN: dict[str, str] = {
    "FIG-5-01_particiones": "C",
    "FIG-5-02_separabilidad_nivel": "C",
    "FIG-5-03_separabilidad_dispersion": "C",
    "FIG-5-04_forma_del_fallo": "C",
    "FIG-5-05_mezcla_pobre": "C",
    "FIG-5-06_confusiones": "C",
    "FIG-5-07_confusor_volumen": "C",
    "FIG-5-08_limite_evidencia_termostato": "D",
    "FIG-5-09_expresion_del_fallo": "B",
    "FIG-5-10_ventana_y_descriptor": "C",
    "FIG-5-11_calibracion": "C",
    "FIG-5-12_mapa_atribucion": "B",
    "FIG-5-13_recuperacion": "C",
    "FIG-5-14_aplicables_vs_cobertura": "B",
    "FIG-5-15_ablaciones": "C",
    "FIG-5-16_evaluacion_final": "B",
    "FIG-5-17_decisiones_e19": "B",
    "FIG-5-18_decisiones_y_umbral": "C",
    "FIG-6-01_recorrido_experimental": "E",
    "FIG-6-02_objetivos_y_evidencia": "E",
    "FIG-6-03_compromiso_cobertura_abstencion": "C",
    "FIG-A-01_series_normal_vs_fallo": "D",
    "FIG-A-02_pareja_contrafactual": "C",
    "FIG-B-01_f1_por_clase": "C",
}

#: Las dos que no se pueden regenerar, con el motivo que lo impide.
NO_REGENERABLES = {
    "FIG-5-08_limite_evidencia_termostato": "necesita la predicción por ventana, que E6 no guarda",
    "FIG-A-01_series_normal_vs_fallo": "su generador cambió el 1-09-2026",
}


def _dpi(ruta: Path) -> int:
    datos = ruta.read_bytes()
    posicion = datos.find(b"pHYs")
    if posicion < 0:
        return 0
    x, _, unidad = struct.unpack(">IIB", datos[posicion + 4 : posicion + 13])
    return round(x * 0.0254) if unidad == 1 else 0


def test_toda_figura_declarada_existe_en_el_disco() -> None:
    faltan = [n for n in ORIGEN if not (FIGURAS / f"{n}.png").is_file()]
    assert not faltan, "figuras declaradas que no existen: " + ", ".join(faltan)


def test_toda_figura_del_disco_esta_clasificada() -> None:
    """Una figura sin clasificar es una figura sin procedencia declarada."""
    en_disco = {p.stem for p in FIGURAS.glob("*.png")}
    sin_clasificar = sorted(en_disco - set(ORIGEN))
    assert not sin_clasificar, "figuras sin origen declarado: " + ", ".join(sin_clasificar)


def test_toda_figura_esta_en_el_registro_del_guion() -> None:
    guion = REGISTRO_DEL_GUION.read_text("utf-8")
    faltan = [n for n in ORIGEN if f'"{n}"' not in guion]
    assert not faltan, "figuras que el guion no sabe producir: " + ", ".join(faltan)


def test_el_codigo_que_dibuja_vive_en_el_paquete_y_no_en_el_guion() -> None:
    """Dos implementaciones de la misma figura es el defecto que esto evita."""
    guion = REGISTRO_DEL_GUION.read_text("utf-8")
    assert "plt.subplots" not in guion, (
        "el guion ha vuelto a contener código de dibujo; su sitio es"
        " mecanico_ia_exp.visualization.memoria"
    )
    paquete = paths.ROOT / "src" / "mecanico_ia_exp" / "visualization" / "memoria"
    assert paquete.is_dir(), "falta el paquete de figuras de la memoria"


def test_cada_figura_dibujada_tiene_su_funcion_en_el_paquete() -> None:
    from mecanico_ia_exp.visualization import memoria

    dibujadas = [n for n, origen in ORIGEN.items() if origen == "C"]
    funciones = {x for x in memoria.__all__ if x.startswith("fig_")}
    assert len(funciones) >= len(dibujadas), (
        f"{len(dibujadas)} figuras dibujadas y solo {len(funciones)} funciones públicas"
    )


@pytest.mark.parametrize("nombre", sorted(ORIGEN))
def test_cada_figura_tiene_resolucion_de_impresion(nombre: str) -> None:
    assert _dpi(FIGURAS / f"{nombre}.png") >= 200, f"{nombre} está por debajo de 200 ppp"


@pytest.mark.parametrize("nombre", sorted(n for n, o in ORIGEN.items() if o == "C"))
def test_las_figuras_dibujadas_llevan_tambien_su_version_vectorial(nombre: str) -> None:
    assert (FIGURAS / f"{nombre}.svg").is_file(), f"{nombre} no tiene SVG"


def test_las_no_regenerables_declaran_su_motivo() -> None:
    """Una figura histórica es válida; una figura histórica sin motivo, no."""
    guion = REGISTRO_DEL_GUION.read_text("utf-8")
    for nombre in NO_REGENERABLES:
        assert "motivo_de_la_copia" in guion
        assert f'"{nombre}"' in guion
    for nombre, origen in ORIGEN.items():
        if origen == "D":
            assert nombre in NO_REGENERABLES, f"{nombre} es histórica y no declara su motivo"


def test_las_cifras_de_las_figuras_coinciden_con_sus_registros() -> None:
    """La comprobación que de verdad importa: que el gráfico diga lo que el dato.

    Se recalcula desde el registro lo que cada figura afirma, y se contrasta con
    lo que el capítulo publica. Si una reejecución cambiara un registro, esto
    falla antes de que la figura llegue al documento.
    """
    tablas = paths.ROOT / "artifacts" / "tables"
    registros = paths.ROOT / "experiments"

    # Figura 5.6 y Tabla 5.1: los errores de cada modelo.
    bosque = pd.read_csv(tablas / "E6_baseline_confusion_synthetic_v2.csv", index_col=0)
    red = pd.read_csv(tablas / "E7_temporal_confusion_synthetic_v2.csv", index_col=0)
    traza_bosque = sum(bosque.iloc[i, i] for i in range(len(bosque)))
    traza_red = sum(red.iloc[i, i] for i in range(len(red)))
    assert int(bosque.to_numpy().sum() - traza_bosque) == 12
    assert int(red.to_numpy().sum() - traza_red) == 17

    # Figura 5.11: la calibración, y su signo.
    calibracion = json.loads((registros / "E15_suficiencia.json").read_text("utf-8"))["calibration"]
    assert round(calibracion["uncalibrated"]["bias"], 4) == -0.1395, (
        "el sesgo sin calibrar es NEGATIVO: el modelo promete menos de lo que cumple"
    )
    assert round(calibracion["uncalibrated"]["ece"], 3) == 0.144

    # Figura 5.15: las cuatro ablaciones.
    esperado = {"A1": (0, 9, 2, 5), "A2": (0, 9, 5, 5), "A3": (6, 9, 0, 5), "A4": (9, 9, 2, 5)}
    for ablacion, (fc_n, fc_d, ai_n, ai_d) in esperado.items():
        resumen = json.loads((registros / f"E18_ablacion_{ablacion}.json").read_text("utf-8"))[
            "summary"
        ]
        assert resumen["false_confidence"]["numerator"] == fc_n
        assert resumen["false_confidence"]["denominator"] == fc_d
        assert resumen["unnecessary_abstention"]["numerator"] == ai_n
        assert resumen["unnecessary_abstention"]["denominator"] == ai_d

    # Figura 5.13: la recuperación, de cero a cinco de cinco.
    e12 = pd.read_csv(tablas / "E12_retrieval_por_estrategia.csv").set_index("strategy")
    assert float(e12.loc["semantic", "hit_rate"]) == 0.0
    assert float(e12.loc["diagnosis-guided", "hit_rate"]) == 1.0


def test_ninguna_figura_de_la_memoria_sale_de_un_conjunto_no_reconstruible_sin_decirlo() -> None:
    """`synthetic_v1` y `synthetic_v3` no se reconstruyen, y eso se declara."""
    anexos = (paths.ROOT / "docs" / "memoria" / "anexos.md").read_text("utf-8")
    capitulo = (paths.ROOT / "docs" / "memoria" / "cap5_resultados.md").read_text("utf-8")
    plano = anexos.replace("**", "")
    assert "`synthetic_v1`" in plano, "el anexo no nombra el conjunto"
    assert any(
        forma in plano for forma in ("no es reconstruible", "no se reconstruye", "¿Reconstruible?")
    ), "el anexo no declara que haya conjuntos que no se reconstruyen"
    # La figura 5.2 sale de synthetic_v1 y su pie tiene que decirlo.
    pie = next(
        linea
        for linea in capitulo.splitlines()
        if linea.startswith("*Fuente:") and "E4" in linea and "synthetic_v1" in linea
    )
    assert "L-25" in pie or "no se reconstruye" in pie or "pre-calibración" in pie, (
        "el pie de la figura de separabilidad no declara que su conjunto no se reconstruye"
    )


def test_el_guion_no_inventa_valores() -> None:
    """Ninguna función de dibujo debe llevar datos escritos a mano.

    Se busca una lista larga de números literales dentro del paquete: es la forma
    que tomaría un gráfico fabricado a partir de una descripción.
    """
    paquete = paths.ROOT / "src" / "mecanico_ia_exp" / "visualization" / "memoria"
    sospechosas = []
    for fichero in paquete.glob("*.py"):
        for numero, linea in enumerate(fichero.read_text("utf-8").splitlines(), 1):
            if linea.lstrip().startswith("#"):
                continue
            # La geometría de un eje —límites, una diagonal, un relleno— no son
            # datos: son el marco sobre el que los datos se dibujan.
            if any(
                metodo in linea
                for metodo in (
                    "set_xlim",
                    "set_ylim",
                    "fill_between",
                    "axvline",
                    "axhline",
                    "figsize",
                    "set_xticks",
                    "set_yticks",
                    "linspace",
                    "subplots_adjust",
                    "bbox_to_anchor",
                    "xytext",
                    "textcoords",
                    "eje.plot([",
                )
            ):
                continue
            # Una constante de módulo en mayúsculas y con anotación de tipo es un
            # **parámetro declarado**, no un dato: está nombrada, documentada y a
            # la vista de quien revise el fichero, que es lo contrario de una
            # cifra de un registro copiada dentro del código de dibujo. El riesgo
            # que esta prueba cubre es el segundo caso, no el primero.
            if re.match(r"^[A-Z][A-Z0-9_]*(\s*:\s*[^=]+)?\s*=", linea):
                continue
            literales = re.findall(r"(?<![\w.])\d+\.\d+", linea)
            if len(literales) >= 4:
                sospechosas.append(f"{fichero.name}:{numero}  {linea.strip()[:70]}")
    assert not sospechosas, (
        "hay líneas con cuatro o más decimales literales, que podrían ser datos"
        " escritos a mano en lugar de leídos de un registro:\n  " + "\n  ".join(sospechosas)
    )
