# application/services/diff_service.py
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import pandas as pd
from bc3_lib import parse_bc3_to_df


class DiffService:
    """
    Casos de uso de comparación entre dos presupuestos BC3 expresados
    como DataFrames.
    """

    _KEY_COLS = ["precio", "cantidad_pres", "descripcion_corta", "unidad"]

    # ───────────────────────────── LOAD ────────────────────────────────
    @staticmethod
    def load_dfs(old_path: Path, new_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Devuelve los DataFrames generados por bc3_lib.parse_bc3_to_df
        a partir de los dos ficheros BC3.
        """
        return parse_bc3_to_df(old_path), parse_bc3_to_df(new_path)

    # ────────────────────────── PARENT MAP ─────────────────────────────
    @staticmethod
    def _build_parent_map(df: pd.DataFrame) -> dict[str, str]:
        """
        Construye un diccionario {hijo: padre} utilizando la columna
        'hijos' (códigos separados por coma) de cada fila.
        """
        mapping: dict[str, str] = {}
        for _, row in df.iterrows():
            parent = row["codigo"]
            children = str(row.get("hijos", "")).split(",") if row.get("hijos") else []
            for child in (c.strip() for c in children):
                if child and child not in mapping:
                    mapping[child] = parent
        return mapping

    @staticmethod
    def _ancestor_chain(code: str, parent_map: dict[str, str], index: pd.Index) -> str:
        """
        Devuelve una cadena 'CAP# > SUB# > … > PADRE' recorriendo hacia
        arriba con parent_map hasta encontrar un nodo cuyo tipo sea
        'capitulo' o no tenga más padre.
        """
        chain: List[str] = []
        cur = parent_map.get(code)
        while cur:
            chain.append(cur)
            # Si sabemos el tipo y es capitulo → parar
            # (index puede ser MultiIndex con nivel 'tipo'; si no, omitimos)
            cur = parent_map.get(cur)
        return " > ".join(reversed(chain))

    # ─────────────────────— GENERAL DIFFS ──────────────────────────────
    @staticmethod
    def general_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        """
        Añadidos, eliminados y modificados en las columnas clave.
        """
        o = df_old.set_index("codigo")
        n = df_new.set_index("codigo")

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

    # ──────────────── GENERIC COLUMN DIFF HELPER ───────────────────────
    @staticmethod
    def column_diff(
        df_old: pd.DataFrame,
        df_new: pd.DataFrame,
        column: str,
        parent_map_old: dict[str, str],
        parent_map_new: dict[str, str],
    ) -> pd.DataFrame:
        """
        Genera un diff para *column* devolviendo los valores old/new y la
        cadena ascendente de padres (ancestors_*).
        """
        o = df_old.set_index("codigo")
        n = df_new.set_index("codigo")

        common = o.index.intersection(n.index)
        mask = o.loc[common, column] != n.loc[common, column]

        rows: list[dict] = []
        for code in common[mask]:
            rows.append(
                {
                    "codigo": code,
                    "ancestors_old": DiffService._ancestor_chain(code, parent_map_old, o.index),
                    "ancestors_new": DiffService._ancestor_chain(code, parent_map_new, n.index),
                    f"{column}_old": o.at[code, column],
                    f"{column}_new": n.at[code, column],
                    "descripcion_corta": n.at[code, "descripcion_corta"],
                }
            )
        return pd.DataFrame(rows)

    # ──────────────── SHORTCUTS POR COLUMNA ────────────────────────────
    @staticmethod
    def price_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        p_old = DiffService._build_parent_map(df_old)
        p_new = DiffService._build_parent_map(df_new)
        return DiffService.column_diff(df_old, df_new, "precio", p_old, p_new)

    @staticmethod
    def qty_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        p_old = DiffService._build_parent_map(df_old)
        p_new = DiffService._build_parent_map(df_new)
        return DiffService.column_diff(df_old, df_new, "cantidad_pres", p_old, p_new)

    @staticmethod
    def importe_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        p_old = DiffService._build_parent_map(df_old)
        p_new = DiffService._build_parent_map(df_new)
        return DiffService.column_diff(df_old, df_new, "importe_pres", p_old, p_new)

    # ──────────────── DESCRIPCION_LARGA DIFF ───────────────────────────
    @staticmethod
    def long_desc_diffs(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
        """
        Códigos comunes cuya descripcion_larga difiere.
        Incluye descripción corta, precio, cantidad, importe, mediciones y
        la cadena de ancestros completa.
        """
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
