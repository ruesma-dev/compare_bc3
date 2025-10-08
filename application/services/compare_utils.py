# application/services/compare_utils.py
from __future__ import annotations

from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd


def neq_with_tolerance(
    s_old: pd.Series,
    s_new: pd.Series,
    tol_abs: float | None = None,
    tol_pct: float | None = None,
) -> pd.Series:
    """
    Devuelve una Serie booleana con True cuando s_old != s_new considerando NaN==NaN
    y aplicando tolerancias opcionales (absoluta y/o porcentual) para valores numéricos.

    Reglas:
      - NaN == NaN (no cuenta como cambio)
      - Si no hay tolerancias -> desigualdad NaN-safe
      - tol_abs: |a - b| > tol_abs
      - tol_pct: |a - b| / |a| > tol_pct   (si a==0 -> denominador 1.0 para evitar div/0)
    """
    a = pd.to_numeric(s_old, errors="coerce")
    b = pd.to_numeric(s_new, errors="coerce")

    both_nan = a.isna() & b.isna()
    base_neq = ~(a.eq(b) | both_nan)

    if tol_abs is None and tol_pct is None:
        return base_neq

    diff = (a.fillna(0.0) - b.fillna(0.0)).abs()

    mask = base_neq
    if tol_abs is not None:
        mask &= diff > float(tol_abs)

    if tol_pct is not None:
        denom = a.abs()
        # evita división por cero: si a==0 o NaN, usa 1.0 (equivale a evaluar sólo tol_abs en esos casos)
        denom = denom.where(denom > 0, 1.0)
        pct = diff / denom
        mask &= pct > float(tol_pct)

    return mask


def neq_na_safe(s_old: pd.Series, s_new: pd.Series) -> pd.Series:
    """
    Desigualdad NaN-safe para series NO numéricas (o genéricas):
      - NaN == NaN
      - El resto usa comparación de igualdad de pandas.
    """
    a = s_old
    b = s_new
    both_nan = a.isna() & b.isna()
    return ~(a.eq(b) | both_nan)


def clean_children_field(value: object) -> List[str]:
    """
    Limpia el campo 'hijos':
      - Acepta None/NaN/"" -> []
      - Split por coma
      - strip() por elemento
      - filtra vacíos y literales 'nan' (en minúscula)
      - dedup preservando orden
    """
    if value is None:
        return []
    # Convertimos a str de forma segura y bajamos a minúscula para filtrar 'nan'
    text = str(value)
    if not text or text.lower() == "nan":
        return []

    out: List[str] = []
    seen = set()
    for raw in text.split(","):
        child = raw.strip()
        if not child:
            continue
        if child.lower() == "nan":
            continue
        if child not in seen:
            out.append(child)
            seen.add(child)
    return out
