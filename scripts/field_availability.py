"""Aggregate field availability for follow-on research questions (Prompt 4). Aggregate counts only.
Usage: python tools/field_availability.py outputs/audit/field_availability_for_new_questions.csv"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from stroke_repro import config as C  # noqa: E402

COLS = ['Cause of death', 'Complication per hospitalization', 'Become after leaving UNV', 'Length of hospitalization', 'Rankin at M1',
        'Barthel at M1', 'Rankin at M3', 'Barthel at M3', 'death3', 'Rankin at M6', 'Rankin at M12', 'stroke recurrence at m3',
        'illness-consultation start time', 'HGD arrival time', 'delay4.5', 'Time to obtain the scanner', 'Brain CT results',
        'OCSP Classification', 'Monthly income', 'place of residence', 'means of transport', 'type of support', 'educational level',
        'Complication on admission', 'NIHSS score', 'glagow score']


def nonmiss(s):
    t = s.map(lambda v: None if pd.isna(v) else str(v).strip())
    return t.notna() & ~t.isin(['', '9', '99', '9.0', '99.0'])


def main(out):
    x = pd.read_excel(C.RAW_XLSX)
    yr = pd.to_datetime(x['Date of entry'], errors='coerce').dt.year
    per = np.where(yr <= 2016, '2010-16', np.where(yr <= 2023, '2017-23', 'other'))
    rows = []
    for c in COLS:
        nm = nonmiss(x[c])
        rows.append([c, int(nm.sum()), round(100 * nm.mean(), 1), round(100 * nm[per == '2010-16'].mean(), 1), round(100 * nm[per == '2017-23'].mean(), 1)])
    d = pd.DataFrame(rows, columns=['field', 'n_nonmissing_excl_codes_9_99', 'pct_all_rows', 'pct_2010_16', 'pct_2017_23'])
    d.to_csv(out, index=False)
    print(d.to_string())


if __name__ == "__main__":
    main(sys.argv[1])
