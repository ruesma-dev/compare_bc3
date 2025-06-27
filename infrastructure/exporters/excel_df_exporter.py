# infrastructure/exporters/excel_df_exporter.py
from __future__ import annotations
from pathlib import Path
import pandas as pd
import xlsxwriter


def export_df_excel(df: pd.DataFrame, path: Path) -> None:
    """
    Guarda *df* en un .xlsx simple (una hoja “data”) sin aplicar formatos
    especiales.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    # ningún parámetro extra: pandas se encarga del cód. interno UTF-8
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="data", index=False)
