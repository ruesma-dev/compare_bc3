# application/services/diff_service.py
from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd
from bc3_lib import parse_bc3_to_df


class DiffService:
    _KEY_COLS = ["precio", "cantidad_pres", "descripcion_corta", "unidad"]

    # ───── helpers ───────────────────────────────────────────────────────
    @staticmethod
    def _build_parent_map(df: pd.DataFrame) -> dict[str, str]:
        """Devuelve {hijo: padre} usando la columna 'hijos'."""
        mapping: dict[str, str] = {}
        for _, row in df.iterrows():
            parent = row["codigo"]
            for child in str(row.get("hijos", "")).split(","):
                child = child.strip()
                if child and child not in mapping:
                    mapping[child] = parent
        return mapping

    @staticmethod
    def _ancestor_chain(
        code: str,
        parent_map: dict[str, str],
        df_index: pd.Index,
    ) -> str:
        """
        Devuelve la cadena 'CAP# > SUB# > … > PADRE' hasta llegar a un nodo
        cuyo 'tipo' sea 'capitulo' o no tenga más padre.
        """
        chain: List[str] = []
        cur = parent_map.get(code)
        while cur:
            chain.append(cur)
            # detenerse si el padre es un capítulo
            # (suponemos df tiene índice completo y columna 'tipo')
            tipo = df_index.get_level_values(0).to_series().get(cur, "")
            if tipo == "capitulo":
                break
            cur = parent_map.get(cur)
        return " > ".join(reversed(chain))  # del cap. al inmediato

    # ───── API pública ──────────────────────────────────────────────────
    @staticmethod
    def load_dfs(old_path: Path, new_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
        return parse_bc3_to_df(old_path), parse_bc3_to_df(new_path)

    @staticmethod
    def general_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        # … sin cambios …
        ...

    @staticmethod
    def long_desc_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        """Igual que antes, pero añade ancestros completos hasta capítulo."""
        o = df_old.set_index("codigo")
        n = df_new.set_index("codigo")

        p_old = DiffService._build_parent_map(df_old)
        p_new = DiffService._build_parent_map(df_new)

        common = o.index.intersection(n.index)
        mask = o.loc[common, "descripcion_larga"] != n.loc[common, "descripcion_larga"]

        rows: List[dict] = []
        for code in common[mask]:
            rows.append(
                {
                    "codigo": code,
                    "ancestors_old": DiffService._ancestor_chain(code, p_old, o.index),
                    "ancestors_new": DiffService._ancestor_chain(code, p_new, n.index),
                    "descripcion_corta_old": o.at[code, "descripcion_corta"],
                    "descripcion_corta_new": n.at[code, "descripcion_corta"],
                    "descripcion_larga_old": o.at[code, "descripcion_larga"],
                    "descripcion_larga_new": n.at[code, "descripcion_larga"],
                    "precio_old": o.at[code, "precio"],
                    "precio_new": n.at[code, "precio"],
                    "cantidad_pres_old": o.at[code, "cantidad_pres"],
                    "cantidad_pres_new": n.at[code, "cantidad_pres"],
                    "importe_pres_old": o.at[code, "importe_pres"],
                    "importe_pres_new": n.at[code, "importe_pres"],
                    "mediciones_old": o.at[code, "mediciones"],
                    "mediciones_new": n.at[code, "mediciones"],
                }
            )
        return pd.DataFrame(rows)
