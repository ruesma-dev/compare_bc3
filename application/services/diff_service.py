# application/services/diff_service.py
from __future__ import annotations

from pathlib import Path
from typing import Optional, List

import pandas as pd
from bc3_lib import parse_bc3_to_df


class DiffService:
    _KEY_COLS = ["precio", "cantidad_pres", "descripcion_corta", "unidad"]

    # ---------- leer DataFrames ----------------
    @staticmethod
    def load_dfs(old_path: Path, new_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
        return parse_bc3_to_df(old_path), parse_bc3_to_df(new_path)

    # ---------- diff general (igual que antes) -
    @staticmethod
    def general_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        ...
        # (se mantiene sin cambios)
        ...

    # ---------- diff de descripcion_larga -------
    @staticmethod
    def long_desc_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        """
        Códigos comunes cuya descripcion_larga difiere. Devuelve, además,
        descripcion_corta, precio, cantidad_pres, importe_pres y mediciones
        viejas/nuevas, junto con el padre correspondiente.
        """
        o = df_old.set_index("codigo")
        n = df_new.set_index("codigo")
        common = o.index.intersection(n.index)

        mask = o.loc[common, "descripcion_larga"] != n.loc[common, "descripcion_larga"]

        def _find_parent(index: pd.Index, code: str) -> Optional[str]:
            pref = [c for c in index if c != code and code.startswith(c)]
            return max(pref, key=len) if pref else None

        rows: List[dict] = []
        for code in common[mask]:
            rows.append(
                {
                    "codigo": code,
                    "parent_old": _find_parent(o.index, code) or "",
                    "parent_new": _find_parent(n.index, code) or "",
                    # --- descripciones ---------------------------------
                    "descripcion_corta_old": o.at[code, "descripcion_corta"],
                    "descripcion_corta_new": n.at[code, "descripcion_corta"],
                    "descripcion_larga_old": o.at[code, "descripcion_larga"],
                    "descripcion_larga_new": n.at[code, "descripcion_larga"],
                    # --- numéricos --------------------------------------
                    "precio_old": o.at[code, "precio"],
                    "precio_new": n.at[code, "precio"],
                    "cantidad_pres_old": o.at[code, "cantidad_pres"],
                    "cantidad_pres_new": n.at[code, "cantidad_pres"],
                    "importe_pres_old": o.at[code, "importe_pres"],
                    "importe_pres_new": n.at[code, "importe_pres"],
                    # --- mediciones -------------------------------------
                    "mediciones_old": o.at[code, "mediciones"],
                    "mediciones_new": n.at[code, "mediciones"],
                }
            )
        return pd.DataFrame(rows)
