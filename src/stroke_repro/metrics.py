"""Discrimination, calibration and utility metrics (DeLong, calibration slope/intercept, net benefit)."""
import numpy as np
import statsmodels.api as sm
from scipy import stats
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


def _midrank(x):
    j = np.argsort(x)
    z = x[j]
    n = len(x)
    t = np.zeros(n)
    i = 0
    while i < n:
        k = i
        while k < n and z[k] == z[i]:
            k += 1
        t[i:k] = 0.5 * (i + k - 1) + 1
        i = k
    out = np.empty(n)
    out[j] = t
    return out


def _delong_components(y, preds):
    """preds: (k, n) array. Returns aucs (k,), covariance (k,k)  [Sun & Xu 2014 fast DeLong]."""
    y = np.asarray(y).astype(int)
    order = np.argsort(-y, kind="mergesort")
    preds = np.atleast_2d(preds)[:, order]
    m = int(y.sum())
    n = len(y) - m
    k = preds.shape[0]
    tx = np.empty((k, m)); ty = np.empty((k, n)); tz = np.empty((k, m + n))
    for r in range(k):
        tx[r] = _midrank(preds[r, :m]); ty[r] = _midrank(preds[r, m:]); tz[r] = _midrank(preds[r])
    aucs = tz[:, :m].sum(axis=1) / m / n - (m + 1.0) / 2.0 / n
    v01 = (tz[:, :m] - tx) / n
    v10 = 1.0 - (tz[:, m:] - ty) / m
    sx = np.atleast_2d(np.cov(v01)); sy = np.atleast_2d(np.cov(v10))
    return aucs, sx / m + sy / n


def delong_ci(y, p, alpha=0.05):
    auc, cov = _delong_components(y, np.asarray(p)[None, :])
    se = np.sqrt(cov[0, 0])
    z = stats.norm.ppf(1 - alpha / 2)
    return float(auc[0]), float(max(0, auc[0] - z * se)), float(min(1, auc[0] + z * se))


def delong_paired(y, p1, p2, alpha=0.05):
    """Paired DeLong test.  Returns AUC1, AUC2, difference (1-2), its 95% CI, two-sided p."""
    aucs, cov = _delong_components(y, np.vstack([p1, p2]))
    d = aucs[0] - aucs[1]
    var = cov[0, 0] + cov[1, 1] - 2 * cov[0, 1]
    se = np.sqrt(max(var, 1e-12))
    z = stats.norm.ppf(1 - alpha / 2)
    p = 2 * (1 - stats.norm.cdf(abs(d) / se))
    return dict(auc1=float(aucs[0]), auc2=float(aucs[1]), diff=float(d), diff_lo=float(d - z * se),
                diff_hi=float(d + z * se), p=float(p))


def calibration(y, p, w=None):
    """Calibration intercept (calibration-in-the-large, slope fixed at 1) and slope; Brier."""
    y = np.asarray(y).astype(float)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    lp = np.log(p / (1 - p))
    fw = None if w is None else np.asarray(w, float)
    m_slope = sm.GLM(y, sm.add_constant(lp), family=sm.families.Binomial(), var_weights=fw).fit()
    m_int = sm.GLM(y, np.ones_like(lp), family=sm.families.Binomial(), offset=lp, var_weights=fw).fit()
    ci_s = m_slope.conf_int()[1]
    ci_i = m_int.conf_int()[0]
    brier = float(np.average((p - y) ** 2, weights=fw))
    return dict(slope=float(m_slope.params[1]), slope_lo=float(ci_s[0]), slope_hi=float(ci_s[1]),
                intercept=float(m_int.params[0]), intercept_lo=float(ci_i[0]), intercept_hi=float(ci_i[1]),
                brier=brier, mean_pred=float(np.average(p, weights=fw)), obs_rate=float(np.average(y, weights=fw)))


def summary(y, p, w=None):
    out = {}
    if w is None:
        a, lo, hi = delong_ci(y, p)
        out.update(auroc=a, auroc_lo=lo, auroc_hi=hi)
    else:
        out.update(auroc=float(roc_auc_score(y, p, sample_weight=w)))
    out["auprc"] = float(average_precision_score(y, p, sample_weight=w))
    out.update(calibration(y, p, w))
    out["n"] = int(len(y))
    out["events"] = int(np.sum(y))
    return out


def bootstrap_auc_ci(y, p, w=None, B=1000, seed=1):
    rng = np.random.default_rng(seed)
    y, p = np.asarray(y), np.asarray(p)
    w = None if w is None else np.asarray(w)
    vals = []
    for _ in range(B):
        i = rng.integers(0, len(y), len(y))
        if y[i].min() == y[i].max():
            continue
        vals.append(roc_auc_score(y[i], p[i], sample_weight=None if w is None else w[i]))
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def net_benefit(y, p, thresholds, w=None):
    y = np.asarray(y); p = np.asarray(p)
    w = np.ones_like(p, dtype=float) if w is None else np.asarray(w, float)
    N = w.sum()
    out = []
    prev = np.sum(w * y) / N
    for t in thresholds:
        pos = p >= t
        tp = np.sum(w * (pos & (y == 1))) / N
        fp = np.sum(w * (pos & (y == 0))) / N
        out.append((t, tp - fp * t / (1 - t), prev - (1 - prev) * t / (1 - t)))
    return np.array(out)


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)
