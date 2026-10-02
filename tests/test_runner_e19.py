"""Contrato del ejecutor de E19, **sin abrir el conjunto de prueba**.

Ninguna prueba de este fichero lee la partición final. Todas trabajan con una
rejilla de ventanas construida aquí mismo, con los identificadores de sesión y
los tiempos que el conjunto real tiene, o con el conjunto elegible congelado, que
es configuración y no datos. Esa es la condición: el ejecutor tiene que quedar
auditado antes de que exista la primera cifra de prueba.

Reglas: `docs/methodology/congelacion-anotacion-e19.md`.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
import pandas as pd
import pytest
import yaml

from mecanico_ia_exp.config import paths
from mecanico_ia_exp.experiments.congelacion import (
    CongelacionInvalidaError,
    cargar_anclaje,
    cargar_manifiesto,
    casos_elegibles,
    exigir_dataset_congelado,
    exigir_espacio_congelado,
    exigir_politica_canonica,
    exigir_redactor_congelado,
    exigir_redactor_disponible,
    verificar,
)
from mecanico_ia_exp.experiments.final_runner import (
    ABSTIENE,
    ES_ENSAYO,
    ES_EVALUACION_FINAL,
    ESTRATO_PRIMARIO,
    ESTRATOS,
    EXPLICA,
    AnotacionIncoherenteError,
    AperturaNoDeclaradaError,
    CasoFinal,
    RedactorRequeridoError,
    RepeticionSinIdentificadorError,
    Ventana,
    casos_del_estrato,
    comparar_con_lo_declarado,
    comprobar_denominadores,
    condicion_del_artefacto,
    decision_esperada,
    denominadores,
    documento_anotacion,
    documento_incidencias,
    exigir_destinos_libres,
    orden_canonico,
    politicas_de_referencia,
    recuento,
    resumen_de_redaccion,
    run_final_evaluation,
    sufijo_de,
    tasas,
    trazabilidad,
    ventana_adversa,
    ventana_comparativa,
    ventanas_operativas,
)

CONDICIONES = (
    "F01_vacuum_leak",
    "F02_maf_drift",
    "F03_thermostat_stuck",
    "F04_o2_lag",
    "F05_misfire",
)


def rejilla(
    *,
    sesiones_por_condicion: int = 2,
    ventanas_por_sesion: int = 3,
    normales_al_inicio: int = 0,
) -> tuple[pd.DataFrame, npt.NDArray[np.str_]]:
    """Una rejilla con la forma del conjunto real, construida aquí.

    Dos sesiones por condición y tres ventanas por sesión, con paso de 60 s, que
    es la geometría del conjunto. Se construye **desordenada** a propósito: si el
    ejecutor dependiera del orden de las filas en lugar del orden canónico, las
    pruebas de selección pasarían por casualidad.

    `normales_al_inicio` reproduce lo que el conjunto real tiene y una rejilla
    ingenua no: en una sesión con avería, las primeras ventanas llevan etiqueta de
    funcionamiento normal, porque el fallo se inyecta tras un calentamiento.
    """
    filas = []
    etiquetas = []
    for condicion in CONDICIONES:
        for s in range(sesiones_por_condicion):
            for v in range(ventanas_por_sesion):
                filas.append(
                    {
                        "session_id": f"{condicion}__urban__{s:02d}",
                        "t_start": 60.0 * v,
                        "t_end": 60.0 * v + 120.0,
                    }
                )
                etiquetas.append("F00_normal" if v < normales_al_inicio else condicion)
    meta = pd.DataFrame(filas)
    y = np.asarray(etiquetas, dtype=np.str_)
    revuelto = np.random.default_rng(20260901).permutation(len(meta))
    return meta.iloc[revuelto].reset_index(drop=True), y[revuelto]


@pytest.fixture
def manifiesto() -> dict[str, Any]:
    return cargar_manifiesto()


@pytest.fixture
def casos_gold() -> dict[str, dict[str, Any]]:
    gold = yaml.safe_load((paths.CONFIGS / "goldset_mazda3_bk.yaml").read_text(encoding="utf-8"))
    return {str(c["case_id"]): c for c in gold["cases"]}


# --- Selección determinista de ventanas --------------------------------------


def test_el_orden_canonico_no_depende_del_orden_de_las_filas() -> None:
    meta, _ = rejilla()
    indices = list(range(len(meta)))
    ordenados = orden_canonico(meta, indices)
    claves = [(str(meta.iloc[i]["session_id"]), float(meta.iloc[i]["t_start"])) for i in ordenados]
    assert claves == sorted(claves)


def test_la_regla_primaria_toma_una_ventana_por_sesion_y_la_primera() -> None:
    """Una por sesión es lo que evita el solape: con ventana de 120 s y paso de
    60 s, dos ventanas consecutivas comparten la mitad de sus muestras."""
    meta, y = rejilla()
    ventanas = ventanas_operativas(meta, y, "F03_thermostat_stuck")

    assert len(ventanas) == 2
    assert len({v.session_id for v in ventanas}) == 2
    assert all(v.t_start == 0.0 for v in ventanas)
    assert [v.session_id for v in ventanas] == sorted(v.session_id for v in ventanas)


def test_la_regla_primaria_toma_la_primera_ventana_de_la_condicion_no_de_la_sesion() -> None:
    """El caso que una rejilla ingenua no cubre, y el conjunto real sí tiene.

    En una sesión con avería las dos primeras ventanas están etiquetadas como
    funcionamiento normal. Tomar «la primera de la sesión» daría una ventana sin el
    fallo, que no puede explicarse con la documentación de ese fallo.
    """
    meta, y = rejilla(ventanas_por_sesion=5, normales_al_inicio=2)
    ventanas = ventanas_operativas(meta, y, "F05_misfire")

    assert len(ventanas) == 2
    assert all(v.t_start == 120.0 for v in ventanas)
    assert all(y[v.indice] == "F05_misfire" for v in ventanas)


def test_la_regla_primaria_no_consulta_al_modelo() -> None:
    """El canal de oráculo `O-1` queda cerrado en el estrato que responde a la
    pregunta: la firma no recibe ni predicciones ni aciertos."""
    parametros = set(inspect.signature(ventanas_operativas).parameters)
    assert parametros == {"meta", "y", "fault_id"}


def test_el_estrato_comparativo_toma_la_primera_bien_clasificada() -> None:
    meta, y = rejilla()
    aciertos = np.zeros(len(meta), dtype=bool)
    # Un único acierto, y no es la primera ventana en orden canónico.
    objetivo = orden_canonico(meta, np.flatnonzero(y == "F04_o2_lag").tolist())[3]
    aciertos[objetivo] = True

    ventana = ventana_comparativa(meta, y, aciertos, "F04_o2_lag")
    assert ventana is not None
    assert ventana.indice == objetivo


def test_el_estrato_comparativo_no_inventa_ventana_si_el_modelo_falla_siempre() -> None:
    meta, y = rejilla()
    aciertos = np.zeros(len(meta), dtype=bool)
    assert ventana_comparativa(meta, y, aciertos, "F04_o2_lag") is None


def test_el_estrato_adverso_elige_el_error_mas_confiado() -> None:
    """Elegir el primero por índice escogía el error menos adverso: el que no
    supera la puerta de confianza y nunca llega al verificador."""
    meta, y = rejilla()
    aciertos = np.ones(len(meta), dtype=bool)
    confianzas = np.zeros(len(meta), dtype=np.float64)
    errores = orden_canonico(meta, np.flatnonzero(y == "F05_misfire").tolist())
    for i in errores:
        aciertos[i] = False
    confianzas[errores[2]] = 0.91
    confianzas[errores[0]] = 0.55

    ventana = ventana_adversa(meta, y, aciertos, confianzas, "F05_misfire")
    assert ventana is not None
    assert ventana.indice == errores[2]


def test_el_empate_en_el_estrato_adverso_lo_resuelve_el_orden_canonico() -> None:
    meta, y = rejilla()
    aciertos = np.ones(len(meta), dtype=bool)
    confianzas = np.zeros(len(meta), dtype=np.float64)
    errores = orden_canonico(meta, np.flatnonzero(y == "F01_vacuum_leak").tolist())
    for i in errores:
        aciertos[i] = False
        confianzas[i] = 0.88

    ventana = ventana_adversa(meta, y, aciertos, confianzas, "F01_vacuum_leak")
    assert ventana is not None
    assert ventana.indice == errores[0]


# --- La decisión esperada ----------------------------------------------------


def test_la_decision_esperada_solo_admite_las_tres_entradas_congeladas() -> None:
    """Si alguien añadiera aquí la cobertura, el veredicto o una comprobación de
    soporte, se estaría midiendo la política contra sí misma."""
    parametros = set(inspect.signature(decision_esperada).parameters)
    assert parametros == {"label", "predicted_class", "corpus_variant"}


@pytest.mark.parametrize(
    ("variante", "predicha", "esperada"),
    [
        ("FULL", "F01_vacuum_leak", EXPLICA),
        ("FULL", "F00_normal", ABSTIENE),
        ("PARTIAL", "F01_vacuum_leak", ABSTIENE),
        ("PARTIAL", "F00_normal", ABSTIENE),
        ("ABSENT", "F01_vacuum_leak", ABSTIENE),
    ],
)
def test_la_decision_esperada_exige_evidencia_admisible_y_diagnostico_correcto(
    variante: str, predicha: str, esperada: str
) -> None:
    assert (
        decision_esperada(
            label="F01_vacuum_leak", predicted_class=predicha, corpus_variant=variante
        )
        == esperada
    )


def test_con_diagnostico_incorrecto_no_hay_evidencia_admisible_que_citar() -> None:
    """Es lo que hace que el estrato adverso espere abstención incluso con
    evidencia completa en el índice: el manual documenta bien **otra** cosa."""
    assert (
        decision_esperada(
            label="F03_thermostat_stuck", predicted_class="F00_normal", corpus_variant="FULL"
        )
        == ABSTIENE
    )


# --- Generación de los casos -------------------------------------------------


def _casos(
    estrato: str,
    manifiesto: dict[str, Any],
    casos_gold: dict[str, dict[str, Any]],
    *,
    aciertos: npt.NDArray[np.bool_] | None = None,
    predicciones: npt.NDArray[np.str_] | None = None,
) -> tuple[list[CasoFinal], list[dict[str, str]]]:
    meta, y = rejilla()
    return casos_del_estrato(
        estrato,
        elegibles=casos_elegibles(manifiesto),
        casos_gold=casos_gold,
        meta=meta,
        y=y,
        predicciones=y if predicciones is None else predicciones,
        aciertos=np.ones(len(meta), dtype=bool) if aciertos is None else aciertos,
        confianzas=np.full(len(meta), 0.9, dtype=np.float64),
    )


def test_el_estrato_operativo_da_veintidos_ejecuciones_sobre_diez_sesiones(
    manifiesto: dict[str, Any], casos_gold: dict[str, dict[str, Any]]
) -> None:
    """Veintidós es aritmética: once condiciones de evidencia por las dos
    sesiones de prueba de cada fallo."""
    casos, no_evaluables = _casos("operativo", manifiesto, casos_gold)

    assert not no_evaluables
    assert recuento(casos) == {"n_runs": 22, "n_windows": 10, "n_sessions": 10}
    assert recuento(casos)["n_runs"] == manifiesto["eligible_cases"]["n"] * 2
    declarado = manifiesto["window_selection"]["primary_stratum"]
    assert recuento(casos)["n_runs"] == declarado["n_runs"]
    assert recuento(casos)["n_windows"] == declarado["n_windows"]
    assert recuento(casos)["n_sessions"] == declarado["n_sessions"]


def test_cada_ventana_del_estrato_operativo_lleva_las_condiciones_de_su_fallo(
    manifiesto: dict[str, Any], casos_gold: dict[str, dict[str, Any]]
) -> None:
    """Varias condiciones de evidencia sobre la **misma** ventana es el
    experimento central, y por eso la ejecución necesita identificador propio."""
    casos, _ = _casos("operativo", manifiesto, casos_gold)
    por_ventana: dict[str, set[str]] = {}
    for caso in casos:
        por_ventana.setdefault(caso.ventana.case_id, set()).add(caso.corpus_variant)

    assert len({c.ejecucion_id for c in casos}) == len(casos)
    con_tres = [v for v, variantes in por_ventana.items() if len(variantes) == 3]
    con_una = [v for v, variantes in por_ventana.items() if len(variantes) == 1]
    assert len(con_tres) == 6
    assert len(con_una) == 4


def test_el_estrato_adverso_solo_usa_las_condiciones_con_evidencia_completa(
    manifiesto: dict[str, Any], casos_gold: dict[str, dict[str, Any]]
) -> None:
    meta, _ = rejilla()
    aciertos = np.zeros(len(meta), dtype=bool)
    predicciones = np.full(len(meta), "F00_normal", dtype=np.str_)
    casos, _ = _casos(
        "adverso", manifiesto, casos_gold, aciertos=aciertos, predicciones=predicciones
    )

    assert {c.corpus_variant for c in casos} == {"FULL"}
    assert len(casos) == 5
    assert all(c.expected_decision == ABSTIENE for c in casos)


def test_un_caso_sin_ventana_se_declara_no_evaluable_y_no_se_sustituye(
    manifiesto: dict[str, Any], casos_gold: dict[str, dict[str, Any]]
) -> None:
    """La ausencia de ventanas es un hecho de la partición, no un error que haya
    que rodear eligiendo otra."""
    meta, _ = rejilla()
    casos, no_evaluables = _casos(
        "adverso", manifiesto, casos_gold, aciertos=np.ones(len(meta), dtype=bool)
    )

    assert not casos
    assert len(no_evaluables) == 5
    assert all("ausencia de ventanas" in n["reason"] for n in no_evaluables)


def test_ningun_caso_generado_es_de_la_condicion_con_distractor(
    manifiesto: dict[str, Any], casos_gold: dict[str, dict[str, Any]]
) -> None:
    casos, _ = _casos("operativo", manifiesto, casos_gold)
    assert not [c for c in casos if c.corpus_variant.startswith("DISTRACTOR")]


def test_un_estrato_desconocido_no_se_ejecuta(
    manifiesto: dict[str, Any], casos_gold: dict[str, dict[str, Any]]
) -> None:
    with pytest.raises(ValueError, match="estrato desconocido"):
        _casos("mejorado", manifiesto, casos_gold)


# --- Denominadores, tasas y unidades ----------------------------------------


def _caso(variante: str, sesion: str, t: float, esperada: str) -> CasoFinal:
    return CasoFinal(
        gold={"case_id": f"C_{variante}_{sesion}_{t:.0f}", "fault_id": "F01_vacuum_leak"},
        estrato="operativo",
        ventana=Ventana(indice=0, session_id=sesion, t_start=t),
        label="F01_vacuum_leak",
        predicted_class="F01_vacuum_leak" if esperada == EXPLICA else "F00_normal",
        expected_decision=esperada,
    )


def test_los_denominadores_distinguen_ejecuciones_ventanas_y_sesiones() -> None:
    casos = [
        _caso("FULL", "s1", 0.0, EXPLICA),
        _caso("FULL", "s2", 0.0, EXPLICA),
        _caso("PARTIAL", "s1", 0.0, ABSTIENE),
        _caso("ABSENT", "s1", 0.0, ABSTIENE),
    ]
    cuentas = denominadores(casos)

    assert cuentas["total"] == {"n_runs": 4, "n_windows": 2, "n_sessions": 2}
    assert cuentas["expected_explain"]["n_runs"] == 2
    assert cuentas["expected_abstain"] == {"n_runs": 2, "n_windows": 1, "n_sessions": 1}


def test_las_dos_tasas_tienen_denominadores_distintos_y_no_se_suman() -> None:
    pares = [
        (_caso("FULL", "s1", 0.0, EXPLICA), EXPLICA),
        (_caso("FULL", "s2", 0.0, EXPLICA), ABSTIENE),
        (_caso("PARTIAL", "s1", 0.0, ABSTIENE), EXPLICA),
        (_caso("ABSENT", "s3", 0.0, ABSTIENE), ABSTIENE),
    ]
    resultado = tasas(pares)

    assert resultado["false_confidence"]["numerator"] == 1
    assert resultado["false_confidence"]["denominator"] == 2
    assert resultado["unnecessary_abstention"]["numerator"] == 1
    assert resultado["unnecessary_abstention"]["denominator"] == 2
    assert "accuracy" not in resultado


def test_cada_tasa_viaja_con_sus_ventanas_y_sus_sesiones() -> None:
    """Tres ejecuciones de una sola sesión no son tres observaciones."""
    pares = [
        (_caso("FULL", "s1", 0.0, ABSTIENE), EXPLICA),
        (_caso("PARTIAL", "s1", 0.0, ABSTIENE), EXPLICA),
        (_caso("ABSENT", "s1", 0.0, ABSTIENE), ABSTIENE),
    ]
    tasa = tasas(pares)["false_confidence"]

    assert tasa["denominator"] == 3
    assert tasa["n_independent_windows"] == 1
    assert tasa["n_independent_sessions"] == 1
    assert tasa["rate"] == pytest.approx(2 / 3, abs=1e-4)


def test_una_tasa_sin_denominador_no_se_inventa() -> None:
    assert tasas([])["false_confidence"]["rate"] is None


def test_las_politicas_de_referencia_se_recalculan_sobre_las_mismas_ejecuciones() -> None:
    uno = _caso("FULL", "s1", 0.0, EXPLICA)
    dos = _caso("ABSENT", "s2", 0.0, ABSTIENE)
    pares = [(uno, EXPLICA), (dos, ABSTIENE)]
    confianzas = {uno.ejecucion_id: 0.95, dos.ejecucion_id: 0.95}

    referencia = politicas_de_referencia(pares, confianzas, min_confidence=0.79)

    siempre = referencia["abstain_always"]
    assert siempre["false_confidence"]["rate"] == 0.0
    assert siempre["unnecessary_abstention"]["rate"] == 1.0
    confia = referencia["explain_if_model_is_confident"]
    assert confia["false_confidence"]["rate"] == 1.0
    assert confia["unnecessary_abstention"]["rate"] == 0.0


# --- La anotación, sellada antes de medir ------------------------------------


def test_la_anotacion_lleva_los_denominadores_y_la_regla_congelada(
    manifiesto: dict[str, Any], casos_gold: dict[str, dict[str, Any]]
) -> None:
    casos, no_evaluables = _casos("operativo", manifiesto, casos_gold)
    documento = documento_anotacion(
        particion="validation",
        dataset_id="synthetic_v2",
        policy="v2.2",
        manifiesto=manifiesto,
        anclaje=cargar_anclaje(),
        verificacion=verificar().to_dict(),
        casos=casos,
        no_evaluables=no_evaluables,
    )

    assert documento["primary_stratum"] == ESTRATO_PRIMARIO
    assert set(documento["strata"]) == set(ESTRATOS)
    assert documento["strata"][ESTRATO_PRIMARIO]["answers_pi"] is True
    assert documento["strata"]["comparativo"]["answers_pi"] is False
    assert documento["strata"][ESTRATO_PRIMARIO]["denominators"]["total"]["n_runs"] == 22
    regla = documento["expected_decision_rule"]
    assert len(regla["allowed_inputs"]) == 3
    assert "veredicto del verificador de suficiencia" in regla["forbidden_inputs"]
    assert documento["frozen_rules"]["frozen_at_commit"]


def test_la_anotacion_no_filtra_ninguna_decision_del_sistema(
    manifiesto: dict[str, Any], casos_gold: dict[str, dict[str, Any]]
) -> None:
    """Lo que la anotación **no** puede contener: el documento se escribe antes de
    que el verificador haya visto un caso, y por tanto no puede llevar su
    veredicto, su cobertura ni sus comprobaciones de soporte."""
    casos, no_evaluables = _casos("operativo", manifiesto, casos_gold)
    documento = documento_anotacion(
        particion="validation",
        dataset_id="synthetic_v2",
        policy="v2.2",
        manifiesto=manifiesto,
        anclaje=cargar_anclaje(),
        verificacion=verificar().to_dict(),
        casos=casos,
        no_evaluables=no_evaluables,
    )
    texto = json.dumps(documento["strata"], ensure_ascii=False)

    for prohibido in (
        '"decision"',
        '"verdict"',
        '"sufficiency"',
        '"claim_coverage"',
        '"support_checks"',
        '"n_documents_applicable"',
    ):
        assert prohibido not in texto, f"la anotación no puede llevar {prohibido}"


# --- Fallo cerrado -----------------------------------------------------------


def test_sin_declaracion_de_apertura_la_particion_de_prueba_no_se_toca() -> None:
    """La comprobación va **antes** de cargar nada: el error se produce sin haber
    leído una sola ventana."""
    with pytest.raises(AperturaNoDeclaradaError, match="declaración formal de apertura"):
        run_final_evaluation(particion="test")
    with pytest.raises(AperturaNoDeclaradaError):
        run_final_evaluation(particion="test", open_test=True, reason="   ")


def test_los_artefactos_de_un_ensayo_no_pueden_pisar_los_de_la_evaluacion_final() -> None:
    assert sufijo_de("test") == ""
    assert sufijo_de("validation") == "_validation"


def test_si_los_denominadores_cambian_entre_anotar_y_medir_la_ejecucion_se_detiene(
    manifiesto: dict[str, Any], casos_gold: dict[str, dict[str, Any]]
) -> None:
    casos, no_evaluables = _casos("operativo", manifiesto, casos_gold)
    documento = documento_anotacion(
        particion="validation",
        dataset_id="synthetic_v2",
        policy="v2.2",
        manifiesto=manifiesto,
        anclaje=cargar_anclaje(),
        verificacion=verificar().to_dict(),
        casos=casos,
        no_evaluables=no_evaluables,
    )

    comprobar_denominadores(documento, casos, "operativo")
    with pytest.raises(AnotacionIncoherenteError, match="no son los anotados"):
        comprobar_denominadores(documento, casos[:-1], "operativo")


def test_una_huella_que_no_cuadra_detiene_la_ejecucion(tmp_path: Path) -> None:
    """La política es cerrada: sin anclaje verificable no se mide.

    Una ejecución de E19 que no pueda demostrar bajo qué reglas se midió no vale
    menos que otra, vale nada, y el momento de descubrirlo es antes de abrir el
    conjunto de prueba.
    """
    anclaje = cargar_anclaje()
    falso = dict(anclaje)
    falso["files"] = {ruta: "0" * 16 for ruta in anclaje["files"]}
    ruta = tmp_path / "anclaje.json"
    ruta.write_text(json.dumps(falso), encoding="utf-8")

    verificacion = verificar(ruta)
    assert not verificacion.ok
    with pytest.raises(CongelacionInvalidaError, match="no se puede verificar"):
        verificacion.exigir()


def test_un_anclaje_que_falta_no_se_da_por_bueno(tmp_path: Path) -> None:
    with pytest.raises(CongelacionInvalidaError, match="falta el fichero de anclaje"):
        cargar_anclaje(tmp_path / "no-existe.json")


def test_un_anclaje_incompleto_no_se_da_por_bueno(tmp_path: Path) -> None:
    ruta = tmp_path / "anclaje.json"
    ruta.write_text(json.dumps({"anchor_id": "E19"}), encoding="utf-8")
    with pytest.raises(CongelacionInvalidaError, match="frozen_at_commit"):
        cargar_anclaje(ruta)


def test_la_congelacion_vigente_se_verifica_entera() -> None:
    verificacion = verificar()
    assert verificacion.ok, str(verificacion)
    assert len(verificacion.comprobaciones) == 10


def test_los_recuentos_declarados_se_cotejan_y_una_discrepancia_no_se_absorbe(
    manifiesto: dict[str, Any], casos_gold: dict[str, dict[str, Any]]
) -> None:
    """Las cifras congeladas son una expectativa sobre la partición, no una regla
    del método: una discrepancia no detiene la ejecución, pero queda registrada."""
    casos, _ = _casos("operativo", manifiesto, casos_gold)
    cotejo = comparar_con_lo_declarado(manifiesto, casos)

    assert cotejo["matches"] is True
    assert cotejo["declared"] == {"n_runs": 22, "n_windows": 10, "n_sessions": 10}

    recortado = comparar_con_lo_declarado(manifiesto, casos[:-1])
    assert recortado["matches"] is False
    assert recortado["observed"]["n_runs"] == 21


def test_un_ensayo_dice_dentro_del_artefacto_que_no_es_un_resultado_de_e19() -> None:
    """El sufijo del nombre lo distingue, pero un registro se lee seis meses
    después sin mirar de dónde salió."""
    final = condicion_del_artefacto("test")
    ensayo = condicion_del_artefacto("validation")

    assert final["status"] == ES_EVALUACION_FINAL
    assert ensayo["status"] == ES_ENSAYO
    assert "NO es un resultado de E19" in ensayo["note"]


# --- Lo que el anclaje solo no puede ver -------------------------------------


def test_e19_no_mide_un_conjunto_que_no_este_congelado(manifiesto: dict[str, Any]) -> None:
    """Sin esto, pedir otro conjunto producía un artefacto que declaraba una
    congelación verificada sobre datos que nunca se congelaron."""
    assert exigir_dataset_congelado(manifiesto, "synthetic_v2") == "synthetic_v2"
    with pytest.raises(CongelacionInvalidaError, match="el conjunto congelado para E19"):
        exigir_dataset_congelado(manifiesto, "synthetic_v3")


def test_e19_no_admite_otra_politica_que_la_canonica(manifiesto: dict[str, Any]) -> None:
    """La verificación del anclaje solo comprueba que la política del manifiesto
    existe: un parámetro que permitiera otra versión escribiría un registro con la
    política equivocada bajo un anclaje correcto."""
    assert exigir_politica_canonica(manifiesto, "v2.2") == "v2.2"
    with pytest.raises(CongelacionInvalidaError, match="política canónica congelada"):
        exigir_politica_canonica(manifiesto, "v2.1")


def test_la_politica_no_es_un_parametro_del_ejecutor() -> None:
    parametros = set(inspect.signature(run_final_evaluation).parameters)
    assert "policy" not in parametros
    assert {"particion", "open_test", "reason", "estratos"} <= parametros


def test_el_arbol_sucio_detiene_la_evaluacion_final_y_solo_avisa_en_un_ensayo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """El manifiesto congela el código por su commit, y esa declaración no vale
    nada si hay cambios sin comitear: la ejecución usaría una recuperación o un
    verificador que ese commit no contiene."""
    from mecanico_ia_exp.experiments import congelacion

    monkeypatch.setattr(
        congelacion,
        "ficheros_con_seguimiento_modificados",
        lambda: ("src/mecanico_ia_exp/rag/store.py",),
    )
    assert congelacion.exigir_arbol_limpio(estricto=False) == ("src/mecanico_ia_exp/rag/store.py",)
    with pytest.raises(CongelacionInvalidaError, match="ficheros con seguimiento modificados"):
        congelacion.exigir_arbol_limpio(estricto=True)

    monkeypatch.setattr(congelacion, "ficheros_con_seguimiento_modificados", lambda: ())
    assert congelacion.exigir_arbol_limpio(estricto=True) == ()

    # Y la distinción que importa: «no se ha podido averiguar» no es «está limpio».
    monkeypatch.setattr(congelacion, "ficheros_con_seguimiento_modificados", lambda: None)
    with pytest.raises(CongelacionInvalidaError, match="no se ha podido averiguar"):
        congelacion.exigir_arbol_limpio(estricto=True)
    assert congelacion.exigir_arbol_limpio(estricto=False) == ()


# --- La redacción se guarda, no se pierde ------------------------------------


def test_el_resumen_de_redaccion_conserva_las_salidas_y_sus_recuentos() -> None:
    """La primera versión ejecutaba el redactor y tiraba su salida: las métricas
    que la congelación manda publicar no podían auditarse después."""

    class EjecucionFalsa:
        def __init__(self, *, valid: bool, respected: bool | None, falsas: int, esquema: bool):
            self.valid = valid
            self.respected_verdict = respected
            self.fake_citations = ["c1"] * falsas
            self.schema_error = esquema
            self.raw = None

        def to_dict(self) -> dict[str, Any]:
            return {"valid": self.valid, "schema_error": self.schema_error}

    def par(ejecucion: Any) -> tuple[CasoFinal, Any]:
        caso = _caso("FULL", "s1", 0.0, EXPLICA)
        verificado = type("V", (), {"agente": ejecucion})()
        return caso, verificado

    pares = [
        par(EjecucionFalsa(valid=True, respected=True, falsas=0, esquema=False)),
        par(EjecucionFalsa(valid=True, respected=False, falsas=2, esquema=False)),
        par(EjecucionFalsa(valid=False, respected=None, falsas=0, esquema=True)),
    ]
    resumen = resumen_de_redaccion(pares, llm="echo")

    assert resumen["summary"] == {
        "n_runs": 3,
        "valid_outputs": 2,
        "respected_verdict": 1,
        "n_evaluable_for_verdict": 2,
        "fake_citations": 2,
        "schema_errors": 1,
    }
    assert len(resumen["runs"]) == 3
    assert resumen["prompt_version"]


def test_la_evaluacion_final_no_se_mide_sin_redactor() -> None:
    """La sección 9 de las reglas congeladas no admite omitir ninguna de las
    métricas que enumera, y tres son de redacción. Sin redactor el artefacto
    quedaría incompleto declarándose completo."""
    with pytest.raises(RedactorRequeridoError, match="métricas de redacción"):
        run_final_evaluation(
            particion="test", open_test=True, reason="declaración de apertura de prueba"
        )


def test_un_ensayo_si_puede_medirse_sin_redactor() -> None:
    """La exigencia es de la evaluación final, no del ejecutor: un ensayo sobre
    validación no publica nada."""
    parametros = inspect.signature(run_final_evaluation).parameters
    assert parametros["llm"].default is None


def test_un_caso_que_no_termina_deja_su_traza_y_su_causa(tmp_path: Path) -> None:
    """Sin este artefacto, un fallo a mitad de la evaluación final dejaría la
    anotación sellada y ningún rastro de qué pasó después."""
    completado = _caso("FULL", "s1", 0.0, EXPLICA)
    documento = documento_incidencias(
        particion="test",
        dataset_id="synthetic_v2",
        policy="v2.2",
        ruta_anotacion=tmp_path / "E19_anotacion.json",
        huella_anotacion="0123456789abcdef",
        incidencias=[
            {
                "run_id": "C05_vacuum_leak@s2@0s",
                "stratum": "operativo",
                "cause": "OperationalError: la conexión se cerró",
                "traceback": "Traceback (most recent call last): ...",
            }
        ],
        completados=[completado],
    )

    assert documento["experiment_id"] == "E19_ejecucion_no_completada"
    assert documento["n_completed_before_failure"] == 1
    assert documento["completed_runs"] == [completado.ejecucion_id]
    assert documento["annotation"]["sha256_16"] == "0123456789abcdef"
    assert "secciones 8 y 11" in documento["validity_criterion"]
    incidencia = documento["incidents"][0]
    assert incidencia["cause"].startswith("OperationalError")
    assert incidencia["traceback"]


def test_una_repeticion_sobre_prueba_no_sustituye_a_la_anterior(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """La sección 11 es explícita: el registro de una ejecución inválida se
    conserva y la repetición es una versión nueva con su propio identificador.

    Con nombres fijos, repetir habría borrado la anotación sellada de la ejecución
    anterior y con ella la huella que la hacía auditable.
    """
    from mecanico_ia_exp.experiments import final_runner

    monkeypatch.setattr(final_runner.paths, "EXPERIMENTS", tmp_path)
    monkeypatch.setattr(final_runner.paths, "TABLES", tmp_path)

    assert exigir_destinos_libres("", intento="")
    (tmp_path / "E19_anotacion.json").write_text("{}", encoding="utf-8")
    with pytest.raises(RepeticionSinIdentificadorError, match="no permite sustituirlos"):
        exigir_destinos_libres("", intento="")

    # El identificador de la repetición despeja los destinos.
    assert exigir_destinos_libres(sufijo_de("test", "v2"), intento="v2")


def test_el_sufijo_distingue_la_particion_y_el_intento() -> None:
    assert sufijo_de("test") == ""
    assert sufijo_de("test", "v2") == "_v2"
    assert sufijo_de("validation") == "_validation"
    assert sufijo_de("validation", "v2") == "_validation_v2"


@pytest.mark.parametrize("estratos", [("comparativo",), ("operativo",), ("operativo", "adverso")])
def test_la_evaluacion_final_mide_los_tres_estratos_congelados(
    estratos: tuple[str, ...],
) -> None:
    """Ninguno de los tres es opcional. Sin el comparativo, una diferencia con las
    cifras de validación confundiría el efecto de la partición con el de haber
    cambiado la regla de selección; sin el adverso no se mide el escenario del
    diagnóstico incorrecto; y sin el operativo no se responde a la pregunta."""
    with pytest.raises(ValueError, match="mide los tres estratos congelados"):
        run_final_evaluation(
            particion="test",
            open_test=True,
            reason="declaración de apertura de prueba",
            estratos=estratos,
            llm="echo",
        )


def test_la_evaluacion_final_exige_el_redactor_congelado(manifiesto: dict[str, Any]) -> None:
    """Cualquier proveedor no vacío pasaba la comprobación de que hay redactor, de
    modo que un `echo` --que ni razona ni respeta el veredicto-- podía producir las
    métricas de redacción de la evaluación final."""
    congelado = manifiesto["controlled_state"]["writer"]["llm"]
    assert exigir_redactor_congelado(manifiesto, congelado) == congelado
    with pytest.raises(CongelacionInvalidaError, match="el redactor congelado para E19"):
        exigir_redactor_congelado(manifiesto, "echo")
    with pytest.raises(CongelacionInvalidaError):
        exigir_redactor_congelado(manifiesto, None)


def test_el_espacio_vectorial_incluye_el_dispositivo_y_se_comprueba(
    manifiesto: dict[str, Any],
) -> None:
    """En una máquina sin MPS el proveedor resuelve a CPU y produce vectores de otro
    espacio. La recuperación filtra por nombre de modelo, de modo que compararía
    espacios distintos sin avisar: es `MIXED-EMBEDDING-SPACE` otra vez."""
    congelado = manifiesto["controlled_state"]["embedding"]["space_id"]
    assert exigir_espacio_congelado(manifiesto, congelado, estricto=True) == congelado

    en_cpu = congelado.replace("[mps]", "[cpu]")
    with pytest.raises(CongelacionInvalidaError, match="espacio vectorial congelado"):
        exigir_espacio_congelado(manifiesto, en_cpu, estricto=True)
    # En un ensayo avisa y sigue: ahí no se publica nada.
    assert exigir_espacio_congelado(manifiesto, en_cpu, estricto=False) == en_cpu


def test_la_politica_de_referencia_usa_la_confianza_de_la_clase_predicha() -> None:
    """La calibración isotónica puede reordenar clases: con el máximo por ventana,
    la referencia explicaría casos que la puerta de confianza rechaza."""
    caso = _caso("FULL", "s1", 0.0, EXPLICA)
    pares = [(caso, ABSTIENE)]

    bajo = politicas_de_referencia(pares, {caso.ejecucion_id: 0.60}, min_confidence=0.79)[
        "explain_if_model_is_confident"
    ]
    alto = politicas_de_referencia(pares, {caso.ejecucion_id: 0.95}, min_confidence=0.79)[
        "explain_if_model_is_confident"
    ]

    assert bajo["unnecessary_abstention"]["numerator"] == 1
    assert alto["unnecessary_abstention"]["numerator"] == 0


def test_los_ficheros_del_conjunto_estan_anclados_por_huella(
    manifiesto: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Están fuera del control de versiones, de modo que la comprobación del árbol
    no puede verlos: sustituir uno dejando los recuentos declarados pasaba
    inadvertido y la evaluación final habría medido otros datos."""
    from mecanico_ia_exp.experiments import congelacion

    declarados = manifiesto["controlled_state"]["dataset"]["files"]
    assert set(declarados) == {
        "data/processed/synthetic_v2_x.npy",
        "data/processed/synthetic_v2_features.npy",
        "data/processed/synthetic_v2_meta.parquet",
        "data/processed/synthetic_v2_preprocess.json",
    }
    assert all(len(h) == 16 for h in declarados.values())

    comprobacion = congelacion._comprobar_ficheros_del_conjunto(manifiesto)
    assert comprobacion.ok

    falseado = json.loads(json.dumps(manifiesto))
    falseado["controlled_state"]["dataset"]["files"]["data/processed/synthetic_v2_meta.parquet"] = (
        "0" * 16
    )
    assert not congelacion._comprobar_ficheros_del_conjunto(falseado).ok


def test_el_redactor_se_construye_una_vez_por_ejecucion() -> None:
    """Crearlo por caso volvía a cargar el modelo base y a fundir el adaptador en
    cada uno, y en la evaluación final son treinta y ocho ejecuciones."""
    from mecanico_ia_exp.experiments import final_runner

    assert "redactor" in inspect.signature(final_runner.ejecutar_caso).parameters
    fuente = inspect.getsource(final_runner.ejecutar_caso)
    assert "get_llm" not in fuente, "el proveedor no puede construirse dentro del caso"


def test_el_indice_incompleto_detiene_la_evaluacion_final(manifiesto: dict[str, Any]) -> None:
    """Un índice incompleto no da error: da menos evidencia, y menos evidencia se
    cuenta como una abstención legítima. Sería el peor fallo posible de esta
    evaluación, porque confirmaría la hipótesis por la razón equivocada."""
    from mecanico_ia_exp.experiments.congelacion import exigir_corpus_congelado

    congelado = manifiesto["controlled_state"]["corpus"]
    completo = {
        "n_chunks": congelado["n_chunks"],
        "n_source_files": congelado["n_source_files"],
        "n_vectors_in_space": congelado["n_chunks"],
    }
    huella = congelado["content_fingerprint_16"]
    assert exigir_corpus_congelado(manifiesto, completo, estricto=True, fingerprint=huella)[
        "matches"
    ]

    incompleto = {**completo, "n_chunks": congelado["n_chunks"] - 7}
    with pytest.raises(CongelacionInvalidaError, match="corpus congelado completo"):
        exigir_corpus_congelado(manifiesto, incompleto, estricto=True)
    assert not exigir_corpus_congelado(manifiesto, incompleto, estricto=False)["matches"]

    sin_vectores = {**completo, "n_vectors_in_space": 0}
    with pytest.raises(CongelacionInvalidaError, match="vectores en el espacio declarado"):
        exigir_corpus_congelado(manifiesto, sin_vectores, estricto=True)


def test_un_corpus_sustituido_con_los_mismos_recuentos_tambien_detiene(
    manifiesto: dict[str, Any],
) -> None:
    """Cambiar el texto de un fragmento, o un código por el que la recuperación
    filtra, deja el número de filas igual y cambia lo que el sistema encuentra."""
    from mecanico_ia_exp.experiments.congelacion import exigir_corpus_congelado

    congelado = manifiesto["controlled_state"]["corpus"]
    completo = {
        "n_chunks": congelado["n_chunks"],
        "n_source_files": congelado["n_source_files"],
        "n_vectors_in_space": congelado["n_chunks"],
    }
    with pytest.raises(CongelacionInvalidaError, match="huella de contenido"):
        exigir_corpus_congelado(manifiesto, completo, estricto=True, fingerprint="0" * 16)
    assert not exigir_corpus_congelado(manifiesto, completo, estricto=False, fingerprint="0" * 16)[
        "matches"
    ]


def test_la_huella_del_indice_cubre_lo_que_decide_una_recuperacion() -> None:
    import inspect as inspeccion

    from mecanico_ia_exp.rag.store import PgVectorStore

    fuente = inspeccion.getsource(PgVectorStore.corpus_fingerprint)
    assert "row_to_json(c)" in fuente and "row_to_json(d)" in fuente, (
        "la huella cubre la fila completa del fragmento y la de su documento: elegir "
        "campos obliga a acertar la lista, y la lista crece"
    )
    assert "ORDER BY c.chunk_id" in fuente, "sin orden total la huella no es reproducible"


def test_el_identificador_de_ejecucion_distingue_los_estratos(
    manifiesto: dict[str, Any], casos_gold: dict[str, dict[str, Any]]
) -> None:
    """El estrato comparativo puede elegir la misma ventana que el operativo: sin
    el estrato en el identificador, dos ejecuciones distintas lo compartirían y los
    cruces entre la anotación, la tabla y el registro quedarían ambiguos."""
    meta, _ = rejilla()
    aciertos = np.ones(len(meta), dtype=bool)
    operativo, _ = _casos("operativo", manifiesto, casos_gold, aciertos=aciertos)
    comparativo, _ = _casos("comparativo", manifiesto, casos_gold, aciertos=aciertos)

    ventanas_compartidas = {c.ventana.case_id for c in operativo} & {
        c.ventana.case_id for c in comparativo
    }
    assert ventanas_compartidas, "el escenario del hallazgo tiene que darse aquí"
    todos = operativo + comparativo
    assert len({c.ejecucion_id for c in todos}) == len(todos)
    assert all(c.ejecucion_id.startswith(f"{c.estrato}:") for c in todos)


def test_la_trazabilidad_se_publica_agregada_y_con_su_denominador() -> None:
    """La sección 9 enumera las tres cuentas entre las métricas publicables, y
    dejar que el lector las derive de un JSON de miles de líneas es, para el caso,
    no publicarlas."""
    from mecanico_ia_exp.evidence.model import Claim, EvidenceBundle, SupportStatus

    def verificado(claims: list[Claim]) -> Any:
        bundle = EvidenceBundle(
            case_id="s1@0s",
            vehicle_id="mazda-3-bk-2007",
            predicted_class="F01_vacuum_leak",
            model_confidence=0.9,
            claims=claims,
        )
        return type("V", (), {"bundle": bundle})()

    pares = [
        (
            _caso("FULL", "s1", 0.0, EXPLICA),
            verificado(
                [
                    Claim(
                        claim_id="C01",
                        text="",
                        observation_ids=("O1",),
                        chunk_ids=("k1",),
                        support_status=SupportStatus.SUPPORTED,
                    ),
                    Claim(claim_id="C02", text="", observation_ids=("O2",)),
                ]
            ),
        ),
        (
            _caso("ABSENT", "s2", 0.0, ABSTIENE),
            verificado([Claim(claim_id="C03", text="", chunk_ids=("k2",))]),
        ),
    ]
    resultado = trazabilidad(pares)

    assert resultado["denominator_claims"] == 3
    assert resultado["with_observation"] == 2
    assert resultado["with_citation"] == 2
    assert resultado["with_support"] == 1
    assert resultado["rates"]["with_support"] == pytest.approx(1 / 3, abs=1e-4)
    assert resultado["n_runs"] == 2
    assert resultado["n_sessions"] == 2
    assert "propiedad del verificador" in resultado["note"]


def test_el_recuento_de_vectores_filtra_por_la_identidad_completa_del_espacio() -> None:
    """Filtrar por nombre de modelo dejaba pasar un índice con vectores producidos
    en CPU bajo el mismo nombre mientras la consulta se vectoriza en otro espacio:
    es la forma que tendría de reaparecer `MIXED-EMBEDDING-SPACE`."""
    import inspect as inspeccion

    from mecanico_ia_exp.rag.store import PgVectorStore

    firma = inspeccion.signature(PgVectorStore.corpus_counts).parameters
    assert "identidad" in firma
    assert "embedding_model" not in firma
    fuente = inspeccion.getsource(PgVectorStore.corpus_counts)
    for columna in (
        "embedding_provider",
        "embedding_model",
        "embedding_dimension",
        "embedding_version",
    ):
        assert columna in fuente, f"el recuento debe filtrar por {columna}"


def test_el_adaptador_que_falta_es_un_fallo_de_preparacion(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """La sección 8 lo clasifica así: se resuelve antes de ejecutar y no es un
    resultado. Descubrirlo después de sellar la anotación lo habría convertido en
    una ejecución no completada, y repetir habría exigido un intento nuevo."""
    from mecanico_ia_exp.experiments import congelacion

    assert exigir_redactor_disponible("echo") is None
    assert exigir_redactor_disponible("transformers-lora@slm_lora_v2") is not None

    monkeypatch.setattr(congelacion.paths, "ROOT", tmp_path)
    with pytest.raises(CongelacionInvalidaError, match="fallo de preparación"):
        congelacion.exigir_redactor_disponible("transformers-lora@slm_lora_v2")

    # Y la configuración sola no basta: los pesos se cargan en la primera
    # redacción, es decir después de sellar la anotación.
    directorio = tmp_path / "models" / "slm_lora_v2"
    directorio.mkdir(parents=True)
    (directorio / "adapter_config.json").write_text("{}", encoding="utf-8")
    with pytest.raises(CongelacionInvalidaError, match=r"adapter_model\.safetensors"):
        congelacion.exigir_redactor_disponible("transformers-lora@slm_lora_v2")

    (directorio / "adapter_model.safetensors").write_bytes(b"pesos")
    assert congelacion.exigir_redactor_disponible("transformers-lora@slm_lora_v2") == directorio


def test_los_pesos_del_adaptador_tienen_que_ser_los_congelados(
    manifiesto: dict[str, Any],
) -> None:
    """Están fuera del control de versiones, de modo que la comprobación del árbol
    no los ve: sustituirlos por otros válidos habría publicado las métricas de
    redacción de otro modelo bajo el nombre del congelado."""
    declarados = manifiesto["controlled_state"]["writer"]["files"]
    assert set(declarados) == {
        "models/slm_lora_v2/adapter_config.json",
        "models/slm_lora_v2/adapter_model.safetensors",
    }
    assert exigir_redactor_disponible("transformers-lora@slm_lora_v2", manifiesto) is not None

    falseado = json.loads(json.dumps(manifiesto))
    falseado["controlled_state"]["writer"]["files"][
        "models/slm_lora_v2/adapter_model.safetensors"
    ] = "0" * 16
    with pytest.raises(CongelacionInvalidaError, match="no son los congelados"):
        exigir_redactor_disponible("transformers-lora@slm_lora_v2", falseado)


def test_la_huella_del_indice_cubre_el_texto_y_la_autoridad() -> None:
    """La columna que resume el texto podría quedarse igual mientras el texto
    cambia, y la reordenación por autoridad manda sobre la similitud: cambiar el
    tipo de documento cambia qué evidencia llega al verificador."""
    import inspect as inspeccion

    from mecanico_ia_exp.rag.store import PgVectorStore

    fuente = inspeccion.getsource(PgVectorStore.corpus_fingerprint)
    assert "row_to_json" in fuente, "la fila entera cubre el texto, la sección y la autoridad"
    assert "c.content_hash" not in fuente, "la huella no puede fiarse de la columna resumen"
    assert "JOIN" in fuente, "el documento aporta el tipo y el nivel de autoridad"


def test_el_redactor_se_valida_antes_de_sellar_la_anotacion() -> None:
    """El orden importa: la anotación sellada es el referente de la ejecución, y
    sellarla para descubrir después que falta un fichero deja un rastro que habla
    de un fallo del sistema cuando era un fallo de preparación."""
    import inspect as inspeccion

    from mecanico_ia_exp.experiments import final_runner

    fuente = inspeccion.getsource(final_runner.run_final_evaluation)
    assert fuente.index("_redactor(llm,") < fuente.index("sellar_anotacion(")
    assert fuente.index("exigir_redactor_disponible(") < fuente.index("sellar_anotacion(")


def test_un_vector_sustituido_tambien_detiene(manifiesto: dict[str, Any]) -> None:
    """La búsqueda ordena por distancia al vector: sustituir uno cambia qué
    evidencia se recupera sin que ningún recuento ni la huella del contenido se
    muevan. Era la última pieza que decidía el resultado y no estaba cubierta."""
    from mecanico_ia_exp.experiments.congelacion import exigir_corpus_congelado

    congelado = manifiesto["controlled_state"]["corpus"]
    completo = {
        "n_chunks": congelado["n_chunks"],
        "n_source_files": congelado["n_source_files"],
        "n_vectors_in_space": congelado["n_chunks"],
    }
    vectores = manifiesto["controlled_state"]["embedding"]["vectors_fingerprint_16"]
    assert exigir_corpus_congelado(
        manifiesto,
        completo,
        estricto=True,
        fingerprint=congelado["content_fingerprint_16"],
        vectors_fingerprint=vectores,
    )["matches"]

    with pytest.raises(CongelacionInvalidaError, match="huella de los vectores"):
        exigir_corpus_congelado(
            manifiesto,
            completo,
            estricto=True,
            fingerprint=congelado["content_fingerprint_16"],
            vectors_fingerprint="0" * 16,
        )


def test_la_huella_de_los_vectores_los_lee_del_espacio_declarado() -> None:
    import inspect as inspeccion

    from mecanico_ia_exp.rag.store import PgVectorStore

    fuente = inspeccion.getsource(PgVectorStore.vectors_fingerprint)
    assert "e.vector::text" in fuente, (
        "el vector se lee como texto, no como lo materialice el driver"
    )
    for columna in ("embedding_provider", "embedding_dimension", "embedding_version"):
        assert columna in fuente, f"la huella debe acotarse al espacio por {columna}"
    assert "ORDER BY e.chunk_id" in fuente


def test_el_nombre_del_modelo_tiene_que_identificar_un_solo_espacio() -> None:
    """La búsqueda acota por nombre de modelo. Si dos espacios compartieran nombre,
    acotar por nombre dejaría de identificar uno y la ordenación volvería a mezclar
    vectores de espacios distintos: es `MIXED-EMBEDDING-SPACE`.

    Se comprueba en lugar de cambiar el filtro de la búsqueda: mientras el nombre
    identifique un único espacio, acotar por nombre y por identidad son la misma
    cosa, y las fases ya medidas no cambian de comportamiento.
    """
    from mecanico_ia_exp.experiments.congelacion import (
        exigir_espacio_identificado_por_su_nombre,
    )

    uno = (("sentence-transformers[mps]", 384, "1.0.0"),)
    assert exigir_espacio_identificado_por_su_nombre(uno, modelo="m", estricto=True) == uno

    dos = (*uno, ("sentence-transformers[cpu]", 384, "1.0.0"))
    with pytest.raises(CongelacionInvalidaError, match="identifica 2 espacios"):
        exigir_espacio_identificado_por_su_nombre(dos, modelo="m", estricto=True)
    assert exigir_espacio_identificado_por_su_nombre(dos, modelo="m", estricto=False) == dos

    with pytest.raises(CongelacionInvalidaError, match="identifica 0 espacios"):
        exigir_espacio_identificado_por_su_nombre((), modelo="m", estricto=True)


def test_las_revisiones_de_los_modelos_de_inferencia_estan_congeladas(
    manifiesto: dict[str, Any],
) -> None:
    """Era la última dependencia sin fijar: los dos modelos se cargan por nombre y
    sus pesos los administra una caché de terceros. Si cambiaran manteniendo el
    nombre, la evaluación ordenaría los vectores del índice con consultas de otro
    espacio, o atribuiría las métricas de redacción a otra base."""
    from mecanico_ia_exp.experiments.congelacion import (
        exigir_revisiones_congeladas,
        revision_en_cache,
    )

    embeddings = manifiesto["controlled_state"]["embedding"]
    redactor = manifiesto["controlled_state"]["writer"]
    assert len(embeddings["revision"]) == 40
    assert len(redactor["base_model_revision"]) == 40
    assert redactor["base_model"] == "Qwen/Qwen2.5-3B-Instruct"

    resultado = exigir_revisiones_congeladas(manifiesto, estricto=True)
    assert resultado["matches"]
    assert resultado["snapshot_available"][embeddings["model"]] is True

    falseado = json.loads(json.dumps(manifiesto))
    falseado["controlled_state"]["embedding"]["revision"] = "f" * 40
    with pytest.raises(CongelacionInvalidaError, match="no está descargada"):
        exigir_revisiones_congeladas(falseado, estricto=True)
    assert not exigir_revisiones_congeladas(falseado, estricto=False)["matches"]

    assert revision_en_cache("organizacion/modelo-que-no-existe") is None


def test_lo_que_decide_es_la_instantanea_fijada_y_no_la_rama_principal(
    manifiesto: dict[str, Any],
) -> None:
    """Los dos cargadores reciben la revisión congelada, de modo que una rama
    principal que haya avanzado es irrelevante mientras la instantánea siga ahí.
    Exigir que coincidieran habría bloqueado la evaluación final por un motivo
    falso."""
    from mecanico_ia_exp.experiments.congelacion import (
        exigir_revisiones_congeladas,
        instantanea_disponible,
    )

    embeddings = manifiesto["controlled_state"]["embedding"]
    assert instantanea_disponible(embeddings["model"], embeddings["revision"])
    assert not instantanea_disponible(embeddings["model"], "f" * 40)

    resultado = exigir_revisiones_congeladas(manifiesto, estricto=True)
    assert resultado["matches"]
    assert "main_ref_in_cache" in resultado, "la rama principal se registra, no decide"


def test_el_redactor_se_carga_antes_de_sellar_no_solo_se_construye() -> None:
    """Construirlo no basta: los proveedores cargan de forma diferida, y un modelo
    base incompleto fallaría en el primer caso, con la partición abierta y la
    anotación sellada, convirtiendo un fallo de preparación en una ejecución a
    medias."""
    import inspect as inspeccion

    from mecanico_ia_exp.experiments import final_runner
    from mecanico_ia_exp.llm.provider import EchoProvider, LLMProvider, TransformersProvider

    assert hasattr(LLMProvider, "warmup")
    EchoProvider().warmup()  # el proveedor sin estado no tiene qué cargar
    assert "self._cargar()" in inspeccion.getsource(TransformersProvider.warmup)

    fuente = inspeccion.getsource(final_runner.run_final_evaluation)
    assert fuente.index("redactor.warmup()") < fuente.index("sellar_anotacion(")


def test_los_dos_cargadores_reciben_la_revision_congelada() -> None:
    """Comprobar la caché antes de cargar no basta: si la rama principal avanza y
    la máquina tiene red, la misma orden resuelve otros pesos. La revisión se pasa
    al cargador, que es lo único que ata lo comprobado a lo ejecutado."""
    import inspect as inspeccion

    from mecanico_ia_exp.experiments import final_runner
    from mecanico_ia_exp.llm.provider import TransformersProvider
    from mecanico_ia_exp.rag.embeddings import SentenceTransformerProvider

    assert "revision" in inspeccion.signature(SentenceTransformerProvider.__init__).parameters
    assert "revision" in inspeccion.signature(TransformersProvider.__init__).parameters
    assert "revision" in inspeccion.signature(final_runner._redactor).parameters

    carga = inspeccion.getsource(SentenceTransformerProvider._cargar)
    assert "revision=self._revision" in carga

    fuente = inspeccion.getsource(final_runner.run_final_evaluation)
    assert '"revision": manifiesto["controlled_state"]["embedding"]["revision"]' in fuente
    assert "base_model_revision" in fuente


def test_sin_revision_el_comportamiento_es_el_de_las_fases_anteriores() -> None:
    """Las fases ya medidas cargaron por nombre, y eso no puede cambiar al preparar
    una evaluación final: la revisión es opcional y por omisión no interviene."""
    import inspect as inspeccion

    from mecanico_ia_exp.rag.embeddings import SentenceTransformerProvider

    assert (
        inspeccion.signature(SentenceTransformerProvider.__init__).parameters["revision"].default
        is None
    )
    carga = inspeccion.getsource(SentenceTransformerProvider._cargar)
    assert "if self._revision" in carga, "sin revisión se llama como antes"
