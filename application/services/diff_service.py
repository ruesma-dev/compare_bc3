# application/services/diff_service.py
from __future__ import annotations

from pathlib import Path
from typing import List, Dict
import difflib

import pandas as pd
from bc3_lib import parse_bc3_to_df


class DiffService:
    """Casos de uso de comparación entre dos DataFrames BC3."""

    _KEY_COLS = ["precio", "cantidad_pres", "descripcion_corta", "unidad"]

    # ───────────────────── cargar DataFrames ────────────────────────────
    @staticmethod
    def load_dfs(old_path: Path, new_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
        return parse_bc3_to_df(old_path), parse_bc3_to_df(new_path)

    # ───────────────────── helpers de jerarquía ─────────────────────────
    @staticmethod
    def _build_parent_map(df: pd.DataFrame) -> Dict[str, str]:
        """Construye {hijo: padre} usando la columna 'hijos'."""
        mapping: Dict[str, str] = {}
        for _, row in df.iterrows():
            parent = row["codigo"]
            for child in str(row.get("hijos", "")).split(","):
                child = child.strip()
                if child and child not in mapping:
                    mapping[child] = parent
        return mapping

    @staticmethod
    def _ancestor_chain(code: str, parent_map: Dict[str, str], _index: pd.Index) -> str:
        """Devuelve 'CAP# > SUB# > … > PADRE' (hasta que no haya más padre)."""
        chain: List[str] = []
        cur = parent_map.get(code)
        while cur:
            chain.append(cur)
            cur = parent_map.get(cur)
        return " > ".join(reversed(chain))

    # ───────────────────── cambios generales (opcional) ────────────────
    @staticmethod
    def general_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        o, n = df_old.set_index("codigo"), df_new.set_index("codigo")
        rows: list[dict] = []

        added = n.index.difference(o.index)
        removed = o.index.difference(n.index)
        rows += [{"codigo": c, "cambio": "nuevo"} for c in added]
        rows += [{"codigo": c, "cambio": "eliminado"} for c in removed]

        common = o.index.intersection(n.index)
        for col in DiffService._KEY_COLS:
            mask = o.loc[common, col] != n.loc[common, col]
            for code in mask[mask].index:
                rows.append(
                    {
                        "codigo": code,
                        "cambio": "modificado",
                        "campo": col,
                        "antes": o.at[code, col],
                        "despues": n.at[code, col],
                    }
                )
        return pd.DataFrame(rows)

    # ───────────────────── columna genérica diff ───────────────────────
    @staticmethod
    def _column_diff(
        df_old: pd.DataFrame,
        df_new: pd.DataFrame,
        column: str,
        p_old: Dict[str, str],
        p_new: Dict[str, str],
    ) -> pd.DataFrame:
        o, n = df_old.set_index("codigo"), df_new.set_index("codigo")
        common = o.index.intersection(n.index)
        mask = o.loc[common, column] != n.loc[common, column]

        rows: list[dict] = []
        for code in common[mask]:
            rows.append(
                {
                    "codigo": code,
                    "ancestors_old": DiffService._ancestor_chain(code, p_old, o.index),
                    "ancestors_new": DiffService._ancestor_chain(code, p_new, n.index),
                    f"{column}_old": o.at[code, column],
                    f"{column}_new": n.at[code, column],
                    "descripcion_corta": n.at[code, "descripcion_corta"],
                }
            )
        return pd.DataFrame(rows)

    # ───────────────────── diffs específicos ────────────────────────────
    @staticmethod
    def price_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        p_old, p_new = DiffService._build_parent_map(df_old), DiffService._build_parent_map(df_new)
        return DiffService._column_diff(df_old, df_new, "precio", p_old, p_new)

    @staticmethod
    def qty_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        p_old, p_new = DiffService._build_parent_map(df_old), DiffService._build_parent_map(df_new)
        return DiffService._column_diff(df_old, df_new, "cantidad_pres", p_old, p_new)

    @staticmethod
    def importe_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        p_old, p_new = DiffService._build_parent_map(df_old), DiffService._build_parent_map(df_new)
        return DiffService._column_diff(df_old, df_new, "importe_pres", p_old, p_new)

    # ──────────────────── nuevos y eliminados ───────────────────────────
    @staticmethod
    def new_deleted_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        """
        Informe unificado de códigos NUEVOS y ELIMINADOS con:
            codigo · estado · ancestors_* · descripcion_corta_* · descripcion_larga_*
        """
        o = df_old.set_index("codigo")
        n = df_new.set_index("codigo")

        p_old = DiffService._build_parent_map(df_old)
        p_new = DiffService._build_parent_map(df_new)

        added = n.index.difference(o.index)
        removed = o.index.difference(n.index)

        rows: list[dict] = []

        # NUEVOS ---------------------------------------------------------
        for code in added:
            rows.append(
                {
                    "codigo": code,
                    "estado": "nuevo",
                    "ancestors_old": "",
                    "ancestors_new": DiffService._ancestor_chain(code, p_new, n.index),
                    "descripcion_corta_old": "",
                    "descripcion_corta_new": n.at[code, "descripcion_corta"],
                    "descripcion_larga_old": "",
                    "descripcion_larga_new": n.at[code, "descripcion_larga"],
                }
            )

        # ELIMINADOS -----------------------------------------------------
        for code in removed:
            rows.append(
                {
                    "codigo": code,
                    "estado": "eliminado",
                    "ancestors_old": DiffService._ancestor_chain(code, p_old, o.index),
                    "ancestors_new": "",
                    "descripcion_corta_old": o.at[code, "descripcion_corta"],
                    "descripcion_corta_new": "",
                    "descripcion_larga_old": o.at[code, "descripcion_larga"],
                    "descripcion_larga_new": "",
                }
            )

        return pd.DataFrame(
            rows,
            columns=[
                "codigo",
                "estado",
                "ancestors_old",
                "ancestors_new",
                "descripcion_corta_old",
                "descripcion_corta_new",
                "descripcion_larga_old",
                "descripcion_larga_new",
            ],
        )

    # ───────── helper para resaltar diferencias en línea ────────────────

    @staticmethod
    def _highlight_diff(old: str, new: str) -> str:
        """
        Devuelve *new* con los fragmentos que no coinciden con *old*
        envueltos en **doble asterisco** (Markdown bold).
        """
        sm = difflib.SequenceMatcher(None, old or "", new or "")
        out: list[str] = []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal":
                out.append(new[j1:j2])
            else:                          # replace / insert / delete
                out.append(f"**{new[j1:j2]}**")
        return "".join(out)

    # ─────────────── descripcion_larga diff  ────────────────────────
    @staticmethod
    def long_desc_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        o, n = df_old.set_index("codigo"), df_new.set_index("codigo")
        p_old, p_new = DiffService._build_parent_map(df_old), DiffService._build_parent_map(df_new)

        common = o.index.intersection(n.index)
        mask = o.loc[common, "descripcion_larga"] != n.loc[common, "descripcion_larga"]

        rows: List[dict] = []
        for code in common[mask]:
            old_long = o.at[code, "descripcion_larga"]
            new_long = n.at[code, "descripcion_larga"]

            rows.append(
                {
                    "codigo": code,
                    "ancestors_old": DiffService._ancestor_chain(code, p_old, o.index),
                    "ancestors_new": DiffService._ancestor_chain(code, p_new, n.index),
                    "descripcion_corta_old": o.at[code, "descripcion_corta"],
                    "descripcion_corta_new": n.at[code, "descripcion_corta"],
                    "descripcion_larga_old": old_long,
                    "descripcion_larga_new": new_long,
                    "descripcion_larga_diff": DiffService._highlight_diff(old_long, new_long),
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

        return pd.DataFrame(
            rows,
            columns=[
                "codigo",
                "ancestors_old",
                "ancestors_new",
                "descripcion_corta_old",
                "descripcion_corta_new",
                "descripcion_larga_old",
                "descripcion_larga_new",
                "descripcion_larga_diff",   # ← nueva columna
                "precio_old",
                "precio_new",
                "cantidad_pres_old",
                "cantidad_pres_new",
                "importe_pres_old",
                "importe_pres_new",
                "mediciones_old",
                "mediciones_new",
            ],
        )

