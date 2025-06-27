# infrastructure/exporters/excel_exporter.py
from __future__ import annotations
from pathlib import Path
import difflib
import pandas as pd
import xlsxwriter


def _rich_diff(old: str, new: str, bold_red):
    """
    Construye la lista [txt|fmt, txt|fmt, …] requerida por write_rich_string,
    garantizando: al menos 3 elementos y que primero/último sean texto.
    """
    sm = difflib.SequenceMatcher(None, old or "", new or "")
    parts: list = []

    for op, _i1, _i2, j1, j2 in sm.get_opcodes():
        chunk = new[j1:j2]
        if not chunk:
            continue
        if op == "equal":
            parts.append(chunk)
        else:                          # insert / replace / delete
            parts.extend([bold_red, chunk])

    # ---- asegurar formato válido para write_rich_string ---------------
    if not parts:                      # texto idéntico
        return [new]

    if isinstance(parts[0], xlsxwriter.format.Format):
        parts.insert(0, "")
    if isinstance(parts[-1], xlsxwriter.format.Format):
        parts.append("")

    # write_rich_string necesita ≥3 args (fmt,string,fmt,string,...,string)
    if len(parts) < 3:
        return [new]

    return parts


def export_long_desc_excel(df: pd.DataFrame, path: Path) -> None:
    """
    Exporta *df* a Excel resaltando en rojo+negrita los cambios en
    'descripcion_larga_diff'. Si la columna no existe, guarda sin formato.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="diff", index=False)

        wb  = writer.book
        ws  = writer.sheets["diff"]
        bold_red = wb.add_format({"bold": True, "font_color": "red"})

        if "descripcion_larga_diff" not in df.columns:
            return  # nada que formatear

        diff_col = df.columns.get_loc("descripcion_larga_diff")

        for row_num, (_, r) in enumerate(df.iterrows(), start=1):  # +1 header
            old_long = r["descripcion_larga_old"] or ""
            new_long = r["descripcion_larga_new"] or ""

            # caso: uno de los dos está vacío -> celda entera en rojo bold
            if not old_long.strip() or not new_long.strip():
                ws.write(row_num, diff_col, new_long or old_long, bold_red)
                continue

            # resto de casos -> rich string con partes resaltadas
            rich_parts = _rich_diff(old_long, new_long, bold_red)
            if len(rich_parts) >= 3:
                ws.write_rich_string(row_num, diff_col, *rich_parts)
            else:  # texto idéntico
                ws.write(row_num, diff_col, new_long)

        # wb.close()

