"""Las doce comprobaciones del generador, con conjuntos generados en el momento.

Ninguna toca `synthetic_v2`, `v3` ni ninguna partición reservada: lo que se
prueba es el instrumento, y para eso hace falta poder romperlo a propósito.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mecanico_ia_exp.obd.auditoria import (
    COMPROBACIONES,
    FALLA,
    INFORMATIVA,
    NO_VERIFICABLE,
    PASS,
    AuditoriaDelGeneradorError,
    auditar,
    exigir_auditoria_limpia,
)
from mecanico_ia_exp.obd.procedencia import construir
from mecanico_ia_exp.obd.signals import COLUMNAS_DE_EXPRESION
from mecanico_ia_exp.obd.synthetic import SessionSpec, build_balanced_specs, generate_dataset


@pytest.fixture(scope="module")
def conjunto() -> tuple[pd.DataFrame, dict]:
    """Un conjunto pequeño pero completo: las seis condiciones y los cuatro regímenes."""
    specs = [
        SessionSpec(
            session_id=s.session_id,
            regime=s.regime,
            duration_s=300.0,
            seed=s.seed,
            fault_id=s.fault_id,
            fault_onset_s=0.0 if s.fault_onset_s == 0.0 else 60.0,
            ambient_temp_c=s.ambient_temp_c,
        )
        for s in build_balanced_specs(seed=20260901, sessions_per_fault=4)
    ]
    datos, _ = generate_dataset(specs, dataset_id="auditoria_test", seed=20260901)
    manifiesto = construir(specs, datos, dataset_id="auditoria_test", seed=20260901)
    return datos, manifiesto


# --------------------------------------------------- el conjunto sano las pasa


def test_son_doce_comprobaciones() -> None:
    assert len(COMPROBACIONES) == 12


def test_un_conjunto_sano_no_bloquea(conjunto) -> None:
    datos, manifiesto = conjunto
    informe = exigir_auditoria_limpia(datos, manifiesto)
    assert len(informe) == 12
    assert {c.numero for c in informe} == set(range(1, 13))


def test_dos_comprobaciones_se_publican_sin_aprobarse(conjunto) -> None:
    """La expresión de los fallos y la variabilidad se miden, no se aprueban."""
    datos, manifiesto = conjunto
    informativas = {c.numero for c in auditar(datos, manifiesto) if c.estado == INFORMATIVA}
    assert informativas == {7, 8}


def test_el_ralenti_cae_en_el_rango_del_manual(conjunto) -> None:
    """La comprobación que habría detectado el problema de `synthetic_v3`."""
    datos, manifiesto = conjunto
    rangos = next(c for c in auditar(datos, manifiesto) if c.numero == 2)
    assert rangos.estado == PASS, rangos.detalle
    assert "640-740" in rangos.detalle


def test_la_expresion_se_informa_por_condicion(conjunto) -> None:
    datos, manifiesto = conjunto
    expresion = next(c for c in auditar(datos, manifiesto) if c.numero == 8)
    assert expresion.estado == INFORMATIVA
    for prefijo in ("F01", "F02", "F03", "F04", "F05"):
        assert prefijo in expresion.detalle


def test_el_fallo_de_encendido_se_expresa_poco(conjunto) -> None:
    """No es un defecto del conjunto: es el fenómeno, y conviene tenerlo delante."""
    datos, _ = conjunto
    activas = datos[datos["fault_active"] & (datos["fault_id"] == "F05_misfire")]
    fraccion = float(activas["fault_expressed"].mean())
    assert 0.0 < fraccion < 0.5, f"fracción expresada {fraccion:.0%}"


# ----------------------------------------- cada comprobación detecta su fallo


def test_detecta_un_valor_fuera_de_rango(conjunto) -> None:
    datos, manifiesto = conjunto
    roto = datos.copy()
    roto.loc[roto.index[0], "rpm"] = 99999.0
    fisica = next(c for c in auditar(roto, manifiesto) if c.numero == 1)
    assert fisica.estado == FALLA
    assert "rpm" in fisica.detalle


def test_detecta_un_ralenti_fuera_del_manual(conjunto) -> None:
    """Es exactamente el defecto de `synthetic_v3`: 820 rpm donde el manual dice 640-740."""
    datos, manifiesto = conjunto
    roto = datos.copy()
    sanas_paradas = (roto["fault_id"] == "F00_normal") & (roto["vehicle_speed"] < 2.0)
    roto.loc[sanas_paradas, "rpm"] = 820.0
    rangos = next(c for c in auditar(roto, manifiesto) if c.numero == 2)
    assert rangos.estado == FALLA
    assert "820" in rangos.detalle


def test_detecta_una_relacion_que_desaparece(conjunto) -> None:
    datos, manifiesto = conjunto
    roto = datos.copy()
    generador = np.random.default_rng(0)
    roto["maf"] = generador.uniform(0.0, 70.0, len(roto))
    relaciones = next(c for c in auditar(roto, manifiesto) if c.numero == 3)
    assert relaciones.estado == FALLA
    assert "rpm~maf" in relaciones.detalle


def test_detecta_un_salto_en_el_tiempo(conjunto) -> None:
    datos, manifiesto = conjunto
    roto = datos.copy()
    roto.loc[roto.index[5], "timestamp"] = 999.0
    continuidad = next(c for c in auditar(roto, manifiesto) if c.numero == 4)
    assert continuidad.estado == FALLA


def test_detecta_una_frecuencia_distinta_de_la_declarada(conjunto) -> None:
    datos, manifiesto = conjunto
    mentiroso = {**manifiesto, "sampling_rate_hz": 10.0}
    frecuencia = next(c for c in auditar(datos, mentiroso) if c.numero == 5)
    assert frecuencia.estado == FALLA
    assert "10.0" in frecuencia.detalle


def test_detecta_un_calentamiento_que_no_calienta(conjunto) -> None:
    datos, manifiesto = conjunto
    roto = datos.copy()
    calentamiento = (roto["fault_id"] == "F00_normal") & (roto["regime"] == "warmup")
    roto.loc[calentamiento, "coolant_temperature"] = 22.0
    evolucion = next(c for c in auditar(roto, manifiesto) if c.numero == 6)
    assert evolucion.estado == FALLA


def test_detecta_dos_sesiones_identicas() -> None:
    """Si la semilla por sesión no entrara, el conjunto tendría menos
    información de la que su número de sesiones sugiere.

    Se construye el caso en lugar de buscarlo: dos sesiones de la misma
    condición y el mismo régimen generadas con **la misma semilla**, que es
    exactamente lo que ocurriría si el constructor del plan no la sorteara.
    """
    specs = [
        SessionSpec(
            session_id=f"F00_normal__urban__{k:02d}",
            regime="urban",
            duration_s=120.0,
            seed=99,
            fault_id="F00_normal",
        )
        for k in range(2)
    ]
    datos, _ = generate_dataset(specs, dataset_id="semilla_repetida", seed=1)
    manifiesto = construir(specs, datos, dataset_id="semilla_repetida", seed=1)
    variabilidad = next(c for c in auditar(datos, manifiesto) if c.numero == 7)
    assert variabilidad.estado == FALLA
    assert "F00_normal/urban" in variabilidad.detalle


def test_sin_columnas_de_expresion_la_octava_no_se_verifica(conjunto) -> None:
    """Y no se salta: no verificable cuenta como fallo."""
    datos, manifiesto = conjunto
    antiguo = datos.drop(columns=list(COLUMNAS_DE_EXPRESION))
    expresion = next(c for c in auditar(antiguo, manifiesto) if c.numero == 8)
    assert expresion.estado == NO_VERIFICABLE
    with pytest.raises(AuditoriaDelGeneradorError, match="expresión"):
        exigir_auditoria_limpia(antiguo, manifiesto)


def test_detecta_una_muestra_sana_marcada_como_expresada(conjunto) -> None:
    datos, manifiesto = conjunto
    roto = datos.copy()
    sanas = roto.index[roto["fault_id"] == "F00_normal"][:1]
    roto.loc[sanas, "fault_expressed"] = True
    expresion = next(c for c in auditar(roto, manifiesto) if c.numero == 8)
    assert expresion.estado == FALLA
    assert "sanas" in expresion.detalle


def test_detecta_una_senal_delatora(conjunto) -> None:
    """Una señal que separe una condición con un solo umbral haría trivial el
    problema y convertiría la comparación en un artefacto del generador."""
    datos, manifiesto = conjunto
    roto = datos.copy()
    es_termostato = roto["fault_id"] == "F03_thermostat_stuck"
    roto.loc[es_termostato, "ignition_timing"] = 60.0
    roto.loc[~es_termostato, "ignition_timing"] = -60.0
    delator = next(c for c in auditar(roto, manifiesto) if c.numero == 9)
    assert delator.estado == FALLA
    assert "ignition_timing" in delator.detalle


def test_detecta_una_sesion_con_dos_condiciones(conjunto) -> None:
    datos, manifiesto = conjunto
    roto = datos.copy()
    primera = str(roto["session_id"].iloc[0])
    indices = roto.index[roto["session_id"] == primera][:10]
    roto.loc[indices, "fault_id"] = "F05_misfire"
    independencia = next(c for c in auditar(roto, manifiesto) if c.numero == 10)
    assert independencia.estado == FALLA


def test_detecta_una_sesion_sin_ficha(conjunto) -> None:
    datos, manifiesto = conjunto
    recortado = {**manifiesto, "sessions": manifiesto["sessions"][:-1]}
    procedencia = next(c for c in auditar(datos, recortado) if c.numero == 11)
    assert procedencia.estado == FALLA
    assert "sin ficha" in procedencia.detalle


def test_sin_manifiesto_tres_comprobaciones_no_se_verifican(conjunto) -> None:
    datos, _ = conjunto
    informe = auditar(datos, None)
    no_verificables = {c.numero for c in informe if c.estado == NO_VERIFICABLE}
    assert no_verificables == {5, 11, 12}
    with pytest.raises(AuditoriaDelGeneradorError):
        exigir_auditoria_limpia(datos, None)


def test_detecta_que_la_serie_no_se_regenera(conjunto) -> None:
    """La comprobación que da sentido al manifiesto."""
    datos, manifiesto = conjunto
    primera = sorted(str(f["session_id"]) for f in manifiesto["sessions"])[0]
    mentiroso = {
        **manifiesto,
        "sessions": [
            {**f, "seed": f["seed"] + 1} if f["session_id"] == primera else f
            for f in manifiesto["sessions"]
        ],
    }
    reproducibilidad = next(c for c in auditar(datos, mentiroso) if c.numero == 12)
    assert reproducibilidad.estado == FALLA
    assert "difiere" in reproducibilidad.detalle
