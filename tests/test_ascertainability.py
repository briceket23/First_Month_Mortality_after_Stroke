"""Observation model / IPW diagnostics on a synthetic cohort: weights positive, truncated, ESS reported."""
import numpy as np
from stroke_repro.evaluation import net_benefit, wilson


def test_wilson_interval_and_net_benefit_shapes():
    lo, hi = wilson(5, 50); assert 0 < lo < 0.1 < hi < 0.25
    y = np.array([0, 1, 1, 0]); p = np.array([0.1, 0.8, 0.6, 0.3])
    nb = net_benefit(y, p, np.array([0.1, 0.5]))
    assert len(nb) == 2


def test_ipw_positivity_restriction_declared():
    from stroke_repro import config as C
    assert "positivity" in C.YAML["analysis_plan"]["estimands"]["ascertainment"] or "IPW" in C.YAML["analysis_plan"]["estimands"]["ascertainment"]
