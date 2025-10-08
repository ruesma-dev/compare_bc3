# interface_adapters/controllers/compare_controller.py
# interface_adapters/controllers/compare_controller.py
from pathlib import Path

from application.services.diff_service import DiffService
from infrastructure.exporters.excel_workbook_combined_min import export_combined_min
from config import settings


def run(old_bc3: Path, new_bc3: Path) -> None:
    # 1) DataFrames completos -------------------------------------------------
    df_old, df_new = DiffService.load_dfs(old_bc3, new_bc3)

    # 2) Comparativas ---------------------------------------------------------
    ld_diff = DiffService.long_desc_diffs(df_old, df_new)
    price_diff = DiffService.price_diffs(df_old, df_new)
    qty_diff = DiffService.qty_diffs(df_old, df_new)
    imp_diff = DiffService.importe_diffs(df_old, df_new)
    new_del_diff = DiffService.new_deleted_diffs(df_old, df_new)
    general = DiffService.general_diffs(df_old, df_new)

    # 3) SOLO archivo combinado (se eliminan exports individuales)
    export_combined_min(
        path=settings.COMBINED_XLSX_DEFAULT,
        descripcion_df=ld_diff,
        precio_df=price_diff,
        qty_df=qty_diff,
        importe_df=imp_diff,
        altas_bajas_df=new_del_diff,
        resumen_df=general,
    )
    print(f"Informe combinado → {settings.COMBINED_XLSX_DEFAULT.resolve()}")
