# infrastructure/exporters/diff_csv_exporter.py
from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from domain.models.change import Change
from config import settings


def export_diff(changes: List[Change], csv_path: Path) -> None:
    rows = [
        {
            "codigo": c.codigo,
            "cambio": c.tipo,
            "campo": c.campo or "",
            "antes": c.antes if c.antes is not None else "",
            "despues": c.despues if c.despues is not None else "",
        }
        for c in changes
    ]
    df = pd.DataFrame(
        rows,
        columns=["codigo", "cambio", "campo", "antes", "despues"],
    )
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, sep=settings.CSV_SEP, index=False, encoding=settings.CSV_ENCODING)
