# interface_adapters/controllers/compare_controller.py
from pathlib import Path

from application.services.diff_service import DiffService
from infrastructure.exporters.df_exporter import export_df
from config import settings


def run(old_bc3: Path, new_bc3: Path) -> None:
    # ── 1) Cargar DataFrames completos ─────────────────────────────────
    df_old, df_new = DiffService.load_dfs(old_bc3, new_bc3)

    print("=== PRESUPUESTO 1 (DataFrame) ===")
    print(df_old)
    print("\n=== PRESUPUESTO 2 (DataFrame) ===")
    print(df_new)

    export_df(df_old, settings.OLD_DF_CSV_DEFAULT)
    export_df(df_new, settings.NEW_DF_CSV_DEFAULT)
    print(f"DataFrames exportados a {settings.OLD_DF_CSV_DEFAULT} y {settings.NEW_DF_CSV_DEFAULT}")

    # ── 2) Diferencias en DESCRIPCION_LARGA ────────────────────────────
    ld_diff = DiffService.long_desc_diffs(df_old, df_new)
    print("\n=== DIFERENCIAS: descripcion_larga ===")
    print(ld_diff)
    export_df(ld_diff, settings.LONG_DESC_DIFF_CSV_DEFAULT)

    # ── 3) Diferencias en PRECIO ───────────────────────────────────────
    price_diff = DiffService.price_diffs(df_old, df_new)
    print("\n=== DIFERENCIAS: precio ===")
    print(price_diff)
    export_df(price_diff, settings.PRICE_DIFF_CSV_DEFAULT)

    # ── 4) Diferencias en CANTIDAD_PRES ────────────────────────────────
    qty_diff = DiffService.qty_diffs(df_old, df_new)
    print("\n=== DIFERENCIAS: cantidad_pres ===")
    print(qty_diff)
    export_df(qty_diff, settings.QTY_DIFF_CSV_DEFAULT)

    # ── 5) Diferencias en IMPORTE_PRES ─────────────────────────────────
    imp_diff = DiffService.importe_diffs(df_old, df_new)
    print("\n=== DIFERENCIAS: importe_pres ===")
    print(imp_diff)
    export_df(imp_diff, settings.IMP_DIFF_CSV_DEFAULT)

    print("\nTodos los informes se han generado en la carpeta 'output/'.")
