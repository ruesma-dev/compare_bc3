# infrastructure/exporters/excel_workbook_combined_min.py
from __future__ import annotations
# infrastructure/exporters/excel_workbook_combined_min.py
from pathlib import Path
from typing import List, Optional, Iterable, Set

import difflib
import pandas as pd
import xlsxwriter


def _rich_diff(old: str, new: str, bold_red):
    """
    MISMO algoritmo que el original (no modificado).
    Construye la lista [txt|fmt, txt|fmt, …] requerida por write_rich_string.
    """
    sm = difflib.SequenceMatcher(None, old or "", new or "")
    parts: list = []
    for op, _i1, _i2, j1, j2 in sm.get_opcodes():
        chunk = new[j1:j2]
        if not chunk:
            continue
        if op == "equal":
            parts.append(chunk)
        else:  # insert / replace / delete
            parts.extend([bold_red, chunk])

    if not parts:  # texto idéntico
        return [new]
    if isinstance(parts[0], xlsxwriter.format.Format):
        parts.insert(0, "")
    if isinstance(parts[-1], xlsxwriter.format.Format):
        parts.append("")
    if len(parts) < 3:
        return [new]
    return parts


def _autofit_widths(df: pd.DataFrame, max_width_chars: int = 60) -> List[int]:
    """
    Calcula un ancho aproximado por columna en 'caracteres' (unidades Excel).
    Limita por 'max_width_chars'. Añade margen +2.
    """
    widths: List[int] = []
    header_lens = [len(str(c)) for c in df.columns.to_list()]

    for idx, col in enumerate(df.columns):
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            widths.append(min(max(header_lens[idx] + 2, 12), max_width_chars))
            continue
        try:
            max_len = series.astype(str).str.len().max()  # type: ignore
            if pd.isna(max_len):
                max_len = header_lens[idx]
        except Exception:
            max_len = header_lens[idx]
        width = int(min(max(max_len + 2, header_lens[idx] + 2), max_width_chars))
        widths.append(width)
    return widths


def _apply_autofit_except(
    ws: xlsxwriter.worksheet.Worksheet,
    df: pd.DataFrame,
    wb: xlsxwriter.Workbook,
    exclude_cols: Optional[Set[int]] = None,
    wrap_columns: Optional[Iterable[str]] = None,
    max_width_chars: int = 60,
) -> None:
    """
    Auto-ajusta columnas excepto las indicadas en exclude_cols (índices).
    - wrap_columns: nombres de columnas (case-insensitive) a las que aplicar 'Ajustar texto'.
    - max_width_chars: límite superior del auto-ajuste (en unidades de Excel).
    """
    widths = _autofit_widths(df, max_width_chars=max_width_chars)
    fmt_wrap = wb.add_format({"text_wrap": True, "valign": "top"})
    fmt_default = wb.add_format({"valign": "top"})

    wrap_set: Set[str] = {c.lower() for c in (wrap_columns or [])}
    exclude_cols = exclude_cols or set()

    for j, col in enumerate(df.columns):
        if j in exclude_cols:
            continue
        col_l = str(col).lower()
        use_fmt = fmt_wrap if col_l in wrap_set else fmt_default
        ws.set_column(j, j, widths[j], use_fmt)


def _chars_from_pixels(pixels: int) -> float:
    """
    Conversión aproximada de píxeles a 'ancho de columna' de Excel (caracteres).
    Excel limita a 255 caracteres (~ 1725–1800 px según fuente).
    Aproximación estándar: 1 carácter ≈ 7 px y un offset ≈ 5 px.
    """
    if pixels <= 0:
        return 0.0
    # inversa aproximada de: pixels ≈ trunc((256*width + 128/7)/256)*7 + 5
    # usamos la aproximación continua:
    width = (pixels - 5) / 7.0
    return max(0.0, width)


def export_combined_min(
    path: Path,
    descripcion_df: pd.DataFrame,
    precio_df: pd.DataFrame,
    qty_df: pd.DataFrame,
    importe_df: pd.DataFrame,
    altas_bajas_df: pd.DataFrame,
    resumen_df: pd.DataFrame,
) -> None:
    """
    Genera un único .xlsx con hojas:
      - 00_Resumen_cambios
      - 01_Descripcion   (con el mismo resaltado rojo de siempre)
      - 02_Precio
      - 03_Medicion
      - 04_Importe
      - 05_Altas_Bajas
    En 01_Descripcion la columna 'descripcion_larga_diff' fija primero
    un ancho equivalente a ~1790 px (capado al máximo de Excel) y DESPUÉS
    activa 'Ajustar texto', para minimizar la altura de filas.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        # 00 - Resumen
        resumen_df.to_excel(writer, sheet_name="00_Resumen_cambios", index=False)
        wb = writer.book
        ws = writer.sheets["00_Resumen_cambios"]
        ws.freeze_panes(1, 0)
        _apply_autofit_except(ws, resumen_df, wb)

        # 01 - Descripcion (con rich string original)
        descripcion_df.to_excel(writer, sheet_name="01_Descripcion", index=False)
        ws = writer.sheets["01_Descripcion"]
        ws.freeze_panes(1, 0)

        # --- Ajuste especial para la columna de diferencias ---
        diff_col_idx: Optional[int] = None
        if "descripcion_larga_diff" in descripcion_df.columns:
            diff_col_idx = descripcion_df.columns.get_loc("descripcion_larga_diff")

            # 1) Fijar ancho 'máximo' solicitado (~1790 px) ANTES del wrap
            desired_pixels = 1790
            # convertir a unidades de Excel y capar a 255 (límite de Excel)
            width_chars = min(255.0, _chars_from_pixels(desired_pixels))
            # formato con wrap (se aplicará ahora, tras fijar ancho)
            fmt_wrap = wb.add_format({"text_wrap": True, "valign": "top"})
            ws.set_column(diff_col_idx, diff_col_idx, width_chars, fmt_wrap)

        # 2) Auto-ajustar el resto de columnas (sin tocar la diff)
        exclude = {diff_col_idx} if diff_col_idx is not None else set()
        _apply_autofit_except(ws, descripcion_df, wb, exclude_cols=exclude)

        # 3) Escribir el rich text (marcado rojo) SIN cambios
        bold_red = wb.add_format({"bold": True, "font_color": "red"})
        if diff_col_idx is not None:
            for row_num, (_, r) in enumerate(descripcion_df.iterrows(), start=1):
                old_long = r["descripcion_larga_old"] or ""
                new_long = r["descripcion_larga_new"] or ""

                if not str(old_long).strip() or not str(new_long).strip():
                    ws.write(row_num, diff_col_idx, new_long or old_long, bold_red)
                    continue

                parts = _rich_diff(str(old_long), str(new_long), bold_red)
                if len(parts) >= 3:
                    ws.write_rich_string(row_num, diff_col_idx, *parts)
                else:
                    ws.write(row_num, diff_col_idx, str(new_long))

        # 02..05 - resto
        precio_df.to_excel(writer, sheet_name="02_Precio", index=False)
        ws = writer.sheets["02_Precio"]
        ws.freeze_panes(1, 0)
        _apply_autofit_except(ws, precio_df, wb)

        qty_df.to_excel(writer, sheet_name="03_Medicion", index=False)
        ws = writer.sheets["03_Medicion"]
        ws.freeze_panes(1, 0)
        _apply_autofit_except(ws, qty_df, wb)

        importe_df.to_excel(writer, sheet_name="04_Importe", index=False)
        ws = writer.sheets["04_Importe"]
        ws.freeze_panes(1, 0)
        _apply_autofit_except(ws, importe_df, wb)

        altas_bajas_df.to_excel(writer, sheet_name="05_Altas_Bajas", index=False)
        ws = writer.sheets["05_Altas_Bajas"]
        ws.freeze_panes(1, 0)
        _apply_autofit_except(ws, altas_bajas_df, wb)
