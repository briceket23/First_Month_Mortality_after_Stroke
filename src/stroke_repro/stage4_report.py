"""Stage 4: regenerate every manuscript figure, LaTeX table and numeric macro from analysis outputs.

Nothing in this file computes a new statistic from patient data except plotting coordinates;
all reported numbers are read from outputs/*.json|csv written by stages 1-3.
"""
import json
import pickle

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve

from . import config as C

PAL = {"LR": "#2a78d6", "ClinRef": "#eb6834", "RF": "#1baf7a", "HGB": "#eda100", "XGB": "#e87ba4"}
NAMES = {"LR": "L2 logistic regression (primary)", "ClinRef": "Clinical-reference model", "RF": "Random forest",
         "HGB": "Histogram gradient boosting", "XGB": "XGBoost"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "lines.linewidth": 2,
                     "savefig.dpi": 300, "figure.dpi": 100, "legend.frameon": False})

MS = C.ROOT / "manuscript"
MFIG, MTAB = MS / "figures", MS / "tables"


def f3(x):
    return f"{x:.3f}"


def f2(x):
    v = f"{x:.2f}"
    return "0.00" if v == "-0.00" else v


def pfmt(p):
    return "$<$0.001" if p < 0.001 else f"{p:.3f}" if p < 0.01 else f"{p:.2f}"


def pct(x, d=1):
    return f"{x:.{d}f}"


def ci3(a, lo, hi):
    return f"{a:.3f} ({lo:.3f}--{hi:.3f})"


def num(n):
    return f"{int(n):,}".replace(",", "{,}")


def save(fig, name):
    for d in (C.FIG, MFIG):
        d.mkdir(parents=True, exist_ok=True)
        fig.savefig(d / f"{name}.png", bbox_inches="tight")
    plt.close(fig)


def table(name, caption, label, header, rows, colspec, note=None, size="\\small"):
    import re as _re
    colspec = _re.sub(r"p\{", r">{\\raggedright\\arraybackslash}p{", colspec)
    body = "\n".join(" & ".join(r) + r" \\" for r in rows)
    tex = (f"\\begin{{table}}[htbp]\\centering{size}\n\\caption{{{caption}}}\\label{{{label}}}\n"
           f"\\begin{{tabular}}{{{colspec}}}\n\\toprule\n{' & '.join(header)} \\\\\n\\midrule\n{body}\n\\bottomrule\n\\end{{tabular}}\n")
    if note:
        tex += f"\\par\\smallskip\\begin{{minipage}}{{0.95\\linewidth}}\\footnotesize {note}\\end{{minipage}}\n"
    tex += "\\end{table}\n"
    (MTAB / f"{name}.tex").write_text(tex, encoding="utf-8")


def main():
    MTAB.mkdir(parents=True, exist_ok=True)
    flows = json.loads((C.COHORT / "cohort_flows.json").read_text(encoding="utf-8"))
    orig = json.loads((C.AUDIT / "reproduction_of_submitted_counts.json").read_text(encoding="utf-8"))
    asc = json.loads((C.ANALYSIS / "ascertainment_summary.json").read_text(encoding="utf-8"))
    mr = json.loads((C.ANALYSIS / "model_results.json").read_text(encoding="utf-8"))
    rec_year = pd.read_csv(C.AUDIT / "recording_by_admission_year.csv", index_col=0)
    byp = pd.read_csv(C.ANALYSIS / "ascertainment_by_period_primary.csv", index_col=0)
    delta = pd.read_csv(C.ANALYSIS / "mnar_delta_primary.csv")
    comp = pd.read_csv(C.ANALYSIS / "labelled_vs_unresolved.csv")
    fd = pickle.load(open(C.RESTRICTED / "ckpt" / "figdata.pkl", "rb"))
    shp = pickle.load(open(C.RESTRICTED / "ckpt" / "shap.pkl", "rb"))
    coefs = pd.read_csv(C.ANALYSIS / "lr_coefficients_bootstrap.csv", index_col=0)
    pimp = pd.read_csv(C.ANALYSIS / "permutation_importance_temporal_test.csv", index_col=0)
    shift = pd.read_csv(C.ANALYSIS / "temporal_shift_primary.csv")
    P = flows["primary"]
    S = flows["strict_timing"]
    A = asc["primary"]
    cc = P["class_counts"]
    mac = {}

    # ------------------------------------------------------------- macros
    mac.update(Nreg=num(P["source_rows"]), Nrecon=num(P["after_reconciliation"]), Nelig=num(P["eligible"]),
               Nlab=num(P["labelled"]), Ndeaths=num(P["deaths"]), Nunres=num(P["unresolved"]),
               Mortlab=pct(P["mortality_labelled_pct"]),
               MortlabLo=pct(A["labelled_mortality_ci"][0]), MortlabHi=pct(A["labelled_mortality_ci"][1]),
               NexBlank=num(P["excluded_blank_records"]), NexDate=num(P["excluded_no_valid_admission_date"]),
               NexAge=num(P["excluded_age_lt18"]), NexTIA=num(P["excluded_tia"]),
               NEone=num(cc.get("E1_inhosp_death_le30", 0)), NEtwo=num(cc.get("E2_month1_death_postdischarge", 0)),
               NNone=num(cc.get("N1_inhosp_death_gt30", 0)), NNtwo=num(cc.get("N2_month1_alive", 0)),
               NNthree=num(cc.get("N3_discharged_alive_gt30", 0)), NNfour=num(cc.get("N4_alive_later_contact", 0)),
               NstrictLab=num(S["labelled"]), NstrictDeaths=num(S["deaths"]), Mortstrict=pct(S["mortality_labelled_pct"]),
               BoundLo=pct(A["bound_all_unresolved_alive_pct"]), BoundHi=pct(A["bound_all_unresolved_dead_pct"]),
               Mortinhosp=pct(A["inhosp_30d_mortality_pct"]), MortinhospLo=pct(A["inhosp_30d_mortality_ci"][0]),
               MortinhospHi=pct(A["inhosp_30d_mortality_ci"][1]), Ninhospden=num(A["inhosp_denominator_known_disposition"]),
               Mortipw=pct(A["ipw_mortality_pct"]), MortipwLo=pct(A["ipw_mortality_ci"][0]), MortipwHi=pct(A["ipw_mortality_ci"][1]),
               Nipwpop=num(A["ipw_population"]), Nnodisp=num(A["excluded_from_ipw_no_disposition"]),
               IPWess=f"{A['ipw_diagnostics']['ess']:.0f}", IPWcap=f"{A['ipw_diagnostics']['weight_cap_p99']:.2f}",
               IPWmax=f"{A['ipw_diagnostics']['weight_max_untruncated']:.1f}", IPWntrunc=str(A['ipw_diagnostics']['n_truncated']),
               OrigObs=num(orig["observed"]), OrigInf=num(orig["inferred"]), OrigUnl=num(orig["unlabelled"]),
               OrigLab=num(orig["labelled"]), OrigDeaths=num(orig["deaths"]), OrigMort=pct(orig["mortality_pct"]),
               OrigObsDeaths=num(orig["observed_only_deaths"]))
    d = delta.set_index(["reference", "delta_odds_ratio"]).mortality_pct
    mac.update(DeltaMARearly=pct(d[("early_era", 1.0)]), DeltaMARper=pct(d[("period_specific", 1.0)]),
               DeltaMin=pct(delta.mortality_pct.min()), DeltaMax=pct(delta.mortality_pct.max()),
               DeltaTwoEarly=pct(d[("early_era", 2.0)]), DeltaFourEarly=pct(d[("early_era", 4.0)]))
    pdr = A["postdischarge_risk_by_period"]
    k1 = sum(int(pdr[p].split("/")[0]) for p in ["2010-12", "2013-14"]); n1 = sum(int(pdr[p].split("/")[1]) for p in ["2010-12", "2013-14"])
    k2 = sum(int(pdr[p].split("/")[0]) for p in ["2015-16", "2017-19", "2020", "2021-23"]); n2 = sum(int(pdr[p].split("/")[1]) for p in ["2015-16", "2017-19", "2020", "2021-23"])
    mac.update(PDearlyK=str(k1), PDearlyN=str(n1), PDearly=pct(100 * k1 / n1), PDlateK=str(k2), PDlateN=str(n2), PDlate=pct(100 * k2 / n2))
    ry = rec_year
    e = ry.loc[2010:2012]; l = ry.loc[2015:2023]
    mac.update(IHDeathOneEarly=f"{int(e.inhosp_deaths_with_death1_yes.sum())}/{int(e.inhosp_deaths.sum())}",
               IHDeathOneLate=f"{int(l.inhosp_deaths_with_death1_yes.sum())}/{int(l.inhosp_deaths.sum())}",
               DispMissTwenty=str(int(ry.loc[2020, "disp_missing"])), AdmTwenty=str(int(ry.loc[2020, "admissions"])),
               OtherLate=str(int(ry.loc[2021:2023, "disp_other"].sum())), AdmLate=str(int(ry.loc[2021:2023, "admissions"].sum())))
    # models
    NP = mr["nested_primary"]
    for m, tag in [("LR", "LR"), ("ClinRef", "CR"), ("RF", "RF"), ("HGB", "HGB"), ("XGB", "XGB")]:
        mac[f"Nest{tag}"] = f3(NP[m]["auroc"]); mac[f"Nest{tag}Lo"] = f3(NP[m]["auroc_lo"]); mac[f"Nest{tag}Hi"] = f3(NP[m]["auroc_hi"])
        mac[f"Nest{tag}Fold"] = f"{NP[m]['fold_auc_mean']:.3f}"; mac[f"Nest{tag}FoldSD"] = f"{NP[m]['fold_auc_sd']:.3f}"
        mac[f"Nest{tag}Slope"] = f2(NP[m]["slope_per_repeat_mean"]); mac[f"Nest{tag}Int"] = f2(NP[m]["intercept_per_repeat_mean"])
        mac[f"Nest{tag}Brier"] = f3(NP[m]["brier_per_repeat_mean"])
        mac[f"Nest{tag}AP"] = f3(NP[m]["auprc"])
    mac["NestLRipwAUC"], mac["NestLRipwInt"], mac["NestLRipwSlope"] = f3(NP["LR"]["ipw_auroc"]), f2(NP["LR"]["ipw_intercept"]), f2(NP["LR"]["ipw_slope"])
    mac["NestLRipwMeanPred"], mac["NestLRipwObs"] = pct(100 * NP["LR"]["ipw_mean_pred"]), pct(100 * NP["LR"]["ipw_obs_rate"])
    pr = mr["nested_paired_LR_vs_ClinRef"]
    mac.update(PairNestDiff=f3(pr["diff"]), PairNestLo=f3(pr["diff_lo"]), PairNestHi=f3(pr["diff_hi"]), PairNestP=pfmt(pr['p']))
    px = mr["nested_paired_XGB_vs_LR"]
    mac.update(PairXGBDiff=f3(px["diff"]), PairXGBLo=f3(px["diff_lo"]), PairXGBHi=f3(px["diff_hi"]), PairXGBP=pfmt(px['p']))
    pf = mr["nested_fold_diff_LR_minus_ClinRef"]
    mac.update(FoldDiffMean=f3(pf["mean"]), FoldDiffSD=f3(pf["sd"]), FoldLRBetter=str(pf["n_LR_better"]), NFolds=str(pf["n_folds"]))
    T = mr["temporal_primary"]
    mac.update(TCut=mr["temporal_cutoff"], TNtr=num(T["n_train"]), TEtr=num(T["events_train"]), TNte=num(T["n_test"]), TEte=num(T["events_test"]),
               TPrev=pct(100 * T["events_test"] / T["n_test"]))
    for m, tag in [("LR", "LR"), ("ClinRef", "CR"), ("RF", "RF"), ("HGB", "HGB"), ("XGB", "XGB")]:
        mac[f"T{tag}"] = f3(T[m]["auroc"]); mac[f"T{tag}Lo"] = f3(T[m]["auroc_lo"]); mac[f"T{tag}Hi"] = f3(T[m]["auroc_hi"])
        mac[f"T{tag}Slope"] = f2(T[m]["slope"]); mac[f"T{tag}Int"] = f2(T[m]["intercept"]); mac[f"T{tag}Brier"] = f3(T[m]["brier"])
    ens = [T[m]["auroc"] for m in ("RF", "HGB", "XGB")]
    mac["TEnsLo"], mac["TEnsHi"] = f2(min(ens)), f2(max(ens))          # tree-ensemble range on the temporal test set (generated, not typed)
    tp = mr["temporal_paired_LR_vs_ClinRef"]
    mac.update(TPairDiff=f3(tp["diff"]), TPairLo=f3(tp["diff_lo"]), TPairHi=f3(tp["diff_hi"]), TPairP=pfmt(tp['p']))
    tw = mr["temporal_primary_ipw_LR"]
    mac.update(TLRipw=f3(tw["auroc"]), TLRipwLo=f3(tw["auroc_boot_ci"][0]), TLRipwHi=f3(tw["auroc_boot_ci"][1]),
               TLRipwInt=f2(tw["intercept"]), TLRipwSlope=f2(tw["slope"]))
    for nm, tag in [("strict_timing", "St"), ("observed_only", "Ob")]:
        t = mr[f"temporal_{nm}"]
        mac.update({f"T{tag}N": num(t["n_test"]), f"T{tag}E": num(t["events_test"]), f"T{tag}Ntr": num(t["n_train"]), f"T{tag}Etr": num(t["events_train"]),
                    f"T{tag}LR": f3(t["LR"]["auroc"]), f"T{tag}LRLo": f3(t["LR"]["auroc_lo"]), f"T{tag}LRHi": f3(t["LR"]["auroc_hi"])})
    mac["TMember"] = f3(mr["temporal_membership_auc"][0])
    rc = mr["recalibration_oof"]
    mac.update({f"Rec{t}{k.capitalize()}": (f3 if k == "brier" else f2)(rc[src][f"{k}_per_repeat_mean"])
                for t, src in [("Platt", "sigmoid"), ("Iso", "isotonic"), ("Unc", "uncalibrated")] for k in ("slope", "intercept", "brier")})
    sh = mr["shap_rank_spearman_LR_vs_XGB"]
    mac.update(ShapRho=f2(sh["rho"]), ShapRhoLo=f2(sh["ci_feature_bootstrap"][0]), ShapRhoHi=f2(sh["ci_feature_bootstrap"][1]), NFeat=str(len(mr["features"])))
    mac.update(EPV=f"{mr['epv_candidate_df']:.1f}", LRC=f"{mr['lr_final_C']:g}",
               MIdrawSD=f"{mr['sensitivity_nested']['multiple_imputation_m5']['between_draw_sd_of_fold_auc_mean']:.3f}",
               NlowMiss=str(len(mr["low_missing_predictors"])), NhiMiss=str(len(mr["missing_indicator_predictors"])),
               LaterRec=num(A["later_contact_recorded"]), LaterPct=pct(A["later_contact_pct"]), LaterNoDone=num(A["later_contact_without_death1"]),
               LaterAliveNoDone=num(A["later_alive_without_death1"]))
    # data dictionary audit (stage 1e)
    da = json.loads((C.AUDIT / "dictionary_audit.json").read_text(encoding="utf-8"))
    cf, od = da["conformance"], da["onset_delay"]
    mac.update(DictRows=str(cf["dictionary_rows"]), DictMatched=str(cf["dictionary_labels_matched_exactly"]),
               DictNoType=str(cf["variables_without_type"]), NtwoDelay=num(od["N2_with_delay_recorded"]),
               NtwoGap=num(od["N2_with_delay_gt_threshold"]), NtwoAll=num(od["N2_labels"]),
               DelayMed=f"{od['quantiles_all_rows']['0.5']:.0f}", DelayQthree=f"{od['quantiles_all_rows']['0.75']:.0f}",
               DelayHeap=f"{100 * od['share_at_multiples_of_24']:.0f}")
    dv = {r["period"]: r for r in da["death1_vs_definition_inhospital"]}
    late = [dv[k] for k in ("2015-16", "2017-19", "2020", "2021-23")]
    mac.update(DictIHearlyK=dv["2010-12"]["Yes"], DictIHearlyN=dv["2010-12"]["n"],
               DictIHlateK=str(sum(int(r["Yes"]) for r in late)), DictIHlateN=str(sum(int(r["n"]) for r in late)))
    # post hoc Riley et al. (2020) check, written by tools/riley_samplesize.py (run before this stage)
    rl = json.loads((C.ANALYSIS / "riley_samplesize_posthoc.json").read_text(encoding="utf-8"))["scenarios"]
    a, b = rl["conservative_15pct_of_max"], rl["from_observed_auroc"]
    assert C.SYNTHETIC or ((not a["met"]) and b["met"]), "manuscript wording assumes conservative criterion unmet and AUROC-based criterion met"
    mac["Ncand"] = str(json.loads((C.ANALYSIS / "riley_samplesize_posthoc.json").read_text(encoding="utf-8"))["candidate_parameters"])
    mac.update(RileyConsN=num(a["n_required"]), RileyConsE=num(a["events_required"]), RileyConsRsq=f2(a["anticipated_r2cs"]),
               RileyCN=num(b["n_required"]), RileyCE=num(b["events_required"]), RileyCRsq=f2(b["anticipated_r2cs"]))
    ob = mr["sensitivity_nested"]["observed_only"]
    mac["MortObs"] = pct(100 * ob["events"] / ob["n"]); mac["ObsN"] = num(ob["n"]); mac["ObsE"] = num(ob["events"])
    sens = mr["sensitivity_nested"]
    for k, tag in [("strict_timing", "St"), ("observed_only", "Ob"), ("dup_keep_first", "Kf"), ("dup_exclude_conflicts", "Xc"),
                   ("era_2010_2016", "Era"), ("complete_nihss", "Cn"), ("nihss_missing_indicator", "Ni"), ("gcs_nihss_ratio", "Ra"),
                   ("multiple_imputation_m5", "Mi"), ("ipw_weighted_fit", "Iw"), ("missing_indicators_all", "Ma"),
                   ("low_missing_predictors", "Lm"), ("no_later_contact", "Nl"),
                   ("onset_anchor_gap", "Og"), ("onset_anchor_gap_unknown_excluded", "Ou")]:
        mac[f"Sens{tag}"] = f3(sens[k]["LR"]["auroc"])
        mac[f"Sens{tag}N"] = num(sens[k]["n"]); mac[f"Sens{tag}E"] = num(sens[k]["events"])
    for k in ["strict_timing", "observed_only", "era_2010_2016", "complete_nihss"]:
        pass
    ti = pd.DataFrame(mr["tiers_oof"]).set_index("tier"); tt = pd.DataFrame(mr["tiers_temporal"]).set_index("tier")
    for tg, df_ in [("O", ti), ("T", tt)]:
        for tier in ["Low", "Moderate", "High"]:
            r = df_.loc[tier]
            mac[f"Tier{tg}{tier}N"] = str(int(r.n)); mac[f"Tier{tg}{tier}Pct"] = pct(r.pct_patients)
            mac[f"Tier{tg}{tier}Mort"] = pct(r.mortality) if r.n else "--"
            mac[f"Tier{tg}{tier}Cap"] = pct(r.pct_deaths)
    (MTAB / "macros.tex").write_text("\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in mac.items()) + "\n")
    json.dump(mac, open(C.TAB / "macros.json", "w", encoding="utf-8"), indent=1)

    # ------------------------------------------------------------- tables
    names = {"E1_inhosp_death_le30": ("In-hospital death, stay $\\le$30 d", "1", "Hospital record", "Established (A1)"),
             "E2_month1_death_postdischarge": ("Death recorded in month-1 field after discharge", "1", "\\texttt{death1}", "Assumption A2 (dictionary-supported)"),
             "N1_inhosp_death_gt30": ("In-hospital death after day 30", "0", "Hospital record", "Established (A1)"),
             "N2_month1_alive": ("Alive at month-1 contact", "0", "\\texttt{death1}", "Established to month 1 after stroke"),
             "N3_discharged_alive_gt30": ("Discharged alive after day 30", "0", "Hospital record", "Established"),
             "N4_alive_later_contact": ("Alive at month-3/6/9 contact", "0", "\\texttt{death3/6/9}", "Established"),
             "U_discharged_alive_no_followup": ("Discharged alive by day 30, no follow-up", "--", "--", "Unresolved"),
             "U_disposition_missing_no_followup": ("No disposition, no follow-up", "--", "--", "Unresolved"),
             "U_other_disposition_no_followup": ("``Other'' disposition, no follow-up", "--", "--", "Unresolved"),
             "U_contradictory_status": ("Contradictory status fields", "--", "--", "Unresolved"),
             "U_los_conflict_at_boundary": ("Stay measures disagree across day 30", "--", "--", "Unresolved"),
             "U_record_misaligned": ("Column-misaligned record", "--", "--", "Unresolved"),
             "U_duplicate_outcome_conflict": ("Duplicate rows disagree on outcome", "--", "--", "Unresolved"),
             "U_inhosp_death_timing_unknown": ("In-hospital death, stay unknown", "--", "--", "Unresolved"),
             "U_later_death_timing_unknown": ("Death at month 3--9 only, timing unknown", "--", "--", "Unresolved")}
    rows = []
    for k, v in names.items():
        n = cc.get(k, 0)
        if n:
            tcls = {"E1_inhosp_death_le30": "I", "N1_inhosp_death_gt30": "I", "N3_discharged_alive_gt30": "I",
                    "E2_month1_death_postdischarge": "R", "N2_month1_alive": "R", "N4_alive_later_contact": "R"}.get(k, "U")
            rows.append([v[0], v[1], v[2], v[3], tcls, num(n), pct(100 * n / P["eligible"])])
    table("recon", f"Outcome provenance under the revised endpoint (eligible patients, $n={num(P['eligible'])}$). "
          "A1: disposition `death' denotes death before leaving the unit, with the stay ending at death. "
          "A2: a post-discharge death recorded in the month-1 field occurred within 30 days of admission.",
          "tab:recon", ["Evidence class", "Label", "Source", "Timing", "Grade", "$n$", "\\%"], rows, "p{4.8cm}cp{2.0cm}p{2.0cm}crr",
          note=f"Labelled: {num(P['labelled'])}; deaths: {num(P['deaths'])}; unresolved: {num(P['unresolved'])}. Grade (pre-specified evidence grades): "
               "E1/E0, event or survival confirmed by documented dates or an unequivocal field definition; R, recorded status whose time origin is not established; "
               "I, inferred from disposition and stay under stated assumptions; U, unresolved or conflicting; X, undocumented code. No label currently reaches E1/E0.")

    rows = [[r.variable.replace("%", "\\%"), r.labelled.replace("%", "\\%"), r.unresolved.replace("%", "\\%"),
             "" if pd.isna(r.smd) else f"{r.smd:.2f}"] for r in comp.itertuples()]
    table("selbias", f"Labelled versus unresolved eligible patients (labelled $n={num(P['labelled'])}$; unresolved $n={num(P['unresolved'])}$). "
          "Continuous variables: median [IQR] (number with a recorded value); SMD, standardised mean difference.",
          "tab:selbias", ["Characteristic", "Labelled", "Unresolved", "SMD"], rows, "p{3.6cm}p{3.9cm}p{3.9cm}r", size="\\scriptsize")

    rows = []
    for per, r in byp.iterrows():
        rows.append([per, num(r.eligible), f"{int(r.labelled)} ({r.labelled_pct:.1f})", f"{int(r.deaths)}",
                     f"{r.labelled_mortality_pct:.1f}", f"{int(r.inhosp_30d_deaths)}/{int(r.known_disposition)} ({r.inhosp_30d_pct_known_disp:.1f})",
                     f"{int(r.later_contact_recorded)} ({r.later_contact_pct:.1f})", str(int(r.n4_alive_by_later_contact))])
    table("period", "Outcome ascertainment and mortality by admission period (revised primary endpoint). In-hospital 30-day deaths "
          "are shown over patients with a recorded death, home or transfer disposition. Later contact: any month-3, -6 or -9 status recorded; "
          "N4: patients whose survival label comes only from such a contact.",
          "tab:period", ["Period", "Eligible", "Labelled (\\%)", "Deaths", "Labelled mortality, \\%", "In-hospital 30-d deaths (\\%)", "Later contact (\\%)", "N4"],
          rows, "lrrrrrrr", size="\\scriptsize")

    rows = [["Labelled-subset proportion", f"{pct(P['mortality_labelled_pct'])} ({mac['MortlabLo']}--{mac['MortlabHi']})", "Labelled patients only; selectively ascertained"],
            ["All unresolved survived (lower bound)", mac["BoundLo"], "Logical bound"],
            ["All unresolved died (upper bound)", mac["BoundHi"], "Logical bound"],
            ["In-hospital death within 30 days", f"{mac['Mortinhosp']} ({mac['MortinhospLo']}--{mac['MortinhospHi']})", f"Known disposition, $n={mac['Ninhospden']}$; excludes post-discharge deaths"],
            ["Inverse-probability-of-observation weighted", f"{mac['Mortipw']} ({mac['MortipwLo']}--{mac['MortipwHi']})", f"MAR given admission data, period and disposition; $n={mac['Nipwpop']}$"],
            ["Pattern-mixture, $\\delta=1$ (2010--14 post-discharge risk)", mac["DeltaMARearly"], "MAR-type reference"],
            ["Pattern-mixture, $\\delta=1$ (period-specific)", mac["DeltaMARper"], "MAR within period"],
            ["Pattern-mixture, $\\delta$ from 0.25 to 8", f"{mac['DeltaMin']}--{mac['DeltaMax']}", "MNAR sensitivity range"]]
    table("reconbounds", f"Estimates of 30-day mortality among all eligible patients ($n={num(P['eligible'])}$). "
          "Only the bounds are assumption-free; no single value is identified by the data.",
          "tab:reconbounds", ["Estimator", "Mortality, \\% (95\\% CI)", "Population / assumption"], rows, "p{5.0cm}p{2.9cm}p{5.4cm}")

    rows = []
    for ref, lab_ in [("early_era", "2010--14 post-discharge risk"), ("period_specific", "Period-specific post-discharge risk")]:
        sub = delta[delta.reference == ref]
        rows.append([lab_] + [pct(v) for v in sub.mortality_pct])
    table("delta", "Pattern-mixture (delta-adjustment) analysis: estimated 30-day mortality (\\%) among all eligible patients when the odds of death "
          "in unresolved patients are multiplied by $\\delta$ relative to comparable resolved patients.",
          "tab:delta", ["Reference"] + [f"$\\delta={x:g}$" for x in delta[delta.reference == 'early_era'].delta_odds_ratio], rows, "lrrrrrr")

    rows = []
    for m in ["LR", "ClinRef", "RF", "HGB", "XGB"]:
        r = NP[m]
        rows.append([NAMES[m], ci3(r["auroc"], r["auroc_lo"], r["auroc_hi"]), f"{r['fold_auc_mean']:.3f} $\\pm$ {r['fold_auc_sd']:.3f}",
                     f3(r["auprc"]), f2(r["slope_per_repeat_mean"]), f2(r["intercept_per_repeat_mean"]), f3(r["brier_per_repeat_mean"])])
    table("nestedcv", f"Nested cross-validation ({C.OUTER_FOLDS} outer folds $\\times$ {C.OUTER_REPEATS} repeats; inner {C.INNER_FOLDS}-fold tuning) on the labelled cohort "
          f"($n={num(mr['n'])}$, {num(mr['events'])} deaths). Pooled AUROC uses out-of-fold predictions averaged over repeats (DeLong 95\\% CI); "
          "fold AUROC is mean $\\pm$ SD over the 25 outer test folds. Calibration slope, intercept and Brier score are means over the 5 repeats of pooled out-of-fold predictions.",
          "tab:nestedcv", ["Model", "Pooled AUROC (95\\% CI)", "Fold AUROC", "AUPRC", "Slope", "Intercept", "Brier"], rows,
          "p{3.6cm}p{2.7cm}p{2.1cm}rrrr", size="\\scriptsize")

    rows = [["Nested CV (pooled out-of-fold)", f3(pr["auc1"]), f3(pr["auc2"]), f"{f3(pr['diff'])} ({f3(pr['diff_lo'])} to {f3(pr['diff_hi'])})", pfmt(pr['p'])],
            [f"Temporal test ($n={num(T['n_test'])}$)", f3(tp["auc1"]), f3(tp["auc2"]), f"{f3(tp['diff'])} ({f3(tp['diff_lo'])} to {f3(tp['diff_hi'])})", pfmt(tp['p'])]]
    table("paireddelong", "Paired comparison of the primary model with the clinical-reference model (DeLong). A non-significant difference is "
          "not evidence of equivalence; no equivalence margin was pre-specified.",
          "tab:paireddelong", ["Setting", "AUROC primary", "AUROC reference", "Difference (95\\% CI)", "$p$"], rows, "p{4.0cm}rrp{3.4cm}r")

    rows = []
    for nm, lab_ in [("primary", "Revised primary endpoint"), ("strict_timing", "Strict admission-timed endpoint"), ("observed_only", "Observed-only \\texttt{death1}")]:
        t = mr[f"temporal_{nm}"]
        for m in ["LR", "ClinRef"] + (["RF", "HGB", "XGB"] if nm == "primary" else []):
            rows.append([lab_ if m == "LR" else "", NAMES[m].replace(" (primary)", ""), f"{num(t['n_train'])}/{num(t['events_train'])}",
                         f"{num(t['n_test'])}/{num(t['events_test'])}", ci3(t[m]["auroc"], t[m]["auroc_lo"], t[m]["auroc_hi"]),
                         f2(t[m]["slope"]), f2(t[m]["intercept"])])
    table("temporal", f"Temporal validation: training on admissions before {mr['temporal_cutoff']} and testing on later admissions (cut-off = 70th "
          "percentile of admission dates among all eligible patients; identical for every endpoint). $n$/deaths shown for training and test sets.",
          "tab:temporal", ["Endpoint", "Model", "Train $n$/deaths", "Test $n$/deaths", "AUROC (95\\% CI)", "Slope", "Intercept"], rows,
          "p{2.6cm}p{2.8cm}rrp{2.6cm}rr", size="\\scriptsize")

    rows = [[r.variable.replace("_", " ").replace("pct", "(\\%)"), str(r.early), str(r.late),
             "" if pd.isna(r.early_missing_pct) else f"{r.early_missing_pct:.1f}", "" if pd.isna(r.late_missing_pct) else f"{r.late_missing_pct:.1f}"]
            for r in shift.itertuples()]
    table("tempshift", f"Case mix, missingness and ascertainment before and after the temporal cut-off ({mr['temporal_cutoff']}), all eligible patients. "
          "Means for continuous and binary variables.", "tab:tempshift", ["Characteristic", "Before", "After", "Missing before (\\%)", "Missing after (\\%)"],
          rows, "p{5.6cm}rrrr", size="\\scriptsize")

    rows = []
    for k, lab_ in [("uncalibrated", "Primary model, no recalibration (pre-specified)"), ("sigmoid", "In-fold Platt scaling"), ("isotonic", "In-fold isotonic regression")]:
        r = rc[k]
        rows.append([lab_, f3(r["auroc"]), f2(r["slope_per_repeat_mean"]), f2(r["intercept_per_repeat_mean"]), f3(r["brier_per_repeat_mean"])])
    table("recal", "Calibration of out-of-fold predictions (nested CV). Recalibration maps were fitted inside each outer training fold only; "
          "no method was selected on test data. Slope, intercept and Brier score are means over the 5 repeats.", "tab:recal", ["Model", "AUROC", "Slope", "Intercept", "Brier"], rows, "p{5.6cm}rrrr")

    rows = []
    for tg, df_, lab_ in [("O", ti, "Pooled out-of-fold"), ("T", tt, "Temporal test")]:
        for tier in ["Low", "Moderate", "High"]:
            r = df_.loc[tier]
            rows.append([lab_ if tier == "Low" else "", tier, f"{int(r.n)} ({r.pct_patients:.1f})", str(int(r.deaths)),
                         "--" if r.n == 0 else f"{r.mortality:.1f} ({r.mort_lo:.1f}--{r.mort_hi:.1f})", f"{r.pct_deaths:.1f}",
                         "--" if not r.deaths else f"{r.patients_per_death:.1f}"])
    lo, hi = C.RISK_TIERS
    table("tiers", f"Risk tiers at pre-specified absolute-risk cut-points (low $<${int(lo*100)}\\%, high $\\ge${int(hi*100)}\\%). Mortality refers to the labelled, "
          "selectively ascertained cohort and is not a population risk. Patients per death: number of patients in the tier for each death it contains, "
          "an illustration of follow-up effort per death reached if follow-up were directed to that tier.", "tab:tiers",
          ["Setting", "Tier", "Patients (\\%)", "Deaths", "Mortality \\% (95\\% CI)", "\\% of deaths", "Patients per death"], rows, "llrrrrr", size="\\footnotesize")
    mac.update(TierOHighPPD=f"{ti.loc['High', 'patients_per_death']:.1f}", TierOLowPPD=f"{ti.loc['Low', 'patients_per_death']:.0f}",
               TierOModPPD=f"{ti.loc['Moderate', 'patients_per_death']:.1f}")

    sl = [("strict_timing", "Strict admission-timed endpoint"), ("observed_only", "Observed-only \\texttt{death1}"),
          ("dup_keep_first", "Duplicates: keep first row"), ("dup_exclude_conflicts", "Duplicates: exclude conflicting groups"),
          ("era_2010_2016", "Admissions 2010--2016 only"), ("complete_nihss", "Complete NIHSS only"),
          ("no_later_contact", "Later-contact survival (N4) treated as unresolved"),
          ("onset_anchor_gap", "Stroke-anchored month 1: \\texttt{death1} = No with onset-to-arrival delay $>$72 h unresolved"),
          ("onset_anchor_gap_unknown_excluded", "As above, and \\texttt{death1} = No with unknown delay unresolved"),
          ("nihss_missing_indicator", "NIHSS missingness indicator added"), ("missing_indicators_all", "Missingness indicators for all predictors $>$20\\% missing"),
          ("low_missing_predictors", "Predictors $<$10\\% missing only"), ("gcs_nihss_ratio", "Glasgow-to-NIHSS ratio added"),
          ("multiple_imputation_m5", "Multiple imputation, $m=5$ posterior draws"), ("ipw_weighted_fit", "IPW-weighted fitting and evaluation")]
    rows = []
    for k, lab_ in sl:
        s = sens[k]
        cr = f3(s["ClinRef"]["auroc"]) if "ClinRef" in s else "--"
        lr_ = s["LR"]
        rows.append([lab_, f"{num(s['n'])}/{num(s['events'])}", ci3(lr_["auroc"], lr_["auroc_lo"], lr_["auroc_hi"]) if "auroc_lo" in lr_ else f3(lr_["auroc"]), cr,
                     f2(lr_["slope"]), f2(lr_["intercept"])])
    table("sens", "Sensitivity analyses (nested CV, 5 outer folds $\\times$ 2 repeats). IPW row: weighted AUROC without DeLong interval. "
          f"Multiple imputation: penalty fixed at $C={mac['LRC']}$; between-draw SD of fold AUROC {sens['multiple_imputation_m5']['between_draw_sd_of_fold_auc_mean']:.3f}.",
          "tab:sens", ["Analysis", "$n$/deaths", "AUROC primary (95\\% CI)", "AUROC reference", "Slope", "Intercept"], rows, "p{4.6cm}rp{3.0cm}rrr", size="\\scriptsize")

    pretty = {"age": "Age", "nihss": "NIHSS", "gcs": "Glasgow Coma Scale", "mrs": "Modified Rankin (admission)", "sbp": "Systolic BP",
              "dbp": "Diastolic BP", "heart_rate": "Heart rate", "resp_rate": "Respiratory rate", "temperature": "Temperature",
              "glucose_cap": "Capillary glucose", "creatinine": "Creatinine", "urea": "Urea", "total_cholesterol": "Total cholesterol",
              "hemoglobin": "Haemoglobin", "wbc": "White-cell count", "platelets": "Platelets", "crp": "CRP", "sodium": "Sodium",
              "potassium": "Potassium", "male": "Male sex", "hypertension": "Hypertension", "diabetes": "Diabetes", "smoking": "Smoking",
              "heart_disease": "Heart disease", "atrial_fib": "Atrial fibrillation", "prior_stroke": "Prior stroke", "hemorrhagic": "Haemorrhagic subtype"}
    imp = shp["imp"]
    rows = []
    for f, r in coefs.head(12).iterrows():
        rows.append([pretty.get(f, f), f"{r.OR_per_SD:.2f} ({r.OR_lo:.2f}--{r.OR_hi:.2f})", f"{r.top5_frequency:.2f}",
                     f"{imp.loc[f, 'LR_mean_abs_shap']:.3f}", f"{imp.loc[f, 'XGB_mean_abs_shap']:.3f}", f"{pimp.loc[f, 'mean_auc_drop']:.3f}"])
    table("interp", f"Final primary model ($C={mac['LRC']}$): odds ratio per standard deviation (binary: per unit change after standardisation) with bootstrap 95\\% CI "
          "(200 resamples), frequency of a top-5 rank across bootstrap refits, mean $|$SHAP$|$ for the primary model and XGBoost, and permutation "
          "importance (AUROC drop) on the temporal test set. Twelve largest coefficients shown; associations are not causal.",
          "tab:interp", ["Predictor", "OR per SD (95\\% CI)", "Top-5 freq.", "$|$SHAP$|$ LR", "$|$SHAP$|$ XGB", "Perm. drop"], rows, "p{3.3cm}p{2.7cm}rrrr", size="\\scriptsize")

    miss = pd.read_csv(C.ANALYSIS / "predictor_missingness_labelled.csv", index_col=0).iloc[:, 0]
    misse = pd.read_csv(C.ANALYSIS / "predictor_missingness_eligible.csv", index_col=0).iloc[:, 0]
    rows = [[pretty.get(k, k if k != "spo2" else "SpO$_2$"), f"{100*misse[k]:.1f}", f"{100*v:.1f}", "yes" if v <= C.MAX_MISSING_FOR_PREDICTOR else "no ($>$60\\%)"]
            for k, v in miss.sort_values(ascending=False).items() if v > 0.05]
    table("missing", "Predictor missingness (variables with $>$5\\% missing). BMI (89\\% missing in the registry) was not considered.",
          "tab:missing", ["Predictor", "Eligible, \\%", "Labelled, \\%", "Used"], rows, "lrrl")

    bl = pd.read_csv(C.ANALYSIS / "baseline_by_outcome.csv")
    bn = json.loads((C.ANALYSIS / "baseline_n.json").read_text(encoding="utf-8"))
    rows = [[r.variable.replace("x10^3/uL", "$\\times10^3/\\mu$L").replace("\u00b0", "$^\\circ$"), r.survived, r.died, f"{r.missing_pct:.1f}",
             "$<$0.001" if r.p < 0.001 else f"{r.p:.3f}"] for r in bl.itertuples()]
    table("baseline", f"Admission characteristics of labelled patients by outcome (survived $n={bn['n_survived']}$; died $n={bn['n_died']}$). "
          "Median [IQR] or $n$ (\\%); missing \\% refers to the labelled cohort; Mann--Whitney or $\\chi^2$ test.",
          "tab:baseline", ["Characteristic", "Survived", "Died", "Missing \\%", "$p$"], rows, "p{4.2cm}p{2.8cm}p{2.8cm}rr", size="\\scriptsize")
    sg = pd.read_csv(C.ANALYSIS / "subgroups_oof.csv")
    rows = [[r.subgroup, f"{r.n}/{r.deaths}", ci3(r.auroc, r.lo, r.hi), f2(r.slope), f2(r.intercept)] for r in sg.itertuples()]
    table("subgroups", "Discrimination and calibration of the primary model by subgroup (pooled out-of-fold predictions). Calibration "
          "intercepts in later admissions reflect selective ascertainment of survivors, not necessarily model error.",
          "tab:subgroups", ["Subgroup", "$n$/deaths", "AUROC (95\\% CI)", "Slope", "Intercept"], rows, "lrp{3.0cm}rr")
    sgd = sg.set_index("subgroup")
    mac.update(SGfem=f3(sgd.loc["Female", "auroc"]), SGmale=f3(sgd.loc["Male", "auroc"]), SGlateInt=f2(sgd.loc["Admitted 2017-2023", "intercept"]),
               SGearlyInt=f2(sgd.loc["Admitted 2010-2016", "intercept"]), SGnihssMiss=f3(sgd.loc["NIHSS missing", "auroc"]),
               SGnihssRec=f3(sgd.loc["NIHSS recorded", "auroc"]))
    (MTAB / "macros.tex").write_text("\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in mac.items()) + "\n")
    json.dump(mac, open(C.TAB / "macros.json", "w", encoding="utf-8"), indent=1)

    dfs = pd.read_csv(C.COHORT / "duplicate_field_differences_summary.csv", index_col=0)
    cat = {"identity_dates": "Identity and dates", "sociodemographic_prehospital": "Socio-demographic and pre-hospital",
           "admission_clinical": "Admission clinical (history, examination, imaging, laboratory)",
           "hospital_course_disposition": "Hospital course and disposition", "follow_up_M1_to_M12": "Follow-up, months 1--12", "total": "All fields"}
    rows = []
    for k, lab_ in cat.items():
        a_, b_ = dfs.loc[f"any_difference:{k}"], dfs.loc[f"both_present_differ:{k}"]
        rows.append([lab_, f"{a_['median']:.0f} ({a_['min']:.0f}--{a_['max']:.0f})", f"{b_['median']:.0f} ({b_['min']:.0f}--{b_['max']:.0f})", f"{int(b_['groups_with_any'])}"])
    table("dupfields", "Field differences within the 38 repeated-identifier groups, by field category (median and range per group). "
          "`Any difference' counts a value present in one row and missing in the other; `both present' counts only two different non-missing values. "
          "Earlier counts that differed did so because they used different conventions.", "tab:dupfields",
          ["Field category", "Any difference", "Both present, different", "Groups with $\\ge$1 conflict"], rows, "p{5.4cm}rrr")

    tm = mr["temporal_observed_only"]
    rows = [
        ["Records after de-duplication", "1{,}615 (first row kept)", f"{mac['Nrecon']} (logged rules)", "Corrected"],
        ["Reconstruction counts (observed / inferred / unlabelled)", "803 / 218 / 594", f"{mac['OrigObs']} / {mac['OrigInf']} / {mac['OrigUnl']}", "Reproduced exactly"],
        ["Labelled patients; deaths", "1{,}021; 345 (33.8\\%)", f"{mac['Nlab']}; {mac['Ndeaths']} ({mac['Mortlab']}\\%)", "Corrected (revised endpoint)"],
        ["Interpretation of labelled-subset mortality", "Corrected registry mortality", "Upper-biased; registry mortality not identified", "Withdrawn"],
        ["Under-ascertainment by observed-only exclusion", "$\\sim$14 percentage points", f"Not identified; bounds {mac['BoundLo']}--{mac['BoundHi']}\\%", "Withdrawn"],
        ["Mortality bounds", "21.4--58.1\\% (1{,}615)", f"{mac['BoundLo']}--{mac['BoundHi']}\\% ({mac['Nelig']})", "Corrected"],
        ["Weighted / delta-adjusted mortality", "Not done", f"{mac['Mortipw']}\\%; {mac['DeltaMin']}--{mac['DeltaMax']}\\%", "New"],
        ["Events per variable", "18.5 (13 LASSO features)", f"{mac['EPV']} (27 candidates, no selection)", "Corrected"],
        ["Nested CV AUROC: LR / RF / HGB / reference", "0.843 / 0.857 / 0.859 / 0.835", f"{mac['NestLR']} / {mac['NestRF']} / {mac['NestHGB']} / {mac['NestCR']}", "Not reproduced; new re-analysis"],
        ["Hold-out AUROC LR vs reference", "0.822 vs 0.848, DeLong $p=0.17$", "Single split removed", "Withdrawn"],
        ["Paired difference, LR minus reference", "Not reported", f"CV {mac['PairNestDiff']} ({mac['PairNestLo']} to {mac['PairNestHi']}); temporal {mac['TPairDiff']} ({mac['TPairLo']} to {mac['TPairHi']})", "New"],
        ["Temporal AUROC (reconstructed)", "0.846; cut-off 2016-08-24; $n=306$", f"{mac['TLR']}; cut-off {mac['TCut']}; $n={mac['TNte']}$", "Not reproduced; new"],
        ["Temporal AUROC (observed-only)", "0.721; cut-off 2015-12-26; 7/241 deaths", f"{mac['TObLR']}; same cut-off; {tm['events_test']}/{tm['n_test']} deaths (uninformative)", "Corrected"],
        ["Recalibration", "Platt chosen on test set; slope 0.89", f"None adopted; in-fold Platt slope {mac['RecPlattSlope']}", "Corrected"],
        ["Risk tiers", "Thresholds from validation split; no low tier", f"Pre-specified; low tier {mac['TierOLowPct']}\\% (mortality {mac['TierOLowMort']}\\%)", "Corrected"],
        ["SHAP rank concordance", "$\\rho=0.70$, `stable'", f"$\\rho={mac['ShapRho']}$ ({mac['ShapRhoLo']}--{mac['ShapRhoHi']}), moderate", "Corrected"],
        ["LIME (four cases)", "Presented as explanations", "Removed", "Withdrawn"],
        ["Glasgow-to-NIHSS ratio", "Consistent risk marker", f"No added discrimination ({mac['SensRa']} vs {mac['NestLR']})", "Corrected"],
    ]
    table("origvsrev", "Key results of the submitted version and of this re-analysis. `Reproduced': same value from independent code; "
          "`not reproduced': the original code was unavailable and the value was not recovered; `new': analysis not previously reported.",
          "tab:origvsrev", ["Item", "Submitted", "Revised", "Status"], rows, "p{3.6cm}p{3.3cm}p{4.3cm}p{2.2cm}", size="\\scriptsize")

    # ---- A-4 / A-11 tables: stay distribution, label transitions, count reconciliation; audit macros
    lb = pd.read_csv(C.COHORT / "los_by_disposition.csv")
    rows = [[r.disposition.replace("'", "`", 1), str(r.n), str(r.stay_known), f"{r.median:.0f} [{r.q1:.0f}--{r.q3:.0f}]", f"{r.max:.0f}",
             str(r.le7), str(r.d8_30), str(r.d28_32), str(r.gt30)] for r in lb.itertuples()]
    table("lostab", "Elapsed stay (days from admission to release) by disposition among eligible patients. Stay is taken from the dates when both are valid "
          "and the derived stay is 0--120 days, otherwise from the recorded length of stay. Days 28--32 show how many labels sit near the 30-day boundary.",
          "tab:lostab", ["Disposition", "$n$", "Stay known", "Median [IQR]", "Max", "$\\le$7 d", "8--30 d", "28--32 d", "$>$30 d"], rows, "lrrrrrrrr")
    cw = pd.read_csv(C.COHORT / "label_transitions.csv", index_col=0)
    short = {"E1_inhosp_death_le30": "E1", "E2_month1_death_postdischarge": "E2", "N1_inhosp_death_gt30": "N1", "N2_month1_alive": "N2",
             "N3_discharged_alive_gt30": "N3", "N4_alive_later_contact": "N4"}
    cw2 = pd.DataFrame(index=cw.index)
    for c in cw.columns:
        key = short.get(c, "Unresolved")
        cw2[key] = cw2.get(key, 0) + cw[c]
    cw2 = cw2[[c for c in ["E1", "E2", "N1", "N2", "N3", "N4", "Unresolved"] if c in cw2.columns]]
    rlab = {"observed_death1": "Observed \\texttt{death1}", "inferred_inhosp_death_le30": "Inferred death, in hospital $\\le$30 d",
            "inferred_inhosp_death_gt30": "Inferred alive, in-hospital death $>$30 d", "inferred_long_stay_alive": "Inferred alive, long stay",
            "inferred_later_followup_alive": "Inferred alive, later follow-up", "unlabelled": "Unlabelled", "not in submitted cohort": "Not in submitted cohort"}
    rows = [[rlab.get(i, i)] + [str(int(v)) for v in r.values] + [str(int(r.sum()))] for i, r in cw2.iterrows()]
    table("transitions", "Label transitions from the submitted reconstruction (rows) to the revised endpoint classes (columns), matched on the first source row "
          "of each patient. Rows not in the revised cohort (excluded records, TIA) are omitted.", "tab:transitions",
          ["Submitted label"] + list(cw2.columns) + ["Total"], rows, "l" + "r" * (len(cw2.columns) + 1), size="\\scriptsize")
    tr = pd.read_csv(C.AUDIT / "tracker_count_reconciliation.csv")
    tex = lambda x: str(x).replace("%", "\\%").replace("_", "\\_").replace("<", "$<$").replace(">", "$>$").replace("|", "$|$").replace("&", "\\&")
    rows = [[("\\quad " + tex(r.item.strip())) if str(r.item).startswith("  ") else tex(r.item), tex(r.tracker_value), tex(r.rule), tex(r.revision_value)]
            for r in tr.itertuples() if not str(r.item).startswith("Raw")]
    table("auditrecon", "Reconciliation of audit counts recorded during the authors' preliminary audit with the counts from the revision code. "
          "Differences arise from definitions (year filters, tolerance, field sets), which are stated for each count.",
          "tab:auditrecon", ["Item", "Preliminary audit", "Rule applied here", "Revision"], rows, "p{3.5cm}p{2.6cm}p{4.6cm}p{3.0cm}", size="\\scriptsize")
    clg = pd.read_csv(C.AUDIT / "cleaning_and_integrity_log.csv").set_index("item")
    lc = json.loads((C.AUDIT / "los_convention_check.json").read_text(encoding="utf-8"))
    trd = tr.set_index("item")
    mac.update(Nmisaligned=str(int(clg.loc["column_shift", "n_records"])), Nrelbefore=str(int(clg.loc["flag_release_before_entry", "n_records"])),
               Nstayimpl=str(int(clg.loc["flag_date_stay_implausible", "n_records"])), LOSdisagree=str(lc["n_abs_gt2"]),
               LOSexact=str(lc["n_exact"]), LOSplusone=str(lc["n_plus1"]), LOSboth=num(lc["n_both_available"]),
               RelBeforePlaus=str(trd.loc["Release before entry", "revision_value"]), LOSdiffOne=str(trd.loc["LOS differs from date interval by >1 day", "revision_value"]),
               FlagUnion=str(trd.loc["Union of the two timing flags", "revision_value"]))
    (MTAB / "macros.tex").write_text("\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in mac.items()) + "\n")
    json.dump(mac, open(C.TAB / "macros.json", "w", encoding="utf-8"), indent=1)

    # ------------------------------------------------------------- figures
    # 1. recording by year
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.4))
    yrs = ry.index.values
    ax[0].plot(yrs, ry.death1_recorded_pct, color=PAL["LR"], marker="o", ms=4, label="Month-1 field recorded")
    ax[0].plot(yrs, 100 * ry.inhosp_deaths_with_death1_yes / ry.inhosp_deaths.replace(0, np.nan), color=PAL["ClinRef"], marker="s", ms=4,
               label="In-hospital deaths with death1 = Yes")
    ax[0].set_ylabel("% of admissions / of in-hospital deaths"); ax[0].set_xlabel("Admission year"); ax[0].set_ylim(-3, 103)
    ax[0].xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2)); ax[0].legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=1); ax[0].set_title("a  Recording of the month-1 field", loc="left", fontsize=9)
    x = np.arange(len(byp))
    ax[1].bar(x - 0.2, byp.labelled_mortality_pct, 0.38, color=PAL["ClinRef"], label="Labelled-subset mortality")
    ax[1].bar(x + 0.2, byp.inhosp_30d_pct_known_disp, 0.38, color=PAL["LR"], label="In-hospital 30-d mortality")
    ax[1].plot(x, byp.labelled_pct, color=INK2, marker="o", ms=4, lw=1.5, label="% labelled")
    ax[1].set_xticks(x, byp.index, rotation=0, fontsize=7); ax[1].set_ylabel("%"); ax[1].set_xlabel("Admission period")
    ax[1].legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2); ax[1].set_title("b  Ascertainment and mortality", loc="left", fontsize=9); ax[1].set_ylim(0, 105)
    fig.tight_layout(); save(fig, "fig_ascertainment")

    # 2. cohort flow
    fig, ax = plt.subplots(figsize=(7.2, 4.4)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    def box(x, y, w, h, t, fc="#f3f2ee"):
        ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec=INK2, lw=0.8)); ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=7.5)
    def arr(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color=INK2, lw=0.8))
    box(3, 8.8, 4, 0.9, f"Registry rows (2010–2023)\nn = {P['source_rows']}")
    box(3, 7.0, 4, 1.3, f"After duplicate reconciliation\nn = {P['after_reconciliation']} records\n(38 repeated codes: rule-based log)")
    box(7.4, 6.4, 2.5, 2.3, f"Excluded\nblank records: {P['excluded_blank_records']}\nno valid admission\ndate: {P['excluded_no_valid_admission_date']}\nage < 18 y: {P['excluded_age_lt18']}\nTIA: {P['excluded_tia']}", fc="#fbfaf7")
    box(3, 5.6, 4, 0.9, f"Eligible stroke admissions\nn = {P['eligible']}")
    box(0.2, 3.1, 4.4, 2.0, f"Labelled (revised endpoint)\nn = {P['labelled']}; deaths {P['deaths']} ({P['mortality_labelled_pct']}%)\nhospital-record events {cc.get('E1_inhosp_death_le30',0)}\nmonth-1 field events {cc.get('E2_month1_death_postdischarge',0)} (timing assumption A2)", fc="#eaf2fb")
    box(5.4, 3.1, 4.4, 2.0, f"Unresolved, n = {P['unresolved']}\ndischarged alive ≤30 d, no follow-up {cc.get('U_discharged_alive_no_followup',0)}\nno / 'Other' disposition {cc.get('U_disposition_missing_no_followup',0)+cc.get('U_other_disposition_no_followup',0)}\nconflicting, misaligned or\ntiming unknown {P['unresolved']-cc.get('U_discharged_alive_no_followup',0)-cc.get('U_disposition_missing_no_followup',0)-cc.get('U_other_disposition_no_followup',0)}", fc="#fdf0ea")
    box(0.2, 0.6, 4.4, 1.9, f"Prediction modelling\nnested CV on n = {mr['n']}\ntemporal split at {mr['temporal_cutoff']}\ntrain {T['n_train']} / test {T['n_test']}")
    box(5.4, 0.6, 4.4, 1.9, f"Ascertainment analyses (all {P['eligible']})\nlabelled vs unresolved comparison\nIPW (n = {A['ipw_population']} with a recorded disposition)\nbounds and delta-adjustment")
    arr(5, 8.8, 5, 8.3); arr(5, 7.0, 5, 6.5); arr(7, 7.7, 7.4, 7.6); arr(4.2, 5.6, 2.4, 5.1); arr(5.8, 5.6, 7.6, 5.1); arr(2.4, 3.1, 2.4, 2.5); arr(7.6, 3.1, 7.6, 2.5)
    save(fig, "fig_flow")

    # 3. ROC (pooled OOF)
    y = fd["y"]
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.3))
    for m in ["LR", "ClinRef", "RF", "HGB", "XGB"]:
        fpr, tpr, _ = roc_curve(y, fd["pbar"][m]); ax[0].plot(fpr, tpr, color=PAL[m], lw=1.6, label=f"{NAMES[m].replace(' (primary)','')} {NP[m]['auroc']:.3f}")
        tv = fd["tv"]; fpr, tpr, _ = roc_curve(tv["yte"], tv["preds"][m]); ax[1].plot(fpr, tpr, color=PAL[m], lw=1.6, label=f"{T[m]['auroc']:.3f}")
    for a_, t_ in zip(ax, ["a  Nested CV (pooled out-of-fold)", f"b  Temporal test (n = {T['n_test']})"]):
        a_.plot([0, 1], [0, 1], color=GRID, lw=1, ls="--"); a_.set_xlabel("1 − specificity"); a_.set_ylabel("Sensitivity"); a_.set_title(t_, loc="left", fontsize=9)
        a_.legend(fontsize=6.5, loc="lower right", title="AUROC", title_fontsize=7)
    fig.tight_layout(); save(fig, "fig_roc")

    # 4. calibration
    def calcurve(yv, pv, bins=10):
        q = pd.qcut(pv, bins, duplicates="drop"); g = pd.DataFrame({"y": yv, "p": pv, "q": q}).groupby("q", observed=True)
        return g.p.mean().values, g.y.mean().values
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.3))
    for lab_, pv, col in [("Primary model (no recalibration)", fd["pbar"]["LR"], PAL["LR"]), ("In-fold Platt", fd["rc"]["sigmoid"], PAL["ClinRef"]),
                          ("In-fold isotonic", fd["rc"]["isotonic"], PAL["RF"])]:
        a_, b_ = calcurve(y, pv); ax[0].plot(a_, b_, marker="o", ms=4, color=col, lw=1.5, label=lab_)
    a_, b_ = calcurve(fd["tv"]["yte"], fd["tv"]["preds"]["LR"], 5); ax[1].plot(a_, b_, marker="o", ms=5, color=PAL["LR"], lw=1.5, label="Primary model, temporal test")
    a_, b_ = calcurve(fd["tv"]["yte"], fd["tv"]["preds"]["ClinRef"], 5); ax[1].plot(a_, b_, marker="s", ms=5, color=PAL["ClinRef"], lw=1.5, label="Clinical reference, temporal test")
    for a_, t_ in zip(ax, ["a  Out-of-fold (deciles)", "b  Temporal test (quintiles)"]):
        a_.plot([0, 1], [0, 1], color=INK2, lw=0.8, ls="--"); a_.set_xlim(0, 1); a_.set_ylim(0, 1)
        a_.set_xlabel("Mean predicted risk"); a_.set_ylabel("Observed proportion (labelled)"); a_.set_title(t_, loc="left", fontsize=9); a_.legend(fontsize=6.5, loc="upper left")
    fig.tight_layout(); save(fig, "fig_calibration")

    # 5. DCA
    fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.8), sharey=False)
    for a_, dd, t_ in zip(ax, [fd["dca_oof"], fd["dca_oof_w"], fd["dca_tmp"]], ["a  Out-of-fold", "b  Out-of-fold, IPW", "c  Temporal test"]):
        for m in ["LR", "ClinRef"]:
            a_.plot(dd[m][:, 0], dd[m][:, 1], color=PAL[m], lw=1.6, label=NAMES[m].replace(" (primary)", ""))
        a_.plot(dd["LR"][:, 0], dd["LR"][:, 2], color=INK2, lw=1, ls="--", label="Treat all"); a_.axhline(0, color=INK, lw=0.8, label="Treat none")
        a_.set_ylim(-0.05, max(0.4, dd["LR"][:, 1].max() + 0.02)); a_.set_xlabel("Threshold probability"); a_.set_title(t_, loc="left", fontsize=9)
    ax[0].set_ylabel("Net benefit"); ax[0].legend(fontsize=6, loc="upper right")
    fig.tight_layout(); save(fig, "fig_dca")

    # 6. delta
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    for ref, col, lab_ in [("early_era", PAL["LR"], "2010–14 post-discharge risk"), ("period_specific", PAL["ClinRef"], "Period-specific risk")]:
        sub = delta[delta.reference == ref]; ax.plot(sub.delta_odds_ratio, sub.mortality_pct, marker="o", ms=5, color=col, label=lab_)
    ax.set_xscale("log", base=2); ax.set_xticks([0.25, 0.5, 1, 2, 4, 8], ["0.25", "0.5", "1", "2", "4", "8"])
    ax.axhline(P["mortality_labelled_pct"], color=INK2, ls=":", lw=1); ax.text(0.27, P["mortality_labelled_pct"] + 0.6, "labelled-subset proportion", fontsize=7, color=INK2)
    ax.axhline(A["bound_all_unresolved_alive_pct"], color=INK2, ls="--", lw=1); ax.text(0.27, A["bound_all_unresolved_alive_pct"] + 0.6, "lower bound", fontsize=7, color=INK2)
    ax.set_xlabel("δ (odds ratio, unresolved vs comparable resolved)"); ax.set_ylabel("Estimated 30-day mortality, %"); ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(0.0, 0.93))
    fig.tight_layout(); save(fig, "fig_delta")

    # 7. SHAP / importance
    imp = shp["imp"].copy(); imp.index = [pretty.get(i, i) for i in imp.index]
    imp = imp.sort_values("LR_mean_abs_shap").tail(14)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.6), sharey=True)
    ax[0].barh(imp.index, imp.LR_mean_abs_shap, color=PAL["LR"], height=0.7); ax[0].set_title("a  Primary model", loc="left", fontsize=9)
    ax[1].barh(imp.index, imp.XGB_mean_abs_shap, color=PAL["XGB"], height=0.7); ax[1].set_title("b  XGBoost", loc="left", fontsize=9)
    for a_ in ax:
        a_.set_xlabel("Mean |SHAP| (log-odds)"); a_.grid(axis="y", visible=False)
    fig.tight_layout(); save(fig, "fig_shap")

    # 8. tiers
    fig, ax = plt.subplots(figsize=(4.8, 2.8))
    xs = np.arange(3)
    for k_, (df_, col, lab_) in enumerate([(ti, PAL["LR"], "Pooled out-of-fold"), (tt, PAL["ClinRef"], "Temporal test")]):
        mort = df_.loc[["Low", "Moderate", "High"]]
        ax.bar(xs + (k_ - 0.5) * 0.38, mort.mortality.fillna(0), 0.36, color=col, label=lab_)
        ax.errorbar(xs + (k_ - 0.5) * 0.38, mort.mortality.fillna(0), yerr=[(mort.mortality - mort.mort_lo).fillna(0), (mort.mort_hi - mort.mortality).fillna(0)],
                    fmt="none", ecolor=INK2, lw=0.8, capsize=2)
    ax.set_xticks(xs, ["Low (<10%)", "Moderate", "High (≥40%)"]); ax.set_ylabel("Observed mortality, % (labelled)"); ax.legend(fontsize=7)
    fig.tight_layout(); save(fig, "fig_tiers")
    print(f"wrote {len(mac)} macros, tables and figures")


if __name__ == "__main__":
    main()
