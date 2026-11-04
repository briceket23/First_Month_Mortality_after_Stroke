"""Duplicate-identifier reconciliation that never destroys evidence.

Every source row is kept in the restricted record table.  For each repeated `unique_code`
(initials + admission date) group a rule-based decision is logged:

  D0 non-record      : all rows blank (no admission date, age or sex)           -> dropped (not a patient)
  D1 collision       : sex conflict, or |age difference| > 5 y                   -> separate patients
  D2 same encounter, compatible : no conflict in outcome-defining fields       -> one patient, fields coalesced
  D3 same encounter, outcome conflict : outcome-defining fields disagree        -> one patient, outcome UNRESOLVED
A row that is column-shifted (misaligned) contributes no values when a clean partner exists.
Admission-time predictors that disagree between rows are set to missing for the merged patient
(logged), never chosen by row order.

Alternative rules for sensitivity analysis:
  'keep_first' : first row of each group (reproduces the submitted cohort size of 1,615)
  'exclude_conflicts' : as primary, but D3 groups and D1 groups removed entirely
"""
import numpy as np
import pandas as pd

from . import config as C

OUTCOME_FIELDS = ["death1", "death3", "death6", "death9", "disp"]
PRED_FIELDS = C.NUMERIC + C.BINARY


def _vals(sub, col):
    v = sub[col]
    v = v[v.notna()]
    if col == "disp":
        v = v[~v.isin(["missing"])]
    if col.startswith("death"):
        v = v[v.isin(["Yes", "No"])]
    return v


def _decide(sub):
    clean = sub[~sub.flag_blank_record]
    if len(clean) == 0:
        return "D0_non_record", "all rows blank", []
    if len(clean) == 1:
        return "D2_same_encounter_compatible", "partner row blank", []
    sexes = clean.male.dropna().unique()
    ages = clean.age.dropna()
    if len(sexes) > 1:
        return "D1_identifier_collision", "sex differs between rows", []
    if len(ages) > 1 and ages.max() - ages.min() > C.DUP_AGE_DIFF_DISTINCT:
        return "D1_identifier_collision", f"age differs by {ages.max() - ages.min():.0f} y", []
    use = clean[~clean.flag_column_shift] if (~clean.flag_column_shift).any() else clean
    conflicts = []
    for col in OUTCOME_FIELDS:
        v = _vals(use, col)
        if v.nunique() > 1:
            conflicts.append(col)
    los = use.los_days.dropna()
    if len(los) > 1 and los.max() - los.min() > C.DUP_LOS_TOL:
        conflicts.append("los_days")
    if conflicts:
        return "D3_same_encounter_outcome_conflict", "conflict in " + ", ".join(conflicts), conflicts
    return "D2_same_encounter_compatible", "no outcome-field conflict", []


def _merge(sub, outcome_unresolved):
    use = sub[~sub.flag_blank_record]
    if (~use.flag_column_shift).any():
        use = use[~use.flag_column_shift]
    out = use.iloc[0].copy()
    pred_conf = []
    for col in use.columns:
        v = use[col].dropna()
        if col in ("src_id", "src_row"):
            continue
        if col.startswith("death") and not col.endswith("_raw"):
            v = v[v.isin(["Yes", "No"])]
        if col == "disp":
            v = v[v != "missing"]
        if len(v) == 0:
            out[col] = use[col].iloc[0]
            continue
        if v.astype(str).nunique() == 1:
            out[col] = v.iloc[0]
        elif col in PRED_FIELDS:
            out[col] = np.nan
            pred_conf.append(col)
        else:
            out[col] = v.iloc[0]   # descriptive / raw field; outcome handled by flag below
    out["src_ids"] = "|".join(sub.src_id)
    out["src_rows_used"] = "|".join(use.src_id)
    out["outcome_forced_unresolved"] = outcome_unresolved
    out["predictor_conflicts"] = ",".join(pred_conf)
    return out, pred_conf


def reconcile(rec, rule="primary"):
    """Return (patients, decision_log)."""
    rec = rec.copy()
    rec["src_ids"] = rec.src_id
    rec["src_rows_used"] = rec.src_id
    rec["outcome_forced_unresolved"] = False
    rec["predictor_conflicts"] = ""
    rec["dup_group"] = ""
    rec["dup_decision"] = ""
    codes = rec.unique_code.astype(str)
    dupmask = codes.duplicated(keep=False) & rec.unique_code.notna()
    singles = rec[~dupmask]
    groups = rec[dupmask].groupby(codes[dupmask], sort=True)
    patients, log = [singles], []
    for i, (code, sub) in enumerate(groups, start=1):
        gid = f"DUP{i:02d}"
        dec, why, conf = _decide(sub)
        n_field_diff = sum(sub[c].astype(str).nunique() > 1 for c in sub.columns if c.endswith("_raw"))
        entry = dict(dup_group=gid, unique_code=code, src_ids="|".join(sub.src_id), n_rows=len(sub),
                     decision=dec, reason=why, outcome_conflict_fields=",".join(conf),
                     any_row_column_shifted=bool(sub.flag_column_shift.any()),
                     n_raw_fields_differing=int(n_field_diff),
                     adjudicator="rule-based (revision analysis); source-record adjudication pending",
                     decision_date="2026-10-16")
        if rule == "keep_first":
            keep = sub.iloc[[0]].copy()
            keep["dup_group"], keep["dup_decision"] = gid, "keep_first"
            patients.append(keep)
            entry["applied"] = "first row kept (sensitivity rule)"
        elif dec == "D0_non_record":
            entry["applied"] = "dropped (non-record)"
        elif dec == "D1_identifier_collision":
            if rule == "exclude_conflicts":
                entry["applied"] = "excluded (sensitivity rule)"
            else:
                k = sub.copy()
                k["dup_group"], k["dup_decision"] = gid, dec
                k["patient_suffix"] = [f"{gid}-{j}" for j in range(1, len(k) + 1)]
                patients.append(k)
                entry["applied"] = "rows kept as separate patients"
        else:
            if rule == "exclude_conflicts" and dec.startswith("D3"):
                entry["applied"] = "excluded (sensitivity rule)"
            else:
                m, pc = _merge(sub, dec.startswith("D3"))
                m["dup_group"], m["dup_decision"] = gid, dec
                patients.append(pd.DataFrame([m]))
                entry["applied"] = ("merged; outcome unresolved pending source" if dec.startswith("D3")
                                    else "merged (fields coalesced)")
                entry["predictor_fields_set_missing"] = ",".join(pc)
        log.append(entry)
    pts = pd.concat(patients, ignore_index=True)
    pts["patient_key"] = [f"P{i:04d}" for i in range(1, len(pts) + 1)]
    return pts, pd.DataFrame(log)
