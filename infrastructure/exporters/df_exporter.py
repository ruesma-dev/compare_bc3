# infrastructure/exporters/df_exporter.py
from __future__ import annotations
from pathlib import Path
import pandas as pd
from config import settings

def export_df(df: pd.DataFrame, path: Path) -> None:
    """
    Exporta cualquier DataFrame a CSV, creando carpetas si es necesario.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep=settings.CSV_SEP, encoding=settings.CSV_ENCODING, index=False)
