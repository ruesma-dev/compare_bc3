# config/settings.py
from pathlib import Path

# rutas por defecto de los BC3 a comparar
OLD_BC3_DEFAULT: Path = Path("input/presupuesto_1.bc3")
NEW_BC3_DEFAULT: Path = Path("input/presupuesto_2.bc3")

# rutas donde se volcáran los DataFrames
OLD_DF_CSV_DEFAULT: Path = Path("output/old_df.csv")
NEW_DF_CSV_DEFAULT: Path = Path("output/new_df.csv")

# ruta para las diferencias
LONG_DESC_DIFF_CSV_DEFAULT: Path = Path("output/long_desc_diff.csv")
PRICE_DIFF_CSV_DEFAULT: Path = Path("output/price_diff.csv")
QTY_DIFF_CSV_DEFAULT: Path   = Path("output/qty_diff.csv")
IMP_DIFF_CSV_DEFAULT: Path   = Path("output/importe_diff.csv")
NEW_DEL_DIFF_CSV_DEFAULT: Path  = Path("output/new_deleted_diff.csv")

OLD_DF_XLSX_DEFAULT: Path        = Path("output/old_df.xlsx")
NEW_DF_XLSX_DEFAULT: Path        = Path("output/new_df.xlsx")
LONG_DESC_DIFF_XLSX_DEFAULT: Path= Path("output/long_desc_diff.xlsx")
PRICE_DIFF_XLSX_DEFAULT: Path    = Path("output/price_diff.xlsx")
QTY_DIFF_XLSX_DEFAULT: Path      = Path("output/qty_diff.xlsx")
IMP_DIFF_XLSX_DEFAULT: Path      = Path("output/importe_diff.xlsx")
NEW_DEL_DIFF_XLSX_DEFAULT: Path  = Path("output/new_deleted_diff.xlsx")

# CSV
CSV_SEP: str = ";"
CSV_ENCODING: str = "utf-8"
