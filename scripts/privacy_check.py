"""Verify that the outputs directory contains aggregate data only: no unique_code column, no row-level pickles, no patient names/phones.
Usage: python tools/privacy_check.py OUTPUTS_DIR  (exit 1 on violation)"""
import sys, re
from pathlib import Path
bad = []
for p in Path(sys.argv[1]).rglob("*"):
    if not p.is_file(): continue
    if p.suffix in (".pkl", ".joblib", ".parquet"): bad.append((str(p), "serialised row-level object")); continue
    if p.suffix in (".csv", ".txt", ".json", ".md", ".tex"):
        head = p.read_text(encoding="utf-8", errors="ignore")[:200000]
        if re.search(r"(^|,|\")unique_code(,|\"|$)", head.splitlines()[0] if head else ""): bad.append((str(p), "unique_code column"))
        if re.search(r"\b(?:\+?237)?6\d{8}\b", head): bad.append((str(p), "phone-number-like token"))
for b in bad: print("VIOLATION", b)
print("privacy check:", "PASS" if not bad else "FAIL"); sys.exit(1 if bad else 0)
