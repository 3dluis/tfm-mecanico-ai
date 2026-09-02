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
ORIGEN = ROOT / "data" / "processed" / "slm_finetune"
DESTINO = ROOT / "data" / "processed" / "slm_finetune_prepared"
# Se renderiza con el tokenizador del MISMO modelo que se ajusta, para que lo que
# ve en el ajuste sea exactamente lo que verá al inferir.
MODELO = "Qwen/Qwen2.5-3B-Instruct"


def main() -> int:
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODELO)
    DESTINO.mkdir(parents=True, exist_ok=True)

    for nombre in ("train", "valid"):
        origen = ORIGEN / f"{nombre}.jsonl"
        if not origen.is_file():
            print(f"falta {origen}")
            return 1

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

        destino = DESTINO / f"{nombre}.jsonl"
        destino.write_text("\n".join(salidas) + "\n", encoding="utf-8")
        largos = [len(tok(json.loads(s)["prompt"])["input_ids"]) for s in salidas]
        print(
            f"{nombre:<6} {len(salidas):>4} ejemplos · "
            f"prompt {min(largos)}-{max(largos)} tokens "
            f"(mediana {sorted(largos)[len(largos) // 2]})"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
