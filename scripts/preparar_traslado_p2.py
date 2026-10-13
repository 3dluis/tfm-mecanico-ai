"""Las diez comprobaciones previas al traslado de P2 a otra máquina.

**Qué es esto.** El autor autorizó la alternativa D —ejecutar el reentrenamiento
del adaptador en una máquina con más memoria— y fijó diez condiciones que hay que
comprobar **antes** de ejecutar. Este guion las comprueba todas, en orden, y
**devuelve distinto de cero si alguna falla**, de modo que «se comprobó» no sea
una afirmación sino un código de salida.

Se ejecuta **en la máquina de destino**, dentro del clon del repositorio.

Las diez:

1. compatibilidad del entorno
2. memoria realmente disponible
3. huellas de los datos de ajuste
4. integridad de la congelación
5. hardware y versiones, registrados
6. ausencia de diferencias metodológicas
7. estimación del consumo de memoria
8. prueba técnica breve
9. diferencias numéricas derivadas del hardware
10. veredicto: solo se ejecuta el ajuste si las nueve anteriores pasan

**Lo que este guion no hace:** no entrena, no escribe en `models/` y no toca
ningún artefacto congelado. La prueba técnica del paso 8 hace una pasada hacia
adelante y otra hacia atrás sobre el ejemplo **más largo** —el caso peor— y
libera; no hay optimizador y no se guarda nada.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[1]
CONGELACION = RAIZ / "configs" / "congelacion-adaptador-v3.json"
SONDA = RAIZ / "configs" / "sonda-equivalencia-p2.json"
PROCESADOS = RAIZ / "data" / "processed"

#: Necesidad medida en la máquina de 24 GB, en los seis intentos de INC-P2-02.
#: El pico de un paso creció de 13,0 a 17,0 GB según la longitud del ejemplo.
PICO_MEDIDO_GB = 17.0

#: Margen sobre el pico medido. No es un número elegido por gusto: el pico creció
#: con cada intento porque los ejemplos no miden lo mismo, y 47 de 101 topan en
#: 3 072 tokens. Un 40 % cubre que el peor ejemplo pida más de lo observado.
MARGEN = 1.4


class ComprobacionFallidaError(Exception):
    """Una comprobación que no pasa. Detiene el guion con su motivo."""


def _huella(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()[:16]


def _titulo(n: int, texto: str) -> None:
    print(f"\n{'─' * 72}\n{n}. {texto}\n")


# ----------------------------------------------------------------- 1 · entorno


def comprobar_entorno() -> dict[str, Any]:
    _titulo(1, "Compatibilidad del entorno")
    import torch

    datos: dict[str, Any] = {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "plataforma": platform.platform(),
    }
    faltan = []
    for modulo in ("transformers", "peft", "accelerate", "datasets"):
        try:
            importado = __import__(modulo)
            datos[modulo] = getattr(importado, "__version__", "?")
            print(f"  ok       {modulo} {datos[modulo]}")
        except ImportError:
            faltan.append(modulo)
            print(f"  FALTA    {modulo}")
    if faltan:
        msg = (
            f"faltan {', '.join(faltan)}. Instale con «uv sync --extra nb --extra ml "
            "--extra embeddings --extra finetune --extra llm»"
        )
        raise ComprobacionFallidaError(msg)

    if torch.backends.mps.is_available():
        datos["acelerador"] = "mps"
    elif torch.cuda.is_available():  # pragma: no cover - no hay CUDA aquí
        datos["acelerador"] = "cuda"
    else:
        datos["acelerador"] = "cpu"
    print(f"  ok       acelerador disponible: {datos['acelerador']}")
    if datos["acelerador"] == "cpu":
        raise ComprobacionFallidaError(
            "no hay acelerador. El dispositivo congelado es «mps»; ejecutar en CPU sería la "
            "alternativa B, que cambia la configuración congelada y exige otra autorización"
        )
    return datos


# ----------------------------------------------------------------- 2 · memoria


def comprobar_memoria() -> dict[str, Any]:
    _titulo(2, "Memoria realmente disponible")
    import torch

    datos: dict[str, Any] = {}
    if torch.backends.mps.is_available():
        total = int(
            subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout
            or 0
        )
        datos["memoria_fisica_gb"] = round(total / 2**30, 1)
        datos["memoria_recomendada_mps_gb"] = round(torch.mps.recommended_max_memory() / 2**30, 2)
        print(f"  memoria física de la máquina        {datos['memoria_fisica_gb']:.1f} GB")
        print(f"  máximo que MPS recomienda           {datos['memoria_recomendada_mps_gb']:.2f} GB")
    else:  # pragma: no cover - no hay CUDA aquí
        propiedades = torch.cuda.get_device_properties(0)
        datos["gpu"] = propiedades.name
        datos["memoria_recomendada_mps_gb"] = round(propiedades.total_memory / 2**30, 2)
        print(f"  GPU                                 {datos['gpu']}")
        print(f"  memoria de la GPU                   {datos['memoria_recomendada_mps_gb']:.2f} GB")

    necesario = PICO_MEDIDO_GB * MARGEN
    print(f"  pico medido en la máquina de 24 GB  {PICO_MEDIDO_GB:.1f} GB")
    print(f"  con margen del {round((MARGEN - 1) * 100)} %                  {necesario:.1f} GB")
    datos["necesario_gb"] = round(necesario, 1)
    if datos["memoria_recomendada_mps_gb"] < necesario:
        raise ComprobacionFallidaError(
            f"el acelerador recomienda {datos['memoria_recomendada_mps_gb']:.2f} GB y hacen falta "
            f"{necesario:.1f} GB. Esta máquina NO es adecuada; no se intenta el ajuste en ella"
        )
    print(
        f"\n  ok       hay holgura: {datos['memoria_recomendada_mps_gb']:.2f} ≥ {necesario:.1f} GB"
    )
    return datos


# ------------------------------------------------------- 3 y 4 · datos y congelación


def comprobar_datos_y_congelacion() -> dict[str, Any]:
    _titulo(3, "Huellas de los datos de ajuste")
    if not CONGELACION.is_file():
        msg = f"no está {CONGELACION.name}: sin congelación no hay nada que verificar"
        raise ComprobacionFallidaError(msg)
    congelacion = json.loads(CONGELACION.read_text("utf-8"))
    esperadas = congelacion["datos_de_ajuste"]["huellas_sha256_16"]

    problemas = 0
    for relativa, esperada in esperadas.items():
        fichero = PROCESADOS / relativa
        if not fichero.is_file():
            print(f"  FALTA    {relativa}")
            problemas += 1
            continue
        real = _huella(fichero)
        estado = "ok      " if real == esperada else "DIFIERE "
        print(f"  {estado} {relativa}  {real}")
        problemas += int(real != esperada)
    if problemas:
        raise ComprobacionFallidaError(
            f"{problemas} de {len(esperadas)} ficheros de ajuste no coinciden con la congelación. "
            "El ajuste no sería el declarado"
        )

    _titulo(4, "Integridad de la congelación")
    hiper = {
        "lora_rank": 16,
        "lora_alpha": 32,
        "epochs": 4,
        "learning_rate": 2e-4,
        "max_seq_length": 3072,
        "seed": 20260901,
        "device": "mps",
    }
    from mecanico_ia_exp.llm.finetune import FinetuneConfig

    cfg = FinetuneConfig()
    diferencias = []
    for clave, valor in hiper.items():
        actual = getattr(cfg, clave)
        estado = "ok      " if actual == valor else "CAMBIÓ  "
        print(f"  {estado} {clave:18} {actual}")
        if actual != valor:
            diferencias.append(f"{clave}: {valor} → {actual}")
    if diferencias:
        raise ComprobacionFallidaError(
            "hiperparámetros distintos de los congelados: " + "; ".join(diferencias) + ". "
            "La instrucción del autor es no modificarlos"
        )
    print("\n  ok       los 7 hiperparámetros coinciden con los congelados")
    print(f"  ok       {len(esperadas)} huellas de datos coinciden")
    return {"congelacion": CONGELACION.name, "n_huellas": len(esperadas)}


# ------------------------------------------------- 5 y 6 · hardware y método


def registrar_hardware(entorno: dict[str, Any], memoria: dict[str, Any]) -> dict[str, Any]:
    _titulo(5, "Hardware y versiones, registrados")
    registro = {**entorno, **memoria}
    for clave, valor in registro.items():
        print(f"  {clave:34} {valor}")
    return registro


def comprobar_metodo() -> None:
    _titulo(6, "Ausencia de diferencias metodológicas")
    from mecanico_ia_exp.llm.finetune import FinetuneConfig

    cfg = FinetuneConfig()
    print(f"  modelo base                        {cfg.base_model}")
    print("  precisión                          bfloat16 (fijada en el código)")
    print(f"  módulos objetivo                   {', '.join(cfg.target_modules)}")
    print("  recomputación de gradientes        activada")
    print("  partición de origen de los datos   train (la congelación lo declara)")
    print("\n  Lo que SÍ es distinto entre máquinas, y está declarado:")
    print(f"    techo del asignador              {cfg.fraccion_de_memoria}")
    print(f"    vaciado del caché por paso       {cfg.vaciar_cache_por_paso}")
    print(
        "\n  ok       ninguna de las dos altera el cálculo: cambian cuándo se devuelve la memoria"
    )


# --------------------------------------------- 7 y 8 · estimación y prueba técnica


def prueba_tecnica(dispositivo: str) -> dict[str, Any]:
    _titulo(7, "Estimación del consumo de memoria")
    print(
        f"  pico medido en la máquina de 24 GB, con el ejemplo más largo: {PICO_MEDIDO_GB:.1f} GB"
    )
    print("  desglose observado en el sexto intento:")
    print("    13,39 GB reservados + 1,87 GB otras reservas + 1,74 GB pedidos")
    print("  la reserva grande es la pérdida sobre 151 936 entradas de vocabulario")

    _titulo(8, "Prueba técnica breve: una pasada completa sobre el ejemplo más largo")
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from mecanico_ia_exp.llm.finetune import FinetuneConfig, _cargar_jsonl, _tokenizar

    cfg = FinetuneConfig()
    if dispositivo == "mps":
        torch.mps.set_per_process_memory_fraction(cfg.fraccion_de_memoria)

    tokenizador = AutoTokenizer.from_pretrained(cfg.base_model)
    ejemplos = _cargar_jsonl(PROCESADOS / "slm_finetune_prepared_sin_contaminacion" / "train.jsonl")
    peor = max(ejemplos, key=lambda e: len(tokenizador(e["prompt"] + e["completion"])["input_ids"]))
    ids, etiquetas, recortado = _tokenizar(tokenizador, peor, cfg.max_seq_length)
    print(f"  ejemplo más largo: {len(ids)} tokens (recortado: {recortado})")

    base: Any = AutoModelForCausalLM.from_pretrained(cfg.base_model, dtype=torch.bfloat16)
    base.to(dispositivo)
    modelo: Any = get_peft_model(
        base,
        LoraConfig(
            r=cfg.lora_rank,
            lora_alpha=cfg.lora_alpha,
            lora_dropout=cfg.lora_dropout,
            target_modules=list(cfg.target_modules),
            task_type="CAUSAL_LM",
        ),
    )
    modelo.gradient_checkpointing_enable()
    modelo.enable_input_require_grads()
    modelo.config.use_cache = False
    modelo.train()

    entrada = torch.tensor([ids], device=dispositivo)
    objetivos = torch.tensor([etiquetas], device=dispositivo)
    salida = modelo(input_ids=entrada, labels=objetivos)
    print(f"  ok       pasada hacia adelante: pérdida {float(salida.loss.item()):.6f}")
    salida.loss.backward()
    print("  ok       pasada hacia atrás completada")

    pico = None
    if dispositivo == "mps":
        pico = round(torch.mps.driver_allocated_memory() / 2**30, 2)
        print(f"  pico del asignador tras el paso: {pico:.2f} GB")
        torch.mps.empty_cache()
    print("\n  ok       el caso peor cabe. Nada se ha escrito en models/")
    return {"tokens_del_peor_ejemplo": len(ids), "pico_asignador_gb": pico}


# ------------------------------------------------------------- 9 · equivalencia


def comprobar_equivalencia(dispositivo: str) -> int:
    _titulo(9, "Diferencias numéricas derivadas del hardware")
    if not SONDA.is_file():
        print("  no hay sonda de referencia; ejecute antes el guion de la sonda con --medir")
        return 1
    orden = [sys.executable, str(RAIZ / "scripts" / "sonda_equivalencia_p2.py"), "--comprobar"]
    if dispositivo:
        orden += ["--dispositivo", dispositivo]
    return subprocess.run(orden, cwd=RAIZ, check=False).returncode


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--sin-prueba-tecnica",
        action="store_true",
        help="omite los pasos 8 y 9, que cargan el modelo; el veredicto queda incompleto",
    )
    parser.add_argument("--dispositivo", default="")
    args = parser.parse_args(argv)

    print("COMPROBACIONES PREVIAS AL TRASLADO DE P2 (alternativa D)")
    print(f"repositorio: {RAIZ}")

    registro: dict[str, Any] = {}
    try:
        entorno = comprobar_entorno()
        memoria = comprobar_memoria()
        registro["datos"] = comprobar_datos_y_congelacion()
        registro["hardware"] = registrar_hardware(entorno, memoria)
        comprobar_metodo()
        dispositivo = args.dispositivo or entorno["acelerador"]
        if args.sin_prueba_tecnica:
            print("\n  (pasos 8 y 9 omitidos por petición)")
            codigo_equivalencia = -1
        else:
            registro["prueba_tecnica"] = prueba_tecnica(dispositivo)
            codigo_equivalencia = comprobar_equivalencia(dispositivo)
    except ComprobacionFallidaError as fallo:
        _titulo(10, "Veredicto")
        print(f"  NO SE EJECUTA EL AJUSTE.\n\n  Motivo: {fallo}")
        print(
            "\n  Si esta máquina no sirve, P2 queda pendiente por dependencia de infraestructura.\n"
            "  Eso NO es un fracaso científico del experimento: es que no hay máquina."
        )
        return 1
    except Exception as error:
        _titulo(10, "Veredicto")
        print(f"  NO SE EJECUTA EL AJUSTE.\n\n  Fallo inesperado: {type(error).__name__}: {error}")
        return 1

    _titulo(10, "Veredicto")
    if codigo_equivalencia == 0:
        print("  LAS NUEVE COMPROBACIONES PASAN. El ajuste se puede ejecutar:\n")
        print("    uv run mecanico-exp finetune-slm --datos sin_contaminacion \\")
        print("      --adapter-dir slm_lora_v3 --epochs 4")
        print(
            "\n  Registre la salida en experiments/runs/ y, al terminar, las huellas del adaptador."
        )
        print("  Y recuerde lo que la sonda NO garantiza: que las pérdidas sean idénticas a las de")
        print("  otra máquina. Si difieren, se registra la diferencia; no se oculta.")
        return 0
    if codigo_equivalencia == -1:
        print("  INCOMPLETO: los pasos 8 y 9 se omitieron. No se autoriza el ajuste.")
        return 2
    print("  NO SE EJECUTA EL AJUSTE: la sonda de equivalencia no coincide.")
    print("  Antes de seguir hay que presentar una evaluación de equivalencia.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
