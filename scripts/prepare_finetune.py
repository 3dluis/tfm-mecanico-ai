"""Convierte los ejemplos al par prompt/completion que consume el entrenador.

Cada ejemplo se renderiza con la plantilla de conversación del propio modelo, de
modo que lo que ve durante el ajuste es exactamente lo que verá al inferir. Si se
entrenara con un formato y se infiriera con otro, el modelo aprendería a
responder a una pregunta que nunca se le hará.

Se produce el par ``prompt`` / ``completion``: el prompt llega hasta el turno de
herramienta --donde viaja el texto del manual-- y la completion es solo el JSON.
Así el gradiente actúa **únicamente sobre la salida**, y el contenido del manual
no entra en los pesos ni siquiera como continuación probable.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESADOS = ROOT / "data" / "processed"
# Se renderiza con el tokenizador del MISMO modelo que se ajusta, para que lo que
# ve en el ajuste sea exactamente lo que verá al inferir.
MODELO = "Qwen/Qwen2.5-3B-Instruct"


def main(etiqueta: str = "") -> int:
    """Prepara un conjunto de ejemplos. Con etiqueta, el suyo y no el histórico.

    Los nombres llevan la etiqueta por el mismo motivo que todo lo demás: el
    conjunto preparado de `slm_lora_v2` sostiene un adaptador congelado y no se
    sobrescribe.
    """
    from transformers import AutoTokenizer

    sufijo = f"_{etiqueta}" if etiqueta else ""
    origen_dir = PROCESADOS / f"slm_finetune{sufijo}"
    destino_dir = PROCESADOS / f"slm_finetune_prepared{sufijo}"
    if destino_dir.exists() and any(destino_dir.iterdir()):
        print(f"Ya existe {destino_dir.relative_to(ROOT)} y no se sobrescribe.")
        return 1

    # Los DOS ficheros de entrada se comprueban antes de crear nada. Si faltara
    # uno a mitad, el directorio de destino quedaría creado con un solo fichero
    # dentro, y la negativa a sobrescribir --que existe para proteger un conjunto
    # preparado-- impediría reintentarlo una vez corregida la entrada.
    faltan = [n for n in ("train", "valid") if not (origen_dir / f"{n}.jsonl").is_file()]
    if faltan:
        nombres = ", ".join(f"{n}.jsonl" for n in faltan)
        print(f"faltan en {origen_dir.relative_to(ROOT)}: {nombres}")
        return 1

    tok = AutoTokenizer.from_pretrained(MODELO)
    destino_dir.mkdir(parents=True, exist_ok=True)

    for nombre in ("train", "valid"):
        origen = origen_dir / f"{nombre}.jsonl"
        salidas: list[str] = []
        for linea in origen.read_text(encoding="utf-8").splitlines():
            if not linea.strip():
                continue
            mensajes = json.loads(linea)["messages"]
            # Todo menos el último turno es el prompt; el último es lo que se
            # aprende a producir.
            contexto, objetivo = mensajes[:-1], mensajes[-1]
            prompt = tok.apply_chat_template(contexto, tokenize=False, add_generation_prompt=True)
            salidas.append(
                json.dumps(
                    {"prompt": prompt, "completion": objetivo["content"]},
                    ensure_ascii=False,
                )
            )

        destino = destino_dir / f"{nombre}.jsonl"
        destino.write_text("\n".join(salidas) + "\n", encoding="utf-8")
        largos = [len(tok(json.loads(s)["prompt"])["input_ids"]) for s in salidas]
        print(
            f"{nombre:<6} {len(salidas):>4} ejemplos · "
            f"prompt {min(largos)}-{max(largos)} tokens "
            f"(mediana {sorted(largos)[len(largos) // 2]})"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
