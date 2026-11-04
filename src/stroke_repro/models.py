"""Model specifications. Every learned preprocessing step lives inside the estimator so that it
is re-fitted on training data only (inner and outer folds, temporal training set)."""
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from . import config as C


class GcsNihssRatio(BaseEstimator, TransformerMixin):
    """Append Glasgow-to-NIHSS ratio, gcs/(nihss+1), computed from (imputed) components."""

    def __init__(self, gcs_idx=0, nihss_idx=1):
        self.gcs_idx, self.nihss_idx = gcs_idx, nihss_idx

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = np.asarray(X, float)
        r = X[:, self.gcs_idx] / (np.clip(X[:, self.nihss_idx], 0, None) + 1.0)
        return np.column_stack([X, r])


def _imputer(seed, sample_posterior=False):
    return IterativeImputer(max_iter=15, random_state=seed, sample_posterior=sample_posterior,
                            skip_complete=True)


def lr_pipeline(seed, ratio_idx=None, sample_posterior=False):
    steps = [("impute", _imputer(seed, sample_posterior))]
    if ratio_idx is not None:
        steps.append(("ratio", GcsNihssRatio(*ratio_idx)))
    steps += [("scale", StandardScaler()), ("clf", LogisticRegression(max_iter=5000))]
    return Pipeline(steps)


def make(name, seed, inner_folds=C.INNER_FOLDS, ratio_idx=None, sample_posterior=False):
    cv = StratifiedKFold(inner_folds, shuffle=True, random_state=seed)
    if name in ("LR", "LR_ratio", "LR_mi"):
        est = lr_pipeline(seed, ratio_idx, sample_posterior)
        grid = {"clf__C": [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0]}
    elif name == "ClinRef":
        est = Pipeline([("impute", _imputer(seed)), ("scale", StandardScaler()),
                        ("clf", LogisticRegression(C=1e4, max_iter=5000))])
        return est                                   # fully pre-specified: no tuning
    elif name == "RF":
        est = Pipeline([("impute", _imputer(seed)),
                        ("clf", RandomForestClassifier(n_estimators=400, random_state=seed, n_jobs=1))])
        grid = {"clf__min_samples_leaf": [5, 15], "clf__max_features": ["sqrt", 0.5]}
    elif name == "HGB":
        est = HistGradientBoostingClassifier(random_state=seed, max_iter=300, early_stopping=False)
        grid = {"learning_rate": [0.03, 0.1], "max_depth": [2, 3], "l2_regularization": [0.0, 1.0]}
    elif name == "XGB":
        est = XGBClassifier(n_estimators=300, subsample=0.8, colsample_bytree=0.8, random_state=seed,
                            n_jobs=1, eval_metric="logloss", tree_method="hist")
        grid = {"learning_rate": [0.03, 0.1], "max_depth": [2, 3], "min_child_weight": [1, 5]}
    else:
        raise ValueError(name)
    return GridSearchCV(est, grid, scoring="roc_auc", cv=cv, n_jobs=2, refit=True)


class MIEnsemble(BaseEstimator):
    """Multiple imputation by chained equations with m posterior draws: one imputer + logistic model per
    draw, fitted on training data only; predictions are the mean probability over draws (Rubin-style
    pooling on the probability scale).  Penalty C is fixed (pre-set from the primary analysis) so that
    tuning does not multiply the cost."""

    def __init__(self, m=5, C=0.03, seed=0):
        self.m, self.C, self.seed = m, C, seed

    def fit(self, X, y, sample_weight=None):
        self.models_ = []
        for j in range(self.m):
            pipe = Pipeline([("impute", _imputer(self.seed + 101 * j, sample_posterior=True)),
                             ("scale", StandardScaler()), ("clf", LogisticRegression(C=self.C, max_iter=5000))])
            pipe.fit(X, y)
            self.models_.append(pipe)
        self.classes_ = np.array([0, 1])
        return self

    def predict_proba(self, X):
        return np.mean([mdl.predict_proba(X) for mdl in self.models_], axis=0)

    def per_draw_proba(self, X):
        return np.array([mdl.predict_proba(X)[:, 1] for mdl in self.models_])


def fit_predict(name, Xtr, ytr, Xte, seed, wtr=None, **kw):
    if name == "LR_MI":
        est = MIEnsemble(m=kw.get("m", 5), C=kw.get("C", 0.03), seed=seed).fit(Xtr, ytr)
        return est, est.predict_proba(Xte)[:, 1], {"m": est.m, "C": est.C}
    m = make(name, seed, **kw)
    fitkw = {}
    if wtr is not None:
        key = "clf__sample_weight" if name not in ("HGB", "XGB") else "sample_weight"
        fitkw[key] = wtr
    m.fit(Xtr, ytr, **fitkw)
    best = getattr(m, "best_params_", {})
    return m, m.predict_proba(Xte)[:, 1], best


def clone_fit(m, X, y):
    return clone(m).fit(X, y)
