# application/services/bc3_text_fix.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple, Iterable


def _decode_best(data: bytes, encodings: Iterable[str]) -> tuple[str, str]:
    """
    Devuelve (texto, encoding_usado). Prioriza cp1252/latin-1 para BC3 españoles.
    """
    for enc in encodings:
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            continue
    # Último recurso: latin-1 con 'replace' para no reventar
    return data.decode("latin-1", errors="replace"), "latin-1*"


def extract_multiline_texts(path: Path) -> Tuple[str, Dict[str, str]]:
    """
    Reconstruye los bloques ~T|<codigo>|... hasta encontrar una línea que termine en '|'.
    Conserva saltos de línea intermedios.

    Retorna:
      (encoding_usado, {codigo: descripcion_larga})
    """
    raw = path.read_bytes()
    text, used = _decode_best(raw, ("cp1252", "latin-1", "utf-8"))
    lines = text.splitlines()

    out: Dict[str, str] = {}
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        if line.startswith("~T|"):
            # ~T|<codigo>|<contenido_parcial_posible>
            parts = line.split("|", 2)
            if len(parts) >= 3:
                code = parts[1]
                first = parts[2]
                block = [first]

                if first.endswith("|"):
                    block[-1] = block[-1][:-1]
                else:
                    i += 1
                    while i < n:
                        block.append(lines[i])
                        if block[-1].endswith("|"):
                            block[-1] = block[-1][:-1]
                            break
                        i += 1

                out[code] = "\n".join(block)
        i += 1

    return used, out
