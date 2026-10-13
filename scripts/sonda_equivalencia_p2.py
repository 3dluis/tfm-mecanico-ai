"""Sonda de equivalencia entre máquinas, para el traslado de P2.

**Qué problema resuelve.** El ajuste del adaptador se traslada a una máquina con
más memoria. La instrucción del autor es explícita: *no asumir que los resultados
serán idénticos entre plataformas*. Pero «no asumir» no basta: hay que poder
**medir** cuánto difieren, y para eso hace falta una cifra tomada en las dos
máquinas con el mismo procedimiento.

**Qué mide.** La pérdida del modelo base —sin adaptador, sin entrenar, sin
gradientes— sobre seis ejemplos del conjunto de ajuste congelado: los tres más
largos y los tres más cortos, elegidos por número de tokens y, a igualdad, por
orden alfabético del contenido. Es una medición **determinista**: el mismo modelo,
los mismos pesos, los mismos tokens, sin aleatoriedad de ninguna clase.

**Por qué esos seis.** Los tres más largos son el caso peor de memoria y el que
reventó seis intentos en la máquina de 24 GB. Los tres más cortos dan el otro
extremo. Si la pérdida coincide en los seis, el camino numérico de las dos
máquinas coincide donde importa.

**Qué NO mide.** Nada del ajuste: no hay optimizador, no hay pasos, no se escribe
ningún adaptador y no se toca `models/`. Una sonda que entrenara dejaría de ser
una sonda.

**Cómo se lee el resultado.** Diferencias del orden de 1e-3 en bfloat16 entre
plataformas distintas son esperables y **no** invalidan el traslado: hay que
registrarlas. Diferencias grandes —o un orden de magnitud distinto— significan que
el camino numérico no es el mismo, y entonces el traslado exige una evaluación de
equivalencia antes de ejecutar el ajuste completo, no después.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[1]
SONDA = RAIZ / "configs" / "sonda-equivalencia-p2.json"
DATOS = RAIZ / "data" / "processed" / "slm_finetune_prepared_sin_contaminacion"

#: Cuántos ejemplos de cada extremo. Seis en total: suficiente para ver una
#: divergencia y lo bastante poco para que la sonda tarde un minuto.
POR_EXTREMO = 3

#: Tolerancia por defecto. En bfloat16, entre plataformas distintas, una
#: diferencia de este orden es aritmética y no metodológica.
TOLERANCIA = 5e-3


def _hardware() -> dict[str, Any]:
    """Lo que hace falta para saber si dos mediciones son comparables."""
    import torch

    datos: dict[str, Any] = {
        "plataforma": platform.platform(),
        "procesador": platform.processor() or platform.machine(),
        "python": platform.python_version(),
        "torch": torch.__version__,
    }
    try:
        import transformers

        datos["transformers"] = transformers.__version__
    except ImportError:  # pragma: no cover - el extra puede faltar
        datos["transformers"] = "no instalado"

    if torch.backends.mps.is_available():
        datos["acelerador"] = "mps"
        datos["memoria_recomendada_gb"] = round(torch.mps.recommended_max_memory() / 2**30, 2)
    elif torch.cuda.is_available():  # pragma: no cover - no hay CUDA aquí
        datos["acelerador"] = "cuda"
        propiedades = torch.cuda.get_device_properties(0)
        datos["gpu"] = propiedades.name
        datos["memoria_recomendada_gb"] = round(propiedades.total_memory / 2**30, 2)
    else:  # pragma: no cover
        datos["acelerador"] = "cpu"
        datos["memoria_recomendada_gb"] = None
    return datos


def _elegidos(tokenizador: Any, longitud_maxima: int) -> list[dict[str, Any]]:
    """Los tres ejemplos más largos y los tres más cortos, deterministas."""
    from mecanico_ia_exp.llm.finetune import _cargar_jsonl, _tokenizar

    ejemplos = _cargar_jsonl(DATOS / "train.jsonl")
    medidos = []
    for i, ejemplo in enumerate(ejemplos):
        ids, etiquetas, _ = _tokenizar(tokenizador, ejemplo, longitud_maxima)
        completo = len(tokenizador(ejemplo["prompt"] + ejemplo["completion"])["input_ids"])
        medidos.append(
            {
                "indice": i,
                "tokens_sin_recortar": completo,
                "tokens": len(ids),
                "ids": ids,
                "etiquetas": etiquetas,
            }
        )
    # Orden determinista: por longitud sin recortar y, a igualdad, por índice.
    medidos.sort(key=lambda m: (m["tokens_sin_recortar"], m["indice"]))
    return medidos[:POR_EXTREMO] + medidos[-POR_EXTREMO:]


def medir(dispositivo: str) -> dict[str, Any]:
    """Calcula la sonda. Sin gradientes, sin optimizador, sin escribir nada."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from mecanico_ia_exp.llm.finetune import FinetuneConfig

    cfg = FinetuneConfig()
    tokenizador = AutoTokenizer.from_pretrained(cfg.base_model)
    elegidos = _elegidos(tokenizador, cfg.max_seq_length)

    modelo: Any = AutoModelForCausalLM.from_pretrained(cfg.base_model, dtype=torch.bfloat16)
    modelo.to(dispositivo)
    modelo.eval()

    medidas = []
    with torch.no_grad():
        for ejemplo in elegidos:
            entrada = torch.tensor([ejemplo["ids"]], device=dispositivo)
            etiquetas = torch.tensor([ejemplo["etiquetas"]], device=dispositivo)
            salida = modelo(input_ids=entrada, labels=etiquetas)
            medidas.append(
                {
                    "indice": ejemplo["indice"],
                    "tokens_sin_recortar": ejemplo["tokens_sin_recortar"],
                    "tokens": ejemplo["tokens"],
                    "perdida": round(float(salida.loss.item()), 6),
                }
            )
            if dispositivo == "mps":
                torch.mps.empty_cache()

    return {
        "que_es": (
            "perdida del modelo BASE, sin adaptador y sin entrenar, sobre los 3 ejemplos mas "
            "largos y los 3 mas cortos del conjunto de ajuste congelado. Deterministica"
        ),
        "modelo_base": cfg.base_model,
        "precision": "bfloat16",
        "max_seq_length": cfg.max_seq_length,
        "dispositivo": dispositivo,
        "datos": "data/processed/slm_finetune_prepared_sin_contaminacion/train.jsonl",
        "hardware": _hardware(),
        "medidas": medidas,
    }


def _comparar(referencia: dict[str, Any], nueva: dict[str, Any], tolerancia: float) -> int:
    print("\nCOMPARACIÓN CON LA SONDA DE REFERENCIA\n")
    ref = {m["indice"]: m for m in referencia["medidas"]}
    problemas = 0
    for medida in nueva["medidas"]:
        anterior = ref.get(medida["indice"])
        if anterior is None:
            print(f"  ejemplo {medida['indice']}: no está en la referencia")
            problemas += 1
            continue
        if anterior["tokens"] != medida["tokens"]:
            print(
                f"  ejemplo {medida['indice']}: TOKENS DISTINTOS "
                f"{anterior['tokens']} → {medida['tokens']}. El tokenizador no es el mismo"
            )
            problemas += 1
            continue
        diferencia = abs(anterior["perdida"] - medida["perdida"])
        estado = "ok" if diferencia <= tolerancia else "FUERA DE TOLERANCIA"
        print(
            f"  ejemplo {medida['indice']:3} · {medida['tokens']:5} tokens · "
            f"referencia {anterior['perdida']:.6f} · aquí {medida['perdida']:.6f} · "
            f"diferencia {diferencia:.2e}  {estado}"
        )
        if diferencia > tolerancia:
            problemas += 1

    print()
    for clave in ("plataforma", "acelerador", "torch", "transformers", "memoria_recomendada_gb"):
        print(
            f"  {clave:24} referencia {referencia['hardware'].get(clave)} · "
            f"aquí {nueva['hardware'].get(clave)}"
        )

    print()
    if problemas:
        print(
            f"{problemas} de {len(nueva['medidas'])} medidas fuera de tolerancia.\n"
            "El camino numérico de las dos máquinas NO coincide. Antes de ejecutar el ajuste hay "
            "que presentar una evaluación de equivalencia, no después."
        )
        return 1
    print(
        f"Las {len(nueva['medidas'])} medidas coinciden dentro de {tolerancia:g}. "
        "El camino numérico es el mismo donde importa.\n"
        "Esto NO garantiza que el ajuste dé pérdidas idénticas: garantiza que la diferencia, si "
        "aparece, no viene del modelo ni del tokenizador."
    )
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--medir",
        action="store_true",
        help="calcula la sonda y la escribe como referencia; se niega a sobrescribirla",
    )
    parser.add_argument(
        "--comprobar",
        action="store_true",
        help="calcula la sonda y la compara con la referencia congelada",
    )
    parser.add_argument(
        "--dispositivo", default="", help="mps, cuda o cpu; por defecto, el de la configuración"
    )
    parser.add_argument("--tolerancia", type=float, default=TOLERANCIA)
    args = parser.parse_args(argv)

    if not (args.medir or args.comprobar):
        parser.error("hay que pedir --medir o --comprobar")

    dispositivo = args.dispositivo
    if not dispositivo:
        from mecanico_ia_exp.llm.finetune import FinetuneConfig

        dispositivo = FinetuneConfig().device

    if args.medir and SONDA.is_file():
        print(
            f"Ya existe {SONDA.relative_to(RAIZ)} y no se sobrescribe: es la referencia contra la "
            "que se compara el traslado. Use --comprobar."
        )
        return 2

    print(f"Calculando la sonda en «{dispositivo}». Sin gradientes y sin escribir en models/.\n")
    nueva = medir(dispositivo)
    for medida in nueva["medidas"]:
        print(
            f"  ejemplo {medida['indice']:3} · {medida['tokens']:5} tokens "
            f"(sin recortar {medida['tokens_sin_recortar']:5}) · pérdida {medida['perdida']:.6f}"
        )

    if args.medir:
        nueva["medida_el"] = "referencia tomada en la máquina del autor"
        SONDA.write_text(json.dumps(nueva, ensure_ascii=False, indent=2) + "\n", "utf-8")
        print(f"\nEscrita la referencia en {SONDA.relative_to(RAIZ)}")
        return 0

    if not SONDA.is_file():
        print(f"\nNo hay referencia en {SONDA.relative_to(RAIZ)}; ejecute --medir primero.")
        return 2
    return _comparar(json.loads(SONDA.read_text("utf-8")), nueva, args.tolerancia)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
