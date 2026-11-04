"""No patient overlap across folds; temporal cut-off is outcome-independent."""
import numpy as np
from sklearn.model_selection import RepeatedStratifiedKFold
from stroke_repro import config as C


def test_no_overlap_across_outer_folds():
    y = np.array([0, 1] * 60); keys = np.arange(120)
    for tr, te in RepeatedStratifiedKFold(n_splits=C.OUTER_FOLDS, n_repeats=2, random_state=C.SEED).split(keys, y):
        assert not set(keys[tr]) & set(keys[te])


def test_temporal_cutoff_declared_outcome_independent():
    assert "ALL eligible" in C.YAML["modelling"]["temporal_split"] and "outcome-independent" in C.YAML["modelling"]["temporal_split"]
