"""Eligibility, endpoint assignment and cohort flow."""
import numpy as np
import pandas as pd

from . import config as C
from . import endpoint as E
from .reconcile import reconcile


def _endpoint_rows(pts, strict):
    out = []
    for _, p in pts.iterrows():
        if p.get("flag_column_shift", False):
            res = E._u("U_record_misaligned", "row values misaligned across columns; status not trusted")
        elif p.get("outcome_forced_unresolved", False):
            res = E._u("U_duplicate_outcome_conflict", "duplicate rows disagree on outcome fields", conflict=True)
        else:
            alt = None
            if pd.notna(p.los_date_elapsed) and pd.notna(p.los_recorded):
                alt = p.los_recorded
            res = E.assign(dict(disp=p.disp, los_days=p.los_days, los_alt=alt, death1=p.death1,
                                death3=p.death3, death6=p.death6, death9=p.death9), strict=strict)
        out.append(res)
    r = pd.DataFrame(out, index=pts.index)
    r.columns = ["y", "y_class", "y_provenance", "y_timing", "y_conflict", "y_reason"]
    r["y_direct_month1"] = pts.death1.isin(["Yes", "No"]) & r.y.notna() & \
        r.y_class.isin(["E2_month1_death_postdischarge", "N2_month1_alive", "E1_inhosp_death_le30", "N1_inhosp_death_gt30"])
    return r


def build(raw_records, rule="primary", strict=False):
    """Return (patients_with_outcome, flow dict, dup_log)."""
    rec = raw_records.copy()
    flow = {"source_rows": len(rec)}
    pts, dlog = reconcile(rec, rule=rule)
    flow["after_reconciliation"] = len(pts)
    blank = pts.flag_blank_record.astype(bool)
    flow["excluded_blank_records"] = int(blank.sum())
    pts = pts[~blank].copy()
    no_date = pts.entry_date.isna()
    flow["excluded_no_valid_admission_date"] = int(no_date.sum())
    pts = pts[~no_date]
    child = pd.to_numeric(pts.age_raw, errors="coerce") < 18
    flow["excluded_age_lt18"] = int(child.sum())
    pts = pts[~child]
    tia = pts.diagnosis.astype(str).isin(C.EXCLUDED_DIAGNOSES)
    flow["excluded_tia"] = int(tia.sum())
    pts = pts[~tia].copy()
    flow["eligible"] = len(pts)
    ep = _endpoint_rows(pts, strict)
    pts = pd.concat([pts, ep], axis=1)
    pts["labelled"] = pts.y.notna()
    flow["labelled"] = int(pts.labelled.sum())
    flow["deaths"] = int(np.nansum(pts.y))
    flow["unresolved"] = int((~pts.labelled).sum())
    flow["mortality_labelled_pct"] = round(100 * flow["deaths"] / flow["labelled"], 1)
    flow["class_counts"] = pts.y_class.value_counts().to_dict()
    return pts, flow, dlog


def reproduce_original(rec):
    """Re-implementation of the submitted manuscript's reconstruction (for audit only):
    keep-first de-duplication, death1 Yes/No used directly, then in-hospital death by stay,
    long stay alive (any non-death disposition), later follow-up 'No' -> alive."""
    d = rec.drop_duplicates("unique_code", keep="first").copy()
    los = pd.to_numeric(d.los_raw, errors="coerce")
    los = los.fillna((pd.to_datetime(d.release_date_raw, errors="coerce") - pd.to_datetime(d.entry_date_raw, errors="coerce")).dt.days)
    disp = d.disp_raw.astype(object).astype(str)
    d1 = d.death1_raw.astype(object).astype(str)
    y = pd.Series(np.nan, index=d.index)
    cls = pd.Series("unlabelled", index=d.index)
    m = d1.isin(["Yes", "No"])
    y[m] = (d1[m] == "Yes").astype(float)
    cls[m] = "observed_death1"
    mm = ~m
    a = mm & (disp == "death") & (los <= 30)
    y[a], cls[a] = 1, "inferred_inhosp_death_le30"
    b = mm & (disp == "death") & (los > 30)
    y[b], cls[b] = 0, "inferred_inhosp_death_gt30"
    c = mm & y.isna() & (disp != "death") & d.disp_raw.notna() & (los > 30)
    y[c], cls[c] = 0, "inferred_long_stay_alive"
    later = (d.death3_raw.astype(object).astype(str) == "No") | (d.death6_raw.astype(object).astype(str) == "No") | \
            (d.death9_raw.astype(object).astype(str) == "No")
    e = mm & y.isna() & later
    y[e], cls[e] = 0, "inferred_later_followup_alive"
    d["y_orig"], d["y_orig_class"] = y, cls
    return d
