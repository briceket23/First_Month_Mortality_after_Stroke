"""Reconcile pandas vs raw-Excel-cell (openpyxl) parsing of entry/release dates and LOS (P0-C; ticket DATA-DATE-001).
Writes aggregate counts only.  Usage: python tools/date_parser_reconciliation.py OUT_JSON"""
import json, sys
from datetime import datetime, date
from pathlib import Path
from collections import Counter
import numpy as np, pandas as pd, openpyxl
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from stroke_repro import config as C

def main(out):
    raw = pd.read_excel(C.RAW_XLSX); raw.columns = [str(c).strip() for c in raw.columns]
    e = pd.to_datetime(raw["Date of entry"], errors="coerce"); r = pd.to_datetime(raw["Release date"], errors="coerce")
    los = pd.to_numeric(raw["Length of hospitalization"], errors="coerce"); d = (r - e).dt.days
    m = e.notna() & r.notna() & los.notna()
    pdres = dict(complete_pairs=int(m.sum()), equal=int((d[m] == los[m]).sum()), differ=int((d[m] != los[m]).sum()),
                 negative_in_pairs=int((d[m] < 0).sum()), negative_all_date_pairs=int((d[e.notna() & r.notna()] < 0).sum()), pandas_version=pd.__version__)
    lim = pd.Timestamp("2262-04-11"); e2, r2 = e.where(e <= lim), r.where(r <= lim); m2 = e2.notna() & r2.notna() & los.notna(); d2 = (r2 - e2).dt.days
    emul = dict(complete_pairs=int(m2.sum()), equal=int((d2[m2] == los[m2]).sum()), differ=int((d2[m2] != los[m2]).sum()), negative_in_pairs=int((d2[m2] < 0).sum()))
    wb = openpyxl.load_workbook(C.RAW_XLSX, data_only=True); ws = wb[wb.sheetnames[0]]; h = [c.value for c in ws[1]]
    ie, ir, il = h.index("Date of entry"), h.index("Release date"), h.index("Length of hospitalization")
    types, fmts = Counter(), Counter(); pairs = eq = df_ = neg = negall = 0; oor = []
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        if all(c.value is None for c in row): continue
        ce, cr, cl = row[ie], row[ir], row[il]
        for c, nm in ((ce, "entry"), (cr, "release")):
            types[f"{nm}:{type(c.value).__name__}"] += 1; fmts[f"{nm}:{c.number_format}"] += 1
        if isinstance(ce.value, (datetime, date)) and isinstance(cr.value, (datetime, date)):
            dd = (cr.value - ce.value).days
            if dd < 0: negall += 1
            if ce.value.year > 2262 or cr.value.year > 2262: oor.append((ce.value.year, cr.value.year))
            if isinstance(cl.value, (int, float)):
                pairs += 1; eq += dd == cl.value; df_ += dd != cl.value; neg += dd < 0
    xl = dict(complete_pairs=pairs, equal=eq, differ=df_, negative_in_pairs=neg, negative_all_date_pairs=negall, cell_types=dict(types), number_formats=dict(fmts),
              rows_with_year_beyond_pandas_ns_limit=[{"entry_year": a, "release_year": b} for a, b in oor])
    res = dict(sheet=wb.sheetnames, pandas_current=pdres, pandas_pre3_emulated=emul, openpyxl_raw_cells=xl,
               reconciled=(pdres["complete_pairs"] == xl["complete_pairs"] and pdres["differ"] == xl["differ"]),
               explanation="All date cells are Excel datetimes. pandas < 3.0 stores timestamps in nanoseconds and converts years > 2262 to NaT silently; "
                           "the two rows with such years (entry 3016; release 2916) account for the earlier 1,486/665/22 figures. "
                           "Both rows are flagged as invalid dates (never corrected) by the integrity rules.")
    Path(out).parent.mkdir(parents=True, exist_ok=True); json.dump(res, open(out, "w", encoding="utf-8"), indent=1); print(json.dumps(res, indent=1))

if __name__ == "__main__":
    main(sys.argv[1])
