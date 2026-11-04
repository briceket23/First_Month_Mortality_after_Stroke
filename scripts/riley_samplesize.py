"""Post hoc minimum sample size check for a binary-outcome prediction model (Riley et al., BMJ 2020;368:m441).

Not part of the pre-specified analysis. It asks whether the development sample (labelled patients, events,
candidate parameters) meets the three Riley criteria under two anticipated Cox-Snell R2 values:
(a) conservative: 15% of the maximum R2_CS for the observed prevalence (Riley's default when no prior model exists);
(b) C-statistic-based: R2_CS implied by the observed nested-CV AUROC, by simulation (Riley et al. 2021 approach).
Usage: python tools/riley_samplesize.py outputs/analysis/model_results.json outputs/analysis/riley_samplesize_posthoc.json
"""
import json
import math
import sys

import numpy as np
from scipy.optimize import brentq
from sklearn.metrics import roc_auc_score


def r2cs_max(phi):
    lnl0 = phi * math.log(phi) + (1 - phi) * math.log(1 - phi)
    return 1 - math.exp(2 * lnl0)


def r2cs_from_c(c, phi, n=400_000, seed=20261102):
    rng = np.random.default_rng(seed)
    z = rng.standard_normal(n)

    def sim(sigma):
        # intercept chosen so that mean risk equals phi
        a = brentq(lambda a: (1 / (1 + np.exp(-(a + sigma * z)))).mean() - phi, -20, 20)
        p = 1 / (1 + np.exp(-(a + sigma * z)))
        y = rng.random(n) < p
        return a, p, y

    def auc_gap(sigma):
        _, p, y = sim(sigma)
        return roc_auc_score(y, p) - c

    sigma = brentq(auc_gap, 0.05, 6.0, xtol=1e-3)
    _, p, y = sim(sigma)
    ll_model = np.sum(y * np.log(p) + (~y) * np.log(1 - p))
    ph = y.mean()
    ll_null = n * (ph * math.log(ph) + (1 - ph) * math.log(1 - ph))
    lr = 2 * (ll_model - ll_null)
    return 1 - math.exp(-lr / n)


def criteria(P, phi, r2, S=0.9, delta=0.05, moe=0.05):
    n1 = P / ((S - 1) * math.log(1 - r2 / S))
    rmax = r2cs_max(phi)
    s_opt = r2 / (r2 + delta * rmax)
    n2 = P / ((s_opt - 1) * math.log(1 - r2 / s_opt))
    n3 = (1.96 / moe) ** 2 * phi * (1 - phi)
    return {"n_shrinkage": math.ceil(n1), "n_optimism": math.ceil(n2), "n_intercept": math.ceil(n3),
            "n_required": math.ceil(max(n1, n2, n3))}


def main(results, out):
    mr = json.load(open(results, encoding="utf-8"))
    n, e = int(mr["n"]), int(mr["events"])
    P = round(e / mr["epv_candidate_df"])  # candidate degrees of freedom (no data-driven selection)
    c = float(mr["nested_primary"]["LR"]["auroc"])
    phi = e / n
    rmax = r2cs_max(phi)
    out_d = {"n_available": n, "events_available": e, "prevalence": round(phi, 4), "candidate_parameters": P,
             "r2cs_max": round(rmax, 4), "scenarios": {}}
    for label, r2 in [("conservative_15pct_of_max", 0.15 * rmax), ("from_observed_auroc", r2cs_from_c(c, phi))]:
        crit = criteria(P, phi, r2)
        crit.update(anticipated_r2cs=round(r2, 4), events_required=math.ceil(crit["n_required"] * phi),
                    met=n >= crit["n_required"])
        out_d["scenarios"][label] = crit
    json.dump(out_d, open(out, "w", encoding="utf-8"), indent=2)
    print(json.dumps(out_d, indent=2))


if __name__ == "__main__":
    main(*sys.argv[1:3])
