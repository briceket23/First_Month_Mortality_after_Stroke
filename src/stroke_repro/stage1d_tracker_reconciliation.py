"""Stage 1d: reconcile the revision's audit counts with the counts recorded in the authors'
execution tracker (Stroke_Registry_Revision_Execution_Tracker.xlsx, 'Evidence Reconciliation' sheet),
and produce the label-transition and length-of-stay tables requested under reviewer item A-4.

Every count is computed from the raw workbook under an explicitly stated rule, so that apparently
different numbers can be traced to different definitions rather than to errors.
"""
import json

import numpy as np
import pandas as pd

from . import config as C
from .registry import load_raw


def main():
    raw = load_raw()
    rec = pd.read_pickle(C.RESTRICTED / "records.pkl")
    ent = pd.to_datetime(raw["Date of entry"], errors="coerce")
    rel = pd.to_datetime(raw["Release date"], errors="coerce")
    dob = pd.to_datetime(raw["Date of birth"], errors="coerce")
    los = pd.to_numeric(raw["Length of hospitalization"], errors="coerce")
    plaus = lambda s: s.dt.year.between(1900, 2030)                       # calendar-plausible year
    win_e, win_r = ent.dt.year.between(*C.VALID_ENTRY_YEARS), rel.dt.year.between(*C.VALID_RELEASE_YEARS)
    el = (rel - ent).dt.days
    both_plaus = plaus(ent) & plaus(rel)
    rows = []

    def add(item, tracker, rule, value, note=""):
        rows.append(dict(item=item, tracker_value=tracker, rule=rule, revision_value=value, note=note))

    add("Source rows", "1,653", "data rows in sheet", len(raw))
    add("Source columns", "251", "columns", raw.shape[1] - 2)
    add("Distinct unique_code values", "1,615", "distinct non-missing codes", int(raw.unique_code.nunique()))
    dup = raw[raw.unique_code.duplicated(keep=False)]
    add("Repeated-code groups", "38 (76 rows)", "codes occurring more than once", f"{dup.unique_code.nunique()} ({len(dup)} rows)")
    src_cols = [c for c in raw.columns if c not in ("src_id", "src_row", "unique_code")]
    anydiff = sum(any(g[c].astype(str).where(g[c].notna(), "<NA>").nunique() > 1 for c in src_cols) for _, g in dup.groupby("unique_code"))
    add("Groups with any field discrepancy", "37/38", "any of 250 fields differs, missing-vs-present counted", f"{anydiff}/38")
    tf = ["Date of entry", "Release date", "Length of hospitalization", "Become after leaving UNV", "output processing",
          "Cause of death", "duration followed1", "duration followed3", "duration followed6", "duration followed9",
          "death1", "death3", "death6", "death9"]
    tdiff = sum(any(g[c].astype(str).where(g[c].notna(), "<NA>").nunique() > 1 for c in tf) for _, g in dup.groupby("unique_code"))
    add("Groups with timing/outcome-field differences", "35/38",
        "tracker field set (dates, LOS, disposition, output processing, cause of death, follow-up durations, death codes); missing-vs-present counted",
        f"{tdiff}/38")
    tdiff2 = sum(any(g[c].notna().all() and g[c].astype(str).nunique() > 1 for c in tf) for _, g in dup.groupby("unique_code"))
    add("  same, both rows non-missing", "—", "as above, only two different non-missing values", f"{tdiff2}/38")
    add("Groups with selected clinical-variable differences", "28 (author-reported)", "selected-variable list unavailable; nearest revision rule = any admission-clinical field with two different non-missing values",
        f"{int((pd.read_csv(C.COHORT / 'duplicate_field_differences_by_category.csv')['both_present_differ:admission_clinical'] > 0).sum())}/38",
        "Not reproducible without the original variable list")
    add("Release before entry", "23 rows (plausible-year filter)", "release < entry, both years 1900-2030", int(((rel < ent) & both_plaus).sum()))
    add("  same, unfiltered", "24 (naive)", "release < entry, any year", int((rel < ent).sum()))
    add("  same, registry window", "—", f"entry {C.VALID_ENTRY_YEARS}, release {C.VALID_RELEASE_YEARS} (rule used in the analysis)",
        int(rec.flag_release_before_entry.sum()), "The 2009 release year falls outside the analysis window and is flagged as an impossible release year instead")
    d = los - el
    add("LOS differs from date interval by >1 day", "174 rows (plausible-year filter)", "|recorded LOS - (release - entry)| > 1, both years plausible",
        int(((d.abs() > 1) & both_plaus).sum()))
    add("  same, tolerance >2 days", "—", "|difference| > 2 days, plausible years; the analysis applies this tolerance after excluding derived stays >120 d",
        f"{int(((d.abs() > 2) & both_plaus).sum())} ({int(rec.flag_los_disagree.sum())} in the analysis)")
    u = ((rel < ent) & both_plaus) | ((d.abs() > 1) & both_plaus)
    add("Union of the two timing flags", "175 distinct rows", "release<entry OR |diff|>1, plausible years", int(u.sum()))
    add("Reported total flagged rows", "194 (author-reported)", "flag classes not documented", "not reproducible",
        "Requires the original audit build script; the revision's own flags are listed in cleaning_and_integrity_log.csv")
    imp = []
    for nm, s in [("Release date", rel), ("Date of entry", ent), ("Date of birth", dob)]:
        bad = raw.loc[s.notna() & ~plaus(s), "src_row"].tolist()
        imp.append(f"{nm}: rows {bad} (year {', '.join(str(int(y)) for y in s[s.notna() & ~plaus(s)].dt.year)})")
    add("Implausible dates", "rows 767, 773, 808", "year outside 1900-2030", "; ".join(imp), "Not corrected; date of birth is not used in the analysis")
    for k, tv in [("death1", "Yes 162; No 658; '9' 1; missing 832"), ("death3", "Yes 165; No 553; '3' 2; '9' 1; missing 932")]:
        vc = raw[k].astype(object).fillna("missing").astype(str).value_counts().to_dict()
        add(f"Raw {k} values", tv, "raw 1,653 rows", "; ".join(f"{a} {b}" for a, b in vc.items()))
    for nm, col, tv in [("NIHSS", "NIHSS score", "790/1,653 = 47.8%"), ("modified Rankin", "Modified Rankin score", "857/1,653 = 51.8%"),
                        ("SA O2", "SA O2", "1,122/1,653 = 67.9%"), ("BMI", "Body mass index", "1,466/1,653 = 88.7%")]:
        m = raw[col].isna().sum()
        add(f"Raw {nm} missingness", tv, "raw rows", f"{m}/1,653 = {100*m/1653:.1f}%")
    out = pd.DataFrame(rows)
    out.to_csv(C.AUDIT / "tracker_count_reconciliation.csv", index=False)
    print(out.to_string())

    # ------------------------------------------------ label transitions (submitted reconstruction -> revised endpoint)
    cw = pd.read_csv(C.COHORT / "crosswalk_submitted_vs_revised_labels.csv", index_col=0)
    cw.to_csv(C.COHORT / "label_transitions.csv")

    # ------------------------------------------------ length-of-stay distribution by disposition (eligible patients)
    P = pd.read_pickle(C.RESTRICTED / "cohort_primary.pkl")
    rows = []
    for dsp, lab in [("death", "Died in hospital"), ("home", "Discharged home"), ("transfer", "Transferred"), ("other", "'Other' disposition")]:
        s = P.loc[P.disp == dsp, "los_days"]
        rows.append(dict(disposition=lab, n=int((P.disp == dsp).sum()), stay_known=int(s.notna().sum()),
                         median=s.median(), q1=s.quantile(.25), q3=s.quantile(.75), max=s.max(),
                         le7=int((s <= 7).sum()), d8_30=int(s.between(8, 30).sum()), d28_32=int(s.between(28, 32).sum()), gt30=int((s > 30).sum())))
    pd.DataFrame(rows).to_csv(C.COHORT / "los_by_disposition.csv", index=False)
    src = P.los_source.value_counts().to_dict()
    json.dump(dict(los_source=src), open(C.COHORT / "los_source_counts.json", "w", encoding="utf-8"))
    print(pd.DataFrame(rows).to_string(), src)


if __name__ == "__main__":
    main()
