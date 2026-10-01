"""Contrato de la congelación de E19: las reglas no pueden moverse después.

Un documento que dice «congelado» no congela nada por decirlo. Estas pruebas lo
hacen cumplir: la huella del documento está en el manifiesto, y cualquier edición
posterior a la congelación rompe la suite en lugar de pasar inadvertida hasta que
alguien compare dos versiones a mano.

Reglas congeladas: `docs/methodology/congelacion-anotacion-e19.md`.
Estado congelado: `configs/manifest_e19.json`.
"""

from __future__ import annotations

import collections
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[1]
MANIFIESTO = RAIZ / "configs" / "manifest_e19.json"
ANCLAJE = RAIZ / "configs" / "congelacion-e19.anchor.json"
CONGELACION = RAIZ / "docs" / "methodology" / "congelacion-anotacion-e19.md"
GOLDSET = RAIZ / "configs" / "goldset_mazda3_bk.yaml"
PREPROCESADO = RAIZ / "data" / "processed" / "synthetic_v2_preprocess.json"


def huella(ruta: Path) -> str:
    """Las dieciséis primeras cifras del sha256, como en el manifiesto de RERUN-A."""
    return hashlib.sha256(ruta.read_bytes()).hexdigest()[:16]


@pytest.fixture(scope="module")
def manifiesto() -> dict[str, Any]:
    datos: dict[str, Any] = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    return datos


@pytest.fixture(scope="module")
def anclaje() -> dict[str, Any]:
    datos: dict[str, Any] = json.loads(ANCLAJE.read_text(encoding="utf-8"))
    return datos


@pytest.fixture(scope="module")
def casos_anotados() -> dict[str, dict[str, Any]]:
    gold = yaml.safe_load(GOLDSET.read_text(encoding="utf-8"))
    return {str(c["case_id"]): c for c in gold["cases"]}


# --- La congelación misma ----------------------------------------------------


def _git(*argumentos: str) -> subprocess.CompletedProcess[bytes]:
    """Ejecuta git sin interpretar el resultado."""
    try:
        return subprocess.run(
            ["git", "-C", str(RAIZ), *argumentos],
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:  # pragma: no cover - entorno sin git
        pytest.skip("git no está disponible: el anclaje de la congelación no se puede comprobar")


def exigir_historial(commit: str) -> None:
    """Se salta la prueba solo si **el entorno** no puede comprobar el anclaje.

    La distinción importa, y la primera versión de este fichero la pasaba por
    alto: cualquier fallo de git se saltaba la prueba, de modo que un commit mal
    escrito en el manifiesto dejaba la suite en verde sin haber comprobado nada.
    Hay exactamente dos situaciones que justifican saltarla --una copia sin
    historial y una clonación superficial que no alcanza al commit-- y cualquier
    otro fallo es un fallo.
    """
    if _git("rev-parse", "--verify", "HEAD").returncode != 0:  # pragma: no cover
        pytest.skip(
            "esta copia no tiene historial de git: el anclaje de la congelación "
            "no se puede comprobar aquí"
        )
    if _git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:  # pragma: no cover
        superficial = _git("rev-parse", "--is-shallow-repository").stdout.strip() == b"true"
        if superficial:
            pytest.skip(
                f"clonación superficial: el commit de congelación {commit} no está "
                "en esta copia y el anclaje no se puede comprobar aquí"
            )
        pytest.fail(
            f"el manifiesto declara el commit de congelación {commit} y este "
            "repositorio no lo contiene: o está mal escrito o el historial se "
            "reescribió sin actualizar el manifiesto"
        )


def git(*argumentos: str) -> str:
    """Salida de una orden de git que **tiene** que funcionar.

    Un fallo aquí no es una limitación del entorno --eso ya lo filtró
    `exigir_historial`-- sino que lo que el manifiesto declara no está donde dice.
    """
    resultado = _git(*argumentos)
    assert resultado.returncode == 0, (
        f"git {' '.join(argumentos)} falló con código {resultado.returncode}: "
        f"{resultado.stderr.decode('utf-8', errors='replace').strip()}"
    )
    return resultado.stdout.decode("utf-8", errors="replace")


def test_el_anclaje_cubre_las_reglas_y_el_estado_congelado(
    anclaje: dict[str, Any], manifiesto: dict[str, Any]
) -> None:
    """Anclar solo las reglas dejaría libre lo que de verdad fija las cifras.

    Un umbral, un caso elegible o una métrica publicable viven en el manifiesto.
    Si el anclaje no lo cubriera, podrían moverse después de abrir la partición
    sin que nada fallara, que es el hueco que la revisión del diff señaló.
    """
    anclados = set(anclaje["files"])
    assert anclados == {
        "docs/methodology/congelacion-anotacion-e19.md",
        "configs/manifest_e19.json",
    }
    assert manifiesto["anchor_file"] == "configs/congelacion-e19.anchor.json"
    assert manifiesto["frozen_rules"]["file"] in anclados


def test_las_huellas_de_los_ficheros_anclados_corresponden(anclaje: dict[str, Any]) -> None:
    """La comprobación rápida. Por sí sola no basta --quien editara el fichero y
    su huella a la vez la pasaría-- y por eso las dos siguientes van al commit."""
    for ruta, declarada in anclaje["files"].items():
        assert huella(RAIZ / ruta) == declarada, (
            f"{ruta} no corresponde a la huella declarada en el anclaje: "
            "una de las dos cosas se movió después de la congelación"
        )


def test_los_ficheros_anclados_son_los_del_commit_que_los_congelo(
    anclaje: dict[str, Any],
) -> None:
    """El anclaje de verdad: el contenido de un commit es inmutable.

    El fichero de anclaje se puede editar, y las huellas que declara también. Lo
    que no se puede editar es el objeto que el commit de congelación guarda.
    """
    commit = anclaje["frozen_at_commit"]
    exigir_historial(commit)
    for ruta in anclaje["files"]:
        congelado = git("cat-file", "blob", f"{commit}:{ruta}").encode("utf-8")
        assert hashlib.sha256(congelado).hexdigest()[:16] == huella(RAIZ / ruta), (
            f"{ruta} en el árbol de trabajo no es el que el commit {commit} "
            "congeló: o se editó después de congelarlo, y hay que decir por qué y "
            "volver a revisarlo, o el anclaje apunta a otro commit"
        )


def test_ningun_commit_posterior_toca_lo_congelado(anclaje: dict[str, Any]) -> None:
    """Una edición posterior tiene que verse, aunque deje el fichero equivalente.

    Esto no impide cambiar nada: impide que el cambio sea silencioso. Después de
    la congelación, cualquier cambio exige dos commits visibles, el que edita el
    fichero y el que mueve el anclaje.
    """
    commit = anclaje["frozen_at_commit"]
    exigir_historial(commit)
    for ruta in anclaje["files"]:
        posteriores = git("log", "--oneline", f"{commit}..HEAD", "--", ruta).strip()
        assert not posteriores, (
            f"hay commits posteriores a la congelación que tocan {ruta}:\n"
            f"{posteriores}\n"
            "la congelación solo vale si la revisión fue sobre el texto definitivo"
        )


def test_el_conjunto_anotado_no_ha_cambiado(manifiesto: dict[str, Any]) -> None:
    """Las consultas de E19 se reutilizan literalmente: si el fichero cambia,
    la reutilización deja de ser literal."""
    declarada = manifiesto["controlled_state"]["annotated_set"]["file_sha256_16"]
    assert huella(GOLDSET) == declarada


def test_el_manifiesto_apunta_a_ficheros_que_existen(manifiesto: dict[str, Any]) -> None:
    for ruta in (
        manifiesto["frozen_rules"]["file"],
        manifiesto["anchor_file"],
        manifiesto["controlled_state"]["annotated_set"]["file"],
    ):
        assert (RAIZ / ruta).is_file(), f"el manifiesto declara {ruta}, que no existe"


# --- El conjunto de prueba sigue cerrado -------------------------------------


def test_el_manifiesto_declara_el_conjunto_de_prueba_cerrado(manifiesto: dict[str, Any]) -> None:
    assert manifiesto["test_set"]["status"] == "CLOSED"
    assert manifiesto["test_set"]["opened"] is False


def test_el_cargador_sigue_impidiendo_leer_la_particion_de_prueba() -> None:
    """La congelación no abre nada. El cierre técnico sigue en su sitio."""
    from mecanico_ia_exp.data.dataset import LockedPartitionError, load_partition

    with pytest.raises(LockedPartitionError):
        load_partition("test")
    with pytest.raises(LockedPartitionError):
        load_partition("test", allow_test=True, reason="   ")


# --- La política canónica y los umbrales -------------------------------------


def test_la_politica_canonica_de_e19_es_v2_2_y_todavia_no_rige(
    manifiesto: dict[str, Any],
) -> None:
    """La transición entra **con** la evaluación final, no antes.

    El manifiesto declara v2.2 para E19 y el código mantiene v2.1 como canónica:
    las cifras ya publicadas se midieron con ella y no se reabren. Si alguien
    adelantara la transición cambiando `VERIFIER_VERSION`, las dos afirmaciones
    dejarían de ser compatibles y esta prueba lo diría.
    """
    from mecanico_ia_exp.abstention.sufficiency import POLITICAS, VERIFIER_VERSION

    politica = manifiesto["canonical_policy"]
    assert politica["verifier_version"] == "v2.2"
    assert politica["verifier_version"] in POLITICAS
    assert politica["published_results_stay_under"] == VERIFIER_VERSION == "v2.1"


def test_los_umbrales_congelados_son_los_del_codigo(manifiesto: dict[str, Any]) -> None:
    """Un umbral que se moviera entre la congelación y la ejecución invalidaría
    la evaluación sin dejar rastro en ningún resultado."""
    from mecanico_ia_exp.abstention.sufficiency import SufficiencyThresholds

    vigentes = SufficiencyThresholds().to_dict()
    congelados = manifiesto["thresholds"]
    for clave, valor in vigentes.items():
        assert congelados[clave] == valor, f"el umbral {clave} no es el congelado"


def test_la_semilla_y_el_conjunto_son_los_congelados(manifiesto: dict[str, Any]) -> None:
    from mecanico_ia_exp.models.baseline import BaselineConfig

    estado = manifiesto["controlled_state"]
    configuracion = BaselineConfig()
    assert estado["seed"] == configuracion.seed == 20260901
    assert estado["diagnosis_model"]["n_estimators"] == configuracion.n_estimators
    assert estado["diagnosis_model"]["min_samples_leaf"] == configuracion.min_samples_leaf
    assert estado["diagnosis_model"]["class_weight"] == configuracion.class_weight


# --- El conjunto elegible ----------------------------------------------------


def test_el_conjunto_elegible_son_once_casos(manifiesto: dict[str, Any]) -> None:
    elegibles = manifiesto["eligible_cases"]
    ids = [c for lista in elegibles["by_evidence_condition"].values() for c in lista]
    assert len(ids) == len(set(ids)) == elegibles["n"] == 11


def test_cada_caso_elegible_existe_y_tiene_la_condicion_declarada(
    manifiesto: dict[str, Any], casos_anotados: dict[str, dict[str, Any]]
) -> None:
    """La clasificación del manifiesto no se cree a sí misma: se comprueba contra
    el `corpus_variant` del conjunto anotado, que es quien la define."""
    for condicion, ids in manifiesto["eligible_cases"]["by_evidence_condition"].items():
        for case_id in ids:
            assert case_id in casos_anotados, f"{case_id} no está en el conjunto anotado"
            variante = str(casos_anotados[case_id].get("corpus_variant", "FULL"))
            assert variante == condicion, (
                f"{case_id} está declarado como {condicion} y el conjunto anotado dice {variante}"
            )


def test_ningun_caso_elegible_es_de_la_condicion_con_distractor(
    manifiesto: dict[str, Any], casos_anotados: dict[str, dict[str, Any]]
) -> None:
    """PI.4 no puede interpretarse con el diseño actual: medir el distractor sobre
    prueba produciría cifras que después habría que retirar."""
    elegibles = manifiesto["eligible_cases"]
    ids = {c for lista in elegibles["by_evidence_condition"].values() for c in lista}
    excluidos = set(elegibles["excluded"]["DISTRACTOR"]["cases"])

    assert not (ids & excluidos)
    for case_id in excluidos:
        assert case_id in casos_anotados
        variante = str(casos_anotados[case_id]["corpus_variant"])
        assert variante.startswith("DISTRACTOR"), (
            f"{case_id} está excluido como distractor y su variante es {variante}"
        )
    assert len(ids) + len(excluidos) == len(casos_anotados) == 17


def test_las_ejecuciones_declaradas_cuadran_con_los_casos_y_las_sesiones(
    manifiesto: dict[str, Any],
) -> None:
    """Veintidós ejecuciones es aritmética, no una estimación: once condiciones de
    evidencia por las dos sesiones de prueba de cada fallo."""
    primario = manifiesto["window_selection"]["primary_stratum"]
    n_casos = manifiesto["eligible_cases"]["n"]
    sesiones_por_condicion = 2
    assert primario["n_runs"] == n_casos * sesiones_por_condicion == 22
    assert primario["n_windows"] == primario["n_sessions"] == 10


# --- Las reglas de selección -------------------------------------------------


def test_solo_el_estrato_primario_responde_a_la_pregunta(manifiesto: dict[str, Any]) -> None:
    """Separar lo que responde a la PI de lo que solo describe es la mitad del
    valor de este documento: evita que un estrato comparativo acabe citado como
    resultado principal."""
    seleccion = manifiesto["window_selection"]
    assert seleccion["primary_stratum"]["answers_pi"] is True
    assert seleccion["primary_stratum"]["consults_model"] is False
    for nombre in ("comparative_stratum", "adverse_stratum"):
        assert seleccion[nombre]["answers_pi"] is False
        assert seleccion[nombre]["descriptive"] is True


def test_una_sola_ventana_por_sesion_para_que_no_haya_solape(
    manifiesto: dict[str, Any],
) -> None:
    """Con ventana de 120 s y paso de 60 s, dos ventanas consecutivas comparten la
    mitad de sus muestras. Una por sesión es lo que lo evita."""
    datos = manifiesto["controlled_state"]["dataset"]
    assert datos["window_stride_s"] * 2 == datos["window_length_s"]
    primario = manifiesto["window_selection"]["primary_stratum"]
    assert primario["n_windows"] == primario["n_sessions"]


# --- La no circularidad de la decisión esperada ------------------------------


def test_la_decision_esperada_solo_admite_tres_entradas(manifiesto: dict[str, Any]) -> None:
    esperada = manifiesto["expected_decision"]
    assert len(esperada["allowed_inputs"]) == 3
    assert not set(esperada["allowed_inputs"]) & set(esperada["forbidden_inputs"])


def test_ninguna_salida_del_verificador_puede_anotar_la_decision_esperada(
    manifiesto: dict[str, Any],
) -> None:
    """Si la anotación se derivara del veredicto, de la cobertura o de las cuatro
    comprobaciones de soporte, se estaría midiendo la política contra sí misma y
    el acuerdo sería una tautología.

    La prueba no puede impedir la circularidad --eso lo hace el procedimiento--
    pero sí que la lista de prohibiciones se quede corta frente a lo que el
    verificador devuelve de hecho.
    """
    from mecanico_ia_exp.abstention.sufficiency import SufficiencyVerdict

    prohibidas = " ".join(manifiesto["expected_decision"]["forbidden_inputs"]).lower()
    for pieza in ("veredicto", "motivos", "cobertura", "fragmentos", "fuentes", "soporte"):
        assert pieza in prohibidas, f"la lista de entradas prohibidas no menciona {pieza}"

    salidas = set(SufficiencyVerdict.__dataclass_fields__)
    assert {"sufficiency", "decision", "reasons", "signals"} <= salidas, (
        "el veredicto ya no devuelve lo que la lista de prohibiciones cubre: "
        "hay que revisar la lista"
    )


def test_la_anotacion_se_instancia_despues_de_abrir_y_antes_de_medir(
    manifiesto: dict[str, Any],
) -> None:
    orden = manifiesto["expected_decision"]["instantiation_order"]
    assert len(orden) == 4
    assert "abrir" in orden[0]
    assert "huella" in orden[2], "la anotación debe quedar con huella antes de medir"
    assert "suficiencia" in orden[3]


# --- Las dos tasas y las agregaciones ---------------------------------------


def test_las_dos_tasas_tienen_denominadores_distintos_y_no_se_agregan(
    manifiesto: dict[str, Any],
) -> None:
    tasas = manifiesto["error_rates"]
    assert tasas["T_FC"]["denominator"] != tasas["T_AI"]["denominator"]
    assert tasas["denominators_known_now"] is False
    for clave in ("T_FC", "T_AI"):
        assert tasas[clave]["reported_with"] == [
            "ejecuciones",
            "ventanas distintas",
            "sesiones distintas",
        ]


def test_las_agregaciones_prohibidas_cubren_las_medidas_repetidas(
    manifiesto: dict[str, Any],
) -> None:
    prohibidas = " ".join(manifiesto["forbidden_aggregations"]).lower()
    assert "comparten ventana" in prohibidas
    assert "independientes" in prohibidas
    assert not set(manifiesto["allowed_aggregations"]) & set(manifiesto["forbidden_aggregations"])


# --- El reparto declarado ----------------------------------------------------


def test_los_recuentos_de_sesiones_son_los_del_reparto_real(
    manifiesto: dict[str, Any],
) -> None:
    """Lo único que se leyó de la partición de prueba para congelar las reglas.

    Comprueba que lo declarado en el manifiesto es exactamente lo que el reparto
    dice, y que la prueba sigue teniendo dos sesiones por condición: si dejara de
    tenerlas, la regla primaria no daría diez ventanas y habría que reescribirla
    **antes** de abrir.
    """
    reparto = json.loads(PREPROCESADO.read_text(encoding="utf-8"))["split_assignment"]
    sesiones: collections.Counter[str] = collections.Counter(reparto.values())
    declarado = manifiesto["controlled_state"]["dataset"]["partitions"]
    for particion, cifras in declarado.items():
        assert sesiones[particion] == cifras["sessions"], (
            f"el reparto da {sesiones[particion]} sesiones en {particion} y el "
            f"manifiesto declara {cifras['sessions']}"
        )

    por_condicion = collections.Counter((p, s.split("__")[0]) for s, p in reparto.items())
    for condicion in (
        "F00_normal",
        "F01_vacuum_leak",
        "F02_maf_drift",
        "F03_thermostat_stuck",
        "F04_o2_lag",
        "F05_misfire",
    ):
        assert por_condicion[("test", condicion)] == 2


def test_el_total_de_ventanas_cuadra_con_el_manifiesto_de_preprocesado(
    manifiesto: dict[str, Any],
) -> None:
    """Las 98 ventanas de prueba se obtienen por resta, sin leer la partición."""
    preprocesado = json.loads(PREPROCESADO.read_text(encoding="utf-8"))
    datos = manifiesto["controlled_state"]["dataset"]
    particiones = datos["partitions"]

    assert datos["n_windows_total"] == preprocesado["n_windows"]
    assert sum(p["windows"] for p in particiones.values()) == preprocesado["n_windows"]
    assert particiones["test"]["windows"] == (
        preprocesado["n_windows"]
        - particiones["train"]["windows"]
        - particiones["validation"]["windows"]
    )
    assert datos["split_seed"] == preprocesado["split_seed"]
    assert datos["window_length_s"] == preprocesado["window_length_s"]
    assert datos["window_stride_s"] == preprocesado["window_stride_s"]
    assert datos["n_features"] == preprocesado["n_features"]


# --- La fuente de la clase predicha ------------------------------------------


def test_la_anotacion_usa_la_clase_que_usa_el_recorrido_evaluado(
    manifiesto: dict[str, Any],
) -> None:
    """El recorrido tiene una asimetría y la anotación tiene que respetarla.

    El diagnóstico con que se acota la recuperación y se verifica el soporte sale
    del bosque **sin calibrar**; la confianza que se compara con el umbral es la
    probabilidad **calibrada** de esa misma clase. La calibración isotónica puede
    reordenar clases, de modo que anotar la decisión esperada con el modelo
    calibrado declararía esperada una clase que el sistema no usa, y los
    denominadores de las dos tasas quedarían mal.

    La prueba lee el código: si alguien cambiara el modelo que produce la
    atribución o el que produce la confianza, la asimetría declarada dejaría de
    ser cierta y esto fallaría antes de que el error llegara a un resultado.
    """
    import inspect

    from mecanico_ia_exp.experiments import sufficiency_runner as runner

    atribucion = inspect.getsource(runner.atribucion_de)
    confianza = inspect.getsource(runner.confianza_calibrada_de)

    assert "ctx.modelo" in atribucion and "ctx.calibrado" not in atribucion, (
        "la atribución, que es de donde sale la clase predicha del recorrido, "
        "debe producirse con el bosque sin calibrar"
    )
    assert "ctx.calibrado" in confianza, (
        "la confianza comparada con el umbral debe ser la calibrada"
    )

    declarado = manifiesto["controlled_state"]["diagnosis_model"]["prediction_source"]
    assert "SIN calibrar" in declarado
    permitidas = " ".join(manifiesto["expected_decision"]["allowed_inputs"])
    assert "sin calibrar" in permitidas, (
        "las entradas permitidas de la decisión esperada deben nombrar la fuente "
        "de la clase predicha, no dejarla implícita"
    )


def test_el_acierto_que_selecciona_ventanas_es_el_del_mismo_modelo() -> None:
    """El estrato comparativo elige la primera ventana que el modelo clasifica
    bien. Si ese acierto se calculara con el modelo calibrado y la anotación con
    el otro, el estrato compararía dos cosas distintas."""
    import inspect

    from mecanico_ia_exp.experiments import sufficiency_runner as runner

    preparacion = inspect.getsource(runner.preparar)
    assert "predicciones = np.asarray(modelo.predict(" in preparacion, (
        "el vector de aciertos debe venir del mismo bosque sin calibrar que "
        "produce la clase predicha del recorrido"
    )
