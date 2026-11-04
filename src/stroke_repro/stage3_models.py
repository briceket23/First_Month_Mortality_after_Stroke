"""Stage 3: leakage-free model development and validation (clean-room reanalysis).

Design (fixed before any model was evaluated):
  * cohort: labelled patients of the revised primary endpoint; admission-time predictors only
  * primary internal validation: nested cross-validation, outer 5 folds x 5 repeats, inner 3-fold tuning
  * temporal validation: single cut-off = 70th percentile of admission dates among ALL eligible
    patients (outcome-independent); identical cut-off for every endpoint variant
  * calibration: un-weighted L2 logistic regression (no class weighting) is the primary model and is
    not recalibrated; in-fold Platt / isotonic recalibration are sensitivity analyses only
  * risk tiers: pre-specified absolute-risk cut-points (config.RISK_TIERS); never tuned on test data
"""
import json
import pickle
import sys
import time

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.inspection import permutation_importance
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold

from . import config as C
from . import metrics as M
from .models import make, fit_predict
from .stage2_ascertainment import add_period

MODELS = ["LR", "ClinRef", "RF", "HGB", "XGB"]
CK = C.RESTRICTED / "ckpt"
CK.mkdir(exist_ok=True)


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def load(name):
    p = add_period(pd.read_pickle(C.RESTRICTED / f"cohort_{name}.pkl"))
    return p


def observed_only(p):
    q = p.copy()
    ok = q.death1.isin(["Yes", "No"]) & ~q.outcome_forced_unresolved.astype(bool) & ~q.flag_column_shift.astype(bool)
    q["y"] = np.where(ok, (q.death1 == "Yes").astype(float), np.nan)
    q["labelled"] = ok
    return q


def choose_features(p):
    lab = p[p.labelled]
    cand = C.NUMERIC + C.BINARY
    miss = lab[cand].isna().mean()
    feats = [c for c in cand if miss[c] <= C.MAX_MISSING_FOR_PREDICTOR]
    return feats, miss


def nested(X, y, model_names, repeats, seed=C.SEED, tag="", w_fit=None, **kw):
    path = CK / f"nested_{tag}.pkl"
    if path.exists():
        return pickle.load(open(path, "rb"))
    rskf = RepeatedStratifiedKFold(n_splits=C.OUTER_FOLDS, n_repeats=repeats, random_state=seed)
    oof = {m: np.full((repeats, len(y)), np.nan) for m in model_names}
    fold_auc = {m: [] for m in model_names}
    params = {m: [] for m in model_names}
    for k, (tr, te) in enumerate(rskf.split(X, y)):
        r = k // C.OUTER_FOLDS
        for m in model_names:
            Xm = X if m != "ClinRef" else X[C.CLINICAL_REFERENCE]
            wtr = None if w_fit is None else w_fit[tr]
            _, pr, best = fit_predict(m, Xm.iloc[tr], y[tr], Xm.iloc[te], seed + k, wtr=wtr, **kw.get(m, {}))
            oof[m][r, te] = pr
            from sklearn.metrics import roc_auc_score
            fold_auc[m].append(roc_auc_score(y[te], pr))
            params[m].append(best)
        log(f"  [{tag}] outer fold {k+1}/{C.OUTER_FOLDS*repeats} done")
    res = dict(oof=oof, fold_auc=fold_auc, params=params)
    pickle.dump(res, open(path, "wb"))
    return res


def summarise_nested(res, y, w=None):
    rows = {}
    for m, o in res["oof"].items():
        per_rep = [M.delong_ci(y, o[r])[0] for r in range(o.shape[0])]
        pbar = o.mean(axis=0)
        s = M.summary(y, pbar)
        cal_r = [M.calibration(y, o[r]) for r in range(o.shape[0])]
        for key in ("slope", "intercept", "brier"):
            s[f"{key}_per_repeat_mean"] = float(np.mean([c[key] for c in cal_r]))
        s.update(fold_auc_mean=float(np.mean(res["fold_auc"][m])), fold_auc_sd=float(np.std(res["fold_auc"][m], ddof=1)),
                 pooled_oof_auc_by_repeat_mean=float(np.mean(per_rep)),
                 pooled_oof_auc_by_repeat_range=[float(min(per_rep)), float(max(per_rep))])
        if w is not None:
            sw = M.summary(y, pbar, w)
            s.update({f"ipw_{k}": v for k, v in sw.items() if k in ("auroc", "auprc", "slope", "intercept", "brier", "mean_pred", "obs_rate")})
        rows[m] = s
    return rows


def recalibration_nested(X, y, repeats, seed=C.SEED):
    """In-fold Platt and isotonic recalibration of the primary LR (sensitivity; never selected on test data)."""
    path = CK / "recal.pkl"
    if path.exists():
        return pickle.load(open(path, "rb"))
    rskf = RepeatedStratifiedKFold(n_splits=C.OUTER_FOLDS, n_repeats=repeats, random_state=seed)
    out = {k: np.full((repeats, len(y)), np.nan) for k in ("sigmoid", "isotonic")}
    for k, (tr, te) in enumerate(rskf.split(X, y)):
        r = k // C.OUTER_FOLDS
        base = make("LR", seed + k).fit(X.iloc[tr], y[tr]).best_estimator_
        for meth in out:
            cal = CalibratedClassifierCV(base, method=meth, cv=StratifiedKFold(3, shuffle=True, random_state=seed + k))
            cal.fit(X.iloc[tr], y[tr])
            out[meth][r, te] = cal.predict_proba(X.iloc[te])[:, 1]
        log(f"  [recal] fold {k+1}")
    pickle.dump(out, open(path, "wb"))
    return out


def temporal(p, feats, cutoff, model_names, tag, seed=C.SEED, w=None):
    path = CK / f"temporal_{tag}.pkl"
    if path.exists():
        return pickle.load(open(path, "rb"))
    lab = p[p.labelled].copy()
    tr = lab.entry_date < cutoff
    te = ~tr
    Xtr, ytr = lab.loc[tr, feats], lab.loc[tr, "y"].astype(int).values
    Xte, yte = lab.loc[te, feats], lab.loc[te, "y"].astype(int).values
    preds = {}
    fitted = {}
    for m in model_names:
        cols = feats if m != "ClinRef" else C.CLINICAL_REFERENCE
        est, pr, best = fit_predict(m, Xtr[cols], ytr, Xte[cols], seed)
        preds[m] = pr
        fitted[m] = est
    res = dict(n_train=int(tr.sum()), events_train=int(ytr.sum()), n_test=int(te.sum()), events_test=int(yte.sum()),
               yte=yte, preds=preds, test_keys=lab.loc[te, "patient_key"].values,
               train_keys=lab.loc[tr, "patient_key"].values)
    pickle.dump(res, open(path, "wb"))
    pickle.dump(fitted, open(CK / f"temporal_models_{tag}.pkl", "wb"))
    return res


def tiers(y, p, cuts=C.RISK_TIERS):
    lo, hi = cuts
    lab = np.where(p < lo, "Low", np.where(p >= hi, "High", "Moderate"))
    rows = []
    for t in ["Low", "Moderate", "High"]:
        m = lab == t
        n, k = int(m.sum()), int(y[m].sum())
        ci = M.wilson(k, n) if n else (np.nan, np.nan)
        rows.append(dict(tier=t, n=n, pct_patients=100 * n / len(y), deaths=k, mortality=100 * k / n if n else np.nan,
                         mort_lo=100 * ci[0], mort_hi=100 * ci[1], pct_deaths=100 * k / y.sum(),
                         patients_per_death=(n / k) if k else np.nan))
    return pd.DataFrame(rows)


def shift_table(p, cutoff, feats):
    e = p.copy()
    e["late"] = e.entry_date >= cutoff
    rows = []
    for c in ["age", "nihss", "gcs", "mrs", "hemorrhagic", "male"]:
        a, b = e.loc[~e.late, c], e.loc[e.late, c]
        rows.append(dict(variable=c, early=f"{a.mean():.2f}", late=f"{b.mean():.2f}",
                         early_missing_pct=round(100 * a.isna().mean(), 1), late_missing_pct=round(100 * b.isna().mean(), 1)))
    for lab_, sel in [("labelled_pct", "labelled")]:
        rows.append(dict(variable=lab_, early=f"{100*e.loc[~e.late, sel].mean():.1f}", late=f"{100*e.loc[e.late, sel].mean():.1f}"))
    L = e[e.labelled]
    rows.append(dict(variable="labelled_mortality_pct", early=f"{100*L.loc[~L.late, 'y'].mean():.1f}", late=f"{100*L.loc[L.late, 'y'].mean():.1f}"))
    rows.append(dict(variable="share_of_labels_from_hospital_record_pct",
                     early=f"{100*L.loc[~L.late].y_class.str.startswith(('E1','N1','N3')).mean():.1f}",
                     late=f"{100*L.loc[L.late].y_class.str.startswith(('E1','N1','N3')).mean():.1f}"))
    rows.append(dict(variable="share_labelled_deaths_in_hospital_pct",
                     early=f"{100*(L.loc[~L.late].y_class=='E1_inhosp_death_le30').sum()/max(1,L.loc[~L.late].y.sum()):.1f}",
                     late=f"{100*(L.loc[L.late].y_class=='E1_inhosp_death_le30').sum()/max(1,L.loc[L.late].y.sum()):.1f}"))
    return pd.DataFrame(rows)


def main(quick=False):
    t0 = time.time()
    reps = 2 if quick else C.OUTER_REPEATS
    out = {}
    P = load("primary")
    feats, miss = choose_features(P)
    lab = P[P.labelled].reset_index(drop=True)
    X, y = lab[feats].astype(float), lab.y.astype(int).values
    miss.rename("missing_fraction_labelled").to_csv(C.ANALYSIS / "predictor_missingness_labelled.csv")
    P[C.NUMERIC + C.BINARY].isna().mean().rename("missing_fraction_eligible").to_csv(C.ANALYSIS / "predictor_missingness_eligible.csv")
    out["features"] = feats
    out["dropped_features_missing_gt_60pct"] = [c for c in C.NUMERIC + C.BINARY if c not in feats]
    out["n"], out["events"] = int(len(y)), int(y.sum())
    out["epv_candidate_df"] = round(y.sum() / len(feats), 1)
    log("features", feats, "n", len(y), "events", y.sum())

    ipw = pd.read_pickle(C.RESTRICTED / "ipw_primary.pkl").set_index("patient_key").ipw
    w = ipw.reindex(lab.patient_key).fillna(1.0).values

    # ------------------------------------------------ primary nested CV, all models
    res = nested(X, y, MODELS, reps, tag="primary")
    out["nested_primary"] = summarise_nested(res, y, w)
    pbar = {m: res["oof"][m].mean(axis=0) for m in MODELS}
    out["nested_paired_LR_vs_ClinRef"] = M.delong_paired(y, pbar["LR"], pbar["ClinRef"])
    out["nested_paired_XGB_vs_LR"] = M.delong_paired(y, pbar["XGB"], pbar["LR"])
    out["nested_paired_RF_vs_LR"] = M.delong_paired(y, pbar["RF"], pbar["LR"])
    d_fold = np.array(res["fold_auc"]["LR"]) - np.array(res["fold_auc"]["ClinRef"])
    out["nested_fold_diff_LR_minus_ClinRef"] = dict(mean=float(d_fold.mean()), sd=float(d_fold.std(ddof=1)),
                                                     n_folds=int(len(d_fold)), n_LR_better=int((d_fold > 0).sum()))
    out["lr_C_selected"] = pd.Series([pp.get("clf__C") for pp in res["params"]["LR"]]).value_counts().to_dict()
    pd.DataFrame({"patient_key": lab.patient_key, "y": y, **{m: pbar[m] for m in MODELS}, "ipw": w}).to_pickle(C.RESTRICTED / "oof_primary.pkl")
    log("primary nested done")

    # ------------------------------------------------ recalibration (sensitivity)
    rc = recalibration_nested(X, y, reps)
    out["recalibration_oof"] = {"uncalibrated": M.calibration(y, pbar["LR"]),
                                **{k: M.calibration(y, v.mean(axis=0)) for k, v in rc.items()}}
    for k, v in rc.items():
        out["recalibration_oof"][k]["auroc"] = M.delong_ci(y, v.mean(axis=0))[0]
    out["recalibration_oof"]["uncalibrated"]["auroc"] = M.delong_ci(y, pbar["LR"])[0]
    reps_arr = {"uncalibrated": res["oof"]["LR"], **rc}
    for k, arr in reps_arr.items():
        cr = [M.calibration(y, arr[r]) for r in range(arr.shape[0])]
        for key in ("slope", "intercept", "brier"):
            out["recalibration_oof"][k][f"{key}_per_repeat_mean"] = float(np.mean([c[key] for c in cr]))

    # ------------------------------------------------ risk tiers + DCA on pooled OOF
    out["tiers_oof"] = tiers(y, pbar["LR"]).to_dict(orient="records")
    th = np.round(np.arange(C.DCA_RANGE[0], C.DCA_RANGE[1] + 1e-9, 0.01), 2)
    dca_oof = {m: M.net_benefit(y, pbar[m], th) for m in ["LR", "ClinRef"]}
    dca_oof_w = {m: M.net_benefit(y, pbar[m], th, w) for m in ["LR", "ClinRef"]}

    # ------------------------------------------------ temporal validation
    cutoff = P.entry_date.sort_values().iloc[int(0.7 * len(P))]
    out["temporal_cutoff"] = str(cutoff.date())
    tv = temporal(P, feats, cutoff, MODELS, "primary")
    yte = tv["yte"]
    out["temporal_primary"] = {"n_train": tv["n_train"], "events_train": tv["events_train"],
                               "n_test": tv["n_test"], "events_test": tv["events_test"],
                               **{m: M.summary(yte, tv["preds"][m]) for m in MODELS}}
    out["temporal_paired_LR_vs_ClinRef"] = M.delong_paired(yte, tv["preds"]["LR"], tv["preds"]["ClinRef"])
    out["temporal_paired_XGB_vs_LR"] = M.delong_paired(yte, tv["preds"]["XGB"], tv["preds"]["LR"])
    wte = ipw.reindex(tv["test_keys"]).fillna(1.0).values
    out["temporal_primary_ipw_LR"] = M.summary(yte, tv["preds"]["LR"], wte)
    out["temporal_primary_ipw_LR"]["auroc_boot_ci"] = M.bootstrap_auc_ci(yte, tv["preds"]["LR"], wte)
    out["tiers_temporal"] = tiers(yte, tv["preds"]["LR"]).to_dict(orient="records")
    dca_tmp = {m: M.net_benefit(yte, tv["preds"][m], th) for m in ["LR", "ClinRef"]}
    shift_table(P, cutoff, feats).to_csv(C.ANALYSIS / "temporal_shift_primary.csv", index=False)
    # membership model: how separable are early vs late admissions on admission predictors?
    from sklearn.model_selection import cross_val_predict
    from .models import lr_pipeline
    late = (lab.entry_date >= cutoff).astype(int).values
    pm = cross_val_predict(lr_pipeline(C.SEED), X, late, cv=StratifiedKFold(5, shuffle=True, random_state=C.SEED), method="predict_proba")[:, 1]
    out["temporal_membership_auc"] = M.delong_ci(late, pm)
    log("temporal primary done")

    # ------------------------------------------------ temporal: other endpoint definitions, same cut-off
    variants = {"strict_timing": load("strict_timing"), "observed_only": observed_only(P)}
    for nm, q in variants.items():
        tq = temporal(q, feats, cutoff, ["LR", "ClinRef"], nm)
        out[f"temporal_{nm}"] = {"n_train": tq["n_train"], "events_train": tq["events_train"], "n_test": tq["n_test"],
                                 "events_test": tq["events_test"],
                                 **{m: M.summary(tq["yte"], tq["preds"][m]) for m in ["LR", "ClinRef"]}}
    # same test patients as the observed-only test set, scored against the primary label
    tq = pickle.load(open(CK / "temporal_observed_only.pkl", "rb"))
    common = np.intersect1d(tq["test_keys"], tv["test_keys"])
    idx_p = pd.Series(np.arange(len(tv["test_keys"])), index=tv["test_keys"]).loc[common].values
    out["temporal_primary_on_observed_only_test_patients"] = M.summary(yte[idx_p], tv["preds"]["LR"][idx_p]) \
        if yte[idx_p].min() != yte[idx_p].max() else None

    # ------------------------------------------------ sensitivity analyses (LR + ClinRef, nested 5x2)
    sens = {}
    sreps = 2
    def run_sens(tag, q, feats_, extra=None, model_names=("LR", "ClinRef"), wfit=None, wev=None):
        l = q[q.labelled].reset_index(drop=True)
        Xs, ys = l[feats_].astype(float), l.y.astype(int).values
        r = nested(Xs, ys, list(model_names), sreps, tag=tag, w_fit=wfit, **(extra or {}))
        s = summarise_nested(r, ys, wev)
        s["n"], s["events"] = int(len(ys)), int(ys.sum())
        sens[tag] = s
        log("sens", tag, {m: round(s[m]["auroc"], 3) for m in model_names})
        return l, r
    run_sens("strict_timing", variants["strict_timing"], feats)
    run_sens("observed_only", variants["observed_only"], feats)
    run_sens("dup_keep_first", load("dup_keep_first"), feats)
    run_sens("dup_exclude_conflicts", load("dup_exclude_conflicts"), feats)
    era = P.copy(); era["labelled"] = era.labelled & (era.admission_year <= 2016)
    run_sens("era_2010_2016", era, feats)
    cc = P.copy(); cc["labelled"] = cc.labelled & cc.nihss.notna()
    run_sens("complete_nihss", cc, feats)
    ni = P.copy(); ni["nihss_missing"] = ni.nihss.isna().astype(float)
    run_sens("nihss_missing_indicator", ni, feats + ["nihss_missing"], model_names=("LR",))
    gi, ni_ = feats.index("gcs"), feats.index("nihss")
    run_sens("gcs_nihss_ratio", P, feats, extra={"LR": {"ratio_idx": (gi, ni_)}}, model_names=("LR",))
    # multiple imputation (m = 5 posterior draws, C fixed at the modal primary choice) with between-draw variability
    C_mode = max(out["lr_C_selected"], key=out["lr_C_selected"].get)
    l_mi, r_mi = run_sens("multiple_imputation_m5", P, feats, extra={"LR_MI": {"m": 5, "C": float(C_mode)}}, model_names=("LR_MI",))
    sens["multiple_imputation_m5"]["LR"] = sens["multiple_imputation_m5"].pop("LR_MI")
    # between-imputation variability of fold AUROC: refit on 5 outer folds once and score each draw separately
    from sklearn.metrics import roc_auc_score
    from .models import MIEnsemble
    Xm_, ym_ = l_mi[feats].astype(float), l_mi.y.astype(int).values
    draw_auc = []
    for tr_, te_ in StratifiedKFold(C.OUTER_FOLDS, shuffle=True, random_state=C.SEED).split(Xm_, ym_):
        est = MIEnsemble(m=5, C=float(C_mode), seed=C.SEED).fit(Xm_.iloc[tr_], ym_[tr_])
        pd_ = est.per_draw_proba(Xm_.iloc[te_])
        draw_auc.append([roc_auc_score(ym_[te_], pd_[j]) for j in range(5)])
    draw_auc = np.array(draw_auc)
    sens["multiple_imputation_m5"]["between_draw_sd_of_fold_auc_mean"] = float(np.mean(draw_auc.std(axis=1, ddof=1)))
    sens["multiple_imputation_m5"]["within_fold_draw_range_max"] = float(np.max(draw_auc.max(axis=1) - draw_auc.min(axis=1)))
    # missingness indicators for every predictor missing in > 20 % of labelled patients (A-5)
    hi_miss = [c for c in feats if miss[c] > 0.20]
    mi_all = P.copy()
    for c in hi_miss:
        mi_all[c + "_missing"] = mi_all[c].isna().astype(float)
    run_sens("missing_indicators_all", mi_all, feats + [c + "_missing" for c in hi_miss], model_names=("LR",))
    out["missing_indicator_predictors"] = hi_miss
    # predictors with < 10 % missing only (no dependence on heavily imputed variables)
    low_miss = [c for c in feats if miss[c] < 0.10]
    run_sens("low_missing_predictors", P, low_miss, model_names=("LR",))
    out["low_missing_predictors"] = low_miss
    # no inference from later follow-up contacts (N4 -> unresolved) (A-4)
    nl = P.copy(); nl["labelled"] = nl.labelled & (nl.y_class != "N4_alive_later_contact")
    run_sens("no_later_contact", nl, feats, model_names=("LR",))
    # stroke-anchored month-1 window (data dictionary, 2 Nov): death1 = No certifies survival to onset + 1 month only;
    # N2 labels whose onset-to-arrival delay exceeds ONSET_GAP_HOURS (unit assumed hours) -> unresolved
    dl = pd.read_pickle(C.RESTRICTED / "arrival_delay_labelled.pkl").set_index("patient_key").arrival_delay_raw
    dly = P.patient_key.map(dl)
    og = P.copy(); og["labelled"] = og.labelled & ~((og.y_class == "N2_month1_alive") & (dly > C.ONSET_GAP_HOURS))
    run_sens("onset_anchor_gap", og, feats, model_names=("LR",))
    og2 = P.copy(); og2["labelled"] = og2.labelled & ~((og2.y_class == "N2_month1_alive") & ~(dly <= C.ONSET_GAP_HOURS))
    run_sens("onset_anchor_gap_unknown_excluded", og2, feats, model_names=("LR",))
    l_ipw = P[P.labelled].reset_index(drop=True)
    w_l = ipw.reindex(l_ipw.patient_key).fillna(1.0).values
    run_sens("ipw_weighted_fit", P, feats, wfit=w_l, wev=w_l)
    out["sensitivity_nested"] = sens

    # ------------------------------------------------ interpretation on final model (fit on all labelled)
    fin = make("LR", C.SEED).fit(X, y).best_estimator_
    coefs = pd.Series(fin.named_steps["clf"].coef_[0], index=feats)
    # bootstrap coefficient CIs and top-5 rank stability
    rng = np.random.default_rng(C.SEED)
    C_best = fin.named_steps["clf"].C
    from .models import lr_pipeline
    bcoef, ranks = [], []
    for b in range(200):
        i = rng.integers(0, len(y), len(y))
        mdl = lr_pipeline(C.SEED + b); mdl.set_params(clf__C=C_best)
        mdl.fit(X.iloc[i], y[i])
        cb = pd.Series(mdl.named_steps["clf"].coef_[0], index=feats)
        bcoef.append(cb)
        ranks.append(cb.abs().rank(ascending=False))
    bcoef = pd.DataFrame(bcoef)
    ranks = pd.DataFrame(ranks)
    interp = pd.DataFrame({"coef_per_SD": coefs, "OR_per_SD": np.exp(coefs),
                           "OR_lo": np.exp(bcoef.quantile(0.025)), "OR_hi": np.exp(bcoef.quantile(0.975)),
                           "top5_frequency": (ranks <= 5).mean(), "median_rank": ranks.median()}).sort_values("coef_per_SD", key=abs, ascending=False)
    interp.to_csv(C.ANALYSIS / "lr_coefficients_bootstrap.csv")
    out["lr_final_C"] = float(C_best)
    out["imputer_iterations_final_model"] = int(fin.named_steps["impute"].n_iter_)
    out["imputer_max_iter"] = 15
    # permutation importance on the temporal test set (model fitted on the temporal training set)
    tm = pickle.load(open(CK / "temporal_models_primary.pkl", "rb"))
    labT = P[P.labelled].set_index("patient_key").loc[tv["test_keys"]]
    pim = permutation_importance(tm["LR"], labT[feats].astype(float), yte, scoring="roc_auc", n_repeats=30, random_state=C.SEED)
    pi = pd.DataFrame({"mean_auc_drop": pim.importances_mean, "sd": pim.importances_std}, index=feats).sort_values("mean_auc_drop", ascending=False)
    pi.to_csv(C.ANALYSIS / "permutation_importance_temporal_test.csv")
    # SHAP: LR (linear, on imputed+scaled data) and XGB; rank concordance with bootstrap CI
    import shap
    Xi = fin.named_steps["impute"].transform(X)
    Xs = fin.named_steps["scale"].transform(Xi)
    sv_lr = shap.LinearExplainer(fin.named_steps["clf"], Xs).shap_values(Xs)
    xgbm = make("XGB", C.SEED).fit(X, y).best_estimator_
    sv_x = shap.TreeExplainer(xgbm).shap_values(X)
    imp = pd.DataFrame({"LR_mean_abs_shap": np.abs(sv_lr).mean(0), "XGB_mean_abs_shap": np.abs(sv_x).mean(0)}, index=feats)
    from scipy.stats import spearmanr
    rho = spearmanr(imp.LR_mean_abs_shap, imp.XGB_mean_abs_shap).statistic
    brho = []
    for b in range(100):
        i = rng.integers(0, len(feats), len(feats))
        if len(set(i)) > 3:
            brho.append(spearmanr(imp.LR_mean_abs_shap.values[i], imp.XGB_mean_abs_shap.values[i]).statistic)
    imp.sort_values("LR_mean_abs_shap", ascending=False).to_csv(C.ANALYSIS / "shap_importance.csv")
    out["shap_rank_spearman_LR_vs_XGB"] = dict(rho=float(rho), ci_feature_bootstrap=[float(np.nanpercentile(brho, 2.5)), float(np.nanpercentile(brho, 97.5))],
                                               n_features=len(feats))
    pickle.dump(dict(sv_lr=sv_lr, Xs=Xs, sv_x=sv_x, X=X.values, feats=feats, imp=imp), open(CK / "shap.pkl", "wb"))

    # ------------------------------------------------ save
    pickle.dump(dict(th=th, dca_oof=dca_oof, dca_oof_w=dca_oof_w, dca_tmp=dca_tmp, pbar=pbar, y=y,
                     rc={k: v.mean(axis=0) for k, v in rc.items()}, tv=tv, w=w), open(CK / "figdata.pkl", "wb"))
    (C.ANALYSIS / "model_results.json").write_text(json.dumps(out, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    log(f"stage 3 complete in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main(quick="--quick" in sys.argv)
