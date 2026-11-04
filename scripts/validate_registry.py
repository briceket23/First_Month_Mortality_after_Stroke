"""Validate a registry workbook against the declared schema and dictionary WITHOUT running the analysis.
Usage: STROKE_DATA_PATH=... python scripts/validate_registry.py   (or STROKE_SYNTHETIC=1)
Prints: sheet names, shape, required columns present/missing, identifier duplicates (aggregate), date cell types, dictionary coverage."""
import json, sys
from collections import Counter
from pathlib import Path
import openpyxl, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from stroke_repro import config as C
from stroke_repro.ingest import load_raw, RAW_FIELDS
from stroke_repro.schema_validation import validate_columns

raw = load_raw(); missing, shape_bad = validate_columns(raw)
wb = openpyxl.load_workbook(C.RAW_XLSX, read_only=True); ws = wb[wb.sheetnames[0]]
hdr = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
types = Counter()
for row in ws.iter_rows(min_row=2, max_row=min(ws.max_row, 5000)):
    for nm in ("Date of entry", "Release date"):
        if nm in hdr:
            types[f"{nm}:{type(row[hdr.index(nm)].value).__name__}"] += 1
uc = raw["unique_code"]; vc = uc.value_counts()
dd = C.load_dictionary()
norm = lambda s: " ".join(str(s).split()).strip().lower(); wl = {norm(c) for c in raw.columns}
res = {"workbook": str(C.RAW_XLSX), "synthetic": C.SYNTHETIC, "sheets": wb.sheetnames, "rows": int(len(raw)), "columns": int(raw.shape[1] - 2),
       "required_columns_missing": missing, "shape_matches_declared": not shape_bad, "identifier_groups_repeated": int((vc > 1).sum()),
       "identifier_excess_rows": int((vc[vc > 1] - 1).sum()), "date_cell_types": dict(types),
       "dictionary_file": C.DICT_XLSX.name, "dictionary_labels_matched": int(sum(norm(l) in wl for l in dd.label)), "dictionary_variables": int(len(dd))}
print(json.dumps(res, indent=1)); sys.exit(1 if missing else 0)
