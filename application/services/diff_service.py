# application/services/diff_service.py
from __future__ import annotations
from pathlib import Path
from typing import List

import pandas as pd
from bc3_lib import parse_bc3_to_df


class DiffService:
    """
    Servicio de comparación de BC3 que:
     - produce diferencias generales (añadidos, eliminados, modificados)
     - detecta diferencias en 'descripcion_larga'
    """

    _KEY_COLS = ["precio", "cantidad_pres", "descripcion_corta", "unidad"]

    @staticmethod
    def load_dfs(old_path: Path, new_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
        df_old = parse_bc3_to_df(old_path)
        df_new = parse_bc3_to_df(new_path)
        return df_old, df_new

    @staticmethod
    def general_diffs(
        df_old: pd.DataFrame, df_new: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Devuelve un DataFrame con las diferencias de tipo, campo y valores
        (igual al diff previo, pero en DataFrame).
        """
        o = df_old.set_index("codigo").sort_index()
        n = df_new.set_index("codigo").sort_index()

        rows: list[dict] = []
        added = n.index.difference(o.index)
        removed = o.index.difference(n.index)
        for code in added:
            rows.append({"codigo": code, "cambio": "añadido", "campo": "", "antes": "", "despues": ""})
        for code in removed:
            rows.append({"codigo": code, "cambio": "eliminado", "campo": "", "antes": "", "despues": ""})

        common = o.index.intersection(n.index)
        for col in DiffService._KEY_COLS:
            mask = o.loc[common, col] != n.loc[common, col]
            for code in mask[mask].index:
                rows.append({
                    "codigo": code,
                    "cambio": "modificado",
                    "campo": col,
                    "antes": o.at[code, col],
                    "despues": n.at[code, col],
                })
        return pd.DataFrame(rows)

    @staticmethod
    def long_desc_diffs(
        df_old: pd.DataFrame, df_new: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Devuelve un DataFrame con los códigos comunes cuya
        descripcion_larga difiere.
        """
        o = df_old.set_index("codigo")
        n = df_new.set_index("codigo")
        common = o.index.intersection(n.index)
        mask = o.loc[common, "descripcion_larga"] != n.loc[common, "descripcion_larga"]

        rows = []
        for code in common[mask]:
            rows.append({
                "codigo": code,
                "descripcion_larga_old": o.at[code, "descripcion_larga"],
                "descripcion_larga_new": n.at[code, "descripcion_larga"],
            })
        return pd.DataFrame(rows)
