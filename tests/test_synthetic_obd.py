"""El generador sintético debe ser reproducible, plausible y honesto sobre lo que hace."""

from __future__ import annotations

import numpy as np
import pytest

from mecanico_ia_exp.obd.faults import FAULTS, NORMAL_ID
from mecanico_ia_exp.obd.signals import SIGNAL_NAMES, SIGNALS_BY_NAME, validate_ranges
from mecanico_ia_exp.obd.synthetic import (
    SessionSpec,
    build_balanced_specs,
    generate_dataset,
    generate_session,
)


def _sesion(fault_id: str = NORMAL_ID, seed: int = 7, duration_s: float = 300.0) -> SessionSpec:
    return SessionSpec(
        session_id=f"s_{fault_id}_{seed}",
        regime="urban",
        duration_s=duration_s,
        seed=seed,
        fault_id=fault_id,
    )


# ------------------------------------------------------------ reproducibilidad


def test_la_misma_semilla_produce_la_misma_serie() -> None:
    a = generate_session(_sesion(seed=123))
    b = generate_session(_sesion(seed=123))
    assert a.equals(b)


def test_semillas_distintas_producen_series_distintas() -> None:
    a = generate_session(_sesion(seed=1))
    b = generate_session(_sesion(seed=2))
    assert not a[list(SIGNAL_NAMES)].equals(b[list(SIGNAL_NAMES)])


# -------------------------------------------------------------- plausibilidad


def test_ninguna_senal_sale_de_su_rango_fisico() -> None:
    datos = generate_session(_sesion())
    for nombre in SIGNAL_NAMES:
        spec = SIGNALS_BY_NAME[nombre]
        assert datos[nombre].min() >= spec.minimum, nombre
        assert datos[nombre].max() <= spec.maximum, nombre


def test_validate_ranges_detecta_lo_imposible() -> None:
    assert validate_ranges({"rpm": 900.0}) == []
    assert validate_ranges({"rpm": 99_000.0}) == ["rpm"]


@pytest.mark.parametrize("fault_id", list(FAULTS))
def test_ningun_fallo_saca_una_senal_de_rango(fault_id: str) -> None:
    datos = generate_session(_sesion(fault_id=fault_id))
    for nombre in SIGNAL_NAMES:
        spec = SIGNALS_BY_NAME[nombre]
        assert datos[nombre].between(spec.minimum, spec.maximum).all(), nombre


# ------------------------------------------------- relaciones entre variables
# El generador no produce ruido independiente: si estas relaciones no se
# observan, no hay estructura que un modelo pueda aprender ni que la atribución
# pueda señalar, y el resto del experimento carecería de sentido.


@pytest.mark.parametrize("regime", ["urban", "highway", "acceleration"])
def test_el_caudal_de_aire_sigue_al_producto_regimen_por_carga(regime: str) -> None:
    """El caudal admitido depende de régimen Y carga conjuntamente, no de uno solo.

    Se comprueba la relación que el motor implementa realmente. La correlación
    marginal entre régimen y caudal es débil, y en autovía llega a ser negativa:
    a velocidad de crucero constante ambas señales apenas varían y domina el
    ruido. Eso no es un defecto del generador --un vehículo real se comporta
    igual-- sino un recordatorio de que una correlación marginal baja no implica
    ausencia de relación. La distinción importa al interpretar la atribución en
    E9: una señal puede ser determinante sin destacar en un diagrama de
    dispersión bivariante.

    El régimen de ralentí puro queda fuera de este test y tiene el suyo propio:
    allí el producto régimen x carga apenas varía --unas 5 veces entre su mínimo
    y su máximo, frente a las 100 o 150 de la conducción-- y el ruido del sensor
    domina. No es un defecto del modelo; un caudalímetro real en ralentí se
    comporta igual.
    """
    spec = SessionSpec(session_id="x", regime=regime, duration_s=600.0, seed=7, fault_id=NORMAL_ID)
    datos = generate_session(spec)
    producto = datos["rpm"].to_numpy() * datos["engine_load"].to_numpy()
    r = float(np.corrcoef(producto, datos["maf"])[0, 1])
    assert r > 0.85, f"{regime}: caudal desacoplado de régimen x carga: {r:.3f}"


def test_carga_y_presion_de_colector_estan_relacionadas() -> None:
    datos = generate_session(_sesion(duration_s=600.0))
    r = float(np.corrcoef(datos["engine_load"], datos["map"])[0, 1])
    assert r > 0.8, f"correlación carga-presión insuficiente: {r:.3f}"


def test_mariposa_y_carga_estan_relacionadas() -> None:
    datos = generate_session(_sesion(duration_s=600.0))
    r = float(np.corrcoef(datos["throttle_position"], datos["engine_load"])[0, 1])
    assert r > 0.8, f"correlación mariposa-carga insuficiente: {r:.3f}"


def test_velocidad_y_regimen_estan_relacionados() -> None:
    datos = generate_session(_sesion(duration_s=600.0))
    r = float(np.corrcoef(datos["vehicle_speed"], datos["rpm"])[0, 1])
    assert r > 0.5, f"correlación velocidad-régimen insuficiente: {r:.3f}"


def test_en_ralenti_el_caudal_esta_dominado_por_el_ruido_del_sensor() -> None:
    """En ralentí la relación existe pero es débil, y debe serlo.

    El caudal en ralentí ronda los 2,5 g/s que el manual documenta, con un ruido
    de sensor del orden del 14 %. Con tan poco recorrido, la correlación con el
    producto régimen x carga cae muy por debajo de la que se observa conduciendo.

    Se comprueba explícitamente en vez de excluirlo en silencio: es el mismo
    fenómeno que E4 y E5 encontraron una y otra vez --una relación real puede
    quedar enmascarada cuando el rango dinámico es pequeño-- y conviene tenerlo
    escrito antes de interpretar la atribución de E9.
    """
    spec = SessionSpec(session_id="x", regime="idle", duration_s=900.0, seed=5)
    datos = generate_session(spec)
    producto = datos["rpm"].to_numpy() * datos["engine_load"].to_numpy()
    r = float(np.corrcoef(producto, datos["maf"])[0, 1])
    assert 0.4 < r < 0.85, f"correlación en ralentí fuera de lo esperable: {r:.3f}"


def test_el_caudal_en_ralenti_coincide_con_la_especificacion_del_manual() -> None:
    """Manual: "Idle (after warm up): approx. 2.5 g/s" (srvc/B3E014018880W14.pdf).

    Es el anclaje inferior de la calibración del caudalímetro. Si se rompe, el
    generador ha dejado de corresponder al vehículo documentado.
    """
    for regime in ("idle", "urban", "acceleration"):
        spec = SessionSpec(session_id="x", regime=regime, duration_s=900.0, seed=5)
        datos = generate_session(spec)
        en_ralenti = datos.loc[datos["vehicle_speed"] < 2.0, "maf"]
        if en_ralenti.empty:
            continue
        assert 2.0 < float(en_ralenti.mean()) < 3.0, (
            f"{regime}: caudal en ralentí {en_ralenti.mean():.2f} g/s, "
            "fuera del entorno de los 2,5 g/s documentados"
        )


def test_el_regimen_de_ralenti_respeta_la_especificacion_del_manual() -> None:
    """Manual: 640-740 rpm para Z6 con transmisión manual (srvc/B3E011002000W01.pdf)."""
    spec = SessionSpec(session_id="x", regime="idle", duration_s=900.0, seed=5)
    datos = generate_session(spec)
    en_ralenti = datos.loc[datos["vehicle_speed"] < 2.0, "rpm"]
    assert float(en_ralenti.min()) > 620, f"ralentí demasiado bajo: {en_ralenti.min():.0f}"
    assert float(en_ralenti.max()) < 760, f"ralentí demasiado alto: {en_ralenti.max():.0f}"


def test_el_avance_de_encendido_en_ralenti_respeta_la_especificacion() -> None:
    """Manual: 9-11 BTDC° en ralentí (srvc/B3E011002000W01.pdf)."""
    spec = SessionSpec(session_id="x", regime="idle", duration_s=900.0, seed=5)
    datos = generate_session(spec)
    medio = float(datos.loc[datos["vehicle_speed"] < 2.0, "ignition_timing"].mean())
    assert 8.5 < medio < 11.5, f"avance en ralentí {medio:.1f} BTDC, fuera de 9-11"


def test_el_termostato_regula_en_el_rango_documentado() -> None:
    """Manual: apertura inicial 80-84 °C (srvc/B3E010002000T03.pdf).

    El valor anterior del generador, 88 °C, quedaba por encima del rango real.
    """
    spec = SessionSpec(
        session_id="x", regime="urban", duration_s=1800.0, seed=5, ambient_temp_c=20.0
    )
    datos = generate_session(spec)
    maximo = float(datos["coolant_temperature"].max())
    assert 80.0 <= maximo <= 86.0, f"regulación en {maximo:.1f} °C, fuera de 80-84"


def test_la_temperatura_sube_con_el_tiempo_en_arranque_frio() -> None:
    spec = SessionSpec(
        session_id="frio", regime="warmup", duration_s=600.0, seed=5, ambient_temp_c=15.0
    )
    datos = generate_session(spec)
    primeros = datos["coolant_temperature"].head(30).mean()
    ultimos = datos["coolant_temperature"].tail(30).mean()
    assert ultimos > primeros + 10.0, f"sin calentamiento: {primeros:.1f} -> {ultimos:.1f}"


# ------------------------------------------------------- verdad de referencia


def test_el_fallo_no_actua_antes_de_su_inicio() -> None:
    spec = SessionSpec(
        session_id="t",
        regime="urban",
        duration_s=400.0,
        seed=3,
        fault_id="F01_vacuum_leak",
        fault_onset_s=200.0,
    )
    datos = generate_session(spec)
    assert not datos.loc[datos["timestamp"] < 200.0, "fault_active"].any()
    assert datos.loc[datos["timestamp"] >= 200.0, "fault_active"].all()


def test_la_sesion_normal_no_tiene_ningun_instante_con_fallo_activo() -> None:
    datos = generate_session(_sesion())
    assert not datos["fault_active"].any()


@pytest.mark.parametrize("fault_id", list(FAULTS))
def test_cada_fallo_altera_alguna_de_las_senales_que_declara(fault_id: str) -> None:
    """La ficha del fallo declara qué señales toca. Si no las toca, la ficha
    miente, y toda explicación construida sobre ella sería falsa."""
    normal = generate_session(_sesion(fault_id=NORMAL_ID, seed=11, duration_s=400.0))
    con_fallo = generate_session(_sesion(fault_id=fault_id, seed=11, duration_s=400.0))
    declaradas = FAULTS[fault_id].affected_signals

    diferencias = [
        nombre
        for nombre in declaradas
        if not np.allclose(normal[nombre].to_numpy(), con_fallo[nombre].to_numpy())
    ]
    assert diferencias, f"{fault_id} no alteró ninguna de sus señales declaradas"


def test_el_termostato_bloqueado_impide_alcanzar_la_temperatura_de_regimen() -> None:
    spec = SessionSpec(
        session_id="term",
        regime="warmup",
        duration_s=900.0,
        seed=9,
        fault_id="F03_thermostat_stuck",
        ambient_temp_c=20.0,
    )
    datos = generate_session(spec)
    tope = FAULTS["F03_thermostat_stuck"].default_params["temp_cap_c"]
    assert datos["coolant_temperature"].max() < tope + 3.0


# ------------------------------------------------------------------- dataset


def test_el_dataset_registra_su_procedencia() -> None:
    specs = build_balanced_specs(seed=42, sessions_per_fault=1, duration_s=120.0)
    datos, metadata = generate_dataset(specs, dataset_id="d_test", seed=42)

    assert metadata.dataset_type == "synthetic"
    assert metadata.seed == 42
    assert metadata.n_sessions == len(specs)
    assert metadata.n_samples == len(datos)
    assert metadata.signals == SIGNAL_NAMES
    assert "mecanico_ia_exp.obd.synthetic" in metadata.source


def test_el_plan_equilibrado_cubre_todas_las_condiciones() -> None:
    specs = build_balanced_specs(seed=1, sessions_per_fault=3, duration_s=60.0)
    condiciones = {s.fault_id for s in specs}
    por_condicion = {f: sum(1 for s in specs if s.fault_id == f) for f in condiciones}
    assert set(por_condicion) == {NORMAL_ID, *FAULTS}
    assert set(por_condicion.values()) == {3}


def test_no_se_admiten_identificadores_de_sesion_repetidos() -> None:
    spec = _sesion(duration_s=60.0)
    with pytest.raises(ValueError, match="únicos"):
        generate_dataset([spec, spec], dataset_id="d", seed=1)


def test_se_rechaza_un_regimen_desconocido() -> None:
    with pytest.raises(ValueError, match="Régimen desconocido"):
        SessionSpec(session_id="x", regime="submarino", duration_s=10.0, seed=1)


def test_se_rechaza_un_fallo_desconocido() -> None:
    with pytest.raises(ValueError, match="Fallo desconocido"):
        SessionSpec(session_id="x", regime="urban", duration_s=10.0, seed=1, fault_id="F99")


def test_la_ficha_del_dataset_sobrevive_a_un_viaje_por_disco(tmp_path: object) -> None:
    from pathlib import Path

    from mecanico_ia_exp.data.metadata import DatasetMetadata

    specs = build_balanced_specs(seed=3, sessions_per_fault=1, duration_s=60.0)
    _, metadata = generate_dataset(specs, dataset_id="d_io", seed=3)
    destino = Path(str(tmp_path)) / "meta.json"
    metadata.write(destino)
    assert DatasetMetadata.read(destino).model_dump() == metadata.model_dump()
