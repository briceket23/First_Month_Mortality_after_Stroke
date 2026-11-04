"""Endpoint specification and provenance-tagged outcome assignment.

ENDPOINT (revised primary): death from any cause within 30 days of hospital admission
(day 0 = registry 'Date of entry'), including death during the index hospitalisation.

Evidence hierarchy (applied per reconciled patient record):
  conflicts are checked first; a record with contradictory status evidence is UNRESOLVED.
  E1  in-hospital death (disposition 'death') with elapsed stay <= 30 d      -> 1  timing: hospital record
  N1  in-hospital death with elapsed stay > 30 d                             -> 0  alive on day 30
  E2  month-1 follow-up field death1 = Yes (not an in-hospital death)        -> 1  timing ASSUMPTION A2
  N2  death1 = No                                                            -> 0  alive at month-1 contact
  N3  death1 unknown, discharged alive (home/transfer) after > 30 d          -> 0  alive on day 30
  N4  death1 unknown, later contact (death3/6/9 = No) records patient alive  -> 0  alive after day 30
  U*  anything else                                                          -> unresolved (never forced)

Assumptions (not documented in the available material; see registry clarification request):
  A1  disposition 'death' = death before leaving the neurological unit; release date / LOS end at death.
  A2  a death1 = Yes recorded after discharge occurred within 30 days of admission.  Under a
      discharge-anchored month-1 window this event could fall up to LOS + 30 days after admission;
      the sensitivity endpoint STRICT treats E2 as unresolved.
Cause-of-death entries are never used as event dates.  No death date is derived from anything
other than an in-hospital death's stay.
"""
import math

WINDOW = 30

CLASSES = {
    "E1_inhosp_death_le30": (1, "hospital record (disposition + stay)", "established under A1"),
    "E2_month1_death_postdischarge": (1, "month-1 follow-up field", "conditional on A2"),
    "N1_inhosp_death_gt30": (0, "hospital record (disposition + stay)", "established under A1"),
    "N2_month1_alive": (0, "month-1 follow-up field", "established"),
    "N3_discharged_alive_gt30": (0, "hospital record (disposition + stay)", "established"),
    "N4_alive_later_contact": (0, "month-3/6/9 follow-up field", "established"),
}


def _na(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def assign(rec, strict=False):
    """Assign the endpoint for one record.

    rec keys: disp ('death','home','transfer','other','missing','invalid'),
              los_days (resolved elapsed stay, days), los_alt (the alternative stay measure, if both
              recorded LOS and date-derived stay exist), death1..death9 ('Yes','No','invalid',None).
    Returns dict(y, cls, provenance, timing, conflict, reason).
    """
    disp = rec.get("disp")
    los = rec.get("los_days")
    los = None if _na(los) else float(los)
    d1, d3, d6, d9 = (rec.get(k) for k in ("death1", "death3", "death6", "death9"))
    later = [v for v in (d3, d6, d9) if v in ("Yes", "No")]
    later_alive = "No" in later
    conflicts = []

    alt = rec.get("los_alt")
    if disp in ("death", "home", "transfer") and los is not None and not _na(alt):
        if (los <= WINDOW) != (float(alt) <= WINDOW) and d1 not in ("Yes", "No"):
            return _u("U_los_conflict_at_boundary", "recorded and date-derived stay disagree across day 30")

    if disp == "death":
        if d1 == "No" and (los is None or los <= WINDOW):
            conflicts.append("in-hospital death within 30 d but death1 = No")
        if later_alive:
            conflicts.append("in-hospital death but alive at a later contact")
        if d1 == "Yes" and los is not None and los > WINDOW:
            conflicts.append("death1 = Yes but in-hospital death after day 30")
    if d1 == "Yes" and later_alive:
        conflicts.append("death1 = Yes but alive at a later contact")
    if conflicts:
        return _u("U_contradictory_status", "; ".join(conflicts), conflict=True)

    if disp == "death":
        if los is None:
            if d1 == "Yes":
                return _c("E2_month1_death_postdischarge", strict, note="in-hospital death, stay unknown; death1 = Yes")
            return _u("U_inhosp_death_timing_unknown", "in-hospital death with no usable stay or dates")
        return _c("E1_inhosp_death_le30" if los <= WINDOW else "N1_inhosp_death_gt30", strict)
    if d1 == "Yes":
        return _c("E2_month1_death_postdischarge", strict)
    if d1 == "No":
        return _c("N2_month1_alive", strict)
    if disp in ("home", "transfer") and los is not None and los > WINDOW:
        return _c("N3_discharged_alive_gt30", strict)
    if later_alive:
        return _c("N4_alive_later_contact", strict)
    if "Yes" in later:
        return _u("U_later_death_timing_unknown", "death recorded at month 3/6/9 only; timing unknown")
    if disp in ("home", "transfer"):
        return _u("U_discharged_alive_no_followup", "discharged alive within 30 d, no follow-up status")
    if disp == "other":
        return _u("U_other_disposition_no_followup", "'Other' disposition (undocumented meaning), no follow-up")
    return _u("U_disposition_missing_no_followup", "no disposition and no follow-up status")


def _c(cls, strict, note=""):
    y, prov, timing = CLASSES[cls]
    if strict and cls == "E2_month1_death_postdischarge":
        return _u("U_strict_timing_unestablished", "death1 = Yes after discharge; timing vs admission not established")
    return dict(y=y, cls=cls, provenance=prov, timing=timing, conflict=False, reason=note or cls)


def _u(cls, reason, conflict=False):
    return dict(y=float("nan"), cls=cls, provenance="none", timing="unresolved", conflict=conflict,
                reason=reason)
