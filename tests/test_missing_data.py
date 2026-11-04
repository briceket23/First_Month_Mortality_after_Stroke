"""Imputation lives inside the pipeline; the multiple-imputation ensemble returns per-draw probabilities."""
import numpy as np, pandas as pd
from stroke_repro import config as C
from stroke_repro.imputation import MIEnsemble
from stroke_repro.model_training import make


def test_imputer_inside_every_pipeline():
    for name in ("LR", "ClinRef", "RF"):
        est = make(name, C.SEED)
        steps = est.estimator.steps if hasattr(est, "estimator") else est.steps
        assert steps[0][0] == "impute"


def test_mi_ensemble_draws_differ_and_average():
    rng = np.random.default_rng(0); n = 200
    X = pd.DataFrame(rng.normal(size=(n, 4)), columns=list("abcd")); X.loc[rng.random(n) < 0.3, "a"] = np.nan
    y = (X.b + rng.normal(size=n) > 0).astype(int).values
    est = MIEnsemble(m=3, C=0.3, seed=1).fit(X, y)
    P = est.per_draw_proba(X)
    assert P.shape[0] == 3 and not np.allclose(P[0], P[1])
    # transform re-samples the posterior, so repeated predictions vary slightly; pooled and per-draw means must agree closely
    assert np.corrcoef(est.predict_proba(X)[:, 1], P.mean(axis=0))[0, 1] > 0.95
