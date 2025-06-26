# config/settings.py
from pathlib import Path

# rutas por defecto de los BC3 a comparar
OLD_BC3_DEFAULT: Path = Path("input/presupuesto_1.bc3")
NEW_BC3_DEFAULT: Path = Path("input/presupuesto_2.bc3")

# rutas donde se volcáran los DataFrames
OLD_DF_CSV_DEFAULT: Path = Path("output/old_df.csv")
NEW_DF_CSV_DEFAULT: Path = Path("output/new_df.csv")

# ruta para las diferencias de descripción larga
LONG_DESC_DIFF_CSV_DEFAULT: Path = Path("output/long_desc_diff.csv")

# CSV
CSV_SEP: str = ";"
CSV_ENCODING: str = "utf-8"
