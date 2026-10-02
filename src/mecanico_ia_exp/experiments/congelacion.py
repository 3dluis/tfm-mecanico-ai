"""Verificación de la congelación de E19, con **fallo cerrado**.

Las reglas y el estado de la evaluación final están congelados en dos ficheros
--`docs/methodology/congelacion-anotacion-e19.md` y `configs/manifest_e19.json`--
y anclados en el commit que los introdujo, declarado aparte en
`configs/congelacion-e19.anchor.json`.

Este módulo comprueba ese anclaje y lo hace **antes** de que el ejecutor toque
una partición. La política es cerrada por una razón concreta: una ejecución de
E19 que no pueda demostrar bajo qué reglas se midió no vale menos que otra, vale
nada, y el momento de descubrirlo es antes de abrir el conjunto de prueba, no al
escribir el informe.

Una comprobación que el entorno no puede realizar --una copia sin historial de
Git, una clonación superficial-- se marca `NO_VERIFICABLE` y **también** detiene
la ejecución. Quien ejecute la evaluación final en una copia así tendrá que
clonar el repositorio completo; lo que no puede es medir sin anclaje y enterarse
después.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from mecanico_ia_exp.config import paths

#: Fichero que declara el commit de congelación y las huellas de lo congelado.
RUTA_ANCLAJE = paths.CONFIGS / "congelacion-e19.anchor.json"

PASS = "PASS"
FALLA = "FALLA"
NO_VERIFICABLE = "NO_VERIFICABLE"

CONDICIONES = (
    "F00_normal",
    "F01_vacuum_leak",
    "F02_maf_drift",
    "F03_thermostat_stuck",
    "F04_o2_lag",
    "F05_misfire",
)


class CongelacionInvalidaError(RuntimeError):
    """La congelación no se puede verificar, y por tanto no se ejecuta nada."""


@dataclass(frozen=True)
class Comprobacion:
    """Una comprobación con su estado y el detalle que la justifica."""

    nombre: str
    estado: str
    detalle: str

    @property
    def ok(self) -> bool:
        return self.estado == PASS

    def to_dict(self) -> dict[str, Any]:
        return {"check": self.nombre, "status": self.estado, "detail": self.detalle}


@dataclass(frozen=True)
class Verificacion:
    """Resultado completo, para registrar entero y no solo su veredicto."""

    comprobaciones: tuple[Comprobacion, ...]

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.comprobaciones)

    @property
    def fallidas(self) -> tuple[Comprobacion, ...]:
        return tuple(c for c in self.comprobaciones if not c.ok)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": PASS if self.ok else FALLA,
            "checks": [c.to_dict() for c in self.comprobaciones],
        }

    def exigir(self) -> Verificacion:
        """Devuelve la verificación, o la convierte en excepción si algo falla."""
        if self.ok:
            return self
        detalle = "\n".join(f"  - {c.nombre} [{c.estado}]: {c.detalle}" for c in self.fallidas)
        msg = (
            "la congelación de E19 no se puede verificar y la ejecución se "
            f"detiene:\n{detalle}\n"
            "Ninguna medición sobre el conjunto de prueba es interpretable sin "
            "este anclaje."
        )
        raise CongelacionInvalidaError(msg)

    def __str__(self) -> str:
        return "\n".join(f"[{c.estado:<14}] {c.nombre}: {c.detalle}" for c in self.comprobaciones)


def huella(ruta: Path) -> str:
    """Las dieciséis primeras cifras del sha256, como en el manifiesto de RERUN-A."""
    return hashlib.sha256(ruta.read_bytes()).hexdigest()[:16]


def _git(*argumentos: str) -> subprocess.CompletedProcess[bytes] | None:
    """Ejecuta Git en la raíz del repositorio, o ``None`` si no está disponible."""
    try:
        return subprocess.run(
            ["git", "-C", str(paths.ROOT), *argumentos],
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def cargar_anclaje(ruta: Path = RUTA_ANCLAJE) -> dict[str, Any]:
    """Lee el fichero de anclaje, o falla diciendo qué falta."""
    if not ruta.is_file():
        msg = f"falta el fichero de anclaje de la congelación: {ruta}"
        raise CongelacionInvalidaError(msg)
    datos: dict[str, Any] = json.loads(ruta.read_text(encoding="utf-8"))
    for clave in ("frozen_at_commit", "files"):
        if clave not in datos:
            msg = f"el anclaje no declara {clave!r}"
            raise CongelacionInvalidaError(msg)
    return datos


def cargar_manifiesto(anclaje: dict[str, Any] | None = None) -> dict[str, Any]:
    """Lee el manifiesto que el anclaje cubre, no uno cualquiera con ese nombre."""
    datos_anclaje = anclaje or cargar_anclaje()
    candidatos = [r for r in datos_anclaje["files"] if r.endswith("manifest_e19.json")]
    if len(candidatos) != 1:
        msg = f"el anclaje debe cubrir un único manifiesto; cubre {candidatos}"
        raise CongelacionInvalidaError(msg)
    manifiesto: dict[str, Any] = json.loads(
        (paths.ROOT / candidatos[0]).read_text(encoding="utf-8")
    )
    return manifiesto


# ---------------------------------------------------------------------------
# Las comprobaciones, una función por cosa que puede haberse movido
# ---------------------------------------------------------------------------


def _comprobar_huellas(anclaje: dict[str, Any]) -> Comprobacion:
    problemas = []
    for ruta, declarada in anclaje["files"].items():
        fichero = paths.ROOT / ruta
        if not fichero.is_file():
            problemas.append(f"{ruta} no existe")
            continue
        actual = huella(fichero)
        if actual != declarada:
            problemas.append(f"{ruta}: huella {actual}, declarada {declarada}")
    if problemas:
        return Comprobacion("huellas_de_lo_congelado", FALLA, "; ".join(problemas))
    return Comprobacion(
        "huellas_de_lo_congelado",
        PASS,
        f"{len(anclaje['files'])} fichero(s) con la huella declarada",
    )


def _comprobar_commit(anclaje: dict[str, Any]) -> tuple[Comprobacion, Comprobacion]:
    """El anclaje de verdad, y la comprobación de que nada posterior lo toca.

    Se devuelven las dos juntas porque comparten el mismo trabajo previo: si el
    entorno no puede resolver el commit, ninguna de las dos es verificable y
    decirlo una sola vez sería menos claro en el registro.
    """
    commit = str(anclaje["frozen_at_commit"])
    cabeza = _git("rev-parse", "--verify", "HEAD")
    if cabeza is None or cabeza.returncode != 0:
        detalle = "esta copia no tiene historial de Git: el anclaje no se puede resolver"
        return (
            Comprobacion("objeto_del_commit_de_congelacion", NO_VERIFICABLE, detalle),
            Comprobacion("sin_commits_posteriores_a_la_congelacion", NO_VERIFICABLE, detalle),
        )

    existe = _git("cat-file", "-e", f"{commit}^{{commit}}")
    if existe is None or existe.returncode != 0:
        superficial = _git("rev-parse", "--is-shallow-repository")
        es_superficial = superficial is not None and superficial.stdout.strip() == b"true"
        detalle = f"el commit de congelación {commit} no está en esta copia" + (
            " (clonación superficial)" if es_superficial else ""
        )
        estado = NO_VERIFICABLE if es_superficial else FALLA
        return (
            Comprobacion("objeto_del_commit_de_congelacion", estado, detalle),
            Comprobacion("sin_commits_posteriores_a_la_congelacion", estado, detalle),
        )

    problemas: list[str] = []
    posteriores: list[str] = []
    for ruta in anclaje["files"]:
        objeto = _git("cat-file", "blob", f"{commit}:{ruta}")
        if objeto is None or objeto.returncode != 0:
            problemas.append(f"{ruta} no está en el commit {commit}")
            continue
        congelado = hashlib.sha256(objeto.stdout).hexdigest()[:16]
        actual = huella(paths.ROOT / ruta)
        if congelado != actual:
            problemas.append(f"{ruta}: el árbol de trabajo no es el del commit {commit}")
        registro = _git("log", "--oneline", f"{commit}..HEAD", "--", ruta)
        if registro is not None and registro.stdout.strip():
            posteriores.append(f"{ruta}: {registro.stdout.decode().strip().splitlines()[0]}")

    primera = (
        Comprobacion("objeto_del_commit_de_congelacion", FALLA, "; ".join(problemas))
        if problemas
        else Comprobacion(
            "objeto_del_commit_de_congelacion",
            PASS,
            f"lo congelado coincide con el objeto del commit {commit}",
        )
    )
    segunda = (
        Comprobacion(
            "sin_commits_posteriores_a_la_congelacion",
            FALLA,
            "hay commits posteriores que tocan lo congelado: " + "; ".join(posteriores),
        )
        if posteriores
        else Comprobacion(
            "sin_commits_posteriores_a_la_congelacion",
            PASS,
            f"ningún commit posterior a {commit} toca lo congelado",
        )
    )
    return primera, segunda


def _comprobar_politica(manifiesto: dict[str, Any]) -> Comprobacion:
    from mecanico_ia_exp.abstention.sufficiency import POLITICAS

    declarada = str(manifiesto["canonical_policy"]["verifier_version"])
    if declarada not in POLITICAS:
        return Comprobacion(
            "politica_canonica_declarada",
            FALLA,
            f"la política {declarada!r} no está entre las implementadas {POLITICAS}",
        )
    return Comprobacion(
        "politica_canonica_declarada", PASS, f"la evaluación final se mide con {declarada}"
    )


def _comprobar_umbrales(manifiesto: dict[str, Any]) -> Comprobacion:
    from mecanico_ia_exp.abstention.sufficiency import SufficiencyThresholds

    vigentes = SufficiencyThresholds().to_dict()
    congelados = manifiesto["thresholds"]
    diferencias = [
        f"{clave}: código {valor!r}, congelado {congelados.get(clave)!r}"
        for clave, valor in vigentes.items()
        if congelados.get(clave) != valor
    ]
    if diferencias:
        return Comprobacion("umbrales", FALLA, "; ".join(diferencias))
    return Comprobacion("umbrales", PASS, "los umbrales del código son los congelados")


def _comprobar_modelo(manifiesto: dict[str, Any]) -> Comprobacion:
    from mecanico_ia_exp.models.baseline import BaselineConfig

    configuracion = BaselineConfig()
    estado = manifiesto["controlled_state"]
    modelo = estado["diagnosis_model"]
    diferencias = []
    if estado["seed"] != configuracion.seed:
        diferencias.append(f"semilla: código {configuracion.seed}, congelada {estado['seed']}")
    for clave, valor in (
        ("n_estimators", configuracion.n_estimators),
        ("min_samples_leaf", configuracion.min_samples_leaf),
        ("class_weight", configuracion.class_weight),
    ):
        if modelo.get(clave) != valor:
            diferencias.append(f"{clave}: código {valor!r}, congelado {modelo.get(clave)!r}")
    if diferencias:
        return Comprobacion("semilla_y_modelo", FALLA, "; ".join(diferencias))
    return Comprobacion(
        "semilla_y_modelo", PASS, f"semilla {configuracion.seed} y bosque como el congelado"
    )


def _comprobar_conjunto_anotado(manifiesto: dict[str, Any]) -> Comprobacion:
    anotado = manifiesto["controlled_state"]["annotated_set"]
    fichero = paths.ROOT / anotado["file"]
    if not fichero.is_file():
        return Comprobacion("conjunto_anotado", FALLA, f"falta {anotado['file']}")
    actual = huella(fichero)
    if actual != anotado["file_sha256_16"]:
        return Comprobacion(
            "conjunto_anotado",
            FALLA,
            f"{anotado['file']}: huella {actual}, declarada {anotado['file_sha256_16']}",
        )
    return Comprobacion(
        "conjunto_anotado",
        PASS,
        f"{anotado['file']} con la huella declarada; consultas reutilizadas",
    )


def casos_elegibles(manifiesto: dict[str, Any]) -> dict[str, str]:
    """Identificador de caso elegible -> condición de evidencia congelada."""
    elegibles: dict[str, str] = {}
    for variante, ids in manifiesto["eligible_cases"]["by_evidence_condition"].items():
        for case_id in ids:
            elegibles[str(case_id)] = str(variante)
    return elegibles


def _comprobar_casos_elegibles(manifiesto: dict[str, Any]) -> Comprobacion:
    anotado = paths.ROOT / manifiesto["controlled_state"]["annotated_set"]["file"]
    gold = yaml.safe_load(anotado.read_text(encoding="utf-8"))
    por_id = {str(c["case_id"]): c for c in gold["cases"]}
    elegibles = casos_elegibles(manifiesto)

    problemas = []
    if len(elegibles) != int(manifiesto["eligible_cases"]["n"]):
        problemas.append(
            f"el manifiesto declara {manifiesto['eligible_cases']['n']} casos y enumera "
            f"{len(elegibles)}"
        )
    for case_id, variante in elegibles.items():
        caso = por_id.get(case_id)
        if caso is None:
            problemas.append(f"{case_id} no está en el conjunto anotado")
            continue
        real = str(caso.get("corpus_variant", "FULL"))
        if real != variante:
            problemas.append(f"{case_id}: declarado {variante}, anotado {real}")
        if real.startswith("DISTRACTOR"):
            problemas.append(f"{case_id} es de la condición con distractor y E19 la excluye")
    if problemas:
        return Comprobacion("casos_elegibles", FALLA, "; ".join(problemas))
    return Comprobacion(
        "casos_elegibles",
        PASS,
        f"{len(elegibles)} casos elegibles, con la condición de evidencia que el conjunto anota",
    )


def _comprobar_reparto(manifiesto: dict[str, Any]) -> Comprobacion:
    datos = manifiesto["controlled_state"]["dataset"]
    ruta = paths.DATA_PROCESSED / f"{datos['dataset_id']}_preprocess.json"
    if not ruta.is_file():
        return Comprobacion("reparto_declarado", FALLA, f"falta {ruta.name}")
    preprocesado = json.loads(ruta.read_text(encoding="utf-8"))
    reparto = preprocesado["split_assignment"]
    sesiones = Counter(reparto.values())

    problemas = []
    if preprocesado["split_seed"] != datos["split_seed"]:
        problemas.append("la semilla del reparto no es la congelada")
    if preprocesado["n_windows"] != datos["n_windows_total"]:
        problemas.append("el número total de ventanas no es el congelado")
    for particion, cifras in datos["partitions"].items():
        if sesiones[particion] != cifras["sessions"]:
            problemas.append(
                f"{particion}: {sesiones[particion]} sesiones, congeladas {cifras['sessions']}"
            )
    if sum(c["windows"] for c in datos["partitions"].values()) != preprocesado["n_windows"]:
        problemas.append("las ventanas por partición no suman el total")
    if problemas:
        return Comprobacion("reparto_declarado", FALLA, "; ".join(problemas))
    return Comprobacion(
        "reparto_declarado",
        PASS,
        "el reparto de sesiones es el congelado, sin leer ninguna ventana",
    )


def exigir_dataset_congelado(manifiesto: Mapping[str, Any], dataset_id: str) -> str:
    """El conjunto de datos tiene que ser el congelado, y no otro con ese nombre.

    Sin esta comprobación, pedir otro conjunto producía un artefacto que declaraba
    una congelación verificada --porque la verificación mira el manifiesto, que
    habla de `synthetic_v2`-- sobre datos que nunca se congelaron. El defecto lo
    encontró la revisión del diff antes de abrir nada.
    """
    congelado = str(manifiesto["controlled_state"]["dataset"]["dataset_id"])
    if dataset_id != congelado:
        msg = (
            f"el conjunto congelado para E19 es {congelado!r} y se ha pedido "
            f"{dataset_id!r}. La verificación de la congelación habla del primero: "
            "medir el segundo produciría un artefacto que declara una congelación "
            "que no le corresponde."
        )
        raise CongelacionInvalidaError(msg)
    return congelado


def exigir_politica_canonica(manifiesto: Mapping[str, Any], policy: str) -> str:
    """La política de E19 es la canónica del manifiesto, sin excepción.

    Un parámetro que permitiera medir con otra versión dejaría pasar la
    verificación --que solo comprueba que la del manifiesto existe-- y escribiría
    un registro con la política equivocada bajo un anclaje correcto.
    """
    canonica = str(manifiesto["canonical_policy"]["verifier_version"])
    if policy != canonica:
        msg = (
            f"E19 se mide con la política canónica congelada, {canonica!r}, y se ha "
            f"pedido {policy!r}. Para medir con otra versión está el ejecutor de "
            "suficiencia, cuyos artefactos llevan sufijo."
        )
        raise CongelacionInvalidaError(msg)
    return canonica


def exigir_redactor_congelado(manifiesto: Mapping[str, Any], llm: str | None) -> str:
    """El redactor de la evaluación final es el congelado, y no otro cualquiera.

    Cualquier proveedor no vacío pasaba la comprobación de que hay redactor, de
    modo que un `echo` --que ni razona ni respeta el veredicto-- podía producir las
    métricas de redacción de un artefacto marcado como evaluación final.
    """
    congelado = str(manifiesto["controlled_state"]["writer"]["llm"])
    if llm != congelado:
        msg = (
            f"el redactor congelado para E19 es {congelado!r} y se ha pedido {llm!r}. "
            "Las métricas de redacción de la evaluación final describen ese adaptador "
            "con ese prompt, no otro proveedor."
        )
        raise CongelacionInvalidaError(msg)
    return congelado


def exigir_espacio_congelado(
    manifiesto: Mapping[str, Any], space_id: str, *, estricto: bool
) -> str:
    """El espacio vectorial de la consulta tiene que ser el del índice.

    La identidad del proveedor incluye el **dispositivo**, y con razón: en una
    máquina sin MPS el proveedor resuelve a CPU y produce vectores de otro espacio.
    La recuperación filtra por nombre de modelo, de modo que compararía vectores de
    consulta de un espacio con vectores indexados de otro y devolvería resultados
    sin avisar. Es el mismo defecto que `MIXED-EMBEDDING-SPACE`, que ya obligó a
    repetir una fase entera.
    """
    congelado = str(manifiesto["controlled_state"]["embedding"]["space_id"])
    if space_id == congelado:
        return congelado
    msg = (
        f"el espacio vectorial congelado es {congelado!r} y el proveedor resuelve a "
        f"{space_id!r}. La identidad incluye el dispositivo: medir asi compararia "
        "vectores de consulta de un espacio con vectores indexados de otro."
    )
    if estricto:
        raise CongelacionInvalidaError(msg)
    print(f"AVISO: {msg} En un ensayo se admite; en la evaluación final detendría.")
    return space_id


def _carpeta_en_cache(modelo: str) -> Path | None:
    try:
        from huggingface_hub import constants
    except ImportError:  # pragma: no cover - entorno sin la biblioteca
        return None
    return Path(constants.HF_HUB_CACHE) / f"models--{modelo.replace('/', '--')}"


def revision_en_cache(modelo: str) -> str | None:
    """Revisión a la que apunta la rama principal en la caché local.

    Es **informativa**: la rama principal se mueve, y lo que la ejecución carga es
    la revisión que se le pasa al cargador. Se registra para poder decir, si alguna
    vez hiciera falta, qué había en la máquina el día de la medición.
    """
    carpeta = _carpeta_en_cache(modelo)
    if carpeta is None:
        return None
    referencia = carpeta / "refs" / "main"
    if referencia.is_file():
        return referencia.read_text(encoding="utf-8").strip() or None
    instantaneas = carpeta / "snapshots"
    if instantaneas.is_dir():
        disponibles = sorted(d.name for d in instantaneas.iterdir() if d.is_dir())
        if len(disponibles) == 1:
            return disponibles[0]
    return None


def instantanea_disponible(modelo: str, revision: str) -> bool:
    """Si la revisión **congelada** está descargada en la caché local.

    Es lo que hay que comprobar, y no que la rama principal coincida con ella: los
    dos cargadores reciben la revisión congelada, de modo que una rama principal que
    haya avanzado es irrelevante mientras la instantánea fijada siga ahí. Exigir que
    coincidieran habría bloqueado la evaluación final por un motivo falso.

    No se descarga nada ni se consulta la red: se mira lo que hay.
    """
    carpeta = _carpeta_en_cache(modelo)
    if carpeta is None:
        return False
    instantanea = carpeta / "snapshots" / revision
    return instantanea.is_dir() and any(instantanea.iterdir())


def exigir_revisiones_congeladas(
    manifiesto: Mapping[str, Any], *, estricto: bool
) -> dict[str, Any]:
    """Las revisiones congeladas de los dos modelos tienen que estar descargadas.

    Es la última dependencia que quedaba sin fijar, y la que menos se ve: el
    código está anclado por su commit, el índice y el adaptador por sus huellas, y
    los pesos que descarga una biblioteca de terceros no estaban en ninguna parte.

    Lo que se comprueba es que **la instantánea fijada** está en la caché, no que la
    rama principal coincida con ella: los dos cargadores reciben la revisión
    congelada, de modo que una rama principal que haya avanzado es irrelevante.
    """
    estado = manifiesto["controlled_state"]
    declaradas = {
        estado["embedding"]["model"]: estado["embedding"].get("revision"),
        estado["writer"]["base_model"]: estado["writer"].get("base_model_revision"),
    }
    disponibles = {
        modelo: (instantanea_disponible(modelo, esperada) if esperada else None)
        for modelo, esperada in declaradas.items()
    }
    diferencias = [
        f"{modelo}: la revisión congelada {esperada} no está descargada"
        for modelo, esperada in declaradas.items()
        if esperada and not disponibles[modelo]
    ]
    resultado = {
        "declared": declaradas,
        "snapshot_available": disponibles,
        # La rama principal se registra pero no decide: lo que se carga es la
        # revisión congelada, que se le pasa al cargador.
        "main_ref_in_cache": {modelo: revision_en_cache(modelo) for modelo in declaradas},
        "matches": not diferencias,
    }
    if not diferencias:
        return resultado
    msg = (
        "faltan en la caché local las revisiones congeladas de los modelos de "
        "inferencia: " + "; ".join(diferencias) + ". Es un fallo de preparación: se "
        "descargan antes de ejecutar."
    )
    if estricto:
        raise CongelacionInvalidaError(msg)
    print(f"AVISO: {msg} En un ensayo se admite; en la evaluación final detendría.")
    return resultado


def exigir_redactor_disponible(
    llm: str, manifiesto: Mapping[str, Any] | None = None
) -> Path | None:
    """El adaptador del redactor, presente y **el congelado**, antes de sellar.

    La sección 8 clasifica un artefacto de entrada ausente como fallo de
    preparación, que se resuelve antes de ejecutar y no es un resultado. Si se
    descubriera después de sellar, el fallo quedaría registrado como una ejecución
    no completada y repetir exigiría un identificador de intento nuevo, cuando lo
    único que pasaba era que faltaba un fichero.

    Con `manifiesto` se comprueba además la **huella de los pesos**. Están fuera del
    control de versiones, de modo que la comprobación del árbol no los ve:
    sustituirlos por otros válidos publicaría las métricas de redacción de otro
    modelo bajo el nombre del congelado.
    """
    from mecanico_ia_exp.llm.provider import adapter_dir_from_name

    relativo = adapter_dir_from_name(llm)
    if relativo is None:
        return None
    directorio = paths.ROOT / relativo
    if not directorio.is_dir():
        msg = (
            f"el redactor {llm!r} necesita el adaptador de {relativo} y ahí no hay "
            "directorio. Es un fallo de preparación: se resuelve antes de ejecutar."
        )
        raise CongelacionInvalidaError(msg)

    faltan = []
    for nombre in ("adapter_config.json", "adapter_model.safetensors"):
        fichero = directorio / nombre
        if not fichero.is_file() or fichero.stat().st_size == 0:
            faltan.append(nombre)
            continue
        try:  # legible, no solo presente
            with fichero.open("rb") as abierto:
                abierto.read(1)
        except OSError:  # pragma: no cover - permisos o fichero corrupto
            faltan.append(f"{nombre} (ilegible)")
    if faltan:
        msg = (
            f"el adaptador de {relativo} está incompleto: falta o no se puede leer "
            f"{', '.join(faltan)}. La configuración sola no basta --los pesos se cargan "
            "en la primera redacción, es decir después de sellar la anotación-- y la "
            "sección 8 clasifica esto como fallo de preparación, no como resultado."
        )
        raise CongelacionInvalidaError(msg)

    if manifiesto is not None:
        declarados = manifiesto["controlled_state"]["writer"].get("files") or {}
        distintos = []
        for ruta, declarada in declarados.items():
            fichero = paths.ROOT / ruta
            if not fichero.is_file():
                distintos.append(f"{ruta} no existe")
                continue
            actual = huella(fichero)
            if actual != declarada:
                distintos.append(f"{ruta}: huella {actual}, declarada {declarada}")
        if distintos:
            msg = (
                "los pesos del redactor no son los congelados: "
                + "; ".join(distintos)
                + ". Las métricas de redacción describirían otro modelo bajo el nombre "
                "del congelado."
            )
            raise CongelacionInvalidaError(msg)
    return directorio


def exigir_corpus_congelado(
    manifiesto: Mapping[str, Any],
    recuentos: Mapping[str, int],
    *,
    estricto: bool,
    fingerprint: str | None = None,
    vectors_fingerprint: str | None = None,
) -> dict[str, Any]:
    """El índice tiene que tener el corpus congelado completo.

    Un índice incompleto no da error: da **menos evidencia**, y menos evidencia se
    cuenta como una abstención legítima. Sería el peor fallo posible de esta
    evaluación, porque confirmaría la hipótesis por la razón equivocada y las
    cifras parecerían buenas. La sección 11 lo trata como motivo de invalidez.
    """
    congelado = manifiesto["controlled_state"]["corpus"]
    esperado = {
        "n_chunks": int(congelado["n_chunks"]),
        "n_source_files": int(congelado["n_source_files"]),
    }
    diferencias = [
        f"{clave}: indexado {recuentos.get(clave)}, congelado {valor}"
        for clave, valor in esperado.items()
        if recuentos.get(clave) != valor
    ]
    vectores = recuentos.get("n_vectors_in_space")
    if vectores != esperado["n_chunks"]:
        diferencias.append(
            f"vectores en el espacio declarado: {vectores}, fragmentos {esperado['n_chunks']}"
        )

    # Los recuentos no detectan una sustitución: cambiar el texto de un fragmento o
    # un código por el que la recuperación filtra deja el número de filas igual.
    huella_congelada = congelado.get("content_fingerprint_16")
    if huella_congelada and fingerprint is not None and fingerprint != huella_congelada:
        diferencias.append(
            f"huella de contenido: indexada {fingerprint}, congelada {huella_congelada}"
        )

    # Y los vectores: la búsqueda ordena por distancia al vector, de modo que
    # sustituir uno cambia qué evidencia se recupera sin mover ningún recuento.
    vectores_congelados = manifiesto["controlled_state"]["embedding"].get("vectors_fingerprint_16")
    if (
        vectores_congelados
        and vectors_fingerprint is not None
        and vectors_fingerprint != vectores_congelados
    ):
        diferencias.append(
            f"huella de los vectores: indexada {vectors_fingerprint}, "
            f"congelada {vectores_congelados}"
        )

    resultado = {
        "declared": {
            **esperado,
            "content_fingerprint_16": huella_congelada,
            "vectors_fingerprint_16": vectores_congelados,
        },
        "indexed": {
            **dict(recuentos),
            "content_fingerprint_16": fingerprint,
            "vectors_fingerprint_16": vectors_fingerprint,
        },
        "matches": not diferencias,
    }
    if not diferencias:
        return resultado
    msg = (
        "el indice no contiene el corpus congelado completo: "
        + "; ".join(diferencias)
        + ". Un indice incompleto no da error, da menos evidencia, y menos evidencia "
        "se cuenta como una abstencion legitima."
    )
    if estricto:
        raise CongelacionInvalidaError(msg)
    print(f"AVISO: {msg} En un ensayo se admite; en la evaluación final detendría.")
    return resultado


def exigir_espacio_identificado_por_su_nombre(
    espacios: Sequence[tuple[str, int, str]], *, modelo: str, estricto: bool
) -> tuple[tuple[str, int, str], ...]:
    """El nombre del modelo tiene que identificar **un solo** espacio indexado.

    La búsqueda acota por nombre de modelo, que es lo que RERUN-A impuso para no
    mezclar dos modelos en una ordenación. Pero la identidad de un espacio incluye
    el proveedor con su dispositivo, la dimensión y la versión: si dos espacios
    compartieran nombre, acotar por nombre dejaría de identificar uno y la
    ordenación volvería a mezclar vectores de espacios distintos, que es
    exactamente `MIXED-EMBEDDING-SPACE`.

    Se comprueba en lugar de cambiar el filtro de la búsqueda: mientras el nombre
    identifique un único espacio, acotar por nombre y acotar por identidad son la
    misma cosa, y las fases ya medidas no cambian de comportamiento.
    """
    if len(espacios) == 1:
        return tuple(espacios)
    detalle = "; ".join(f"{p}/d{d}/v{v}" for p, d, v in espacios)
    msg = (
        f"el nombre de modelo {modelo!r} identifica {len(espacios)} espacios en el "
        f"índice ({detalle or 'ninguno'}), y la búsqueda acota por nombre: la "
        "ordenación mezclaría vectores de espacios distintos."
    )
    if estricto:
        raise CongelacionInvalidaError(msg)
    print(f"AVISO: {msg} En un ensayo se admite; en la evaluación final detendría.")
    return tuple(espacios)


def ficheros_con_seguimiento_modificados() -> tuple[str, ...] | None:
    """Ficheros **con seguimiento** modificados, o `None` si no se puede saber.

    Deja fuera los que no tienen seguimiento a propósito: la anotación de E19 se
    sella antes del registro y en ese momento es uno de ellos, de modo que exigir
    un árbol sin nada pendiente sería imposible de cumplir.

    La distinción entre «no hay ninguno» y «no se ha podido averiguar» es la que
    importa, y la primera versión las confundía: devolvía la tupla vacía cuando
    Git fallaba, y un árbol que no se podía comprobar pasaba por limpio.
    """
    resultado = _git("status", "--porcelain", "--untracked-files=no")
    if resultado is None or resultado.returncode != 0:
        return None
    lineas = resultado.stdout.decode("utf-8", errors="replace").splitlines()
    return tuple(linea[3:].strip() for linea in lineas if linea.strip())


def exigir_arbol_limpio(*, estricto: bool) -> tuple[str, ...]:
    """Con `estricto`, un fichero con seguimiento modificado detiene la ejecución.

    El manifiesto congela el código por su commit, y esa declaración no vale nada
    si el árbol de trabajo tiene cambios: la ejecución usaría una recuperación o un
    verificador que ese commit no contiene mientras el registro declara lo
    contrario. En un ensayo sobre validación solo se avisa, porque ahí es normal
    estar desarrollando.
    """
    modificados = ficheros_con_seguimiento_modificados()
    if modificados is None:
        detalle = (
            "no se ha podido averiguar el estado del árbol de trabajo: sin Git no hay "
            "forma de comprobar que el código es el del commit que el manifiesto declara"
        )
        if estricto:
            raise CongelacionInvalidaError(detalle)
        print(f"AVISO: {detalle}")
        return ()
    if not modificados:
        return ()
    if estricto:
        msg = (
            "hay ficheros con seguimiento modificados y la evaluación final declara "
            "el código por su commit:\n"
            + "\n".join(f"  - {f}" for f in modificados)
            + "\nO se comitean, o la medición declararía un código que no es el que "
            "ejecutó."
        )
        raise CongelacionInvalidaError(msg)
    print(
        "AVISO: hay ficheros con seguimiento modificados. En un ensayo se admite; "
        f"en la evaluación final detendría la ejecución: {', '.join(modificados)}"
    )
    return modificados


def _comprobar_ficheros_del_conjunto(manifiesto: Mapping[str, Any]) -> Comprobacion:
    """Las huellas de los ficheros preprocesados que la ejecución va a leer.

    Están fuera del control de versiones --son binarios de varios megabytes-- de
    modo que la comprobación del árbol de trabajo no puede verlos. Sustituir uno
    dejando el manifiesto de preprocesado con sus recuentos declarados pasaría
    inadvertido, y la evaluación final mediría otros datos creyéndolos los
    congelados.
    """
    declarados = manifiesto["controlled_state"]["dataset"].get("files")
    if not declarados:
        return Comprobacion(
            "ficheros_del_conjunto",
            FALLA,
            "el manifiesto no declara las huellas de los ficheros del conjunto",
        )
    problemas = []
    for ruta, declarada in declarados.items():
        fichero = paths.ROOT / ruta
        if not fichero.is_file():
            problemas.append(f"{ruta} no existe")
            continue
        actual = huella(fichero)
        if actual != declarada:
            problemas.append(f"{ruta}: huella {actual}, declarada {declarada}")
    if problemas:
        return Comprobacion("ficheros_del_conjunto", FALLA, "; ".join(problemas))
    return Comprobacion(
        "ficheros_del_conjunto",
        PASS,
        f"{len(declarados)} fichero(s) preprocesados con la huella congelada",
    )


def verificar(ruta_anclaje: Path = RUTA_ANCLAJE) -> Verificacion:
    """Todas las comprobaciones, en un orden que no esconde ninguna.

    No lanza por un fallo de comprobación: devuelve el resultado completo, para
    que el registro de la ejecución pueda llevarlo entero. Quien decide detener
    la ejecución es `Verificacion.exigir`.
    """
    anclaje = cargar_anclaje(ruta_anclaje)
    manifiesto = cargar_manifiesto(anclaje)
    objeto, posteriores = _comprobar_commit(anclaje)
    return Verificacion(
        (
            _comprobar_huellas(anclaje),
            objeto,
            posteriores,
            _comprobar_politica(manifiesto),
            _comprobar_umbrales(manifiesto),
            _comprobar_modelo(manifiesto),
            _comprobar_conjunto_anotado(manifiesto),
            _comprobar_casos_elegibles(manifiesto),
            _comprobar_reparto(manifiesto),
            _comprobar_ficheros_del_conjunto(manifiesto),
        )
    )
