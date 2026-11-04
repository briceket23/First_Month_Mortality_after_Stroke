"""Observed-only ('recorded month-1 vital status') summary: aggregate counts from death1 alone, by period; no reconstruction.
Usage: python tools/observed_only_summary.py OUT_JSON"""
import json, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from stroke_repro import config as C

def main(out):
    P = pd.read_pickle(C.RESTRICTED / "cohort_primary.pkl")
    ok = P.death1.isin(["Yes", "No"]) & ~P.outcome_forced_unresolved.astype(bool) & ~P.flag_column_shift.astype(bool)
    per = pd.cut(P.admission_year, [2009, 2012, 2014, 2016, 2019, 2020, 2023], labels=["2010-12", "2013-14", "2015-16", "2017-19", "2020", "2021-23"])
    t = pd.DataFrame({"eligible": P.groupby(per, observed=False).size(), "recorded_month1_status": ok.groupby(per, observed=False).sum(),
                      "recorded_deaths": (ok & (P.death1 == "Yes")).groupby(per, observed=False).sum()})
    t["recorded_pct"] = (100 * t.recorded_month1_status / t.eligible).round(1)
    t["mortality_among_recorded_pct"] = (100 * t.recorded_deaths / t.recorded_month1_status).round(1)
    res = {"endpoint_name": "recorded month-1 vital status (death1 Yes/No only; no reconstruction; time origin per dictionary implicit)",
           "eligible": int(len(P)), "with_recorded_status": int(ok.sum()), "recorded_deaths": int((ok & (P.death1 == "Yes")).sum()),
           "mortality_among_recorded_pct": round(100 * float((ok & (P.death1 == "Yes")).sum()) / float(ok.sum()), 1),
           "by_period": t.reset_index().astype(str).to_dict(orient="records"),
           "model_results_key": "sensitivity_nested.observed_only and temporal_observed_only in model_results.json (when the reconstructed run has been executed)"}
    mr = C.ANALYSIS / "model_results.json"
    if mr.exists():
        m = json.loads(mr.read_text(encoding="utf-8")); res["nested_cv_observed_only"] = m["sensitivity_nested"].get("observed_only"); res["temporal_observed_only"] = m.get("temporal_observed_only")
    Path(out).parent.mkdir(parents=True, exist_ok=True); json.dump(res, open(out, "w", encoding="utf-8"), indent=1); print(json.dumps(res, indent=1)[:1500])

if __name__ == "__main__":
    main(sys.argv[1])
