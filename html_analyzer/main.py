"""Punto de entrada opcional para probar el analizador desde Python."""

import json
import sys
from .analyzer import analyze


def main() -> None:
    """Lee HTML desde un archivo o stdin y escribe el analisis como JSON."""
    source = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    print(json.dumps(analyze(source).as_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
