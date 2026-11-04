"""Endpoint rule boundary conditions and unknown-status preservation."""
import math
from stroke_repro.outcome_reconstruction import assign


def a(**kw):
    base = dict(disp="home", los_days=None, los_alt=None, death1=None, death3=None, death6=None, death9=None); base.update(kw)
    return assign(base)


def test_day30_event_day31_non_event():
    assert a(disp="death", los_days=30)["cls"] == "E1_inhosp_death_le30" and a(disp="death", los_days=31)["cls"] == "N1_inhosp_death_gt30"


def test_postdischarge_death1_is_assumption_dependent_and_strict_unresolves_it():
    assert a(disp="home", los_days=5, death1="Yes")["cls"] == "E2_month1_death_postdischarge"
    assert math.isnan(assign(dict(disp="home", los_days=5, death1="Yes"), strict=True)["y"])


def test_discharged_alive_after_day30_is_non_event_and_within_30_without_followup_is_unresolved():
    assert a(disp="home", los_days=35)["cls"] == "N3_discharged_alive_gt30"
    assert math.isnan(a(disp="home", los_days=5)["y"])


def test_later_contact_alive_is_survival_but_later_death_never_an_event():
    assert a(disp="home", los_days=5, death3="No")["cls"] == "N4_alive_later_contact"
    assert math.isnan(a(disp="home", los_days=5, death3="Yes")["y"])


def test_contradictions_codes_and_other_disposition_stay_unknown():
    assert a(disp="death", los_days=3, death1="No")["conflict"] is True
    assert math.isnan(a(disp="home", los_days=5, death1="invalid")["y"])
    assert math.isnan(a(disp="other", los_days=40)["y"])
    assert math.isnan(a(disp="death", los_days=None)["y"])


def test_stay_boundary_conflict_is_unresolved():
    assert a(disp="home", los_days=29, los_alt=32)["cls"] == "U_los_conflict_at_boundary"
