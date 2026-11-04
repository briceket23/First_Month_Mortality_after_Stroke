"""Stage 2: outcome ascertainability, inverse-probability-of-observation weighting,
full-registry mortality bounds and MNAR delta-adjustment (pattern-mixture) analysis.
"""
import json

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression

from . import config as C

PERIODS = [2009, 2012, 2014, 2016, 2019, 2020, 2023]
PERIOD_LABELS = ["2010-12", "2013-14", "2015-16", "2017-19", "2020", "2021-23"]


def add_period(p):
    p = p.copy()
    p["period"] = pd.cut(p.admission_year, PERIODS, labels=PERIOD_LABELS).astype(str)
    return p


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def smd(a, b, binary=False):
    a, b = a.dropna(), b.dropna()
    if len(a) < 2 or len(b) < 2:
        return np.nan
    if binary:
        p1, p2 = a.mean(), b.mean()
        s = np.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / 2)
    else:
        p1, p2 = a.mean(), b.mean()
        s = np.sqrt((a.var() + b.var()) / 2)
    return (p1 - p2) / s if s > 0 else np.nan


def compare_groups(p):
    L, U = p[p.labelled], p[~p.labelled]
    rows = []
    cont = [("Age, y", "age"), ("NIHSS", "nihss"), ("Glasgow Coma Scale", "gcs"), ("Modified Rankin (admission)", "mrs"),
            ("Systolic BP, mmHg", "sbp"), ("Creatinine, mg/dL", "creatinine"), ("CRP, mg/L", "crp"),
            ("Length of stay, d", "los_days")]
    for lab, c in cont:
        a, b = L[c], U[c]
        pv = stats.mannwhitneyu(a.dropna(), b.dropna()).pvalue if a.notna().sum() > 2 and b.notna().sum() > 2 else np.nan
        rows.append(dict(variable=lab, labelled=f"{a.median():.1f} [{a.quantile(.25):.1f}-{a.quantile(.75):.1f}] (n={a.notna().sum()})",
                         unresolved=f"{b.median():.1f} [{b.quantile(.25):.1f}-{b.quantile(.75):.1f}] (n={b.notna().sum()})",
                         smd=round(smd(a, b), 2), p=pv))
    binv = [("Male sex", "male"), ("Haemorrhagic stroke", "hemorrhagic"), ("Hypertension", "hypertension"),
            ("Diabetes", "diabetes"), ("Atrial fibrillation", "atrial_fib"), ("Prior stroke", "prior_stroke")]
    for lab, c in binv:
        a, b = L[c], U[c]
        ka, kb = int(a.sum()), int(b.sum())
        pv = stats.chi2_contingency([[ka, a.notna().sum() - ka], [kb, b.notna().sum() - kb]])[1]
        rows.append(dict(variable=lab, labelled=f"{ka}/{a.notna().sum()} ({100*a.mean():.1f}%)",
                         unresolved=f"{kb}/{b.notna().sum()} ({100*b.mean():.1f}%)", smd=round(smd(a, b, True), 2), p=pv))
    for lab, c in [("NIHSS missing", "nihss"), ("mRS missing", "mrs"), ("CRP missing", "crp")]:
        a, b = L[c].isna(), U[c].isna()
        pv = stats.chi2_contingency([[a.sum(), (~a).sum()], [b.sum(), (~b).sum()]])[1]
        rows.append(dict(variable=lab, labelled=f"{a.sum()}/{len(a)} ({100*a.mean():.1f}%)",
                         unresolved=f"{b.sum()}/{len(b)} ({100*b.mean():.1f}%)", smd=round(smd(a.astype(float), b.astype(float), True), 2), p=pv))
    for per in PERIOD_LABELS:
        a, b = L.period == per, U.period == per
        rows.append(dict(variable=f"Admitted {per}", labelled=f"{a.sum()} ({100*a.mean():.1f}%)",
                         unresolved=f"{b.sum()} ({100*b.mean():.1f}%)", smd=round(smd(a.astype(float), b.astype(float), True), 2), p=np.nan))
    for dsp in ["death", "home", "transfer", "other", "missing"]:
        a, b = L.disp == dsp, U.disp == dsp
        rows.append(dict(variable=f"Disposition: {dsp}", labelled=f"{a.sum()} ({100*a.mean():.1f}%)",
                         unresolved=f"{b.sum()} ({100*b.mean():.1f}%)", smd=np.nan, p=np.nan))
    return pd.DataFrame(rows), len(L), len(U)


def design(p):
    X = pd.DataFrame(index=p.index)
    for c in ["age", "nihss", "gcs", "mrs", "sbp"]:
        x = p[c].astype(float)
        X[c] = (x.fillna(x.median()) - x.median()) / (x.std() or 1)
        X[c + "_miss"] = x.isna().astype(float)
    for c in ["male", "hemorrhagic", "hypertension", "diabetes"]:
        X[c] = p[c].fillna(0).astype(float)
        X[c + "_miss"] = p[c].isna().astype(float)
    for per in PERIOD_LABELS[1:]:
        X["period_" + per] = (p.period == per).astype(float)
    for d in ["death", "transfer", "other", "missing"]:
        X["disp_" + d] = (p.disp == d).astype(float) if d != "missing" else p.disp.isin(["missing", "invalid"]).astype(float)
    X["los_gt30"] = (p.los_days > 30).astype(float)
    return X


def ipw(p):
    """P(labelled | admission covariates, period, disposition). Disposition and stay are post-baseline,
    which is allowed for an observation model (never for the prediction model)."""
    X = design(p)
    R = p.labelled.astype(int)
    m = LogisticRegression(C=1.0, max_iter=5000).fit(X, R)     # mild L2 for separation (deaths ~ always labelled)
    pi = m.predict_proba(X)[:, 1]
    w = np.where(R == 1, 1 / pi, 0.0)
    cap = np.quantile(w[R == 1], 0.99)
    wt = np.minimum(w, cap)
    lab = R == 1
    ess = wt[lab].sum() ** 2 / (wt[lab] ** 2).sum()
    diag = dict(pi_min=float(pi.min()), pi_max=float(pi.max()), pi_labelled_min=float(pi[lab].min()),
                n_pi_lt_0_05=int((pi < 0.05).sum()), n_labelled_pi_lt_0_10=int((pi[lab] < 0.10).sum()),
                weight_cap_p99=float(cap), weight_max_untruncated=float(w.max()), n_truncated=int((w > cap).sum()),
                weight_sum=float(wt.sum()), n_eligible=int(len(p)), ess=float(ess), n_labelled=int(lab.sum()),
                coefficients={k: round(float(v), 3) for k, v in zip(X.columns, m.coef_[0])},
                pi_by_disposition={d: [round(float(np.quantile(pi[(p.disp == d).values], q)), 3) for q in (0, .5, 1)]
                                   for d in ["death", "home", "transfer", "other", "missing"] if (p.disp == d).any()})
    return pi, wt, diag


def weighted_mortality(p, wt, B=C.BOOTSTRAP_N, seed=C.SEED):
    lab = p.labelled.values
    y = p.y.values
    est = np.sum(wt[lab] * y[lab]) / np.sum(wt[lab])
    rng = np.random.default_rng(seed)
    bs = []
    idx_all = np.arange(len(p))
    for _ in range(B):            # bootstrap the weights model as well
        ii = rng.choice(idx_all, len(idx_all), replace=True)
        q = p.iloc[ii].reset_index(drop=True)
        try:
            _, w2, _ = ipw(q)
        except Exception:
            continue
        l2 = q.labelled.values
        bs.append(np.sum(w2[l2] * q.y.values[l2]) / np.sum(w2[l2]))
    return est, np.percentile(bs, [2.5, 97.5]), len(bs)


def delta_analysis(p, reference="early_era", weights=None):
    """Pattern-mixture estimate of 30-day mortality in the whole eligible cohort.

    Unresolved patients discharged alive within 30 d: post-discharge risk taken from labelled
    discharged-alive patients of the same period (MAR within period), shifted by odds ratio delta.
    Other unresolved patients (missing/'other' disposition, conflicts, timing unknown): risk from an
    IPW-weighted logistic model of the outcome on admission covariates + period fitted on labelled patients,
    shifted by the same delta.  delta = 1 is MAR; delta > 1 means unresolved patients are more
    likely to have died than comparable resolved patients.
    """
    out = []
    lab = p.labelled
    disc = p.disp.isin(["home", "transfer"]) & ~(p.los_days > 30)
    # post-discharge month-1 risk among labelled discharged-alive-within-30d patients, by period
    pd_risk = {}
    for per in PERIOD_LABELS:
        m = lab & disc & (p.period == per)
        k, n = int(p.y[m].sum()), int(m.sum())
        pd_risk[per] = (k, n)
    pooled_k = sum(v[0] for v in pd_risk.values())
    pooled_n = sum(v[1] for v in pd_risk.values())
    X = design(p).drop(columns=[c for c in design(p).columns if c.startswith("disp_") or c == "los_gt30"])
    sw = None if weights is None else weights[lab.values]
    om = LogisticRegression(C=1.0, max_iter=5000).fit(X[lab], p.y[lab].astype(int), sample_weight=sw)
    base_other = om.predict_proba(X)[:, 1]
    logit = lambda q: np.log(q / (1 - q))
    expit = lambda z: 1 / (1 + np.exp(-z))
    known_deaths = int(p.y[lab].sum())
    N = len(p)
    for delta in [0.25, 0.5, 1.0, 2.0, 4.0, 8.0]:
        exp_deaths = 0.0
        for i in np.where(~lab)[0]:
            row = p.iloc[i]
            if disc.iloc[i]:
                if reference == "early_era":      # 2010-14, when post-discharge deaths were demonstrably recorded
                    k = pd_risk["2010-12"][0] + pd_risk["2013-14"][0]
                    n = pd_risk["2010-12"][1] + pd_risk["2013-14"][1]
                else:                             # period-specific MAR
                    k, n = pd_risk.get(row.period, (pooled_k, pooled_n))
                    if n < 20:
                        k, n = pooled_k, pooled_n
                q = (k + 0.5) / (n + 1)
            else:
                q = base_other[i]
            exp_deaths += expit(logit(q) + np.log(delta))
        out.append(dict(reference=reference, delta_odds_ratio=delta, expected_deaths_unresolved=round(exp_deaths, 1),
                        mortality_pct=round(100 * (known_deaths + exp_deaths) / N, 1)))
    return pd.DataFrame(out), pd_risk, (pooled_k, pooled_n)


def main():
    res = {}
    for name in ["primary", "strict_timing"]:
        p = add_period(pd.read_pickle(C.RESTRICTED / f"cohort_{name}.pkl"))
        N, nl, nd = len(p), int(p.labelled.sum()), int(p.y.sum())
        r = dict(eligible=N, labelled=nl, deaths=nd, unresolved=N - nl)
        r["labelled_mortality_pct"] = round(100 * nd / nl, 1)
        r["labelled_mortality_ci"] = [round(100 * x, 1) for x in wilson(nd, nl)]
        r["bound_all_unresolved_alive_pct"] = round(100 * nd / N, 1)
        r["bound_all_unresolved_dead_pct"] = round(100 * (nd + N - nl) / N, 1)
        # in-hospital 30-day mortality among patients with a known disposition and usable stay
        known = p.disp.isin(["death", "home", "transfer"]) & p.los_days.notna()
        e1 = (p.y_class == "E1_inhosp_death_le30")
        r["inhosp_30d_deaths"] = int(e1.sum())
        r["inhosp_denominator_known_disposition"] = int(known.sum())
        r["inhosp_30d_mortality_pct"] = round(100 * e1[known].mean(), 1)
        r["inhosp_30d_mortality_ci"] = [round(100 * x, 1) for x in wilson(int(e1[known].sum()), int(known.sum()))]
        # by period
        byp = p.groupby("period").agg(eligible=("y", "size"), labelled=("labelled", "sum"), deaths=("y", "sum"))
        byp["labelled_pct"] = (100 * byp.labelled / byp.eligible).round(1)
        byp["labelled_mortality_pct"] = (100 * byp.deaths / byp.labelled).round(1)
        byp["inhosp_30d_deaths"] = e1.groupby(p.period).sum()
        byp["known_disposition"] = known.groupby(p.period).sum()
        byp["inhosp_30d_pct_known_disp"] = (100 * byp.inhosp_30d_deaths / byp.known_disposition).round(1)
        later_any = p[["death3", "death6", "death9"]].isin(["Yes", "No"]).any(axis=1)
        later_alive = (p[["death3", "death6", "death9"]] == "No").any(axis=1)
        no_d1 = ~p.death1.isin(["Yes", "No"])
        byp["later_contact_recorded"] = later_any.groupby(p.period).sum()
        byp["later_contact_pct"] = (100 * byp.later_contact_recorded / byp.eligible).round(1)
        byp["later_contact_no_death1"] = (later_any & no_d1).groupby(p.period).sum()
        byp["n4_alive_by_later_contact"] = (p.y_class == "N4_alive_later_contact").groupby(p.period).sum()
        byp = byp.loc[PERIOD_LABELS]
        byp.to_csv(C.ANALYSIS / f"ascertainment_by_period_{name}.csv")
        r["later_contact_recorded"] = int(later_any.sum())
        r["later_contact_pct"] = round(100 * later_any.mean(), 1)
        r["later_contact_without_death1"] = int((later_any & no_d1).sum())
        r["later_alive_without_death1"] = int((later_alive & no_d1).sum())
        r["n4_alive_by_later_contact"] = int((p.y_class == "N4_alive_later_contact").sum())
        # positivity: patients with no recorded disposition are almost never labelled (pi ~ 0.002), so the
        # IPW target population is restricted to eligible patients with a recorded disposition.
        pk = p[~p.disp.isin(["missing", "invalid"])].reset_index(drop=True)
        r["ipw_population"] = int(len(pk))
        r["ipw_population_labelled"] = int(pk.labelled.sum())
        r["excluded_from_ipw_no_disposition"] = int(len(p) - len(pk))
        pi, wt, wdiag = ipw(pk)
        est, ci, nb = weighted_mortality(pk, wt, B=300 if name != "primary" else C.BOOTSTRAP_N)
        r["ipw_mortality_pct"] = round(100 * est, 1)
        r["ipw_mortality_ci"] = [round(100 * x, 1) for x in ci]
        r["ipw_bootstrap_replicates"] = nb
        r["ipw_diagnostics"] = wdiag
        wfull = pd.Series(wt, index=pk.patient_key).reindex(p.patient_key).fillna(1.0).values
        dtab, pdr, pooled = delta_analysis(p, "early_era", wfull)
        dtab = pd.concat([dtab, delta_analysis(p, "period_specific", wfull)[0]], ignore_index=True)
        dtab.to_csv(C.ANALYSIS / f"mnar_delta_{name}.csv", index=False)
        r["postdischarge_risk_by_period"] = {k: f"{v[0]}/{v[1]}" for k, v in pdr.items()}
        r["postdischarge_risk_pooled"] = f"{pooled[0]}/{pooled[1]} ({100*pooled[0]/pooled[1]:.1f}%)"
        r["delta_table"] = dtab.to_dict(orient="records")
        res[name] = r
        if name == "primary":
            tab, nL, nU = compare_groups(p)
            tab.to_csv(C.ANALYSIS / "labelled_vs_unresolved.csv", index=False)
            res["comparison_n"] = dict(labelled=nL, unresolved=nU)
            out = pk[["patient_key", "src_ids", "labelled", "y"]].copy()
            out["pi_observed"], out["ipw"] = pi, wt
            out.to_pickle(C.RESTRICTED / "ipw_primary.pkl")
            print(tab.to_string())
            print(byp.to_string())
            print(dtab.to_string())
    (C.ANALYSIS / "ascertainment_summary.json").write_text(json.dumps(res, indent=2, default=float), encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("delta_table", "ipw_diagnostics")} if isinstance(v, dict) else v
                      for k, v in res.items()}, indent=1, default=float))
    print(json.dumps(res["primary"]["ipw_diagnostics"], indent=1, default=float))


if __name__ == "__main__":
    main()
