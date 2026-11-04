"""Load the raw registry without altering it, attach stable source-row identifiers,
flag record-level integrity problems and derive *separate* cleaned analysis fields.

Raw values are never overwritten: every derived field lives in a new column, and the
raw workbook is only read.
"""
import hashlib
import warnings

import numpy as np
import pandas as pd

from . import config as C

warnings.filterwarnings("ignore")

RAW_FIELDS = {  # raw column (whitespace-stripped) -> analysis name
    "unique_code": "unique_code", "Date of entry": "entry_date_raw", "Release date": "release_date_raw",
    "age": "age_raw", "sex": "sex_raw", "diagnostic": "diagnosis",
    "Length of hospitalization": "los_raw", "Become after leaving UNV": "disp_raw",
    "Cause of death": "cause_of_death_raw",
    "death1": "death1_raw", "death3": "death3_raw", "death6": "death6_raw", "death9": "death9_raw",
    "duration followed1": "dur1_raw", "duration followed3": "dur3_raw",
    "duration followed6": "dur6_raw", "duration followed9": "dur9_raw",
    # admission-time candidate predictors
    "NIHSS score": "nihss_raw", "glagow score": "gcs_raw", "Modified Rankin score": "mrs_raw",
    "Systolic BP": "sbp_raw", "Diastolic BP": "dbp_raw", "cardiac frequency": "hr_raw",
    "respiratory rate": "rr_raw", "temperature": "temp_raw", "SA O2": "spo2_raw",
    "Body mass index": "bmi_raw", "capillary blood sugar": "glucose_raw",
    "HISTORY of hypertension": "htn_raw", "Diabetes ATCD": "dm_raw", "Smoking": "smoke_raw",
    "ATCD of heart disease": "hd_raw", "ATCD of atrial fibrillation": "af_raw", "Stroke ATCD": "prior_raw",
    "Ischemik stroke on scanner": "ct_isch_raw", "Stroke Hemorrhagic": "ct_hem_raw",
    "creatinine": "creat_raw", "uremia": "urea_raw", "Total cholesterol": "chol_raw",
    "Tx Hb": "hb_raw", "GB blood": "wbc_raw", "Blood platelets": "plt_raw", "CRP": "crp_raw",
    "Na+": "na_raw", "K+": "k_raw",
}


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_raw():
    """Return the full raw workbook with stable identifiers (no value changes)."""
    raw = pd.read_excel(C.RAW_XLSX)
    raw.columns = [c.strip() for c in raw.columns]
    raw = raw.copy()
    raw.insert(0, "src_row", np.arange(2, len(raw) + 2))          # Excel row number (header = row 1)
    raw.insert(0, "src_id", [f"R{r:04d}" for r in raw["src_row"]])
    return raw


def _yesno(s):
    s = s.astype(object)
    out = pd.Series(np.nan, index=s.index, dtype=object)
    st = s.astype(str).str.strip()
    out[st == "Yes"] = "Yes"
    out[st == "No"] = "No"
    out[s.notna() & ~st.isin(["Yes", "No"])] = "invalid"          # e.g. 9, 3 (undocumented codes)
    return out


def _bin(s):
    st = s.astype(object).astype(str).str.strip()
    return pd.Series(np.where(st == "Yes", 1.0, np.where(st == "No", 0.0, np.nan)), index=s.index)


def _num(s):
    return pd.to_numeric(s, errors="coerce").astype(float)


def _isnum(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def build_records(raw):
    """Derive analysis fields + integrity flags; returns (records, cleaning_log)."""
    log = []
    r = pd.DataFrame({"src_id": raw.src_id, "src_row": raw.src_row})
    for k, v in RAW_FIELDS.items():
        r[v] = raw[k].values

    # ---------------------------------------------------------- structural integrity
    yn_cols = [c for c in raw.columns if raw[c].astype(str).isin(["Yes", "No"]).sum() > 300]
    junk = raw[yn_cols].apply(lambda s: s.map(lambda v: pd.notna(v) and str(v) not in ("Yes", "No") and _isnum(v)))
    r["n_numeric_in_yesno"] = junk.sum(axis=1).values
    r["flag_column_shift"] = r.n_numeric_in_yesno >= C.SHIFT_JUNK_MIN
    core = raw[["Date of entry", "age", "sex"]].notna().sum(axis=1)
    r["flag_blank_record"] = (core == 0).values
    log.append(("integrity", "column_shift", int(r.flag_column_shift.sum()),
                f">= {C.SHIFT_JUNK_MIN} numeric codes in Yes/No fields (misaligned row)"))
    log.append(("integrity", "blank_record", int(r.flag_blank_record.sum()), "no admission date, age or sex"))

    # ---------------------------------------------------------- dates and length of stay
    ent, rel = pd.to_datetime(r.entry_date_raw, errors="coerce"), pd.to_datetime(r.release_date_raw, errors="coerce")
    ent_ok = ent.dt.year.between(*C.VALID_ENTRY_YEARS)
    rel_ok = rel.dt.year.between(*C.VALID_RELEASE_YEARS)
    r["entry_date"] = ent.where(ent_ok)
    r["release_date"] = rel.where(rel_ok)
    r["flag_entry_missing"] = ent.isna()
    r["flag_entry_impossible_year"] = ent.notna() & ~ent_ok
    r["flag_release_impossible_year"] = rel.notna() & ~rel_ok
    elapsed = (r.release_date - r.entry_date).dt.days
    r["flag_release_before_entry"] = elapsed < 0
    # a date-derived stay above the plausible maximum (e.g. 365-376 d: release year mistyped) is not used
    r["flag_date_stay_implausible"] = elapsed > C.LOS_MAX_PLAUSIBLE
    r["los_date_elapsed"] = elapsed.where((elapsed >= 0) & (elapsed <= C.LOS_MAX_PLAUSIBLE))
    los = _num(r.los_raw)
    r["flag_los_missing_code"] = los.isin(C.LOS_MISSING_CODES)
    r["flag_los_implausible"] = (los < 0) | (los > C.LOS_MAX_PLAUSIBLE)
    r["los_recorded"] = los.where(~r.flag_los_missing_code & ~r.flag_los_implausible)
    diff = r.los_recorded - r.los_date_elapsed
    r["los_rec_minus_elapsed"] = diff
    r["flag_los_disagree"] = diff.abs() > C.LOS_AGREEMENT_TOL
    # resolved elapsed stay: date-derived when valid, else recorded LOS (convention undocumented)
    r["los_days"] = r.los_date_elapsed.where(r.los_date_elapsed.notna(), r.los_recorded)
    r["los_source"] = np.where(r.los_date_elapsed.notna(), "dates",
                               np.where(r.los_recorded.notna(), "recorded_los", "none"))
    for f in ["flag_entry_missing", "flag_entry_impossible_year", "flag_release_impossible_year",
              "flag_release_before_entry", "flag_date_stay_implausible", "flag_los_missing_code", "flag_los_implausible", "flag_los_disagree"]:
        log.append(("dates_los", f, int(r[f].sum()), "flagged; raw value preserved"))

    # ---------------------------------------------------------- outcome-related fields
    for k in ["death1", "death3", "death6", "death9"]:
        r[k] = _yesno(r[f"{k}_raw"])
        log.append(("outcome_fields", f"{k}_invalid_code", int((r[k] == "invalid").sum()),
                    "non Yes/No code (undocumented, e.g. 9/3) -> treated as unknown"))
    d = r.disp_raw.astype(object)
    ds = d.astype(str).str.strip()
    r["disp"] = np.select(
        [d.isna(), ds == "death", ds == "RAD", ds.isin(["transfer to another hospital", "transfer abroad"]), ds == "Other"],
        ["missing", "death", "home", "transfer", "other"], default="invalid")
    r["cause_of_death_recorded"] = r.cause_of_death_raw.notna() & ~r.cause_of_death_raw.astype(str).isin(["0", "9", "99", "0.0"])

    # ---------------------------------------------------------- demographics & population
    r["age"] = _num(r.age_raw).where(lambda x: x.between(18, 110))
    log.append(("population", "age_outside_18_110", int((_num(r.age_raw).notna() & r.age.isna()).sum()), "set to NA"))
    sx = r.sex_raw.astype(object).astype(str).str.strip().str.lower()
    r["male"] = np.where(sx == "male", 1.0, np.where(sx == "female", 0.0, np.nan))

    # ---------------------------------------------------------- predictors (unit harmonisation, logged)
    def rng(x, lo, hi, name):
        bad = x.notna() & ~x.between(lo, hi)
        if bad.any():
            log.append(("range_to_NA", name, int(bad.sum()), f"outside [{lo}, {hi}]"))
        return x.where(~bad)

    r["nihss"] = rng(_num(r.nihss_raw), 0, 42, "nihss")
    r["gcs"] = rng(_num(r.gcs_raw), 3, 15, "gcs")
    r["mrs"] = rng(_num(r.mrs_raw), 0, 5, "mrs")           # mRS 6 = dead; not a valid admission value
    r["sbp"] = rng(_num(r.sbp_raw), 50, 300, "sbp")
    r["dbp"] = rng(_num(r.dbp_raw), 30, 200, "dbp")
    r["heart_rate"] = rng(_num(r.hr_raw), 20, 220, "heart_rate")
    r["resp_rate"] = rng(_num(r.rr_raw), 5, 60, "resp_rate")
    t = _num(r.temp_raw)
    fx = t > 50
    log.append(("unit_fix", "temperature_x10", int(fx.sum()), "values > 50 divided by 10"))
    r["temperature"] = rng(t.where(~fx, t / 10), 30, 43, "temperature")
    r["spo2"] = rng(_num(r.spo2_raw), 50, 100, "spo2")
    r["bmi"] = rng(_num(r.bmi_raw), 10, 80, "bmi")
    r["glucose_cap"] = rng(_num(r.glucose_raw), 0.2, 8, "glucose_cap (g/L)")
    r["creatinine"] = rng(_num(r.creat_raw) / 10.0, 0.1, 25, "creatinine (mg/L -> mg/dL)")
    log.append(("unit_convert", "creatinine", int(_num(r.creat_raw).notna().sum()), "mg/L -> mg/dL (/10)"))
    r["urea"] = rng(_num(r.urea_raw), 0, 6, "urea (g/L)")
    r["total_cholesterol"] = rng(_num(r.chol_raw), 0.3, 15, "total_cholesterol")
    r["hemoglobin"] = rng(_num(r.hb_raw), 3, 22, "hemoglobin")
    w = _num(r.wbc_raw)
    fw = w > 100
    log.append(("unit_harmonise", "wbc", int(fw.sum()), "absolute counts /1000 -> x10^3/uL"))
    r["wbc"] = rng(w.where(~fw, w / 1000), 0.5, 60, "wbc")
    p = _num(r.plt_raw)
    fp = p > 1000
    log.append(("unit_harmonise", "platelets", int(fp.sum()), "absolute counts /1000 -> x10^3/uL"))
    r["platelets"] = rng(p.where(~fp, p / 1000), 5, 1200, "platelets")
    r["crp"] = rng(_num(r.crp_raw), 0, 500, "crp")
    r["sodium"] = rng(_num(r.na_raw), 100, 180, "sodium")
    r["potassium"] = rng(_num(r.k_raw), 1.5, 9, "potassium")
    for new, old in [("hypertension", "htn_raw"), ("diabetes", "dm_raw"), ("smoking", "smoke_raw"),
                     ("heart_disease", "hd_raw"), ("atrial_fib", "af_raw"), ("prior_stroke", "prior_raw")]:
        r[new] = _bin(r[old])
    hem_ct = _bin(r.ct_hem_raw)
    dx = r.diagnosis.astype(object).astype(str)
    r["hemorrhagic"] = np.where(dx.isin(["AVCH", "HSA"]), 1.0, np.where(dx.isin(["DALY", "TVC", "AIT"]), 0.0, hem_ct))
    # predictors from column-shifted rows are unreliable: blank them (raw kept)
    pred_cols = C.NUMERIC + C.BINARY + ["bmi"]
    pred_cols = [c for c in dict.fromkeys(pred_cols) if c in r.columns and c not in ("age", "male")]
    r.loc[r.flag_column_shift, pred_cols] = np.nan
    log.append(("integrity", "column_shift_predictors_blanked", int(r.flag_column_shift.sum()),
                "clinical predictors set to NA in misaligned rows (raw kept)"))
    r["admission_year"] = r.entry_date.dt.year
    return r, pd.DataFrame(log, columns=["step", "item", "n_records", "detail"])
