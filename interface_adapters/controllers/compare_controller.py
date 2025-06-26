# interface_adapters/controllers/compare_controller.py
from pathlib import Path
from application.services.diff_service import DiffService
from infrastructure.exporters.df_exporter import export_df
from config import settings


def run(old_bc3: Path, new_bc3: Path) -> None:
    # 1) Cargar DataFrames
    df_old, df_new = DiffService.load_dfs(old_bc3, new_bc3)

    # 2) Imprimir en consola
    print("=== DataFrame PRESUPUESTO 1 ===")
    print(df_old)
    print("\n=== DataFrame PRESUPUESTO 2 ===")
    print(df_new)

    # 3) Guardar cada DF a CSV
    export_df(df_old, settings.OLD_DF_CSV_DEFAULT)
    print(f"DataFrame 1 exportado → {settings.OLD_DF_CSV_DEFAULT.resolve()}")
    export_df(df_new, settings.NEW_DF_CSV_DEFAULT)
    print(f"DataFrame 2 exportado → {settings.NEW_DF_CSV_DEFAULT.resolve()}")

    # 4) Comparar descripciones largas
    ld_diffs = DiffService.long_desc_diffs(df_old, df_new)
    print("\n=== Diferencias en DESCRIPCION_LARGA ===")
    print(ld_diffs)

    # 5) Guardar diff de descripciones largas
    export_df(ld_diffs, settings.LONG_DESC_DIFF_CSV_DEFAULT)
    print(f"Diferencias de descripción larga exportadas → {settings.LONG_DESC_DIFF_CSV_DEFAULT.resolve()}")
