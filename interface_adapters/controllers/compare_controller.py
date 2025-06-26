# interface_adapters/controllers/compare_controller.py
from pathlib import Path

from application.services.diff_service import DiffService
from infrastructure.exporters.df_exporter import export_df
from config import settings


def run(old_bc3: Path, new_bc3: Path) -> None:
    # 1) DataFrames
    df_old, df_new = DiffService.load_dfs(old_bc3, new_bc3)

    print("=== PRESUPUESTO 1 ===")
    print(df_old)
    print("\n=== PRESUPUESTO 2 ===")
    print(df_new)

    # 2) Guardar DataFrames
    export_df(df_old, settings.OLD_DF_CSV_DEFAULT)
    export_df(df_new, settings.NEW_DF_CSV_DEFAULT)
    print(f"DataFrames exportados en {settings.OLD_DF_CSV_DEFAULT} y {settings.NEW_DF_CSV_DEFAULT}")

    # 3) Diferencias en descripcion_larga + extras
    ld_diff = DiffService.long_desc_diffs(df_old, df_new)
    print("\n=== DIFERENCIAS EN DESCRIPCION_LARGA (con precio, cantidades, mediciones) ===")
    print(ld_diff)

    export_df(ld_diff, settings.LONG_DESC_DIFF_CSV_DEFAULT)
    print(f"Diferencias exportadas → {settings.LONG_DESC_DIFF_CSV_DEFAULT.resolve()}")
