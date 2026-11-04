"""Calibration metrics and in-fold recalibration without test-set selection."""
import numpy as np
from stroke_repro import config as C
from stroke_repro.calibration import calibration


def test_calibration_slope_near_one_for_calibrated_probabilities():
    rng = np.random.default_rng(1); p = rng.uniform(0.05, 0.95, 5000); y = (rng.random(5000) < p).astype(int)
    c = calibration(y, p)
    assert abs(c["slope"] - 1) < 0.1 and abs(c["intercept"]) < 0.1


def test_recalibration_code_uses_training_folds_only():
    txt = (C.ROOT / "src" / "stroke_repro" / "stage3_models.py").read_text(encoding="utf-8")
    recal = txt[txt.index("def recalibration_nested"):txt.index("def temporal")]
    assert "CalibratedClassifierCV" in recal and "cv=StratifiedKFold" in recal and ".fit(X.iloc[te]" not in recal
    assert C.YAML["modelling"]["risk_tiers"]["pre_specified"] is True
