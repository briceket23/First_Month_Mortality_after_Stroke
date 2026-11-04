"""No post-baseline or outcome field can be a predictor."""
from stroke_repro import config as C
from stroke_repro.feature_engineering import CANDIDATES, CLINICAL_REFERENCE

BANNED = {"los_days", "los_recorded", "release_date", "disp", "death1", "death3", "death6", "death9", "cause_of_death_recorded", "labelled", "y", "admission_year"}


def test_predictors_exclude_post_baseline_fields():
    assert not (set(CANDIDATES) & BANNED) and set(CLINICAL_REFERENCE) <= set(CANDIDATES)
    for f in C.YAML["preprocessing"]["excluded_post_baseline_fields"]:
        assert f not in CANDIDATES


def test_no_data_driven_feature_selection():
    src = "\n".join(p.read_text(encoding="utf-8") for p in (C.ROOT / "src" / "stroke_repro").glob("*.py"))
    assert "SelectFromModel" not in src and "RFE(" not in src
