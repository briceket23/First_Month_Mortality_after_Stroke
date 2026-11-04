"""Duplicate reconciliation never picks a row by position; conflicts are preserved."""
import re
import numpy as np, pandas as pd
from conftest import ROOT
from stroke_repro import config as C
from stroke_repro.deduplication import reconcile


def _pair(**kw):
    base = dict(src_id=["R0001", "R0002"], src_row=[2, 3], unique_code=["AB2015-01-01"] * 2, entry_date=[pd.Timestamp("2015-01-01")] * 2,
                release_date=[pd.Timestamp("2015-01-05")] * 2, age=[60.0, 60.0], male=[1.0, 1.0], sex_raw=["male", "male"], age_raw=[60, 60],
                death1=["Yes", "No"], death3=[None, None], death6=[None, None], death9=[None, None], disp=["home", "home"],
                los_recorded=[4.0, 4.0], los_days=[4.0, 4.0], los_date_elapsed=[4.0, 4.0], flag_blank_record=[False, False], flag_column_shift=[False, False],
                diagnosis=["AVCI", "AVCI"], nihss=[5.0, 7.0])
    base.update(kw)
    for c in C.NUMERIC + C.BINARY:
        base.setdefault(c, [np.nan, np.nan])
    return pd.DataFrame(base)


def test_conflicting_outcome_is_unresolved_not_first_row():
    pts, _ = reconcile(_pair(), rule="primary")
    assert len(pts) == 1 and bool(pts.outcome_forced_unresolved.iloc[0]) and np.isnan(pts.nihss.iloc[0])
    assert set(pts.src_ids.iloc[0].split("|")) == {"R0001", "R0002"}


def test_sex_conflict_is_identifier_collision():
    pts, log = reconcile(_pair(male=[1.0, 0.0], sex_raw=["male", "female"]), rule="primary")
    assert len(pts) == 2 and (log.decision.str.contains("collision")).any()


def test_no_keep_first_in_primary_code():
    src = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "src" / "stroke_repro").glob("*.py")).split("def reproduce_original")[0]
    assert not re.search(r"drop_duplicates\([^)]*keep=['\"](first|last)", src)
