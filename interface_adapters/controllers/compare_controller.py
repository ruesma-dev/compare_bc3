# interface_adapters/controllers/compare_controller.py
from pathlib import Path

from application.services.diff_service import DiffService
from infrastructure.exporters.df_exporter import export_df
from infrastructure.exporters.excel_df_exporter import export_df_excel
from infrastructure.exporters.excel_exporter import export_long_desc_excel
from config import settings


def run(old_bc3: Path, new_bc3: Path) -> None:
    # 1) DataFrames completos -------------------------------------------------
    df_old, df_new = DiffService.load_dfs(old_bc3, new_bc3)

    export_df(df_old, settings.OLD_DF_CSV_DEFAULT)
    export_df_excel(df_old, settings.OLD_DF_XLSX_DEFAULT)

    export_df(df_new, settings.NEW_DF_CSV_DEFAULT)
    export_df_excel(df_new, settings.NEW_DF_XLSX_DEFAULT)

    # 2) descripción larga ----------------------------------------------------
    ld_diff = DiffService.long_desc_diffs(df_old, df_new)
    export_df(ld_diff, settings.LONG_DESC_DIFF_CSV_DEFAULT)
    export_long_desc_excel(ld_diff, settings.LONG_DESC_DIFF_XLSX_DEFAULT)

    # 3) precio ----------------------------------------------------------------
    price_diff = DiffService.price_diffs(df_old, df_new)
    export_df(price_diff, settings.PRICE_DIFF_CSV_DEFAULT)
    export_df_excel(price_diff, settings.PRICE_DIFF_XLSX_DEFAULT)

    # 4) cantidad_pres ---------------------------------------------------------
    qty_diff = DiffService.qty_diffs(df_old, df_new)
    export_df(qty_diff, settings.QTY_DIFF_CSV_DEFAULT)
    export_df_excel(qty_diff, settings.QTY_DIFF_XLSX_DEFAULT)

    # 5) importe_pres ----------------------------------------------------------
    imp_diff = DiffService.importe_diffs(df_old, df_new)
    export_df(imp_diff, settings.IMP_DIFF_CSV_DEFAULT)
    export_df_excel(imp_diff, settings.IMP_DIFF_XLSX_DEFAULT)

    # 6) nuevos / eliminados ---------------------------------------------------
    new_del_diff = DiffService.new_deleted_diffs(df_old, df_new)
    export_df(new_del_diff, settings.NEW_DEL_DIFF_CSV_DEFAULT)
    export_df_excel(new_del_diff, settings.NEW_DEL_DIFF_XLSX_DEFAULT)

    print("Todos los CSV y XLSX se han generado en la carpeta 'output/'.")
