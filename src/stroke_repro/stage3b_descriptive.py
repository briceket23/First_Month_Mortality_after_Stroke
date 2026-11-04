"""Stage 3b: baseline table by outcome (labelled cohort) and subgroup discrimination from out-of-fold predictions."""
import json

import numpy as np
import pandas as pd
from scipy import stats

from . import config as C
from . import metrics as M
from .stage2_ascertainment import add_period

PRETTY = {"age": "Age, y", "nihss": "NIHSS", "gcs": "Glasgow Coma Scale", "mrs": "Modified Rankin (admission)",
          "sbp": "Systolic BP, mmHg", "heart_rate": "Heart rate, /min", "resp_rate": "Respiratory rate, /min",
          "temperature": "Temperature, °C", "glucose_cap": "Capillary glucose, g/L", "creatinine": "Creatinine, mg/dL",
          "urea": "Urea, g/L", "wbc": "White-cell count, x10^3/uL", "crp": "CRP, mg/L", "hemoglobin": "Haemoglobin, g/dL",
          "male": "Male sex", "hemorrhagic": "Haemorrhagic stroke", "hypertension": "Hypertension", "diabetes": "Diabetes",
          "atrial_fib": "Atrial fibrillation", "prior_stroke": "Prior stroke"}


def main():
    p = add_period(pd.read_pickle(C.RESTRICTED / "cohort_primary.pkl"))
    lab = p[p.labelled]
    a, b = lab[lab.y == 0], lab[lab.y == 1]
    rows = []
    for c in ["age", "nihss", "gcs", "mrs", "sbp", "heart_rate", "resp_rate", "temperature", "glucose_cap", "creatinine", "urea", "wbc", "crp", "hemoglobin"]:
        f = lambda s: f"{s.median():.1f} [{s.quantile(.25):.1f}-{s.quantile(.75):.1f}]"
        pv = stats.mannwhitneyu(a[c].dropna(), b[c].dropna()).pvalue
        rows.append(dict(variable=PRETTY[c], survived=f(a[c]), died=f(b[c]), missing_pct=round(100 * lab[c].isna().mean(), 1), p=pv))
    for c in ["male", "hemorrhagic", "hypertension", "diabetes", "atrial_fib", "prior_stroke"]:
        f = lambda s: f"{int(s.sum())} ({100*s.mean():.1f})"
        tab = [[a[c].sum(), a[c].notna().sum() - a[c].sum()], [b[c].sum(), b[c].notna().sum() - b[c].sum()]]
        rows.append(dict(variable=PRETTY[c], survived=f(a[c]), died=f(b[c]), missing_pct=round(100 * lab[c].isna().mean(), 1),
                         p=stats.chi2_contingency(tab)[1]))
    pd.DataFrame(rows).to_csv(C.ANALYSIS / "baseline_by_outcome.csv", index=False)
    json.dump(dict(n_survived=int(len(a)), n_died=int(len(b))), open(C.ANALYSIS / "baseline_n.json", "w", encoding="utf-8"))

    o = pd.read_pickle(C.RESTRICTED / "oof_primary.pkl").merge(lab[["patient_key", "male", "hemorrhagic", "period", "nihss"]], on="patient_key")
    sg = []
    for name, mask in [("Female", o.male == 0), ("Male", o.male == 1), ("Ischaemic or other", o.hemorrhagic == 0),
                       ("Haemorrhagic", o.hemorrhagic == 1), ("Admitted 2010-2016", o.period.isin(["2010-12", "2013-14", "2015-16"])),
                       ("Admitted 2017-2023", o.period.isin(["2017-19", "2020", "2021-23"])), ("NIHSS recorded", o.nihss.notna()),
                       ("NIHSS missing", o.nihss.isna())]:
        s = o[mask]
        auc, lo, hi = M.delong_ci(s.y.values, s.LR.values)
        cal = M.calibration(s.y.values, s.LR.values)
        sg.append(dict(subgroup=name, n=len(s), deaths=int(s.y.sum()), auroc=auc, lo=lo, hi=hi,
                       intercept=cal["intercept"], slope=cal["slope"]))
    pd.DataFrame(sg).to_csv(C.ANALYSIS / "subgroups_oof.csv", index=False)
    print(pd.DataFrame(sg).round(3).to_string())


if __name__ == "__main__":
    main()
