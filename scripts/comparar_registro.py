"""Compara un registro reproducido con el versionado, sin tocar ninguno de los dos.

**Por qué existe.** Los guiones de reproducción comparaban con `git diff`, lo que
exigía que la reejecución **sobrescribiera** el registro publicado. Funcionaba, y
tenía un precio: para comprobar que un resultado se reproduce había que destruir
el resultado. Si la reproducción fallaba a mitad, el registro quedaba a medias.

Ahora la reejecución escribe con etiqueta propia y este guion compara los dos
ficheros. El publicado no se toca.

**Qué ignora, y por qué.** La cabecera de identificación —`commit`,
`executed_at`, `dirty`— cambia siempre, por construcción: una reejecución ocurre
en otro momento y casi siempre en otro commit. Compararla produciría una
diferencia en cada ejecución y acabaría ignorándose entera, que es peor que
declarar desde el principio qué no se compara.

Lo que sí se compara es todo lo demás: métricas, configuración, recuentos y
decisiones.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

#: Campos que cambian en toda reejecución y cuya diferencia no significa nada.
VOLATILES: frozenset[str] = frozenset(
    {"commit", "executed_at", "dirty", "etiqueta", "training_seconds", "elapsed_seconds"}
)


def _aplanar(valor: Any, prefijo: str = "") -> dict[str, Any]:
    """Convierte un documento anidado en rutas planas, para comparar hoja a hoja."""
    if isinstance(valor, dict):
        plano: dict[str, Any] = {}
        for clave, dentro in valor.items():
            if clave in VOLATILES:
                continue
            plano.update(_aplanar(dentro, f"{prefijo}.{clave}" if prefijo else str(clave)))
        return plano
    if isinstance(valor, list):
        plano = {}
        for i, dentro in enumerate(valor):
            plano.update(_aplanar(dentro, f"{prefijo}[{i}]"))
        return plano
    return {prefijo: valor}


def comparar(publicado: Path, reproducido: Path) -> int:
    """Devuelve 0 si coinciden en todo lo que no es volátil."""
    if not publicado.is_file():
        print(f"no está el registro publicado: {publicado}")
        return 2
    if not reproducido.is_file():
        print(f"no está el registro reproducido: {reproducido}")
        return 2

    a = _aplanar(json.loads(publicado.read_text("utf-8")))
    b = _aplanar(json.loads(reproducido.read_text("utf-8")))

    solo_publicado = sorted(set(a) - set(b))
    # Un campo que solo está en el reproducido **no es una diferencia**: el
    # esquema de los registros crece --se añadió `protocolo`, por ejemplo-- y un
    # registro antiguo no lo tiene. Lo que sí es una diferencia es que al
    # reproducido le **falte** algo que el publicado traía: ahí se ha perdido
    # información.
    campos_nuevos = sorted(set(b) - set(a))
    distintos = sorted(c for c in set(a) & set(b) if a[c] != b[c])

    print(f"\n{publicado.name}  frente a  {reproducido.name}")
    if campos_nuevos:
        print(
            f"  {len(campos_nuevos)} campo(s) que el registro publicado no traía, por haber "
            f"crecido el esquema: {', '.join(campos_nuevos[:6])}"
        )
    if not (solo_publicado or distintos):
        print(
            f"  REPRODUCIDO: coinciden los {len(a)} campos del registro publicado "
            f"(se ignoran {', '.join(sorted(VOLATILES))})"
        )
        return 0

    for campo in solo_publicado[:10]:
        print(f"  FALTA en el reproducido: {campo} = {a[campo]!r}")
    for campo in distintos[:20]:
        print(f"  DIFIERE {campo}: publicado {a[campo]!r} · reproducido {b[campo]!r}")
    total = len(solo_publicado) + len(distintos)
    print(f"  {total} diferencia(s) sobre {len(a)} campos del registro publicado")
    return 1


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("uso: comparar_registro.py <registro_publicado.json> <registro_reproducido.json>")
        return 2
    return comparar(Path(argv[0]), Path(argv[1]))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
