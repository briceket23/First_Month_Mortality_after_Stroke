"""Field-level comparison of the 38 repeated-identifier groups across ALL 251 source fields.

Two counting conventions are reported so that earlier, apparently discrepant counts can be reconciled:
  'any_difference'      : values differ, counting missing-vs-present as a difference
  'both_present_differ' : both rows non-missing and values differ (true value conflicts)
Fields are grouped into categories by their position in the source workbook.
"""
import numpy as np
import pandas as pd

from . import config as C
from .registry import load_raw


def category(i):
    if i <= 3:
        return "identity_dates"
    if i <= 20:
        return "sociodemographic_prehospital"
    if i <= 148:
        return "admission_clinical"
    if i <= 153:
        return "hospital_course_disposition"
    return "follow_up_M1_to_M12"


def main():
    raw = load_raw()
    src_cols = [c for c in raw.columns if c not in ("src_id", "src_row")]
    cats = {c: category(i) for i, c in enumerate(src_cols)}
    grp = raw[raw.unique_code.duplicated(keep=False)]
    dlog = pd.read_csv(C.RESTRICTED / "duplicate_decision_log_with_codes.csv")
    gid = dict(zip(dlog.unique_code, dlog.dup_group))
    rows = []
    for code, sub in grp.groupby("unique_code"):
        rec = {"dup_group": gid.get(code)}
        for conv in ("any_difference", "both_present_differ"):
            for cat in sorted(set(cats.values())):
                rec[f"{conv}:{cat}"] = 0
            rec[f"{conv}:total"] = 0
        for c in src_cols:
            if c == "unique_code":
                continue
            v = sub[c]
            s = v.astype(str).where(v.notna(), "<NA>")
            if s.nunique() > 1:
                rec[f"any_difference:{cats[c]}"] += 1
                rec["any_difference:total"] += 1
                if v.notna().all():
                    rec[f"both_present_differ:{cats[c]}"] += 1
                    rec["both_present_differ:total"] += 1
        rows.append(rec)
    t = pd.DataFrame(rows).sort_values("dup_group")
    t.to_csv(C.COHORT / "duplicate_field_differences_by_category.csv", index=False)
    summ = t.drop(columns="dup_group").agg(["median", "min", "max", "sum"]).T
    summ["groups_with_any"] = (t.drop(columns="dup_group") > 0).sum()
    summ.to_csv(C.COHORT / "duplicate_field_differences_summary.csv")
    print(summ.to_string())


if __name__ == "__main__":
    main()
