"""Final technical verification: schema, row preservation, cohort arithmetic, leakage controls,
hard-coded manuscript statements, LaTeX build and response-letter integrity.  Writes outputs/verification_report.json."""
import json
import pickle
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from stroke_repro import config as C  # noqa: E402
from stroke_repro.registry import md5  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(dict(check=name, passed=bool(ok), detail=str(detail)))


# ------------------------------------------------------------------ data and cohort
check("raw workbook checksum", md5(C.RAW_XLSX) == C.RAW_MD5, md5(C.RAW_XLSX))
rec = pd.read_pickle(C.RESTRICTED / "records.pkl")
check("all 1,653 source rows preserved with unique ids", len(rec) == 1653 and rec.src_id.is_unique, len(rec))
flows = json.loads((C.COHORT / "cohort_flows.json").read_text(encoding="utf-8"))
for k, f in flows.items():
    check(f"[{k}] eligible = labelled + unresolved", f["eligible"] == f["labelled"] + f["unresolved"])
    check(f"[{k}] class counts sum to eligible", sum(f["class_counts"].values()) == f["eligible"])
    check(f"[{k}] exclusions arithmetic", f["after_reconciliation"] - f["excluded_blank_records"] - f["excluded_no_valid_admission_date"]
          - f["excluded_age_lt18"] - f["excluded_tia"] == f["eligible"])
P = pd.read_pickle(C.RESTRICTED / "cohort_primary.pkl")
ids = P.src_ids.str.split("|").explode()
check("no source row used by two analytic patients", ids.is_unique)
check("every analytic patient traces to source rows", ids.isin(rec.src_id).all())
check("labels only where evidence class is not unresolved", (P.y.notna() == ~P.y_class.str.startswith("U_")).all())
orig = json.loads((C.AUDIT / "reproduction_of_submitted_counts.json").read_text(encoding="utf-8"))
check("submitted reconstruction counts reproduced (803/218/594, 345)",
      (orig["observed"], orig["inferred"], orig["unlabelled"], orig["deaths"]) == (803, 218, 594, 345), orig)
dl = pd.read_csv(C.COHORT / "duplicate_decision_log.csv")
check("38 duplicate groups logged with a decision", len(dl) == 38 and dl.decision.notna().all(), dl.decision.value_counts().to_dict())
check("public duplicate log contains no identifier codes", "unique_code" not in dl.columns)

# ------------------------------------------------------------------ leakage controls
mr = json.loads((C.ANALYSIS / "model_results.json").read_text(encoding="utf-8"))
forbidden = {"los_days", "los_recorded", "length_of_stay", "disp", "release_date", "death1", "death3", "death6", "death9", "y"}
check("no post-admission variable among predictors", not (set(mr["features"]) & forbidden), mr["features"])
from stroke_repro.models import make  # noqa: E402
m = make("LR", 1)
check("imputer and scaler inside the tuned pipeline", [s for s, _ in m.estimator.steps][:1] == ["impute"] and "scale" in dict(m.estimator.steps))
tv = pickle.load(open(C.RESTRICTED / "ckpt" / "temporal_primary.pkl", "rb"))
lab = P[P.labelled].set_index("patient_key")
cut = pd.Timestamp(mr["temporal_cutoff"])
check("temporal: all training admissions before cut-off", (lab.loc[tv["train_keys"], "entry_date"] < cut).all())
check("temporal: all test admissions on/after cut-off", (lab.loc[tv["test_keys"], "entry_date"] >= cut).all())
check("temporal: train and test disjoint", len(set(tv["train_keys"]) & set(tv["test_keys"])) == 0)
check("temporal cut-off = 70th percentile of eligible admission dates (outcome-independent)",
      P.entry_date.sort_values().iloc[int(0.7 * len(P))] == cut)
check("recalibration fitted in-fold only (CalibratedClassifierCV inside outer training fold)", "recalibration_nested" in
      (ROOT / "src" / "stroke_repro" / "stage3_models.py").read_text(encoding="utf-8") and "cal.fit(X.iloc[tr]" in (ROOT / "src" / "stroke_repro" / "stage3_models.py").read_text(encoding="utf-8"))

# ------------------------------------------------------------------ hard-coded statements in the manuscript prose
asc = json.loads((C.ANALYSIS / "ascertainment_summary.json").read_text(encoding="utf-8"))["primary"]
byp = pd.read_csv(C.ANALYSIS / "ascertainment_by_period_primary.csv", index_col=0)
comp = pd.read_csv(C.ANALYSIS / "labelled_vs_unresolved.csv").set_index("variable")
diag = json.loads((C.AUDIT / "outcome_field_diagnostics.json").read_text(encoding="utf-8"))
los = json.loads((C.AUDIT / "los_convention_check.json").read_text(encoding="utf-8"))
clog = pd.read_csv(C.AUDIT / "cleaning_and_integrity_log.csv").set_index("item")
miss = pd.read_csv(C.ANALYSIS / "predictor_missingness_labelled.csv", index_col=0).iloc[:, 0]
missE = pd.read_csv(C.ANALYSIS / "predictor_missingness_eligible.csv", index_col=0).iloc[:, 0]
ry = pd.read_csv(C.AUDIT / "recording_by_admission_year.csv", index_col=0)
dfs = pd.read_csv(C.COHORT / "duplicate_field_differences_summary.csv", index_col=0)
f = flows["primary"]
facts = {
    "62% of eligible labelled": round(100 * f["labelled"] / f["eligible"]) == 62,
    "labelled mortality 46% (2017-19) and 62% (2020)": (round(byp.loc["2017-19", "labelled_mortality_pct"]), round(byp.loc["2020", "labelled_mortality_pct"])) == (46, 62),
    "labelled 44% and 7%": (round(byp.loc["2017-19", "labelled_pct"]), round(byp.loc["2020", "labelled_pct"])) == (44, 7),
    "labelled 91% in 2010-12; 7-46% in 2017-23": round(byp.loc["2010-12", "labelled_pct"]) == 91 and round(byp.loc["2020", "labelled_pct"]) == 7 and round(byp.loc["2021-23", "labelled_pct"]) == 46,
    "217 of 219 causes of death with disposition death": diag["cause_of_death_recorded_by_disposition"]["death"] == 217 and sum(diag["cause_of_death_recorded_by_disposition"].values()) == 219,
    "14 misaligned rows": clog.loc["column_shift", "n_records"] == 14,
    "22 release before entry": clog.loc["flag_release_before_entry", "n_records"] == 22,
    "duplicate decisions 1/4/26/7": dl.decision.value_counts().to_dict() == {"D2_same_encounter_compatible": 26, "D3_same_encounter_outcome_conflict": 7, "D1_identifier_collision": 4, "D0_non_record": 1},
    "median 18 conflicting fields per duplicate group": dfs.loc["both_present_differ:total", "median"] == 18,
    "NIHSS 41% and mRS 48% missing (labelled)": (round(100 * miss["nihss"]), round(100 * miss["mrs"])) == (41, 48),
    "SpO2 69% missing; BMI 89% missing in registry": round(100 * miss["spo2"]) == 69 and round(100 * pd.to_numeric(rec.bmi_raw, errors="coerce").isna().mean()) == 89,
    "resp 37%, CRP 44%, cholesterol 46% missing": (round(100 * miss["resp_rate"]), round(100 * miss["crp"]), round(100 * miss["total_cholesterol"])) == (37, 44, 46),
    "imputer converged in 11 iterations": mr["imputer_iterations_final_model"] == 11,
    "20% of unresolved without disposition": round(100 * 119 / f["unresolved"]) == 20 and "119 (19.9%)" in comp.loc["Disposition: missing", "unresolved"],
    "NIHSS median 10 vs 7; mRS 4 vs 3": comp.loc["NIHSS", "labelled"].startswith("10.0") and comp.loc["NIHSS", "unresolved"].startswith("7.0")
        and comp.loc["Modified Rankin (admission)", "labelled"].startswith("4.0") and comp.loc["Modified Rankin (admission)", "unresolved"].startswith("3.0"),
    "haemorrhagic 41.6% vs 32.4%; NIHSS missing 41 vs 58%": "41.6%" in comp.loc["Haemorrhagic stroke", "labelled"] and "32.4%" in comp.loc["Haemorrhagic stroke", "unresolved"]
        and "41.3%" in comp.loc["NIHSS missing", "labelled"] and "58.3%" in comp.loc["NIHSS missing", "unresolved"],
    "temporal tree ensembles: manuscript range generated from outputs (TEnsLo/TEnsHi macros)": "\\TEnsLo--\\TEnsHi" in (ROOT / "manuscript" / "main.tex").read_text(encoding="utf-8"),
    "month-1 recorded ~90% early, 3-61% from 2015": ry.loc[2010:2012, "death1_recorded_pct"].between(88, 92).all() and ry.loc[2015:2023, "death1_recorded_pct"].min() >= 3 and ry.loc[2015:2023, "death1_recorded_pct"].max() < 61.5,
    "follow-up duration coded 1 / 30 / 0": ry.loc[2010:2016, "dur1_coded_1"].sum() > 400 and ry.loc[2017:2019, "dur1_coded_30"].sum() == 50 and ry.loc[2021:2023, "dur1_coded_0"].sum() == 26,
    "matching labelled mortality needs delta 2-4": True,
    "38% of eligible unresolved": round(100 * f["unresolved"] / f["eligible"]) == 38,
    "24 TIA excluded": f["excluded_tia"] == 24,
    "33 post-discharge events (A2)": f["class_counts"]["E2_month1_death_postdischarge"] == 33,
    "fold count used in text (macro) consistent": mr["nested_fold_diff_LR_minus_ClinRef"]["n_folds"] == 25,
    "temporal difference compatible with gain up to 0.07": round(mr["temporal_paired_LR_vs_ClinRef"]["diff_hi"], 2) == 0.07,
}
lb = pd.read_csv(C.COHORT / "los_by_disposition.csv").set_index("disposition")
tr = pd.read_csv(C.AUDIT / "tracker_count_reconciliation.csv").set_index("item").revision_value.astype(str)
facts.update({
    "in-hospital death median stay 4 d; 1 death and 11 home discharges at days 28-32": lb.loc["Died in hospital", "median"] == 4 and lb.loc["Died in hospital", "d28_32"] == 1 and lb.loc["Discharged home", "d28_32"] == 11,
    "37/38 groups any difference; 35/38 timing/outcome": tr["Groups with any field discrepancy"] == "37/38" and tr["Groups with timing/outcome-field differences"] == "35/38",
    "tracker counts 23 / 174 / 175 reproduced": (tr["Release before entry"], tr["LOS differs from date interval by >1 day"], tr["Union of the two timing flags"]) == ("23", "174", "175"),
    "28 groups = timing/outcome both-present differences": tr["  same, both rows non-missing"] == "28/38",
    "implausible dates rows 767/773/808": all(x in tr["Implausible dates"] for x in ["[767]", "[773]", "[808]"]),
    "22 release-before-entry within registry years": int(tr["  same, registry window"]) == 22,
    "date-derived stays >120 d (9 records)": int(rec.flag_date_stay_implausible.sum()) == 9,
    "A-4: 20 non-events from later contact": f["class_counts"]["N4_alive_later_contact"] == 20,
})
facts.update({
    "later contacts 87% in 2010-12, <=16% from 2017": round(byp.loc["2010-12", "later_contact_pct"]) == 87 and byp.loc[["2017-19", "2020", "2021-23"], "later_contact_pct"].max() <= 16.5,
    "N4 = 20 later-contact labels": asc["n4_alive_by_later_contact"] == 20 and f["class_counts"]["N4_alive_later_contact"] == 20,
    "27 candidate predictors": len(mr["features"]) == 27,
    "MI m=5 sensitivity present with between-draw SD": "between_draw_sd_of_fold_auc_mean" in mr["sensitivity_nested"]["multiple_imputation_m5"],
    "missing-indicator set includes CRP, urea, cholesterol, resp rate, mRS": set(["crp", "urea", "total_cholesterol", "resp_rate", "mrs"]) <= set(mr["missing_indicator_predictors"]),
    "A-7 tier effort figures present": all("patients_per_death" in t for t in mr["tiers_oof"]),
    "no coloured hyperlinks (print)": "hidelinks" in (ROOT / "manuscript" / "main.tex").read_text(encoding="utf-8"),
    "Discussion has >= 2 subsections": (ROOT / "manuscript" / "main.tex").read_text(encoding="utf-8").count("\\subsection{", (ROOT / "manuscript" / "main.tex").read_text(encoding="utf-8").index("\\section{Discussion}")) >= 2,
})
d = pd.read_csv(C.ANALYSIS / "mnar_delta_primary.csv")
lm = f["mortality_labelled_pct"]
e = d[d.reference == "early_era"].set_index("delta_odds_ratio").mortality_pct
pp = d[d.reference == "period_specific"].set_index("delta_odds_ratio").mortality_pct
facts["matching labelled mortality needs delta 2-4"] = (e[2.0] < lm <= e[4.0]) and (pp[4.0] < lm <= pp[8.0])
for k, v in facts.items():
    check("manuscript statement: " + k, v)

# ------------------------------------------------------------------ manuscript build
ms = ROOT / "manuscript"
logtxt = (ms / "main.log").read_text(encoding="utf-8", errors="ignore")
check("LaTeX: no errors", not re.search(r"^!", logtxt, re.M))
check("LaTeX: no undefined references/citations", "undefined" not in logtxt.lower())
txt = subprocess.run(["pdftotext", str(ms / "main.pdf"), "-"], capture_output=True, text=True).stdout
check("PDF: no unresolved '??' references", "??" not in txt)
check("PDF: no bracketed placeholders", not re.search(r"\[(IRB|GitHub|TODO|XX|placeholder)", txt, re.I))
pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(ms / "main.pdf")], capture_output=True, text=True).stdout).group(1))
check("PDF page count", pages > 10, pages)
blg = (ms / "main.blg").read_text(encoding="utf-8", errors="ignore") if (ms / "main.blg").exists() else ""
check("BibTeX: no warnings or errors", "There were" not in blg and "Warning--" not in blg, blg[-200:])

# ------------------------------------------------------------------ journal format and citation integrity (Prompt 6)
abs_txt = txt[txt.find("Abstract"):txt.find("Keywords")] if "Keywords" in txt else ""
abs_words = len(re.sub(r"^\s*\d+\s*$", "", abs_txt.replace("Abstract", "", 1), flags=re.M).split())
check("journal: structured abstract <= 250 words", 0 < abs_words <= 250, abs_words)
tex = (ms / "main.tex").read_text(encoding="utf-8")
kw = re.search(r"\\begin\{keyword\}(.*?)\\end\{keyword\}", tex, re.S).group(1)
check("journal: 1-7 keywords", 1 <= kw.count("\\sep") + 1 <= 7, kw.count("\\sep") + 1)
check("journal: generative-AI declaration present", "Declaration of generative AI" in tex)
hl = ROOT / "docs" / "highlights.txt"
if hl.exists():
    lines = [x.strip() for x in hl.read_text(encoding="utf-8").splitlines() if x.strip()]
    check("journal: 3-5 highlights, each <= 85 characters", 3 <= len(lines) <= 5 and all(len(x) <= 85 for x in lines), [len(x) for x in lines])
cites = set(k for g in re.findall(r"\\cite\{([^}]*)\}", tex) for k in g.split(","))
check("citations: off-topic or mis-keyed sources removed", not ({"ashu2022challenges", "kingston2019opportunities"} & cites))
check("citations: iScore/PLAN cited to original derivation papers", {"saposnik2011iscore", "odonnell2012plan"} <= cites)
check("citations: RECORD and STROBE cited", {"benchimol2015record", "vonelm2007strobe"} <= cites)
check("citations: Nkoke figures match source (15% readmitted)", "15\\% of patients discharged alive were readmitted" in tex)
rly = json.loads((C.ANALYSIS / "riley_samplesize_posthoc.json").read_text(encoding="utf-8"))["scenarios"]
check("manuscript statement: post hoc Riley criteria met only under AUROC-based R2",
      (not rly["conservative_15pct_of_max"]["met"]) and rly["from_observed_auroc"]["met"])
check("manuscript statement: four imputation sensitivity analyses (consistent wording)", "three imputation sensitivity" not in tex)
check("manuscript: observed-only mortality comes from the generated macro (no hard-coded 20.2%)", "20.2" not in tex and "\\MortObs" in tex)

# ------------------------------------------------------------------ data dictionary (received 2 Nov 2026)
check("dictionary checksum is one of the recorded versions", md5(C.DICT_XLSX) in C.DICT_KNOWN_MD5, C.DICT_XLSX.name)
dd = C.load_dictionary()
d1def = dd.loc[dd.name == "décès1", "description"].str.strip().iloc[0]
check("manuscript quotes the dictionary definition of death1 verbatim",
      "Death at Month 1, recording if the patient passed away within the first month" in d1def and
      "Death at Month 1, recording if the patient passed away within the first month" in tex)
check("dictionary: follow-up items described as 'after the stroke'", dd.description.astype(str).str.contains("after the stroke").sum() >= 20)
da = json.loads((C.AUDIT / "dictionary_audit.json").read_text(encoding="utf-8"))
check("dictionary: no value codes (statement in manuscript)", da["conformance"]["descriptions_with_value_codes"] == 0)
check("dictionary: no date-of-death variable", not dd.label.astype(str).str.contains("date of death", case=False).any())
check("dursuiv1 = 1 in 2010-16 and 30 in 2017-19 (dominant values)", True if (lambda t: t.loc[["2010-12", "2013-14", "2015-16"], ("duration followed1", "1.0")].sum() > 400 and t.loc["2017-19", ("duration followed1", "30.0")] >= 50)(pd.read_csv(C.AUDIT / "followup_duration_values_by_period.csv", header=[0, 1], index_col=0)) else False)
check("onset-anchored sensitivity analyses present", {"onset_anchor_gap", "onset_anchor_gap_unknown_excluded"} <= set(mr["sensitivity_nested"]))
check("A1: 217 of 219 recorded causes belong to in-hospital deaths (unchanged statement)", "217 of the 219 recorded causes" in tex)

# ------------------------------------------------------------------ response letter
from docx import Document  # noqa: E402
rl = ROOT / "outputs" / "reports" / "response_to_reviewers_NEURI-D-26-00184.docx"
if rl.exists():
    t = "\n".join(p.text for p in Document(rl).paragraphs)
    check("letter: no placeholders", not re.search(r"TODO|XX|\?\?|\[insert|tbd", t, re.I))
    check("letter: residual endpoint uncertainty stated (no dates of death; time origin not explicit)", "no dates of death" in t and "does not state the time origin explicitly" in t)
    check("letter: dictionary definition of death1 quoted", "passed away within the first month" in t)
    ids = ["R1-1", "R1-2", "R1-3", "R1-4", "R1-5"] + [f"A-{i}" for i in range(1, 14)] + ["E-1"]
    check("letter: all 19 tracker items answered", all(f"{i} — " in t for i in ids))
    check("letter: verbatim reviewer text present", "definitional contradiction arises" in t and "statistical logical error" in t)
    locs = re.findall(r"p\. (\d+), line (\d+)", t)
    check("letter: every page cited exists", all(1 <= int(p_) <= pages for p_, _ in locs), len(locs))
else:
    check("letter exists", False)

rep = pd.DataFrame(checks)
(ROOT / "outputs" / "reports" / "verification_report.json").write_text(json.dumps(checks, indent=1), encoding="utf-8")
print(rep.to_string())
print(f"\n{rep.passed.sum()}/{len(rep)} checks passed")
sys.exit(0 if rep.passed.all() else 1)
