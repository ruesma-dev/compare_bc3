# domain/models/change.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class Change:
    codigo: str              # código de concepto
    tipo: str                # 'añadido' | 'eliminado' | 'modificado'
    campo: Optional[str]     # campo modificado (None para alta/baja)
    antes: Optional[Any]     # valor en BC3 origen
    despues: Optional[Any]   # valor en BC3 revisado
