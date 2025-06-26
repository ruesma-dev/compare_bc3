# interface_adapters/controllers/compare_controller.py
from pathlib import Path
from application.services.diff_service import DiffService
from infrastructure.exporters.df_exporter import export_df
from config import settings


def run(old_bc3: Path, new_bc3: Path) -> None:
    df_old, df_new = DiffService.load_dfs(old_bc3, new_bc3)

    # DataFrames completos -------------------------------------------------
    export_df(df_old, settings.OLD_DF_CSV_DEFAULT)
    export_df(df_new, settings.NEW_DF_CSV_DEFAULT)

    # descripcion_larga diff ----------------------------------------------
    export_df(
        DiffService.long_desc_diffs(df_old, df_new),
        settings.LONG_DESC_DIFF_CSV_DEFAULT,
    )

    # precio diff ----------------------------------------------------------
    export_df(
        DiffService.price_diffs(df_old, df_new),
        settings.PRICE_DIFF_CSV_DEFAULT,
    )

    # cantidad diff --------------------------------------------------------
    export_df(
        DiffService.qty_diffs(df_old, df_new),
        settings.QTY_DIFF_CSV_DEFAULT,
    )

    # importe diff ---------------------------------------------------------
    export_df(
        DiffService.importe_diffs(df_old, df_new),
        settings.IMP_DIFF_CSV_DEFAULT,
    )

    # nuevos / eliminados --------------------------------------------------
    export_df(
        DiffService.new_deleted_diffs(df_old, df_new),
        settings.NEW_DEL_DIFF_CSV_DEFAULT,
    )

    print("Informes generados en carpeta 'output/'.")
