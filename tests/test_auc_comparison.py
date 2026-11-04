"""Paired AUROC difference interval (DeLong) agrees with a paired bootstrap; empty tiers are reported."""
import numpy as np
from sklearn.metrics import roc_auc_score
from stroke_repro.statistical_comparison import delong_paired
from stroke_repro.risk_stratification import tiers


def test_paired_delong_matches_paired_bootstrap():
    rng = np.random.default_rng(3); n = 600; y = rng.integers(0, 2, n); s = rng.normal(size=n)
    p1 = 1 / (1 + np.exp(-(1.2 * y + 0.8 * s))); p2 = 1 / (1 + np.exp(-(0.9 * y + 0.8 * s + 0.3 * rng.normal(size=n))))
    r = delong_paired(y, p1, p2)
    assert abs(r["diff"] - (roc_auc_score(y, p1) - roc_auc_score(y, p2))) < 1e-9 and r["diff_lo"] < r["diff"] < r["diff_hi"]
    d = [roc_auc_score(y[i], p1[i]) - roc_auc_score(y[i], p2[i]) for i in (rng.integers(0, n, n) for _ in range(300))]
    lo, hi = np.percentile(d, [2.5, 97.5]); assert abs(lo - r["diff_lo"]) < 0.03 and abs(hi - r["diff_hi"]) < 0.03


def test_empty_low_tier_reported():
    t = tiers(np.array([0, 1, 1, 0, 1]), np.array([0.5, 0.6, 0.9, 0.45, 0.8]))
    low = t[t.tier == "Low"].iloc[0]; assert low.n == 0 and np.isnan(low.mortality) and len(t) == 3
