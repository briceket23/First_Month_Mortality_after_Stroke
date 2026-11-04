"""Stage 1: provenance, integrity audit, duplicate reconciliation, endpoint, cohort flow.

Aggregate outputs -> outputs/audit, outputs/cohort.  Row-level files -> restricted/ only.
"""
import json

import numpy as np
import pandas as pd

from . import config as C
from . import registry as R
from .cohort import build, reproduce_original


def jdump(obj, path):
    path.write_text(json.dumps(obj, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


def main():
    md5 = R.md5(C.RAW_XLSX)
    if C.SYNTHETIC:
        print("SYNTHETIC FIXTURE RUN: checksum", md5, "(no registry data)")
    else:
        assert md5 == C.RAW_MD5, f"raw workbook checksum mismatch: {md5}"
    raw = R.load_raw()
    assert C.SYNTHETIC or raw.shape == (1653, 253), raw.shape
    assert raw.src_id.is_unique
    rec, clog = R.build_records(raw)
    assert len(rec) == len(raw) and (rec.src_id.values == raw.src_id.values).all()
    rec.to_pickle(C.RESTRICTED / "records.pkl")
    clog.to_csv(C.AUDIT / "cleaning_and_integrity_log.csv", index=False)
    print(f"raw md5 {md5}; {raw.shape[0]} rows x {raw.shape[1]-2} source columns; src_id unique")

    # ---------------------------------------------- outcome-field diagnostics (aggregate)
    diag = {}
    diag["death_field_counts"] = {k: rec[k].fillna("missing").value_counts().to_dict() for k in ["death1", "death3", "death6", "death9"]}
    diag["disposition_counts"] = rec.disp.value_counts().to_dict()
    diag["disposition_x_death1"] = pd.crosstab(rec.disp, rec.death1.fillna("missing")).to_dict()
    yn = {k: rec[k].map({"Yes": 1, "No": 0}) for k in ["death1", "death3", "death6", "death9"]}
    diag["monotonicity"] = {
        "death1_yes_death3_no": int(((yn["death1"] == 1) & (yn["death3"] == 0)).sum()),
        "death3_yes_death6_no": int(((yn["death3"] == 1) & (yn["death6"] == 0)).sum()),
        "death6_yes_death9_no": int(((yn["death6"] == 1) & (yn["death9"] == 0)).sum()),
        "death1_no_death3_yes": int(((yn["death1"] == 0) & (yn["death3"] == 1)).sum()),
    }
    dur = {k: pd.to_numeric(rec[f"dur{k}_raw"], errors="coerce").value_counts().sort_index().to_dict() for k in (1, 3, 6, 9)}
    diag["duration_followed_values"] = dur
    inh = rec.disp == "death"
    diag["inhosp_death_by_death1"] = {
        k: dict(n=int(m.sum()), stay_median=float(rec.los_days[m].median()), stay_gt30=int((rec.los_days[m] > 30).sum()),
                stay_missing=int(rec.los_days[m].isna().sum()))
        for k, m in {"death1_yes": inh & (rec.death1 == "Yes"), "death1_no": inh & (rec.death1 == "No"),
                     "death1_missing": inh & rec.death1.isna()}.items()}
    diag["cause_of_death_recorded_by_disposition"] = rec.groupby("disp").cause_of_death_recorded.sum().astype(int).to_dict()
    jdump(diag, C.AUDIT / "outcome_field_diagnostics.json")

    # time-varying recording by admission year
    yr = rec.admission_year
    tv = pd.DataFrame({
        "admissions": yr.value_counts().sort_index(),
        "death1_recorded_pct": (rec.death1.isin(["Yes", "No"]).groupby(yr).mean() * 100).round(1),
        "death1_yes": (rec.death1 == "Yes").groupby(yr).sum(),
        "inhosp_deaths": inh.groupby(yr).sum(),
        "inhosp_deaths_with_death1_yes": (inh & (rec.death1 == "Yes")).groupby(yr).sum(),
        "disp_missing": (rec.disp == "missing").groupby(yr).sum(),
        "disp_other": (rec.disp == "other").groupby(yr).sum(),
        "discharged_home": (rec.disp == "home").groupby(yr).sum(),
        "home_death1_yes": ((rec.disp == "home") & (rec.death1 == "Yes")).groupby(yr).sum(),
        "home_death1_recorded": ((rec.disp == "home") & rec.death1.isin(["Yes", "No"])).groupby(yr).sum(),
        "dur1_coded_1": (pd.to_numeric(rec.dur1_raw, errors="coerce") == 1).groupby(yr).sum(),
        "dur1_coded_30": (pd.to_numeric(rec.dur1_raw, errors="coerce") == 30).groupby(yr).sum(),
        "dur1_coded_0": (pd.to_numeric(rec.dur1_raw, errors="coerce") == 0).groupby(yr).sum(),
    }).fillna(0).astype({"death1_recorded_pct": float})
    tv.index = tv.index.astype(int)
    tv.to_csv(C.AUDIT / "recording_by_admission_year.csv")

    # date / LOS anomalies (aggregate)
    dl = rec.los_rec_minus_elapsed.dropna()
    jdump({"recorded_minus_elapsed_distribution": dl.value_counts().sort_index().to_dict(),
           "n_both_available": int(len(dl)), "n_exact": int((dl == 0).sum()), "n_plus1": int((dl == 1).sum()),
           "n_abs_gt2": int((dl.abs() > 2).sum())}, C.AUDIT / "los_convention_check.json")

    # ---------------------------------------------- forensic reproduction of the submitted counts
    o = reproduce_original(rec)
    orig = dict(after_dedup=len(o), observed=int((o.y_orig_class == "observed_death1").sum()),
                inferred=int(o.y_orig.notna().sum() - (o.y_orig_class == "observed_death1").sum()),
                unlabelled=int(o.y_orig.isna().sum()), labelled=int(o.y_orig.notna().sum()),
                deaths=int(o.y_orig.sum()), mortality_pct=round(100 * o.y_orig.mean(), 1),
                observed_only_deaths=int(((o.y_orig_class == "observed_death1") & (o.y_orig == 1)).sum()),
                class_counts=o.y_orig_class.value_counts().to_dict())
    jdump(orig, C.AUDIT / "reproduction_of_submitted_counts.json")
    print("Reproduction of submitted reconstruction:", orig)

    # ---------------------------------------------- revised cohorts
    flows = {}
    for name, rule, strict in [("primary", "primary", False), ("strict_timing", "primary", True),
                               ("dup_keep_first", "keep_first", False), ("dup_exclude_conflicts", "exclude_conflicts", False)]:
        pts, flow, dlog = build(rec, rule=rule, strict=strict)
        flows[name] = flow
        pts.to_pickle(C.RESTRICTED / f"cohort_{name}.pkl")
        if name == "primary":
            dlog.to_csv(C.RESTRICTED / "duplicate_decision_log_with_codes.csv", index=False)
            dlog.drop(columns=["unique_code"]).to_csv(C.COHORT / "duplicate_decision_log.csv", index=False)
            print(dlog.decision.value_counts().to_dict())
    jdump(flows, C.COHORT / "cohort_flows.json")
    for k, v in flows.items():
        print(k, {kk: vv for kk, vv in v.items() if kk != "class_counts"})
    print("primary classes", flows["primary"]["class_counts"])

    # label provenance table (primary)
    pts = pd.read_pickle(C.RESTRICTED / "cohort_primary.pkl")
    prov = pts.groupby(["y_class"]).agg(n=("patient_key", "size"), y=("y", "first"), provenance=("y_provenance", "first"),
                                        timing=("y_timing", "first")).reset_index()
    prov["pct_of_eligible"] = (100 * prov.n / len(pts)).round(1)
    prov.to_csv(C.COHORT / "label_provenance_primary.csv", index=False)
    # crosswalk original vs revised label at source-row level (aggregate)
    first = o.set_index("src_id")
    pts_first = pts.assign(first_src=pts.src_ids.str.split("|").str[0]).set_index("first_src")
    cw = pd.crosstab(first.y_orig_class.reindex(pts_first.index).fillna("not in submitted cohort"),
                     pts_first.y_class)
    cw.to_csv(C.COHORT / "crosswalk_submitted_vs_revised_labels.csv")
    print(cw.to_string())


if __name__ == "__main__":
    main()
